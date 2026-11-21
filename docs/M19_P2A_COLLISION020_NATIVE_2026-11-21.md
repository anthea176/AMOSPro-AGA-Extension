# M19 P2a — noyau privé de collision MC68020 — 21 novembre 2026

## Statut et provenance

**Source-only native : PASS sur le noyau isolé.** L'émetteur [`m19_p2a_collision020_emit.py`](../tools/m19_p2a_collision020_emit.py) produit un **vrai noyau MC68020 de 764 octets**, SHA256 `2546b269cad753c6b401c5d3cf3330e0f96545e64506a023d381b60c154450b7`, en code M68K réinstallable à deux adresses. La [CI 44901130823](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901130823) a exécuté ces octets dans Unicorn 2.1.4, avec décodage Capstone 5.0.9, sur deux implantations, après correctif de préservation du registre `A3`. **Le noyau n'est relié à aucun token AP20, ni à l'AMOS actif, ni à WinUAE.**

**Base de provenance :** P1e LAST_GOOD, reconstruite par [`build_m19_p1e_bank_edit_in_memory.py`](../tools/build_m19_p1e_bank_edit_in_memory.py), 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, cinq unités natives MC68020. Le noyau P2a part des sources `m19_p0e_object_table_emit.py`, `m19_p0f_bank_stamp_emit.py`, `m19_p1d_limit_bob_emit.py` et `m19_p0a_multi_bob_abk.py`, **jamais de la Lib désassemblée**. Les deux fichiers `dist/AMOSPro_AGA*.Lib` P1e restent octet-identiques ; l'ASC actif est inchangé.

## Contrat **privé** du noyau

Entrée : `A0` pointe vers un descripteur Bob A de 40 octets ; `A1` vers B, et `D0` contient 0 (rectangles) ou 1 (masques AGBO). **La préparation des descripteurs est obligatoire** : la couche appelante doit avoir déjà validé CPU, propriétaire `A5`, écran actif, objets P0e, stamps P0f, banque source, générations, bornes mémoire `TypeOfMem`, image AGBO et limites P1d. L'algorithme **ne sait pas** lire directement les structures privées dans la Lib.

| Offset (long big-endian) | Contenu |
| --- | --- |
| 0 / 4 / 8 / 12 | Bornes visibles `left, top, right, bottom` signées, **fin exclusive**, déjà coupées par écran et limites P1d |
| 16 / 20 | Origine réelle `X - hotspotX`, `Y - hotspotY`, signée |
| 24 / 28 | Largeur et hauteur source, de 1 à 4096 pixels |
| 32 | Pas réel de masque AGBO, `2 * ceil(W/16)` octets |
| 36 | Pointeur vers masque AGBO **validé et lisible**, ou zéro si l'image est entièrement opaque |

Sortie : `D3=1` collision, `D3=0` absence de collision, `D3=-1` descripteur/mode invalide ; `D2=0`. Les registres `D0,D1,D4..D7,A0..A6` et `A7` sont préservés. L'ancien prologue AMOS ne sauvegardait pas `A3` : sa modification initiale dans le noyau a été détectée par Gate A, puis corrigée en utilisant `A6`, qui est bien préservé. Pas de DMA, pas de Blit, pas d'allocation, pas de dessin et **pas de Swap implicite**.

La recherche masquée parcourt l'intersection effective et interroge le bit individuel à l'offset `(Y-originY)*stride + ((X-originX)//8)` avec `BTST`, bit `7-(X-originX)%8`. Une image sans masque est opaque, y compris couleur zéro. Les descripteurs contrôlent dimensions, strides, rectangles et alignement ; **l'identité physique et la plage réelle des pointeurs de masque doivent rester des garanties de l'appelant**.

## Régressions

| Groupe | Validation |
| --- | --- |
| Modèle rectangles / masques | 17 tests Python PASS |
| Pont P0e/P0f/AGBO/P1d | 23 tests Python PASS, dont banque ABK 26 réelle |
| Vrai noyau MC68020 isolé | 9 tests PASS sous Unicorn, à **deux bases** |
| Comparaisons au modèle indépendant | 720 appels aléatoires et 240 appels sur largeurs AGBO non alignées PASS |
| Registres et sécurité du noyau | D2/D3, préservation des registres AMOS, stack, canaris mémoire, refus des modes/pointeurs/dimensions invalides PASS |
| Contrôle de livraison / CPU | [CI dédiée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901130811) PASS |

Le [banc natif](../tools/test_m19_p2a_collision020_gate_a.py) produit la preuve d'exécution des octets. **49 tests (17 + 23 + 9) PASS** au total. Le contrôle exécuté n'implique **aucune** mesure de performance sur Amiga réel ; le parcours pixel à pixel reste à profiler.

## Gates

- **Gate A noyau MC68020 isolé : PASS** sous Unicorn + tests structurels/ABI. **Gate A intégration AMOS/AP20 : NON TESTÉE** (pas d'intégration).
- **Gate B Runtime WinUAE P2a : NON TESTÉE**.
- **Gate C AMOS Compiler P2a : NON TESTÉE**.
- **Gate D machine physique P2a : NON TESTÉE**.

## Prochain jalon

Ajouter un **adaptateur natif de lecture** qui exploite les ponts P1e déjà vérifiés : capture cohérente de deux Bobs actifs, vérification des stamps et banques sans changer la sélection, résolution des deux images et masques Chip, application des limites, construction des deux descripteurs, appel du noyau. Préciser le refus sur `READY/DIRTY` et l'impact des collisions hors écran avant d'autoriser un token AP20 ou une nouvelle Lib. Aucune promotion P2a implicite.
