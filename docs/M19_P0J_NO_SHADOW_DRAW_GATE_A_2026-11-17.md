# M19 P0j-b4 — rendu privé de 64 Bobs sans projection de sélection

**Cible MC68020 minimum, source-only, Gate A en attente.** Cette étape termine le raccordement privé des trois dépendances initiales au shadow, **sans modifier les octets historiques des fonctions P0c/P0d**.

## Chemins natifs

`explicit_safe_blit_entry` reprend les validations d'état AGA et de back BitMap Safe du peintre P0d, résout l'image avec le P0j-b3 de la **banque d'origine**, puis rejoint le peintre P0d original après un label zéro octet : clipping, masques, Blitter et WaitBlit restent identiques.

`explicit_frame_draw_entry` lance **P0h/P0j-a pour les 64 objets avant toute opération DMA**, puis parcourt 1 à 64 en ordre croissant et revalide chaque Bob P0g, prépare sa source via le P0j-b2 explicite (cache Chip réutilisable), arme la fermeture P0c et dessine dans le **back buffer non visible**. Aucun `Aga Swap` implicite, aucune lecture ou écriture de `bank_active_state`.

## Tests

[Émetteur](../tools/m19_p0j_explicit_safe_draw_emit.py), [builder source-only](../tools/build_m19_p0j_explicit_safe_draw_in_memory.py), [banc pixel-exact MC68020](../tools/test_m19_p0j_explicit_safe_draw_gate_a.py). Les tests doivent exécuter deux placements V2 natifs : Bobs masqués/opaques, 64 objets issus de deux banques, front inchangé, cache Chip réutilisé sans copie à chaque frame, refus de génération périmée et image absente avant DMA, aucun Swap, SafePort non prêt et fermeture. Hook sur les 12 octets sélectionnés : **aucune écriture autorisée pendant la frame**.

**Limites importantes :** les services AmigaOS/graphics restent simulés en Gate A. Une erreur de SafePort ou une mutation des sources après que des Bobs précédents ont été peints peut laisser un **back buffer partiel non présenté**. Aucun public `Aga Bob Draw` n'est intégré, et les Gates B/C/D restent non exécutées pour b4. `dist/AMOSPro_AGA.Lib`, ASC actuel, `LAST_GOOD` R84 et archives protégés.
