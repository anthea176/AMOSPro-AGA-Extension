# Audit P2d — passage 13 : écrivains graphiques et acquisition SafePort

**24 novembre 2026 · main uniquement · source examinée : `15d146339c4f9e353e701bc06e58013872901407`.** Audit statique, aucune nouvelle Gate A/B/C/D. S1-P1e Sprite gelée, P2d LAST_GOOD protégée. Aucune autorisation de correction native.

Référence P2d : 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Candidate S1-P1e : 142 000 octets, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`. Identités documentées ; aucun nouveau recalcul ou rebuild.

## 1. Comparaison des chemins réellement liés

| Commande | AP20 P2d | Sélection back | Acquisition Safe | Écriture |
|---|---:|---|---|---|
| Aga Back Fill | 22 | Oui | Absente | SetRast(-234) |
| Aga Blit Fill | 33 | Oui | GetMsg(-372) conditionnel | SetRast(-234) ou RectFill(-306) |
| Aga Iff Load | 24 | Oui | Absente | Copie CPU des bitplanes |
| Aga Screen Pattern | 14 | Non explicite | Absente | RectFill sur Screen.RastPort |

**Précision nouvelle : Blit Fill possède déjà un chemin SetRast sécurisé.** [Source UNIT142 $078A4](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_BLOCK_078A4_MC68020.s#L129-L216) : si DB+20 bit0 est posé, GetMsg sur DB+12 ; absence de message = retour 0 avant dessin ; message reçu = effacement du seul bit0, conservation de Disp. Après acquisition, RastPort temporaire sur le bitmap choisi ; si origine (0,0) et dimensions égales à BytesPerRow*8 et Rows, SetRast, sinon RectFill. WaitBlit après dessin. Le chemin plein bitmap existe donc déjà ; il ne faut pas supposer que Blit Fill utilise exclusivement RectFill.

[Back Fill $00C9E](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_BLOCK_00C9E_MC68020.s#L6-L56) sélectionne le même back selon DB+8, alloue un RastPort de 128 octets, InitRastPort, masque la couleur sur 8 bits, SetRast, WaitBlit puis FreeVec. Aucun contrôle Safe. C'est une instruction sans retour, contrairement à Blit Fill. Ne pas substituer aveuglément les deux entrées : validation des couleurs, géométrie incluant padding, ABI et comportement sur refus doivent être conservés ou explicitement définis.

[IFF Load](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L44-L81) : validation et première passe BODY, allocation de la table palette, WaitBlit puis seconde passe écrivant les plans, application palette ensuite. [Sélection du back](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L321-L402) sans acquisition Safe. Point candidat pour la garde : après validation et allocations, avant seconde passe ; conserver cleanup et retour 0 au refus. Ne pas confondre WaitBlit avec réception Safe.

[Screen Pattern $00764](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_BLOCK_00764_MC68020.s#L6-L56) : SetAPen et RectFill sur Screen.RastPort, sans sélection explicite du back ni GetMsg. Le README le définit comme mire de diagnostic. La cible bitmap réelle après Swap et la compatibilité DB/B8 restent à déterminer ; aucune corruption front reproduite. Noter que l'appel palette -852 n'est pas LoadRGB32 (-882) ; ne pas reprendre cette appellation erronée du passage 8.

## 2. Contrat Safe proposé pour décision ultérieure

[Swap historique $00BA2](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/15d146339c4f9e353e701bc06e58013872901407/src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s#L53-L89) : publication DB+20=3 après présentation réussie ; acquisition séparée Safe et Disp. Pour une écriture back, ne consommer que Safe si pending et disponible, préserver Disp, refuser sans écriture si absent. Aucun WaitPort infini, aucun Swap implicite.

- AGA-001 / AGA-010 : P0 statiques maintenues. Réutiliser la logique de garde déjà éprouvée localement ; aucun patch ici.
- AGA-002 : premier Bind B8 doit pouvoir acquitter Safe disponible avant de refuser ; ne pas changer la publication Swap ni contourner DIRTY. Voir passage 11.
- AGA-011 : P1 suspect ; identifier d'abord la page ciblée par la mire, puis décider de sa sémantique en DB.
- AGA-003 : maintenir Clear → décor → Swap ; la garde Safe ne remplace pas le contrat snapshot B8.

## 3. Qualification future, sans nouveau test

| Scénario existant | Discriminant |
|---|---|
| T04 / T12 | IFF valide/invalide, Safe absent/arrivé/acquis ; contrôler plans et ColorMap séparément, cleanup sur refus |
| T05 | bit0 seul effacé après GetMsg réussi ; Disp préservé ; aucun dessin avant acquisition |
| T06 | Blit Fill plein bitmap SetRast et rectangle RectFill ; Screen Pattern avec suivi des deux bitmaps et palette |
| T19 | Back Fill sans retour : observer appels OS et pixels, pas un code résultat fictif ; comparer au témoin Blit Fill |
| T02 / T17 | Premier Bind B8 après Swap sans Bob, port vide vs message disponible, témoin acquis |

Commencer en Gate A MC68020/ABI avec services OS simulés et traces d'appels, puis B Runtime WinUAE et C vrai Compiler après autorisation. Ne pas provoquer volontairement une écriture non Safe sur matériel physique.

**Bilan :** 102 commandes inventoriées, 19 scénarios conservés, aucun nouvel essai. Audit ouvert. Aucune modification native, ASC, binaire, builder, CI ou journal ; aucune promotion. Le cycle Close/End et les autres validations manquantes restent à examiner.

[Audit transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Passage 7](AUDIT_AGA_SWAP_IFF_BACKFILL_B8_PALETTES_2026-11-24.md) · [Passage 11](AUDIT_AGA_AMORCAGE_DOUBLE_BUFFER_B8_2026-11-24.md).
