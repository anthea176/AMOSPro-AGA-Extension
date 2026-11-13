# M18/R68 — CBlock temporaire Chip : Gate B WinUAE interprétée À FAIRE

**Candidate unique R68 v0.13.13** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **51 064 octets**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, **64 commandes / 71 AP20**, **Gate A M68000 48 cas PASS** ([CI préparatoire](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43469372550)). **Gate B WinUAE NON TESTÉE.** R63 `LAST_GOOD` intacte.

**Seul ASC actif :** [`M18_R68_CBLOCK_CHIP_01.asc`](M18_R68_CBLOCK_CHIP_01.asc). Les banques **11, 12 et 13 doivent être LIBRES**. Copier R68 dans APSystem sous le même slot d'extension, redémarrer AMOS. Dans l'éditeur : **New → Project → Merge ASCII**, puis **Run interprété uniquement**. Aucun AMOS Compiler avant la fin de M18.

Le test crée deux banques DATA `AGACBLK ` en Chip RAM, en réutilise une sans réallocation, compare les **512 octets planaires** sur CPU8/CPU16/Blitter et vérifie le refus des appels invalides. Les trois copies restaurent le fond en opaque, y compris l'index 0 noir. Le test libère les banques avec `Erase` et contrôle la récupération mémoire Chip. Aucun fichier ABK n'est écrit.

**Rendu attendu :** fond bleu, trois rectangles colorés à intérieur noir : X8 CPU8, X96 Blitter, X160 CPU16, vers Y120 ; X240 reste bleu. Une rangée CPU8/16/Blitter apparaît aussi vers Y152 après le benchmark. La phase graphique dure environ 175 VBL.

**Console attendue :** `RESULT 1`, `CLOSE RETURNED`, `PLANE EQ BLIT/CPU8/WORD 1 1 1`, `BYTE MISMATCH 0 0 0`, `BENCH ERR 0`, `NOS/CLOSE 0 -1`, `CHIP START/END` identiques. Les lignes de **six durées** `BENCH CAP CPU8/16/BLIT` et `BENCH DRAW CPU8/16/BLIT` correspondent chacune à **300 appels**, et ne suffisent pas seules à établir un vainqueur.

[**Protocole détaillé Gate B R68**](../../docs/M18_R68_CBLOCK_WINUAE_GATE_B_PROTOCOL_2026-11-13.md). De préférence transmettre une capture de l'écran AGA puis la capture console. R67 A/B PASS [archivée](../passed/M18_R67_FICON8_CAPTURE_01.asc).
