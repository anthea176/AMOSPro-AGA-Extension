# Tests AMOS en cours

**11/11/2026 : aucun fichier `.asc` actif.** Le test M12/R27 0.9.3 des Blitters Safe a passé Gate B sous **AMOS interprété / WinUAE** et a été archivé **sans modification** dans [`tests/passed/M12_R27_SAFE_BLIT_01.asc`](../passed/M12_R27_SAFE_BLIT_01.asc). Git blob original : `3b3a6d8c120b1ec066669231d382eae6e0e4bd82`.

**R27 :** Gate A CPU 68000/CI **403 cas PASS** ([CI finale du binaire](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220)) et Gate B WinUAE **PASS sur le scénario de 40 swaps** : `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED` (fin normale ligne 167). L'utilisateur a confirmé avoir vu les rectangles clignoter. **Pas de confirmation séparée du détail précis des couleurs**, ni de mesure de FPS, Compiler ou Amiga réel. [Rapport R27](../../docs/M12_SAFE_BLITTER_R27.md).

La bibliothèque courante est R27 0.9.3 ; les archives R26/R25/R24 et `LAST_GOOD` R10 restent intactes. Aucune branche supplémentaire.
