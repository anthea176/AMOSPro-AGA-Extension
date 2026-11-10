# M4b — état consolidé

## R6C-R1 — VALIDÉ interprété + compilé

Version stable :

`archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib`

Fichiers courants :

- `dist/AMOSPro_AGA.Lib`
- `dist/AMOSPro_AGA_LAST_GOOD.Lib`

Identité :

- taille : **2564 octets**
- SHA256 : `a2d36ac198b5bfe18d50a223f4001c8ce0773d15310145d9d081abaddc2a6615`

Validation runtime :

- Open / Close / Double Buffer : **OK**
- 100 swaps : **OK**
- Back Fill simple : **OK**
- Back Fill + Swap visuel : **OK**
- 50 cycles Back Fill + Swap en interprété : **50/50 OK**
- le même test compilé avec AMOS Compiler : **50/50 OK**
- TOTAL FAILURES : **0**
- aucun blocage : **OK**

## Conclusion

**M4b est clôturé.**

Le test compilé dédié `M4B_R6C_04_COMPILED.asc` est devenu inutile : le test 03, plus exigeant, a été validé directement en version compilée.
