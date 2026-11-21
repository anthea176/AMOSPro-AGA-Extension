# M19 P2a — Collisions Bob–Bob (modèle hôte)

**21 novembre 2026.** P2a est engagé après la promotion de P1e. Ce document formalise un **modèle de référence Python, source-only**, pas une nouvelle API AMOS ni une implémentation native.

## Portée et comportement envisagé

Le futur équivalent de BOB COL / COL sera abordé en deux niveaux :

1. **Rectangle** : intersection des empreintes visibles des images après positionnement et clipping. Un simple contact de bords ne constitue pas une collision.
2. **Masque** : au moins un pixel opaque commun dans la zone d'intersection. Une image sans masque est opaque, index couleur 0 compris.

Le modèle utilise la position logique moins les coordonnées du hotspot pour déterminer l'origine graphique. Il coupe la zone par l'écran, la limite globale, puis la limite locale éventuelle (P1d). Les Bobs OFF ne participent pas. Les paires sont renvoyées dans l'ordre des IDs, indépendant de la priorité de dessin. Il ne modifie ni banques, ni images partagées, ni buffers ou états Safe/Disp.

**Attention :** le masque du modèle est une représentation **hôte de test** (bit 1 = opaque, MSB d'abord, par ligne), **pas** une spécification du stockage AGBO natif.

## Livrables

- [Modèle Python P2a](../tools/m19_p2a_bob_collision_model.py) : rectangles et masques, hotspot, clipping, OFF.
- [17 tests de régression](../tools/test_m19_p2a_bob_collision_model.py) : bords, positions négatives, masques non alignés, image partagée, erreurs d'ID et ordre des paires.
- [CI P2a dédiée](../.github/workflows/m19-p2a-bob-collisions-host.yml) : syntaxe, tests et absence de modification des fichiers binaires ou ASC.
- [Conception générale P2](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) : collisions, retournements H/V, modes avancés et AMAL ultérieurement.

## Décisions à prendre avant développement natif

Signatures publiques exactes, retour par paire ou liste de contacts, politique de collisions hors écran et limites de clipping, effets des états READY/DIRTY, consommation CPU MC68020, gestion du masque AGBO réel, lecture de l'objet Bob sans modifier la frame. **Aucune compatibilité OCS, aucun token AP20 et aucun résultat Compiler ne sont revendiqués.**

## Validation

**17 tests hôtes PASS**, exécutés par la CI sur le modèle versionné ; l'analyse statique et les exemples n'établissent aucune qualification native. **Gate A P2a native : NON TESTÉE**, **Gate B WinUAE : NON TESTÉE**, **Gate C Compiler : NON TESTÉE**, **Gate D physique : NON TESTÉE**. La bibliothèque P1e LAST_GOOD reste inchangée.

Suite : inspecter le contrat interne des enregistrements Bob et des images AGBO P1e, puis raccorder ces données au modèle de collision en lecture seule, sans nouvelle commande AMOS avant approbation du contrat.
