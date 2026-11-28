# M19 S2g — audit des priorités Sprite/playfield (proposition 0.15.0-alpha.4)

**28/11/2026 — audit initial (historique, avant accord sur P1).** Auteur « ok » en réponse à la proposition d'audit matériel/API avant modification native. Aucun nouveau token, ASM, ASC, builder, binaire ou activation autorisés par ce relevé.

**28/11/2026 — S2g-P1a source-only engagé après accord auteur « ok go » sur les deux signatures et P1 en premier.** Entrée native MC68020 cinq entiers (D3=layer, A3=image/Y/X/ID), frame privée +4o, rang 0 automatique, 1/2/3 filtre exact de paire, refus -210 rang invalide et -206 paire indisponible ou migration. Quatre arguments conservés ; registre v8, cache, largeur, palettes et retraite S2f inchangés. Builder privé reconstruit S2f exacte puis overlay P1a, ajoute GetP/Rbsr avant îlot Sprite (indices AP20 décalés, noms/signatures publics inchangés). Titre de développement 0.15.0-alpha.4.p1a, NON installable ; aucun token surchargé déclaré avant preuve de grammaire AMOS. [Source](../src/native/m19_s2/M19_S2G_PRIORITY_MC68020.s), [builder](../tools/build_m19_s2g_in_memory.py), [banc CPU](../tools/test_m19_s2g_priority_gate_a.py), [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2g-priority-gate-a.yml) à relever. B/C/D non testées. Alpha.3/ASC/ABK/LAST_GOOD intactes, aucun nouveau test AMOS actif, aucune bascule ni promotion.

## 1. Base exacte

[main au début de l'audit](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/3a0ed16140156235f44872b9afb34fd6d3159bef) : S2f alpha.3, Lib 162288o SHA256 `6efdc6f17897de69fb7f292e131cbb31bd55626dea0566d77555f1d7f7073e66`, blob `d58c985692d88b08df2d55b690b43ed47b087b13`, 105 commandes/219 AP20, MC68020+. [Builder S2f](../tools/build_m19_s2f_in_memory.py) : parent S2e exact puis overlays S2f. UNIT142 65062o (472 libres), UNIT213 19964o (45570 libres bruts ; réserve 16384o et portée PC16 séparées). Gate A préalable complète PASS ; [B Runtime et visuel PASS](M19_S2F_RUNTIME_2026-11-28.md), C réelle différée, D non testée. CI post-activation [S2f](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46168682920) et [intégrité](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46168683147) en cours au relevé ; CPU/chemins et documentation PASS. Taille et blob des fichiers actifs contrôlés sur main, aucun rebuild local. LAST_GOOD L2b et ASC/ABK inchangés.

## 2. Matériel et code actuel

- Priorité fixe entre canaux : plus petit numéro devant. Priorité playfield/Sprites par groupes 0/1, 2/3, 4/5, 6/7. Le [Hardware Reference Manual, BPLCON2](https://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide/node0159.html) précise que PF2P (bits 5..3) s'applique au playfield non-dual. Ne pas confondre champs matériels et traduction des tags OS. Les seuils matériels valides sont 0..4 ; seuil 0 pourrait masquer le pointeur, à exclure de l'API proposée.
- [M19_S2D_PUBLIC_MC68020.s](../src/native/m19_s2/M19_S2D_PUBLIC_MC68020.s), `s2d_pub_pick` : parcourir les trois paires 2/3, 4/5, 6/7 dans cet ordre, masque registry libre, largeur commune, bits OS de réservation, compatibilité RGB24. Les simples occupent aussi une paire. L'ID logique 1..64 n'est pas le canal ni la priorité. `s2d_pub_palette` : VideoControl GET $80000028/$80000029 (bases attendues 16/16), $80000032 (résolution 255), $80000034 (PF1 attendu 4), AuxFlags attendu 1. Le code S2f [overlay](../tools/m19_s2f_clip_source.py) conserve pick/palette. Une variation de PF1 sans adaptation de cette garde peut refuser des Show/Change ; garder les autres exigences. Simple RGB24 : pens 21..23, 25..27, 29..31 suivant paire ; attaché : pens 17..31. Aucun SET palette.
- [First Show](../src/native/m19_s2/M19_S2D_EXT_HIDDEN_SHOW_MC68020.s) : publication par graphics.library, références exactes, pas d'écriture des descripteurs OS. [Contrat S2f](M19_S2F_CLIPPING_0_15_0.md) : original immutable, stage et clés de clipping ; aucun remaniement des canaux à chaque Move. Cache et lifetime à préserver.
- Les Bobs sont dans les bitplanes du même playfield. Une priorité Sprite/playfield ne distingue pas un Bob du décor ni une priorité individuelle de Bob. Dual Playfield M21, multiplexage S3 et z-order logiciel sont hors S2g.
- Les gardes de contexte S2d refusent SprIns/UCopIns non nuls (ViewPort +12/+20). Le Copper utilisateur actif n'est donc pas à déclarer compatible aujourd'hui ; ne pas relâcher ces gardes sans preuve spécifique. Ne pas toucher canaux 0/1, FMODE, BPLCON4, couleurs, UCopList ni ViewPort étranger.

## 3. Contrat public proposé, à approuver

### S2g-P1 : choix de couche à la création

Surcharge proposée (pas une syntaxe disponible à ce jour) : `_OK=Aga Sprite(_N,_X,_Y,_I,_LAYER)`.
- LAYER 0 = auto (identique à la forme quatre arguments) ; 1 = paire 2/3 devant, 2 = 4/5 milieu, 3 = 6/7 arrière. Valable à la création de l'objet, pas de nouvelle limite sur ID, banque ou largeur.
- 1 succès ; négatif sur refus selon contrat de la commande existante. Un rang hors 0..3 est invalide (-210 dans l'entrée privée P1a). Paire demandée indisponible/incompatible : -206 proposé, aucun repli vers une autre paire ; aucune destruction des autres objets. Palette simple compatible obligatoire.
- Objet existant : 0 conserve paire actuelle ; rang explicite identique accepté ; rang différent refusé sans effet. Changement de rang volontaire via Off puis Show à partir d'une banque encore disponible ; pas de swap de canaux, tri Y dynamique, nouvelle copie de cache ni migration implicite. La forme quatre arguments garde ses octets/sémantique publique autant que possible ; AP20 et GetP/A3 à qualifier sur les deux layouts. Aucune promesse de compatibilité syntaxique avant preuve.

### S2g-P2 : priorité du playfield

Fonction proposée `_OK=Aga Sprite Playfield(_MODE)`, valeur par écran, par défaut 3 (comportement S2f). Mode = nombre de paires du moteur devant le playfield, pas le numéro de Sprite. Seuil matériel = mode+1 ; 0..3 uniquement.

| Mode | Du devant vers le fond |
| --- | --- |
| 0 | 0/1, playfield, 2/3, 4/5, 6/7 |
| 1 | 0/1, 2/3, playfield, 4/5, 6/7 |
| 2 | 0/1, 2/3, 4/5, playfield, 6/7 |
| 3 | 0/1, 2/3, 4/5, 6/7, playfield |

Protéger la priorité de 0/1, ne pas supposer la présence du curseur sur un canal précis dans toutes les configurations. 1 si réellement appliqué et vérifié ; 0 si refus sans changement confirmé. Diagnostic distinct/pending si résultat incertain et rollback non démontré, code à définir avant implémentation. Le premier périmètre autorisé à proposer : changement seulement sur écran privé de mode S2f, sans Sprite actif ni retraite pending, sans DB Safe/Disp en vol ni Copper utilisateur actif. Ne pas appeler Swap. Aucune obligation de changer de priorité à chaque frame. Étendre aux objets actifs seulement après preuve du chemin OS immédiat et de la stabilité des références.

## 4. Verrou OS à lever avant toute écriture native de priorité

[NDK videocontrol.h](https://d0.se/include/graphics/videocontrol.h) : PF1 SET/GET $80000033/$80000034, PF2 SET/GET $80000035/$80000036, IMMEDIATE $80000037 ; [Autodoc VideoControl V39/V40](https://d0.se/autodocs/graphics.library/VideoControl) : ColorMap attachée, GET modifie les TagItems, résultat zéro OS=succès, flag LONG pour IMMEDIATE cleared si tout est appliqué, sinon reconstruction nécessaire. [DisplayInfo](https://www.theflatnet.de/pub/cbm/amiga/amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node05FF.html) : DIPF_IS_SPRITES_CHNG_PRI = $00080000.

**Non vérifié à ce stade** : mapping effectif PF1/PF2 tags vers BPLCON2 normal sous V39 et V40, comportement immédiat pour ces tags (pas simplement pour BorderBlank), permanence sur Swap/renégociation largeur/rethink, état du pointeur, succès/rollback sur partial SET. Un GET seul ne prouve pas la valeur de la liste effective ni le rendu. Ne pas coder une écriture brute à $DFF104, ne pas patcher Copper vivant ou écrire ViewPort.SpritePriorities directement. Vérifier d'abord les deux GET et le champ NDK SpritePriorities en lecture seule, les capacités du ModeID, la bonne ColorMap et les listes effectives sur V39/V40. Si SET+IMMEDIATE ne peut être prouvé, ne pas lancer une reconstruction à chaud d'office. Étudier un réglage à l'ouverture (SA_VideoControl V39), ou une reconstruction contrôlée par Intuition exclusivement sans ressources actives, avec campagne dédiée. Incident IFF/MakeScreen historique à respecter. Les sources OS exactes de VideoControl et le mécanisme de rollback restent à établir ; aucune validation WinUAE de S2g à ce stade.

## 5. Qualification proposée

1. P1 en source-only après accord explicite sur la surcharge : sélection exacte des 3 couches, saturation, conflit de palette simple, slot OS occupé, rang invalide, ID déjà actif, refus de migration et refus largeur. Conservation des quatre arguments et des 105 commandes existantes ; compter les signatures/entrées AP20 réelles après ajout, pas de nombre supposé. Ordre visuel de trois glyphes asymétriques se recouvrant, tous ordres de création, mix simple/attaché, 16/32/64, clipping et Erase. Aucun mouvement implicite de canal.
2. P2 : d'abord preuve OS (lecture puis SET/GET et affichage discriminants), erreur/rollback et contrôle des références ; uniquement après ce verrou, API publique approuvée. Fond pen 0 et bandes opaques contrastées, 4 seuils, superposition des trois paires et dessin Bob dans bitplanes. Curseur et retour AMOS ; DB, plusieurs Swap et Close/reopen, avec priorité par défaut à la nouvelle ouverture. Tester explicitement refus lorsque Copper actif/pending ; ne pas déclarer cette coexistence validée. Pas de benchmark inventé.
3. Gate A : builder reproductible depuis S2f exacte, MC68020, AP20 ABI et marges UNIT142/213/PC16, deux layouts, régressions S2f/AGAPIC/AGSP/Bob/Pattern/SafePort/DB/IFF/Swap, injections d'erreur. Gate B Runtime et contrôle visuel, Chip/Fast avant/après, journal unique ; C réelle au jalon convenu (à avancer si nouvelle ABI risquée), D séparée. Seul ASC actif après autorisation de bascule, Lib/ABK vérifiées. Aucune promotion LAST_GOOD automatique.

## Décision et suite

Accord auteur « ok go » pour P1 et les signatures proposées. P1a implémente l'entrée privée et le test AP20 sans exposer encore la surcharge ; qualifier la CI, vérifier la grammaire native AMOS de surcharge et les offsets de token avant P1b. P2 reste soumis au verrou OS. Aucune activation de bibliothèque autorisée par cet accord.
