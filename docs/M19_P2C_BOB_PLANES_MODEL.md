# M19 P2c — Sélection des plans à écrire par Bob

Cette première étape de SET BOB définit la sélection des plans de destination. Le masque numérique tient sur huit bits. Le bit 0 sélectionne le plan 0 et le bit 7 le plan 7. Le dessin copie les bits source dans les plans de même indice. Les autres bits de destination conservent leur valeur. Les bits au-delà de la profondeur sont ignorés.

## Contrat du modèle

- Le mode par défaut écrit tous les plans. Un masque de 0 laisse le fond intact. Le réglage appartient au slot Bob, exige un Bob actif et reste attaché au slot après rebind ou Off. Close le réinitialise. Un refus laisse le réglage précédent intact.
- Le masque AGBO d’opacité reste indépendant. Un pixel transparent préserve tous les plans. Un pixel opaque de couleur 0 efface les bits des plans sélectionnés. La sélection des plans ne change ni la géométrie ni les collisions P2a. Le futur raccordement à P2b utilisera les plans et le masque de la variante déjà retournée, avec le même hotspot.
- Le modèle conserve l’exigence de profondeur identique pour la source et la page cible, ainsi que la transaction existante Clear, Update et Swap avec restauration par page physique. Un échec d’Update bloque la présentation.

## Résultats et raccordement à vérifier

Le modèle hôte passe **7 tests**, avec **1 024 compositions comparées bit par bit**, des masques non contigus et des essais de restauration sur les deux pages. Les 14 régressions Clear/Update et les 6 régressions hôtes P2b passent aussi.

## Raccordement natif livré

`Aga Bob Planes(N,Masque)` renvoie 1 après écriture du réglage du Bob actif, ou 0 si le Bob ou le masque est refusé. Le réglage est stocké dans le slot P2b et effacé à la fermeture effective. Le [point de raccordement natif](../tools/m19_p2c_bob_planes_emit.py) règle le byte `Mask` du RastPort privé, après InitRastPort et avant le rendu opaque ou masqué. Il utilise l’[interface classique du RastPort](https://www.theflatnet.de/pub/cbm/amiga/AmigaDevDocs/lib_27.html) et [sa structure](https://github.com/aros-development-team/AROS/blob/master/compiler/include/graphics/rastport.h). Le choix des plans reste distinct du masque AGBO et du minterm.

Le [banc natif](../tools/test_m19_p2c_bob_planes_gate_a.py) couvre le dispatch AP20, les deux implantations, les pixels en opaque et masqué, Flip, la restauration par page, les refus et la réinitialisation à Close.

La [campagne WinUAE](../tests/current/README.md) passe **34/34 en Runtime**. Le journal fourni indique `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `PROBE_PREALLOC 1`, `CHECKS 34`, `CLOSE_RETURNED 1` et `VERDICT PASS`. Son SHA256 est `9c395425ebee144bc57c34857a0556b2414fd9221a48a4740dafc40fcf5b77df`. AMOS Compiler n’a pas été testé. L’update automatique se poursuit dans [P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md).

[Modèle Python](../tools/m19_p2c_bob_planes_model.py) · [Tests](../tools/test_m19_p2c_bob_planes_model.py)
