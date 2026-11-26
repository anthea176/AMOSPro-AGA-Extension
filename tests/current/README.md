# S1-P2l-c — diagnostic DMA détaillé actif unique

**S1-P2l-c active (26/11/2026).** Autorisation auteur « va y ct inplicite! » après Gate A PASS. Lib 150056 octets, SHA256 `148b4d06702f84dd6de3eacd069a55c4759164bb4dd3c74f319f81e6f077f3f5`, blob `86d9497e3a2d5446001b9b41fc25d2e6a878ae50`, 105 commandes / 214 AP20, MC68020+. [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45877952385) : 532 contrôles (496 hérités + 36 détail idle). [Reconstruction exacte et préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45880559895). UNIT142 65276, marge 258 ; UNIT207 11178, PC16 max 11208, marge 21556 ; helper natif 114 octets, patch 8 octets à 10978. ASC unique 6425 octets SHA256 `25a50fd84962dcdd0a52a45d496ad3413676d37aa4b3df4c2d74391d18c4a89e`, blob `fad7c3f78a20907f25a0e8072508c5c2c9e9b409`. ABK inchangée (532 octets) et LAST_GOOD L2b protégée. B/C/D NON TESTÉES sur P2l-c ; CI post-activation à relever. Aucune libération ni réemploi DMA.

[Lib](../../dist/AMOSPro_AGA.Lib) · [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) · [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK), ABK SHA256 `225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93`.

## Exécution Runtime uniquement

1. Installer la Lib P2l-c dans APSystem, fermer WinUAE complètement puis redémarrer sans restaurer de Save State (AGA PAL, 68030/JIT ON). Relancer AMOS. Ne pas utiliser un ancien programme tokenisé/compilé.
2. Placer l'ASC et l'ABK dans le même dossier, Project → Merge ASCII. Lancer Runtime, saisir 1. Observer le Sprite se déplacer 100 fois et disparaître. Sauvegarder `RAM:M19_P2LC_P1_RUNTIME.TXT`.
3. **Uniquement si RESULT=1 et DIAG_ROUTE_OK=1**, relancer le même programme sans reset ni réinstallation, saisir 2. Aucun nouveau Sprite attendu. Sauvegarder `RAM:M19_P2LC_P2_RUNTIME.TXT`.
4. Transmettre les deux journaux. En cas de Guru/FAIL/DIAG_ROUTE_FAIL, arrêter et conserver les preuves. Pas de Compiler à ce jalon ni de debugger.

Ne pas relancer la phase 1 sans reset : le refus -123 et ERR10 restent attendus après rétention.

| Champ | Phase 1 | Phase 2 |
| --- | --- | --- |
| SOURCE_TAG | M19_S1P2LC_IDLE_DETAIL_V1 | M19_S1P2LC_IDLE_DETAIL_V1 |
| PRG_STATE | 1 | 1 |
| SPRITE_RC | 1 | -123 attendu |
| MOVE_RC / MOVES | 1 / 100 | -999 / 0 |
| SOURCE_ERASED | 1 | 1 |
| OFF_RC / CURSOR_RC / CLOSE_RETURNED / CLOSED | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 |
| BANK_FREE_RC | 0 | 0 |
| CLEAN_ERR / ERR / RESULT | 0 / 0 / 1 | 0 / 0 / 1 |
| DIAG_START | -131 | relever |
| DIAG_ACTIVE | -180 | relever |
| DIAG_CLOSE / DIAG_FRONT | relever / relever | relever / relever |
| DIAG_ROUTE_OK | 1 | 1 |
| DMA_FREE_PROVEN | 0 | 0 |
| VERDICT | PASS_DISPLAY_CLOSE_RETAINED_ONLY | PASS_QUARANTINE_NO_NEW_DISPLAY |

## Observations DMA

DIAG_CLOSE immédiatement après Close, DIAG_FRONT après Amos To Front et quatre Wait Vbl. Le détail -256-MASK (1 à 63) cumule les bits : 1 ActiView non nul (-257), 2 LOF (-258), 4 SHF (-260), 8 WAIT terminal (-264), 16 copinit non vérifiable (-272), 32 copinit changé (-288). Si base non vérifiable, pas d'évaluation LOF/SHF/WAIT ; si base change, relevé incomplet. -185 reste possible si transitoire. Retours P2l-b préservés : -180 reçu Close/record manquant, -181 record non mappé, -182 flags, -183 géométrie, -184 Gfx, -186 layout, -187 référence privée/canal, -188 changement de bases, -189 restitution du verrou refusée (anormal), -190 deux observations compatibles seulement.

OBS_PENDING et OBS_COMPATIBLE_ONLY ne prouvent aucune libération DMA. Le diagnostic temporaire Bank Free(-19000) n'est pas une API de production. Aucun nouveau réemploi ; le refus -123 reste volontaire. [Rapport P2l-c](../../docs/M19_S1_P2L_C_IDLE_DETAIL_2026-11-26.md) · [Historique P2l-b, Runtime PASS 2/2 et FAIL initial](../../docs/M19_S1_P2L_B_DIAG_ROUTE_2026-11-26.md). Logs distincts par phase et mode ; préserver les originaux.
