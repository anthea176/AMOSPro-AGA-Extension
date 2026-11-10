# M4b v0.0.8 R6B — candidat Single Swap

R6B part de la fondation R6A validée sous AMOS365.

## Différence volontaire par rapport à R6A

- DBState passe de 16 à 24 octets ;
- deux MsgPorts dédiés sont créés : Safe et Disp ;
- les deux ScreenBuffers reçoivent leurs ReplyPorts Safe/Disp ;
- `Aga Swap` effectue exactement un `ChangeScreenBuffer` ;
- aucun retry non borné ;
- après succès, l’index courant est mis à jour puis les réponses Safe et Disp sont collectées par `WaitPort/GetMsg` ;
- aucun `ReplyMsg` n’est effectué sur ces réponses ;
- `Aga Back Fill` reste désactivé.

## Artefact

`dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B.Lib`

- taille : **2372 octets** ;
- SHA256 : `8ca68ced29fe9d3574c7800b79ba0f28cd6ea11526efbfc73a44ee43a54ba194` ;
- jumps AP20 : `152,2,8,8,48,167,193,75,108,15,141,88,1,0`.

## Contrôles statiques

`tools/test_m4b_r6b.py` couvre notamment :

- intégrité AP20 ;
- identité de `Aga Screen Open` avec R6A ;
- état partagé 36 octets ;
- DBState 24 octets ;
- deux MsgPorts ;
- ReplyPorts Safe/Disp configurés sur les deux buffers ;
- exactement un `ChangeScreenBuffer` ;
- `WaitBlit` avant le changement ;
- index mis à jour seulement après succès ;
- deux `WaitPort/GetMsg` ;
- absence de `ReplyMsg` ;
- préservation A3 / retour D3 ;
- cleanup des ports après les ScreenBuffers ;
- Back Fill toujours stub.

Résultat local : **10/10 tests OK**.

## Validation runtime requise

Exécuter uniquement :

`tests/current/M4B_R6B_01_SINGLE_SWAP.asc`

Résultat attendu :

- `OPEN = 1`
- `DOUBLE BUFFER = 1`
- `BEFORE SWAP`
- `SWAP = 1`
- `AFTER SWAP`
- `CLOSE = OK`
- `TEST 01 FINISHED`

Ne pas lancer de boucle de swaps avant validation de ce test.
