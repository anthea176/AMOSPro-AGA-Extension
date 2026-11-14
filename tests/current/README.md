# Test actif C2P R74 / Aga C2P Open — 14 novembre 2026

**Unique ASC actif : [C2P_R74_OPEN_01.asc](C2P_R74_OPEN_01.asc).** Le test P2/GDB a été retiré : **aucun PowerShell, aucun port réseau et aucune modification WinUAE**.

**Dépendances :** installer la candidate `dist/AMOSPro_AGA.Lib` (R74 v0.13.19, 52 612 octets) dans le répertoire des extensions AMOS, et placer le fichier `libs/c2p.library` du SDK utilisateur dans **LIBS:** de l'Amiga. CPU 68020+, écran AGA. La banque AMOS **12 doit être libre** : l'ASC la réserve (81 920 octets) et l'efface après le test.

1. Importer le programme dans AMOS Professional par **Merge ASCII** et exécuter **en interprété**.
2. Le programme teste Open, Double Buffer, le refus de double Open et le nettoyage Screen Close sur les écrans **16, 32, 64, 128 et 256 couleurs**.
3. Lire les lignes `COL ... OPEN 1 DB 1 C2P 1 DUP 0 POST 0`, puis **`RESULT 1`** et **`CLOSE RETURNED`**. La quantité de Chip RAM avant/après est affichée pour information.
4. Transmettre une capture de la sortie. Aucune image générée : **Convert n'est pas encore implémenté**.

**Statut vérifié :** Gate A CPU hôte R74 PASS, structure AP20 et protections R73 PASS ; Gate B WinUAE R74 NON TESTÉE, Gate C Compiler R74 NON TESTÉE, Gate D NON TESTÉE. R73 v0.13.18 reste `dist/AMOSPro_AGA_LAST_GOOD.Lib` intacte.

[Contrat technique R74](../../docs/C2P_R74_OPEN_2026-11-14.md).
