# M18 / R60 — benchmark 16×16 CPU AGAPIC vs copie Blitter (13/11/2026)

**Source :** [programme ASC](m18_r60_cpu_vs_blit_16x16.asc) · [protocole](README_M18_CPU_BLIT_16X16.md). **Preuves : deux captures WinUAE transmises par l'auteur le 13/11/2026, toutes deux en AMOS interprété, sous deux profils CPU différents.** **Conditions précisées par l'auteur après la capture : AMOS interprété sous WinUAE, processeur 68030 avec JIT activé (configuration boostée).** La capture seule ne permettait pas de le savoir. La fréquence exacte, le réglage cycle-exact et la configuration RAM ne sont pas consignés. Ce relevé ne constitue **pas** une référence de performance 68020/68EC020 sans JIT.

La sortie indique PAL 320×256×16 couleurs (4 bitplanes), 3 essais par géométrie, 1 tick Timer = 20 ms, N = 1 200 appels par essai.

## 1. Premier relevé : AMOS interprété, WinUAE 68030 + JIT

| Géométrie | CPU Aga Image Region | Blitter Aga Blit Copy | Médiane CPU | Médiane Blitter | Rapport Blitter/CPU |
|---|---|---|---:|---:|---:|
| **ALIGNÉ** — source X=16, destination X=160 | **3 / 2 / 2** | **8 / 7 / 8** | **2 ticks** | **8 ticks** | **4×** |
| **SHIFT X+1** — source X=17, destination X=161 | **2 / 1 / 2** | **12 / 12 / 11** | **2 ticks** | **12 ticks** | **6×** |

Médiane CPU 2 ticks = 40 ms / 1 200 appels, soit ~0,033 ms/appel ; Blitter aligné 8 ticks = 160 ms / 1 200, soit ~0,133 ms/appel ; Blitter décalé 12 ticks = 240 ms / 1 200, soit ~0,200 ms/appel. Ces moyennes **ne sont pas des chronométrages individuels**. La quantification de 20 ms est très grossière lorsque le CPU n'utilise que 1 à 3 ticks par série : rapports indicatifs, non des facteurs précis.

### Fin d'exécution constatée — 68030 + JIT

- **ERR 0** : aucune erreur relevée par le programme. Attention : le script ne vérifie que le dernier code de retour de chaque série de 1 200 appels, pas la totalité des retours.
- **CLOSE -1** : valeur relevée après Aga Screen Close par Aga Mouse X.
- **CHIP BEFORE/END 1799968 1799968** : même valeur Chip Free avant ouverture et après fermeture / effacement de la banque.
- **BENCH FINISHED - CLOSE RETURNED** : fin normale du test visible, pas de Guru à l'écran.
- Aucun contrôle bit à bit des images n'est effectué. La capture ne prouve pas l'identité SHA du binaire effectivement chargé. Le mode interprété et le profil WinUAE 68030 + JIT sont confirmés par le témoignage de l'auteur, pas déductibles de la capture elle-même.

## 2. Deuxième relevé : AMOS interprété, WinUAE 68020 sans JIT

**Preuve : nouvelle capture fournie par l'auteur le 13/11/2026**, explicitement indiquée comme exécutée en **interprété**. Le bandeau visible mentionne **68020 no JIT, 128 Mo Z3 Fast, cycle-exact** ; il s'agit de la configuration déclarée sur la capture, non d'une vérification indépendante des réglages internes WinUAE. La fréquence CPU effective n'est pas documentée. Le benchmark affiche toujours **PAL 320×256×16, 3 essais, N=1 200 appels et tick Timer = 20 ms**.

| Géométrie | CPU Aga Image Region (ticks bruts) | Blitter Aga Blit Copy (ticks bruts) | Médiane CPU | Médiane Blitter | Avantage observé du Blitter |
|---|---|---|---:|---:|---:|
| **ALIGNÉ** — X=16 → 160 | **1245 / 1216 / 1232** | **22 / 22 / 22** | **1232 ticks** | **22 ticks** | **56×** (CPU/Blitter) |
| **SHIFT X+1** — X=17 → 161 | **1225 / 1227 / 1223** | **28 / 28 / 27** | **1225 ticks** | **28 ticks** | **43,75×** (CPU/Blitter) |

D'après les médianes : aligné CPU **24,64 s / 1 200 ≈ 20,53 ms/appel** et Blitter **0,44 s / 1 200 ≈ 0,367 ms/appel** ; décalé CPU **24,50 s / 1 200 ≈ 20,42 ms/appel** et Blitter **0,56 s / 1 200 ≈ 0,467 ms/appel**. Il s'agit de temps *moyens par appel* dérivés de durées de séries, pas de chronométrages isolés. Dans cette configuration, le Blitter termine les séries beaucoup plus rapidement que la voie CPU AGAPIC.

**Fin affichée :** `ERR 0`, `CLOSE -1`, `CHIP BEFORE/END 1845800 1845800`, `BENCH FINISHED - CLOSE RETURNED`. Aucune fuite Chip RAM apparente entre l'avant et l'après dans ce scénario.

**Point de vigilance :** la durée CPU (~20 ms/appel) avoisine **une période PAL entière**. Le benchmark n'insère aucun `Wait Vbl` dans ses boucles chronométrées, mais cette coïncidence justifie de contrôler d'éventuelles synchronisations internes et le profil d'émulation avant d'attribuer l'intégralité du ralentissement aux instructions CPU. **Hypothèse, pas diagnostic démontré.**

**Traçabilité du programme :** la nouvelle capture présente un ajout au bandeau (`68020 no JIT 128Mo Z3Fast cycle exact`) qui **n'apparaît pas dans l'ASC enregistré** `benchmarks/m18_r60_cpu_vs_blit_16x16.asc`. Le corps du benchmark et ses libellés de résultats paraissent correspondre, mais l'identité octet pour octet du programme AMOS local avec le fichier GitHub **n'est pas prouvée**. Cela n'invalide pas les chiffres affichés, mais limite leur statut de comparaison contrôlée.

## Comparaison et limites

**Observations :** dans le premier test (**68030 + JIT**), la commande CPU `Aga Image Region` finit les séries plus rapidement que `Aga Blit Copy`. Dans le second (**68020 sans JIT, cycle-exact indiqué**), le **Blitter** est plus rapide dans les deux géométries. Décaler X de 1 pixel pénalise le Blitter dans les deux profils. **Ne pas comparer ces deux captures comme si seule la présence du JIT avait changé** : CPU, mode d'émulation et RAM diffèrent, et le binaire local exact n'est pas authentifié.

**Hypothèses NON démontrées :** le coût fixe de validation Safe, de préparation et de synchronisation Blitter pourrait dominer sur une surface de 16×16. Les opérations supplémentaires sur les mots non alignés pourraient expliquer une part de l'écart. Les résultats ne prouvent pas que le Blitter est intrinsèquement moins rapide que le CPU. **Le JIT modifie fortement les coûts du code CPU et du pilotage du Blitter : les rapports 4×/6× ne doivent pas être transposés à un 68020 réel, ni à un 68020 WinUAE sans JIT.**

**Comparaison asymétrique :** CPU lit une banque AGAPIC compressée et décode à chaque appel ; la source Blitter est déjà en Chip RAM (staging exclu du chronomètre). Aucun des deux chemins n'est le futur moteur Fast Icon natif non compressé. Le banc teste **4 plans (16 couleurs)**, alors que le prototype Fast Icon Unity AGA cible **8 plans (256 couleurs)**. Ne pas utiliser ces rapports pour choisir un backend AUTO CPU/Blitter.

## Suite

1. **Prochain relevé :** exécuter un **nouvel exécutable AMOS Compiler** du même benchmark en **WinUAE 68020 sans JIT, cycle-exact**, avec les **mêmes paramètres** que le deuxième relevé interprété (vitesse, RAM, écran). Relever les quatre trios de ticks, `ERR`, `CLOSE` et Chip Free. Ne pas supposer que les timings d'un compilé correspondent aux timings de l'interpréteur.
2. **Clarifier la traçabilité :** comparer le programme AMOS effectivement utilisé au fichier ASC du dépôt et consigner précisément le profil WinUAE ; la capture 68020 contient un bandeau de configuration absent de l'ASC GitHub. Si seul le libellé a été ajouté, le documenter sans réécrire le benchmark historique.
3. **Avant de tirer des conclusions de performance :** investiguer la proximité entre ~20 ms/appel CPU et une période PAL (synchronisation potentielle, sans supposer de cause). Pour affiner la mesure, envisager ensuite un banc distinct avec davantage d'appels (par exemple 12 000), **sans modifier le programme de référence actuel**.
4. Réaliser ensuite le moteur Fast Icon natif et mesurer **CPU Fast→Chip contre Blitter Chip→Chip**, y compris le staging, les attentes et le résultat pixel par pixel en opaque/masqué. Garder M18 actif pour CBlock après les icônes.

**Dépôt :** R60 v0.13.5 LAST_GOOD non modifiée, 35 056 octets. Pas de R61, pas de nouvel ASC actif, pas de promotion. Gate D Amiga physique non testée.
