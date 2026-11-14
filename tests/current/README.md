# R79 C2P Zoom — Gate B WinUAE (NON TESTÉE)

**Étape en cours :** R79 v0.13.24 `Aga C2P Zoom` (nearest-neighbour), depuis banque DATA/WORK chunky 8 bits, 10 paramètres, source et destination rectangulaires. **Gate A native à qualifier en CI avant d'installer R79. Gate B WinUAE NON TESTÉE ; Gate C AMOS Compiler à la toute fin du chantier C2P.**

**Seul ASC prévu :** [C2P_R79_ZOOM_01.asc](C2P_R79_ZOOM_01.asc). Il remplace l'ASC R78 **seulement après réussite de Gate A native et publication de la candidate R79**, sans coexistence de deux ASC actifs dans `tests/current/`. R78 Gates A/B PASS ; R73 `LAST_GOOD` protégée.

## Procédure (après autorisation de la candidate)

1. Installer la bibliothèque candidate R79 dans le slot AMOS AGA habituel, redémarrer AMOS et conserver `LIBS:c2p.library` v1.9 ; WinUAE AGA, CPU 68020+.
2. Libérer si nécessaire les banques **12 et 13**. Importer l'ASC R79 avec **Merge ASCII dans un programme vide**. Exécuter sous AMOS sans Compiler.
3. Le test exécute les 5 profondeurs **16/32/64/128/256**. Après Blit R78, Zoom R79 ajoute des sprites agrandis 32×32→64×64, réduits 32×32→16×16, des échelles non entières (13×11→29×7) et un clipping sur les quatre bords. Il vérifie les indices chunky par `Peek`, dont **0 opaque**, et six rejets sans écriture. Des blocs visuels de tailles différentes sont attendus.
4. Les tests de cycle R77/R78 restent présents : Convert/Swap explicites ; `Aga C2P Close` puis Convert/Zoom refusés, réouverture C2P, nouveau Zoom/Blit/Convert/Swap, second Close, fermeture écran.
5. **`Amos To Back` est intégré avant le dernier écran AGA 256 couleurs**. Après observation, appuyer sur **Échap**, ne pas utiliser Ctrl+C. Le test effectue `Amos To Front` après `Aga Screen Close`, efface les deux banques et revient normalement à AMOS par `End`.
6. Copier le journal volatile de **`RAM:C2P_R79_RUNTIME.TXT`** si `PRG_STATE 1`. Pour un autre mode, nom identique avec `_INTERPRETED.TXT` ou `_COMPILED.TXT`. Le fichier doit être récupéré avant tout reset ou relancement du même mode.

## Critères attendus

```text
TEST C2P-R79-ZOOM-01
VERSION R79 V0.13.24 CANDIDATE
RESULT  1
VERDICT PASS
DEPTH_TESTED  5
PASS_DEPTH  5
FAIL_DEPTH  0
BLIT_COPY_OK  5
BLIT_PIXEL_OK  5
BLIT_REJECT_OK  5
BLIT_REOPEN_OK  5
ZOOM_COPY_OK  5
ZOOM_PIXEL_OK  5
ZOOM_REJECT_OK  5
ZOOM_REOPEN_OK  5
C2P_CLOSE_OK  5
EMPTY_CLOSE_OK  5
REOPEN_OK  5
CLOSE_COUNT  5
ERR  0
NOS  0
CHIP_DELTA  0
FAST_DELTA  0
CLOSE_RETURNED  5
```

**Deltas mémoire 0 attendus** après exécution propre ; un écart devra être interprété avec les mesures complètes et l'historique des essais, pas qualifié automatiquement de fuite. Si problème de focus, relever l'écran et les événements avant d'interrompre le test.

[Contrat Zoom R79](../../docs/C2P_R79_ZOOM_CONTRACT_2026-11-14.md) · [Gate B R78](../../docs/C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) · [Règles AMOS](../../EXTENSION_SOURCE_RULES.md).
