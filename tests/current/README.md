# M19 P2b — Banc WinUAE de retournement des Bobs

[AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) M19 P2b, **135 352 octets**, SHA256 `96f4bc7e1d604d57d615e198eb43ca6abc800cdc3853c6e9ac2827ad6a86e448`, **98 commandes et 200 entrées AP20**. La version protégée [LAST_GOOD](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) est P1e.

1. Copier la Lib active dans l'emplacement habituel sous `APSystem`, puis redémarrer AMOS Pro en AGA avec un MC68020 ou supérieur.
2. Dans un programme vierge, importer [M19_P2B_BOB_FLIP.asc](M19_P2B_BOB_FLIP.asc) via **Project → Merge ASCII**. Les banques 24, 25 et 27 doivent être libres. Le banc crée ses images lui-même.
3. Lancer en Runtime et ouvrir `RAM:M19_P2B_BOB_FLIP.TXT`.

Le banc alloue d’abord la banque CBlock 27, prépare les deux banques AGBO en Chip et lie les Bobs. Les captures suivantes réutilisent la banque 27 de même taille. Le banc capture un pixel du buffer arrière avec `Aga C Block Capture` pour chaque orientation et vérifie deux positions de collision. Attendu en Runtime `PRG_STATE 1`, `RESULT 1`, `PROBE_PREALLOC 1`, `CHECKS 21`, `ERR 0`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

| Mode | Pixel attendu |
| --- | --- |
| Normal | (101,101) |
| H | (99,101) |
| V | (101,99) |
| HV | (99,99) |

Les contrôles CPU, ABI, pixels et gestion Chip passent sous émulation MC68020 avec services Exec et Blitter simulés. Le passage sous WinUAE Runtime et le vrai Compiler restent à établir. Le [banc P2a précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/8b8830fb4d4308deeed8ec58d79d2a5baf2db226/tests/current/M19_P2A_BOB_COL.asc) est conservé dans l’historique Git.

Premier essai Runtime au commit `900afe2` — pixel correct en mode 0, puis `ERR 10`, `RECT -1`, `MASK -1`. Le banc révisé reste à vérifier sous WinUAE.
