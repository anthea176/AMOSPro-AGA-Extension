# M18/R68 — Gate B CBlock Chip : WinUAE interprété PASS (13/11/2026)

**Verdict : GATE B INTERPRÉTÉE PASS, Y COMPRIS CONTRÔLE VISUEL**, sur le scénario `M18_R68_CBLOCK_CHIP_01.asc`. Captures fournies par l'auteur dans la conversation : écran AGA et consoles distinctes **68020 à 14 MHz sans JIT** et **68030 avec JIT**. Les captures elles-mêmes ne sont pas copiées au dépôt. Ce compte rendu transcrit les observations et les deux profils sans les confondre. Ne pas confondre avec un résultat Compiler Gate C ou un essai Amiga physique Gate D.

## Version et périmètre

- **Unique candidate R68 v0.13.13, NON PROMUE** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **51 064 octets**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, **64 commandes / 71 entrées AP20**.
- [ASC R68 exact, archivé sans modification](../tests/passed/M18_R68_CBLOCK_CHIP_01.asc), 250 lignes ; aucune banque supplémentaire chargée, banques temporaires 11/12 et banque de comparaison 13, aucun ABK sauvegardé.
- **Gate A native 48 cas M68000 PASS**, [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43471866604) (export natif strict, pont Compiler V2 simulé, AP20/ABI et régressions historiques). Ce n'est pas la Gate C réelle.
- **R63 `LAST_GOOD` protégée, non modifiée**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. Aucune promotion automatique.

## Capture graphique — conforme

L'écran AGA privé 320×256×256 présente un fond bleu uniforme et les motifs sources en haut : rectangle bicolore rouge/vert avec intérieur noir, rectangle blanc avec intérieur noir. Le test affiche ensuite les restitutions **CPU8 à X8**, **Blitter à X96** (blocs 24×16), et **CPU16 à X160** (bloc 32×16), ainsi que la dernière rangée de bench à Y152.

Les restitutions conservent **la géométrie, les couleurs et les zones noires d'index 0 en mode opaque**, sans trace visible de détérioration du fond bleu ni dépassement autour des blocs. La zone témoin à X240 reste bleue. Contrôle visuel PASS pour les scénarios couverts, **pas une validation exhaustive de toutes les tailles ou des limites mémoire physiques**.

## Console AMOS — premier relevé (68030 avec JIT, 0/0/6 ticks)

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
| `CHIP REC/CURRENT` | `1630912 1630912` | PASS — 68030 JIT ; le 68020 sans JIT est détaillé plus bas |
| `CHIP START/END` | `1801960 1801960` | PASS — 68030 JIT ; le 68020 sans JIT est détaillé plus bas |
| `NOS/CLOSE` | `0 -1` | PASS |
| Verdict console | `RESULT 1`, `CLOSE RETURNED` | **PASS** |

## Mesures WinUAE — deux configurations DISTINCTES

**Méthode identique :** 300 appels par méthode, sur des rectangles 32×16×8 plans, AMOS **interprété** ; mesures en ticks `Timer` (environ 20 ms/tick en PAL). La bibliothèque R68 et l'ASC sont identiques entre les deux essais.

| Méthode | 68020 14 MHz, **JIT OFF** : Capture | 68020 14 MHz, **JIT OFF** : Draw | 68030, **JIT ON** : Capture | 68030, **JIT ON** : Draw |
|---|---:|---:|---:|---:|
| CPU8 (`0`) | 34 | 35 | 0 | 0 |
| CPU16 (`1`) | **28** | **29** | 0 | 0 |
| Blitter (`2`) | 30 | **29** | 6 | 6 |

### Relevé 1 — 68020 à 14 MHz, sans JIT

- Profil confirmé par l'auteur : **68020, 14 MHz, JIT désactivé, 128 Mo Fast Z3**, AMOS interprété.
- `BENCH CAP CPU8/16/BLIT 34 28 30` ; `BENCH DRAW CPU8/16/BLIT 35 29 29`.
- `CHIP REC/CURRENT 1674752 1674752` ; `CHIP START/END 1845800 1845800`.
- `BENCH ERR 0`, `RESULT 1`, `CLOSE RETURNED` ; appels invalides, égalité planaire, recapture et récupération mémoire conformes.
- **CPU16 est le plus rapide en capture** (28 contre 30 pour Blitter), et **à égalité avec Blitter en Draw** (29 contre 29). CPU8 est derrière. Une répétition reste utile pour établir la variabilité.

### Relevé 2 — 68030, avec JIT

- Profil précisé par l'auteur sur la capture comparative : **68030, JIT activé**, AMOS interprété. **Fréquence CPU et quantité de RAM non documentées** pour cet essai ; ne pas reprendre automatiquement les 14 MHz / 128 Mo du 68020.
- `BENCH CAP CPU8/16/BLIT 0 0 6` ; `BENCH DRAW CPU8/16/BLIT 0 0 6`.
- `CHIP REC/CURRENT 1630912 1630912` ; `CHIP START/END 1801960 1801960`.
- `BENCH ERR 0`, `RESULT 1`, `CLOSE RETURNED`.
- Les **0 ticks CPU8/CPU16 sont sous la résolution** de `Timer` et ne prouvent ni un coût nul, ni un gagnant entre CPU8 et CPU16. **6 ticks Blitter ≈ 120 ms pour 300 appels**, sans extrapolation au matériel réel.

**Conclusion limitée au protocole observé :** R68 Gates A/B PASS pour les opérations testées dans **les deux profils**. Les réglages JIT produisent des mesures de vitesse très différentes ; **ne pas attribuer les valeurs 0/0/6 au 68020 sans JIT**. Le test graphique confirme l'affichage du scénario, mais ne constitue pas une nouvelle preuve graphique indépendante pour chaque profil.

**Suite performance :** répéter les mesures sur **68020 et 68030 sans JIT**, documenter fréquences/mémoire, augmenter N si nécessaire et comparer des séries répétées. Les résultats JIT ne sont pas transposables directement à un Amiga physique.

## Gates indépendantes et suite

- **Gate A M68000 native : PASS**, 48 cas et CI complète.
- **Gate B AMOS interprété WinUAE : PASS**, deux captures utilisateur (écran + console), rendu, indices, recapture, erreurs, mémoire et fermeture conformes.
- **Gate C AMOS Compiler réelle : NON TESTÉE** ; une seule exécution manuelle réservée à **la fin de M18**.
- **Gate D Amiga AGA physique : NON TESTÉE**.
- **Candidate R68 NON PROMUE**. `dist/AMOSPro_AGA.Lib` conserve la même SHA, `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R63. Aucun changement de branche (toujours `main`), pas de publication Aminet.
