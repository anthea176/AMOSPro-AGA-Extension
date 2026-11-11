# Tests AMOS actifs

**Un seul ASC actif pour R36 :** [`M13_R36_PALETTE_CYCLE_01.asc`](M13_R36_PALETTE_CYCLE_01.asc). **Gate A CPU/CI et Gate B WinUAE NON TESTÉES à ce stade.** Ne pas exécuter avec la R35 `LAST_GOOD`, qui ne contient pas `Aga Palette Cycle`.

Après PASS de Gate A et publication de la candidate R36 0.10.8 : installer la `.Lib` du dossier `dist/` dans le même slot APSystem, redémarrer AMOS, puis **New → Project → Merge ASCII**.

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
