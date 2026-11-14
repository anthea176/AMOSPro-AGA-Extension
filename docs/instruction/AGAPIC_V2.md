# AGAPIC v2 — Images, palette et lecture des informations

**AMOS Professional AGA — R82 v0.13.27 (68020 minimum)**

AGAPIC v2 est un format d'image **indexée et compressée en RLE planaire**, stockée dans une **banque DATA AMOS**. Chaque image contient ses dimensions, sa profondeur, un masque facultatif, une **palette RGB24 complète** et le **DisplayModeID** nécessaire à son affichage. AGAPIC v1 reste compatible, mais **ne contient ni palette ni ModeID**.

## 1. Charger la banque et lire son en-tête

```amos
Load "R82_AGAPIC_V2_BANK10.abk",10
P=Start(10)
TAILLE=Length(10)
```

- `Start(10)` : adresse du **début des données AGAPIC** en mémoire.
- `Length(10)` : taille de ces données en octets, incluant l'en-tête AGAPIC, la palette et le flux compressé.
- `P+N` : adresse du champ situé à l'offset `N` **dans les données AGAPIC**, pas au début du fichier `.abk`.
- `Deek(adresse)` lit un entier sur **16 bits** ; `Leek(adresse)` sur **32 bits** ; `Peek(adresse)` lit **1 octet**. Les champs multioctets sont en **big-endian**.

Le fichier `.abk` comporte en plus une enveloppe AMOS de **20 octets**, retirée de ces offsets lorsque la banque est chargée. Après un autre `Load`, un `Erase` ou un déplacement de banque, il faut relire `Start(Bank)` ; ne pas conserver une ancienne adresse.

## 2. Toutes les informations disponibles

Dans le tableau, `P=Start(Bank)`. Les champs marqués **v2** ne doivent **pas** être lus comme des métadonnées v1.

| Information | Lecture AMOS | Signification |
|---|---|---|
| Signature | `Peek$(P,6)` | Doit valoir `"AGAPIC"` |
| **Version AGAPIC** | `Deek(P+6)` | `1` ou `2` |
| **Largeur en pixels** | `Deek(P+12)` | 1 à 4096 |
| **Hauteur en pixels** | `Deek(P+14)` | 1 à 4096 |
| **Profondeur** | `Deek(P+16)` | 1 à 8 plans ; nombre théorique de couleurs = `2^Profondeur` |
| **Nombre de couleurs de la palette (v2)** | `Deek(P+36)` | Exactement `2^Profondeur` (256 à 8 plans) |
| **DisplayModeID (v2)** | `Leek(P+32)` | Identifiant AGA à faire correspondre au mode réel de l'écran |
| **Format des pixels (v2)** | `Deek(P+38)` | `1` = indices de couleur en **planaire** |
| **Présence d'un masque** | `Deek(P+8) And 1` | `0` = absent ; `1` = masque 1 bit présent |
| **Codec** | `Deek(P+10)` | `1` = compression **RLE planaire par lignes** |
| **Taille des données** | `Length(Bank)` | Taille du *payload* chargé ; `Leek(P+28)` doit indiquer la même valeur |

**Palette v2 :** elle commence à `P+64`, avec **3 octets par couleur** : rouge, vert, bleu (0 à 255 par canal). Pour la couleur d'index `I` :

```amos
ADR=P+64+3*I
R=Peek(ADR)
V=Peek(ADR+1)
B=Peek(ADR+2)
```

Indices valides : `0` à `Deek(P+36)-1`. Ne lire cette zone **que si la banque est bien AGAPIC v2**, assez longue et correctement formée.

## 3. Exemple AMOS — afficher les informations AGAPIC v2

À utiliser avec la banque de démonstration R82 `R82_AGAPIC_V2_BANK10.abk`, placée dans le répertoire courant d'AMOS :

```amos
Cls
_B=10
Load "R82_AGAPIC_V2_BANK10.abk",_B

P=Start(_B)
TAILLE=Length(_B)
If P=0 or TAILLE<64
   Print "Banque absente ou trop courte"
   End
End If

If Peek$(P,6)<>"AGAPIC" or Deek(P+6)<>2
   Print "Ce n'est pas une AGAPIC v2"
   End
End If

If Leek(P+28)<>TAILLE
   Print "Longueur de banque incoherente"
   End
End If

VERSION=Deek(P+6)
LARGEUR=Deek(P+12)
HAUTEUR=Deek(P+14)
PLANS=Deek(P+16)
COULEURS=Deek(P+36)
MODEID=Leek(P+32)
FORMAT=Deek(P+38)
MASQUE=Deek(P+8) And 1
CODEC=Deek(P+10)

Print "AGAPIC version ";VERSION
Print "Dimensions ";LARGEUR;" x ";HAUTEUR
Print "Plans ";PLANS;" Couleurs ";COULEURS
Print "ModeID ";MODEID
Print "Format ";FORMAT;" Masque ";MASQUE
Print "Codec ";CODEC;" Octets ";TAILLE
End
```

**Résultat attendu avec cet exemple :** version `2`, **96 × 64 pixels**, **8 plans**, **256 couleurs**, ModeID `$00021000`, format `1`, masque `1`, codec `1`. Le `Print` du ModeID ci-dessus affiche sa valeur numérique, pas nécessairement en hexadécimal.

L'exemple effectue une **lecture simple**, pas la validation exhaustive du format : une signature et quelques champs cohérents ne prouvent pas que la palette ou le RLE sont intacts.

## 4. Utiliser ensuite l'image avec R82

```amos
' Sur un ecran AGA prive deja ouvert au bon ModeID :
OK1=Aga Bank Palette Apply(10,0)
OK2=Aga Bank Image Draw(10,20,20,0)

' Extraire un rectangle de la meme banque :
OK3=Aga Image Region(10,8,8,48,32,150,40,0)
```

- `Aga Bank Palette Apply(B,0)` applique la **palette intégrée v2**. L'index doit être `0`.
- `Aga Bank Image Draw(B,X,Y,Mode)` dessine l'image ; `Mode=0` opaque, `Mode=1` avec masque si présent.
- `Aga Image Region(B,SrcX,SrcY,Width,Height,X,Y,Mode)` dessine une partie de l'image.
- Le dessin **n'applique pas automatiquement la palette**, ne change pas le mode vidéo et ne réalise pas de `Swap`. Les commandes de dessin renvoient `1` en cas de succès, `0` en cas de refus ; il faut vérifier ce résultat.
- **Ne pas confondre** les dimensions de l'image avec celles de l'écran. Une image de 96 × 64 peut être affichée sur un écran AGA 320 × 256 compatible ; la profondeur et le ModeID doivent correspondre.

### Et avec AGAPIC v1 ?

Les champs communs jusqu'à `P+28` restent lisibles (version, dimensions, profondeur, masque, codec, longueur). **En v1, `P+32` est le début de la table des lignes RLE**, et non un ModeID : ne pas lire `P+32`, `P+36` ou `P+38` comme des informations de palette. `Aga Image Capture` et le convertisseur PNG historique produisent encore du v1.

**R82 ne possède pas de commande `Aga Bank Image Info`.** `Deek`, `Leek`, `Peek`, `Peek$`, `Start` et `Length` sont les fonctions AMOS existantes qui permettent de consulter les informations **sans changer l'extension**.

---

**Références techniques :** [contrat binaire v2](../M16_AGAPIC_V2_CONTRACT_2026-11-14.md) · [format v1](../M16_AGAPIC_FORMAT_DESIGN.md) · [exemple AMOS R82](../../tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc) · [codec v2](../../tools/m16_agapic_v2.py).
