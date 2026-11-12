# M16 — AGAPIC v1 : images compressées en banque DATA / rendu CPU AGA

**État : P0 VALIDÉ sur modèle hôte/CI et chargement ABK sous AMOS/WinUAE (12/11/2026).** 432 contrôles ABK/roundtrips, 1 344 rendus planaires et 31 cas invalides ; [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43214342325). La capture utilisateur du chargement AGAPIC confirme `ABK FORMAT RESULT 1`, banque 10, 1 836 octets DATA, version 1, 64×40×4, masque/codec 1 et offsets 32/196/1 836. [Rapport de validation WinUAE](M16_AGAPIC_WINUAE_P0_PASS.md). Le rendu CPU n'a été testé que dans le modèle Python, **pas encore dans l'extension**.
Aucun token AP20 R45 ni dessin natif 68000 : la validation WinUAE concerne uniquement l'enveloppe ABK et la lecture de son en-tête.
**R44 v0.11.5 reste LAST_GOOD** : 49 commandes AP20, 27 460 octets.
Travail exclusivement sur la branche **main**.

## Objectif

Format alternatif aux IFF/ILBM, sans reproduire les banques Bob/Icon d'AMOS :
image indexée compressée dans une **banque DATA AMOS**, de préférence **Fast RAM**.
Le CPU devra lire cette banque, décompresser progressivement et écrire dans le
**back buffer AGA en Chip RAM**, sans Blitter et sans décompresser toute l'image
dans un tampon Chip. Deux modes : **opaque** et **transparent par masque 1 bit
indépendant**. Un pixel de couleur 0 peut être visible ; l'index 0 ne signifie
jamais automatiquement transparence.

Ce prototype utilise des groupes de **16 pixels planaires** (mots big-endian).
Pour chaque groupe : un WORD de masque si présent, puis 1 à 8 WORD de couleur,
plan 0 d'abord. Le bit 15 représente le pixel le plus à gauche.

## Format binaire intérieur AGAPIC v1

Toutes les valeurs multioctets sont **big-endian** ; les offsets sont relatifs
à l'origine de la zone DATA de la banque (AMOS Start(bank)).

| Offset | Taille | Champ | Valeur |
|---|---:|---|---|
| 0 | 6 | Magic | ASCII AGAPIC |
| 6 | 2 | Version | 1 |
| 8 | 2 | Flags | bit 0 = masque présent |
| 10 | 2 | Codec | 1 = RLE groupes planaires par ligne |
| 12 | 2 | Largeur | 1..4096 pixels |
| 14 | 2 | Hauteur | 1..4096 pixels |
| 16 | 2 | Profondeur | 1..8 bitplanes |
| 18 | 2 | Octets par groupe | 2 × (Depth + Masked) |
| 20 | 4 | Offset table | 32 |
| 24 | 4 | Offset flux | 32+4×(Height+1) |
| 28 | 4 | Longueur totale | taille exacte du payload |
| 32 | 4×(Height+1) | Table lignes | offsets absolus de début/fin par ligne |
| Flux | variable | Données | paquets RLE indépendants pour chaque ligne |

Codage RLE : octet 0..127 = 1..128 groupes littéraux, suivis de leurs données ;
octet 128..255 = 1..128 répétitions du groupe suivant (un seul exemplaire
stocké). Pour un groupe d'image non multiple de 16, les bits hors largeur sont
à zéro. Chaque ligne se termine exactement à son offset de fin.

Le décodeur rejette un paquet tronqué, une longueur dépassant la largeur,
des offsets non monotones ou incohérents, des données en trop, des flags
réservés et les bits de bourrage non nuls. Limites conservatrices hôte :
4 Mio de pixels et 16 Mio d'octets de payload. Pas de garantie d'une
mémoire libre équivalente sur Amiga.

### Enveloppe AMOS DATA (.abk)

L'ABK conserve l'en-tête natif AMOS : magic AmBk (4 octets), numéro banque
WORD (2), flags WORD (2 : 1=DATA/Fast souhaitée, 3=DATA/Chip), longueur
LONG = longueur payload+8 (4), nom ASCII AGAPIC suivi de deux espaces
(8), puis le payload. Soit **20 octets d'en-tête AmBk**.

Modèle fondé sur [AGAPAL R30](M13_AGAPAL_R30_PREVIEW.md), dont le
Save/Load a déjà été validé. Un flag DATA/Fast **ne prouve pas que la
banque chargée réside en Fast RAM**. Sur la capture actuelle, `List Bank` affiche `S: $40413010` (adresse de début) **sans indication F/C explicite** ; confirmer la nature mémoire via la configuration WinUAE ou Exec `TypeOfMem`. Ne pas identifier Fast seulement d'après `S`.
Après un Bank Swap ou Load, relire Start(bank) et Length(bank).

## Outils du prototype

- [Codec Python et modèle de dessin CPU planaire](../tools/m16_agapic.py) :
  compactage RLE, validation stricte, lecture et rendu par mots 16 bits.
- [Convertisseur PNG indexé vers ABK](../tools/m16_agapic_convert.py) :
  exige un PNG mode P ; Pillow est utilisé seulement pour lire les PNG.
  Accepte un masque PNG monochrome indépendant (--mask), un index transparent
  (--transparent-index) ou le tRNS PNG (--png-alpha). Pas de quantification
  RGBA automatique, pas de palette incluse dans AGAPIC.
- [Banque ABK témoin 64×40×4](../tests/design/M16_AGAPIC_SAMPLE_BANK10.abk) : 1 856 octets, SHA256 56443d5ed29527a21d043b845e70c545402648ef35fa590943cd62818499edaf ; [notice de test WinUAE](../tests/design/M16_AGAPIC_PREVIEW_README.md). L'ABK est produit déterministiquement par les scripts PC et son chargement dans AMOS a été confirmé par l'utilisateur (`ABK FORMAT RESULT 1`).
- [Générateur de banque exemple](../tools/m16_agapic_sample.py) :
  64×40×4 couleurs indexées avec masque indépendant, banque DATA numéro 10.
- [Tests de format et rendu de référence](../tools/test_m16_agapic.py) :
  cycle pack/unpack, ABK, clipping quatre côtés, X non aligné, modes
  opaque/transparence (dont index 0 visible), garde mémoire et corruption.
- [Test AMOS de lecture d'ABK](../tests/design/M16_AGAPIC_ABK_PREVIEW_01.asc) :
  Load, Start, Length, Peek$, Deek, Leek, List Bank. **Ne dessine rien**.

Commande de conversion hors Amiga :

    python tools/m16_agapic_convert.py image_indexee.png image.abk --bank 10 --depth 4 --mask masque_gris.png

La compression RLE simplifie le décodage 68000 et compresse les grands aplats. **Mesure de taille hôte (non temporelle) :** 320×256×8 opaque : 81 920 octets planaires, 5 412 octets AGAPIC sur une image uniforme ; échantillon complexe : 83 236 octets AGAPIC, donc légère expansion. Aucun FPS Amiga ne peut en être déduit.
Une image très détaillée/bruitée peut au contraire croître légèrement.
**Aucune vitesse ni cadence 50 FPS n'est revendiquée** à partir de tests PC.

## Rendu natif futur, proposition de contrat R45

**API proposée (NON LIVRÉE)** :

    _OK=Aga Image Draw(Start(bank),Length(bank),X,Y,Mode)

Mode 0 = opaque, y compris index 0 ; Mode 1 = masque 1 bit, exige une image
avec masque. Retour entier proposé : 1 si appel valide (y compris hors écran),
0 si refus **sans modifier les pixels**.

Le runtime natif devra :
1. Accepter seulement Start(bank)/Length(bank) d'une **vraie banque DATA
   AMOS vivante**, vérifier entête, flags, dimensions, offsets, profondeur
   écran et accès mémoire **avant** le premier mot dessiné.
2. Obtenir **exclusivement** le back buffer AGA privé ; contrôler Safe
   avant toute écriture, sans Swap ni VBL implicite.
3. Décompresser un **groupe 16 pixels** à la fois directement depuis
   la Fast/Chip RAM ; pour X non multiple de 16, le décaler en deux mots
   de destination, en bornant strictement chaque bitplane et BytesPerRow.
4. Fusionner les bits de destination par masque : (dest AND NOT mask)
   OR (src AND mask). En opaque, le masque est constitué de tous les pixels
   valides ; en transparent, il est encore filtré par le masque de l'image.
5. Rejeter les coordonnées et longueurs non signées/overflow, les données
   corrompues, les accès Chip illégaux, la profondeur différente de la source
   pour v1, ainsi que les captures d'anciennes banques après Bank Swap.
6. Tester 1/2/4/8 bitplanes, clipping quatre bords, X décalé, pixel index 0
   visible/invisible, double buffering, fermeture et stress répétitif.

**Séquence :** P0 format/outillage/ABK ; R45 rendu CPU natif et Gates A/B ;
puis R46+ optimisations après benchmark 68000 et 68020/030, éventuellement
atlas et images multiples. Un seul nouveau jeton AP20 par sous-version.

## Validation et limites

- **P0** : tests et modèle PC. Ce n'est **pas Gate A de l'extension**.
- **R45 Gate A (non engagée)** : tests CPU 68000 natifs, ABI AMOS, HUNK/AP20,
  Safe et mémoire, export source strict.
- **R45 Gate B (non engagée)** : AMOS interprété/WinUAE avec vraie banque,
  rendu opaque/masqué visible, clipping, Swap et fermeture.
- **Gates C et D** : AMOS Compiler / AGA physique, non testées.
- **R44 LAST_GOOD inchangée** ainsi que sa bibliothèque courante, son archive
  versionnée et tous les tests déjà validés.

Le chargement réel de l'ABK hôte via AMOS est **confirmé** ; la mise en image depuis les données compressées demeure **NON TESTÉE** côté Amiga. Le Blitter ne lit pas directement Fast RAM. [Contrat R45 proposé](M16_R45_IMAGE_DRAW_CONTRACT.md) ; ne pas confondre essai de chargement et Gate B du dessin.
