# Iff AMOS-AGA

## Identification

- **Nom dans le source :** Perfect Iff Viewer and Saver AGA V4.0
- **Sources :** `Iff-AGA.asc`, `Iff-AGAIII.asc`
- **Auteur :** Amethist / HWARF
- **Date indiquee :** 24 novembre 1995
- **Environnement :** AMOS Professional sur Amiga AGA

> L'analyse est basee sur les sources ASCII. Les deux binaires `.AMOS` sont conserves mais n'ont pas ete decodes.

## Objet du projet

Iff AMOS-AGA est un **lecteur et sauvegardeur IFF/ILBM AGA** qui contourne les limites des ecrans AMOS classiques en ouvrant et manipulant directement un ecran Intuition.

Le programme refuse de continuer si le chipset detecte n'est pas AGA.

## Capacites retrouvees

Le lecteur analyse directement plusieurs chunks ILBM :

- `BMHD`
- `CMAP`
- `CAMG`
- `BODY`
- et un chunk maison `SQUASH`.

Il prend en charge :

- les images ILBM non compressees (`compression = 0`) ;
- le **ByteRun1** standard (`compression = 1`) en lecture ;
- les modes **HAM6**, **HAM8** et **Half-Bright/EHB** suivant les indicateurs `CAMG` ;
- le chargement d'une palette en composantes 24 bits vers le systeme graphique ;
- des ecrans AGA pouvant aller jusqu'aux modes que le source presente comme 262144 couleurs.

## Sauvegarde

Le programme propose deux modes de sauvegarde :

- `Iff ILBM Compress rate 0` : BODY non compresse ;
- `Iff ILBM Compress rate 128` : format maison utilisant `Squash`.

Le mode 128 ajoute un chunk `SQUASH` contenant notamment les longueurs compressees des bitplanes. Il s'agit d'une **extension non standard de l'ILBM**, destinee a etre relue par ce programme.

## Deux variantes importantes

`Iff-AGA.asc` et `Iff-AGAIII.asc` ne doivent pas etre consideres comme de simples doublons.

La variante `Iff-AGAIII.asc` contient une evolution importante de l'ouverture d'ecran : elle construit une TagList et utilise directement **`OpenScreenTagList`** avec des tags tels que `SA_DISPLAYID`, `SA_WIDTH`, `SA_HEIGHT` et `SA_DEPTH`.

Les deux variantes doivent donc etre conservees separement dans l'historique.

## Dependances techniques

Le source utilise :

- des appels directs aux bibliotheques systeme/Intuition/Gfx via `Intcall`, `Gfxcall`, etc. ;
- des operations de decalage et routines graphiques accelerees presentes dans l'environnement AMOS utilise a l'epoque ;
- de la memoire Chip pour les bitplanes d'affichage.

Cela rend la restauration plus sensible qu'un simple programme AMOS pur, mais aussi beaucoup plus interessante techniquement.

## Elements conserves

- `Iff AMOS-AGA.AMOS`
- `Iff AMOS-AGAIII.AMOS`
- `Iff-AGA.asc`
- `Iff-AGAIII.asc`

## Etat de conservation

- **Sources ASCII :** presentes pour les deux variantes
- **Programmes AMOS :** presents
- **Format ILBM gere :** lisible dans le source
- **Extension `SQUASH` maison :** lisible dans le source
- **Machine cible :** AGA explicitement requise
- **Execution actuelle :** non validee sur WinUAE ou Amiga reel

## Interet de preservation

**Tres eleve.** Le projet va nettement au-dela d'un petit utilitaire AMOS : il implemente un lecteur/sauvegardeur ILBM AGA, gere HAM/EHB, manipule Intuition directement et definit meme une compression IFF maison.
