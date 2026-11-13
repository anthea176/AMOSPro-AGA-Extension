# M18 / R68 — CBlock PERF-02 : résultats WinUAE 68020/68030 sans JIT (13/11/2026)

**Résultat : PERF-02 PASS sur deux configurations WinUAE, AMOS interprété, JIT désactivé pour les deux.** `RUNS/ERR/MIS/MEM 17 0 0 0`, `RESULT 1` et `CLOSE RETURNED` observés deux fois. Les captures de console ont été fournies par l'auteur dans la conversation, sous les noms `image(20261113-181316).png` et `image(20261113-181744).png` ; **aucun PNG n'est copié dans le dépôt**.

## Bibliothèque et test

- **R68 v0.13.13**, [unique binaire](../dist/AMOSPro_AGA.Lib) : **51 064 octets**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, 64 commandes / 71 entrées AP20 ; inchangé et **NON PROMU**.
- [ASC PERF-02 original archivé et non modifié](../tests/passed/M18_R68_CBLOCK_PERF_02.asc) ; six dimensions, 17 combinaisons taille/méthode, chaque mesure couvre **deux passes**.
- **Gate A native PASS** (48 cas M68000), **Gate B fonctionnelle WinUAE R68 PASS** avec les [captures graphique/console antérieures](M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md). PERF-02 ajoute une **qualification fonctionnelle et comparative** sur six tailles, pas une compilation réelle.
- Dernière CI du benchmark [GitHub Actions 43477512578 : PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43477512578).
- **R63 `LAST_GOOD` protégée** : SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`, intacte.

## Conditions WinUAE

| Relevé | CPU émulé | Fréquence | Fast RAM | JIT | AMOS |
|---|---|---:|---|---|---|
| A | **68020** | **14 MHz** | **128 Mo Zorro III** | **OFF** | **Interprété** |
| B | **68030** | **28 MHz** | **128 Mo Zorro III** | **OFF** | **Interprété** |

**Attention :** ne pas les confondre avec l'ancien benchmark 68030 **avec JIT** qui donnait `0/0/6` ticks et n'appartient pas à PERF-02.

## Mesures PERF-02

Toutes les durées sont des **ticks AMOS `Timer`** pour le **nombre d'appels N affiché**. Ordre de chaque triplet : **CPU8 / CPU16 / Blitter** ; `C` = `Capture` ; `D` = `Draw`. Les N appels **s'appliquent à chacune des deux opérations**, indépendamment. En PAL, un tick vaut environ 20 ms.

| S | Rectangle | N (2 passes) | 68020 C | 68020 D | 68030 C | 68030 D |
|---:|---|---:|---|---|---|---|
| 0 | 16×16 | 1200 | `122/108/106` | `112/100/97` | `77/66/68` | `74/62/62` |
| 1 | 24×16 | 1000 | `110/-1/99` | `104/-1/90` | `74/-1/66` | `69/-1/62` |
| 2 | 32×16 | 800 | `98/81/78` | `91/74/73` | `66/56/53` | `64/50/50` |
| 3 | 64×48 | 240 | `81/56/47` | `81/55/46` | `67/43/38` | `66/41/38` |
| 4 | 128×96 | 80 | `84/48/42` | `86/48/43` | `77/41/40` | `76/42/40` |
| 5 | 320×64 | 70 | `113/62/59` | `112/60/59` | `106/55/57` | `106/56/56` |

`-1` dans le cas **24×16 CPU16** : **méthode volontairement sautée**, largeur non multiple de 16 pixels. Ce n'est pas un échec.

## Contrôles d'intégrité (captures de console)

| Contrôle | 68020 JIT OFF | 68030 JIT OFF |
|---|---|---|
| `RUNS/ERR/MIS/MEM` | `17 0 0 0` | `17 0 0 0` |
| `CHIP START/END` | `1845800 1845800` | `1845768 1845768` |
| `NOS/CLOSE` | `0 -1` | `0 -1` |
| `RESULT` | `1` | `1` |
| Fin | `CLOSE RETURNED` | `CLOSE RETURNED` |

`MIS=0` : **comparaison octet par octet des plans** contre une recapture de destination après chaque chemin, vérification faite **hors chronométrage**. `MEM=0` : réemploi sans réallocation inattendue et retour au niveau de Chip RAM avant allocation ; la Chip libre retrouve exactement son niveau initial à la fermeture. Aucun échec de `Capture` ni `Draw` sur les méthodes supportées.

## Lecture technique et limites

- **68020 / 14 MHz / JIT OFF :** le **Blitter est le plus rapide** dans presque tous les scénarios testés. Pour **64×48**, capture `47` ticks contre `56` CPU16, restitution `46` contre `55`. Pour **128×96**, `42` contre `48` en capture et `43` contre `48` en restitution. **CPU8 est systématiquement plus lent**.
- **68030 / 28 MHz / JIT OFF :** CPU16 est **légèrement meilleur en capture 16×16** (`66` vs `68` Blitter) et **320×64** (`55` vs `57`) ; la restitution est **ex æquo** pour ces tailles (`62/62` et `56/56`). Le **Blitter** reste plus rapide pour 24×16 (CPU16 non applicable), 32×16 en capture, 64×48 et 128×96.
- Les écarts **1 à 3 ticks** peuvent fluctuer avec la résolution `Timer`, le rafraîchissement et les conditions d'émulation. Les valeurs incluent le coût du wrapper AP20, contrôles banque, Safe/WaitBlit et l'appel AMOS ; elles excluent l'allocation initiale.
- Ces résultats **ne permettent pas encore de fixer un basculement automatique CPU16/Blitter** indépendant du processeur et de la taille, ni de déduire les performances sur un Amiga AGA physique. Ils démontrent cependant **le bon fonctionnement** et donnent une première base crédible sans JIT.

## Suite M18

Les tests PERF-02 sur **les deux CPU sans JIT sont terminés et l'ASC est archivé**. On peut établir une politique de sélection explicite par taille/alignement/CPU ou poursuivre des tests de répétabilité ciblés avant de modifier le chemin de copie. Toute modification effective de l'extension requerrait de nouvelles Gates A/B ; **ne pas toucher aux routines R68 déjà validées sans besoin justifié**.

**Gate C Compiler AMOS réelle : toujours NON TESTÉE, une seule exécution manuelle en fin M18. Gate D Amiga physique : NON TESTÉE.** Aucun changement du binaire, de la branche (`main`) ni de `LAST_GOOD`.
