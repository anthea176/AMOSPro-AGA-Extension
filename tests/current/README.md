# S1-P2m — cycle de vie Sprite, campagne active unique

**26/11/2026 — clôture fonctionnelle P2m, accord auteur « oui passons a la suite du chantier sprite » puis « ok go ».** Gate B Runtime fonctionnelle validée (trois derniers PASS stricts), Gate C Compiler fonctionnelle 2/2 (PASS strict 1/2 ; ERR14 sur écart Fast temporaire 128 octets). Aucun écart net de Chip/Fast par exécution. D physique non testée. Auteur accepte la clôture fonctionnelle avec réserve ; aucune promotion LAST_GOOD. Les fichiers RAM conservés expliquent les différences entre lancements selon l'auteur ; leur coût exact n'a pas été isolé. La Lib et l'ASC exacts restent actifs, LAST_GOOD L2b protégée. Prochaine étape S2a : changement d'image à chaud, source-only avant Gate A, sans nouveau token. [Résultats et journaux originaux](../../docs/M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md).

Campagne ci-dessous exécutée ; ne pas répéter les essais P2m sans anomalie nouvelle.

**26/11/2026 — S1-P2m active sur main, Gate A complète PASS.** Lib 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, blob `a29e86a6414021e19b87615681dcc08fe406518c`, 105 commandes / 214 AP20, MC68020+. [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891037257) (source ee70cdf84e4ec1896eb657b07e2a2876d2244932) : 100 cycles et 10 fermetures par modèle AP20, cas négatifs, 184 Pattern, 172 SafePort, 10 suites Bob, DB/IFF/Swap/capture ; reconstruction identique et préflight strict PASS. [Reconstruction indépendante](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891360197). UNIT142 65424 (110 libres), UNIT207 10380 (22354 libres PC16), PC16 max 10410. ASC 6700 octets SHA256 `84d2dfddc753e2c05d8a05ff991fe8b4f3e6d36daa20110cc447add547aaa684`, blob `ddd9b676b9a3d4c0f4cccf08ca058cade61df9aa`. À la livraison : B/C/D non testées (voir actualisation ci-dessus). LAST_GOOD L2b et ABK inchangées. Autorisation auteur « continu livre moi cette lib ». P2l-c historique rejetée en relance fonctionnelle.

## Fichiers
- [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`.
- [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc), 6700 octets, SHA256 `84d2dfddc753e2c05d8a05ff991fe8b4f3e6d36daa20110cc447add547aaa684`.
- [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK), 532 octets, SHA256 `225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93`.

## Gate B — Runtime réel
1. Copier la Lib dans APSystem, conserver le slot d'extension. WinUAE AGA PAL, 68030 JIT ON. Redémarrage complet unique sans Save State lors du changement de Lib (schéma de registre v3).
2. Placer ASC et ABK ensemble. Importer l'ASC exact par Merge ASCII. Exécuter en Runtime (PRG_STATE=1). Aucun Erase All ni reset entre lancements.
3. Faire trois lancements successifs. Sauvegarder chaque journal RAM:M19_P2M_RUNTIME.TXT séparément avant écrasement. Vérifier visuellement affichage, déplacement, disparition et retour à AMOS.
4. Attendu par lancement : OPENED=10, CLOSED=10, SHOWN=100, MOVED=100, OFF_COUNT=100, AUTO_CLOSE=10, SPRITE_RC=MOVE_RC=OFF_RC=FREE_RC=1, CHIP_CYCLE_LOSS=FAST_CYCLE_LOSS=CHIP_SCREEN_LOSS=FAST_SCREEN_LOSS=0, RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_FUNCTIONAL_LIFECYCLE. Comparer Chip/Fast avant/après et entre lancements. Premier Close référence stabilisée, pas une preuve de fuite nulle au premier passage.
5. Si échec, conserver le premier journal et ne pas poursuivre les lancements. Gate C vrai AMOS Compiler seulement après Gate B fonctionnelle. D matériel distincte.

[Rapport technique et journaux historiques P2l-c](../../docs/M19_S1_P2M_FUNCTIONAL_LIFECYCLE_2026-11-26.md). Aucun test de quarantaine P2l-c à relancer.
