# M19 P0j-b4 — rendu privé de 64 Bobs sans projection de sélection

**Cible MC68020 minimum, source-only. Gate A PASS : 104 contrôles**, deux implantations V2, [CI renforcée 44179811049](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44179811049), commit `56954bd`. Le banc initial avait PASS 60 cas ([CI 44174998272](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44174998272)). Le code historique P0c/P0d reste byte-identique. **Gates B/C/D non effectuées pour B4.** Cette étape termine le raccordement privé des trois dépendances initiales au shadow, **sans modifier les octets historiques des fonctions P0c/P0d**.

## Chemins natifs

`explicit_safe_blit_entry` reprend les validations d'état AGA et de back BitMap Safe du peintre P0d, résout l'image avec le P0j-b3 de la **banque d'origine**, puis rejoint le peintre P0d original après un label zéro octet : clipping, masques, Blitter et WaitBlit restent identiques.

`explicit_frame_draw_entry` lance **P0h/P0j-a pour les 64 objets avant toute opération DMA**, puis parcourt 1 à 64 en ordre croissant et revalide chaque Bob P0g, prépare sa source via le P0j-b2 explicite (cache Chip réutilisable), arme la fermeture P0c et dessine dans le **back buffer non visible**. Aucun `Aga Swap` implicite, aucune lecture ou écriture de `bank_active_state`.

## Tests

**Provenance vérifiée en CI (banc B4 initial) :** source BOBS native **20 104 octets**, SHA256 `6cde37acbee13004acf4cf23582b267a11247c28c85011896de7570c190b60e8` ; candidate AP20 **100 596 octets**, SHA256 `b6a318118d0f8c58ab839d905c4094b8de27b6f481d411c647626266d69a6a7b` ; **85 commandes**, **178 entrées AP20**, **4 unités**, PC16 max **854**. Tout est construit **en mémoire**, sans remplacement de `dist/AMOSPro_AGA.Lib`.

[Émetteur](../tools/m19_p0j_explicit_safe_draw_emit.py), [builder source-only](../tools/build_m19_p0j_explicit_safe_draw_in_memory.py), [banc pixel-exact MC68020](../tools/test_m19_p0j_explicit_safe_draw_gate_a.py). Les tests doivent exécuter deux placements V2 natifs : Bobs masqués/opaques, 64 objets issus de deux banques, front inchangé, cache Chip réutilisé sans copie à chaque frame, refus de génération périmée et image absente avant DMA, aucun Swap, SafePort non prêt et fermeture. Hook sur les 12 octets sélectionnés : **aucune écriture autorisée pendant la frame**.

**Limites importantes :** les services AmigaOS/graphics restent simulés en Gate A. Une erreur de SafePort ou une mutation des sources après que des Bobs précédents ont été peints peut laisser un **back buffer partiel non présenté**. Aucun public `Aga Bob Draw` n'est intégré, et les Gates B/C/D restent non exécutées pour b4. `dist/AMOSPro_AGA.Lib`, ASC actuel, `LAST_GOOD` R84 et archives protégés.

## Échec de frame : contrat de sécurité avant Draw public

- **Avant la première opération DMA :** P0h/P0j-a refuse les sources absentes, images invalides et identités périmées. Le test CI renforcé ajoute la corruption de longueur d'un masque AGBO du Bob 1, avec vérification qu'aucun Blit, allocation Chip ni écriture du back buffer n'a eu lieu.
- **Après le premier Blit :** un refus `SafePort`, une mutation asynchrone de banque ou une autre erreur tardive peuvent laisser le **back buffer partiellement modifié**, même si le retour privé est `D3=0` et si le front reste intact. Le nouveau test force le refus de `SafePort` au deuxième Bob après la peinture masquée du premier : l'état partiel est un risque *à isoler*, pas une réussite d'atomicité.
- **Présentation :** B4 n'appelle jamais `Aga Swap` automatiquement. Une application qui appelle elle-même `Aga Swap` après un échec **peut présenter la page partielle** : B4 ne possède pas encore de verrou de Swap. Toute API publique Draw devra exposer un résultat exploitable, interdire la présentation d'un back invalide et définir comment le reconstruire complètement. Ne pas revendiquer une frame atomique tant que cela n'est pas vérifié sous Gate A, puis B/C.
- **Choix à arbitrer avant intégration publique :** état *invalid* par page arrière contrôlé par `Aga Swap` ou protocole explicite de reconstruction + contrôle strict du retour, avec preuve que l'utilisateur ne peut pas présenter un échec silencieux. Aucun changement du cœur `Aga Swap` n'est réalisé dans B4.

**Banc renforcé validé :** les sources natives et le SHA AP20 sont inchangés ; **104 contrôles MC68020 PASS** sur deux placements. Nouveaux scénarios : clipping gauche masqué et droite opaque, masque AGBO de longueur corrompue avant DMA (aucun `BltMask`/`BltOpaque`, buffer et allocations inchangés), et `SafePort` indisponible au deuxième Bob (un seul `BltMask` effectué, front intact, back partiel, aucun Swap). Le banc distingue `WaitBlit` de synchronisation Chip et véritables dessins. Le registre Chip est nettoyé dans la simulation ; le mock ne couvre pas la fermeture complète AGA lorsque Safe reste pending, qui exige des essais B/C spécifiques. [Logs de la CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44179811049).
