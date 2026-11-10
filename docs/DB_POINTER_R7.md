# M5 — R7 0.5.8 : correction du pointeur `sb_DBufInfo`

## Validation runtime R7 — 10 novembre 2026 (5/5 PASS)

**Retour utilisateur confirmé sous WinUAE : cinq exécutions consécutives sans crash** du test `tests/current/M5_DB_POINTER_R7.asc`, à la géométrie Fallout 640×512×4 plans (ModeID 167936).

`OPEN RETURNED 1` ; `DB RETURNED 1` ; `Aga Wait Key = 64` ; `Aga Screen Close` terminé ; retour AMOS et `End` normaux.

**PASS limité au chemin Open → Double Buffer → Wait Key → Close, sans Swap, sans IFF Load.** Le chemin `ChangeScreenBuffer` puis fermeture reste non validé et potentiellement dangereux. Suite : [contrat Safe/Disp](M5_DB_SWAP_SYNC_DESIGN.md). Ne pas merger sur main.


**Branche :** `codex/intuition-input-r1` — **NE PAS MERGER** avant test WinUAE et résolution séparée du Swap.

## Retour WinUAE à l'origine du chantier

- `Amiga fallout.iff` : 640×512, 4 plans, CAMG $00029000, ModeID 167936.
- Le test **sans Double Buffer**, `M5_ILBM_INPUT_EXIT_DIAG.asc`, a réussi trois fois :
  `Open -> Aga Wait Key -> Close -> Amos To Front`.
- Le test `M5_DB_NO_SWAP_EXIT_DIAG.asc` reste bloqué après la ligne
  `MODE 167936 COLORS 16`. La capture ne montre pas `OPEN =`.
  Le texte peut être masqué par le changement de screen : cette seule capture
  ne localise pas définitivement le blocage sur `Aga Screen Open` ou `Aga Double Buffer`.
- Les essais précédents utilisant `Aga Swap` pouvaient planter WinUAE.

## Défaut source confirmé

Dans `tools/build_m4b_r6b_r1.py`, repris jusqu'à la Lib R6,
l'allocation du Double Buffer contient deux séquences mal encodées :

```asm
; Ancien code pour les deux ScreenBuffers
MOVEA.L (A4),A0           ; sb0
MOVEA.L $4A80(A0),A0     ; ERREUR : lit à +19072 octets
; puis BEQ et écriture des ports Safe/Disp dans ce pointeur invalide
```

Le second `ScreenBuffer` comporte la même erreur. L'opcode `2068`
attend un déplacement 16 bits, et l'ancien mot `4A80` (qui devait être
`TST.L D0`) était **absorbé comme déplacement**. `MOVEA` ne change
en outre pas le CCR, donc le `BEQ` utilisait des flags sans rapport.

La structure officielle Amiga est :

```c
struct ScreenBuffer {
    struct BitMap *sb_BitMap;       // +0
    struct DBufInfo *sb_DBufInfo;   // +4
};
```

Code correct :

```asm
MOVEA.L (A4),A0
MOVEA.L 4(A0),A0         ; pointeur DBufInfo
MOVE.L  A0,D0
TST.L   D0              ; vrai test de nullité
BEQ     fail_both
```

Le même correctif est appliqué à SB1.

Références :
- https://d0.se/include/intuition/screens.i
- https://d0.se/include/graphics/view.h
- https://developer.amigaos3.net/sites/default/files/downloads/2024-02/RKRM%20changes%20and%20additions-%282024-02-21%29.pdf

## Correctif R7

- Builder : `tools/build_db_pointer_r7.py`.
- Tests 68000 : `tools/test_db_pointer_r7.py`.
- **Seul le segment AP20 n°10** (`Aga Double Buffer`) est reconstruit,
  à partir du générateur historique avec labels afin de recalculer tous les
  déplacements de branches.
- L'ancienne séquence est reproduite et comparée **octet pour octet** au
  segment R6 ; les deux corrections ajoutent quatre octets chacune.
- Tous les autres segments 0–9, 11–18 sont strictement identiques au R6,
  incluant Screen Open, Screen Close, Ctrl+C, Generic ILBM R2 et PicInfo.
- Le loader ILBM n'est pas modifié.

**Lib expérimentale courante sur cette branche :**
`dist/AMOSPro_AGA.Lib`

**Archive :** `dist/experimental/AMOSPro_AGA_M5_v0.5.8_DB_POINTER_R7.Lib`

**Taille :** 7 956 octets.

**SHA256 :** `e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce`

## Validation obligatoire

La suite 68000 doit couvrir :

1. allocation de deux ScreenBuffers et deux MsgPorts ;
2. accès uniquement à `sb_DBufInfo` (+4), jamais au faux offset `$4A80` ;
3. écriture des ReplyPorts Safe/Disp à +22/+54 dans chaque DBufInfo ;
4. échec AllocVec, CreateMsgPort, AllocScreenBuffer ou DBufInfo manquant ;
5. appel répété de `Aga Double Buffer`, retour ABI et registres conservés ;
6. fermeture avec Double Buffer alloué **mais sans aucun Swap** ;
7. preuve de conservation des 18 autres segments et du loader ILBM.

**Ces contrôles CPU doivent être exécutés, pas seulement déclarés PASS
par la présence de motifs dans le binaire.**

Sous WinUAE, installer R7 sur une **session neuve** et lancer uniquement :

`tests/current/M5_DB_POINTER_R7.asc`

Ce test utilise directement 640×512×16 couleurs et ModeID 167936.
Il n'utilise ni Fsel, ni PicInfo, ni IFF Load, ni Swap ni dessin. Vérifier
Open, succès du Double Buffer, touche normale, Close et retour AMOS.
Premier essai unique, puis répétition uniquement si le premier a réussi.

## Risque distinct TOUJOURS OUVERT : Swap en vol

Le R7 **ne corrige pas** la disparition du suivi SafeMessage/DispMessage
après `ChangeScreenBuffer()` dans `build_m4b_r6b_r4.py`, ni le
nettoyage Ctrl+C avec Swap en vol. Tant que ce protocole n'est pas réparé
et validé, **ne pas lancer de scénario `Swap -> Close`** sur R7.

Lire aussi `docs/M5_DB_SWAP_CLOSE_INCIDENT.md`.

## Validation CI R7 — 10/11/2026

**12/12 contrôles CPU dédiés PASS** sur GitHub Actions
[run 42814094313](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42814094313).
Binaire reproductible : **7 956 octets**,
SHA256 `e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce`.

Les tests exécutent le segment AP20 10 au niveau 68000 avec des
allocations simulées, vérifient les pointeurs `sb_DBufInfo`, les
ReplyPorts des deux ScreenBuffers, les erreurs partielles, l'ABI et la
fermeture **sans Swap**. Le loader Generic ILBM R2 et les 18 autres
segments sont bit-à-bit identiques à R6.

**Mise à jour : 5/5 PASS sous WinUAE sur Double Buffer sans Swap.** Le chargement IFF/Swap reste bloqué.
Test AMOS isolé : `tests/current/M5_DB_POINTER_R7.asc`.

