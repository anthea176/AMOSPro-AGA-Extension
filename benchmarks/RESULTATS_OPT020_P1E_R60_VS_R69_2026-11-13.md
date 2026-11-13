# OPT020/P1e — benchmark R60/R68 vs R69 sous WinUAE (13/11/2026)

**Résultat : R69 OPT020/P1e plus rapide en dessin natif 68020, jusqu'à 3,32× sur les dix cas mesurés.** Les deux passages sont **AMOS interprété**, 68020 à 14 MHz, **JIT OFF**, PAL 50 Hz, 128 Mo de Fast RAM Z3 indiqués sur les captures auteur. Aucun résultat AMOS Compiler réel et aucun résultat matériel physique. La candidate R69 **n'est pas promue**.

## Protocole et provenance

- **Programme identique** dans les deux passages : [`opt020_p1e_r60_vs_r69.asc`](opt020_p1e_r60_vs_r69.asc), [protocole](README_OPT020_P1E_R60_VS_R69.md), banque `M16_AGAPIC_SAMPLE_BANK10.abk` de 64×40×4, écran AGA 320×256×16.
- **Référence R60** : R68 v0.13.13 `LAST_GOOD`, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, dont `Aga Image Region` contient exactement le peintre R60 68000 (2 012 octets).
- **Candidate R69** : v0.13.14 `dist/AMOSPro_AGA.Lib`, SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`, peintre 68020 (2 174 octets). Les 69 autres unités natives sont identiques : [contrôle statique en CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43503814027).
- **Deux captures** fournies dans la conversation le 13/11/2026 : `image(20261113-204754).png` (R60/R68) et `image(20261113-205150).png` (R69). L'auteur confirme explicitement que **les deux sont interprétées**. Les légendes des captures indiquent la même configuration 68020/14 MHz, JIT OFF, 128 Mo Fast Z3 ; aucun export `.uae` ne vient vérifier ces réglages indépendamment.
- **Méthode** : trois essais de **240 appels** par géométrie, `Timer` PAL **1 tick ≈ 20 ms**. Échauffement avant chaque groupe, aucun Swap/Wait Vbl/Print dans les boucles ; le temps inclut **interpréteur AMOS, API AP20, banque/RLE/Safe, peintre et contrôle des retours**, pas uniquement le noyau BFINS.

## Résultats bruts et médianes

Les triplets sont les trois mesures en **ticks** lues sur chaque capture. Durée par appel = médiane des ticks × 20 / 240 = médiane / 12 en ms. Accélération = médiane R60/R68 ÷ médiane R69 ; au-dessus de 1, R69 est plus rapide.

| Cas | R60/R68 : 3 essais | Médiane R60 | R69 : 3 essais | Médiane R69 | R60 ms/appel | R69 ms/appel | Accélération | Temps réduit |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `OFF16` | 38 / 38 / 39 | 38 | 38 / 38 / 40 | 38 | 3,167 | 3,167 | 1,00× | 0,0 % |
| `ONEPX` | 83 / 83 / 82 | 83 | 81 / 80 / 81 | 81 | 6,917 | 6,750 | 1,02× | 2,4 % |
| `OPA16` | 236 / 236 / 235 | 236 | 109 / 109 / 110 | 109 | 19,667 | 9,083 | **2,17×** | **53,8 %** |
| `MSK16` | 234 / 233 / 234 | 234 | 109 / 110 / 108 | 109 | 19,500 | 9,083 | **2,15×** | **53,4 %** |
| `OPA+1` | 235 / 236 / 236 | 236 | 109 / 109 / 110 | 109 | 19,667 | 9,083 | **2,17×** | **53,8 %** |
| `MSK+1` | 233 / 233 / 234 | 233 | 109 / 109 / 109 | 109 | 19,417 | 9,083 | **2,14×** | **53,2 %** |
| `CLIP17` | 183 / 184 / 188 | 184 | 101 / 102 / 101 | 101 | 15,333 | 8,417 | **1,82×** | **45,1 %** |
| `OPA32` | 392 / 392 / 397 | 392 | 118 / 118 / 118 | 118 | 32,667 | 9,833 | **3,32×** | **69,9 %** |
| `MSK32` | 396 / 407 / 391 | 396 | 122 / 120 / 122 | 122 | 33,000 | 10,167 | **3,25×** | **69,2 %** |
| `FRG17` | 240 / 239 / 240 | 240 | 169 / 169 / 169 | 169 | 20,000 | 14,083 | **1,42×** | **29,6 %** |

## Fonctionnement / mémoire

| Contrôle console | R60/R68 | R69 |
|---|---|---|
| CPU / horloge / mémoire indiqués | 68020 / 14 MHz / Fast Z3 128 Mo | Identique |
| JIT | OFF | OFF |
| Exécution AMOS | Interprété (confirmé auteur) | Interprété (confirmé auteur) |
| `ERR` | **0** | **0** |
| `CLOSE` | **-1** | **-1** |
| `RESULT` | **1** | **1** |
| `CHIP BEFORE/END` | **1 801 352 / 1 801 352** | **1 801 376 / 1 801 376** |
| Fin de programme | **`BENCH FINISHED - CLOSE RETURNED`** | **`BENCH FINISHED - CLOSE RETURNED`** |

Aucune perte de Chip RAM n'est observée **au sein de chaque passage**. Les 24 octets de différence du niveau de mémoire libre **entre** les sessions ne signalent pas une fuite : seules les égalités avant/après dans une même session peuvent servir à ce contrôle. Aucun plantage visible sur les captures.

Le contrôle `ERR 0` vérifie **les 240 valeurs de retour de chacun des 3 essais**, contrairement aux benchmarks qui ne contrôlent que le dernier appel. Il ne compare cependant **pas pixel par pixel** le framebuffer au modèle de référence.

## Interprétation technique

1. **Validation hors écran (`OFF16`) : 38 → 38 ticks**. Les frais des contrôles banque/format/RLE restent pratiquement inchangés. Le cas `ONEPX` gagne 2 ticks sur 240 appels, écart trop faible pour affirmer une accélération robuste.
2. **Groupes complets 16×16 : ~2,14–2,17×** en opaque/masqué, aligné ou X+1. La réduction de durée est d'environ **53–54 %**. Le décalage X+1 n'entraîne pas de pénalité visible dans cette série.
3. **32×20 : 3,32× opaque et 3,25× masqué**, soit **69–70 % de temps en moins**. Le coût de la prévalidation, commun aux deux, rend ce gain d'autant plus significatif pour les rectangles volumineux du scénario.
4. **Clipping et fragment 17 px : 1,82× et 1,42×**. Ces chemins gagnent également, mais les fragments non multiples de 16 conservent un coût relativement élevé ; la présente mesure ne suffit pas à en attribuer précisément l'origine.
5. **Masque significatif, contrairement au précédent R60 :** d'après [`tools/m16_agapic_sample.py`](../tools/m16_agapic_sample.py), sur la région source **(24,12) 16×16, 235/256 pixels (91,80 %) sont conservés** ; sur **(16,8) 32×20, 580/640 pixels (90,63 %) sont conservés**. Le cas historique R60 `MASK16` sur (0,0) ne conservait que 1 pixel sur 256, biais désormais évité.

**Ces résultats mesurent bien un avantage end-to-end reproductible à trois essais sur une configuration WinUAE donnée, en mode interprété.** Ils ne prouvent pas un gain universel, n'isolent pas les cycles natifs du noyau, ne qualifient pas les autres CPU/modes d'exécution, et ne remplacent pas une vérification pixel exacte de tous les rendus.

## État de la P1e

- **Gate A CPU et CI : PASS** ; test P1e 321 cas et [CI intégrité du benchmark PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43503814027).
- **Gate B WinUAE interprétée : PASS** sur [le test graphique R69](../docs/OPT020_P1E_R69_WINUAE_GATE_B_2026-11-13.md), et maintenant **benchmark comparatif R60/R69 JIT OFF PASS**.
- **Gate C AMOS Compiler réel : NON TESTÉE** ; maintenir la règle d'un unique essai final, sans compilation exploratoire intermédiaire.
- **Gate D Amiga physique : NON TESTÉE**.
- **R68 `LAST_GOOD` protégée et R69 candidate active inchangées**, un ASC actif unique dans `tests/current/` ; aucune promotion de R69.

**Décision possible après ce résultat :** P1e R69 peut rester la candidate fonctionnelle et performante à geler avant l'unique Gate C Compiler. Ne pas la promouvoir tant que les validations restantes et l'accord auteur ne sont pas obtenus.
