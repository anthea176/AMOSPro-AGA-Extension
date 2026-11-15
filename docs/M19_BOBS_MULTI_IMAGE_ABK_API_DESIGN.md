# M19 — API Bobs AGA simple et banques ABK multi-images

**Statut : contrat de conception utilisateur ; aucune nouvelle commande AMOS ni nouvelle bibliotheque n'est implementee ou validee par ce document.** Depot `anthea176/AMOSPro-AGA-Extension`, uniquement `main`. Candidate R88 et R84 `LAST_GOOD` protegees. Reprendre les API et fichiers actuels avant tout changement de code.

## Creation des images directement sous AMOS Professional — EXIGENCE DE L'AUTEUR

**Pas de convertisseur PC comme chemin de creation principal.** L'utilisateur veut capturer ses images directement sur **l'ecran AGA prive de l'extension**, par une commande analogue au `Get Bob` OCS, en conservant l'ergonomie AMOS :

```text
Get AGA Bob 1,0,0 To 31,31
Get AGA Bob 2,32,0 To 63,31
Get AGA Bob 3,64,0 To 95,31
```

**Cette syntaxe exacte est une cible a etudier, pas une commande validee sous AMOS, AP20 ou AMOS Compiler V2.** Ne pas la remplacer d'autorite par un convertisseur ou par une API a sept parametres. Verifier en premier si le tokenizer d'extension et le Compiler permettent la combinaison multi-mots `Get AGA Bob` avec separateur `To`. Si impossible, documenter la contrainte et proposer le plus proche equivalent pour decision de l'auteur AVANT de coder.

Chaque appel **cree ou remplace l'image I** dans la meme banque AGA multi-images ; les appels suivants conservent les autres indices. La source est l'ecran AGA de l'extension, **pas l'ecran OCS prive a AMOS**. Le conteneur doit accepter 1..8 bitplanes (jusqu'a 256 couleurs), tailles variables et masques par image. Une fois peuplee, la banque est sauvegardable en un **seul fichier ABK**, rechargeable sous AMOS comme les autres banques. Le code utilisateur ne manipule pas de cache ou de Chip RAM.

**Points restant a arbitrer sans supposer de comportement :**

- **Quelle banque contient les captures ?** La commande demandee ne comporte pas de numero de banque. Il faut definir une banque d'objets AGA active, son numero, sa creation et sa selection, sans forcer la banque native OCS n°1 ni ecraser une banque existante.
- **Convention des bornes `To` :** comparer au `Get Bob` AMOS documente, puis verrouiller par tests pixel (largeur de 1 pixel, bords, alignements) ; ne pas deduire les bornes de `Aga Blit Fill` ou `Screen Copy`.
- **Masque independant :** un ecran indexe seul n'encode pas de transparence. Decider comment indiquer les pixels transparents (index de transparence, masque explicite, autre mecanisme) tout en preservant une couleur 0 opaque quand c'est demande.
- **Palettes, ecrans et double buffering :** choisir le buffer source, fixer les exigences de profondeur et le traitement palette ; assurer les protections DMA/Safe sans les exposer a l'utilisateur.
- **Reprise apres `Load`, `Save`, `Erase` :** eviter les pointeurs caches invalides et confirmer qu'une banque avec plusieurs images reste portable entre interpreteur et Compiler.

La commande historique `Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` capture deja **une image par banque AGAPIC** ; c'est un socle technique a etudier, mais **ce n'est pas la fonction multi-images demandee**. Conserver AGAPIC et ses decodages si pertinent, sans ajouter une contrainte de conversion PC.

**Reference d'ergonomie AMOS OCS :** [effectiveBobs — creation d'une banque via `Get Bob` / `Save`](https://github.com/alain-treesong/amiga_coding_in_amos/tree/main/snippet-014_effectiveBobs). Reprendre le principe multi-images, pas le format OCS limite en profondeur.

## Exigences retenues avec l'auteur

- **Simplicite utilisateur avant micro-optimisation** : un programme AMOS charge ses images, choisit l'image et deplace/affiche ses Bobs ; il n'a pas a gerer des caches AGPC, des banques temporaires, la Chip RAM ou un choix manuel CPU/Blitter.
- **Plusieurs images dans un seul fichier ABK**, accessibles par numero d'image, avec differentes dimensions possibles et masque de transparence independant par image. Un seul chargement de la banque pour tous les frames d'un personnage ou d'une animation.
- **Ne pas multiplier les formats et API visibles** : conserver les ressources existantes quand c'est possible et construire une interface coherente, utilisable pour un Bob unique ou plusieurs objets.
- Une image source peut etre **partagee par plusieurs Bobs** : numero de banque, numero d'image et identifiant d'objet sont trois notions distinctes.
- L'extension est responsable de l'allocation, de la preparation et de la liberation de ses caches acceleres ; le programme reste proprietaire de la banque ABK chargee.
- Aucune optimisation ne doit imposer un code utilisateur beaucoup plus complique pour un gain de rendu faible ou nul en frame complete.

## Ce qui existe aujourd'hui dans le depot (R88, non promue)

- **AGAPIC v1/v2** : une image compressee par banque AMOS DATA ; dessin simple par `Aga Bank Image Draw(Bank,X,Y,Mode)`, lecture CPU possible depuis Fast ou Chip.
- **FICON8** : plusieurs icones dans une banque, mais format **16x16x8** et transparence index zero ; `Aga F Icon(Bank,IconID,X,Y,Mode)`.
- **BOB1/Batch R87** : `Aga Bob Batch(DescriptorBank,Count)` utilise une banque de descripteurs, sans etre une API utilisateur simple de creation/deplacement.
- **AGPC/R88** : `Aga Cache Blit(CacheBank,X,Y,Mode)` n'accepte que le cache 16x16x8 pre-prepare en vraie Chip RAM. Le 15/11/2026, un chargement ABK direct en Fast a provoque `ERR 12` ; le banc corrige reserve de la Chip et a retourne `RESULT 1`, `ERR 0`, `PARITY_OK 8`, `CHIP_STAGE_DELTA 768` en WinUAE Runtime. **Ce contournement de banc n'est pas une API utilisateur satisfaisante.** Gate C R88 pas documentee comme passee.

## Modele utilisateur vise (proposition, PAS syntaxe AMOS validee)

Exemple de forme d'appel envisagée, **non executable dans R88** :

```text
Load "HERO.ABK",10
_OK=Aga Bob Draw(10,5,100,80,1)
```

Sens : fichier banque 10, image 5, position (100,80), mode masque 1. Le programme n'a pas besoin de reserver la Chip RAM ou de preparer un AGPC. Le nom, l'ordre precis des arguments, la gestion d'objets persistants et les retours sont **a definir et approuver** avant tout ajout de token AP20.

Exemple de contenu d'une banque : indices 1..4 marche bas, 5..8 marche haut, 9..12 marche gauche, 13..16 marche droite, 17..20 attaque. Images de dimensions et hotspots potentiellement differents, masque individuel. Un ID image ne doit pas etre confondu avec un ID Bob.

## Orientation technique proposee, non encore arbitree

1. **ABK externe standard AMOS**, contenu interne avec un catalogue d'images : nombre d'images, table d'offsets/longueurs et versions. Reutiliser autant que possible les **blocs AGAPIC v1/v2 existants**, sans changer le codec RLE pour l'objectif multi-image. Ne pas pretendre que cet ABK est une banque native `Get Bob` d'AMOS sans prouver sa compatibilite.
2. **Numero d'image 1-based** pour un acces direct depuis AMOS. Longueur, dimensions, profondeur, masque et eventuel hotspot sont verifies par image. Erreur propre pour un numero hors banque ou un bloc corrompu.
3. **Palette** : une image indexee est interpretee avec la palette active de l'ecran ; ne pas changer la palette a chaque Bob. Etudier une palette commune au pack, compatibilite ModeID AGAPIC v2 et politique en cas de palettes sources differentes.
4. **Fast pour les sources compressees** ; **Chip pour les buffers effectivement transmis au Blitter**. L'extension cree des caches prives utiles, les partage ou les libere ; elle doit garantir `MEMF_CHIP` avant DMA. Le programme n'effectue aucun `Reserve As Chip Data`.
5. **Cache intelligent mais previsible** : preparation hors boucle de rendu, reuse sur plusieurs frames, budget Chip borne, repli CPU si le Blitter ou la Chip RAM ne peuvent pas etre utilises (sans afficher une image invalide). Definir et tester l'invalidation lors de `Load`, `Erase` ou remplacement de banque ; ne pas promettre une detection parfaite de mutations `Poke` non instrumentees.
6. **Dessins multiples** : plusieurs objets peuvent partager l'image 5 ; positions, priorites Z, visibilite et animations vivent dans les objets, pas dans les images compressees. Les ressources cache ne doivent pas etre dupliquees par instance.
7. **Reseau de tests avant remplacement API** : une banque avec une image, plusieurs images, tailles diverses, masque independant et couleur 0 opaque, animation et partage d'image, clipping, banque absente/effacee/remplacee, manque de Chip, Runtime et Compiler distincts, nettoyage Chip/Fast.

## Decision de perimetre

**Ce qui est fixe :** banque ABK multi-images, interface utilisateur simple, pas de staging Chip manuel, distinction image/objet. **Ce qui reste a concevoir :** representation binaire precise, capture `Get AGA Bob` native et ses contraintes AP20/Compiler, choix de la banque active, convention `To`, transparence, API de dessin, budget et politique cache/CPU, hotspots/animation, politique palettes. **Aucun convertisseur PC impose.** Avant d'implementer, obtenir la validation du contrat concret et tester un programme AMOS minimal. Ne pas remplacer le binaire R88 ou promouvoir `LAST_GOOD` sur la base de cette note.

Sources : [format AGAPIC](M16_AGAPIC_FORMAT_DESIGN.md), [contrat manager P2](M19_P2_OBJECT_MANAGER_CONTRACT.md), [FICON8/Chip](M18_FAST_ICON_CACHE.md), [API publique courante](../README.fr.md), [incident P2.8](M19_P28_R88_CHIP_BANK_DIAGNOSTIC_2026-11-15.md).
