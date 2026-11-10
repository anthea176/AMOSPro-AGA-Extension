# Outils obsolètes / historiques

Ce dossier contient les anciens builders, diagnostics et tests Python déplacés
depuis la racine de `tools/`.

Ils sont conservés uniquement pour :

- historique technique ;
- reproduction d'un ancien candidat ;
- comparaison ponctuelle lors d'une régression.

## Règles

- ne pas importer ces scripts depuis un builder courant ;
- ne pas les exécuter dans la CI normale ;
- ne pas les utiliser comme base d'un nouveau chantier ;
- l'état courant est défini par `tools/README.md`, `EXTENSION_SOURCE_RULES.md`
  et les documents STATUS/NEXT_SESSION ;
- si une reproduction historique est nécessaire, certains scripts peuvent avoir
  besoin de `PYTHONPATH=tools` car les utilitaires communs restent à la racine.

Le déplacement dans `obsolete/` ne signifie pas que les anciens binaires
associés doivent être supprimés : les archives et candidats versionnés restent
les preuves de l'historique du projet.
