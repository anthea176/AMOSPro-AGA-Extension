# Intuition Input R6 — retour AMOS au premier plan après Ctrl+C

**Version expérimentale 0.5.7.** Correctif limité à l'affichage.
Aucun changement aux commandes ordinaires, au loader ILBM, au Double Buffer,
à `Aga Screen Close` ou au Break natif R5.

## Observation WinUAE confirmée par l'utilisateur

- R3 : `Aga Screen Close` fonctionne en boucle simple.
- R4 : `Aga Wait Key` ignore bien Ctrl seul, RAWKEY 99.
- R5 : **Ctrl+C interrompt réellement le programme AMOS**.
- Défaut R5 résiduel : après le Break, **Workbench reste affiché**.
  AMOS n'est pas remis visuellement au premier plan.

## Appel AMOS natif, références vérifiées

Le code officiel AMOS Professional
([AOZ-Studio/AMOS-Professional-Official](https://github.com/AOZ-Studio/AMOS-Professional-Official))
définit :

- `+WEqu.s` : `T_SyVect=-4`, `T_EcVect=-8` relatif à `A5` ;
- `+Equ.s` : `AMOS_WB=72`, macro `EcCalD AMOS_WB,1` ;
- `+W.s` : entrée 72 de `EcIn` vers `TAMOSWb` ;
- `TAMOSWb` avec `D1=1` : bascule les circuits et
  `T_AMOSHere` pour remettre AMOS au premier plan.

L'appel est le même que celui utilisé par AMOS lui-même :

```asm
moveq   #1,d1
movea.l -8(a5),a0
jsr     288(a0)       ; AMOS_WB * 4
```

Encodage 68000 : `72 01 20 6D FF F8 4E A8 01 20` (10 octets).

## Séquence Ctrl+C R6

`GetMsg -> ReplyMsg -> CloseWindow -> libération DB -> CloseScreen
-> CloseLibrary -> T_Actualise BitControl+BitVBL
-> EcCalD AMOS_WB,1 -> restauration registres AP20
-> Rjsr L_Test_PaSaut`

L'appel de remise au premier plan précède obligatoirement
`Test_PaSaut` : avec `Break On`, cette dernière routine peut
interrompre le flot sans revenir à l'extension.

Le correctif ajoute 10 octets à l'entrée 17 (`Aga Key`) et
10 octets à l'entrée 18 (`Aga Wait Key`). Il est inséré
au tout début du stub Ctrl+C R5 ; l'adresse d'entrée du stub et
les déplacements relatifs d'origine restent identiques.

**Tous les segments AP20 0 à 16 sont byte-for-byte identiques au R5.**
Le corps de chaque entrée 17/18 est inchangé hors stub Ctrl+C.
La fenêtre Intuition et Generic ILBM R2 restent inchangés.

## Livrables

- Branche : `codex/intuition-input-r1` (PR #4, non mergée).
- Builder : `tools/build_intuition_input_r6.py`.
- Tests CPU : `tools/test_intuition_input_r6.py`.
- Lib actuelle : `dist/AMOSPro_AGA.Lib`.
- Archive : `dist/experimental/AMOSPro_AGA_M5_v0.5.7_INTUITION_INPUT_R6.Lib`.
- Taille : **7 948 octets**.
- SHA256 : `729fc13efbaa710a371048353368ffe3dd5af0a23d0043d1e6ee3bcf2e5330d9`.
- R5 préservé : `dist/experimental/AMOSPro_AGA_M5_v0.5.6_INTUITION_INPUT_R5.Lib`.

## Validation

**Statique / reproductibilité / SHA / conservation segments : PASS.**

**CPU R6 : à exécuter en CI** (le test vérifie
`CloseWindow -> CloseScreen -> AMOS_WB(1) -> Test_PaSaut`,
la conservation des registres, et qu'une touche normale n'appelle
pas le retour AMOS).

**AMOS/WinUAE : à revalider.** Utiliser
`tests/current/M5_INTUITION_INPUT.asc` en interprété et compilé :

1. Une touche ordinaire termine `Aga Wait Key`, le programme continue.
2. `Aga Screen Close` reste fonctionnel sur les cycles répétés.
3. Ctrl seul reste ignoré par `Aga Wait Key`.
4. Ctrl maintenu + C ferme le Screen, **interrompt le programme**,
   **remet l'éditeur AMOS au premier plan**, et ne laisse pas de ressources.
5. Un nouvel Open/Close après le Break doit fonctionner.

Ne pas merger sur `main` avant le PASS runtime complet.
