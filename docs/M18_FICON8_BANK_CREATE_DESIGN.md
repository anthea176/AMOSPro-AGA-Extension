# M18 — Proposition R64 : créer une banque Fast Icon depuis AMOS

**Contrat approuvé par l'auteur le 13/11/2026. R64 implémentée : Gate A 68000 PASS, 42 tests ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43440810232)). Gate B WinUAE NON TESTÉE ; Compiler C manuel en fin M18, D physique non testé.**

- Dépôt : `anthea176/AMOSPro-AGA-Extension`, branche `main` exclusivement.
- Référence installable protégée : R63 v0.13.8, `LAST_GOOD`, 38 736 octets, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`.
- Gates R63 : A CPU/CI et B AMOS interprété/WinUAE PASS ; conformité pixel visuelle en attente ; Compiler C manuelle **une seule fois à la fin de M18**. R63 reste inchangée pendant l'étude.

## 1. Besoin

Permettre à un programme AMOS de **créer directement une banque source d'icônes `FICON8  `** au lieu de dépendre d'un fichier ABK fabriqué sur PC, et sans devoir réserver manuellement une banque de données au préalable. L'initialisation est distincte du remplissage des icônes et de la création du cache Chip `FICHIP8 `.

## 2. API approuvée par l'auteur

```amos
_OK=Aga F Icon Bank Create(10,32)
```

Nom public approuvé : `Aga F Icon Bank Create` (**fonction entière**).

| Élément | Proposition |
|---|---|
| `Bank` | Numéro de banque AMOS de **5 à 65535** ; libre au moment de l'appel |
| `Count` | **4 à 4096** emplacements (mêmes bornes que le moteur `Aga F Icon` R61/R63) |
| Retour | `1` : banque créée et entièrement initialisée ; `0` : échec, sans écraser d'autres banques |
| Mémoire | DATA permanente, **Fast RAM privilégiée**, repli Chip possible selon AMOS ; aucune promesse de placement réel |
| Durée de vie | Appartient au gestionnaire de banques AMOS ; `Erase Bank` et `Save/Load` standards ; indépendante de `Aga Swap` et des écrans privés |
| Effets affichage | Aucun dessin, aucune palette modifiée, aucun `Swap`, aucun VBL implicite |
| Coût | Initialisation synchrone en temps proportionnel au nombre de slots ; aucun DMA Blitter |

**Le choix de `Create` plutôt que `Init` est intentionnel** : `Aga Palette Bank Init(Start(bank),N)` exige une réservation préalable, tandis que cette nouvelle fonction devra réaliser elle-même l'allocation AMOS.

## 3. Format binaire existant — pas de nouveau conteneur

Utiliser **strictement** le format validé `FICON8  ` déjà lu par `Aga F Icon`. Il est différent d'AGAPIC et des banques Icon classiques.

En-tête interne de 12 octets (big-endian) :

| Offset | Type | Contenu |
|---:|---|---|
| 0 | LONG | taille totale `12 + Count × 288` |
| 4 | WORD | `Count` |
| 6 | WORD | largeur : `16` |
| 8 | WORD | hauteur : `16` |
| 10 | WORD | profondeur : `8` bitplanes |

Chaque emplacement contient 16 lignes de 18 octets : **un WORD de masque de préservation** suivi de **8 WORD de données planaires**. Identifiants d'icônes **1 à Count**.

**État initial canonique obligatoire** pour chaque ligne de chaque icône vide :
- `PreserveMask = $FFFF` : tous les pixels sont de couleur zéro, donc préservés en mode transparent.
- `Plane0…Plane7 = $0000`.
- Résultat attendu : `Aga F Icon(Bank,IconID,X,Y,1)` ne modifie aucun pixel ; en mode 0, elle peut dessiner du noir/index zéro.
- **Ne pas simplement mettre 288 octets à zéro** : cela produirait un masque non canonique, rejeté par le moteur actuel.

Taille de données : `12 + 288 × Count` ; fichier ABK AMOS standard : **20 octets d'enveloppe en plus**. Exemples :

| Count | Payload DATA | Fichier ABK (hors alignements RAM) |
|---:|---:|---:|
| 4 | 1 164 o | 1 184 o |
| 32 | 9 228 o | 9 248 o |
| 256 | 73 740 o | 73 760 o |
| 4096 | 1 179 660 o | 1 179 680 o |

La taille mémoire réelle inclura les métadonnées/alignements de l'allocateur AMOS. Le fichier sera utilisable par `Save "Fichier.abk",Bank` et `Load "Fichier.abk",Bank` si les tests WinUAE le confirment.

## 4. Gestion AMOS et garanties de sécurité

Les routines principales sont **déjà auditées et utilisées par `Aga Image Capture`** (R53, Gates A/B/C PASS dans le scénario historique) :

- `Bnk.GetAdr` : repérer une collision, y compris si le numéro contient une banque d'un autre type.
- `Bnk.Reserve` : allouer la banque DATA (flags AMOS privilégiant Fast) avec nom exact `FICON8  ` et taille exacte. **Attention : cette routine peut remplacer une banque occupée** ; vérifier l'absence de collision **avant** tout appel et recontrôler juste avant l'allocation.
- `Bnk.Change` : notifier le gestionnaire des banques après initialisation complète.
- `Bnk.Eff` : effacer seulement **la nouvelle banque créée** si une erreur intervient après réservation ; ne jamais toucher à une banque antérieure.

Les indices AP20 doivent provenir de `amos_main_abi.main_index` et de la fixture source épinglée, **jamais** des anciens numéros erronés R47. Préserver le contrat de registre/pile (consommation des arguments sur A3, résultat D3, D2=0).

Exigences : refuser paramètres invalides, banque occupée, allocation impossible, débordement arithmétique, mauvais pointeur ou échec en cours d'initialisation. **Succès uniquement lorsque tous les slots et l'en-tête sont prêts.** Aucune variable globale ni pointeur persistant vers la banque ; celle-ci peut être déplacée par AMOS.

## 5. Périmètre volontairement limité

Cette commande **n'importe aucune image**, ne capture aucun pixel, ne manipule pas `AGAPIC`, ne crée pas `FICHIP8` et ne fait aucun staging Fast→Chip. Les commandes ultérieures feront l'objet de **contrats indépendants** :

1. Remplissage d'un slot `FICON8` depuis une source définie ; gérer explicitement la transparence index zéro, incompatible avec certains masques indépendants AGAPIC.
2. Création/rafraîchissement d'un cache `FICHIP8` réellement en Chip avec marqueur de validité `0 → copie complète → 1` et contrôle `MEMF_CHIP`.
3. Benchmarks CPU vs Blitter incluant réellement le coût du staging.

## 6. Protocole : Gate A PASS, Gate B à exécuter

**Gate A CPU/CI PASS, 42 cas natifs M68000** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43440810232)) : cas limites (4/4096 slots), allocations et collisions simulées, requêtes invalides, contrôle des masques/plans vides, format et taille, intégrité des banques existantes, nettoyage, ABI et dispositions interpréteur/Compiler V2 simulées. Le builder R64 est déterministe et la nouvelle routine occupe 312 octets. Les simulations ne prouvent pas la Gate B/C WinUAE.

**Gate B AMOS interprété/WinUAE :** un seul ASC actif, création de la banque 10, refus de doublon sans destruction, test de slots vides opaque/transparent, `Save/Erase/Load` ABK, contrôle de `Start`/taille/nom après rechargement, absence de fuite Fast/Chip et conservation de l'écran/palette. Ne pas déduire de ces retours l'exactitude du rendu sans vérification graphique.

**Gate C :** un **unique** essai manuel Compiler sous WinUAE à la fin de M18, avec l'ensemble des fonctions finalisées ; Gate D physique seulement si possible.

## 7. Décision approuvée et implémentation R64

**Signature et paramètres approuvés explicitement.** Candidate R64 v0.13.9 : 39 100 octets, SHA256 `4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c`, 57 commandes / 64 AP20, routine nouvelle de 312 octets. [42 tests natifs Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43440810232). **Ne pas promouvoir sans validation WinUAE B et décision distincte de l'auteur.**

Références :
- [Format et modèles FICON8](../tools/m18_ficon16_model.py)
- [ABK source R61](../tools/m18_ficon16_abk.py)
- [Rendu AP20 existant](../tools/m18_ficon_ap20_emit.py)
- [ABI d'allocation validée R53](M16_MAIN_LINKAGE_FIX.md)
- [Émetteur capture avec services de banques](../tools/m16_capture_emit.py)
- [Politique de validation](../EXTENSION_SOURCE_RULES.md)
