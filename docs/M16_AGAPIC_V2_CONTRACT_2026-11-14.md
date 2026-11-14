# AGAPIC v2 + API Bank palettes — contrat P0 (14/11/2026)

**Décisions auteur validées, implémentation native NON LIVRÉE.** Ce document
décrit la conception retenue et les contrôles hôte. Une validation de format
Python ne vaut ni Gate A native, ni Gate B WinUAE, ni Gate C AMOS Compiler.

Références : [règles](../EXTENSION_SOURCE_RULES.md),
[AGAPIC v1](M16_AGAPIC_FORMAT_DESIGN.md),
[AGAPAL](M13_AGAPAL_R30_PREVIEW.md),
[R54, résolution de banque](M16_R54_BANK_NUMBER.md),
[roadmap](ROADMAP.md).

## Formats conservés

| Banque | Contenu | Palette | ModeID |
|---|---|---|---|
| AGAPIC v1 | Image planaire RLE, masque éventuel | Absente | Absent |
| AGAPIC v2 | Même RLE, masque éventuel | **RGB24 obligatoire et complète** | **U32 obligatoire, strict** |
| AGAPAL v1 | 1..256 emplacements de palettes | Une palette par emplacement, partielle autorisée | Absent |

Tous les formats anciens restent lisibles par leurs fonctions existantes.
Une ancienne R81 ne connaît **pas** les nouvelles banques AGAPIC v2.

### AGAPIC v2 : contrat binaire exact

Le préfixe v1 **32 octets**, `struct >6s7H3I`, ne change pas de disposition.
`Version=2`, `Flags` bit 0 = masque et bit 1 = palette obligatoire.
Donc `Flags=2` ou `3` seulement. `Codec=1` RLE planaire par lignes;
`GroupBytes=2*(Depth+Masked)`, `Depth=1..8`, largeur/hauteur `1..4096`,
`Width*Height<=4 Mi` et `TotalLength<=16 MiB`. Offsets big-endian relatifs
au **début du payload** et non au fichier `.abk`.

Extension fixe de 32 octets à l'offset `$20`, `struct >IHHIII3I` :

| Offset | Type | Champ | Contrainte |
|---|---|---|---|
| `$20` | U32 | DisplayModeID | Obligatoire ; différent de 0 et $FFFFFFFF |
| `$24` | U16 | PaletteCount | Exactement `2^Depth` |
| `$26` | U16 | PixelFormat | `1` : indexé planaire |
| `$28` | U32 | PaletteOffset | `64` |
| `$2C` | U32 | PaletteBytes | `3*(2^Depth)` |
| `$30` | U32 | HeaderBytes | `64` |
| `$34`, `$38`, `$3C` | 3 × U32 | Reserved | Tous zéro |

Palette à l'offset 64, `R,G,B` (8 bits/canal), complète. La table commence
à `ALIGN4(64+PaletteBytes)`, avec 0..3 octets de bourrage **nuls**,
contient `Height+1` offsets U32, puis le flux RLE v1 **inchangé**.
`StreamOffset=TableOffset+4*(Height+1)`, première position de ligne =
`StreamOffset`, dernière = `TotalLength`. Les paquets RLE et le masque
sont validés strictement : pas d'octet supplémentaire, pas de paquet
débordant, ni de bit non nul après la largeur de l'image.

En dessin v2, comparer le ModeID à celui **effectivement utilisé par
l'écran Intuition AGA privé**, en plus de la profondeur et du format.
Aucun changement de mode, aucune application de palette, aucun Swap
implicites. La source exacte et l'ABI de lecture du ModeID système sont
à vérifier avant le code natif. Mode différent -> retour 0 et zéro écriture
dans l'écran. En v1, seul le contrôle historique de profondeur s'applique.

## API Bank — quatre nouvelles fonctions, pas cinq

**Signatures existantes avec** `Start(B)` **inchangées.**

| Nouvelle commande (proposée pour la candidate native) | AGAPAL v1 | AGAPIC v2 | AGAPIC v1 |
|---|---|---|---|
| `Aga Bank Palette Init(B,N)` | Initialisation des N emplacements dans une banque DATA déjà réservée | Refus | Refus |
| `Aga Bank Palette Capture(B,I)` | Capture dans l'emplacement I | Refus | Refus |
| `Aga Bank Palette Apply(B,I)` | Application de l'emplacement I | Palette embarquée, **I=0 exclusivement** | Refus |
| `Aga Bank Palette Fade(B,I,VBL)` | Fondu vers l'emplacement I | Palette embarquée, **I=0 exclusivement** | Refus |

`B` = numéro de banque DATA AMOS existante 5..65535, résolu à chaque
appel par le mécanisme **`Rjsr Bnk.GetAdr` #797** éprouvé depuis R54.
`N` = 1..256 emplacements AGAPAL ; `I` = index AGAPAL 0..N-1 ou
strictement 0 pour AGAPIC v2 ; `VBL` = 1..255 pour un fade bloquant.

`Init` **ne crée ni ne réserve** de banque ; la taille DATA AGAPAL reste
`16+776*N`. Capture n'accepte qu'AGAPAL. Les autres opérations
rejettent la mauvaise signature, la mauvaise version, la banque absente,
le mauvais index, une palette vide/incompatible et les données corrompues,
sans changer l'écran. `Apply` ne provoque pas de VBL ; `Fade` n'écrit
que les couleurs et reste bloquant pour la durée demandée, conformément
aux moteurs R32/R33. Pas de dessinateur/palette automatique.
Les quatre anciennes APIs continuent à lire **AGAPAL uniquement**.

### Architecture à privilégier

- **Init/Capture** : wrappers courts autour des routines qualifiées ;
  aucune duplication des moteurs.
- **Apply/Fade** : dispatch sur la signature AGAPAL ou AGAPIC, extraction
  validée du pointeur RGB24 et du nombre de couleurs, puis réutilisation
  du chemin graphique `LoadRGB32` / `GetRGB32` / `WaitTOF` existant.
  **Ne jamais** interpréter une AGAPIC comme une structure AGAPAL et ne
  pas transformer silencieusement la banque source.
- **Image Draw / Bank Image Draw / Image Region** : conservation de l'API
  et du comportement v1 ; route v2 vers la validation d'en-tête, ModeID
  réel et même moteur RLE/masque/painter 68020. Pas de staging intégral Chip.
- Toute nouvelle routine 020 doit être précédée d'un garde CPU sûr sur
  68000/68010; tester ABI, D2/D3/A3, `Safe`, canaries, relocalisation,
  bancs invalides et fermeture. Une seule candidate `dist/AMOSPro_AGA.Lib`,
  un seul ASC actif `tests/current/` ; protéger `LAST_GOOD`.

## Attention à la limite 16 bits AP20 / Compiler V2

**Mesure du vrai fichier R81 sur `main` (14/11/2026)** :
`dist/AMOSPro_AGA.Lib` = 59 972 octets au total, dont **57 034 octets**
pour le dernier segment AP20 V2 (**dispatcher 34 octets compris**).
Le pont Compiler V2 a un plafond de **65 534 octets**. Il ne reste
donc que **8 500 octets**, soit environ 13 %.

La portée signée d'un `BSR.W` est ±32 768 octets. Des wrappers ajoutés
en queue ne pourront pas forcément joindre les premières routines AGAPAL
avec ce branchement. Un appel PC-relatif **long MC68020** est une piste
à tester sur CPU et Compiler, mais **ne supprime absolument pas** le plafond
de 65 534 octets. Si le budget est dépassé, ne pas forcer l'encodage
16 bits : il faudra qualifier une nouvelle architecture Compiler
multi-unités avant tout ajout.

Précontrôle indépendant :
`python tools/aga_compiler_capacity.py dist/AMOSPro_AGA.Lib --assert-r81`
et `python tools/test_aga_compiler_capacity.py`.
À chaque candidate, remplacer l'option `--assert-r81` par une prévision
`--planned-bytes N` si nécessaire. La protection stricte doit aussi
demeurer dans le constructeur `wrap_native_ap20_v2`.

## Jalons et preuves

**P0 hôte** : `tools/m16_agapic_v2.py` et
`tools/test_m16_agapic_v2.py`, qui réutilisent le codec v1, vérifient
168 allers-retours v1/v2, l'identité du flux RLE, palette obligatoire,
ModeID strict, AGAPAL partiel et rejets. **Ce modèle ne modifie pas
l'extension installable**.

**P1 natif** : lecture/dessin v2, sondage ModeID AmigaOS, palette via Apply/Fade,
quatre tokens, contrôle de capacité final et liens 020 : **NON TESTÉ**.
**Gate B** WinUAE interprété avec ABK réels, 4/8 plans, masques et
journal RAM : **NON TESTÉE**. **Gate C** AMOS Compiler, un test final après
les validations interprétées : **NON TESTÉE**. **Gate D** Amiga AGA
physique : **NON TESTÉE**. Ne pas qualifier ni promouvoir R82 avant
ces preuves et l'autorisation explicite de l'auteur.

R81 v0.13.26 demeure **LAST_GOOD** intacte.
