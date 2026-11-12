# Audit documentaire AGE v1.01 — blocs graphiques et C2P/P2C

**Date :** 12/11/2026 · **Statut : AUDIT UNIQUEMENT — aucune implémentation autorisée** · **Branche :** `main`.

## Périmètre et sources

Archive utilisateur `Age_V1_01.zip` (AGE, Advanced Graphics Environment, Kevin Picone, version 1.01 du 26/11/2000). Analyse en lecture seule du manifeste ZIP, de `Readme.txt`, des pages `Docs/Pages/howtouse.htm`, `welcome.htm` et `copyrights.htm`, et des en-têtes/fichiers graphiques. Lecture de la documentation de l'extension AGA sur `main`. **Aucune exécution de AGE.lib sous WinUAE, aucun désassemblage ni reverse engineering, aucun benchmark matériel.**

AGE indique expressément qu'il **ne s'agit pas d'une extension AMOS** : les procédures AMOS servent de passerelles vers `AGE.lib`. AGE v1.01 est décrit par son auteur comme un état inachevé, avec des fonctions susceptibles de ne pas fonctionner comme prévu. Sa licence freeware **interdit la modification et le reverse engineering de AGE.lib**. Les propositions ci-dessous sont des développements indépendants fondés sur les capacités documentées, pas une intégration de son code.

## A. Inventaire vérifié : blocs et tilemaps

| API documentée AGE | Paramètres listés dans `howtouse.htm` | Ce qui est établi |
|---|---|---|
| `_AGE_OPEN_BLKDATA_BANK` | `BLKFILENAME$,BANK,W,H,D,BLKS,BLKFORMAT` | Ouverture d'une banque de données de blocs |
| `_AGE_REMOVE_BLKDATA_BANK` | `BANK` | Suppression de la banque |
| `_AGE_DRAW_BLOCK_ARRAY_CPU` | `BANK,X1,Y1,X2,Y2,MAPX,MAPY` | Entrée de dessin CPU d'un ensemble de blocs |

L'archive fournit les fichiers `Demonpic.BlockData.raw` et `Demonpic.BlockData.planar.raw` (**81 922 octets chacun**), ainsi que `Demonpic.Blockmap.256.raw` (**81 920 octets**) et `Demonpic.Blockmap.256.iff`. Le `BMHD` de cet IFF indique **320×256, profondeur 8, compression 1**. La division 320/16 × 256/16 donne **320 positions de blocs 16×16** ; ceci est une interprétation de la géométrie, **pas une preuve du format interne des fichiers ni d'un moteur complet de cartes à indices**. Les deux fichiers BlockData ont deux octets de plus que le volume brut 8 bitplanes ; leur rôle exact reste à vérifier par des sources autorisées (documentation / exemple AMOS), sans analyser le binaire AGE.

**Non établi :** scrolling de maps, taille de carte logique, couches, masque/transparence, organisation exacte des indices, accès direct à un bloc, format et durée de vie de toutes les allocations. Une fonction nommée `DRAW_BLOCK_ARRAY_CPU` ne prouve pas à elle seule ces capacités.

### Piste indépendante pour AMOSPro AGA

- **Tileset :** banques DATA AMOS avec blocs 16×16 en 1–8 bitplanes ; étudier un format versionné séparé ou une extension d'AGAPIC, sans casser AGAPIC v1.
- **Rendu :** CPU Fast→Chip vers le **back buffer Intuition privé** avec garde `Safe` non bloquante, clipping X/Y, profondeur/palette et masques opaques/transparents (index 0 visible possible).
- **Cartes :** banque d'indices distincte, dimensions et caméra, tuiles visibles, gestion dirty rectangles par *chaque* back buffer pour prévenir des images obsolètes après `Aga Swap`.
- **Comparatifs requis :** AGAPIC RLE décodé à chaque affichage vs tileset pré-décodé en Fast RAM ; 8/16/32 pixels et X aligné/non aligné ; opaque/transparent ; copie CPU directe vs stratégies utilisant Chip/Blitter si justifiées.
- Une tuile **16×16×8** brute utilise **256 octets** de pixels planaires, ou **288 octets** avec masque 1 bit séparé. Pour 256 tuiles : **65 536 / 73 728 octets**, hors index, en-têtes et allocation.
- Aucune API `Aga Tile Draw` / `Aga Map Draw` validée ; ce sont seulement des noms de travail. Éviter de confondre blocs AGAPIC, animations M18 et scrolling M20.

## B. Inventaire vérifié : conversion Chunky/Planar

| API documentée AGE | Paramètres listés | Ce qui est établi |
|---|---|---|
| `_AGE_C2P_STRIP_FROM_MEMORY` | `STRIPADR,X1,X2,Y` | Conversion Chunky→Planar d'une bande depuis la mémoire |
| `_AGE_P2C_STRIP_TO_MEMORY` | `STRIPADR,X1,X2,Y` | Conversion Planar→Chunky d'une bande vers la mémoire |
| `_AGE_C2P_SCRN` | `SRC,DEST` | Conversion d'écran Chunky→Planar |
| `_AGE_C2P_SCRN_CLS` | `SRC,DEST` | Variante d'écran dont l'effet exact du suffixe `CLS` n'est **pas documenté** par la seule liste |

**Non établi :** algorithme 68020 réel, profondeur exacte admissible, arrangement des buffers, conditions d'alignement, compatibilité compiler ou débit. Ne pas déduire que le suffixe `CLS` efface la destination sans validation. Ne pas désassembler `AGE.lib`.

### Piste indépendante pour AMOSPro AGA

- Buffer Chunky **8 bits = 1 octet/pixel**, préférentiellement en Fast RAM ; destination en **8 bitplanes AGA Chip RAM** déjà gérés par l'extension.
- Première étude : conversion **plein écran**, puis **rectangles partiels** et éventuellement P2C pour capture/retouche ; tous les pointeurs, tailles, `Safe`, clipping, synchronisation et ABI Compiler doivent être contractualisés.
- À 320×256×8, un écran Chunky et un écran Planar occupent **chacun 81 920 octets** (hors alignements/métadonnées). La conversion n'est **pas** une compression ni une économie de Chip RAM ; elle fournit une représentation favorable aux traitements CPU par pixel.
- **Ne pas imposer C2P aux tilemaps planaires** : la voie de rendu direct reste indépendante et potentiellement moins coûteuse.
- Comparer des algorithmes 68000/68020 strictement indépendants, mesurés sur WinUAE et si possible matériel réel ; aucun gain ni FPS annoncé avant test.

## Compatibilité et preuves obligatoires avant un futur chantier

- Conserver le contrat de `Aga Image Draw`, `Aga Image Capture`, `Aga Bank Image Draw`, le format AGAPIC v1 et les tests validés.
- Employer les **services AmigaOS** et l'architecture Intuition existante, sans prise de contrôle système ou accès direct non approuvé aux registres DMA.
- Tests Gate A CPU/CI, Gate B AMOS interprété WinUAE, Gate C **nouvel exécutable** AMOS Compiler WinUAE et Gate D matériel physique **indépendants**.
- Évaluer Fast/Chip réelles, tailles, transparence (index 0 visible), X non aligné, clipping, double buffering, Ctrl+C, fuite mémoire et fermeture.
- **Décision actuelle : documenter uniquement** ; aucune commande AP20, aucun builder, aucun fichier test actif, aucune bibliothèque candidate, aucune promotion de `LAST_GOOD` et aucune implémentation n'est autorisée par cette note.

**Références internes :** [roadmap active](ROADMAP.md) · [format AGAPIC](M16_AGAPIC_FORMAT_DESIGN.md) · [architecture](ARCHITECTURE.md) · [reprise](NEXT_SESSION.md).
