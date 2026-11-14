# R79 C2P Zoom — Gate A native PASS (14/11/2026)

**Statut :** Gate A CPU native **PASS (62 scénarios)**. Gate B WinUAE R79 **NON TESTÉE**, Gate C AMOS Compiler et Gate D Amiga physique **NON TESTÉES**. R73 `LAST_GOOD` conservée, aucune promotion.

## Candidate native déterministe

- **R79 v0.13.24**, `Aga C2P Zoom(SrcBank,SrcPitch,SrcX,SrcY,SrcW,SrcH,DstX,DstY,DstW,DstH)` : fonction entière **10 paramètres**.
- Binaire `dist/AMOSPro_AGA.Lib` **57 344 octets**, SHA256 `ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab`, **69 commandes publiques / 76 entrées AP20**.
- Émetteur natif `tools/c2p_r79_zoom_emit.py` : **1 516 octets** d'instructions compatibles 68000, mais garde CPU **68020+** pour le contrat d'écran AGA. **Append-only** depuis R78 SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`. Seules les entrées natives **73** (ajout `GetP`) et **74** (Zoom) changent.
- Signature AP20 `00,0,0,0,0,0,0,0,0,0` : `D3=DstH`, les neuf arguments précédents consommés depuis `A3`. `D3=1` si dessin, 0 sinon ; `D2=0` en sortie. Anciens registres et code natif préservés ; sept LEA clavier/souris R76 toujours sur `$2F26`.
- Relecture **des deux banques** via `Bnk.GetAdr`, vérification DATA/WORK et tailles réelles, absence de chevauchement physique, contrôle entier/overflow 32 bits avant écriture et refus sans dessin partiel.
- Zoom **nearest-neighbour** par échantillonnage `floor((X-DstX)*SrcW/DstW)` / `floor((Y-DstY)*SrcH/DstH)`. Horizontal **DDA quotient+reste** (pas de division par pixel), vertical une division 16 bits par ligne visible. Destination 320×256 clippée en préservant l'échelle originale ; indice 0 opaque ; pas de Blitter, palette, Convert ou Swap implicites.

## Gate A : vraie exécution 68k

**[GitHub Actions CI source R79 — SUCCESS, 66 étapes](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43603344313)**. Le test de code produit :

```text
R79 C2P ZOOM NATIVE GATE A PASS 62 exact nearest pixels, clipping, bank isolation, CPU/ABI and canaries; WinUAE/Compiler NOT TESTED ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab
```

Les **62 scénarios** comprennent : 5 profondeurs (16/32/64/128/256), 19 cas supplémentaires d'identité, zoom ×2/×4, réduction ×2, non-entiers, 1 pixel source, écran plein 320×256, sous-rectangle source et clipping gauche/droite/haut/bas/corners ; 37 refus de paramètres/banques, en-têtes, overflow, tailles, mémoire, recouvrement et rectangles entièrement hors écran ; 1 refus CPU68000 sans accès aux banques. Les sorties sont comparées octet par octet à une **référence Python indépendante** sur les 81 920 octets du chunky, avec vérification des canaries, des registres, de l'état d'écran, du nombre de recherches de banques et de l'absence d'appels SDK/Blitter. Désassemblage Capstone contrôlé en mode 68000.

La bibliothèque binaire de **57 344 octets** a été extraite du journal CI `[r79-emit]`. Son SHA256 a été **recalculé indépendamment** sur les octets décodés et correspond exactement à `ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab` ; le constructeur est déterministe et part uniquement de R78 SHA figé.

## Gate B à exécuter dans WinUAE

Un seul ASC `tests/current/C2P_R79_ZOOM_01.asc`, construit depuis R78 Gate B PASS et enrichi de Zoom : 5 profondeurs, copies Blit R78 et Close R77 conservées, sept rectangles Zoom (×2, réduction, non-entier, clipping quatre bords), quatre groupes de vérifications de pixels `Peek`, six rejets sûrs, Zoom refusé après Close et restauré après réouverture, Convert/Swap explicites et journal `RAM:C2P_R79_<MODE>.TXT`. `Amos To Back` avant Échap, `Amos To Front` après fermeture et `End` normal.

**Critères :** `RESULT 1`, `PASS_DEPTH 5`, `ZOOM_COPY_OK 5`, `ZOOM_PIXEL_OK 5`, `ZOOM_REJECT_OK 5`, `ZOOM_REOPEN_OK 5`, compteurs Blit/Close/Réouverture à 5, `ERR 0`, `NOS 0`, mémoire Chip/Fast stable attendue. **Aucune Gate B n'est revendiquée sur la seule base des tests CPU.**

**Gate C : une seule compilation AMOS après réussite de la Gate B R79**, pas avant. R73 `dist/AMOSPro_AGA_LAST_GOOD.Lib` (51 608 octets ; SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`) reste protégée.

[Contrat Zoom](C2P_R79_ZOOM_CONTRACT_2026-11-14.md) · [R78 Gate B](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) · [Règles](../EXTENSION_SOURCE_RULES.md).
