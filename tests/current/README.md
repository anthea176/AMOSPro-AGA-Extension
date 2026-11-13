# M18 — Tests AMOS actifs

**Aucun ASC actif** après validation et archivage de **R68 v0.13.13 — CBlock Chip, Gates A/B PASS** le 13 novembre 2026.

- [ASC R68 exact et non modifié](../passed/M18_R68_CBLOCK_CHIP_01.asc), interprété sous WinUAE : rendu graphique et console confirmés (`RESULT 1`, `CLOSE RETURNED`), mémoire Chip récupérée
- [Rapport R68 WinUAE Gate B](../../docs/M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md) : mesures CPU8/CPU16/Blitter `0/0/6` ticks pour 300 captures et `0/0/6` pour 300 dessins ; résultats CPU sous la résolution de Timer
- Unique bibliothèque de travail [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) : R68, **51 064 octets**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, **NON PROMUE**
- R63 [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) protégée, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba` ; **aucun AMOS Compiler avant la Gate C manuelle unique de fin M18**

**Prochaine mesure possible :** nouveau benchmark en interprété pour **68020/68030 sans JIT**, N supérieur afin de résoudre les chronos CPU. Créer alors **un seul nouvel ASC** dans `tests/current/`, sans modifier `tests/passed/`. Les ABK historiques existants dans ce répertoire restent en place.
