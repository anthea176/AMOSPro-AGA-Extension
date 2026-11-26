# S1-P2k r4 — test Runtime transactionnel actif unique

**Lib exacte :** [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 149080 octets, SHA256 `ecfee351e9afbff95dfbfd16ab805b896e8c4889147f70136dd5b1c8dcbdee41`, MC68020+, 105 commandes / 214 AP20. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45705955562). ASC [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 4630 octets, SHA256 `987d45cd1f14aa62df944c7af35eda6884b0a44a70d3b7f0415e0ff2dd8a2c1e`, [préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45786061729). ABK [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK), 532 octets, SHA256 `225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93`. B Runtime et C Compiler deux phases PASS (26/11/2026) ; D non testée. LAST_GOOD L2b inchangée.

Installer la Lib dans APSystem, **reset WinUAE une fois** (AGA PAL, 68030/JIT ON), redémarrer AMOS, placer ASC et ABK dans le même dossier et Merge ASCII. Lancer en Runtime, saisir 1. Voir le Sprite 16x16 se déplacer 100 fois, disparaître puis revenir à AMOS. Sauvegarder le journal `RAM:M19_S1P2K_PHASE1.TXT`. Seulement si PASS, relancer le même programme en Runtime sans reset ni réinstallation, saisir 2. Aucun Sprite ne doit apparaître ; retour à AMOS. Sauvegarder `RAM:M19_S1P2K_PHASE2.TXT`. Transmettre les deux journaux.

| Champ | Phase 1 | Phase 2 |
| --- | --- | --- |
| SPRITE_RC | 1 | -123 |
| MOVE_RC | 1 | -999 (non exécuté) |
| MOVES | 100 | 0 |
| SOURCE_ERASED | 1 | 1 |
| OFF_RC / CURSOR_RC / CLOSE_RETURNED / CLOSED | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 |
| BANK_FREE_RC | 0 | 0 |
| CLEAN_ERR / ERR / RESULT | 0 / 0 / 1 | 0 / 0 / 1 |
| VERDICT | PASS_DISPLAY_CLOSE_RETAINED_ONLY | PASS_QUARANTINE_NO_NEW_DISPLAY |

-123 est le refus attendu de la nouvelle allocation quand le record exposé est conservé. -132/-136/-137 sont anormaux ; ERR10/13 identifient un mauvais résultat Sprite en phase 1/2. ERR12 = Move. CLEAN_ERR bits 0 Off, 1 curseur, 2 Close, 3 rétention inattendue. DMA_FREE_PROVEN 0, pas de réaffichage, pas de récupération DMA. Les mesures Chip/Fast sont informatives : aucun seuil de variation OS n'est inventé. Ne pas confondre PASS de quarantaine et affichage. Si Guru/échec, ne pas poursuivre, conserver le journal. Aucun debugger requis. [Rapport détaillé](../../docs/M19_S1_P2K_TRANSACTION_2026-11-25.md). Ancien banc P2j exact conservé dans Git et tests/proto/sprite_s1_p2j.

**Résultats réels Runtime du 26/11/2026 :** [phase 1](../../docs/evidence/M19_S1P2K_PHASE1_RUNTIME_2026-11-26.TXT) et [phase 2](../../docs/evidence/M19_S1P2K_PHASE2_RUNTIME_2026-11-26.TXT) correspondent au tableau. Chip -200 et Fast -168 en phase 1 ; aucune variation nette en phase 2 ; Fast -544 entre les phases, origine indéterminée. Gate B PASS sur cette campagne seulement, DMA_FREE_PROVEN=0. Les journaux d'origine sont protégés par leurs empreintes dans le rapport. Le même scénario a ensuite été validé en compilé : [phase 1](../../docs/evidence/M19_S1P2K_PHASE1_COMPILED_2026-11-26.TXT) et [phase 2](../../docs/evidence/M19_S1P2K_PHASE2_COMPILED_2026-11-26.TXT), PRG_STATE -1 / COMPILED. Tous les résultats correspondent au tableau, avec les mêmes variations mémoire pendant chaque phase. Entre phases compilées, Chip -8 et Fast -608, origine indéterminée. Gate C PASS sur ce scénario seulement. Aucun nouveau banc, aucune libération DMA et aucune promotion.
