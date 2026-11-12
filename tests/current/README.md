# Test AMOS courant — M16/R46 `Aga Image Draw`

**Unique ASC actif :** [`M16_R46_IMAGE_DRAW_01.asc`](M16_R46_IMAGE_DRAW_01.asc). Installer [R46 v0.12.1 candidate](../../dist/AMOSPro_AGA.Lib) sous WinUAE, **relancer AMOS après remplacement de la bibliothèque**, placer la banque [`M16_AGAPIC_SAMPLE_BANK10.abk`](M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire courant, puis importer le test par **Project → Merge ASCII**. Le test écrase la banque AMOS 10.

**Gate A R46 PASS** : 258 scénarios CPU 68000 et export assembleur strict validés ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43221899949)). **Gate B WinUAE R46 NON TESTÉE.** R45 a échoué (flags natifs 0 non acceptés), [ASC R45 archivé sans retouche](../failed/M16_R45_IMAGE_DRAW_01.asc). [Diagnostic du bug et correctif](../../docs/M16_R46_FLAGS0_FIX.md).

**Visuel attendu :** trois cadres contenant une mosaïque 64×40, une image opaque et deux images masquées circulaires ; portions visibles sur les quatre bords. Vérifier couleur 0 opaque (rose), trous transparents laissant le décor, décalage X, Safe et fermeture. Sortie attendue : `OPAQUE 1 MASK 1 SHIFT 1`, `CLIP 1 1 1 1`, `BAD 0 0 0 OUT 1`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, `ERRORS 0 RESULT 1`, `CLOSE RETURNED`. Diagnostic banque : `NATIVE LEN 1852 WANT 1852`, `NATIVE NO 10 FLAGS 0`, `NATIVE NAME AGAPIC`, `STREAM 196 TOTAL 1836`.

**R44 v0.11.5 demeure `LAST_GOOD`** ([binaire gelé](../../dist/AMOSPro_AGA_LAST_GOOD.Lib)). Ne pas promouvoir R46 avant confirmation utilisateur. Gates C Compiler et D Amiga AGA réel non testées.
