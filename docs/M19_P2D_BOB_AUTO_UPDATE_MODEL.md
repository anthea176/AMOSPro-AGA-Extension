# M19 P2d — Mise à jour des Bobs pendant Swap

Le mode automatique est facultatif et désactivé par défaut. Quand il est actif, l’appel explicite à `Aga Swap` prépare la page arrière avec la transaction Bob existante avant de la présenter. Toutes les opérations se déroulent dans la tâche AMOS, au point choisi par le programme.

| État de la page | Mode automatique activé |
| --- | --- |
| `CLEAN` | Avant le premier Bob, présenter sans réserver de fond. Ensuite, exécuter Update. Si Update échoue, transmettre le refus au programme et conserver la page visible. |
| `READY` | Présenter la page déjà préparée, y compris après un Update explicite. Si la présentation est refusée, garder la page prête pour le prochain Swap. |
| `DIRTY` | Refuser la présentation jusqu’à récupération par Clear ou fermeture. |

Le réglage change sur une frame `CLEAN` et se réinitialise à la fermeture de l’écran. Le programme qui modifie le décor garde la séquence Clear → dessin du décor → Swap pour préserver le décor neuf. La restauration utilise le fond de chaque page physique. Un Bob masqué conserve les pixels transparents, avec sélection P2c des plans sur les pixels opaques.

## Candidate native MC68020 construite en mémoire

La candidate expose la fonction numérique `Aga Bob Auto Update(Mode)`. Après ouverture AGA et activation du double buffer, `Mode=1` active l’update au Swap et `Mode=0` revient au fonctionnement manuel. Retour 1 si le réglage est accepté, 0 si le contexte, le mode ou l’état de la frame est refusé. Le réglage appartient au programme et à l’écran courants. Close et End le réinitialisent après fermeture effective.

Le [constructeur](../tools/build_m19_p2d_in_memory.py) part de P2c SHA256 `eebd7175035f6e6afbd7ed4d2bf5363bd6f816887993db22b848f8d5cfe48d3d`. Il rassemble BOBS et le service B8 dans un groupe AP20 de 60 928 octets. L’[émetteur](../tools/m19_p2d_bob_auto_update_emit.py) appelle le [garde de présentation](../tools/m19_p0j_swap_barrier_emit.py) et la [transaction du premier Update](../tools/m19_b8_first_update_emit.py) dans ce groupe relogeable. Les autres appels AP20 sont conservés et les stubs du service sont recalés. Le déplacement maximal d’un stub vers un groupe est de 854 octets.

Le premier Swap avec un Bob actif peut réserver les deux fonds. Le premier Swap sans Bob actif passe sans allocation de fond. Quand les fonds existent, Update peut encore s’exécuter après le dernier Bob Off pour nettoyer les anciennes images. Les refus de préparation conservent les états natifs de la transaction B8. Lorsque la page est `DIRTY`, la reprise passe par Clear ou Close.

**Identité de la candidate** · 136 020 octets, 100 commandes, 203 entrées AP20, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.

Les [cinq tests natifs](../tools/test_m19_p2d_bob_auto_update_gate_a.py) utilisent deux implantations MC68020 et simulent Exec, graphics.library et Intuition. Ils vérifient le dispatch de huit entrées, y compris les six entrées B8 déplacées, le rendu avec Flip et sélection des plans, les deux fonds physiques, le refus de Swap et la reprise, l’échec d’Update et la fermeture. Les [neuf tests hôtes](../tools/test_m19_p2d_bob_auto_update_model.py) vérifient le contrat de présentation. WinUAE Runtime et AMOS Compiler restent à qualifier sur P2d. La Lib installable sur `main` est P2c et AMAL reste à développer.
