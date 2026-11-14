# M19 P1 — Validation WinUAE Runtime, enregistrée le 15/11/2026

**Preuves transmises :** `M19_P1_AGAPIC_BOBS_RUNTIME.TXT` et capture WinUAE `image(20261114-230347).png`. Programme `tests/current/M19_P1_AGAPIC_BOBS_01.asc`, bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée, écran AGA privé 320×256×256, double buffering et AMAL manuel.

## Journal reçu

| Indicateur | Valeur |
|---|---:|
| RUN_MODE / PRG_STATE | RUNTIME / 1 |
| CPU / CPU_ATTNFLAGS | 68030 / 32823 |
| RESULT / VERDICT / ERR | **1 / PASS / 0** |
| CAP_OK / META_OK | 6 / 6 |
| PROBE_OK / PIXEL_DIFF | 1 / 1 |
| FRAME_OK | 240 |
| MOVE_X0 / MOVE_Y1 | 239 / 239 |
| FRAME_SWITCH0 / FRAME_SWITCH1 | 15 / 10 |
| ORDER_FLIPS / OVERLAP_FRAMES | 3 / 46 |
| CLIP_OK | 240 |
| DRAW_FAIL / SWAP_FAIL | **0 / 0** |
| CHIP_BEFORE / CHIP_AFTER / CHIP_DELTA | 1 842 240 / 1 842 240 / **0** |
| FAST_BEFORE / FAST_AFTER / FAST_DELTA | 138 380 888 / 138 380 888 / **0** |
| CLOSE_RETURNED | **1** |

**Conclusion : Gate B M19 P1 PASS pour WinUAE Runtime sur 68030 en 8 plans.** Tous les critères du banc actif sont satisfaits. La capture fixe montre les formes colorées et le clipping sur les quatre côtés. Les 46 chevauchements viennent du calcul de recouvrement des rectangles ; la sonde RLE indique seulement que **le pixel témoin** change lorsqu'on inverse l'ordre de dessin. Le delta mémoire à 0 n'est pas une garantie universelle d'absence de fuite. Une capture en pause ne prouve pas l'absence de scintillement pendant l'animation.

**Non testé :** M19 AMOS Compiler Gate C, `PRG_STATE 0` strict, Amiga AGA physique Gate D, profondeurs 4–7 plans et sprites matériels P3. Aucune nouvelle commande ni modification du binaire R84.

## CI : incident documentaire indépendant

Le workflow [Artifact integrity du commit source P1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43650690855) a échoué dans `tools/test_readme_api_coverage.py` : `English: wrong README API version, expected '**Current library API R84 0.13.29**'`. Les deux README, inchangés dans le commit source P1, utilisaient des marqueurs de version différents de ceux exigés par le contrôle statique. Des échecs analogues précèdent P1. Les libellés EN/FR sont ajustés dans ce commit de documentation. **Une nouvelle CI reste à vérifier** pour constater l'effet du correctif ; aucun PASS CI n'est présumé.

**Étape suivante :** spécification du contrat de gestion des objets P2 (identifiant, source, position, visibilité, Z, hotspot, état AMAL, nettoyage). **Aucune signature ni implémentation native sans validation explicite préalable**.

[Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md) · [Roadmap](ROADMAP.md) · [Test actif P1](../tests/current/M19_P1_AGAPIC_BOBS_01.asc)
