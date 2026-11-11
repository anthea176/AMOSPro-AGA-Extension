# Tests AMOS actifs

**Un seul ASC actif pour R36 :** [`M13_R36_PALETTE_CYCLE_01.asc`](M13_R36_PALETTE_CYCLE_01.asc). **Gate A CPU/CI R36 PASS (106 scénarios natifs 68000, export strict, [CI réussie](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064528445)). Gate B WinUAE NON TESTÉE.** Ne pas exécuter avec la R35 `LAST_GOOD`, qui ne contient pas `Aga Palette Cycle`.

Installer la candidate R36 0.10.8 maintenant publiée (21 836 octets, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`) depuis `dist/` dans le même slot APSystem, redémarrer AMOS, puis **New → Project → Merge ASCII**.

Le test dessine quatre bandes rouge, verte, bleue et jaune, les affiche par `Aga Swap` puis `Amos To Back`, effectue **20 rotations avec huit VBL entre les appels**, puis teste les deux sens, les valeurs RGB24 exactes et le refus de paramètres incorrects. **Aucune banque AMOS ni fichier ABK/IFF écrasé.**

Principaux résultats attendus :

~~~text
CYC20 1 RESTORED 16711680 16776960
FWD 1 COLOR 16776960 16711680 65280 255
REV 1 RESTORE 16711680 16776960
NEG 1 COLOR 65280 16711680 POS 1
RESET 16711680 16776960
BADFIRST 0 BADEQ 0 BADORDER 0
BADLAST 0 DIR0 0 DIR2 0 DIRN 0
AFTERBAD 16711680 NOSCREEN 0 CLOSED -1
RESULT 1
CLOSE RETURNED
~~~

**R35 0.10.7 demeure `LAST_GOOD` WinUAE-PASS** jusqu'à validation explicite de la Gate B R36. Gates C Compiler et D Amiga physique non testées.
