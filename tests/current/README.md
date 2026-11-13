# OPT020/P2 R71 - Gate B WinUAE interpree pending

**Seule bibliotheque active :** `dist/AMOSPro_AGA.Lib`, candidate **R71 v0.13.16**, 51 460 octets, SHA256 `1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0`. R71 conserve le code natif P1e (entree 59) de R69 et le peintre P2 de R70, mais corrige trois branchements relatifs dans les entrees 20, 57 et 58. **Gate A/CI en attente. Gate B WinUAE NON TESTEE ; Gate C Compiler NON TESTEE.** Ne pas promouvoir.

**R68 LAST_GOOD immuable :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. R69 conserve sa validation WinUAE et ses benchmarks dans les historiques ; R70 a echoue en interprete avec Guru `80000004`.

**ASC unique :** [OPT020_P2_R71_INTERPRETED_01.asc](OPT020_P2_R71_INTERPRETED_01.asc) avec `M16_AGAPIC_SAMPLE_BANK10.abk`. Scenario integre : `Aga Blit Clear` puis `Aga Blit Fill` avant `Aga Image Draw`, `Aga Image Region`, et `Aga Bank Image Draw`. Les valeurs de retour, l'image, `RESULT 1`, `CLOSE RETURNED` et l'absence de Guru doivent etre verifies sous WinUAE 68020 14 MHz, JIT OFF, PAL, AMOS interprete. Gate B reste FAIL/INCONNUE jusqu'aux resultats reels de l'auteur.

**Important :** installer le binaire correspondant dans le slot AGA d'AMOS/APSystem et redemarrer AMOS. Ne pas lancer AMOS Compiler. Les tests Musashi, la CI et la reconstruction AP20 ne prouvent jamais la Gate B.

[Incident R70](../../docs/OPT020_P2_R70_GURU_80000004_2026-11-13.md) | [Correctif R71](../../docs/OPT020_P2_R71_LINK_REPAIR_2026-11-13.md)
