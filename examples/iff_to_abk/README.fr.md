# IFF ↔ ABK AGAPIC — convertisseur et visionneuse

[English](README.md) · [Tous les exemples](../README.fr.md)

Deux exemples AMOS Professional indépendants sont disponibles. Importer les sources **ASCII** par **Project → Merge ASCII**. Utiliser la **R68 `AMOSPro_AGA_LAST_GOOD.Lib` promue**, installée sous le nom `AMOSPro_AGA.Lib` dans le slot `APSystem` habituel. Ces deux exemples n'ont pas encore été exécutés séparément sous WinUAE.

## 1. Conversion IFF vers ABK + palette

[**IFF_TO_ABK.asc**](IFF_TO_ABK.asc) sélectionne une image IFF/ILBM indexée avec `Fsel$("**")`, ouvre l'écran AGA, charge ses pixels puis capture le **back buffer** dans une banque DATA AGAPIC opaque n° 11. Il sauvegarde **deux fichiers côte à côte** :

| Sortie | Contenu |
|---|---|
| `RAM:IFF_TO_ABK.abk` | Banque ABK AMOS contenant les pixels indexés compressés (AGAPIC v1) |
| `RAM:IFF_TO_ABK.iff` | IFF de palette uniquement (`FORM ILBM`, `BMHD`, `CMAP`), créé par `Aga Palette Save` ; **pas de BODY image** |

L'exemple affiche brièvement l'IFF d'origine, efface la banque 11 et l'écran, puis affiche **CHARGEMENT ABK**. Il recharge ensuite **l'ABK sauvegardé**, efface le back buffer, reconstruit les pixels avec `Aga Bank Image Draw`, restaure **uniquement la palette enregistrée** avec `Aga Palette Load` et termine par `Aga Wait Key`.

Le chemin de la palette est déduit automatiquement du nom de l'ABK. Pour enregistrer les deux fichiers ailleurs, modifier uniquement `_ABK$="RAM:IFF_TO_ABK.abk"` ; le fichier `.iff` sera créé dans le même dossier. Attention : `RAM:` est volatile et vidé au redémarrage.

## 2. Visionneuse ABK autonome

[**ABK_VIEWER.asc**](ABK_VIEWER.asc) est un programme indépendant. Sélectionner un **`.abk`** avec `Fsel$("**")` ; le programme cherche automatiquement son fichier de palette **`.iff` portant le même nom de base et situé dans le même dossier**. Il lit l'en-tête de la banque AGAPIC pour connaître les dimensions et la profondeur, ouvre un écran AGA PAL LowRes 320×256, efface le back buffer et affiche l'ABK rechargé. L'image reste visible jusqu'à `Aga Wait Key`, sans avoir besoin de l'IFF d'origine.

**Limites de la visionneuse :** AGAPIC v1, 1–8 bitplanes, largeur ≤ 320 et hauteur ≤ 256 pixels ; mode PAL LowRes `$00021000`. Le fichier compagnon de palette `.iff` est obligatoire. L'ABK ne contient ni la palette ni l'identifiant de mode vidéo ; les résolutions supérieures ou modes particuliers ne sont pas gérés ici.

## Précautions et validation

**Les deux programmes exécutent explicitement `Erase 11` avant de créer ou charger la banque 11 : son éventuel contenu précédent est détruit.** Utiliser un programme vierge ou sauvegarder les banques utiles. Les erreurs de fichiers des commandes AMOS `Save`/`Load` peuvent interrompre l'exécution. Les fichiers de sortie sont écrasés lors d'une nouvelle conversion.

Commencer avec [`examples/demo.iff`](../demo.iff), une mire 320×256×256 couleurs. Contrôle statique réalisé, mais **l'exécution visuelle sous AMOS/WinUAE reste à vérifier** ; aucune validation Compiler ou Amiga physique n'est revendiquée.
