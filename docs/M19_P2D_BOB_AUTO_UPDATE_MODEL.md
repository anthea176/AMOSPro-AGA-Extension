# M19 P2d — Mise à jour des Bobs pendant Swap

Le mode automatique est facultatif et désactivé par défaut. Quand il est actif, l’appel explicite à `Aga Swap` prépare la page arrière avec la transaction Bob existante avant de la présenter. Toutes les opérations se déroulent dans la tâche AMOS, au point choisi par le programme.

| État de la page | Mode automatique activé |
| --- | --- |
| `CLEAN` | Avant le premier Bob, présenter sans réserver de fond. Ensuite, exécuter Update. Si Update échoue, transmettre le refus au programme et conserver la page visible. |
| `READY` | Présenter la page déjà préparée, y compris après un Update explicite. Si la présentation est refusée, garder la page prête pour le prochain Swap. |
| `DIRTY` | Refuser la présentation jusqu’à récupération par Clear ou fermeture. |

Le réglage change sur une frame `CLEAN` et se réinitialise à la fermeture de l’écran. Le programme qui modifie le décor garde la séquence Clear → dessin du décor → Swap pour préserver le décor neuf. La restauration utilise le fond de chaque page physique. Un Bob masqué conserve les pixels transparents, avec sélection P2c des plans sur les pixels opaques.

## Raccordement à éprouver sur MC68020

La [base P2c reconstruite](../tools/build_m19_p2c_in_memory.py) est identique à la Lib active, SHA256 `eebd7175035f6e6afbd7ed4d2bf5363bd6f816887993db22b848f8d5cfe48d3d`. Son entrée AP20 `Aga Swap` (181) vise le groupe 194. `Aga Bob Update` (197) vise le groupe 195. Le prototype natif devra réutiliser le [garde de présentation](../tools/m19_p0j_swap_barrier_emit.py) et la [transaction publique, y compris le premier appel](../tools/m19_b8_first_update_emit.py), via un raccord inter-unité compatible AP20/Compiler. L’état et l’identité du propriétaire de la page doivent être contrôlés avant Update et avant la présentation. Le premier Update peut réserver les deux fonds. La reprise après refus doit conserver la distinction entre une page prête à présenter et une page refusée par Update.

Le [modèle hôte](../tools/m19_p2d_bob_auto_update_model.py) et ses [neuf tests](../tools/test_m19_p2d_bob_auto_update_model.py) couvrent notamment la présentation avant le premier Bob, le refus de présentation, les deux pages, le masque P2c et la récupération après un rendu partiel. Le raccordement natif, la commande publique et AMAL restent à développer.
