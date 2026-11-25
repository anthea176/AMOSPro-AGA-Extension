# S1-P2i — banc public Sprite

**Lib S1-P2i active : 149 384 octets, SHA256 89b7a9ead30152d2088ca761e81f7016a47bab451024c637009426d7ba777b96. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45682158541).** Ce banc utilise les trois nouveaux tokens S1-P2i. Source : SPRITE_PUBLIC.asc (4 049 octets, SHA256 35eeedccf9acf979a0a15bf64c3025459d335346b63396deb9f6e01b470f10b3), préflight strict local PASS. Runtime/Compiler non testés.

Banque : AGSP_S1P1E_FINAL.ABK, 532 octets, SHA256 225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93, blob 46b701afd29720060dc9722af3ad8714e4b318c5, strictement identique au témoin P1i. Image 3, 16x16, 3 couleurs. Ne pas renommer ni convertir.

Exécution : snapshot WinUAE, AGA PAL, 68030/JIT ON, slot d'extension correct, redémarrer AMOS. Placer l'ASC et la banque dans le même dossier, banque 29 libre, Merge ASCII dans un projet vierge. Lancer Runtime. Trois cycles automatiques : déplacement x32..232, y112, effacement de la banque source, Off/re-affichage, fermeture avec Sprite actif, Bank Free avant fermeture. Après chaque Close, Amos To Front et 4 Wait Vbl, récupération Bank Free, contrôle Mouse X=-1. Aucune intervention dans le debugger.

Attendu : RESULT 1 ERR 0, CYCLES 3 MOVES 300 SOURCE_ERASED 3 RESHOW 1 RECOVERED 3. Journal RAM:M19_S1_PUBLIC_RUNTIME.TXT (Prg State 1), puis si demandé Compiler RAM:M19_S1_PUBLIC_COMPILED.TXT (Prg State -1). INTERP est distinct. Comparer Chip/Fast libre entre cycles; ne pas déduire une absence absolue de fuite ni la sécurité DMA matérielle du seul PASS de séquence. Reporter le Sprite visible et les anomalies; arrêter si échec, restaurer snapshot si nécessaire. ERR 1/2: chipset/banque occupée; 3: chargement; 4..9: ouverture, DB, fill, swap, palette, curseur; 10: affichage initial; 11: banque source; 12: déplacement; 13/14: Off/réaffichage; 15: Bank Free actif; 16: récupération; 17: fermeture non confirmée.

La politique S1-P2i réserve les couleurs 21..23 et la paire matérielle 2/3; le banc fixe la palette à partir de la banque exacte. Les restrictions et les gardes DMA sont dans docs/M19_S1_P2I_INTEGRATED_SPRITE_2026-11-25.md.

Test T06 précédent conservé à l'identique dans [tests/proto/t06_pattern](../proto/t06_pattern/T06_PATTERN_TARGET.asc). LAST_GOOD L2b inchangée.
