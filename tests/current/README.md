# Test AMOS actif — R83 v0.13.28 modulaire (main)

**Un seul test actif :** [`C2P_R83_MODULAR_01.asc`](C2P_R83_MODULAR_01.asc).
**Un seul binaire actif :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib).
Il s'agit de la **candidate R83**, non encore promue.
[**R82 `LAST_GOOD`**](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) reste immuable.

## Exécution sous WinUAE AGA, CPU 68020+

1. Sauvegarder la bibliothèque AMOS installée, puis installer
   `dist/AMOSPro_AGA.Lib` en `APSystem/AMOSPro_AGA.Lib` dans le
   slot habituel n°14.
2. Avoir `LIBS:c2p.library` v1.9 et un IFF indexé
   **320×256, 4 à 8 bitplanes** ; témoin :
   `iff-TEST/AGA_DEMO_320x256_256c.iff`.
3. Ouvrir un programme AMOS vide puis **Project → Merge ASCII** avec
   l'ASC actif. Sélectionner l'IFF dans `Fsel$`.
   Les banques DATA 12 et 13 sont effacées au démarrage du test.
4. Vérifier l'affichage de l'IFF, du C2P, Blit et Zoom, puis
   appuyer sur **Échap** pour nettoyer et écrire le journal RAM.
5. Journaux : `RAM:C2P_R83_RUNTIME.TXT` et
   `RAM:C2P_R83_COMPILED.TXT`. Attendus :
   `RESULT 1`, `ERR 0`, `CHUNKY_OK 1`,
   `PIXEL_CHECK_COUNT 14`, `CLOSE_RETURNED`.

**État : Gate A/CI PASS, Gates B Runtime/C Compiler R83 non encore
confirmées sous WinUAE.** Ne pas modifier `LAST_GOOD` ni déplacer
l'ASC R83 dans `tests/passed/` avant validation de l'auteur.
Le précédent banc AGAPIC R82, déjà validé, est désormais conservé dans
[`tests/passed/AGAPIC_R82_V2_BANK_PALETTE_01.asc`](../passed/AGAPIC_R82_V2_BANK_PALETTE_01.asc).
