# S1-P2b — Affichage AGSP réel, sonde WinUAE uniquement

**Ne pas changer de Lib** : P1i 142968 octets, SHA256 2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3. Aucun nouveau token. Source [SPRITE_AGSP_PROBE.asc](SPRITE_AGSP_PROBE.asc), 8366 octets ASCII LF, SHA256 74e79e525eb64b6bb09cc2c8b99575c20f0c7588c3761756f168c48772219793, blob 8927457a659d16a25d4f63138eeefe75dece1a84. Préflight strict local PASS, Runtime non testé.

## Exécution unique

- Créer un snapshot WinUAE AVANT le test (68030/JIT ON/AGA PAL). Banque 29 libre. Placer le fichier original AGSP_S1P1E_FINAL.ABK à côté du programme ; si téléchargé depuis les [preuves](../../../docs/evidence/M19_S1P1I_AGSP_FINAL_2026-11-24.ABK), le renommer exactement AGSP_S1P1E_FINAL.ABK. Taille 532, SHA256 225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93. Aucun IFF nécessaire.
- Programme vierge, Project -> Merge ASCII, Runtime une fois. Le Sprite 16x16 (image 3 de la banque d'origine, 3 couleurs + transparent) doit se déplacer vers la droite, rester affiché, puis disparaître avant fermeture. Prendre une capture visible si possible.
- Récupérer RAM:M19_S1P2B_AGSP_RUNTIME.TXT et les captures hors de la machine virtuelle ; RESTAURER le snapshot après le test, même en cas d'erreur. Ne pas relancer en boucle : la sonde conserve volontairement 244 octets d'AllocVec si un canal a été acquis.

Attendu : SOURCE_ERASED 1, PALETTE_OK 1, MOVES 100, BLANK_SET 1, BLANK_VBL 150, FREES 2, CLOSE_RETURNED 1, CHIP_HELD 244, DMA_FREE_PROVEN 0, RESULT 1, ERR 0, VERDICT PASS_AGSP_DISPLAY_SEQUENCE_ONLY. Le log seul ne prouve pas le rendu visuel ni la disparition effective du Sprite.

## Périmètre et sécurité

La sonde vérifie l'en-tête, le descripteur et les 64 octets de plans / 12 octets de palette de l'image 3 exacte ; elle reproduit le layout P2a dans l'ASC, pas l'exécution du natif P2a. Copie Chip privée indépendante puis Erase 29 AVANT publication. Deux canaux explicites (2 image, 3 réserve de la paire) obtenus par GetSprite ; si l'un manque, abandon sans forcer le canal. Fond uniforme indice 0, aucune utilisation des indices 21..23 par le décor. VideoControl GET confirme les paramètres après acquisition ; GetRGB32 vérifie exactement les 3 couleurs écrites. Appels ChangeSprite/MoveSprite/FreeSprite selon le S0d. Aucun registre matériel écrit directement. La lecture de posctldata vérifie le descripteur, pas la destination DMA ; les compteurs VBL et FreeSprite ne prouvent pas l'arrêt des lectures. Pas de FreeVec après exposition à GetSprite. Les 244 octets restent réservés jusqu'au reset/snapshot ; ce n'est PAS une stratégie de production. Les adresses CHIP_BLOCK, IMAGE, BLANK sont journalisées pour un futur audit Copper/DMA. En cas de Ctrl+C/Guru, restaurer immédiatement le snapshot, ne pas tenter d'Erase/FreeVec à la main.

ERR 1..7 : détection/banque/fixture ; 8..10 : allocation Chip et source ; 11..16 : écran, DB, Swap ou structures ; 17..20 : curseur, canaux et contexte palette ; 21..22 : écriture/lecture RGB24 ; 23..24 : descripteur image/blank ; 25..26 : restauration ou compteurs. Pas de Gate C/D, aucun nouveau binaire.
