# Tests AMOS actifs

**Aucun test `.asc` actif** après validation de R37 0.10.9 sous AMOS interprété/WinUAE le 11/11/2026.

Le test [`M14_R37_FONT_SELECT_01.asc`](../passed/M14_R37_FONT_SELECT_01.asc) a été déplacé vers `tests/passed/` **à l'octet près** : Git blob `5371c310142f33aa2312e59ed81e2e2d6b90da3d`, inchangé. Capture utilisateur : `OPEN 1 DB 1 PALETTE 1 1`, `SEL8 1 TX8 1 SEL9 1 TX9 1`, `BAD0/BAD256/BADNAME 0`, `KEEP 1 RESET 1 DEFAULT 1`, `SWAP 1 NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fonctionnement visuel confirmé.

**R37 v0.10.9 est `LAST_GOOD` WinUAE-PASS** : `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R37, **22 328 octets**, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`. L'archive R36 v0.10.8 (21 836 octets, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`) est préservée.

Gates C Compiler et D Amiga AGA réel **non testées**. R38 (banques de fontes AMCAF) et R39 (fontes bitmap 8x8) nécessiteront un contrat individuel avant tout code.
