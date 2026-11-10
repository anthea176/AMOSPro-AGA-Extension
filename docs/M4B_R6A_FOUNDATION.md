# M4b v0.0.7 R6A — fondation auditée

R6A corrige les défauts prouvés par `docs/M4B_R5_AUDIT.md` sans encore réintroduire le swap.

## Corrections

- `state+28` reste la profondeur d’écran ;
- `state+32` = `DBState*` ;
- A3 préservé ;
- D3 réservé au retour des fonctions AMOS ;
- publication DB seulement après deux `AllocScreenBuffer()` réussis ;
- `WaitBlit()` avant `FreeScreenBuffer()` ;
- même cleanup pour Close et hooks Cold/RESET/END.

## Limitation volontaire

- `Aga Swap` retourne toujours 0 ;
- `Aga Back Fill pen` est un no-op.

## Binaire

`dist/experimental/AMOSPro_AGA_M4b_v0.0.7_R6A.Lib`

- taille : **2004 octets** ;
- SHA256 : `cce0104e1cecf6842de008b58df0533e126cf6b1402f1bedfdc1a45ee88cf784`.

Le fichier commité est vérifié byte-for-byte contre le builder.

## Validation progressive

1. lancement AMOS365 : **OK** ;
2. `tests/passed/M4B_R6A_01_OPEN_CLOSE.asc` : **OK** ;
3. `tests/passed/M4B_R6A_02_DB_ALLOC.asc` : **OK** ;
4. allocation réelle des deux ScreenBuffers puis fermeture propre : **OK** ;
5. prochaine étape : R6B avec un seul Swap synchronisé.

R6A est figé comme fondation validée. Toute modification du protocole de swap doit partir de ce candidat, sans reprendre le code Swap R5 tel quel.
