# RPG Engine / AGTM — benchmark hôte du 23/11/2026

**Statut : PROTOTYPE HÔTE MESURÉ — AUCUNE PERFORMANCE MC68020/AGA VALIDÉE.**
Rattachement : [M20 dans la roadmap](ROADMAP.md), futur chantier natif **après M21 Dual playfield**, étude et prototypes autorisés dès maintenant. Le chantier Sprites AGA n'est pas modifié.

## 1. Sources et environnement de mesure

- **Date :** 23/11/2026 à 08:27:46 UTC.
- **Machine hôte :** Linux 6.18.57 x86-64 sous KVM, CPU Intel Xeon Platinum 8573C, Python 3.13.5.
- [Spécification AGTM](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md).
- [Codec et oracle de référence](../tools/prototypes/agtm_format_proto.py), Git blob f5f3886be11cafb6944600d9bba16e70a19a89ea.
- [Prototype de benchmark](../tools/prototypes/agtm_render_bench.py), Git blob **142f14571c58edd4bba3a081d09326fd222f3f36**.
- Tests : [format](../tools/prototypes/test_agtm_format_proto.py) et [rendu](../tools/prototypes/test_agtm_render_bench.py) : **14 tests PASS localement**, dont scénarios diagonaux, quatre directions, caméra non alignée, grands sauts et deux pages alternées.
- Données synthétiques originales et déterministes : carte 64×64, 64 images de 16×16, 1 ou 2 couches, transparence du pen 0 sur overlays seulement.

**Aucune instruction 68020, aucun Amiga, aucun Blitter DMA, aucun transfert réel en Chip RAM et aucun écran AMOS n'ont été mesurés.**

## 2. Protocole reproductible

Trois stratégies produisant exactement les **mêmes octets de pixels** dans chaque scénario, vérifiés **avant** la fenêtre chronométrée :

1. **Pixel reference** : boucle Python pixel par pixel, servant d'oracle indépendant.
2. **Tile spans** : copie de segments contigus de lignes 16×16, puis transparence des couches supérieures.
3. **Scroll + bandes** : copie des pixels communs à la frame précédente, puis dessin des seuls rectangles découverts.

Configuration : 6 scénarios × 3 méthodes × 5 passes × 5 frames = **450 rendus chronométrés**. Mesures avec **time.perf_counter_ns**, cinq moyennes par méthode et **médiane** des cinq passes ; échauffement hors mesure ; passages intercalés **A-B-C puis C-B-A**. La préparation des tuiles, la constitution de la frame précédente et le contrôle des pixels sont hors chrono. La mesure inclut l'allocation et la construction du buffer chunky rendu.

Depuis la racine du dépôt :

~~~sh
python -B -m unittest discover -s tools/prototypes -p 'test_agtm*.py' -v
python -B tools/prototypes/agtm_render_bench.py --repeats 5 --passes 5
~~~

## 3. Résultats observés (ms/frame)

| Vue | Couches | Décalage (px) | Oracle | Tuiles par segments | Scroll + bandes | Rapport segments / scroll |
|---|---:|---|---:|---:|---:|---:|
| 192×192 | 1 | (+1,0) | 9,252 | 1,182 | 0,162 | ×7,30 |
| 192×192 | 2 | (+8,+8) | 10,415 | 1,491 | 0,204 | ×7,33 |
| 320×256 | 1 | (+16,0) | 20,041 | 2,237 | 0,341 | ×6,56 |
| 320×256 | 2 | (+1,0) | 25,374 | 3,115 | 0,238 | ×13,09 |
| 320×256 | 2 | (+8,+8) | 24,371 | 3,050 | 0,352 | ×8,67 |
| 320×256 | 2 | (+16,0) | 24,426 | 3,379 | 0,404 | ×8,36 |

**Ces rapports ne sont pas des gains Amiga.** La copie de tranches en Python bénéficie de primitives en C du runtime x86-64, et ne reflète ni le coût du DMA Blitter, ni la bande passante Chip ni les synchronisations de l'Amiga. Pics isolés visibles dans les mesures brutes ci-dessous : la virtualisation apporte du bruit.

## 4. Mesures brutes : 5 passes de 5 frames (ms/frame)

~~~text
192x192 / 1 layer / (+1,0)
pixel_reference : 10.217535 9.252078 9.402410 8.559426 8.544203
tile_spans      : 11.276941 1.370264 1.181942 1.174894 1.006117
scroll          : 0.166940 0.929344 0.139786 0.141328 0.162002
192x192 / 2 layers / (+8,+8)
pixel_reference : 10.298262 10.151910 10.414513 11.010660 11.807264
tile_spans      : 1.659036 1.802861 1.491321 1.480953 1.313902
scroll          : 0.192964 0.219935 0.197689 0.203562 0.210787
320x256 / 1 layer / (+16,0)
pixel_reference : 19.488445 33.108373 21.284854 19.254193 20.041230
tile_spans      : 2.215393 2.386422 2.237250 2.303564 2.189213
scroll          : 0.300777 0.317373 0.416477 0.342044 0.341115
320x256 / 2 layers / (+1,0)
pixel_reference : 26.415337 25.373644 23.819330 26.228193 23.720721
tile_spans      : 3.180272 3.115102 2.979573 3.243470 2.948684
scroll          : 0.237893 0.216579 0.304567 0.221614 0.252780
320x256 / 2 layers / (+8,+8)
pixel_reference : 42.667689 23.331620 23.982283 24.371062 24.948370
tile_spans      : 3.807154 3.220823 2.905551 2.855488 3.049584
scroll          : 0.426463 0.351642 0.299646 0.300556 0.554533
320x256 / 2 layers / (+16,0)
pixel_reference : 25.888338 24.220379 23.565458 24.426033 25.873353
tile_spans      : 2.952168 3.652901 2.937242 3.379457 3.445469
scroll          : 0.454276 0.461470 0.385007 0.404133 0.385590
~~~

## 5. Information utile pour le futur backend AGA

À **320×256×8 plans**, une page de pixels représente **81 920 octets**. Déplacement incrémental en chunky :

| Caméra | Pixels recomposés | Part de vue | Pixels recopiés |
|---|---:|---:|---:|
| (+1,0) | 256 | 0,3125 % | 81 664 |
| (+8,+8) | 4 544 | 5,547 % | 77 376 |
| (+16,0) | 4 096 | 5 % | 77 824 |

Avec l'algorithme simulé, chaque pixel destination est encore écrit et les pixels de la zone recopiée sont également lus. La baisse du nombre de tuiles composées **n'implique pas une baisse équivalente des transferts mémoire**. Un scrolling matériel peut supprimer une part des copies, mais son intégration sûre à l'écran Intuition AGA est encore à étudier.

**Préconisations non figées :** indices AGTM U8 bruts, tuiles 16×16, données carte en Fast ; mesurer la préparation du tileset, les couches, les masques, les états propres aux deux pages et les octets réellement transférés. Ne pas déclarer un algorithme gagnant avant comparaison native.

## 6. Prochaine campagne native (après Dual playfield M21)

- **Gate A :** implémentation MC68020 source-provenance, oracles planaires, limites d'adresses, banque AGTM, transparence et alignements.
- **Gate B :** WinUAE 68020 14 MHz, AGA PAL, JIT OFF ; même scène à 192×192 / 320×256, plans 4/5/8 selon capacités réellement vérifiées ; CPU direct vs Blitter, Safe/Disp et Bobs.
- **Gate C :** même banc sous vrai AMOS Compiler, journaux distincts.
- **Gate D :** Amiga AGA réel si disponible.
- Pour chaque méthode : séparer coût de préparation, dessin, copie, VBL/Swap et fermeture ; mesurer sans VBL pour le micro-benchmark de dessin, puis avec VBL en coût frame complet.

**Statut : prototype hôte PASS + mesures locales. AGTM Gates A/B/C/D : NON TESTÉES.**
Aucune nouvelle Lib, aucune commande AP20, aucun changement de tests/current, LAST_GOOD ou du chantier Sprites.
