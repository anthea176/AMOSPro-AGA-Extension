# M19 P2.7 — qualification des pistes AGAPIC pré-décodé / Blitter

**CAMPAGNE TERMINÉE : P2.7 Runtime PASS / Compiled PASS.** Gains mesurés, pas des FPS complets : [rapport et sources brutes](../benchmarks/RESULTATS_M19_P27_R87_CPU_RLE_FICON_BLITTER_2026-11-15.md). **Prochaine étape P2.8 : cache planaire AGAPIC à alpha indépendant + vrai Blitter masqué (non implémentés / non testés).**

**15 novembre 2026. Branche `main` uniquement.** R87 v0.13.32 active inchangée (73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`). R84 `LAST_GOOD` protégée, aucune promotion, aucun tag ou release.

## Hypothèse, pas gain annoncé

Le code `tools/m16_agapic_v2_draw_emit.py` valide le flux RLE en une première passe, le reparcourt en une seconde, puis peint les pixels dans les bitplanes Chip. `tools/m18_ficon16_native_shifted_emit.py` lit une icône FICON8 planaire de 288 octets en mots de 16 bits et écrit au CPU dans les 8 plans, sans RLE. Unity `BlitterObjects.s` utilise de son côté des mots/masques précalculés et des opérations Blitter. Ces observations justifient une **mesure d'un même motif 16×16** dans les deux représentations avant de choisir une future implémentation native plus générale.

Notre R87 dispose déjà de `Aga F Icon Bank Put`, `Aga F Icon`, `Aga Bank Image Capture`, `Aga Bank Image Draw` et `Aga Blit Copy` : **aucune nouvelle commande AP20 n'est nécessaire pour cette étape**.

## Nouveau programme de validation

Test actif unique : [`tests/current/M19_P27_R87_CACHE_CPU_BLITTER_01.asc`](../tests/current/M19_P27_R87_CACHE_CPU_BLITTER_01.asc), **Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`**. Image synthétique : 16×16, fond index 0, bloc index 5 (8×8) et accent index 6 (4×4), profondeur 8. Même banque chunky de 256 pixels pour FICON8, même dessin source capturé en AGAPIC **v1 et v2**, masque d'index 0. **Le mode transparent de ces captures correspond à l'index 0** : un masque AGAPIC indépendant plus général n'est **pas couvert** par FICON8.

### Parité avant toute performance

**9 comparaisons d'images réelles** en Runtime et Compiled : AGAPIC v1/v2 contre FICON8, opaque/transparent, X aligné et non aligné, clipping gauche/droite/haut/bas (8 scènes), puis copie opaque `Aga Blit Copy` contre FICON8 (1 scène). Pour chaque scène : remise à fond index 1, dessin 1, capture AGAPIC 32×32 ; remise à fond identique, dessin 2, capture de la même zone ; comparaison **octet pour octet de l'AGAPIC capturé**. Les captures utilisent le même codec/version, donc le test détecte une divergence de pixels. Deux banques temporaires 20/21 sont effacées après chaque paire. Une divergence ou une erreur native interdit le benchmark et produit `RESULT 0`.

**Limite** : les neuf images ne couvrent pas toutes les palettes, tailles et frontières possibles ; aucun masque alpha indépendant de la couleur zéro n'est transformé implicitement.

### Mesure dans un seul passage WinUAE

| Périmètre | Références comparées | Méthode |
|---|---|---|
| 4/8/16 Bobs, masqué | RLE AGAPIC v1/v2 vs FICON8 CPU planaire | 64 répétitions × 2 passages inversés A/B puis B/A, 12 chronos |
| 8 Bobs, opaque | FICON8 CPU vs Blitter via `Aga Blit Copy` | 64 répétitions × 2 passages inversés, 4 chronos |
| Exclu du chrono | Fond, préparation des banques, capture, cache, staging, Swap, VBL, tri Z | Temps CPU de dessin/orchestration uniquement |

Les objets des deux méthodes sont identiques (coordonnées 20+44×colonne, Y=20+44×ligne) et les positions ne chevauchent pas le slot Blitter préaffiché à (240,200). Chaque méthode dessine sur le **back buffer inactif**. On consigne les **ticks bruts par passe**, les sommes par charge et les compteurs. Une mesure ne constitue pas une preuve de FPS avec Swap/VBL.

**Interprétation :** pour chaque N et méthode, temps moyen de N Bobs en millisecondes = `ticks_totaux × 20 / (2 × 64)`, avec la convention PAL nominale documentée ; gain FICON (%) = `100 × (T_RLE − T_FICON) / T_RLE`, seulement si temps RLE non nul. On vérifiera également la variabilité AB/BA. Pour la comparaison Blitter, la source est **pré-stagée dans le même back buffer** ; le coût du staging et la gestion d'un cache permanent / double buffer sont hors chrono. **Ce résultat ne qualifie ni DMA masquée ni FPS en jeu.**

## Sorties et validation

Préflight local strict exécuté sur l'ASC exact :

`python /home/oai/skills/amos-pro-aga-rules/scripts/amos_preflight.py --strict-target --fail-on-warnings tests/current/M19_P27_R87_CACHE_CPU_BLITTER_01.asc` → **PREFLIGHT PASS**.

Le modèle `tools/test_m19_p27_cache_bench_static.py` vérifie la construction du motif et des 9 scènes simulées, la provenance P2.6, les checksums R84/R87 et la structure des chronos. Il **ne compile pas AMOS** et **n'émule pas le Blitter Amiga**.

WinUAE recommandé : **68020 / 14 MHz / PAL / JIT OFF**. Importer dans AMOS vide par **Project → Merge ASCII**, exécuter en Runtime puis compiler avec AMOS Compiler V2 le **même fichier** ; récupérer `RAM:M19_P27_RUNTIME.TXT` et `RAM:M19_P27_COMPILED.TXT`. Exiger les compteurs décrits dans [le README actif](../tests/current/README.md), absence de Guru/freezes et fermeture correcte. **Gates B et C P2.7 PASS** sur les deux journaux reçus et archivés : [Runtime](../benchmarks/M19_P27_RUNTIME.TXT), [Compiled](../benchmarks/M19_P27_COMPILED.TXT).

## Décision après résultats

1. **Si FICON8 donne un gain réel** sur les mêmes 16×16 masqués : travailler sur un cache AGAPIC planaire **sans perdre son alpha indépendant**, avec allocation explicitement propriétaire, invalidation de cache et budget Fast/Chip. Ne pas obliger les Bobs génériques à être 16×16.
2. **Si la copie Blitter opaque est intéressante** : reprendre le prototype M18 `m18_ficon_chip_ap20_emit.py` / `m18_ficon16_chip_blit_emit.py`, et seulement ensuite mesurer le *vrai* rendu masqué Chip→Chip avec temps de staging inclus ou amorti, Safe/WaitBlit, deux buffers et registres/ABI Compiler. Le prototype M18 n'est pas une commande R87 installée.
3. **Si aucun gain significatif** : profiler séparément contrôle Safe, validations de banque, écriture Chip et préparation du décor, puis envisager dirty rectangles par buffer.

**Aucune modification de `dist/AMOSPro_AGA.Lib` ou `dist/AMOSPro_AGA_LAST_GOOD.Lib`. Pas de promotion automatique.**
