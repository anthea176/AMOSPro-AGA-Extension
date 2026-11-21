# M19 P2b — Retournements H/V des Bobs AGA

Le modèle hôte vérifie la géométrie, les pixels et la collision à partir d'une image AGBO v1. Les états normal, H, V et HV appartiennent à chaque Bob. Deux Bobs peuvent afficher des orientations différentes de la même image, avec les mêmes identifiants de banque et d'image.

## Pixels, masque et point d'ancrage

Pour une image de largeur `W` et de hauteur `H`, un pixel orienté `(x,y)` lit la source en `(W-1-x,y)` en H, `(x,H-1-y)` en V et `(W-1-x,H-1-y)` en HV. Les plans couleur et le masque indépendant suivent cette même transformation. Une image sans masque reste opaque, y compris à l'index 0. Le retournement porte sur la largeur utile et exclut le bourrage AGBO.

Le hotspot effectif suit la même formule, y compris s'il est hors de l'image. Le point logique `(X,Y)` du Bob reste fixe. L'origine du rectangle est `(X-hotspotXEffectif,Y-hotspotYEffectif)`. Calculer le hotspot effectif, l'origine et l'intersection en entier signé large avant toute conversion au format du Blitter. Appliquer le clipping écran et les limites P1d sur le rectangle orienté, avec des bornes de fin exclusives. Une collision par masque doit lire les mêmes pixels opaques que le rendu.

## Noyau privé MC68020 et préparation Chip

[Émetteur](../tools/m19_p2b_planar_orientation020_emit.py) et [banc natif](../tools/test_m19_p2b_planar_orientation020_gate_a.py). Le bloc source de **562 octets**, SHA256 `c4632d93c8af5c856dafd5e27d2003bc805830ff29c3644c412a94735acace69`, expose deux entrées privées.

- Le matérialiseur reçoit des plages déjà validées par l'appelant. Il contrôle dimensions, nombre de plans, orientation, capacité, alignement, débordement d'adresse et chevauchement avant la première écriture. H inverse les bits utiles de chaque ligne, V inverse l'ordre des lignes de chaque plan. Le masque éventuel est traité comme le dernier plan.
- La préparation alloue le bloc exact par `AllocMem(MEMF_CHIP)`, contrôle ses deux extrémités via `TypeOfMem` et appelle le même matérialiseur. Le bloc est libéré si la préparation échoue. En cas de succès, l'appelant reçoit son adresse et sa taille et devient responsable de sa durée de vie.

**Gate A privée PASS** sous Unicorn MC68020 à deux adresses de code, avec **216 comparaisons planaires octet pour octet**, contrôles de refus, canaris, registres et pile. Le noyau natif P2a lit le masque P2b produit et rend les résultats attendus avec ou sans clipping. Les appels Exec sont simulés et le banc calcule l'origine du Bob à partir du hotspot avec le modèle hôte.

## Intégration P2b livrée

La bibliothèque [M19 P2b](../dist/AMOSPro_AGA.Lib), 135 352 octets, SHA256 `96f4bc7e1d604d57d615e198eb43ca6abc800cdc3853c6e9ac2827ad6a86e448`, est reconstruite par le [builder](../tools/build_m19_p2b_in_memory.py). Le point d'entrée public `Aga Bob Flip(N,Mode)` règle l'orientation d'un Bob actif. Le mode appartient au slot et reste en place lorsque le même ID est réutilisé. Le mode 0 libère sa variante, Close/End réinitialisent les modes.

Le cache borné conserve au plus un bloc par slot Bob. Un slot vérifie le numéro de banque, le pointeur, la génération, l'image et les adresses des plans et du masque avant réutilisation. La variante est préparée au premier usage. Une nouvelle génération impose une nouvelle préparation. Bank Free libère les blocs de la banque concernée, Close et End libèrent l'ensemble après fermeture effective. En cas d'épuisement Chip, la collision renvoie -1 et le rendu refuse la frame, ce qui bloque sa présentation via Aga Swap.

Les [tests natifs intégrés](../tools/test_m19_p2b_bob_flip_gate_a.py) couvrent le dispatch AP20 interprété et la relocation Compiler simulée, les pixels, les collisions, la seconde page et le nettoyage. Le [banc WinUAE corrigé](../tests/current/README.md) passe 21/21 en Runtime et avec AMOS Compiler. LAST_GOOD reste P1e.
