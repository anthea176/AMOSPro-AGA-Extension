# M19 P0j-b5 — garde de présentation des Bobs : Gate A en attente

**MC68020 / 68EC020 minimum.** Implémentation privée AP20 V2, construite exclusivement en mémoire depuis P0j-b4 (100 596 octets, SHA256 `b6a318118d0f8c58ab839d905c4094b8de27b6f481d411c647626266d69a6a7b`). **Aucune nouvelle commande publique**, `Aga Bob Draw` n'est pas exposée. Aucun changement de `dist/AMOSPro_AGA.Lib`, du seul ASC actif, de R84 LAST_GOOD ni des archives.

## Raccordements

1. `guarded_frame_draw_entry` : contrôle owner/State/DB/front, inscrit un verrou DIRTY avant de lancer P0j-b4, puis READY uniquement sur succès complet (`D3=1` et `D2=0`). Une erreur, même de préflight sans DMA, laisse DIRTY et refuse les dessins suivants. Aucun shadow `bank_active_state` et aucun Swap implicite.
2. `guarded_swap_entry` : le builder rebranche **le token existant** `Aga Swap` vers cette entrée **dans la candidate en mémoire uniquement**. Si DIRTY, retour 0 sans appel de l'ancien Swap ni `ChangeScreenBuffer`. Si autorisé, l'entrée originale R88, **octets inchangés**, est retrouvée à partir du vrai pointeur AGA State dans A5+$1C8 ; offset de groupe $0BA2, State à $01C2, soit +$09E0. La signature de la routine est vérifiée en builder et au runtime avant JSR.
3. `guarded_close_entry` : route le token existant `Aga Screen Close` vers son pont P0c natif déjà vérifié. DIRTY n'est effacé **que si Screen est réellement fermé**. Fermer l'écran après un SafePort restant pending n'est pas validé par ce banc ; les réponses Safe/Disp doivent être résolues selon le contrat OS.
4. Pour maintenir la portée PC16, les deux nouveaux stubs AP20 sont ajoutés **après** la quatrième unité BOBS sans modifier les stubs historiques, ni le noyau AGA. Les tokens existants changent seulement d'index d'entrée ; **85 signatures de commandes restent identiques**, quatre unités natives, aucune cinquième unité.

## Tests demandés

[Émetteur](../tools/m19_p0j_swap_barrier_emit.py) · [Builder privé](../tools/build_m19_p0j_swap_barrier_in_memory.py) · [Banc natif MC68020](../tools/test_m19_p0j_swap_barrier_gate_a.py).

- Deux implantations V2 distinctes, décodage MC68020 et vérification des registres ABI, signatures AP20, stubs et PC16.
- Swap normal sans Bobs protégés, Draw protégé valide + véritable entrée native AGA Swap, `ChangeScreenBuffer` mocké appelé une fois.
- Échec réel de ChangeScreenBuffer : statut READY conservé et retry possible.
- Signature Swap native altérée : refus sûr avant toute présentation.
- Masque AGBO invalide dès le préflight : aucun pixel DMA, verrou DIRTY (conservateur), aucune présentation.
- `SafePort` défaillant au **deuxième Bob** : un Bob masqué réellement peint, back buffer partiel, front intact, `Aga Swap` refusé ; le second Draw ne lève pas le verrou.
- Fermeture réussie avec tous les messages Safe/Disp déjà acquittés : état privé nettoyé ; cas Close avec messages pending séparé, non couvert.

## Décisions et limites

Le futur retour public proposé est `_OK=Aga Bob Draw` : **fonction numérique 0/1 sans argument, à confirmer par tokenisation et vrai AMOS Compiler**. La commande d'objet `Aga Bob N,X,Y,I` conserve sa fonction de mise à jour de l'état, sans dessin ni Swap.

Cette solution est conservatrice : **la seule récupération après échec est Close/Reopen**. Une reconstruction du back buffer sans fermeture devra être prouvée avant de créer une commande de déverrouillage. Toute voie alternative appelant directement l'entrée native AGA Swap au lieu du token public sort du contrat ; le moteur doit ensuite vérifier End, Open/Close et les deux pages physiques. **Gates B Runtime, C vrai Compiler, D matériel non testées** pour B5. Ce document ne constitue aucune autorisation de bascule de bibliothèque.
