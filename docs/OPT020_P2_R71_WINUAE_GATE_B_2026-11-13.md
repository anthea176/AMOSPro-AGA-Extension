# OPT020/P2 R71 v0.13.16 — Gate B WinUAE interprétée PASS

**Validation : 13 novembre 2026.** Deux captures de l'auteur (rendu AGA et console AMOS), à partir de l'ASC `OPT020_P2_R71_INTERPRETED_01.asc`. L'écran AGA et la console sont visibles ; aucun Guru ni blocage signalé. **Gate B PASS pour le scénario effectivement exécuté**, sans prétendre à une comparaison automatique des pixels ou à un test Compiler.

## Identité et preuves

- [R71 v0.13.16 dans Git à la date du test](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/b333c0dc414c78e1a488a733e1920b7febf84835/dist/AMOSPro_AGA.Lib), **51 460 octets**, SHA256 `1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0`; 64 commandes / 71 entrées AP20.
- [ASC exact du scénario](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/b333c0dc414c78e1a488a733e1920b7febf84835/tests/current/OPT020_P2_R71_INTERPRETED_01.asc). Banque de test `M16_AGAPIC_SAMPLE_BANK10.abk` (1 836 octets).
- Captures originales jointes à la conversation : `image(20261113-222131).png` (graphique) et `image(20261113-222144).png` (console) ; **non déposées sur GitHub**.
- [CI OPT020 CPU/ABI/P2 et contrôle des branches : PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43517634053). [CI générale complète : PASS (51 étapes)](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43518224389).
- R68 `LAST_GOOD` **inchangée**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. R71 **non promue**. R70 conserve son échec Guru `80000004` dans l'historique.

## Relevé de console (capture auteur)

```text
OPT020-P2-R71-INTERPRETED-01
OPT020 P1e+P2 - GATE B ONLY
P2 O/M/SHIFT  1  1  1
P2 CLIP L/R/T/B  1  1  1  1
P2 OUT/BAD P/L/M/X/NOS  1  0  0  0  0  0
OPEN  1 DB  1 SW0  1 SAFE  1
FRAMES  1  1  1  1 SHIFT  1
CLIP  1  1  1  1 OUT  1
EDGE/PART/MASK OPAQUE  1  1  1
BAD BANK/X/Y/W/M  0  0  0  0  0
LEGACY  1 SWAP  1 NOS  0 CLOSE -1
CHIP BEFORE/END  1661542  1661542
RESULT 1
CLOSE RETURNED
```

La console confirme le succès des chemins opaques et masqués, le clipping sur les quatre bords, les refus attendus à zéro, l'ancienne délégation `Aga Bank Image Draw`, le double buffering, les appels `Clear`/`Fill` avant `Draw`, et le retour après fermeture. Le total de Chip RAM libre est **1 661 542 octets avant et après** pour cette exécution : aucune fuite détectée par cet indicateur.

## Contrôle du rendu et limites

La capture AGA montre la palette vive, les motifs opaques rectangulaires, les zones masquées arrondies, les découpes visibles sur les quatre bords et le fond uniforme. Aucun défaut évident ni comportement du Guru R70 n'apparaît. Les très petits fragments aux limites correspondent aux tests de clipping ; **les captures seules ne constituent pas une preuve de conformité pixel par pixel**.

Le bandeau du test est `GATE B ONLY`. La configuration déclarée du banc reste WinUAE AGA, 68020/14 MHz, JIT OFF, PAL ; les captures ne démontrent pas à elles seules les réglages précis. Aucun résultat de vitesse P2 n'a été mesuré lors de cette validation.

| Gate | Statut |
| --- | --- |
| A — CPU/CI native, ABI et branchements AP20 | **PASS** |
| B — AMOS interprété WinUAE, console et visuel | **PASS** (scénario documenté) |
| C — AMOS Compiler réel, exécutable recompilé | **NON TESTÉE** |
| D — Amiga physique AGA | **NON TESTÉE** |
| Comparaison automatique pixel à pixel R69/R71 | **NON EXÉCUTÉE** |

## Suite

L'audit du code P2 a repéré un **cas limite indépendant** : si les données RLE sont modifiées en cours d'exécution *entre* la prévalidation PASS 0 et la peinture PASS 1, le noyau peut avoir modifié `D3` avant un `reject` tardif ; ce rejet doit impérativement renvoyer `D3=0`. Ce scénario n'est **pas couvert** par l'ASC R71, qui utilise une banque stable. Conserver la R71 validée telle quelle et réaliser le durcissement en candidate distincte avec test CPU de mutation après PASS 0.

**Aucune promotion de LAST_GOOD ; pas d'essai AMOS Compiler à ce stade.**
