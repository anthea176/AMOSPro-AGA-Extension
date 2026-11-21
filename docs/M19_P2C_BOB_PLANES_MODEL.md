# M19 P2c — Sélection des plans à écrire par Bob

Cette première étape de SET BOB définit la sélection des plans de destination. Le masque numérique tient sur huit bits. Le bit 0 sélectionne le plan 0 et le bit 7 le plan 7. Le dessin copie les bits source dans les plans de même indice. Les autres bits de destination conservent leur valeur. Les bits au-delà de la profondeur sont ignorés.

## Contrat du modèle

- Le mode par défaut écrit tous les plans. Un masque de 0 laisse le fond intact. Le réglage appartient au slot Bob, exige un Bob actif et reste attaché au slot après rebind ou Off. Close le réinitialise. Un refus laisse le réglage précédent intact.
- Le masque AGBO d’opacité reste indépendant. Un pixel transparent préserve tous les plans. Un pixel opaque de couleur 0 efface les bits des plans sélectionnés. La sélection des plans ne change ni la géométrie ni les collisions P2a. Le futur raccordement à P2b utilisera les plans et le masque de la variante déjà retournée, avec le même hotspot.
- Le modèle conserve l’exigence de profondeur identique pour la source et la page cible, ainsi que la transaction existante Clear, Update et Swap avec restauration par page physique. Un échec d’Update bloque la présentation.

## Résultats et raccordement à vérifier

Le modèle hôte passe **7 tests**, avec **1 024 compositions comparées bit par bit**, des masques non contigus et des essais de restauration sur les deux pages. Les 14 régressions Clear/Update et les 6 régressions hôtes P2b passent aussi.

Le [peintre natif actuel](../tools/m19_p0d_private_blit_emit.py) initialise un RastPort privé avant les appels de rendu opaque et masqué. Le raccordement devra qualifier la sélection des plans sur les deux chemins et comparer les pixels avec Flip, clipping et restauration du fond. L’API publique, l’update automatique et AMAL restent à définir. Les résultats de ce jalon portent sur le modèle hôte.

[Modèle Python](../tools/m19_p2c_bob_planes_model.py) · [Tests](../tools/test_m19_p2c_bob_planes_model.py)
