# M19 P2b — Retournements H/V des Bobs AGA

Le modèle hôte vérifie la géométrie, les pixels et la collision à partir d'une image AGBO v1. Les états normal, H, V et HV appartiennent à chaque Bob. Deux Bobs peuvent afficher des orientations différentes de la même image, avec les mêmes identifiants de banque et d'image.

## Pixels, masque et point d'ancrage

Pour une image de largeur `W` et de hauteur `H`, un pixel orienté `(x,y)` lit la source en `(W-1-x,y)` en H, `(x,H-1-y)` en V et `(W-1-x,H-1-y)` en HV. Les plans couleur et le masque indépendant suivent cette même transformation. Une image sans masque reste opaque, y compris à l'index 0. Le retournement porte sur la largeur utile et exclut le bourrage AGBO.

Le hotspot effectif suit la même formule, y compris s'il est hors de l'image. Le point logique `(X,Y)` du Bob reste fixe. L'origine du rectangle est `(X-hotspotXEffectif,Y-hotspotYEffectif)`. Calculer le hotspot effectif, l'origine et l'intersection en entier signé large avant toute conversion au format du Blitter. Appliquer le clipping écran et les limites P1d sur le rectangle orienté, avec des bornes de fin exclusives. Une collision par masque doit lire les mêmes pixels opaques que le rendu.

## Intégration native à qualifier

- Évaluer un cache Chip de variantes par identité de banque, génération, image et orientation. Préparer uniquement les variantes demandées et les partager entre Bobs. Une variante consomme `2 × ceil(W/16) × H × (profondeur + présence_du_masque)` octets de pixels et masque, hors métadonnées.
- Préparer toutes les sources avant le premier Blit et avant de publier un nouvel état d'orientation. Vérifier le refus sans mutation lors d'un échec d'allocation ou de validation. Couvrir le remplacement d'image P1e, Bank Free, Close et End, et conserver la source jusqu'à la fin du DMA.
- Vérifier les cas écran à deux pages, clipping et restauration du fond, deux Bobs sur la même image et collision avec un masque asymétrique. L'emplacement de l'état natif, sa durée de vie lors des commandes Bob et une éventuelle syntaxe AP20 restent à définir.

[Modèle hôte](../tools/m19_p2b_bob_orientation_model.py) et [tests](../tools/test_m19_p2b_bob_orientation_model.py). **6 tests P2b et 40 régressions hôtes P2a PASS.** Aucun résultat natif, Runtime ni Compiler sur P2b. La candidate active reste P2a et le dernier bon reste P1e.
