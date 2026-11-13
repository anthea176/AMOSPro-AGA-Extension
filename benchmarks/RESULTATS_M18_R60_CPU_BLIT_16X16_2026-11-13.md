# M18 / R60 — benchmark 16×16 CPU AGAPIC vs copie Blitter (13/11/2026)

**Source :** [programme ASC](m18_r60_cpu_vs_blit_16x16.asc) · [protocole](README_M18_CPU_BLIT_16X16.md). **Preuves : quatre captures WinUAE transmises par l'auteur le 13/11/2026 : AMOS interprété 68030/JIT, AMOS interprété et compilé 68020 sans JIT, puis **AMOS compilé 68030 à 50 MHz sans JIT, avec le même exécutable compilé que pour le 68020 (aucune recompilation)**.** **Conditions précisées par l'auteur après la capture : AMOS interprété sous WinUAE, processeur 68030 avec JIT activé (configuration boostée).** La capture seule ne permettait pas de le savoir. La fréquence exacte, le réglage cycle-exact et la configuration RAM ne sont pas consignés. Ce relevé ne constitue **pas** une référence de performance 68020/68EC020 sans JIT.

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

## 3. Troisième relevé : AMOS compilé, WinUAE 68020 sans JIT

**Preuve : troisième capture transmise par l'auteur le 13/11/2026, mode AMOS compilé confirmé par l'auteur.** Bandeau visible : `68020 no JIT 128Mo Z3Fast cycle exact`. Comme pour l'interprété 68020, il s'agit des réglages **déclarés à l'écran**, non d'une vérification indépendante de WinUAE ni du SHA de la bibliothèque installée. Fréquence effective non mesurée. PAL 320×256×16, **N=1 200 appels**, 3 essais, `Timer` à 20 ms par tick.

| Géométrie | CPU Aga Image Region (ticks bruts) | Blitter Aga Blit Copy (ticks bruts) | Médiane CPU | Médiane Blitter | Rapport CPU/Blitter |
|---|---|---|---:|---:|---:|
| **ALIGNÉ** | **1179 / 1178 / 1179** | **16 / 16 / 16** | **1179 ticks** | **16 ticks** | **73,69×** |
| **SHIFT X+1** | **1178 / 1178 / 1179** | **21 / 21 / 21** | **1178 ticks** | **21 ticks** | **56,10×** |

D'après les médianes, temps **moyens** par appel (durée de série / 1 200) : CPU aligné **19,65 ms**, CPU X+1 **19,63 ms**, Blitter aligné **0,267 ms**, Blitter X+1 **0,350 ms**. Les facteurs calculés concernent **ces deux commandes R60 et leurs conditions de préparation distinctes**, pas les futurs Fast Icons.

**Fin d'exécution visible :** `ERR 0`, `CLOSE -1`, `CHIP BEFORE/END 1894528 1894528`, `BENCH FINISHED - CLOSE RETURNED`. Aucune fuite Chip RAM visible dans ce scénario. La quantité de mémoire Chip libre diffère de celle observée en interprété (1 845 800) : cela ne constitue **pas** une fuite entre modes, car le contexte mémoire n'est pas identique.

**Traçabilité :** le bandeau de configuration `68020 no JIT 128Mo Z3Fast cycle exact` figure sur la capture compilée mais pas dans le fichier ASC original du dépôt. L'identité exacte du programme source local compilé et celle de la `.Lib` chargée ne sont pas établies par cette seule capture. Aucun autre changement fonctionnel du programme n'est démontré.

### Comparaison à configuration 68020 sans JIT déclarée identique

| Géométrie / commande | Interprété (médiane ticks) | Compilé (médiane ticks) | Réduction en compilé |
|---|---:|---:|---:|
| CPU aligné | 1232 | 1179 | **4,30 %** |
| Blitter aligné | 22 | 16 | **27,27 %** |
| CPU X+1 | 1225 | 1178 | **3,84 %** |
| Blitter X+1 | 28 | 21 | **25,00 %** |

Le compilé **n'élimine pas** le coût CPU observé : celui-ci reste voisin de **19,6 ms/appel**, alors que la voie Blitter se situe entre **0,27 et 0,35 ms/appel**. L'overhead de l'interpréteur n'explique donc vraisemblablement **pas l'essentiel** du temps mesuré pour `Aga Image Region` dans ce scénario. La proximité d'une période PAL **n'est pas une preuve de synchronisation VBL** ; il faut lire le code natif et vérifier les étapes chronométrées avant de conclure.

## 4. Quatrième relevé : AMOS compilé, WinUAE 68030 à 50 MHz, sans JIT

**Preuve : capture et précision explicite de l'auteur du 13/11/2026.** Ce passage est **en compilé**, exécuté sous **WinUAE 68030 à 50 MHz, sans JIT**. **Il n'a PAS recompilé le programme entre les deux relevés compilés 68020 et 68030 : c'est le même exécutable AMOS**, seul le processeur émulé a été reconfiguré. **Le bandeau CPU intégré au programme compilé n'a pas été régénéré : une indication « 68020 » peut donc subsister et ne reflète pas le processeur émulé au moment de la mesure.** Les 128 Mo Z3 Fast et l'option cycle-exact sont mentionnés sur la capture ; les réglages internes WinUAE ne sont pas audités indépendamment. La SHA de l'exécutable local n'a pas été relevée.

| Géométrie | CPU Aga Image Region (ticks) | Blitter Aga Blit Copy (ticks) | Médiane CPU | Médiane Blitter | Avantage observé du Blitter |
|---|---|---|---:|---:|---:|
| **ALIGNÉ** | **415 / 415 / 415** | **10 / 10 / 10** | **415 ticks** | **10 ticks** | **41,50×** |
| **SHIFT X+1** | **415 / 415 / 415** | **15 / 15 / 15** | **415 ticks** | **15 ticks** | **27,67×** |

PAL 320×256×16 couleurs, 3 répétitions, 1 200 appels par série, `Timer` PAL = 20 ms/tick. Temps moyens déduits des médianes : **CPU 415×20/1200 = 6,917 ms/appel** dans les deux cas ; **Blitter aligné 0,167 ms/appel** ; **Blitter X+1 0,250 ms/appel**. Les ratios décrivent **Aga Image Region (RLE + dessin CPU) versus Aga Blit Copy (source préparée en Chip hors chronométrage)**, pas les futurs Fast Icons.

**Fin de série visible :** `ERR 0`, `CLOSE -1`, `CHIP BEFORE/END 1894528 1894528`, `BENCH FINISHED - CLOSE RETURNED`. Pas de fuite Chip apparente sur ce passage. Identité SHA de la bibliothèque réellement chargée non prouvée.

**Comparaison des deux passages compilés avec le même exécutable, sans JIT :** CPU aligné **1179 → 415 ticks** (temps **2,84× inférieur**), Blitter aligné **16 → 10** (**1,60×**) ; CPU X+1 **1178 → 415** (**2,84×**), Blitter X+1 **21 → 15** (**1,40×**). Le même code compilé écarte **un changement de programme ou de mode AMOS** comme explication de cet écart. La comparaison porte toujours sur **deux configurations de CPU émulé différentes**, et non sur une variation indépendante de la seule fréquence ou une mesure physique des cycles.

**Incidence sur le diagnostic précédent :** avec ce profil 68030 à 50 MHz sans JIT, le CPU prend ≈**6,9 ms/appel**, contre ≈**19,6–20,5 ms/appel** sur le profil 68020 sans JIT. Cette variation importante **affaiblit** l'idée d'une attente fixe d'un VBL PAL (~20 ms) à chaque appel ; elle est compatible avec un temps majoritairement dépensé en calculs et accès mémoire (parcours RLE double passe et écriture pixel/bitplane), **mais ne démontre ni l'absence totale de synchronisation ni la proportion de chaque coût**. L'émetteur natif R60 n'appelle pas explicitement `Wait Vbl` ni `WaitBlit` dans le chemin `Aga Image Region`.

**Traçabilité corrigée :** l'auteur confirme la **réutilisation du même exécutable compilé entre 68020 et 68030**, sans recompilation. Son libellé CPU ancien est donc **périmé**, pas une contradiction sur la configuration WinUAE réellement sélectionnée. La variante ASC locale avec bandeau de configuration n'est toujours pas identique au fichier de benchmark archivé sur GitHub ; le SHA de l'exécutable local et celui de la bibliothèque chargée restent non vérifiés.

## Comparaison et limites

**Observations :** dans le premier test (**68030 + JIT interprété**), la commande CPU `Aga Image Region` finit les séries plus rapidement que `Aga Blit Copy`. Dans les **trois relevés sans JIT** (**68020 interprété, 68020 compilé, 68030 50 MHz compilé à exécutable identique, cycle-exact indiqué**), le **Blitter** est plus rapide dans les deux géométries. Décaler X de 1 pixel pénalise le Blitter dans les deux profils. **Ne pas comparer le premier passage 68030/JIT aux trois passages sans JIT comme si seule la présence du JIT avait changé.** En revanche, **les deux passages compilés 68020/68030 utilisent le même exécutable** selon l'auteur ; cela fournit une comparaison des profils CPU, sans isoler à elle seule fréquence, modèle et paramètres internes.

**Hypothèses NON démontrées :** le coût fixe de validation Safe, de préparation et de synchronisation Blitter pourrait dominer sur une surface de 16×16. Les opérations supplémentaires sur les mots non alignés pourraient expliquer une part de l'écart. Les résultats ne prouvent pas que le Blitter est intrinsèquement moins rapide que le CPU. **Le JIT modifie fortement les coûts du code CPU et du pilotage du Blitter : les rapports 4×/6× ne doivent pas être transposés à un 68020 réel, ni à un 68020 WinUAE sans JIT.**

**Comparaison asymétrique :** CPU lit une banque AGAPIC compressée et décode à chaque appel ; la source Blitter est déjà en Chip RAM (staging exclu du chronomètre). Aucun des deux chemins n'est le futur moteur Fast Icon natif non compressé. Le banc teste **4 plans (16 couleurs)**, alors que le prototype Fast Icon Unity AGA cible **8 plans (256 couleurs)**. Ne pas utiliser ces rapports pour choisir un backend AUTO CPU/Blitter.

## Suite

1. **Relevés réalisés :** AMOS interprété 68030/JIT ; interprété 68020 sans JIT ; compilé 68020 sans JIT ; **68030 50 MHz sans JIT compilé, même exécutable que le 68020 compilé**. Le dernier scénario **s'exécute et se ferme sans erreur visible**, mais il ne constitue pas une nouvelle qualification exhaustive Gate C de la bibliothèque.
2. **Diagnostic en lecture seule du code R60 effectué :** parcours RLE strict en deux passes sur l'image source, puis écriture CPU pixel par pixel et plan par plan, sans appel VBL ou WaitBlit explicite dans `Aga Image Region`. Le nouveau 68030 sans JIT descend à ~6,9 ms/appel, contre ~20 ms sur 68020 ; cela va à l'encontre de l'hypothèse d'une **attente fixe** de 20 ms par appel mais ne constitue pas une mesure isolant le coût de chaque opération.
3. **Mode du quatrième relevé confirmé compilé par l'auteur, sans recompilation du binaire 68020.** Le bandeau affichant l'ancien CPU est une **étiquette obsolète**. Pour une traçabilité vérifiable, documenter les réglages WinUAE effectifs ainsi que l'empreinte du programme compilé et de la Lib installée si possible ; les bandeaux locaux ne sont pas présents dans l'ASC GitHub. Pour une mesure plus fine, envisager un banc **distinct** sans modifier cette référence historique.
4. Réaliser ensuite le moteur Fast Icon natif et mesurer **CPU Fast→Chip contre Blitter Chip→Chip**, y compris le staging, les attentes et le résultat pixel par pixel en opaque/masqué. Garder M18 actif pour CBlock après les icônes.

**Dépôt :** R60 v0.13.5 LAST_GOOD non modifiée, 35 056 octets. Pas de R61, pas de nouvel ASC actif, pas de promotion. Gate D Amiga physique non testée.
