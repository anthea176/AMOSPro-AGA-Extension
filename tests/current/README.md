# Test actif M18/R62 — Chip Blitter masque

**R62 v0.13.7 candidate Gate A CPU PASS** (160 cas AP20 interpreteur/Compiler V2 simules). **Gates B et C WinUAE non encore effectuees.** Gate D sur Amiga physique non testee. R60 reste `LAST_GOOD`, R61 A/B/C PASS conserve dans [tests/passed](../passed/M18_R61_FICON_01.asc).

Bibliotheque unique : [dist/AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), **38 732 octets**, SHA256 `9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6`.

Test AMOS actif unique : [M18_R62_CHIP_BLIT_01.asc](M18_R62_CHIP_BLIT_01.asc). Necessite [M18_FICON8_SAMPLE_BANK10.abk](M18_FICON8_SAMPLE_BANK10.abk) et [M18_FICHIP8_SAMPLE_BANK11.abk](M18_FICHIP8_SAMPLE_BANK11.abk) (**1 188 octets**, cache Chip prepare). **Load ecrase les banques 10 et 11** : utiliser une session WinUAE jetable.

Procedure : installer R62 dans le slot AMOS habituel, redemarrer AMOS, placer les deux ABK dans le repertoire courant, importer l'ASC dans un programme vide (Project -> Merge ASCII), executer en interprete. Ensuite compiler un **nouvel executable avec R62**, sans reutiliser l'executable compile R61.

Attendu : `RESULT 1`, `CLOSE -1`, `NOS 0`, `SWAP 1`, Chip Free identique avant et apres. ICON/BLIT/SHIFT/CLIP/OUT = 1, BAD et BCBAD = 0. Verifier visuellement les icones CPU sur la premiere ligne et Blitter en seconde ligne, y compris transparence et clipping.

Le cache est **pre-stage hors AMOS**, sans staging Fast->Chip pendant le test. `TypeOfMem(MEMF_CHIP)` est controle par la routine, les drapeaux ABK seuls ne garantissant pas l'emplacement physique. Les temps Blitter et couts de staging ne sont pas encore mesures.
