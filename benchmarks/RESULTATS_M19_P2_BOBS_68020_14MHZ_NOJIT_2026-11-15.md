# M19 P2 — Benchmark 4/8/16 Bobs, WinUAE MC68020 14 MHz / JIT OFF (15/11/2026)

**Statut : GATE B BENCHMARK PASS en AMOS Runtime/WinUAE MC68020 dans cette configuration.** L'auteur annonce le réglage **14 MHz, sans JIT**, confirmé par le nom du fichier transmis ; le journal prouve `CPU 68020`, mais **n'enregistre pas lui-même la fréquence CPU, JIT ni la configuration chipset**. Ne pas qualifier ce résultat comme un essai sur Amiga physique.

**Preuve brute :** `M19_P2_BENCH_BOBS_RUNTIME 68020 14Mhz noJIT.TXT` (74 lignes de mesures + fin de fichier), `TEST M19_P2_BENCH_BOBS_01`, `VERSION R84 V0.13.29 LAST_GOOD`, `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68020`, `CPU_ATTNFLAGS 3`. Source active [`tests/current/M19_P2_BENCH_BOBS_01.asc`](../tests/current/M19_P2_BENCH_BOBS_01.asc), **blob Git inchangé `4345d8728af1d6dba29a5936463219ac49b3b109`**. Bibliothèque R84 `LAST_GOOD` et API AP20 inchangées.

## 1. Bilan du journal

| Champ | Valeur |
|---|---:|
| `RESULT / VERDICT / ERR` | **1 / PASS / 0** |
| `CAP_OK / ICON_OK / OBJECTS_PREPARED` | 6 / 4 / 16 |
| `FRAME_OK` | **240 / 240** |
| `DRAW_OK` | **9 088** |
| `SORT_FAIL / FILL_FAIL / DRAW_FAIL / SWAP_FAIL` | **0 / 0 / 0 / 0** |
| `SAFE_RETRIES / SWAP_RETRIES` | **0 / 0** |
| `CHIP_BEFORE / CHIP_AFTER / CHIP_DELTA` | 1 842 552 / 1 842 552 / **0** |
| `FAST_BEFORE / FAST_AFTER / FAST_DELTA` | 138 377 000 / 138 377 000 / **0** |
| `CLOSE_RETURNED` | **1** |

Le calcul de `DRAW_OK` reste cohérent : 8 × 16 objets d'échauffement + 2 × (120 compositions + 40 frames présentées) × (4+8+16) objets = **9088**. Les **six séries de composition** enregistrent **0 retry Safe** et les six séquences de présentation **0 retry Swap**. Les variations mémoire sont nettes entre deux instants instrumentés ; elles ne mesurent pas les pics.

## 2. Ticks réellement mesurés

Les charges **4/8/16 Bobs** utilisent la même répartition source : 25 % AGAPIC masqués, 25 % AGAPIC opaques, 50 % FICON8 masqués. Sources créées avant la mesure ; aucun AMAL pendant ce benchmark. Chaque passage : **800 tris Z**, **120 effacements**, **120 compositions** (fond + tri + N dessins, *sans Swap*), puis **40 présentations** (VBL + composition + Swap).

| Charge | Passage | Tri /800 | Fond /120 | Composition /120 | Présentation /40 | Dessins composition | Retry Safe comp. | Retry Swap |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 4 Bobs | P0 | 162 | 188 | 360 | 160 | 480 | 0 | 0 |
| 4 Bobs | P1 | 163 | 188 | 361 | 160 | 480 | 0 | 0 |
| 8 Bobs | P0 | 604 | 188 | 578 | 202 | 960 | 0 | 0 |
| 8 Bobs | P1 | 604 | 188 | 577 | 201 | 960 | 0 | 0 |
| 16 Bobs | P0 | 2347 | 188 | 1137 | 401 | 1920 | 0 | 0 |
| 16 Bobs | P1 | 2347 | 188 | 1137 | 401 | 1920 | 0 | 0 |

Le `Timer` utilise **20 ms/tick en PAL nominal** dans le protocole, soit une résolution de 20 ms par **séquence complète** et non 20 ms par frame. Les moyennes ci-dessous sont indicatives : temps écoulé, **pas des cycles CPU mesurés**.

## 3. Temps moyens normalisés (deux passages)

| Charge | Tri : ms / appel | Fond : ms / appel | Composition : ms / frame | Présentation : ms / frame | Présentations / s (moyenne) |
|---:|---:|---:|---:|---:|---:|
| **4 Bobs** | **4,06** | **31,33** | **60,08** | **80,00** | **12,5** |
| **8 Bobs** | **15,10** | **31,33** | **96,25** | **100,75** | **9,9** |
| **16 Bobs** | **58,68** | **31,33** | **189,50** | **200,50** | **5,0** |

La colonne « présentations / s » vaut `1000 / (DISP_TICKS × 20 / 40)` ; elle **inclut VBL, dessin, Swap et synchronisation** et n'est pas une mesure de vitesse maximale de calcul ni une preuve d'affichage sans tearing.

## 4. Analyse et coût de la gestion

- **Tri Z BASIC :** augmente fortement avec le nombre d'objets : ~4,06 / 15,10 / 58,68 ms par appel pour 4/8/16. La procédure effectue un tri avec deux boucles imbriquées : la croissance est compatible avec un **coût quadratique**. **Le benchmark retrie chaque frame même quand Z ne change pas.**
- **Fond entier :** ~31,33 ms par `Aga Blit Fill(320,256)`, pratiquement constant. C'est **52 %** de la composition N4, mais seulement **16,5 %** à N16 ; le fond ne représente donc **pas le seul goulot** lorsque la charge monte.
- **Dessin :** estimation par différence de séquences indépendantes, `T_comp - T_fill - T_sort` ; cette différence inclut les boucles BASIC et appels graphiques mais ignore les effets de contexte entre phases. **Ce n'est pas une mesure directe du renderer**.

| Charge | Fond (ms/frame) | Tri (ms/frame) | Reste attribuable au dessin + orchestration (estimé) | Reste / Bob (estimé) |
|---:|---:|---:|---:|---:|
| 4 | 31,33 | 4,06 | 24,69 ms | 6,17 ms |
| 8 | 31,33 | 15,10 | 49,82 ms | 6,23 ms |
| 16 | 31,33 | 58,68 | 99,49 ms | 6,22 ms |

À **16 Bobs**, le tri seul représente environ **31 %** du temps de composition ; le fond **16,5 %** ; le reste calculé, environ **52,5 %**. Supprimer seulement le retri inutile pourrait **théoriquement** retirer ~58,7 ms du temps écoulé par composition, mais ce gain **n'est pas testé** et laisserait un temps de composition estimé d'environ **130,8 ms/frame** à N16 (sans garantir de FPS).

## 5. Comparaison avec le benchmark WinUAE 68030 / JIT activé

Le [journal complet 68030/JIT](RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md) est **PASS** lui aussi, mais le JIT et la configuration CPU sont différents. Les ratios ci-dessous mesurent seulement **le rapport entre temps écoulés dans deux configurations d'émulation différentes**, pas un gain processeur ou une accélération native certifiée.

| Charge | Composition 68030/JIT (ms/frame) | Composition 68020/14 MHz/JIT OFF (ms/frame) | Rapport des temps |
|---:|---:|---:|---:|
| 4 Bobs | 23,25 | 60,08 | **2,58×** |
| 8 Bobs | 23,42 | 96,25 | **4,11×** |
| 16 Bobs | 23,83 | 189,50 | **7,95×** |

Le 68030/JIT donnait un temps d'effacement ~23,2 ms, un tri BASIC quasi indétectable à 4/8 objets et une composition à peine sensible à N. Le nouveau relevé **montre que cette impression ne s'applique pas** au 68020/JIT OFF : coût BASIC et rendu pèsent lourd à N16. **Ne pas tirer de conclusions sur les performances physiques d'un 68030 à partir d'un JIT WinUAE**.

## 6. Recommandations techniques fondées sur les mesures

1. **Priorité 1 — Cache de l'ordre Z en AMOS BASIC.** Trier lors de création, destruction, visibilité ou changement de priorité seulement ; sinon conserver un tableau ordonné `ID`. Faire un A/B avec le même banc 4/8/16, mesurer composante tri et composition, sans nouvelle commande AP20.
2. **Priorité 2 — Séparer les formats de rendu dans un benchmark.** Mesurer `Aga F Icon`, `Aga Bank Image Draw` masqué et opaque indépendamment, car les 6,2 ms par Bob ci-dessus sont une **moyenne résiduelle d'un mélange**. Cela guidera une éventuelle optimisation native ciblée plutôt qu'un gestionnaire entier.
3. **Priorité 3 — Examiner la stratégie de fond et les écritures Chip.** Le fond complet coûte ~31 ms à chaque frame, mais toute alternative par zones sales doit rester sûre avec **deux buffers**, avec restauration correcte dans chacun, avant de promettre un gain.
4. **Aucune API native validée pour l'instant.** L'échantillon prouve le goulet sur 68020/JIT OFF ; une mesure A/B du cache Z permettra de décider si optimiser le BASIC suffit, puis d'identifier l'appel graphique restant le plus coûteux.

**Qualification :** Gate B de ce benchmark **PASS sous WinUAE Runtime/68020**, configuration 14 MHz JIT OFF fournie par l'auteur. `PRG_STATE 0`, AMOS Compiler M19 et Amiga AGA réel **non testés**. Aucun dessin en interruption, aucun nouveau token AP20, et le binaire `LAST_GOOD` reste inchangé.

[Protocole du banc](README_M19_P2_BOBS_4_8_16.md) · [Roadmap M19](../docs/ROADMAP.md) · [Source active](../tests/current/M19_P2_BENCH_BOBS_01.asc) · [Ancien essai interrompu 68030](RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md)
