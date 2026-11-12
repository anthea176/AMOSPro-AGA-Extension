# M16/R52 — diagnostic sur les instructions a la cible de Rjsr

R51 Gate B WinUAE a affiche `RESULT 1` : le marqueur `Rjsr` index 322 est relocalise en `JSR absolute long`, mais l'adresse n'a pas ete comparee a la vraie routine. R49 plante dans WinUAE ; R50 a provoque un Guru `80000004` avec `FnOne`.

**R52 ne execute PAS `Rjsr`.** Elle verifie les parametres precedemment valides (six entiers), saute le marqueur, lit le pointeur de `JSR` et le controle par **`exec.library/TypeOfMem` LVO -534** a ses deux bornes avant de lire les trois mots machines. Source AMOS Professional officielle `+Lib.s`, `Lib_Par FnOne` : `MOVEQ #1,D3`, `MOVEQ #0,D2`, `RTS` = **`7601 7400 4E75`**.

Le programme renvoie **1** si ces trois mots concordent ; **2** s'ils different ; **3** si `TypeOfMem` ne reconnait pas l'adresse (une zone ROM peut aussi produire ce resultat) ; **4** si l'opcode/pointeur du JSR est invalide ; **0** si le contrat d'arguments est different. **Un 1 confirme seulement les premiers octets cibles**, pas encore la possibilite d'executer de facon fiable le `Rjsr` dans un contexte AP20.

[Candidate courante](../dist/AMOSPro_AGA.Lib), [archive versionnee](../dist/experimental/AMOSPro_AGA_M16_v0.12.7_R52_FNONE_TARGET_PROBE.Lib), SHA256 `09ec9797fdea8f1b4694b2c8a9052776ff5cdcf7b959f2f1533c0b41151ea82e`, 32 012 octets, meme API et structure AP20 que R51. [Seul test courant](../tests/current/M16_R52_FNONE_TARGET_PROBE_01.asc).

**Gate A CPU/CI PASS** : [run 43259842568](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43259842568), tests de plusieurs cibles avec garde `TypeOfMem`. **Gate B WinUAE en attente, Gate C Compiler non testee.** M16 ouvert, R46 C1 `LAST_GOOD` non modifiee.
