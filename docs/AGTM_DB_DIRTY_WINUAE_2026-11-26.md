# AGTM — deux pages et carte dynamique, résultats WinUAE du 26/11/2026

**Prototype AMOS : Runtime B PASS et Compiler C PASS.** Ni moteur natif AGTM ni scrolling matériel qualifiés.

## Sources et journaux originaux

- [ASC testé](../tests/proto/agtm_prototype/AGTM_DB_DIRTY_BENCH.asc) : blob Git `8aa8776e15b4f071c7c5d3069e028f922d80155c`, SHA256 `5a2749c931cb3317a39de478b4c0d1bb0dcbf19d1a30414cc3ecd632fbcee80e`, 12012 octets, inchangé.
- [Runtime](evidence/AGTM_DB_RUNTIME_2026-11-26.TXT) : 872 octets, SHA256 `dccbb0628ffc7917776fd9716c1d9929e5e1791794b270126fd97b191f910cb3`, blob `6a4472a44e685d0edae744b6f803eb36b2489608`.
- [Compiler](evidence/AGTM_DB_COMPILED_2026-11-26.TXT) : 873 octets, SHA256 `771c4f903401ab723fed512a05323e07abd621d31f54e3bd4967c733a9dd62bc`, blob `8a9ef94ee4bcf80226032ee150f0562bed0445f6`.

CRLF et octets originaux conservés. Les deux logs identifient le test, la référence attendue P2d-L2b et Prg State 1/-1 ; la SHA installée, le CPU, la fréquence, le JIT, le mode PAL/NTSC et la version du Compiler restent à confirmer. Ne pas attribuer les chiffres à un A1200 standard sans preuve.

## Conformité

| Contrôle | Runtime | Compiler |
|---|---:|---:|
| RESULT / ERR | 1 / 0 | 1 / 0 |
| CHECKS / COMPARE_BYTES / BYTE_MISMATCH | 12 / 983040 / 0 | 12 / 983040 / 0 |
| ORACLE_CHECKS / ORACLE_BAD | 72 / 0 | 72 / 0 |
| BENCH_RUNS / FRAMES_PER_RUN | 4 / 12 | 4 / 12 |
| SWAPS / SWAP_WAITS / INIT_SAFE_WAITS | 70 / 2 / 0 | 70 / 2 / 0 |
| CHIP_BEFORE / CHIP_AFTER | 1838144 / 1838144 | 1792960 / 1792960 |
| FAST_BEFORE / FAST_AFTER | 138262744 / 138262744 | 137954008 / 137954008 |
| CLOSE_RETURNED | 1 | 1 |

Compte par série de 12 frames : FULL 4116 icônes opaques + 1011 overlays ; SCROLL 480 opaques + 127 overlays + 11 copies + 21 patches (les patches sont déjà inclus dans les appels d'icônes). Compteurs identiques aux prévisions du modèle hôte dans les deux modes.

## Mesures

Vue 320×256, huit plans, carte AGTM 64×32, deux couches dont une transparente (la couche de fond est opaque), 12 edits par parcours, caméra horizontale/verticale/diagonale. Deux passes AB/BA, 12 frames par série. La validation graphique précède les mesures.

| Mode | Méthode | DRAW p0 / p1 | FRAME p0 / p1 |
|---|---|---:|---:|
| Runtime | FULL | 478 / 480 | 491 / 492 |
| Runtime | SCROLL | 81 / 81 | 95 / 95 |
| Compiler | FULL | 358 / 358 | 370 / 370 |
| Compiler | SCROLL | 66 / 65 | 79 / 79 |

| Mesure cumulée sur 24 frames | Runtime | Compiler |
|---|---:|---:|
| FULL DRAW | 958 | 716 |
| SCROLL DRAW | 162 | 131 |
| Rapport DRAW | 5,91 | 5,47 |
| FULL FRAME | 983 | 740 |
| SCROLL FRAME | 190 | 158 |
| Rapport FRAME | 5,17 | 4,68 |

DRAW : somme des différences Timer par frame, donc résolution grossière à chaque mesure. FRAME : différence Timer sur la série complète ; inclut modifications de carte, dessin, gestion des pages, Swap et attente VBL explicite, hors initialisation et captures. C'est l'indicateur global de référence. Si Timer = 50 Hz, SCROLL FRAME Compiler correspond à 131,7 ms/frame (environ 7,6 mises à jour/s), hors logique de jeu et Bobs. Réduction globale Compiler 78,65 %. Aucune perte nette Chip/Fast observée à la fin des deux lancements.

## Suite expérimentale

Comparer le chemin CPU FICON8, le chemin Blitter FICHIP8 pré-stagé et une politique hybride sur **le même parcours SCROLL**, avec coûts de staging, mémoire Chip et contrôles de pixels séparés. Aucun gain Blitter anticipé. Les prototypes restent dans tests/proto/ ; M20 natif après M21, sans modification de la bibliothèque, de LAST_GOOD, des sources ASM ni de la campagne Sprite. Gate D non testée.
