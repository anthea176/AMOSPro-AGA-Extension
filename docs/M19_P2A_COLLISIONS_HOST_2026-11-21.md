# M19 P2a — Collisions Bob–Bob (modèle hôte)

**21 novembre 2026.** P2a est engagé après la promotion de P1e. Ce document formalise le **modèle de référence Python et son raccord P1e**, indépendants du [noyau MC68020 source-only déjà exécuté](M19_P2A_COLLISION020_NATIVE_2026-11-21.md). Aucune nouvelle API publique AMOS ni Lib P2a.

## Portée et comportement envisagé

Le futur équivalent de BOB COL / COL sera abordé en deux niveaux :

1. **Rectangle** : intersection des empreintes visibles des images après positionnement et clipping. Un simple contact de bords ne constitue pas une collision.
2. **Masque** : au moins un pixel opaque commun dans la zone d'intersection. Une image sans masque est opaque, index couleur 0 compris.

Le modèle utilise la position logique moins les coordonnées du hotspot pour déterminer l'origine graphique. Il coupe la zone par l'écran, la limite globale, puis la limite locale éventuelle (P1d). Les Bobs OFF ne participent pas. Les paires sont renvoyées dans l'ordre des IDs, indépendant de la priorité de dessin. Il ne modifie ni banques, ni images partagées, ni buffers ou états Safe/Disp.

**Attention :** le masque du modèle est une représentation **hôte de test** (bit 1 = opaque, MSB d'abord, par ligne), **pas** une spécification du stockage AGBO natif.

## Livrables

- [Modèle Python P2a](../tools/m19_p2a_bob_collision_model.py) : rectangles et masques, hotspot, clipping, OFF.
- [17 tests géométriques](../tools/test_m19_p2a_bob_collision_model.py) : bords, positions négatives, masques de modèle, partage d'image et ordre des paires.
- [Pont réel AGBO/P1e](../tools/m19_p2a_agbo_bridge.py) : décodage hôte des objets, stamps et zones P1d, validation de la banque, conversion du masque AGBO et calcul des paires.
- [23 tests de raccord](../tools/test_m19_p2a_agbo_bridge.py) : formats source, coordonnées, refus sur références périmées, banque ABK 26 source-pinnée, bordures 16 bits et limites.
- [CI P2a dédiée](../.github/workflows/m19-p2a-bob-collisions-host.yml) : **40 tests hôtes PASS** ([exécution GitHub 44899748782](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44899748782)), syntaxe et absence de modification de la Lib et de l'ASC.
- [Noyau privé MC68020](M19_P2A_COLLISION020_NATIVE_2026-11-21.md) : code source de 764 octets, 9 tests natifs PASS et comparaison au modèle sur 2 placements, sans token AP20.
- [Conception générale P2](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) : collisions, retournements H/V, modes avancés et AMAL ultérieurement.

## Décisions à prendre avant développement natif

Signatures publiques exactes, retour par paire ou liste de contacts, politique de collisions hors écran et limites de clipping, effets des états READY/DIRTY, coût CPU MC68020, accès sûr au masque AGBO réel et adaptation des Bobs actifs. **Le noyau natif isolé existe et passe ses tests, mais l'API publique / l'intégration AMOS / WinUAE / Compiler ne sont pas validés.**

## Validation

**40 tests hôtes PASS** dans la CI du 21/11/2026 : 17 modèles géométriques + 23 cas de raccord au code source réel P1e/AGBO. La banque `M19_P1B_HOTSPOT_BANK26.abk` (200 octets) est comparée au générateur déterministe et à son SHA256 source-pinné. **Ces 40 tests Python sont distincts des 9 tests du noyau natif MC68020 réellement exécuté sous Unicorn : Gate A du noyau isolé PASS** ([CI 44901130823](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901130823)). **Gate A intégration AMOS/AP20 non testée ; B WinUAE, C Compiler, D physique NON TESTÉES.** La bibliothèque P1e LAST_GOOD reste inchangée.

## Raccord vérifié aux structures natives P1e

| Source de vérité | Format interne | Lecture P2a |
| --- | --- | --- |
| [`m19_p0e_object_table_emit.py`](../tools/m19_p0e_object_table_emit.py) | 64 objets × 24 octets ; six LONG big-endian, banque(+0), image(+4), X signé(+8), Y signé(+12), actif(+16), réservé(+20) | L'ID Bob est l'index 1..64 ; OFF ignoré, un enregistrement actif incohérent est refusé |
| [`m19_p0f_bank_stamp_emit.py`](../tools/m19_p0f_bank_stamp_emit.py) | 16 octets par Bob : pointeur source, génération AGBO, tête `Cur_Banks`, longueur | Rejet si la copie du stamp ne correspond pas à la banque fournie |
| [`m19_p0a_multi_bob_abk.py`](../tools/m19_p0a_multi_bob_abk.py) | AGBO v1 : en-tête 32 octets, entrée image 40 octets, masque 1 bit indépendant sur pas de ligne `2*ceil(W/16)` | `parse_payload` vérifie intégralement les images et leurs bits inutilisés ; conversion en lignes hôtes `ceil(W/8)` (mêmes bits MSB-first) |
| [`m19_p1d_limit_bob_emit.py`](../tools/m19_p1d_limit_bob_emit.py) | 65 zones × 16 octets, bornes de fin exclusives : 0 globale et 1..64 locales | Intersections écran / globale / locale ; seules zones canoniques de surface positive sont acceptées |

**Limites de preuve :** les enregistrements et pointeurs sont des **copies de banc hôte**, pas une lecture directe de la mémoire WinUAE. Le pont compare l'identité et la génération des copies ; il ne peut pas attester la validité d'un pointeur Amiga, le `TypeOfMem`, la propriété A5 ou le risque ABA (même adresse et génération réutilisées). Une implémentation native doit employer les ponts déjà vérifiés `identity_check` / `stamp_verify`, ne jamais lire une banque non validée ni contourner les états du moteur.

La banque ABK 26 vérifiée n'est pas un test P2a natif : elle confirme seulement l'interprétation effective de ses masques et hotspots.

## Première signature AP20 proposée — NON APPROUVÉE, NON IMPLÉMENTÉE

Syntaxe à examiner : `_HIT=Aga Bob Col(_A,_B,_MODE)`, **fonction numérique**, `_A` et `_B` différents, dans 1..64. `_MODE=0` testerait le rectangle visible et `_MODE=1` les masques pixel-exacts. Retour proposé : **1** si collision, **0** si aucune collision (y compris un Bob OFF), **-1** en cas de refus ou d'état source invalide. Aucune modification de Bob, d'image, de limite, de DMA ou de `Aga Swap`.

Une seule interrogation **par paire** suffit pour un premier jalon et évite de définir immédiatement une table `COL` persistante. Une API d'énumération de tous les contacts pourra être étudiée ensuite. **À vérifier avant de fixer cette syntaxe :** unicité AP20 du token, convention D2/D3, analyse du propriétaire et du timestamp des données au cours de READY/DIRTY, distinction collision logique/zone de dessin, coût MC68020 du masque, et protocole Gate A native / B Runtime. Pas de compatibilité implicite avec `BOB COL` des sprites OCS.

## Étape suivante

Le **noyau privé MC68020 est livré en source et confronté au modèle**. Préparer maintenant son adaptateur de lecture natif à partir des ponts de lecture et d'identité P1e, avec validation des pointeurs avant toute utilisation. Pour une livraison de nouvelle `.Lib`, un nouvel ASC ou une promotion de LAST_GOOD, une autorisation distincte restera nécessaire.
