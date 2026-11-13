# M18/R60 — résultats WinUAE Cache Cost v2 (13 novembre 2026)

**Programme :** [m18_r60_cache_cost_v2.asc](m18_r60_cache_cost_v2.asc) · **[protocole](README_M18_CACHE_COST_V2.md)** · **R60 v0.13.5 LAST_GOOD inchangée**.

**Preuves : quatre captures transmises par l'auteur le 13/11/2026. Tous les essais sont explicitement confirmés en mode AMOS Compiler.** Les étiquettes rouges manuscrites identifient les quatre configurations WinUAE. Ce sont des mesures **observées dans l'émulateur**, pas des résultats sur Amiga physique ni une validation de Fast Icons natifs.

## 1. Conditions et résultats bruts

- **Affichage :** PAL 320×256×16 couleurs, 4 bitplanes ; banque AGAPIC 64×40×4, masque indépendant, chargée comme banque AMOS 10.
- **Chronomètre :** AMOS Timer, **1 tick = 20 ms**, **3 essais** par cas ; aucun Wait Vbl ni Swap dans les boucles chronométrées.
- **Volumes :** OFF, 1PIX, CPU16, MASK16 = **240 appels** chacun. BLIT seul = **2 400 copies**. CACHE1, CACHE4 et CACHE16 = **240 copies chacune**, avec respectivement **240, 60 et 15 décodages/stagings AGAPIC** comptabilisés.
- **Exécution :** toutes les captures sont en **compilé**. La configuration précise cycle-exact et les fréquences effectivement appliquées par WinUAE ne sont pas corroborées par export de configuration. La version exacte du programme compilé et l'empreinte de la Lib chargée ne sont pas vérifiables par les captures.

| Ligne (ticks / trois essais) | 68020 14 MHz, sans JIT | 68030 50 MHz, sans JIT | 68040 50 MHz, sans JIT | 68030 avec JIT |
|---|---:|---:|---:|---:|
| **OFF** | 37 / 36 / 36 | 10 / 11 / 11 | 6 / 6 / 6 | 0 / 0 / 0 |
| **1PIX** | 81 / 81 / 82 | 23 / 24 / 23 | 15 / 15 / 15 | 0 / 0 / 0 |
| **CPU16** | 236 / 236 / 236 | 81 / 80 / 80 | 64 / 64 / 64 | 0 / 1 / 1 |
| **MASK16** | 156 / 157 / 156 | 46 / 46 / 46 | 33 / 33 / 33 | 0 / 0 / 0 |
| **BLIT** | 33 / 32 / 32 | 20 / 20 / 20 | 18 / 18 / 18 | 16 / 16 / 15 |
| **CACHE1** | 239 / 239 / 239 | 82 / 82 / 83 | 65 / 65 / 65 | 1 / 1 / 2 |
| **CACHE4** | 62 / 62 / 62 | 22 / 22 / 22 | 18 / 18 / 18 | 2 / 2 / 1 |
| **CACHE16** | 18 / 18 / 18 | 7 / 7 / 7 | 6 / 6 / 6 | 1 / 1 / 2 |

**Résultat de fin :** les quatre captures affichent ERR 0, CLOSE -1 et BENCH FINISHED - CLOSE RETURNED, sans crash visible. Chip Free **avant et après identique** sur chaque passage :

| Profil | Chip Free avant | Chip Free après |
|---|---:|---:|
| 68020 14 MHz sans JIT | 1 909 320 | 1 909 320 |
| 68030 50 MHz sans JIT | 1 909 320 | 1 909 320 |
| 68040 50 MHz sans JIT | 1 906 248 | 1 906 248 |
| 68030 JIT | 1 893 472 | 1 893 472 |

La différence de mémoire libre **entre** configurations n'est pas une fuite ; le contrôle porte uniquement sur l'égalité avant/après **à l'intérieur d'un passage**. ERR 0 vérifie essentiellement les derniers retours de chaque série, pas chaque pixel ni chaque opération.

## 2. Médianes normalisées (hors JIT)

**Formule :** durée moyenne par opération = médiane des ticks × 20 ms / nombre d'appels du cas. Pour les CACHE, le dénominateur est **240 copies**, le staging AGAPIC étant compris dans le temps total.

| Opération | 68020 14 MHz (ms) | 68030 50 MHz (ms) | 68040 50 MHz (ms) |
|---|---:|---:|---:|
| OFF : vérification / première passe | 3,000 | 0,917 | 0,500 |
| 1PIX : une écriture visible | 6,750 | 1,917 | 1,250 |
| CPU16 : AGAPIC opaque 16×16 | **19,667** | **6,667** | **5,333** |
| MASK16 : AGAPIC masqué 16×16* | 13,000 | 3,833 | 2,750 |
| BLIT : copie seule, source déjà en Chip | **0,267** | **0,167** | **0,150** |
| CACHE1 : staging puis 1 copie | 19,917 | 6,833 | 5,417 |
| CACHE4 : staging amorti sur 4 copies | **5,167** | **1,833** | **1,500** |
| CACHE16 : staging amorti sur 16 copies | **1,500** | **0,583** | **0,500** |

*Voir l'avertissement sur la couverture très faible du masque ci-dessous.*

### Amortissement du staging AGAPIC confirmé par les mesures

Sur **240 copies**, le temps total attendu à partir des deux primitives mesurées est approximativement :

- **S** = ticks de CPU16 pour 240 stagings AGAPIC ;
- **B** = ticks de BLIT pour 240 copies = ticks de BLIT / 10 ;
- **CACHE avec n utilisations** ≈ **S/n + B** ticks (240/n stagings, 240 copies).

| Profil | CACHE1 prévu / observé | CACHE4 prévu / observé | CACHE16 prévu / observé |
|---|---|---|---|
| 68020 sans JIT | 239,2 / **239** | 62,2 / **62** | 17,95 / **18** |
| 68030 sans JIT | 82 / **82** | 22 / **22** | 7 / **7** |
| 68040 sans JIT | 65,8 / **65** | 17,8 / **18** | 5,8 / **6** |

La très bonne concordance entre ce modèle additif et les valeurs observées signifie que **le coût de préparation AGAPIC domine** et qu'il s'amortit avec la réutilisation des pixels déjà en Chip RAM. Elle ne constitue pas une mesure des coûts de staging d'un format Fast Icon natif.

| Profil sans JIT | Gain CACHE4 vs dessin CPU16 | Gain CACHE16 vs dessin CPU16 |
|---|---:|---:|
| 68020 14 MHz | **3,81×** | **13,11×** |
| 68030 50 MHz | **3,64×** | **11,43×** |
| 68040 50 MHz | **3,56×** | **10,67×** |

**CACHE1** est légèrement plus lent que CPU16 (un staging identique + une copie supplémentaire). Avec ce modèle et ces primitives, **deux utilisations devraient déjà rendre le staging rentable**, mais ce seuil **n'a pas été testé directement** : seules les réutilisations **1, 4 et 16** ont été mesurées. L'optimisation et le seuil ne sont pas transférables automatiquement aux futurs Fast Icons 256 couleurs.

## 3. Piège de la mesure MASK16 — un seul pixel opaque !

Le [générateur du sample AGAPIC](../tools/m16_agapic_sample.py) définit le masque par un cercle centré en (32,20), rayon 18, moins les pixels pour lesquels (x+2*y) est multiple de 13. Or l'ASC v2 mesure toujours la région source **SrcX=0, SrcY=0, largeur=16, hauteur=16**.

Dans ce carré source (0..15,0..15), **un seul pixel a son masque à 1 : (15,15)**. La couverture est **1/256 = 0,39 %** ; les **255 autres pixels sont ignorés** en mode masqué.

Cela explique une partie importante du fait que **MASK16** est plus rapide que CPU16 sur les trois profils sans JIT. Cela ne prouve **absolument pas** qu'une icône masquée normale est plus rapide qu'une opaque ! Un futur test de masquage devra couvrir des densités réalistes, par exemple avec une région source plus centrale, et vérifier le résultat pixel par pixel.

## 4. Cas 68030 avec JIT : mesure temporelle trop quantifiée

Les séries CPU sur 240 appels donnent seulement **0, 1 ou 2 ticks** (0–40 ms pour la série entière). **Zéro tick signifie une durée inférieure à la résolution de Timer, pas un calcul gratuit.** Par conséquent, ratios et coûts unitaires CPU/CACHE obtenus sous JIT ne sont **pas suffisamment précis** pour décider de l'architecture ; les valeurs brutes sont conservées en section 1. Le temps BLIT seul, sur 2 400 appels, est de **16 ticks médians**, mais il ne suffit pas à corriger la résolution des autres cas.

## 5. Ce que le benchmark valide — et ce qu'il ne valide pas

**Constat sur R60 :** pour une petite image **opaque, pré-stagée en Chip**, la copie Blitter est très rapide face à un décodage/dessin AGAPIC par le CPU. L'amortissement sur 4 ou 16 affichages est mesuré et cohérent. Ces captures constituent un **PASS des scénarios compilés du benchmark** sur quatre profils WinUAE, **pas** une nouvelle Gate C exhaustive de R60 et **pas** une Gate D matérielle.

**Limites bloquantes pour choisir le moteur Fast Icon :**

- R60 CPU = lecture RLE AGAPIC + contrôle complet de la banque + parcours 2 passes + écriture pixel/plan ; R60 Blitter = copie opaque Chip → Chip d'une image déjà préparée. **Les chemins ne sont pas fonctionnellement/économiquement identiques.**
- La mesure est en **4 plans (16 couleurs)**, pas en 8 plans (256 couleurs).
- Aucun transfert réel **Fast → Chip d'une icône pré-décodée** n'est chronométré.
- **Aga Blit Copy est opaque** : pas d'équivalence au mode avec masque indépendant, pas de Blitter masqué.
- La source du cache est placée dans le **back buffer utilisé pour le dessin**, sans aucun Swap dans les boucles. Un atlas Chip persistant et sûr vis-à-vis du double buffer n'est pas testé.
- L'empreinte de l'exécutable et les réglages WinUAE ne sont pas joints aux captures ; ne pas attribuer un comportement matériel réel au seul nom d'un CPU émulé.

**Suite conseillée :** travailler d'abord sur le vrai format M18 Fast Icon planaire 8 plans et sur son stockage (Fast et cache Chip) ; définir la transparence et la gestion du double buffer ; comparer enfin à rendu identique le **CPU Fast→Chip** et le **Blitter après staging Fast→Chip**, durée de staging incluse. Pour le masque, prévoir une image de test avec transparence représentative et un contrôle visuel/pixel. **Ne pas modifier R60 LAST_GOOD sur la base de ces seules mesures.**
