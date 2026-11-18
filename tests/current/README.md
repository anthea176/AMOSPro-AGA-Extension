# M19 B7 — animation des Bobs, Runtime WinUAE uniquement

**Seul ASC actif :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](M19_P0J_B7_ANIM_RUNTIME_03.asc) — **4 718 octets**, SHA256 **0f92b7ee5e1d60b1c0ab78c0d96a7d1aaebb97f3db12696a62c9a73783ad7cb6**.

**Bibliothèque inchangée :** [dist/AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), B7, 102 072 octets, SHA256 **f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b**. R84 LAST_GOOD protégée. **Pas de test Compiler.** [Contrat du test](../../docs/M19_P0J_B7_ANIM_RUNTIME_2026-11-18.md).

## Lancement

1. WinUAE AGA PAL, CPU 68030/JIT activé, même Lib B7 installée dans APSystem. Dans AMOS Professional, ouvrir un programme vide puis **Project → Merge ASCII** (pas Load).
2. Les banques AMOS **24 et 25** doivent être libres. Si d'anciens essais les ont laissées réservées, **Erase All** convient dans une session de test ne contenant aucune banque à préserver ; cette instruction efface **toutes** les banques.
3. Lancer **uniquement en Runtime**. Pendant **120 frames**, un Bob masqué rouge et un Bob jaune opaque effectuent un aller-retour ; deux Bobs fixes testent le clipping aux bords. À chaque frame : effacement complet du back buffer, mise à jour des positions, Aga Bob Draw, puis Aga Swap **uniquement si Draw=1**. Une attente VBL rend l'animation observable : ce n'est pas un benchmark.
4. Le programme appelle **Aga Screen Close** puis **Amos To Front**, efface les banques qu'il a créées et écrit **RAM:M19_B7_ANIM_RUNTIME.TXT**. Le relancer **une deuxième fois sans Erase All** pour contrôler que les banques 24/25 ont bien été libérées.

## Résultat attendu

Le journal indique RESULT 1, ERR 0, FRAMES_TARGET 120, FRAMES_OK 120, BOBS_PER_FRAME 4, DOUBLE_BUFFER 1, CLEAR_FAILS 0, DRAW_FAILS 0, SWAP_FAILS 0, CLOSE_CALLED 1, BANKS_ERASED 2 et VERDICT PATH_OK.

**PATH_OK n'est pas une preuve visuelle.** Vérifier l'absence de traînées, de corruption et de scintillement anormal, le masque et les Bobs rognés, ainsi que le retour à l'éditeur. CLOSE_CALLED constate l'appel de la commande, pas une mesure OS de Chip RAM. Codes ERR : 1=Compiled exclu, 2=AGA absente, 3=banques occupées, 4=Open, 5=Double Buffer, 6–12=préparation, 13=Clear, 14=Draw, 15=Swap.

**Statut : PREFLIGHT statique en CI, Gate B animation NON TESTÉE, Gate C animation non prévue.** L'ancien [banc End sans Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0e7be49a079f75f0ac628625d567b86a3afa042d/tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc) reste intact dans l'historique Git. Son ERR 2 au second lancement concernait les banques AMOS, sans preuve de fuite Chip.
