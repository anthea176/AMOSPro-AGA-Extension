# S1-P2d — audit automatique des références Sprite/Copper

**P2d r2 exécuté : séquence Runtime PASS ; références OS confirmées par réanalyse du journal. Ne pas relancer à l'identique.** Garder la Lib P1i : 142968 octets, SHA256 2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3. Source [SPRITE_OS_PROBE.asc](SPRITE_OS_PROBE.asc) : 13509 octets ASCII LF, SHA256 445512ac68c0049412dcfdeeb0f06f3912d3a3fcc536facadd9e7d9c2b4e8e0b, blob 4b74f84874ce0f417d0abab17ef73f8314336a28. Préflight local strict sans avertissement PASS ; pas de Runtime/Compiler/matériel validé. [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK) : 532 octets, SHA256 225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93, même blob historique 46b701afd29720060dc9722af3ad8714e4b318c5, aucune autre ressource.

## Exécution

Snapshot préalable WinUAE, configuration P2b/P2c habituelle (AGA, PAL, 68030, graphics.library V39/V40, aucun changement de JIT nécessaire). Banque 29 libre. Mettre les deux fichiers ensemble, Project -> Merge ASCII dans programme vierge, Runtime une seule fois. Laisser terminer. Récupérer **RAM:M19_S1P2D2_OS_RUNTIME.TXT** puis restaurer le snapshot, même en cas d'erreur. Ne pas libérer le bloc exposé manuellement.

## Ce que la sonde observe

Six phases : 0 avant acquisition, 1 image active après 100 mouvements, 2 après blank + 150 VBL, 3 après FreeSprite des deux canaux avant fermeture, 4 après fermeture + 3 WaitTOF, 5 après 60 WaitTOF additionnels. À chaque phase, lecture seule : version et taille GfxBase ; réservations, table des huit SimpleSprite*, adresses ActiView, copinit, LOFlist/SHFlist ; seize MOVE SPRxPTH/PTL dans copinit.sprstrtup (les 16 registres doivent être présents sans doublon). Les huit pointeurs Copper sont reconstruits et les huit pointeurs de descripteurs comparés à toute la plage privée. TypeOfMem aux extrémités, sauf exception basse V40 documentée ci-dessous ; taille de bibliothèque et alignement vérifiés, contrôle de stabilité par relecture. Les pointeurs LOF/SHF et ActiView sont seulement journalisés, pas déréférencés : évite un parcours dynamique non borné. Ces contrôles réduisent le risque mais ne garantissent ni la validité de toute la RAM ni une lecture atomique. Aucun registre DMA ou champ système écrit par l'audit.

Résultat souhaité :
```
SAMPLES 6 AUDIT_BAD 0 POST_WAITTOF 60
ACTIVE_POSITIVE 1 BLANK_POSITIVE 1
CLOSE_REFS 0 FINAL_REFS 0
CHIP_HELD 244 DMA_FREE_PROVEN 0
RESULT 1
ERR 0
VERDICT PASS_OS_REFERENCE_SNAPSHOTS_ONLY
```

FREE_REFS peut être non nul après FreeSprite : le relevé tranche. ACTIVE_POSITIVE requiert le vrai pointeur image canal 2, ses deux réservations et les deux descripteurs exacts. BLANK_POSITIVE requiert la redirection vers le tampon transparent. Si un des contrôles positifs manque ou une lecture ne respecte pas le layout : INCONCLUSIVE_OS_REFS. Si les contrôles positifs passent mais que des références restent après fermeture : FAIL_OS_REFS_RETAINED. RESULT/ERR concernent la séquence Runtime, pas le verdict d'audit. Envoyer le TXT complet dans tous les cas.

Le bloc de 244 octets demeure alloué après exposition, comme P2b ; le retour des deux canaux à l'OS ne prouve pas le détachement. Un PASS atteste uniquement les champs inspectés aux instants mesurés ; pas d'observation DMA effective, pas de preuve concernant les listes dynamiques/inactives, interruptions ou réouvertures, pas de FreeVec autorisé. P2c conservé byte-exact, sans redemande de debugger.

## Résultat V1 et correctif r2

**25/11/2026 — P2d V1 Runtime : séquence PASS, audit INCONCLUSIVE.** [Journal original](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/main/docs/evidence/M19_S1P2D_OS_RUNTIME_2026-11-25.TXT), 1398 octets CRLF, SHA256 `69812cd40e6a9e8d373917ff659f0a95e7d69b38de071a7f01825189ea03ee79`, blob `b16f2e775191fd01ec5ce6214d1e6c0e31b40cb4`. Source exacte V1 [conservée dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/6c17b15c30d8d0ec2f8b1a211cf84828bc59a9eb/tests/proto/sprite_s1_os_audit/SPRITE_OS_PROBE.asc), blob a59796cd2a6962c7c4e9537efd8c0d2dcae67173. PRG_STATE 1, RESULT 1 ERR 0, 100 mouvements, blank 150 VBL, FREES 2, CLOSE_RETURNED 1, SAMPLES 6 AUDIT_BAD 6, ACTIVE_POSITIVE 0 BLANK_POSITIVE 0, FREE/CLOSE/FINAL_REFS -1, CHIP_HELD 244 DMA_FREE_PROVEN 0. Chip -248, Fast -2304 (pas de preuve de fuite ou d'absence de fuite). Graphics V40 : RES 1/13/13/1/1/1 (bits 2 et 3 pris puis rendus), copinit $468 et SHF $50C constants, LOF $50C hors écran AGA et $547A0 en phases 1..3. Le garde V1 _RAM_SPAN refuse _P<4096, donc la lecture copinit n'a jamais lieu. Ce rejet est dû au diagnostic, pas une observation de référence DMA retenue. Aucun transfert de PASS à l'audit. Lib P1i attribuée par contexte, SHA installé non mesuré.

**P2d r2 — correctif ciblé prêt à tester, pas de debugger.** Même ASC de travail, V1 identifiée par le commit immuable ci-dessus. Préflight strict local PASS sans avertissement sur les 13509 octets ASCII LF, SHA256 `445512ac68c0049412dcfdeeb0f06f3912d3a3fcc536facadd9e7d9c2b4e8e0b`, blob `4b74f84874ce0f417d0abab17ef73f8314336a28`. Une exception de lecture seule est limitée à GfxBase V40, copinit exactement $468 et SHF exactement $50C, triplet observé dans les six phases ; elle ne constitue pas une autorisation générale de lire la mémoire basse. Lecture bornée des 64 octets copinit +88..151, aucun accès en écriture, pas de suivi des pointeurs LOF/SHF. Table SimpleSprites contrôlée et journalisée avant Copper ; RAW des 16 couples registre/valeur même si le layout diffère ; AUDIT_INVALID porte désormais REASON 1..9. Raisons : 1 garde base, 2 version/taille, 3 garde étendue, 4 table, 5 plage Copper, 6 forme des MOVE, 7 pointeur hors limite signée, 8 changement de base/masque, 9 relecture instable. Boucles terminées normalement avant rejet. La chaîne graphique, les allocations et la politique de non-libération restent identiques. Exécution Runtime sur la même configuration WinUAE uniquement, snapshot obligatoire (lecture basse spécifique expérimentale ; risque résiduel), journal distinct RAM:M19_S1P2D2_OS_RUNTIME.TXT. Aucune Gate B/C/D r2. Toujours DMA_FREE_PROVEN 0.


## 25/11/2026 — P2d r2 : références OS retirées, contrôle positif réévalué hors ligne

[Journal original inchangé](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/main/docs/evidence/M19_S1P2D2_OS_RUNTIME_2026-11-25.TXT), 6187 octets, 237 lignes CRLF, SHA256 `da6cd4c53f58bce0ad339166d478d426ce198b631295d370ec12087cfa0e6dfc`, blob `d0798ca32775043dbc455911b6c4c7a75d599d3e`. ASC exact [r2](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/2cfc8365bc144fd726f21dfe59fb21bdaaa0aa71/tests/proto/sprite_s1_os_audit/SPRITE_OS_PROBE.asc), blob 4b74f84874ce0f417d0abab17ef73f8314336a28. Runtime PRG_STATE 1, RESULT 1 ERR 0, 100 mouvements, palette OK, source effacée, blank 150 VBL, FREES 2, CLOSE_RETURNED 1, SAMPLES 6 AUDIT_BAD 0, POST_WAITTOF 60. Lib P1i attribuée par contexte, SHA installé non relevé. Journal brut conserve ACTIVE_POSITIVE 0, BLANK_POSITIVE 1, FREE_REFS 0 CLOSE_REFS 0 FINAL_REFS 0 et VERDICT INCONCLUSIVE_OS_REFS. Ne jamais le réécrire.

| Phase | Réservation (hex) | COP2 | DESC2 | DESC3 | Références copinit + table |
| --- | --- | --- | --- | --- | --- |
| 0 initiale | 01 | 00000518 | 00000000 | 00000000 | 0 |
| 1 active | 0D | 0001E4EC | 0001E4BC | 00000000 | 2 |
| 2 blank | 0D | 0001E534 | 0001E4BC | 00000000 | 2 |
| 3 FreeSprite | 01 | 00000518 | 00000000 | 00000000 | 0 |
| 4 fermeture + 3 WaitTOF | 01 | 00000518 | 00000000 | 00000000 | 0 |
| 5 +60 WaitTOF | 01 | 00000518 | 00000000 | 00000000 | 0 |

Le test actif demandait en plus _SP(3)=_PAIR. Or 3 est réservé par GetSprite mais n'est jamais publié par ChangeSprite ; DESC3 reste nul sur les six relevés, alors que son bit de réservation est présent pendant l'affichage. Ce critère est une erreur de la sonde, pas un défaut d'affichage. Contrôle positif indépendant : bloc 124092 = $1E4BC, image +48 = $1E4EC, blank +120 = $1E534 ; les deux pointeurs Copper correspondent exactement, DESC2 correspond au bloc, masques 0D puis 01 et les huit slots sont lus sans erreur. **Conclusion hors ligne : PASS des références OS échantillonnées** (copinit.sprstrtup + SimpleSprites uniquement), et PASS de la séquence Runtime ; le verdict automatique original reste INCONCLUSIVE. Le canal 2 retourne au même pointeur neutre $518 que les autres canaux inutilisés. Les adresses LOF/SHF retournent toutes deux à $50C et ActiView à zéro après fermeture. Aucune lecture du contenu des listes LOF/SHF dynamiques et aucune observation effective des lectures DMA. Chip -248, allocation 244 conservée ; Fast -6464 (journal plus volumineux, pas de conclusion sur les fuites). DMA_FREE_PROVEN reste 0, pas de FreeVec qualifié ; C/D non testées. **Ne pas rejouer le test pour faire changer un compteur.** Le scénario P2d r2 et le journal restent intacts.

Suite : exploiter cette preuve pour spécifier le retrait natif via graphics.library et la synchronisation de fin de trame, sans imposer un nouveau diagnostic manuel. Il faut justifier le contrat de réutilisation/libération en auditant les chemins de fermeture/End, les listes actives et la synchronisation OS ; ne pas transformer le retour de FreeSprite seul ni le PASS des snapshots en garantie universelle de sécurité DMA. Pas de bascule de Lib ni de promotion.
