# AMOS Compiler Gate C — plantage R45 à la fermeture, risque hérité de R44

**Date : 12/11/2026.** **Gate C en échec sur la R45 installée (déclaration utilisateur)** ; `Aga Screen Open` retourne `1`, puis `Aga Screen Close` provoque un Guru `80000004`. R44 est la source de la routine de fermeture incriminée, **mais sa Gate C n'a pas été testée dans les captures**. R44 a Gates A/B PASS en interprété ; R45 est toujours en cours (Gate A native PASS, rendu Image Draw WinUAE non validé). Gate D physique non testée. Voir la [candidate R44 relogeable et sa méthode de transposition R45](GATE_C_R44_R45_PORTABLE_FIX.md).

## Observations vérifiées

- Benchmark AMOS/AMCAF/AGA 320x256x32 : exécution interprétée OK, mais exécutable compilé -> `Software Failure 80000004` (exception CPU 4).
- Un programme AMOS Compiler sans extension, limité à `Print` et `Wait`, fonctionne (message `ETAPE 2 - OK`).
- Le test compilé minimal affiche `ETAPE 1 - AVANT OPEN` puis provoque `80000004` ; il contient à la suite `Aga Screen Open`, `Wait` et `Aga Screen Close` **sans message intermédiaire** : **il ne prouve pas encore si Open ou Close plante**.
- **La trace à six étapes a maintenant été exécutée en compilé sur R45** : `02 AGA PROBE RETURNED`, **`04 OPEN RETURNED 1`**, `05 BEFORE AGA SCREEN CLOSE`, puis Guru `80000004`, **sans `06`**. Le défaut est donc localisé dans la fermeture ou son retour.
- Un précédent essai avec `Wait Key` a donné `HALT3` avant l'ouverture : symptôme distinct, évité dans cette nouvelle recette.
- Les dumps à `PC=$00F81472` (`STOP #$2000`) sont dans Kickstart après le Guru, pas à l'adresse fautive ; `tx` exécuté après l'arrêt a intercepté une interruption de niveau 2 (`Exception 26`).

## Anomalie structurelle confirmée : branches non relogeables

Le compilateur AMOS 365 [`+APComp.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s) **charge et recopie les routines d'extension séparément** (chemins `Lib_Load` et `Ll_LoadReloc`). Les sauts inter-routines demandent les conventions de relocation du compilateur, qui ne sont pas équivalentes à un `BSR.w` brut calculé sur la disposition complète du fichier AP20.

Lecture **statique du binaire R44 LAST_GOOD intact**, 27 460 octets, avec sa table des segments :

| Code R44 | Position locale | Branche brute | Cible en bibliothèque complète |
|---|---:|---|---|
| Segment 0, init/reset/cleanup | 398 | `61 00 63 CE` (`BSR.w +25550`) | Segment 54, code `$655E` |
| Segment 8, `Aga Screen Close` | 276 | `61 00 5C 70` (`BSR.w +23664`) | Segment 54, code `$655E` |
| Segment 17, cleanup auxiliaire | 204 | `61 00 49 24` (`BSR.w +18724`) | Segment 54, code `$655E` |
| Segment 18, cleanup auxiliaire | 204 | `61 00 46 78` (`BSR.w +18040`) | Segment 54, code `$655E` |

Le [builder R44](../tools/build_m15bis_cursor_r44.py) calcule `delta = target - (at + 2)` en supposant cette proximité. **Elle n'est pas garantie dans le programme compilé.** D'autres appels directs plus anciens existent entre les segments 8 -> 48 et 17/18 -> 33 ; leur relocation devra aussi être auditée. Les `BSR.w` du segment 6 (`Aga Screen Open`) observés dans le fichier entier pointent en revanche à l'intérieur du segment 6.

**Le risque structurel est démontré, mais le PC exact du crash observé n'a pas encore été capturé.**

## Test de localisation compilé à exécuter

Source : [`tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc`](../tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc).

Import dans **un programme vide AMOS**, via **Project -> Merge ASCII**, puis **compiler et lancer** sous WinUAE avec la R44 actuelle. Aucune extension ni configuration à modifier. Les pauses sont automatiques avec `Wait` (pas de `Wait Key`). La commande `Aga Probe` à zéro paramètre évite l'ambiguïté de nom `Aga Detect` également présent dans AMCAF.

| Dernier repère visible | Signification |
|---|---|
| `01 BEFORE AGA PROBE` | Avant le premier appel de notre extension |
| `02 AGA PROBE RETURNED` | Dispatch de la commande sans paramètre effectué |
| `03 BEFORE AGA SCREEN OPEN` | L'appel d'ouverture est le suivant |
| `04 OPEN RETURNED <valeur>` | Open a rendu la main ; pause **avant tout Close** |
| `05 BEFORE AGA SCREEN CLOSE` | Le prochain appel est Close ; pause avant son exécution |
| `06 AFTER AGA SCREEN CLOSE` | Open et Close sont revenus correctement |

Un Guru après `03` sans `04` implique le chemin Open ou son retour ABI ; après `05` sans `06` implique Close/cleanup et renforce l'hypothèse des appels inter-segments. Un écran noir seul n'est pas une preuve de crash car l'écran privé Intuition peut recouvrir l'écran AMOS.

## Suite

**La trace confirme Close, pas Open.** Une [candidate R44 expérimentale](GATE_C_R44_R45_PORTABLE_FIX.md) a été préparée avec des marqueurs `Rbsr` et deux routines internes ajoutées. Le même générateur effectue une transposition **en mémoire** sur la R45 de référence, sans modifier R45 ni `LAST_GOOD`. **Gate C ne sera considérée PASS qu'après exécution du binaire corrigé sous AMOS Compiler/WinUAE**, puis régressions. D'autres branches historiques inter-routines restent à examiner.

Références : [règles ABI](../EXTENSION_SOURCE_RULES.md) · [compiler 365](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s) · [builder R44](../tools/build_m15bis_cursor_r44.py).
