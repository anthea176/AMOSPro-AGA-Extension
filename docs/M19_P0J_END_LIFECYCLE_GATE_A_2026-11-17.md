# M19 P0j-b7 — cycle de vie End après Safe/Disp en attente

**Cible MC68020 / 68EC020 minimum. Gate A EN ATTENTE.** Aucun binaire installé ou ASC actif modifié ; B6 reste une candidate créée uniquement en mémoire. Source de provenance B6 : **101 476 octets**, SHA256 `3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91` ; 86 commandes, 181 sections AP20, quatre unités natives.

## Problème reproduit

[Diagnostic native B6 pending Safe/Disp](../tools/test_m19_p0j_pending_close_end_gate_a.py) : les vraies instructions AGA R88 attendent coopérativement Safe et Disp via `GetMsg`/`WaitTOF`, sans `ReplyMsg` sur les réponses ; si les notifications n'arrivent pas dans le délai borné, la fermeture abandonne sans FreeScreenBuffer ou DeleteMsgPort. Lors d'un `End` ultérieur réussi, B6 garde cependant `frame_guard_state.status=DIRTY` : **verrou de présentation périmé**.

## Correctif source-only

[Émetteur B7](../tools/m19_p0j_end_lifecycle_emit.py) · [builder AP20 en mémoire](../tools/build_m19_p0j_end_lifecycle_in_memory.py) · [banc Gate A MC68020](../tools/test_m19_p0j_end_lifecycle_gate_a.py).

- `b7_guarded_draw_entry` conserve l'appel B5 et son résultat numérique `D3=1/0` avec `D2=0` ; il vérifie la signature exacte de l'ancien AGA End calculé depuis A5+$1C8 et n'arme le nouveau callback que lorsque les deux pointeurs End AMOS sont d'origine, P0c ou déjà B7. Après un conflit, le Draw renvoie 0 et pose DIRTY pour empêcher `Aga Swap` de présenter une page incomplète.
- `b7_end_entry` vérifie les callbacks du programme, appelle **l'original pont P0c `program_end_bridge_entry`** puis inspecte l'état réel du Screen. Si End a fermé l'écran : il remet à zéro le verrou Bobs du même propriétaire. Si les notifications n'ont pas permis de fermer : DIRTY reste en place et le callback End est réarmé pour un futur essai.
- L'ancien code natif AGA et les anciens tokens sont byte-identiques. Seul le stub Draw AP20 index 180 change de cible ; la source native BOBS reçoit un suffixe privé. Pas de changement de `Aga Swap`, aucun nouveau token, aucun End artificiel en remplacement de la routine système.

## Scénarios Gate A

Deux implantations natives V2 réelles sous Unicorn MC68020, services AmigaOS simulés ; 1) Draw réussi → End sans notification en vol → ressources libérées une fois et DIRTY effacé ; 2) Close puis End → double-libération interdite ; 3) End avec Safe/Disp manquants → écran/ports conservés, WaitTOF borné, callback B7 conservé, DIRTY maintenu ; 4) réponses différées → nouvelle tentative End → Close réussi, DIRTY effacé ; 5) Close avec notifications différées, puis End ; 6) autre callback ou signature originale corrompue → Draw retourne 0 sans Swap. Contrôles PC16, HUNK/AP20, ABI et décodage 68020.

## Gates restantes / politique

**B Runtime WinUAE, C véritable AMOS Compiler et D Amiga physique : NON TESTÉS.** Dans les Gates B/C, il faudra prouver la fermeture normale, l'absence de freeze/Guru après une permutation et l'absence de libération prématurée ; un `End` avec notifications définitivement absentes doit rester fail-closed mais peut conserver des ressources, donc ce cas n'est **pas une garantie d'absence de fuite**. Les essais doivent être faits sur la même candidate canonique après permission **distincte** de remplacer `dist/AMOSPro_AGA.Lib` et le seul ASC actif ; `LAST_GOOD` ne sera jamais promu automatiquement.
