# OPT020/P1e — R60/R68 vs R69, benchmark AMOS compilé (13/11/2026)

**Validation utilisateur : les deux programmes ont été réellement recompilés et exécutés sous WinUAE, avec `ERR 0` et `RESULT 1`.** Les captures montrent 68020 à 14 MHz, JIT désactivé, PAL, 128 Mo Fast Z3 (indiqués dans le programme). Le même benchmark est utilisé pour R60/R68 et R69 ; trois essais de 240 appels par scénario. **Ceci prouve la Gate C de ce benchmark `Aga Image Region`, pas celle de toutes les commandes de la bibliothèque.**

Captures source dans la conversation : `image(20261113-205815).png` (R60/R68 compilé) et `image(20261113-205932).png` (R69 compilé). Les PNG ne sont pas intégrés au dépôt. [Source et protocole](opt020_p1e_r60_vs_r69.asc) · [résultats interprétés distincts](RESULTATS_OPT020_P1E_R60_VS_R69_2026-11-13.md).

**Méthode :** médiane de trois mesures en ticks PAL, un tick = environ 20 ms ; durée par appel = médiane/12 ms ; accélération = médiane R60 ÷ médiane R69.

| Cas | R60/R68 compilé : A/B/C ticks | Médiane | R69 compilé : A/B/C ticks | Médiane | R60 ms/appel | R69 ms/appel | Accélération | Réduction |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `OFF16` | 36 / 36 / 37 | 36 | 37 / 37 / 38 | 37 | 3,000 | 3,083 | 0,97× | −2,8 % |
| `ONEPX` | 80 / 81 / 80 | 80 | 78 / 79 / 79 | 79 | 6,667 | 6,583 | 1,01× | 1,3 % |
| `OPA16` | 234 / 234 / 234 | 234 | 107 / 107 / 108 | 107 | 19,500 | 8,917 | **2,19×** | 54,3 % |
| `MSK16` | 232 / 231 / 232 | 232 | 107 / 108 / 106 | 107 | 19,333 | 8,917 | **2,17×** | 53,9 % |
| `OPA+1` | 233 / 234 / 234 | 234 | 107 / 107 / 107 | 107 | 19,500 | 8,917 | **2,19×** | 54,3 % |
| `MSK+1` | 231 / 237 / 239 | 237 | 107 / 107 / 107 | 107 | 19,750 | 8,917 | **2,21×** | 54,9 % |
| `CLIP17` | 180 / 182 / 181 | 181 | 99 / 99 / 99 | 99 | 15,083 | 8,250 | **1,83×** | 45,3 % |
| `OPA32` | 390 / 390 / 391 | 390 | 115 / 117 / 115 | 115 | 32,500 | 9,583 | **3,39×** | 70,5 % |
| `MSK32` | 382 / 382 / 382 | 382 | 119 / 119 / 120 | 119 | 31,833 | 9,917 | **3,21×** | 68,8 % |
| `FRG17` | 237 / 238 / 236 | 237 | 107 / 107 / 107 | 107 | 19,750 | 8,917 | **2,21×** | 54,9 % |

## Contrôle d'intégrité

| Vérification | R60/R68 | R69 |
|---|---|---|
| Mode | **Compilé** (confirmé utilisateur) | **Compilé** (confirmé utilisateur) |
| CPU/horloge/JIT | 68020 / 14 MHz / OFF | Identique |
| `ERR`, `CLOSE`, `RESULT` | `0 / -1 / 1` | `0 / -1 / 1` |
| `CHIP BEFORE/END` | `1845928 / 1845928` | `1845920 / 1845920` |
| Fin | `BENCH FINISHED - CLOSE RETURNED` | Idem |

Les différences de mémoire libre **entre** sessions (8 octets) ne sont pas un indice de fuite : le niveau initial est retrouvé **dans** chaque exécution. Le nombre de ticks `OFF16` est voisin : les contrôles restent comparables. Les gains marqués apparaissent quand le peintre travaille réellement. **`FRG17` est nettement plus rapide en compilé que lors du passage interprété R69 (107 contre 169 ticks) ; cet écart mérite un contrôle de répétabilité, pas une explication CPU inventée.**

**État :** P1e R69 Gate A CPU/CI PASS ; Gate B WinUAE interprété PASS ; **benchmark WinUAE compilé de `Aga Image Region` PASS**. **Gate C intégrée de la bibliothèque complète non établie par ce seul benchmark**, Gate D matériel non testée. R69 reste la candidate active ; R68 `LAST_GOOD` demeure protégée. Aucun Compiler lancé par l'assistant ; les deux compilations ont été effectuées par l'auteur.
