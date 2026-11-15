# M19 P0a — Format de banque Bob AGA multi-images (base R88)

**État : MODÈLE HÔTE IMPLÉMENTÉ ET TESTÉ ; EXTENSION NATIVE NON MODIFIÉE.**

- Référence technique figée : R88 v0.13.33, commit `7c575a02087d550611b8e966a7708b5f6a8c4b71`.
- Contrat fonctionnel : `docs/M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md` et `EXTENSION_SOURCE_RULES.md`.
- Source du format et validations : `tools/m19_p0a_multi_bob_abk.py` et `tools/test_m19_p0a_multi_bob_abk.py`.
- N'utiliser aucun code, exemple, binaire ou banc R89/R90 dans ce chantier.
- R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste protégée. Ce module ne modifie ni `dist`, ni `tests/current`, ni une banque WinUAE existante.

## Enveloppe AMOS `AmBk` (20 octets)

Un fichier complet contient l'enveloppe `>4sHHI8s` big-endian (`AmBk`, numéro de banque, drapeaux DATA 1/3, longueur du payload + 8, nom ASCII `AGABOBS `), suivie directement du payload. La longueur native du fichier est `20 + payload_size` ; le champ longueur vaut `file_size - 12` conformément aux enveloppes AGAPIC R88. Le drapeau 3 n'est qu'une **préférence Chip** : `Load` ne garantit pas la résidence Chip.

## Payload `AGBO` v1 (32 octets d'en-tête, 40 octets par image)

Tout est **big-endian**, aligné au moins sur 2 octets, sans compression et sans palette privée. Images ordonnées par identifiant croissant, identifiants **1..4096**, zéro image autorisée. Un nouveau payload remplace intégralement l'ancien seulement une fois reconstruit et validé.

| Offset | Taille | Champ |
|---|---:|---|
| 0 | 4 | `AGBO` |
| 4 | 2 | Version `1` |
| 6 | 2 | Flags banque : `0` |
| 8 | 2 | Nombre d'images, 0..4096 |
| 10 | 2 | Taille d'une entrée : `40` |
| 12 | 4 | Offset répertoire : `32` |
| 16 | 4 | Offset pixels : `32 + 40*N` |
| 20 | 4 | Taille totale du payload (exacte) |
| 24 | 4 | Génération : uint32 non nulle, incrémentée à chaque édition |
| 28 | 4 | Réservé : `0` |

Chaque entrée de **40 octets** :

| Offset entrée | Taille | Champ |
|---|---:|---|
| +0 | 2 | ID image, 1..4096 |
| +2 | 2 | Largeur en pixels, 1..4096 |
| +4 | 2 | Hauteur en pixels, 1..4096 |
| +6 | 2 | Profondeur, 1..8 |
| +8 | 2 | Stride par ligne et plan : `2*ceil(width/16)` |
| +10 | 2 | Flags image : bit 0 = masque présent, autres bits = 0 |
| +12 | 4 | Offset de la première couleur planaire |
| +16 | 4 | Longueur totale des bitplanes : `stride*height*depth` |
| +20 | 4 | Offset du masque indépendant, `0` si absent |
| +24 | 4 | Longueur du masque : `stride*height` ou `0` |
| +28 | 2 | Hotspot X signé (réservé pour P1, initialement 0) |
| +30 | 2 | Hotspot Y signé (réservé pour P1, initialement 0) |
| +32 | 4 | Réservé : `0` |
| +36 | 4 | Réservé : `0` |

**Données :** successivement pour chaque image, bitplanes **plan-major** (toutes les lignes du plan 0, puis du plan 1, etc.), puis masque 1 bit (si présent). Dans chaque mot 16 bits, bit 15 = pixel X0. Tout pixel hors largeur dans le dernier mot est **zéro**, sur tous les plans et le masque. Le masque porte `1=visible / 0=transparent`, indépendamment de la valeur d'index de couleur. **Une image sans masque est opaque, y compris pour la couleur zéro.** Offset et taille de chaque bloc doivent être contigus, sans chevauchement, trou ni données finales inutilisées.

## Limites et comportement

- Payload de 32 octets à 16 Mio inclus ; jusqu'à 4 Mio de pixels par image, sous la limite globale.
- Format strict : rejette en-têtes inconnus, mauvais flags, dimensions ou offsets, dépassements, IDs répétés, padding non nul et tailles incohérentes avant exposition des données.
- `put_image` ajoute ou remplace une seule image, conserve toutes les autres, reconstruit un nouveau payload ; refus sans altération du payload initial.
- `make_mask` calcule le masque 1 bit pour **un index transparent explicite** ; `no_mask` rend toute l'image opaque. Ces opérations du modèle anticipent P0b mais **n'ajoutent aucune commande à la bibliothèque**.
- `make_abk` / `parse_abk` vérifient uniquement un aller-retour **fichier hôte** `AmBk`. Ils ne démontrent pas `AMOS Save/Load` sous WinUAE et ne prouvent pas la mémoire Chip accessible au DMA.
- Ne pas confondre le format `AGBO` avec AGAPIC v1/v2 RLE, AGPC 16x16x8 expérimental ou la banque Object OCS.

## Contrôles effectués

`python -B tools/test_m19_p0a_multi_bob_abk.py` (à la racine du dépôt) : **11 scénarios unitaires PASS localement**, comprenant des itérations sur largeurs **1, 17, 31, 32 et 37**, profondeurs **1/4/8**, bitplanes, masques indépendants, couleurs zéro opaques, remplacement d'image, ABK, corruption du répertoire et refus sans mutation. Les tests utilisent un **modèle Python**, pas des instructions 68020.

## Ce qui bloque encore les API natives P0a

1. Confirmer le mécanisme exact de **croissance/remplacement non destructif d'une banque AMOS**. L'appel historique `Bnk.Reserve` peut écraser une banque occupée : impossible de l'utiliser aveuglément pour ajouter/remplacer une image sans risque de perte. Ne pas imposer une banque temporaire numérotée à l'auteur.
2. Implémenter `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2` à partir des unités **R88**, audit des appels `GetP`/`Rjsr`, des stubs AP20 et du back buffer/Safe. Les bornes de `Get AGA Bob` sont **inclusives** ; ne pas reprendre `Screen Copy`.
3. Ajouter un banc ASC unique dans `tests/current/` **uniquement après vérification** du binaire intégrant ces commandes. Aucun exemple fictif ne sera publié comme exécutable sous R88.
4. Gate A native (CPU 68020, AP20 et Compiler simulé) sur le **binaire exact**, puis Gate B WinUAE interprété/Runtime et Gate C AMOS Compiler réel, chacune avec leurs journaux. Aucune Gate B/C déduite du modèle hôte.

**Verdict P0a présent : format et outils hôte testés ; binaire R88 et `LAST_GOOD` inchangés.**
