# M19 P2c — Banc WinUAE de sélection des plans AGA

[AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) M19 P2c, **135 596 octets**, SHA256 `eebd7175035f6e6afbd7ed4d2bf5363bd6f816887993db22b848f8d5cfe48d3d`. La version protégée [LAST_GOOD](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) est P1e.

1. Copier la Lib active sous `APSystem`, puis redémarrer AMOS Pro en AGA avec un MC68020 ou supérieur.
2. Dans un programme vierge, importer [M19_P2C_BOB_PLANES.asc](M19_P2C_BOB_PLANES.asc) via **Project → Merge ASCII**. Laisser libres les banques 24, 25 et 27.
3. Lancer en Runtime puis avec AMOS Compiler. Chaque exécution écrit `RAM:M19_P2C_BOB_PLANES.TXT`. Conserver séparément les deux journaux.

Le banc lit les huit pixels d’une ligne sur le buffer arrière. Il compare le mode par défaut, des masques non contigus, le masque nul et le retournement H. Il vérifie aussi les refus de -1 et 256. Attendu `PROBE_PREALLOC 1`, `CHECKS 34`, `ERR 0`, `CLOSE_RETURNED 1`, `VERDICT PASS`. `PRG_STATE 1` identifie le Runtime et `PRG_STATE -1` le compilé.

En cas de `ERR 10`, `MODE`, `PIXEL`, `VALUE` et `EXPECTED` localisent la première différence. `PIXEL` est l’indice de 0 à 7 dans la capture qui commence à X=96. Gate A passe sous émulation MC68020 avec services Exec et Blitter simulés. Le banc est [validé en Runtime WinUAE](../../docs/M19_P2C_BOB_PLANES_MODEL.md#raccordement-natif-livré), 34/34. AMOS Compiler n’a pas été testé.

Le [banc P2b validé](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/562f24343a379aa4fd69c28edb63219581f4d7c6/tests/current/M19_P2B_BOB_FLIP.asc) est dans l’historique Git. Il a passé 21/21 en Runtime et avec AMOS Compiler.
