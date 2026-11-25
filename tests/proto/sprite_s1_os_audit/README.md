# S1-P2d — audit automatique des références Sprite/Copper

**À tester en Runtime ; aucun debugger, aucune saisie ni pause.** Garder la Lib P1i : 142968 octets, SHA256 2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3. Source [SPRITE_OS_PROBE.asc](SPRITE_OS_PROBE.asc) : 12758 octets ASCII LF, SHA256 5bd44ad91f064125a6ac310507f6b45553d15e63b3cd4ba1150a3710e1d3b8a3, blob a59796cd2a6962c7c4e9537efd8c0d2dcae67173. Préflight local strict sans avertissement PASS ; pas de Runtime/Compiler/matériel validé. [AGSP_S1P1E_FINAL.ABK](AGSP_S1P1E_FINAL.ABK) : 532 octets, SHA256 225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93, même blob historique 46b701afd29720060dc9722af3ad8714e4b318c5, aucune autre ressource.

## Exécution

Snapshot préalable WinUAE, configuration P2b/P2c habituelle (AGA, PAL, 68030, graphics.library V39/V40, aucun changement de JIT nécessaire). Banque 29 libre. Mettre les deux fichiers ensemble, Project -> Merge ASCII dans programme vierge, Runtime une seule fois. Laisser terminer. Récupérer **RAM:M19_S1P2D_OS_RUNTIME.TXT** puis restaurer le snapshot, même en cas d'erreur. Ne pas libérer le bloc exposé manuellement.

## Ce que la sonde observe

Six phases : 0 avant acquisition, 1 image active après 100 mouvements, 2 après blank + 150 VBL, 3 après FreeSprite des deux canaux avant fermeture, 4 après fermeture + 3 WaitTOF, 5 après 60 WaitTOF additionnels. À chaque phase, lecture seule : version et taille GfxBase ; réservations, table des huit SimpleSprite*, adresses ActiView, copinit, LOFlist/SHFlist ; seize MOVE SPRxPTH/PTL dans copinit.sprstrtup (les 16 registres doivent être présents sans doublon). Les huit pointeurs Copper sont reconstruits et les huit pointeurs de descripteurs comparés à toute la plage privée. TypeOfMem aux extrémités, taille de bibliothèque et alignement vérifiés, contrôle de stabilité par relecture. Les pointeurs LOF/SHF et ActiView sont seulement journalisés, pas déréférencés : évite un parcours dynamique non borné. Ces contrôles réduisent le risque mais ne garantissent ni la validité de toute la RAM ni une lecture atomique. Aucun registre DMA ou champ système écrit par l'audit.

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
