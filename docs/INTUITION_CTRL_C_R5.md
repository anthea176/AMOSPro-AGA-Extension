# Intuition Input R5 — Ctrl+C AMOS natif (v0.5.6)

**Statut : candidat expérimental. Validation statique locale PASS. Validation
CPU 68000 complète et retour à l'éditeur AMOS/WinUAE : EN ATTENTE.**

## Constat runtime

- R3 : la fermeture normale `Aga Screen Close` fonctionne sur plusieurs cycles sans Double Buffer.
- R4 : Ctrl seul (`RAWKEY $63 = 99`) ne termine plus `Aga Wait Key`.
- R4 : Ctrl+C termine cependant `Aga Wait Key` avec la touche C,
  **sans interruption effective du programme AMOS**. R4 n'est donc PAS
  une validation Ctrl+C.

## Cause technique investiguée

La source officielle AMOS Professional distingue la **demande de Break**
et l'**exécution du test de Break**.

- `+W.s` : la gestion clavier AMOS pose le bit `BitControl=8` dans
  `T_Actualise(a5)`.
- `+ILib.s` : `Test_Normal` ne lance `Test_Force` que si l'octet fort
  de `T_Actualise` a son bit de signe positionné (BitVBL=15).
  `Test_Force` lit ensuite `BitControl`, `ActuMask` et délègue
  l'arrêt à la gestion d'erreur normale d'AMOS.
- `+ILib.s` : `Test_PaSaut` appelle `Test_Normal` sans saut
  automatique ; `extensions/+Music.s` recommande explicitement ce
  point d'entrée dans les boucles d'attente d'une extension.
- `+CEqu.s` : `Rjsr` est un appel à la bibliothèque AMOS principale
  résolu par l'éditeur de liens AP20. `AMOSPro Sources/+lequ.s` fixe
  `L_Test_PaSaut=140`. Marqueur : `FE 11 F7 00 00 8C`.

Source de référence :
[AMOS Professional Official](https://github.com/AOZ-Studio/AMOS-Professional-Official).

Le R4 positionnait seulement `BitControl`, puis retournait `51`.
Il ne demandait pas directement au moteur AMOS d'exécuter le test natif.
Cette explication est cohérente avec l'échec runtime, mais la
validation finale dépend encore de l'exécution réelle du R5.

## Delta R5

Sur `RAWKEY C ($33) + IEQUALIFIER_CONTROL` :

1. `ReplyMsg` de l'événement déjà lu ;
2. fermeture non bloquante AGA (Window, Double Buffer éventuel, Screen,
   bibliothèques, état remis à zéro) inchangée depuis R3 ;
3. `ORI.W #$8100,T_Actualise(a5)` (BitControl+BitVBL) ;
4. restauration des registres AP20 et `D3=51, D2=0` ;
5. `Rjsr L_Test_PaSaut` ; AMOS décide du Break via son gestionnaire natif ;
6. retour possible uniquement selon le comportement normal d'AMOS
   (`Break Off`, gestion `On Break`, etc.).

Le test ne crée aucune interruption matérielle et n'utilise ni
`FindTask/Signal`, ni `WaitPort`, ni Exec `Wait`, ni arrêt sauvage.

Les **seuls segments AP20 modifiés par rapport au R4** sont :
- 17 : `Aga Key` (le Break doit également fonctionner en polling) ;
- 18 : `Aga Wait Key` (filtrage Ctrl seul R4 préservé).

Chaque segment reçoit un stub de 16 octets en fin de segment. Les
anciens offsets de branches PC-relatives restent inchangés, à
l'exception du seul saut du chemin Ctrl+C redirigé vers son stub.
Segments 0–16, dont Screen Close, Generic ILBM R2 et PicInfo,
**identiques octet pour octet au R4**.

## Livrables

- Branche : `codex/intuition-input-r1`.
- Builder : `tools/build_intuition_input_r5.py`.
- Tests : `tools/test_intuition_input_r5.py`.
- Lib courante : `dist/AMOSPro_AGA.Lib`.
- Archive : `dist/experimental/AMOSPro_AGA_M5_v0.5.6_INTUITION_INPUT_R5.Lib`.
- Taille : **7 928 octets**.
- SHA256 : `3de03160c458f5c6990e18e450ef9d0a34ada950b59d83dd8cc2fbac271f29c5`.
- Repli : R4 conservé intact en archive.

## Validation obligatoire AMOS/WinUAE

Exécuter `tests/current/M5_INTUITION_INPUT.asc` avec `Break On` :

1. A/B/D : touche normale, polling et cycles Open/Close ;
2. C : maintenir Ctrl seul (aucune sortie de `Aga Wait Key`) ;
3. presser C en gardant Ctrl enfoncé ;
4. **attendu** : arrêt réel du programme, aucun affichage `C FAIL`,
   Screen AGA réellement fermé, retour à l'éditeur AMOS ;
5. relancer immédiatement un cycle Open/Close pour exclure les
   ressources orphelines ;
6. vérifier également interprété et compilé.

Si `C FAIL` apparaît, **échec R5** même si le retour clavier vaut 51
ou si l'écran AGA se ferme. Ne pas merger `main` sans validation.
