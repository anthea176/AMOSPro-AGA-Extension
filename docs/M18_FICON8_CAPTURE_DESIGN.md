# M18 — Capture directe d'un Fast Icon 16×16 depuis l'écran AGA

**Statut : API PROPOSÉE pour une étape ultérieure de M18 ; NON implémentée, aucun token AP20, aucune Gate A/B/C.** Ajout à la demande explicite de l'auteur du 13/11/2026, en parallèle de l'étude du cache Chip dynamique.

## Objectif et API proposée

```amos
_OK=Aga F Icon Capture(Bank,IconID,X,Y)
```

La commande **met à jour un emplacement existant** de la banque DATA AMOS `FICON8  ` (créée par `Aga F Icon Bank Create`, R64), directement depuis un rectangle de **16×16 pixels de l'écran AGA privé**. La banque n'est pas recréée, n'est pas effacée et reste sauvegardable avec `Save` / `Load` ABK AMOS. Le travail est effectué au CPU ; il ne crée pas de `FICHIP8`.

| Argument | Proposition |
|---|---|
| `Bank` | Banque DATA `FICON8  ` existante, numéro 5…65535, **sans la remplacer** |
| `IconID` | Index d'icône **1…Count** |
| `X,Y` | Coin supérieur gauche du rectangle à prélever, coordonnées pixel entières |
| Retour | **1** : 288 octets du slot mis à jour ; **0** : refus sans toucher à la banque |

### Quelle surface capturer ?

**Première version proposée : le back buffer AGA inactif**, comme `Aga Image Capture` (M16/R53). Il s'agit du buffer dans lequel on prépare les dessins avant `Aga Swap` — **pas automatiquement du front buffer actuellement visible**. Le nom de la commande ne doit pas laisser supposer une capture du Workbench ou d'un écran AmigaOS quelconque. Un éventuel paramètre `Front/Back` sera étudié séparément, et n'est **pas validé** ici.

La profondeur doit être 8 plans (256 indices). La zone **doit être entièrement à l'intérieur de l'écran** : refus si X/Y négatifs ou si X+16 ou Y+16 dépassent les dimensions ; **pas de clipping silencieux**. Rejeter si écran privé absent/fermé ou si ses plans, son pitch ou sa mémoire sont invalides.

### Indices, transparence et format

Le moteur de capture lit les **indices matériels 0…255 de chaque pixel** en parcourant les 8 bitplanes du bitmap, sans convertir en RVB et sans modifier la palette. Les 16 lignes du slot `FICON8` utilisent le format déjà validé par `Aga F Icon` :

- **18 octets/ligne** = 1 mot de **masque de préservation** + 8 mots de couleur planar ;
- bit 15 = pixel X0, bit 0 = pixel X15 ;
- masque `1` pour un pixel d'index **0**, `0` sinon, soit `Preserve = NOT(Plane0 OR ... OR Plane7)` ;
- **288 octets exactement** écrits à l'emplacement `IconID`.

Conséquence importante : **l'index 0 est transparent uniquement lorsque l'icône est dessinée en mode masqué** (`Aga F Icon(...,1)`). En mode opaque (`Mode=0`), l'index 0 est dessiné. `FICON8` **ne conserve pas de masque alpha indépendant** : une couleur 0 explicitement opaque ne peut pas rester opaque *en mode masqué*, comme dans le format AGAPIC. Cette limite doit figurer dans la notice.

### Sécurité/ABI et comportements exclus

- Vérifier d'abord le numéro, le type DATA, le nom `FICON8  `, l'en-tête, les dimensions, `Count`, les bornes du slot, les droits d'accès mémoire (notamment dernier octet) et la surface AGA, **avant toute écriture**.
- Protéger contre dépassement 32 bits, lecture hors ligne lors d'un X non aligné sur 16, erreur de pointeur de plan, screen fermé et retour d'acquisition du buffer non prêt. Lire avec les garanties mémoire et de disponibilité du back buffer utilisées par les API M16/R53, sans créer de dépendance à AMCAF.
- Retour `0` **sans modifier aucune banque**, écran, palette ou tampon, pour tout échec détectable. Une implémentation peut préparer localement un slot entier avant de le publier, selon la vérification de capacité de pile/mémoire. Aucune allocation persistante ni ancien slot d'une autre icône modifié.
- Ne pas déclencher implicitement `Aga Swap`, `Aga Wait Vbl`, déplacement de banque, DMA Blitter, sauvegarde disque, effacement ou rafraîchissement `FICHIP8`.
- **Après capture, un slot `FICHIP8` déjà pré-stagé est périmé** : l'utilisateur doit explicitement ré-exécuter `Aga F Chip Stage` avant `Aga F Blit`. Une future gestion de cache automatique devra traiter l'invalidation.

### Différence avec les commandes existantes

| Commande | Source | Destination |
|---|---|---|
| `Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)` | Back buffer AGA | **Nouvelle banque AGAPIC RLE** (et masque indépendant optionnel) |
| `Aga F Icon Bank Put(DestBank,IconID,PixelBank,ByteOffset)` | Banque DATA de **256 indices chunky** | Slot 16×16 **FICON8** existant |
| **`Aga F Icon Capture(Bank,IconID,X,Y)` (PROPOSÉE)** | **Back buffer AGA directement, 8 plans** | Slot 16×16 **FICON8** existant, sans intermédiaire chunky |

Une capture de l'écran visible/Workbench, des icônes autres que 16×16 ou une profondeur inférieure à 8 plans sont hors périmètre.

## Test requis avant toute validation

1. **Gate A CPU/ABI réelle** : cas alignés/non alignés (X=0,1,7,15,16, etc.), bords droit/bas exacts, refus de tous les dépassements, vérification des huit plans et du masque ligne par ligne, slot et banques voisins intacts ; disposition interpréteur et Compiler V2 simulée.
2. **Gate B WinUAE en AMOS interprété** : dessiner un motif AGA 256 couleurs dans le **back buffer**, capturer le carré, changer le fond et redessiner avec `Aga F Icon` en opaque/masqué, vérifier X/Y à 1 pixel, `Save / Erase / Load` ABK, résultat et rendu visuel, retour mémoire identique après nettoyage.
3. **Gate C Compiler** : un seul passage manuel final pour **l'ensemble de M18**, pas de test Compiler prématuré ; **Gate D** séparée sur Amiga physique.

**Prérequis** : conserver la R65 (Gates A/B interprétée PASS) comme base actuelle ; protéger R63 `LAST_GOOD`. Contrat public et signature à valider avant code natif. Ne pas attribuer le numéro de révision R67 avant clôture du périmètre R66.

Références : [rapport de validation R65](M18_R65_FICON8_PUT_WINUAE_GATE_B_2026-11-13.md) · [capture AGAPIC M16](M16_AGAPIC_CAPTURE_DESIGN.md) · [format FICON8](M18_FICON16_SOURCE_P1.md) · [règles](../EXTENSION_SOURCE_RULES.md).
