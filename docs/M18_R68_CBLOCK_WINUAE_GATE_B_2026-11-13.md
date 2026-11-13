# M18/R68 — Gate B CBlock Chip : WinUAE interprété PASS (13/11/2026)

**Verdict : GATE B INTERPRÉTÉE PASS, Y COMPRIS CONTRÔLE VISUEL**, sur le scénario `M18_R68_CBLOCK_CHIP_01.asc`. Deux captures fournies par l'auteur dans la conversation : une de l'écran graphique WinUAE (nom reçu `image(20261113-172717).png`) et une de la console AMOS (`image(20261113-172735).png`). **Les captures ne sont pas copiées dans ce dépôt** ; ce compte rendu transcrit les observations. Ne pas confondre avec un résultat Compiler Gate C ou un essai Amiga physique Gate D.

## Version et périmètre

- **Unique candidate R68 v0.13.13, NON PROMUE** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **51 064 octets**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, **64 commandes / 71 entrées AP20**.
- [ASC R68 exact, archivé sans modification](../tests/passed/M18_R68_CBLOCK_CHIP_01.asc), 250 lignes ; aucune banque supplémentaire chargée, banques temporaires 11/12 et banque de comparaison 13, aucun ABK sauvegardé.
- **Gate A native 48 cas M68000 PASS**, [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43471866604) (export natif strict, pont Compiler V2 simulé, AP20/ABI et régressions historiques). Ce n'est pas la Gate C réelle.
- **R63 `LAST_GOOD` protégée, non modifiée**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. Aucune promotion automatique.

## Capture graphique — conforme

L'écran AGA privé 320×256×256 présente un fond bleu uniforme et les motifs sources en haut : rectangle bicolore rouge/vert avec intérieur noir, rectangle blanc avec intérieur noir. Le test affiche ensuite les restitutions **CPU8 à X8**, **Blitter à X96** (blocs 24×16), et **CPU16 à X160** (bloc 32×16), ainsi que la dernière rangée de bench à Y152.

Les restitutions conservent **la géométrie, les couleurs et les zones noires d'index 0 en mode opaque**, sans trace visible de détérioration du fond bleu ni dépassement autour des blocs. La zone témoin à X240 reste bleue. Contrôle visuel PASS pour les scénarios couverts, **pas une validation exhaustive de toutes les tailles ou des limites mémoire physiques**.

## Console AMOS — valeurs observées

| Ligne | Valeur visible | Verdict |
|---|---|---|
| `OPEN/DB/SWAPS` | `1 1 1 1` | PASS |
| `CAP24/RECAP/SAME` | `1 1 1` | PASS — réemploi de la même banque |
| `BLIT/CPU8/WORD DRAW` | `1 1 1` | PASS |
| `REST24/32` | `1 1` | PASS |
| `LEN 24/32` | `552 552` | PASS — 40 octets d'en-tête et 512 octets planaires |
| `PLANE EQ BLIT/CPU8/WORD` | `1 1 1` | PASS — égalité du contenu planaire capturé |
| `BYTE MISMATCH` | `0 0 0` | PASS |
| `BAD 8/DIM/WORD/OUT` | `0 0 0 0` | PASS — appels invalides rejetés |
| `BAD BANK/MODE/X` | `0 0 0` | PASS |
| `BENCH ERR` | `0` | PASS |
| `CHIP REC/CURRENT` | `1630912 1630912` | PASS — aucune baisse de Chip Free à la recapture |
| `CHIP START/END` | `1801960 1801960` | PASS — récupération intégrale mesurée de la mémoire après `Erase` et fermeture |
| `NOS/CLOSE` | `0 -1` | PASS |
| Verdict console | `RESULT 1`, `CLOSE RETURNED` | **PASS** |

## Mesures WinUAE préliminaires — 300 appels par mode

| Chemin `Method` | Capture / 300 | Draw / 300 |
|---|---:|---:|
| CPU8 (`0`) | 0 ticks | 0 ticks |
| CPU16 (`1`) | 0 ticks | 0 ticks |
| Blitter (`2`) | 6 ticks | 6 ticks |

**Configuration WinUAE confirmée par l'auteur après les deux captures : 68020 à 14 MHz, 128 Mo de Fast RAM Zorro III (Z3), AMOS exécuté en interprété.** État JIT non explicitement confirmé. Les 128 Mo Z3 sont de la Fast RAM et ne changent pas l'obligation de stocker les CBlocks en Chip RAM.

**Le banc mesure deux séries distinctes de 300 appels**, avec la même banque préallouée et le même rectangle **32×16×8 plans**. En PAL, **6 ticks représentent environ 120 ms par série, soit 0,4 ms/appel**. Les **0 ticks CPU** signifient uniquement que `Timer` ne résout pas la durée entre ses deux lectures ; **cela ne veut pas dire coût CPU nul**.

La capture WinUAE montre environ **49,7 FPS**. L'auteur a confirmé **68020 / 14 MHz / 128 Mo Fast Z3 / AMOS interprété** ; **le réglage JIT n'est pas établi par sa seule déclaration**. Ces chronos sont une **mesure ponctuelle**, et ne démontrent **pas** une supériorité générale du CPU, ni du Blitter, ni des gains sur Amiga réel.

**Pour comparer les performances :** refaire plusieurs séries sur **68020 et 68030 sans JIT**, paramètres WinUAE documentés, éventuellement augmenter fortement N pour sortir de la quantification de `Timer` sur les méthodes CPU. Une nouvelle variante d'ASC devra être créée dans `tests/current/` ; **ne jamais modifier cet ASC R68 désormais archivé et figé**.

## Gates indépendantes et suite

- **Gate A M68000 native : PASS**, 48 cas et CI complète.
- **Gate B AMOS interprété WinUAE : PASS**, deux captures utilisateur (écran + console), rendu, indices, recapture, erreurs, mémoire et fermeture conformes.
- **Gate C AMOS Compiler réelle : NON TESTÉE** ; une seule exécution manuelle réservée à **la fin de M18**.
- **Gate D Amiga AGA physique : NON TESTÉE**.
- **Candidate R68 NON PROMUE**. `dist/AMOSPro_AGA.Lib` conserve la même SHA, `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R63. Aucun changement de branche (toujours `main`), pas de publication Aminet.
