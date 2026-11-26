# S1-P2l-b — diagnostic DMA actif unique

**Lib exacte :** [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 149940 octets, SHA256 `d9b690287c82c52a766d5ab4b015bb29d25057cbe55a630c0e30d88d46bd4ab1`, MC68020+, 105 commandes / 214 AP20. [Gate A PASS (496 contrôles)](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45867701424). [Reconstruction et préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45874276747). ASC [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 5998 octets, SHA256 `a4ab96585d9e95c65dfaf42b76d9ba8b764c4e50e5cbd2d97d56a1947712d239`. ABK [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK), 532 octets, SHA256 `225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93`. B/C/D non testées. LAST_GOOD L2b inchangée. Parent P2k r4 validé B/C, [preuves](../../docs/M19_S1_P2K_TRANSACTION_2026-11-25.md).

Installer la nouvelle Lib dans APSystem, **reset WinUAE une seule fois** (AGA PAL, 68030/JIT ON), redémarrer AMOS, placer ASC et ABK dans le même dossier et Project -> Merge ASCII. Lancer en Runtime, saisir 1. Observer le Sprite 16x16 se déplacer 100 fois, disparaître, puis revenir à AMOS. Sauvegarder `RAM:M19_S1P2LB_PHASE1.TXT`. Si RESULT=1 et DIAG_ROUTE_OK=1, relancer le même programme **sans reset ni réinstallation**, saisir 2. Aucun nouveau Sprite ne doit apparaître. Sauvegarder `RAM:M19_S1P2LB_PHASE2.TXT`. Transmettre les deux journaux. Si Guru, FAIL ou DIAG_ROUTE_FAIL, ne pas poursuivre, conserver la trace. Pas de debugger.

| Champ | Phase 1 | Phase 2 |
| --- | --- | --- |
| SPRITE_RC | 1 | -123 attendu |
| MOVE_RC / MOVES | 1 / 100 | -999 / 0 |
| SOURCE_ERASED | 1 | 1 |
| OFF_RC / CURSOR_RC / CLOSE_RETURNED / CLOSED | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 |
| BANK_FREE_RC | 0 | 0 |
| CLEAN_ERR / ERR / RESULT | 0 / 0 / 1 | 0 / 0 / 1 |
| DIAG_START | -131 (registre absent) | relever |
| DIAG_ACTIVE | -180 (record actif) | relever |
| DIAG_CLOSE / DIAG_FRONT | relever / relever | relever / relever |
| DIAG_ROUTE_OK | 1 | 1 |
| DMA_FREE_PROVEN | 0 | 0 |
| VERDICT | PASS_DISPLAY_CLOSE_RETAINED_ONLY | PASS_QUARANTINE_NO_NEW_DISPLAY |

## Observations indépendantes

DIAG_CLOSE est relevé immédiatement après Close ; DIAG_FRONT après Amos To Front et quatre Wait Vbl. Phase 2 : le registre conservé doit être sondable, sans présumer d'un View idle. Codes : -180 reçu Close/record manquant, -181 record non mappé, -182 flags, -183 géométrie, -184 Gfx, -185 View non idle, -186 layout, -187 référence privée/canal, -188 changement de bases, -189 restitution du verrou refusée (anormal), -190 deux observations compatibles. -190 ne prouve pas le détachement universel du DMA. OBS_COMPATIBLE_ONLY et OBS_PENDING sont des observations indépendantes du verdict d'affichage ; DIAG_ROUTE_FAIL indique un retour inattendu. Aucun FreeVec exposé, aucun réemploi. Ne pas traiter Bank Free(-19000) comme une API de production ; diagnostic temporaire limité à ce banc. Les retours normaux de Bank Free(29) restent 0. Mesures Chip/Fast informatives. La Gate C nécessitera un nouvel exécutable compilé avec cette Lib, reset initial puis mêmes deux phases et journaux distincts. [Rapport détaillé](../../docs/M19_S1_P2L_B_DIAG_ROUTE_2026-11-26.md).
