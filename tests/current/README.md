# M18/R64 — Unique ASC actif pour Gate B WinUAE interprétée

**R64 v0.13.9**, [librairie candidate](../../dist/AMOSPro_AGA.Lib) de **39 100 octets**, SHA256 `4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c`, [42 tests natifs 68000 Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43440810232). **R63 v0.13.8 LAST_GOOD intacte**. Gate B WinUAE **PASS le 13/11/2026**, avec les captures de l'auteur ([rapport](../../docs/M18_R64_FICON8_WINUAE_GATE_B_2026-11-13.md)) ; Gate C Compiler manuelle une seule fois à la fin M18.

[Unique test actif : M18_R64_FICON8_CREATE_01.asc](M18_R64_FICON8_CREATE_01.asc). Dans AMOS, importer via **Project → Merge ASCII** depuis un programme vide ; utiliser une configuration WinUAE jetable. **Banque 12 libre obligatoire** : sinon la création est refusée sans écrasement et le test s'arrête. Écrit `RAM:M18_R64_FICON8.ABK` (attention à un fichier du même nom déjà présent).

Le test vérifie la création, les tailles, le masque `$FFFF`, les 8 plans nuls, le refus de collision et des paramètres invalides, l'absence de fuite **avant** écriture dans `RAM:`, Save/Erase/Load ABK et le rendu CPU. **Contrôle visuel R64 confirmé** : fond bleu inchangé en X30 (masqué), carré noir en X90 (opaque) ; `RESULT 1`, `CLOSE RETURNED`. L'ASC reste le seul test actif jusqu'à décision de promotion / début de la fonction suivante. La mémoire après sauvegarde RAM: ne sert pas à juger les fuites.

Les ABK de référence FICON8 10 et FICHIP8 11 restent là mais **ne sont pas nécessaires au test R64**.
