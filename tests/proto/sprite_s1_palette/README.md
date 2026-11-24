# S1-P2 — Sonde palette réelle du ViewPort (P1i, non distribuée)

**Ne pas changer de Lib.** Utiliser `dist/AMOSPro_AGA.Lib` S1-P1i, 142968 octets, SHA256 `2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3`. Le test prépare le contrat palette du futur moteur Sprite ; aucune image DMA activée, aucun GetSprite, aucune écriture de palette/Copper, aucun nouveau token. Banque Work temporaire 40 octets, choisie libre dans 100..255, uniquement pour les TagItems ; libérée sans référence DMA.

Source [SPRITE_PALETTE_PROBE.asc](SPRITE_PALETTE_PROBE.asc), 4300 octets, SHA256 `1490e445df3f46a5d7e8768663ca240ce7d6ba2e720a2ae3fbf3eff677d7875e`, Git blob `5bbed3129245fba7312618682aac9a69c33a68a5`. Préflight strict AMOS local PASS. Pas de compilation ou exécution WinUAE encore.

## Test

1. Snapshot WinUAE, 68030/JIT ON/AGA PAL. Ne rien installer de nouveau ; vérifier la Lib P1i. Programme vierge, Project -> Merge ASCII. Aucun ABK/IFF nécessaire.
2. Lancer Runtime une fois. L'écran peut apparaître brièvement vide : c'est une sonde, pas une démonstration Sprite. Elle ouvre l'écran privé, mesure le ColorMap avant DB, après DB, curseur masqué, puis restauré. Elle clôture et retourne à AMOS.
3. Transmettre **RAM:M19_S1P2_PALETTE_RUNTIME.TXT** en entier. Attendu : PRG_STATE 1, SAMPLES 4, CLOSE_RETURNED 1, RESULT 1, ERR 0, VERDICT PASS_PALETTE_QUERY_ONLY. Ne pas présumer les valeurs EVEN_BASE/ODD_BASE ; ce sont précisément les inconnues à mesurer.

LVO VideoControl -708 (A0 ColorMap, A1 TagItems) et tags GET V39 : EVEN $80000028, ODD $80000029, SPRITERESN $80000032, PF1_TO_SPRITEPRI $80000034. Les tags sont recréés à chaque appel ; le système peut les réécrire avec les SET/CLR correspondants. Valeurs brutes et champs NDK ColorMap (44/46, 17/18) journalisés, sans conversion ni hypothèse de base. Source : [Autodoc](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0338.html), [LVO](https://d0.se/autodocs/graphics.library), [tags](https://d0.se/include/graphics/videocontrol.h), [ColorMap V39](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node05ED.html), [AMOS Gfxcall/Execall](https://amospromanual.dev/11-05-libraries-and-devices.html), [S0d](../../design/sprites_aga/SPRITE_PROBE.asc).

ERR 1..8 : détection/banque/écran/DB/curseur ; 10..18 : garde de pointeur/structure/version ; 19 : retour VideoControl non nul ; 20 : réponse non renseignée. TypeOfMem est un contrôle de région, pas une preuve d'allocation ; sonde limitée à l'état privé P1i de confiance et WinUAE. Ne pas modifier les offsets à l'aveugle si échec. Aucun PASS de retrait DMA ni Gate C/D transférable.
