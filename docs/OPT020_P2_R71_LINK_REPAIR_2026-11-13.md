# OPT020/P2 R71 v0.13.16 - correction des branchements AP20

**13 novembre 2026, `main`.** Correctif du Guru R70 `$80000004`. L'existence du mauvais saut et son point de destination sont demontrables dans les binaires. La cause exacte de l'instruction illegalement executee n'a pas ete capturee.

## Preuve et correction minimale

La R70 agrandit l'entree native 55 (Image Draw) de 222 octets, mais conserve a tort les branchements `BRA.W` et `BSR.W` des entrees natives 20/57/58. Le monolithe Compiler V2 recalcule les adresses de ses *stubs publics* uniquement, pas ces destinations inter-routines.

| Appel | Source | Destination R70 fautive | Destination R71 |
| --- | ---: | ---: | ---: |
| Fill vers helper RasterPort | entree 20, offset 0 | 30128 | **30350**, entree 58 +110 |
| Bank Image Draw vers Image Draw | entree 57, offset 122 | 26280 | **26060**, debut entree 55 |
| Bank Font Select vers Font Bank Select | entree 58, offset 80 | 21310 | **21090**, debut entree 49 |

Les adresses sont des offsets dans le code natif du monolithe, sans le dispatcher V2 de 34 octets. `BRA.W`/`BSR.W` utilisent comme PC de base le **mot de deplacement** a `instruction+2` (pas `instruction+4`). Le defaut historique de deux octets des delegations est corrige **uniquement dans la candidate R71**, pas dans les constructeurs/archives historiques R54.

La candidate R71 conserve **51 460 octets**, 64 commandes, 71 entrees AP20. Seules les trois valeurs de deplacement relatif et le titre de version changent par rapport a R70. Toutes les autres entrees sont intactes, en particulier les entrees 55 P2 et 59 P1e.

- R68 `LAST_GOOD` : 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Protegee.
- R69 de reference : 51 240 octets, SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`. Gate B PASS (historique).
- R70 **echec** : SHA256 `fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad`. Conservee dans Git, non active.
- R71 candidate **Gate B interprétée PASS, non promue** : SHA256 `1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0`. Gate B PASS sur le scénario documenté ; Gate C et D en attente.

## Garde-fous permanents

1. `tools/native_relative_links.py` est un manifeste d'arcs de controle source-confirmes. Verifie opcode exact, emplacement du site, prologue cible, adresses absolues reelles et depassement signe 16 bits.
2. `relink_native_parts` recalcule les trois deplacements depuis les tailles finales des **70 entrees natives**, sans scanner heuristiquement les octets `60 00`/`61 00` (certains peuvent appartenir a des donnees).
3. `tools/test_opt020_p2_r71_links.py` exige que R70 echoue a la verification, R71 reussisse, que le relink soit idempotent et que chaque corruption volontaire d'un mot de deplacement soit detectee.
4. La construction `tools/build_opt020_p2_r71.py` est deterministe, en memoire uniquement, protegee par SHA256. Le builder R70 historique reste intact. `tools/active_library.py` rejette toujours explicitement la R70 fautive.
5. Les deux CI (integrite rapide et prototype OPT020) appellent les nouveaux tests. La regle de base pour toute future insertion est de **recalculer les references inter-entrees, puis de les verifier dans le binaire final**. Ne pas deduire un PASS runtime d'un PASS structurel.

### Limites

L'audit a aussi signale un retour `D3` incorrect apres echec tardif de la seconde passe P2. **Ce defaut secondaire n'est pas corrige dans R71** afin de conserver une correction de branchements minimale et octet-limitee ; il doit etre traite et teste dans un jalon distinct. Les tests ne couvrent pas tous les appels inter-entrees de la bibliotheque et ne constituent pas un parcours exhaustif du flot dans AMOS.

**Validation reelle requise :** installer l'unique `dist/AMOSPro_AGA.Lib` R71, relancer AMOS sous WinUAE AGA/68020 14 MHz/JIT OFF/PAL, executer uniquement `tests/current/OPT020_P2_R71_INTERPRETED_01.asc`, relever `RESULT 1`, `CLOSE RETURNED`, les visuels, l'absence de Guru et l'equivalence pixels R69. Ne pas lancer AMOS Compiler avant le jalon final prévu, malgré la Gate B désormais confirmée. Aucune promotion `LAST_GOOD` avant autorisation distincte.
