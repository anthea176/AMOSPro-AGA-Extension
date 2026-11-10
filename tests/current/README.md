# Test AMOS actif unique — M9 R24 Hotspot Hit

[`M9_R24_HOTSPOT_HIT_01.asc`](./M9_R24_HOTSPOT_HIT_01.asc) est le **seul `.asc` actif**. Version candidate **R24 0.9.0**, 29 commandes AP20. Gate A CPU/CI PASS (402 scénarios, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42908096685)), Gate B WinUAE NON TESTÉE.

Installer [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) R24 dans AMOS et redémarrer. Choisir [`AGA_TESTCARD_320x256_256C.iff`](../../iff-TEST/AGA_TESTCARD_320x256_256C.iff), 320×256×8.

Trois rectangles colorés sont affichés ; les **deux grands se recouvrent** :
- Faire un **clic gauche** au centre de leur recouvrement, environ `X=130, Y=100` (priorité à l'ID **20**).
- Faire un **clic droit** tout en bas à droite, en dehors des rectangles, environ `X=300, Y=220`.

Le programme ferme l'écran après les deux clics corrects ou 900 VBL (~18 secondes). Résultat attendu : `STATIC 1`, `OVERLAP 20`, `LEFT ID 20`, `RIGHT OUT 1`, `RESULT 1`, `CLOSE X2 RETURNED`.

La bibliothèque R23, le clavier et Ctrl+C restent **inchangés par R24** (aucun nouveau dispatcher ni état partagé). Les essais de focus, long stress, Compiler et matériel Amiga ne sont pas inclus. [Dossier R24](../../docs/M9_HOTSPOT_R24.md).
