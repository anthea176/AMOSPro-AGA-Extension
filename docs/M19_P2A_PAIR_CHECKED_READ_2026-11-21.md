# M19 P2a — lectures natives appariées P0f — 21 novembre 2026

## Résultat

**Barrière native P2a de lecture de deux Bobs : PASS dans le banc 68020.** Le nouvel émetteur [`m19_p2a_pair_checked_read_emit.py`](../tools/m19_p2a_pair_checked_read_emit.py) produit **328 octets MC68020**, SHA256 `3e2cdedb603fb090f0bfd4b46cf3ecc1e3684ace2ddf922b7b3076c6efa6d5dd`. Les 9 [tests natifs](../tools/test_m19_p2a_pair_checked_read_gate_a.py) exécutent le vrai `identity_check` P0f sur deux implantations V2 (les services AMOS/Exec sont simulés) ; [CI PASS 44901815788](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901815788).

**Périmètre :** entrée privée source-only, PAS de fonction AMOS `Aga Bob Col`, PAS de nouveau token AP20, PAS de modification de `dist/AMOSPro_AGA.Lib`, PAS de modification de `LAST_GOOD` ou de `tests/current/`. L'émission n'est pas une lecture « live » testée dans WinUAE ni une intégration compilée.

## ABI privée du pont

| Registre | Entrée |
| --- | --- |
| `D0` | Numéro du premier Bob 1..64 |
| `D1` | Numéro du second Bob 1..64, distinct du premier |
| `A1` | **Tampon de sortie privé** lisible/écrivable, 48 octets contigus |
| `A4` | **Pointeur privé source-vérifié** vers `identity_check_entry` P0f ; jamais fourni par l'utilisateur AMOS |
| `A5` | Propriétaire AMOS actuel, vérifié par les appels P0f |

**Sortie :** `D3=1` si les deux contrôles `identity_check` réussissent, et les deux enregistrements P0e de 24 octets sont publiés dans le tampon dans l'ordre A/B. `D3=0` si une vérification échoue ; les **48 octets du tampon restent inchangés**. `D2=0`. Les autres registres AMOS et la pile sont préservés. La source n'exécute aucun `Aga Swap`, DMA, Blit ni changement de banque sélectionnée.

La routine rejette les IDs hors limites/égaux, les pointeurs nuls/impairs, la sortie non reconnue par `Exec TypeOfMem` aux deux extrémités, puis utilise **deux fois le `identity_check` natif existant**. Ce dernier s'appuie sur le vrai code P0f `Bnk.GetAdr`, la génération, la taille et la tête `Cur_Banks` liées à chaque Bob actif ; elle ne reconstitue pas cette logique à partir de suppositions.

**Sécurité / limites :** le code n'examine PAS lui-même l'adresse d'exécution de `A4` : le code appelant DOIT injecter une cible de confiance. `TypeOfMem` aux deux bouts ne prouve pas à lui seul l'intégrité des 48 octets intermédiaires : le tampon doit être privé, aligné, contigu et alloué par le moteur. P0f ne garantit pas l'absence d'un scénario ABA (mêmes adresse/génération réutilisées). La lecture suppose une commande **synchrone** non réentrante : aucune banque ne doit être mutée entre les deux appels.

## Tests vérifiés

| Scénario | Résultat |
| --- | --- |
| Émission déterministe + désassemblage complet Capstone MC68020 | PASS |
| Deux Bobs dans deux banques distinctes ; inversion de l'ordre | PASS |
| Conservation des registres, des tampons et de la sélection courante | PASS |
| Génération périmée dans la première ou seconde banque ; suppression de liste | Refus avant publication |
| Bob OFF, propriétaire incorrect, ID nul / `>64` / identique | Refus sans écriture |
| Pointeur d'identité ou de sortie nul / impair, `TypeOfMem` rejeté | Refus sans écriture |
| CPU 68020 non déclaré et réactivation | Refus puis PASS |
| Lecture répétée sur deux placements V2 | PASS |

`python -B tools/test_m19_p2a_pair_checked_read_gate_a.py`

La [CI P2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901815788) passe **58 tests applicatifs** : 17 modèle Python, 23 pont AGBO, 9 noyau de collision MC68020, 9 lectures appariées MC68020. Les tests de politique CPU et livraison sont également PASS. Les autres tests unitaires de contrôle de politique ne sont pas inclus dans ce total.

## Limite actuelle et suite

**Mise à jour 21/11/2026 :** l’étape suivante de résolution de deux images et masques Chip est désormais validée en source-only ([raccord P0f+P0j-b3](M19_P2A_PAIR_CHIP_RESOLVE_2026-11-21.md), 946 octets et 8/8 tests MC68020 supplémentaires). Les 58 tests de ce rapport demeurent la preuve de l’étape précédente ; **66 tests** passent sur la CI élargie. Le pont ne construit pas encore les deux descripteurs de collision de 40 octets.

Ce pont **publie les deux métadonnées Bob, mais ne résout PAS leurs images/masques ni le descripteur de collision de 40 octets**. Les vérifications P0f sont exécutées à partir des sources natives historiques dans un environnement simulé. Avant toute commande AMOS, il reste à raccorder les deux enregistrements au résolveur explicite [P0j-b3](../tools/m19_p0j_explicit_image_resolve_emit.py), à vérifier le propriétaire et la durée de vie des allocations Chip, à appliquer les zones P1d, à construire les deux descripteurs puis à invoquer le [noyau P2a](M19_P2A_COLLISION020_NATIVE_2026-11-21.md) avec un banc intégré Gate A.

**Gates :** Gate A du *pont privé isolé* PASS avec services Amiga simulés. Gate A de la chaîne P2a complète / de l'API AMOS : NON TESTÉE. Gate B WinUAE, Gate C Compiler et Gate D Amiga physique P2a : NON TESTÉES.
