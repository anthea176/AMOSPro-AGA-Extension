# M10 R25 — unique test AMOS actif

[`M10_R25_RECT_OVERLAP_VISUAL_01.asc`](./M10_R25_RECT_OVERLAP_VISUAL_01.asc) est le **seul fichier `.asc` dans `tests/current/`**. `Aga Rect Overlap`, R25 0.9.1 candidate, **Gate A CPU/CI PASS 704 cas, Gate B WinUAE NON TESTÉE**.

Installer la [Lib R25](../../dist/AMOSPro_AGA.Lib) et redémarrer AMOS. Sélectionner la [mire 320×256×8](../../iff-TEST/AGA_TESTCARD_320x256_256C.iff).

Le rectangle **bleu** est fixe. Le mobile **32×32** suit la souris, **vert hors collision** et **rouge en collision**. Le programme redessine le back buffer puis appelle **`_SW=Aga Swap` et `Aga Wait Vbl` exactement une fois par image** pour la synchronisation verticale. Faire au moins une entrée et une sortie de la zone bleue, puis cliquer gauche.

Attendu : `STATIC 1`, `PURE 1`, `SEEN FREE 1 HIT 1`, `DRAWERR 0`, `RESULT 1`, `CLOSE X2 RETURNED`. Aucun `Then` hors commentaires, `If/End If` et `For/Next` équilibrés, **sans garantie de 50 FPS avant essai WinUAE**. [Contrat R25](../../docs/M10_RECT_OVERLAP_R25.md).
