# M19 S1-P0 — Banque Sprite AGA AGSP v1 : format et banc hôte

**Date :** 22 novembre 2026  
**Décision utilisateur : contrat AGSP validé pour lancement du chantier.** Les images sont capturées depuis un écran AGA où un **IFF/ILBM indexé avec CMAP RGB24** a été chargé. Elles sont regroupées dans une **banque AMOS DATA multi-images AGSP**, analogue à AGBO sur le principe mais **incompatible au niveau binaire**. Aucun éditeur Sprite OCS ni banque Object OCS n'est nécessaire.

**Statut du jalon : CODE MODÈLE HÔTE + TESTS UNITAIRES (27 PASS locaux).** La capture WinUAE, le vrai `Save/Load` AMOS, le runtime Sprite, l'API AP20, l'allocateur Chip et l'arrêt DMA natif ne sont **pas encore implémentés ou qualifiés** par ces tests. **P2d et LAST_GOOD ne changent pas.**

Références :
- [Modèle de format](../tools/m19_s1_agsp_bank.py) : `empty_bank`, `put_capture`, `parse_payload`, `delete_image`, `set_hotspot`, `make_abk`, `parse_abk`, `s0_interleaved_image`.
- [27 tests hôtes](../tools/test_m19_s1_agsp_bank.py) : couleur, transparence, largeur, palette, écriture transactionnelle, corruption et enveloppe DATA.
- [Contrat API S1](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md), [feuille de route](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md), [source AGBO v1 historique](M19_P0A_ABK_FORMAT_2026-11-15.md).

## 1. Règles fonctionnelles retenues

1. L'utilisateur **charge un IFF indexé** sur l'écran AGA, puis **capture un rectangle**, éventuellement plusieurs images depuis une planche. Le `CMAP` donne **RGB8 par composante = RGB24**, pas un bitmap 24 plans. Le traitement utilise les pixels indexés réels et les valeurs RGB24 de la palette, sans conversion vers RGB4.
2. L'indice source `TransparentPen` est **explicite**. Seuls les pixels utilisant cet **indice exact** sont transparents. Un pixel opaque noir `$000000` reste opaque même si la palette transparente utilise la même valeur RGB.
3. Deux indices IFF opaques portant **exactement le même RGB24** sont fusionnés en une seule couleur locale. Les couleurs distinctes sont numérotées dans l'ordre de première apparition, indépendamment de l'indice IFF initial.
4. **S1 :** 16 pixels de largeur, 2 bitplanes, au plus **3 couleurs opaques + transparent**. 0 couleur opaque (image vide) est admise. **S2 préparatoire dans le modèle hôte uniquement :** largeurs 16/32/64, et jusqu'à **15 opaques + transparent**, 4 bitplanes si 4..15 couleurs ; cela exigera **2 canaux attachés**, non implémentés.
5. Si la capture dépasse le budget du mode (4 opaques en S1 ou 16 opaques en S2) : **refus clair, aucune quantification automatique ni destruction de l'ancienne image**. Si l'image compte plus de 15 couleurs opaques, conseiller un Bob AGA 256 couleurs plutôt qu'une conversion silencieuse.
6. Chaque image stocke **sa palette locale RGB24**, dimensions, plans, ID et hotspot. Le format est indépendant du numéro de canal matériel, de l'affectation des couleurs à la palette AGA globale, du buffer et de la durée de vie de l'IFF original.
7. Aucune modification des couleurs du décor n'est imposée au moment de la **capture**. Lors de l'**affichage**, la stratégie de palette Sprite doit être qualifiée avec le `BPLCON4`, le curseur Intuition, les bitplanes et le Copper. Une plage comme `240..255` reste une **cible de réservation à tester**, pas une garantie applicable à tous les écrans.

## 2. Enveloppe de fichier AMOS : AmBk DATA, pas OCS Sprite

Fichier sauvegardable **en intention** par `Save "SPRITES.ABK",10`, recharge `Load "SPRITES.ABK",10`, après implémentation de la banque native. Le suffixe `.ABK` désigne ici **l'enveloppe DATA générique**, **pas** le format des banques Sprite OCS. Aucune compatibilité OCS n'est revendiquée.

| Octets fichier | Taille | Valeur |
| --- | ---: | --- |
| 0 | 4 | ASCII `AmBk` |
| 4 | 2 | Numéro banque AMOS 5..65535, big-endian |
| 6 | 2 | Drapeaux DATA `1` ou `3` (préférence Chip seulement) |
| 8 | 4 | Taille du fichier moins 12, éventuellement bit 31 positionné par `Save` natif |
| 12 | 8 | Nom ASCII `AGASPRT ` |
| 20 | variable | Payload `AGSP` |

Le champ `length & $7FFFFFFF` doit correspondre **exactement** à `file_size - 12`. Le drapeau de banque `3` **ne prouve pas** une allocation Chip RAM. Le modèle hôte sait construire et vérifier cette enveloppe ; **aucune preuve de `Save/Load` sous WinUAE pour AGSP à ce stade.**

## 3. Payload AGSP v1 : en-tête 32 octets

Tout est **big-endian** ; sans RLE, sans offsets flottants et sans pointeurs mémoire enregistrés. La longueur maximale totale du payload est **16 Mio**.

| Offset | Taille | Champ |
| ---: | ---: | --- |
| 0 | 4 | ASCII `AGSP` |
| 4 | 2 | Version `1` |
| 6 | 2 | Flags banque `0` |
| 8 | 2 | Nombre d'images `0..4096` |
| 10 | 2 | Taille d'une entrée = `48` |
| 12 | 4 | Offset du répertoire = `32` |
| 16 | 4 | Offset du premier bloc = `32 + 48*N` |
| 20 | 4 | Taille totale du payload, exacte |
| 24 | 4 | Génération `uint32` non nulle |
| 28 | 4 | Réservé `0` |

Images triées par ID croissant, IDs **1..4096**, pas de doublon ; une modification réussie reconstruit le payload avant son remplacement et **incrémente la génération**. Refus si dépassement de taille ou compteur épuisé.

## 4. Entrée image : 48 octets et blocs contigus

| Offset relatif | Taille | Champ |
| ---: | ---: | --- |
| +0 | 2 | ID image 1..4096 |
| +2 | 2 | Largeur `16/32/64` |
| +4 | 2 | Hauteur `1..256` |
| +6 | 2 | Profondeur `2` ou `4` |
| +8 | 2 | Stride `width/8` octets/ligne/plan |
| +10 | 2 | Flags `0` |
| +12 | 4 | Offset pixels planaires |
| +16 | 4 | Longueur pixels = `stride*height*depth` |
| +20 | 4 | Offset palette locale RGB24, après les pixels |
| +24 | 4 | Longueur palette = **48 octets** |
| +28 | 2 | Hotspot X signé |
| +30 | 2 | Hotspot Y signé |
| +32 | 2 | Nombre de couleurs opaques réelles 0..3/15 |
| +34 | 2 | Indice transparent original dans le CMAP, 0..255 |
| +36, +40, +44 | 4 chacun | Réservés, **0** |

Pixels **plan-major** : plan 0 complet puis plan 1, etc., 16-bit WORD big-endian. Le bit 15 du premier WORD est le pixel de gauche. Les indices locaux **0=transparent, 1..3/15=opaques**, et les indices opaques réellement utilisés sont consécutifs, ordonnés selon leur première apparition. La palette locale est **16 triplets RGB8**, dont l'entrée 0 est `000000` (réservée à la transparence) ; toute entrée inutilisée est nulle. Le noir `000000` est autorisé parmi les indices **opaques**.

**Ordre mémoire** : header, répertoire trié, puis pour chaque image `pixels planaires` suivis des **48 octets RGB24**. Pas de trous, chevauchements, RLE, masque 1 bit séparé ou bytes additionnels. Ne pas traiter ce payload comme image DMA directement.

## 5. Construction de l'image DMA : séparation des propriétés

- Le payload AGSP peut résider en **Fast RAM** comme une banque AMOS normale : sa présence n'autorise **aucun accès DMA direct**.
- Lors de la préparation native, l'extension devra **allouer sa propre Chip RAM**, convertir si nécessaire `plane-major` vers **paires de mots interlacées par ligne**, préparer les mots de contrôle/terminateur et l'état `SimpleSprite`, puis acquérir le canal libre via `GetSprite(-1)`.
- Le modèle hôte `s0_interleaved_image(image)` vérifie uniquement la conversion simple **16 pixels, 2 plans** : pour 16x16, **4 octets contrôle + 64 octets lignes + 4 octets fin = 72 octets**. C'est **une maquette d'agencement**, pas une allocation DMA native.
- **Jamais** de `FreeMem` d'une image encore référencée par le Copper/DMA. L'ordre de `FreeSprite`, démontage du ViewPort/Copper et preuve du détachement restent à confirmer avant toute API native, puis à tester sous WinUAE et sur matériel réel.

## 6. API utilisateur retenue en intention, à valider à la tokenisation

Ces commandes **ne sont pas installées dans P2d** ; leurs formes exactes, les retours et l'ABI seront vérifiés avant de livrer un ASC exécutable :

| Commande candidate | Usage attendu |
| --- | --- |
| `Aga Sprite Bank N` | Sélectionner/créer une banque AMOS DATA **AGSP**, sans écraser une banque occupée d'un autre format |
| `Get AGA Sprite I,X1,Y1,X2,Y2,TransparentPen` | Capturer un rectangle de l'écran AGA dans l'image `I`, bornes de fin **inclusives**, nombre de couleurs validé |
| `Aga Sprite N,X,Y,I` | Créer/déplacer l'objet logique `N`, afficher l'image `I` ; **S1 limité à un seul objet actif** |
| `Aga Sprite Off N` | Cacher et détacher l'objet `N` sans effacer la banque AGSP |
| `Aga Sprite Bank Free N` | Libérer la préparation Chip interne de la banque après arrêt sûr, **sans effacer la banque AMOS** |

**Exemple d'ergonomie future (NON exécutable aujourd'hui)** :

~~~text
_OK=Aga Iff Load("Sprites.iff")
Aga Sprite Bank 10
Get AGA Sprite 1,0,0,15,15,0
Get AGA Sprite 2,16,0,31,15,0
Save "SPRITES.ABK",10

Load "SPRITES.ABK",10
Aga Sprite Bank 10
Aga Sprite 1,100,80,1
Aga Sprite Off 1
Aga Sprite Bank Free 10
~~~

Les commandes `Get AGA Sprite` et `Aga Sprite` nécessitent validation de signatures/paramètres AP20/Compiler, comme sur AGBO. Numéro de banque, ID d'image et numéro d'objet sont **trois identifiants distincts**.

## 7. Validation et prochaine tranche native

**Modèle hôte S1-P0** : `python -B -m unittest discover -s tools -p 'test_m19_s1_agsp_bank.py' -v` : **27 tests PASS locaux**, incluant couleurs, budget 3/15, largeur 16/32/64, remplissage des plans, données corrompues, persistance des IDs/Hotspot, écritures transactionnelles et enveloppe `AmBk`. CI dédiée : [m19-s1-agsp-host.yml](../.github/workflows/m19-s1-agsp-host.yml).

**Ce que ces tests ne démontrent pas** : compatibilité `Save/Load` native AMOS, capture depuis le véritable écran AGA/Double Buffer, affectation d'indices Sprite dans `BPLCON4`, possession OS, synchronisation DMA, absence de fuite mesurée, Compiler ou Amiga physique.

**Étape de développement suivante** : intégrer d'abord **banque AGSP + capture** depuis l'écran AGA à la source native MC68020 (puis tests AP20/ABI), **sans activation du DMA Sprite**, et tester des `Save/Load` réels. Ensuite, seulement après preuve des règles Copper/palette/retour/fermeture, intégrer `Aga Sprite` et `Off` sur une **candidate autorisée**. Ne pas toucher automatiquement aux artefacts `dist/`, à `LAST_GOOD`, à l'ASC Bob actif ou à la sonde S0d validée.
