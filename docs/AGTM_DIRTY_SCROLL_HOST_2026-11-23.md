# AGTM — Etude du scrolling dynamique et des deux pages (prototype hote)

**Date des mesures : 23 novembre 2026, 08:45:07 UTC.**  
**Statut : PROTOTYPE HOTE / TESTS PASS — NON VALIDE SUR MC68020 OU AGA.**  
**Cadre :** specification et prototypes preliminaires du futur chantier M20 AGTM, planifie apres M21 Dual Playfield. Aucun changement de l'API publique, des binaires, de l'ASM, des tests WinUAE ni du jalon Sprites en cours.

## 1. Objet

Le benchmark precedent comparait seulement un decor statique rendu integralement avec un decor decale et des bandes decouvertes. Ce second prototype cherche a verifier **le scrolling avec une carte modifiee a l'execution**, des couches transparentes, deux historiques de pages independants et des acteurs mobiles.

Sources du prototype :

- [Carte mutable, mises a jour partielles et cycle a deux pages](../tools/prototypes/agtm_dirty_scene_proto.py) — Git blob 6bc89555615274d31788f36bf5aeb9fca2f97afc.
- [11 tests de scene, edition et double buffer](../tools/prototypes/test_agtm_dirty_scene_proto.py) — blob 7e42781c1bf32c60ba10d05251fac8815802e39a.
- [Banc de mesures reproductible](../tools/prototypes/agtm_dirty_bench.py) — blob 6f4f11f91286767232ad105fa4437c2b48dc5cdd.
- [2 tests propres au benchmark](../tools/prototypes/test_agtm_dirty_bench.py) — blob b6736bba274e26c18b5c82dbbcbcbfb4c55d105a.
- Sources de reference existantes : [specification AGTM](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md), [oracle de pixels](../tools/prototypes/agtm_format_proto.py), [rendu par segments](../tools/prototypes/agtm_render_bench.py), [M20 P0 historique](M20_TILEMAP_P0_HOST_MODEL.md).

**Conformite : 27 tests Python PASS localement** (9 de format + 5 de rendu + 11 de scene + 2 de benchmark). Parmi eux, 120 frames pseudo-aleatoires reproductibles, des modifications sur plusieurs couches, des Bobs rectangulaires opaques de couleur zero, des cas de suppression d'acteurs et des refus avant Swap.

## 2. Contrat d'execution simule

1. Le fichier AGTM reste un format de stockage brut et versionne, sans etat d'execution.
2. Une fois charge, chaque couche devient un tableau **mutable d'octets contigus**. Une modification de cellule a un cout algorithmique O(1), sans recopier une couche complete.
3. Un compteur de revision et un journal borne de 128 editions indiquent quelles cases ont change. Plusieurs editions d'une meme case sont regroupees lors de la reconstruction.
4. Chaque page physique logique conserve sa **propre position de camera**, revision connue, image de decor propre et image composee (decor + acteurs).
5. Pendant la preparation du back, copier la zone commune depuis le dernier **decor propre de cette meme page** ; repeindre les bandes decouvertes et chaque case modifiee encore visible. Si l'historique n'est plus disponible, redessiner le decor entier.
6. Dessiner ensuite les acteurs. Ne jamais recopier un fond deja sali par un acteur pour preparer la frame suivante.
7. Un echec de prevalidation bloque la presentation (etat DIRTY). La page avant reste intacte ; le modele permet un abandon explicite. Aucune presentation implicite.
8. Les representations chunky 8 bits et rectangles Actor du prototype ne sont pas des Bobs AGBO ni des bitplanes AGA natifs ; le contrat d'integration avec les commandes Bobs existantes sera a qualifier.

**Note de performance :** le stockage actuel de deux decors propres et de deux images composees est un choix de modele hote. Il **ne constitue pas une obligation de reserver quatre bitmaps Chip RAM** dans la future extension.

## 3. Protocole de mesure

- **Machine :** Linux 6.18.57 x86-64 sous KVM ; Python 3.13.5.
- **Scenarios :** carte synthétique originale 64x64, tuiles 16x16, 64 indices, 1 ou 2 couches, vue **320x256**, profondeur modele **8 bits chunky**. Un fond initial avant les edits est capture hors mesure.
- **Algorithmes :** full = recomposition integrale par segments de tuiles ; incremental = copie du decor precedent + reconstitution des bandes + tuiles editees.
- **Verification :** egalite octet a octet des deux rendus avec le rendu pixel oracle **avant chaque cas chronometre** ; SHA-256 des pixels pour une trace reproductible.
- **Fenetre mesuree :** 5 passes alternees A/B puis B/A, 4 rendus par passe ; mediane des moyennes par passe. **11 cas x 2 methodes x 5 passes x 4 iterations = 440 rendus chronometres**, hors initialisation, edition de la carte, generation des ressources, oracle et echauffement.
- **Inclus dans le temps :** allocation et construction du nouveau buffer, copie chunky, traitement des regions / revision et composition des tuiles.
- **Exclus du temps :** modification des cellules, creation du fond de reference, acteurs, Swap, VBL, DMA, Blitter, allocation et liberation Chip/Fast, attente Safe/Disp.

Reproduction depuis la racine du depot :

~~~sh
python -B -m unittest discover -s tools/prototypes -p 'test_agtm*.py' -v
python -B tools/prototypes/agtm_dirty_bench.py --repeats 4 --passes 5
~~~

## 4. Resultats chronometres (millisecondes / frame)

| Couches | Edits depuis la derniere image | Camera | Rendu complet | Incremental | Rapport complet / incremental |
|---|---:|---|---:|---:|---:|
| 2 | 0 | +1,0 | 3,108 | 0,248 | x12,55 |
| 2 | 1 | +1,0 | 3,125 | 0,233 | x13,41 |
| 2 | 4 | +1,0 | 3,049 | 0,242 | x12,59 |
| 2 | 16 | +1,0 | 3,304 | 0,363 | x9,11 |
| 2 | 64 | +1,0 | 3,330 | 0,975 | x3,42 |
| 2 | 128 | +1,0 | 3,551 | 1,932 | x1,84 |
| 2 | 129 | +1,0 | 3,760 | 4,256 | x0,88 |
| 2 | 1 | +8,+8 | 3,133 | 0,325 | x9,63 |
| 2 | 16 | +16,0 | 3,182 | 0,535 | x5,95 |
| 2 | 64 | +16,0 | 3,166 | 1,170 | x2,71 |
| 1 | 16 | +1,0 | 2,390 | 0,313 | x7,64 |

**Important : tous les ratios sont des mesures Python/x86-64. Ils ne permettent pas de predire un FPS, un rapport d'acceleration ni un seuil de bascule MC68020/AGA.** Une cellule modifiee mesuree plus rapide que zero modification est un effet du bruit de mesure, pas un gain causal.

A 129 modifications, le journal de 128 entrees n'a plus les informations necessaires : le modele impose un **redessin complet**, avec un faible surcout de preverification et d'orchestration. Ce comportement est correct fonctionnellement et doit etre conserve ou explicitement remplace par un protocole equivalent.

## 5. Mesures brutes par passe

Chaque nombre represente la duree moyenne **d'une frame**, en millisecondes, sur 4 iterations, dans l'ordre des 5 passes.

~~~text
2L / 0 edits / (+1,0):
  FULL 3.442560 3.100285 3.115137 3.108080 3.035542
  INCR 0.247720 0.213181 0.210017 0.251881 0.250088
2L / 1 edit / (+1,0):
  FULL 3.415063 3.125236 3.060348 2.980216 3.320067
  INCR 0.256663 0.233081 0.221437 0.220348 0.245127
2L / 4 edits / (+1,0):
  FULL 2.963233 3.245648 3.048750 3.006588 3.219270
  INCR 0.239702 0.262721 0.242195 0.241895 0.249296
2L / 16 edits / (+1,0):
  FULL 2.978168 3.106168 4.096577 3.303847 3.573720
  INCR 0.374715 0.337001 0.362614 0.338752 0.471231
2L / 64 edits / (+1,0):
  FULL 3.133646 3.461724 3.582336 3.081607 3.329661
  INCR 0.974677 0.921568 1.065733 0.971412 1.029236
2L / 128 edits / (+1,0):
  FULL 3.784689 3.550704 3.463375 3.858949 3.430954
  INCR 1.931651 1.856194 2.016100 2.002158 1.843083
2L / 129 edits / (+1,0):
  FULL 3.517685 3.770310 3.990237 3.723494 3.760048
  INCR 4.533697 3.474648 5.967517 4.255984 3.537221
2L / 1 edit / (+8,+8):
  FULL 3.319487 2.925894 3.133320 3.236517 3.105772
  INCR 0.334475 0.344343 0.322379 0.324249 0.325380
2L / 16 edits / (+16,0):
  FULL 3.063437 3.182253 3.498548 3.173829 3.754681
  INCR 0.459305 0.459126 0.574765 0.549241 0.535049
2L / 64 edits / (+16,0):
  FULL 3.062545 3.068472 3.312508 3.231004 3.165592
  INCR 1.169576 1.092502 1.209139 1.384918 1.128810
1L / 16 edits / (+1,0):
  FULL 2.690920 2.324069 2.661960 2.389515 2.366908
  INCR 0.312275 0.324249 0.337462 0.297812 0.312916
~~~

## 6. Consequences pour la specification AGA

**Moteur de carte :**
- Ne jamais copier toute la carte en RAM pour chaque modification ; modifier un octet en place et incrementer la generation.
- Garder une **revision distincte par page physique** et un mecanisme explicite d'invalidation lors d'edition du tileset / remplacement de banque.
- Reconstituer une cellule modifiee avec toutes ses couches, pour eviter un masque transparent laissant des residus de pixels anciens.
- Apres une perte de l'historique, un saut de camera ou un changement de tileset, **redessin complet** de la page concernee.
- Ne pas reutiliser des pixels contenant des acteurs comme source de copie du decor.
- Mesurer si le seuil de bascule full/partial doit dependere du nombre de zones uniques, du cout des couches, des masques et de la zone d'ecran, plutot que d'un nombre fixe d'editions.

**Memoire :**
- Une page planaire 320x256x8 = **81 920 octets**, deux pages = **163 840 octets**, hors systeme et images.
- Si une solution native exige *en plus* deux caches planaires complets de decor, cela ajouterait **163 840 octets**, soit **327 680 octets pour pages et caches seuls**. Ces caches supplementaires ne sont **pas encore justifies** ; etudier reutilisation de la memoire existante, stockage Fast ou restauration localisee.
- Un tileset de 256 images 16x16x8 = **65 536 octets de pixels** avant masques, staging et structures.
- Pour un scrolling 1 px a 320x256, la zone nouvellement decouverte est seulement de 256 pixels, mais **la copie logicielle du reste du decor represente encore 81 664 pixels** ; le gain en trafic Chip n'est donc pas prouve.

**Backend :**
- Comparer rendu CPU MC68020 en Fast vers bitplanes Chip, Blitter avec tuiles preparees en Chip et **scrolling materiel compatible OS** uniquement apres la qualification de Dual Playfield M21.
- Garder une reference de pixels independante et couvrir 1/2/4 couches, viewport non aligne, masques, snapshots de fond, Bobs existants, Safe/Disp, Runtime et vrai Compiler.

**Prochaine recherche autorisee :** budget de trafic memoire par frame et opportunite d'un cache circulaire / scrolling materiel, avec modele source independant, sans modification de l'extension installable.

**Etat :** tests Python et benchmark hote observes ; **Gates A/B/C/D : NON TESTEES**. Aucune modification de LAST_GOOD, de l'ASC actif, des commandes AP20 ou de sources ASM.
