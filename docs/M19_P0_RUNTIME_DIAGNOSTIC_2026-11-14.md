# M19 P0 — WinUAE Runtime et diagnostic du clignotement (14/11/2026)

## Provenance et configuration

Journal transmis par l'auteur : `M19_P0_AMAL_BOBS_RUNTIME.TXT` (22 lignes).
Test `tests/current/M19_P0_AMAL_BOBS_01.asc`, bibliothèque **R84 v0.13.29 LAST_GOOD**, écran Intuition AGA privé en 320x256x256, deux canaux AMAL mémoire, deux Bobs logiciels `Aga F Icon`, `Aga Blit Fill` et `Aga Swap`.

**Attention :** ce journal concerne **le code initial avec alternance d'images** ; le correctif à images fixes a été confirmé **visuellement** par l'auteur, sans second fichier de résultats. Ne pas transférer les statistiques de l'ancien run au nouveau.

## Résultat communiqué

| Champ journal | Valeur |
|---|---:|
| `RUN_MODE` | `RUNTIME` |
| `PRG_STATE` | 1 |
| `CPU` | `68030` |
| `CPU_ATTNFLAGS` | 32823 |
| `RESULT`, `VERDICT`, `ERR` | 1, PASS, 0 |
| `FRAME_OK` | 211 |
| `MOVE_X0`, `MOVE_Y1` | 210, 210 |
| `DRAW_FAIL`, `SWAP_FAIL` | 0, 0 |
| `CHIP_BEFORE`, `CHIP_AFTER` | 1838872, 1838872 |
| `FAST_BEFORE`, `FAST_AFTER` | 138373256, 138373256 |
| `CLOSE_RETURNED` | 1 |

Conclusion strictement prouvée : **M19 P0 Gate B sous Runtime/WinUAE PASS dans ce scénario** ; les deux déplacements et la sortie propre sont confirmés. Zéro refus `Aga F Icon`/`Aga Swap`, aucun delta mémoire observé. Ce journal ne prouve pas à lui seul l'intégrité pixel par pixel du double buffering.

## Clignotement et résolution

La version initiale définissait dans les chaînes AMAL :

- premier canal : `Let A=3-A` : alternance des images 1 et 2 à chaque `Synchro` ;
- deuxième canal : `Let A=7-A` : alternance des images 3 et 4.

Comme les quatre images de test ont des indices de couleur différents, cette alternance rapide produit un **clignotement visuel**, même lorsque les dessins et swaps aboutissent. L'auteur a **retiré les deux alternances**, essayé la modification sous WinUAE et **confirmé que le clignotement disparaît**.

**Décision de suivi :** inscrire cette variante stable dans le test actif sur `main`, en gardant `A=1` et `A=3`. Pour P1, les changements d'image devront être **cadencés et vérifiés**, plutôt qu'inversés automatiquement à chaque frame. On ne conclut **pas** à un défaut de Safe/Swap pour ce cas à partir du clignotement initial.

## Validation et protection

- Avant modification GitHub : P0 initial **Runtime/WinUAE PASS**, altération visuelle connue liée à l'alternance AMAL.
- Après suppression des deux instructions AMAL : confirmation **visuelle** de l'auteur ; **pas de nouveau journal de validation** fourni à cette date.
- Gate C AMOS Compiler : **NON TESTÉE sur M19 P0**.
- Gate D Amiga physique et exécution strictement interprétée `PRG_STATE 0` : **NON TESTÉES sur M19 P0**.
- R84 `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` : **aucun changement**.
- Aucun nouveau token AP20, aucune nouvelle API, aucune branche nouvelle.

[Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md) · [Test courant](../tests/current/M19_P0_AMAL_BOBS_01.asc) · [Roadmap](ROADMAP.md)
