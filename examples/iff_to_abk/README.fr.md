# IFF vers ABK AGAPIC — démonstration visuelle

[English](README.md) · [Tous les exemples](../README.fr.md)

Importer [`IFF_TO_ABK.asc`](IFF_TO_ABK.asc) dans AMOS Professional par **Project → Merge ASCII**. Utiliser de préférence **R68 `AMOSPro_AGA_LAST_GOOD.Lib`**, installée sous le nom `AMOSPro_AGA.Lib` dans le slot `APSystem` habituel. La candidate R70 active rencontre un blocage WinUAE non résolu et **n'est pas recommandée** pour cette démonstration.

## Déroulement

1. Sélectionner une image **IFF/ILBM indexée** via `Fsel$("**")`, puis lire les dimensions, la profondeur, le nombre de couleurs et le mode écran.
2. Ouvrir l'écran AGA adapté avec double buffering, charger les pixels et la palette IFF.
3. **Avant le premier Swap**, convertir le **back buffer** en banque DATA **AGAPIC v1 opaque n° 11** avec `Aga Image Capture`.
4. Sauvegarder l'ABK natif AMOS dans **`RAM:IFF_TO_ABK.abk`** ; montrer brièvement l'IFF original ; **Erase 11**.
5. Effacer l'écran et afficher **CHARGEMENT ABK**.
6. Recharger l'ABK depuis le disque avec `Load` ; effacer le back buffer ; reconstruire l'image **uniquement à partir des pixels de l'ABK rechargé** avec `Aga Bank Image Draw(11,0,0,0)`.
7. Restaurer **uniquement la palette IFF** avec `Aga Palette Load`, afficher l'image recomposée, terminer par `Aga Wait Key`. Fermer l'écran AGA et libérer la banque 11 de la démonstration.

**Important :** le format AGAPIC contient les pixels indexés compressés, **pas la palette RGB**. Il faut garder l'IFF original accessible pour restaurer les couleurs ; `Aga Palette Load` recharge seulement le CMAP et **ne redessine aucun pixel**.

**Sécurité :** la banque **11 doit être libre**. Le programme refuse de démarrer si elle est occupée, et n'efface que la banque qu'il a lui-même créée. Une erreur disque native de `Save` ou `Load` peut interrompre l'interpréteur AMOS.

**Fichier de sortie :** `RAM:` est temporaire, perdu au redémarrage. Pour sauvegarder définitivement, remplacer `_ABK$="RAM:IFF_TO_ABK.abk"` par un chemin sur un volume inscriptible (par exemple `Work:IFF_TO_ABK.abk`). Une nouvelle exécution écrase le fichier cible.

Pour commencer, choisir [`examples/demo.iff`](../demo.iff), une mire PAL **320×256×256 couleurs**. Les autres IFF indexés restent soumis aux modes acceptés par `Aga Screen Open`/`Aga Iff Load` et à la mémoire disponible.

**Validation :** nouvel exemple public fondé sur des commandes existantes, **non exécuté encore sous AMOS/WinUAE**. Pas de Gate Compiler ni de validation sur Amiga physique revendiquée.
