# M18/R68 — Gate B intégrée Fast Icon + CBlock, WinUAE 68030 JIT ON (13/11/2026)

## Configuration et périmètre

- **Programme testé** : [`M18_R68_COMPILER_FINAL_01.asc`](../tests/current/M18_R68_COMPILER_FINAL_01.asc), candidate de validation combinée des fonctionnalités M18 R64–R68.
- **Environnement déclaré par l'auteur** : Motorola **68030 + JIT activé**, **AMOS interprété sous WinUAE**. Fréquence, mémoire configurée et réglages supplémentaires non établis par cette capture.
- **Preuve utilisateur** : capture d'écran **de la console des résultats**, reçue le 13/11/2026. Elle ne montre pas l'écran graphique. Aucun relevé chronométré.
- **Candidate** : `dist/AMOSPro_AGA.Lib`, R68 v0.13.13, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, inchangée.
- **CI statique/CPU** : [commit 88841fe — Artifact integrity PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43485335139), vérifié après publication.

## Résultats transcrits de la console

| Contrôle | Résultat observé |
|---|---|
| `BANK FICON/CHIP`, `PUT` | `1 1` ; `1` |
| `OPEN/DB/SWAPS` | `1 1 1 1` |
| `DRAW SOURCE NONALIGN/ALIGN` | `1 1` |
| `CAPTURE NONALIGN/ALIGN` | `1 1` |
| `PIXELS 288 BYTE EQ2/EQ3` | `1 1` |
| `BAD X/Y/NEG/ID/BANK/0` | `0 0 0 0 0 0` |
| `CHIP BEFORE/AFTER CAPTURE` | `1674136 / 1674136` |
| `FAST BEFORE/AFTER CAPTURE` | `138449384 / 138449384` |
| `ABK SAVE/LOAD LEN` | `1164 / 1164` |
| `ABK RELOADED EQ2/EQ3` | `1 1` |
| `STAGE2/3 READY2/3/4` | `1 1 1 1 0` |
| `CPU/MASKED/OPAQUE/UNREADY` | `1 1 1 0` |
| `NOS/CLOSE` | `0 -1` |
| `CHIP/FAST AFTER RAM FILE` | `1845800 / 138457592` |
| `CBLOCK CAP/REST/RECAP/SAME` | `1 1 1 1` |
| `CBLOCK DRAW CPU8/BLIT/CPU16` | `1 1 1` |
| `CBLOCK LEN` | **`1064`** |
| `BAD MODE/ALIGN/DIM` | `0 0 0` |
| `CBLOCK AFTER CLOSE` | `0` |
| `RESULT` | **`1`** |
| Fin de console | **`CLOSE RETURNED`** |

Le format `AGACBLK` 32×32 sur 8 bitplanes est cohérent avec **40 octets d'en-tête + 8 × 4 × 32 = 1 064 octets**. La démo publique a été corrigée précédemment ; ce nouvel essai confirme le contrôle **dans l'ASC intégré**. Les refus et la recapture réussissent d'après les valeurs de retour et les contrôles du programme.

## Qualification et suite

**Gate B intégrée : PASS pour ce scénario, en AMOS interprété sous WinUAE 68030 avec JIT ON.** La console montre `RESULT 1` et `CLOSE RETURNED`. Elle ne démontre **pas** à elle seule la conformité visuelle des graphismes ; aucune capture graphique séparée n'a été fournie pour cet essai.

**Gate C AMOS Compiler : NON TESTÉE**, y compris pour ce programme au nom `COMPILER_FINAL`. La Gate A CPU/CI ne la remplace pas. Préserver **l'unique ASC actif** dans `tests/current/` pour la **seule compilation manuelle finale**, sur un **nouvel exécutable** créé depuis R68 installée. **Gate D machine AGA physique : NON TESTÉE**.

R68 demeure candidate **NON PROMUE** ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la **R63**, protégée. Aucune modification de binaire, des tests archivés ou de l'ASC validé ; aucun Compiler lancé par l'assistant. Branche `main` uniquement.
