# OPT020/P1e — comparaison R60 / R69, WinUAE JIT OFF

**Statut : exécuté le 13/11/2026 sous WinUAE, AMOS interprété pour LES DEUX passages, 68020 14 MHz, JIT OFF, 128 Mo Fast Z3 (légendes utilisateur). Résultat fonctionnel PASS et accélération mesurée pour R69. [Rapport complet et données brutes](RESULTATS_OPT020_P1E_R60_VS_R69_2026-11-13.md).** Gate C AMOS Compiler non lancée.

[Source ASCII unique du benchmark](opt020_p1e_r60_vs_r69.asc). Elle se trouve dans `benchmarks/` (et **non** dans `tests/current/`), qui conserve son unique programme actif Gate B. Ce fichier n'est pas une seconde candidate. Le protocole reprend le chronometrage `Timer` du [bench R60 valide](m18_r60_cache_cost_v2.asc), en evitant son biais du masque a 1 pixel sur 256.

## Comparaison strictement a bibliotheque changee

| Passage | Bibliotheque installee dans le slot AGA d'AMOS | Taille | SHA256 |
|---|---|---:|---|
| **A : baseline R60** | Copier **sans modifier la source** `dist/AMOSPro_AGA_LAST_GOOD.Lib` R68 v0.13.13 sous le nom `AMOSPro_AGA.Lib` dans `APSystem` **de WinUAE uniquement** | 51 064 o | `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed` |
| **B : OPT020 R69** | Installer `dist/AMOSPro_AGA.Lib` R69 v0.13.14 dans le **meme slot** d'`APSystem` | 51 240 o | `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298` |

La R68 promue contient le **meme code natif 68000 de `Aga Image Region` que R60** (2 012 octets). La R69 conserve ce contrat, remplace uniquement le peintre natif de l'entree AP20 59 (2 174 octets) et garde les 69 autres noyaux identiques. Cette identite est reverifiee dans `tools/test_opt020_p1e_benchmark_static.py`.

**Ne jamais copier/renommer le fichier du depot `dist/AMOSPro_AGA_LAST_GOOD.Lib` : il est protege.** L'installation A se fait par une **copie** dans l'environnement WinUAE, sans commit ni remplacement de `dist/AMOSPro_AGA.Lib` sur GitHub. Redemarrer AMOS entre A et B : le chargement de l'extension est persistant.

## Configuration et execution

1. Sauvegarder la configuration WinUAE. Selectionner **AGA + 68020 a 14 MHz + PAL 50 Hz + JIT OFF**, avec la **meme** Chip/Fast RAM et les memes reglages CPU dans les deux passages. Les chiffres des anciens benchmarks compiles, avec d'autres CPU ou JIT, ne sont **pas** comparables a cette serie. Un second double passage sur **68030 JIT OFF** est facultatif, apres le 68020.
2. Placer `benchmarks/opt020_p1e_r60_vs_r69.asc` et `tests/current/M16_AGAPIC_SAMPLE_BANK10.abk` dans un repertoire accessible a AMOS. **Attention : `Load` ecrase la banque AMOS 10.** Utiliser une session de test jetable.
3. Installer la version **A** dans le slot existant (normalement 14) et **redemarrer AMOS**. Ouvrir un programme **vide** puis **Project → Merge ASCII**. Executer **en interprete exclusivement**. **NE PAS lancer AMOS Compiler**.
4. Photographier la **console complete** et consigner le CPU, sa frequence, JIT et RAM des reglages WinUAE. Noter explicitement **A = R68/R60**.
5. Installer la version **B** dans le **meme** slot, relancer AMOS, repartir d'un programme vide, importer **exactement le meme ASC** et executer en interprete. Relever les memes informations. Noter **B = R69/P1e**.

Le programme ouvre un ecran prive AGA **320x256x16 (4 bitplanes)**, charge la meme banque **AGAPIC 64x40x4**, effectue un `Swap` et attend que le **back buffer inactif** soit `Safe`. Ensuite il execute **trois essais par cas**, **240 appels** par essai. Le code ne contient **ni `Swap`, ni `Wait Vbl`, ni impression** dans les boucles chronometrees. Un appel d'echauffement non mesure precede chaque cas.

Chaque essai additionne les **240 valeurs de retour** ; toute valeur differente de 1 est detectee (contrairement au test historique qui controlait seulement le dernier appel). Les temps incluent l'interpretation AMOS, le wrapper AP20, la validation banque/RLE, `Safe`, le peintre et l'addition de controle commune ; **ce ne sont pas des temps de noyau 68020 pur**.

## Les dix cas

| Console | Rectangle source / mode | Destination et objectif |
|---|---|---|
| `OFF16` | 16x16 opaque, source (24,12) | x=320, totalement hors ecran ; mesure les validations sans ecriture |
| `ONEPX` | 1x1 opaque, source (32,20) | 1 pixel visible ; mesure le cout d'appel et du RLE |
| `OPA16` | 16x16 opaque, source (24,12) | x=160, **aligne 16 pixels** |
| `MSK16` | 16x16 masque independant, source (24,12) | x=160, masque central dense |
| `OPA+1` | 16x16 opaque, source (24,12) | x=161, **decalage 1 pixel** |
| `MSK+1` | 16x16 masque independant, source (24,12) | x=161, decalage 1 pixel |
| `CLIP17` | 17x16 masque, source (23,12) | x=313, clipping droit, 7 pixels visibles |
| `OPA32` | 32x20 opaque, source (16,8) | x=160, deux groupes 16 px |
| `MSK32` | 32x20 masque, source (16,8) | x=161, plusieurs groupes et fragments |
| `FRG17` | 17x16 masque, source (23,12) | x=163, largeur non multiple de 16, sans clipping ecran |

La source centrale utilise le masque du disque autour de (32,20), et non (0,0) : contrairement au vieux `MASK16` R60 (1 pixel visible sur 256), les tests masques exercent une part importante des pixels.

## Interpretation, resultat attendu et prochain jalon

Le programme a affiché **trois nombres de ticks pour chaque ligne**, toujours en ordre essais 1/2/3 ; les valeurs observées et leurs médianes figurent dans le [rapport](RESULTATS_OPT020_P1E_R60_VS_R69_2026-11-13.md). Sous PAL, **1 tick AMOS `Timer` ~= 20 ms**. Comparer uniquement les **medians** de chaque triplet, puis :

- `ms/appel = median(ticks) * 20 / 240` ;
- `gain R69 / R60 = median_ticks_R68 / median_ticks_R69` ; **valeur > 1** = R69 plus rapide.

Si un cas donne 0 tick ou moins de quelques ticks par essai, le resultat est peu precis : ne pas en deduire un gain. Garder les valeurs brutes et la configuration WinUAE dans le compte rendu.

**Validation du benchmark** : `ERR 0`, `CLOSE -1`, `CHIP BEFORE/END` identiques pour **chaque** passage, `RESULT 1`, `BENCH FINISHED - CLOSE RETURNED`, et aucun Guru. Ces retours assurent les appels et la recuperation Chip globale, **pas** la comparaison pixel par pixel.

**Gate C AMOS Compiler : toujours interdite pour ces essais.** Une seule compilation finale sera tentee apres mesures, interpretation, corrections eventuelles et gel de la candidate. `LAST_GOOD` R68, archives et `tests/current/` restent inchanges.
