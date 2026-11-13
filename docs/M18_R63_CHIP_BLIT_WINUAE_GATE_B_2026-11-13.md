# M18/R63 — Gate B WinUAE interprétée, cache Chip / Blitter 256 couleurs

**Promotion approuvée le 13/11/2026 après [régression complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43436834490).** Lib active et `LAST_GOOD` identiques (38 736 octets, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`) ; [ASC archivé](../tests/passed/M18_R63_CHIP_BLIT_01.asc), [R60 historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/67315eb0f9dee6b742b841c92b5258e1f7a0f765/dist/AMOSPro_AGA_LAST_GOOD.Lib). Aucun changement du natif ni compilation R63.
**Date du test : 13 novembre 2026 — résultat de l'ASC : PASS.**

**Version testée :** R63 v0.13.8, [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) (38 736 octets, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`). [ASC exact archivé](../tests/passed/M18_R63_CHIP_BLIT_01.asc), exécuté **en interprété** sous WinUAE. **Aucune compilation manuelle effectuée pour R63.**

## Résultats relevés sur la capture utilisateur

| Contrôle affiché | Valeur | Verdict |
|---|---|---|
| `RESULT` | **1** | PASS du protocole d'essai |
| `OPEN / DB / SW0 / SAFE` | `1 / 1 / 1 / 1` | PASS |
| `ICON 1 2 3 4 / SHIFT` | `1 / 1 / 1 / 1 / 1` | PASS (retours CPU) |
| `BLIT 1 2 3 4 / SHIFT` | `1 / 1 / 1 / 1 / 1` | PASS (retours Blitter) |
| `BCLP` quatre bords / `OUT` | `1 / 1 / 1 / 1 / 1` | PASS (retours clipping et hors écran) |
| `BCBAD` banque/ID/mode | `0 / 0 / 0` | Rejets corrects |
| `CLIP` CPU quatre bords / `OUT` | `1 / 1 / 1 / 1 / 1` | PASS (retours) |
| `BAD BANK/ID/MODE` | `0 / 0 / 0` | Rejets corrects |
| `R60 REJECT / SWAP / NOS / CLOSE` | `0 / 1 / 0 / -1` | PASS |
| `BANK11 FLAGS OLD / NEW` | `0 / 3` | Banque chargée puis transférée en Chip |
| `BANK 11 START` | `301416` | Valeur observée (pas une adresse fixe) |
| `BANK11 CHIP DELTA / FAST DELTA` | `1192 / 0` octets | Allocation Chip constatée |
| `CHIP PRELOAD/END` | `1796440 / 1796440` octets | Aucune fuite détectée par ce test |
| `CHIP CACHE ACTIVE` | `1795248` octets libres | Cache vivant : 1 192 octets occupés |
| Fin du programme | `CLOSE RETURNED` | Sortie des écrans AGA sans erreur visible |

## Cause et corrections du protocole d'essai

Les premiers essais R62/R63 renvoyaient `BLIT 0` parce que la banque cache était chargée sans assurer **son placement réel en Chip RAM**. Le fichier ABK et les flags natifs avant déplacement ne suffisaient pas pour que le Blitter puisse y accéder. L'ASC utilise désormais, après `Load` :

```amos
Bank Permanent 11
Bank To Chip 11
```

Ces commandes AMCAF déplacent le cache vers la Chip ; le code natif conserve `TypeOfMem(MEMF_CHIP)` avant toute opération DMA.

Un essai intermédiaire renvoyait tous les `BLIT = 1`, mais `RESULT 0` à cause d'une mauvaise comparaison de la mémoire libre **cache encore alloué / cache effacé**. L'ASC final prend `_CF_BASE=Chip Free` **avant les deux `Load`**, puis `_CF1=Chip Free` **après les deux `Erase`**. Il affiche séparément `_CF0` quand le cache est actif. Le nouvel essai affiche **`RESULT 1` et aucune fuite sur ce périmètre**.

## Limites et prochaines étapes

- **Gate A : PASS** — 260 cas CPU/ABI 68000 natifs et simulation Compiler V2 en CI, [run 43429500351](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43429500351).
- **Gate B : PASS sur l'ASC interprété WinUAE** (`RESULT 1`, retours et comptabilité mémoire conformes).
- **Rendu pixel à pixel / vérification visuelle : non démontrée par cette capture**, qui montre exclusivement l'écran de résultats. Une capture de l'écran graphique permettra de confirmer la conformité opaque/masquée.
- **Gate C : non testée**, volontairement réservée à une **unique compilation manuelle à la fin du chantier M18**.
- **Gate D : non testée** sur Amiga physique.
- **Performances : non mesurées pour R63**. La banque `FICHIP8` est pré-stagée sur PC ; le futur staging dynamique Fast→Chip et son coût seront étudiés séparément.

**Aucun changement au code natif R63 ni au binaire `dist/AMOSPro_AGA.Lib`. `dist/AMOSPro_AGA_LAST_GOOD.Lib` est maintenant une copie binaire exacte de R63 après approbation et régression complète PASS ; R60 est préservée dans Git.** L'ASC actif unique reste celui de R63.
