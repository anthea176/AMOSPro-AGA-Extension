# AGTM v1 — spécification exploratoire de tilemap pour RPG Engine

**Date :** 23 novembre 2026. **Statut : SPÉCIFICATION EXPLORATOIRE + PROTOTYPE HÔTE ; FORMAT NON FIGÉ, AUCUN JALON NATIF OUVERT.**
**Dépôt :** `anthea176/AMOSPro-AGA-Extension`, branche `main`.
**Référence active vérifiée :** M19 P2d / `LAST_GOOD` identiques (136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`), MC68020 minimum.
**Portée :** spécification de fichier et prototypes hôtes autonomes. **Aucune commande AP20, routine ASM, nouvelle bibliothèque, promotion, modification de roadmap ou de campagne active.**

## 0. Rattachement à la roadmap et règles de non-interférence

La [roadmap AGA](ROADMAP.md) confirme désormais **M20 — tilemaps / scrolling / AGTM comme chantier natif complet à lancer APRÈS M21 dual playfield**, tandis que le chantier Sprites matériels AGA demeure la priorité actuelle. **AGTM n'est toujours pas un jalon « M20 P1 » déjà exécuté** ; la phase présente reste spécification et prototypes hôtes, sans autorisation de modifier la Lib.

**Autorisés maintenant :** la spécification, les prototypes hôtes autonomes et leurs tests/mesures. **La mise à jour de la roadmap du 23/11/2026 est la décision explicite de planification**, pas une ouverture de développement natif. **Hors périmètre de l'étude :** les builders, le natif MC68020, les tokens AP20, `tests/current/`, `dist/`, `LAST_GOOD` et toute promotion.

**Références de l'étude :**
- [Prototype de codec et oracle chunky AGTM](../tools/prototypes/agtm_format_proto.py) — format binaire, mutations immutables et composition de pixels.
- [Tests hôtes du format](../tools/prototypes/test_agtm_format_proto.py) — 9 tests PASS ; [rendu et scrolling](../tools/prototypes/test_agtm_render_bench.py) — 5 tests PASS supplémentaires, soit **14 PASS localement**, aucune Gate A/B/C/D.
- [M20 P0 original](M20_TILEMAP_P0_HOST_MODEL.md) — modèle de scrolling et tests existants conservés sans modification.

Une décision distincte est requise avant de figer le format, ouvrir un jalon natif, modifier un outil actif ou changer la roadmap.

## 1. Objectif et réutilisation

Créer une représentation de carte 2D extrêmement simple à parcourir dans une boucle native MC68020 : lecture rapide des cellules, tuiles graphiques pré-décodées, défilement incrémental, couches graphiques, mise à jour des deux pages physiques indépendantes. La logique de jeu (collision, quêtes, objets interactifs, pathfinding) reste dans RPG Engine et hors du noyau AGA.

**Base existante conservée :** [M20 P0](M20_TILEMAP_P0_HOST_MODEL.md), `tools/m20_tilemap_model.py` et ses 13 tests hôtes (caméra par page, bandes découvertes, révisions de carte, restauration du fond, Bobs, 405 frames simulées). Le modèle est un oracle chunky et non un renderer AGA. Cette étude ne le modifie pas.

**Séparation délibérée :**
- Banque de carte **AGTM** : indices de cellules, résidente idéalement en Fast RAM.
- Banque graphique **FICON8** existante : images 16×16×8, palette globale de l'écran AGA ; ses données peuvent être pré-stagées en Chip avec **FICHIP8**.
- État runtime : caméra, choix de page physique, historique dirty, état DMA/Swap, pointeurs préparés ; **jamais sérialisé dans AGTM**.

Cette séparation permet de développer un futur tileset optimisé `AGTS` ou de changer de moteur graphique **sans modifier les cartes**.

## 2. Hypothèses exploratoires pour obtenir un parcours rapide

- Taille de tuile fixe du prototype v1 : **16×16** ; division/produits convertibles en décalages. Ne pas rendre cette dimension obligatoire dans RPG Engine à long terme.
- **Un octet par cellule**, brut, sans RLE/LZ ni listes à décoder pendant les frames ; `0..255`.
- Largeur et hauteur de la carte du prototype v1 : **1..256 cellules**, données contiguës ligne par ligne et couche par couche.
- **1 à 4 couches** dans le fichier, mais banc exploratoire d'abord sur 1 couche opaque puis 2 couches.
- Le premier chemin graphique compare le moteur actuel FICON8/FICHIP8 en 8 bitplanes ; les chemins 4/5/6 bitplanes ou une banque `AGTS` spécialisée seront décidés au benchmark.
- L'index de tile `N` correspond au **FICON8 IconID `N+1`**, dans la banque graphique associée **à l'ouverture**, et non à un numéro de banque figé dans le fichier.
- Sur la couche 0, l'index 0 est une tuile valide et opaque. Sur les couches suivantes, **l'index 0 est « aucune tuile »**, les indices 1..255 sont dessinés en mode transparent (index couleur 0 transparent pour FICON8). Le tile 0 ne peut donc être utilisé comme overlay dans ce prototype.
- Aucun retournement, animation, encodage d'attributs ou masque indépendant de l'index couleur 0 dans ce prototype. Ajouter ces capacités seulement après mesure et avec évolution versionnée.
- La palette est **celle de l'écran AGA**, commune à toute la scène ; pas de changement de palette par cellule.

Le format privilégie la simplicité d'accès : les variantes compressées sur disque doivent être décompressées **une seule fois au chargement** vers cette structure brute, jamais en cours de rendu.

## 3. AGTM v1 — contrat binaire du prototype hôte (pas de banque AMOS implémentée)

Tous les entiers multi-octets sont **big-endian**. Les offsets ci-dessous sont relatifs au début des **données de la banque DATA AMOS**, pas à l'enveloppe fichier `AmBk`. Les données pourront être persistées par `Save/Load` AMOS lorsque l'enveloppe DATA et son comportement auront été testés.

| Offset hex | Taille | Type | Valeur / rôle |
|---|---:|---|---|
| `00` | 4 | ASCII | `AGTM` |
| `04` | 2 | U16 | Version = `1` |
| `06` | 2 | U16 | Taille d'en-tête = `64` |
| `08` | 2 | U16 | Nombre de colonnes = `1..256` |
| `0A` | 2 | U16 | Nombre de lignes = `1..256` |
| `0C` | 1 | U8 | Largeur tuile = `16` |
| `0D` | 1 | U8 | Hauteur tuile = `16` |
| `0E` | 1 | U8 | Nombre de couches = `1..4` |
| `0F` | 1 | U8 | Taille de l'index = `1` octet |
| `10` | 2 | U16 | Nombre de tuiles du tileset associé = `1..256` |
| `12` | 2 | U16 | Flags = `0` (réservé) |
| `14` | 4 | U32 | `rowStride` en octets = nombre de colonnes |
| `18` | 4 | U32 | `layerStride` en octets = colonnes × lignes |
| `1C` | 4 | U32 | `dataOffset` = `64` |
| `20` | 4 | U32 | `dataBytes` = `layerStride × layers` |
| `24..3F` | 28 | octets | Réservés = zéro |

La longueur totale exacte de la banque DATA AGTM est `64 + dataBytes`. Les octets suivants, s'il y en a, sont refusés par le prototype.

**Disposition des indices :** `offset = 64 + layer * layerStride + y * rowStride + x`, pour `x < cols`, `y < rows`, `layer < layers`.

Aucun numéro de banque AMOS n'est codé dans AGTM : le RPG Engine lie explicitement banque de carte et banque FICON8 lorsqu'il ouvre une scène. La banque FICON8 doit contenir au moins autant d'images que `tileCount`; chaque indice non vide doit être inférieur à `tileCount`. Pour une couche supérieure, le zéro est traité comme vide **avant** le test de présence graphique.

**Validation au chargement (une fois) :** signature, version, taille, profondeur/format FICON8, dimensions, multiplications de taille sans dépassement, réservation mémoire, plage des indices, longueur réelle et état/identité des banques. Sur erreur, aucune préparation partielle ni pointeur DMA périmé.

**Gestion des modifications :** l'édition d'une cellule change son octet en Fast et incrémente une révision runtime. Chaque page physique conserve sa propre révision et caméra ; si l'historique dirty est perdu, repaint complet de cette page. Aucun champ runtime dans le fichier AGTM.

## 4. Trois backends à mesurer, sans supposer le gagnant

| Backend | Parcours / données | Risques et intérêts |
|---|---|---|
| **A — CPU direct** | Un unique appel native M20 ; indices en Fast, FICON8 pré-validé ; boucle interne 68020 vers bitplanes Chip | Pas de setup Blitter par tuile, mais écritures CPU en Chip potentiellement coûteuses |
| **B — Blitter par lots** | Indices en Fast, images préparées en vraie Chip ; contrôles Safe une fois pour le lot, DMA synchronisée | Bande passante Chip et lancement de nombreux blits ; intérêt dépendant de l'alignement et de la profondeur |
| **C — Scrolling matériel futur** | Décor plus large que la fenêtre ; pointeurs/modulos bitplanes et décalage fin, puis bandes nouvelles | Potentiellement évite la copie du viewport ; exige un contrat matériel/Intuition/Copper sûr, distinct du moteur actuel |

**Ne pas inventer d'accès direct aux registres dans la Lib active.** Le backend C est une expérimentation distincte ; le système actuel possède un écran Intuition privé et des protections Safe/Disp. Le format AGTM ne dépend pas d'une technique de scrolling.

Un moteur à **tuiles pré-composées** peut devenir un quatrième cas : au chargement, fusionner hors frame les couches statiques employées conjointement, puis dessiner une seule couche opaque. Tester le compromis taille du tileset vs appels/données de rendu.

## 5. Budget théorique et limites

- Une tuile **16×16×8 bitplanes** non compressée = **256 octets**.
- Un tileset **256 tuiles** = **65 536 octets** de pixels, hors en-têtes/caches/masques ; idéalement la préparation DMA est faite une fois, hors boucle.
- Carte **32×32, 2 couches** = **2 048 octets** d'indices + 64 octets.
- Carte **200×200, 2 couches** = **80 000 octets** d'indices + 64 octets, de préférence en Fast.
- Un écran **320×256×8** = **81 920 octets** ; deux pages = **163 840 octets**, hors éventuels snapshots Bob, buffers, structures OS, atlas et Chip DMA.
- Vue **192×192** alignée : **12×12 = 144** cellules par couche ; vue **320×256** : **20×16 = 320** cellules par couche. Une bande neuve de 16 pixels de large à 192 de haut couvre environ **12** cellules au lieu de 144, avant prise en compte de la position exacte de la caméra.

**Aucun chiffre de FPS ni facteur d'accélération n'est établi.** Réduire les octets en mémoire, la quantité de blits et le temps complet par frame reste plus important que la compacité sur disque.

## 6. Protocole d'étude avant toute API AMOS publique

1. **Oracle hôte AGTM :** encodeur/décodeur bit-exact, test de longueur et indices invalides, couches et limites, round-trip ; raccordement au modèle M20 P0 sans modifier ses preuves historiques.
2. **Tests de composition :** carte neuve originale 32×32 pour RPG Engine M0, carte synthétique 200×200, 1/2 couches, tuiles opaques, overlays transparents et pen 0.
3. **Micro-benchmarks discriminants :** initialisation hors chrono ; boucles 144 et 320 tuiles, caméra alignée 0/16 et décalée 1/8 ; bande horizontale/verticale/diagonale ; edit d'une tuile ; bascule entre deux pages ; CPU vs Blitter, éventuellement 4/5/8 bitplanes dans une phase séparée.
4. **Benchmark frame complet :** DMA, fond, Bobs, Safe et `Aga Swap` explicite inclus ; aucun Wait VBL dans un micro-benchmark draw-only. Répétitions suffisantes pour dépasser `Timer`; WinUAE MC68020/14 MHz/JIT OFF, Runtime puis vrai Compiler, et matériel si disponible.
5. **Mesures :** ticks bruts, pixels exacts, tuiles/blits réellement exécutés, mémoire Chip/Fast avant/après, échecs Safe, intégrité de l'autre page et absence de fantôme.
6. **Décision après preuves :** figer le backend retenu et, si nécessaire, créer le format graphique AGTS versionné. Le format AGTM reste neutre et sérialisable.

**Gates :** spécification et prototypes hôtes = aucune Gate A/B/C/D. Les 9 tests Python ont passé localement ; native MC68020 (A), WinUAE interprété (B), vrai Compiler (C) et Amiga réel (D) restent indépendants.

## 7. Indépendance RPG Engine / licence

Ce contrat est une conception originale et générique, indépendante de tout projet tiers. Il ne reprend aucun code, aucune donnée ni aucune ressource externe. Les principes de cache, carte, caméra et scrolling sont spécifiés indépendamment. Les ressources et cartes de benchmark sont produites spécifiquement pour cette étude.

## 8. Questions à départager par benchmark, pas par hypothèse

- CPU 68020 Fast→Chip plus rapide que DMA Blitter Chip→Chip pour **16×16×8** en lots ?
- Représentation graphique des tuiles en ordre de plans ou scanlines entrelacées : quel coût de conversion/staging et quel comportement effectif du bitmap Intuition AGA ?
- L'index U8 suffit-il en pratique, ou le passage U16 est-il nécessaire dès la création de cartes ?
- Les overlays doivent-ils être précomposés dans le tileset plutôt que dessinés à chaque mise à jour ?
- Une future architecture de scrolling matériel compatible OS est-elle faisable sans compromettre la stabilité Safe/Disp et Bob ?

**Hypothèse de travail non validée :** explorer **AGTM brut U8 + tuiles 16×16 FICON8 + un futur renderer batch privé**, sans nouveau token aujourd'hui ; ne figer ni backend ni commande publique avant les mesures.

## 9. Contrat testable du codec hôte

- API du prototype **Python uniquement** : `AGTMMap(cols,rows,tile_count,layers)`, `encode_agtm`, `decode_agtm`, `with_cell`, `render_reference` ; **ce ne sont pas des commandes AMOS**.
- Le fond est opaque, y compris le pen 0. Sur les couches supérieures, indice de tuile 0 = vide et pen 0 = transparent.
- Les valeurs de cellules hors limites sont rejetées. Les cartes sont immutables dans le codec ; `with_cell` construit un nouvel objet, sans reproduire le mécanisme de révisions et de dirty rectangles du M20.
- Format canonique et strict : en-tête de 64 octets ; réservés = zéro ; aucun octet ajouté, padding ou pointeur mémoire ; offsets et tailles vérifiés exactement.
- `render_reference` est volontairement lent, **chunky 8 bits uniquement**. Le futur moteur devra produire les mêmes indices de couleur sans que cette référence prétende mesurer le débit CPU/Blitter.

Commande depuis la racine du dépôt :

```sh
python -B -m unittest discover -s tools/prototypes -p 'test_agtm_format_proto.py' -v
```

**9 tests hôtes PASS lors de l'exécution locale.** Aucun test WinUAE, AMOS Compiler ou Amiga physique n'a été effectué pour AGTM.

## 10. Questions de performance encore ouvertes

1. **Stride** : `rowStride=cols` garde la carte compacte, mais un futur moteur peut préparer les pointeurs de début de ligne hors boucle ; comparer avec un padding 16/32/puissance de deux **sans le figer dans AGTM**.
2. **Scrolling** : copier un fond intégral puis réparer les bandes peut transférer davantage d'octets qu'un dessin complet. Mesurer copie, tuiles, transparence, Safe/Disp et Blitter séparément.
3. **Couches** : comparer dessin direct de plusieurs couches, composition statique préparée et suppression des overlays vides ; une édition d'overlay doit recomposer son fond.
4. **Caméra** : déplacements de 1/8/16 pixels, diagonales, sauts, alternance des pages physiques, bordures de carte et cache invalide.
5. **Chip RAM** : mesurer pages, snapshots, atlas, caches de Bobs, masques, DMA et allocations OS ; les volumes théoriques ne sont pas un bilan de mémoire disponible.

La sérialisation de la **carte** ne dépend pas de la représentation **des pixels des tuiles**. Une variante U16, un masque autonome ou un backend de scrolling matériel nécessiteront une évolution explicite et mesurée de la spécification.

## 11. Mesures comparatives préliminaires (23/11/2026)

Le prototype de [rendu/scrolling hôte](../tools/prototypes/agtm_render_bench.py) a été mesuré en Python 3.13.5 / Linux x86-64, 5 passes intercalées par méthode, 5 rendus par passe, 6 scénarios. Avant chaque série, le rendu pixel oracle et les deux méthodes optimisées ont été comparés octet pour octet.

À 320×256, 2 couches, déplacement de caméra de 1 px, les médianes observées sont **3,115 ms pour la composition par segments de tuiles** et **0,238 ms pour copie du décor + bandes**, soit un rapport **×13,09 sur l'hôte uniquement**. Pour (+8,+8), **3,050 ms** contre **0,352 ms** (×8,67), et pour (+16,0), **3,379 ms** contre **0,404 ms** (×8,36).

**Ces chiffres ne mesurent ni n'estiment des performances MC68020/AGA** ; les transferts en Chip RAM, l'attente DMA, les bitplanes, les Bobs et le VBL pourraient modifier radicalement le résultat. La zone d'écran est quasi intégralement copiée, même si peu de pixels exigent une recomposition de tuiles.

Résultats complets, protocole, mesures brutes, hypothèses mémoire et futurs tests : [AGTM — benchmark hôte du 23/11/2026](AGTM_HOST_BENCHMARK_2026-11-23.md). **Aucun backend natif, aucune API AMOS ni aucun jalon M20 n'ont été lancés sur ces seuls résultats.**

## 12. Protocole de carte mutable et deux pages (étude hôte du 23/11/2026)

Le [prototype de carte mutable et scène double buffer](../tools/prototypes/agtm_dirty_scene_proto.py) sépare désormais les **octets AGTM sérialisés** de la **carte active en mémoire**. Les couches actives sont des tableaux contigus modifiables sans recopier la carte complète : une édition d'une cellule coûte O(1) hors rendu. Les changements sont journalisés par révision ; chaque page conserve sa propre caméra, sa propre révision et son propre décor avant composition des acteurs.

**Contrats candidats pour le futur moteur natif :**

1. **Révisions de page indépendantes** : les modifications reçues par une page ne sont pas considérées comme déjà présentées sur l'autre page.
2. **Fond propre** : le scrolling ne recopie jamais des pixels contenant des objets mobiles ; la restauration doit conserver l'ancienne surface correcte ou reconstituer le décor.
3. **Invalidation** : modifications de cellules et, dans une future API, génération du tileset / remplacement de banque doivent invalider explicitement les régions concernées.
4. **Historique borné** : le prototype conserve 128 éditions. Si une page a manqué une partie de l'historique, le rendu intégral remplace le rafraîchissement partiel.
5. **Prévalidation** : un refus ne doit pas présenter un back buffer incomplet ; aucun Swap implicite.
6. **Heuristique de bascule** : à déterminer par benchmarks natifs selon le coût réel des couches, masques, octets Chip transférés et nombre de rectangles.

L'étude a passé **27 tests hôtes** (14 premiers tests + 11 nouveaux tests de scène + 2 tests de benchmark), incluant 120 frames déterministes d'édition, animation et double buffering.

À **320×256, 2 couches, caméra +1 px**, les médianes Python donnent **3,108 ms complet / 0,248 ms incrémental** sans édition ; **3,304 / 0,363 ms** pour 16 éditions ; **3,330 / 0,975 ms** pour 64 éditions ; **3,551 / 1,932 ms** pour 128 éditions. Au-delà du journal, le prototype bascule automatiquement au redraw intégral. **Ce sont uniquement des résultats hôtes x86-64, sans preuve de gain MC68020/AGA.**

Rapport avec protocole, cas limites et échantillons bruts : [AGTM — scrolling dynamique, deux pages et modifications](AGTM_DIRTY_SCROLL_HOST_2026-11-23.md).

**Le contrat d'allocation réelle Chip/Fast, l'intégration avec les Bobs natifs et la stratégie de scrolling matériel restent à définir APRÈS M21. Aucun token ou binaire de l'extension n'est modifié par ces études.**

## 13. Premiers prototypes AMOS — essais WinUAE à réaliser

Deux sources **AMOS Professional autonomes** sont prêtes, sans aucune modification de la bibliothèque installable : [consignes et ressources](../examples/agtm_prototype/README.fr.md).

- [AGTM_BANK_ROUNDTRIP.asc](../examples/agtm_prototype/AGTM_BANK_ROUNDTRIP.asc) : banque DATA AGTM v1, indices zéro-based, sauvegarde `.ABK`, effacement, rechargement et contrôle exact des cellules. Cette sonde vérifie la compatibilité réelle du format en AMOS, indépendamment de l'écran AGA.
- [AGTM_TILE_BENCH.asc](../examples/agtm_prototype/AGTM_TILE_BENCH.asc) : moteur **provisoire construit avec les commandes AGA existantes**, une carte 22×16 stockée dans une banque DATA, quatre tuiles FICON8 16×16 et une vue 320×256. Comparaison du redessin intégral (320 icônes) avec `Aga Blit Copy` de 304×256 pixels + 16 tuiles découvertes. Deux passes A/B puis B/A ; `Aga C Block Capture` et comparaison **des 81 920 octets planaires** hors fenêtre chronométrée.
- Conversion explicite : **AGTM index 0..3 → FICON8 IconID 1..4** ; les données de carte ne contiennent jamais directement les identifiants FICON8.
- **Statut : PREFLIGHT AMOS STRICT PASS uniquement**, sans essai WinUAE ni compilation effective. Les 21 tests du préflight passent. Le test visuel et les journaux Runtime/Compiler sont à obtenir avant toute conclusion de vitesse native.

Ces prototypes sont **préliminaires** : ils ne constituent ni une commande native de tilemap, ni un bench du scrolling au pixel près, ni une preuve de performance pour deux couches ou les Bobs. Le chantier de développement natif AGTM/M20 reste planifié **après M21**.
