# M19 P0j-b7 — cycle de vie End après Safe/Disp en attente

**Cible MC68020 / 68EC020 minimum. Gate A PASS : 88 contrôles natifs**, deux implantations AP20 V2 ([GitHub Actions 44185874211](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)). Candidate B7 **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`; source BOBS **21 544 octets**, SHA256 `4f5305f4b42e0af0b30e557adaf38b92fb2347e598dc123c9e7bb11002a4afbf`; **86 commandes, 181 entrées AP20, quatre unités natives, PC16 maximum 28 600 octets**. 600 octets natifs ajoutés, stub Draw index 180 redirigé vers BOBS 177 offset 27 948. Aucun binaire installé ou ASC actif modifié ; B6 reste une candidate créée uniquement en mémoire. Source de provenance B6 : **101 476 octets**, SHA256 `3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91` ; 86 commandes, 181 sections AP20, quatre unités natives.

## Problème reproduit

[Diagnostic native B6 pending Safe/Disp](../tools/test_m19_p0j_pending_close_end_gate_a.py) : les vraies instructions AGA R88 attendent coopérativement Safe et Disp via `GetMsg`/`WaitTOF`, sans `ReplyMsg` sur les réponses ; si les notifications n'arrivent pas dans le délai borné, la fermeture abandonne sans FreeScreenBuffer ou DeleteMsgPort. Lors d'un `End` ultérieur réussi, B6 garde cependant `frame_guard_state.status=DIRTY` : **verrou de présentation périmé**.

## Correctif source-only

[Émetteur B7](../tools/m19_p0j_end_lifecycle_emit.py) · [builder AP20 en mémoire](../tools/build_m19_p0j_end_lifecycle_in_memory.py) · [banc Gate A MC68020](../tools/test_m19_p0j_end_lifecycle_gate_a.py).

- `b7_guarded_draw_entry` conserve l'appel B5 et son résultat numérique `D3=1/0` avec `D2=0` ; il vérifie la signature exacte de l'ancien AGA End calculé depuis A5+$1C8 et n'arme le nouveau callback que lorsque les deux pointeurs End AMOS sont d'origine, P0c ou déjà B7. Après un conflit, le Draw renvoie 0 et pose DIRTY pour empêcher `Aga Swap` de présenter une page incomplète.
- `b7_end_entry` vérifie les callbacks du programme, appelle **l'original pont P0c `program_end_bridge_entry`** puis inspecte l'état réel du Screen. Si End a fermé l'écran : il remet à zéro le verrou Bobs du même propriétaire. Si les notifications n'ont pas permis de fermer : DIRTY reste en place et le callback End est réarmé pour un futur essai.
- L'ancien code natif AGA et les anciens tokens sont byte-identiques. Seul le stub Draw AP20 index 180 change de cible ; la source native BOBS reçoit un suffixe privé. Pas de changement de `Aga Swap`, aucun nouveau token, aucun End artificiel en remplacement de la routine système.

## Scénarios Gate A — exécutés et PASS

Deux implantations natives V2 réelles sous Unicorn MC68020, services AmigaOS simulés ; 1) Draw réussi → End sans notification en vol → ressources libérées une fois et DIRTY effacé ; 2) Close puis End → double-libération interdite ; 3) End avec Safe/Disp manquants → écran/ports conservés, WaitTOF borné, callback B7 conservé, DIRTY maintenu ; 4) réponses différées → nouvelle tentative End → Close réussi, DIRTY effacé ; 5) Close avec notifications différées, puis End ; 6) autre callback ou signature originale corrompue → Draw retourne 0 sans Swap. Contrôles PC16, HUNK/AP20, ABI et décodage 68020. **Résultat PASS : 88 contrôles B7**, en plus des **44 contrôles du diagnostic B6** confirmant que le défaut initial (verrou DIRTY non libéré par End) existait sur le source B6 inchangé. L'ancien binaire AGA, les tokens et les stubs Swap/Close sont byte-identiques, seule l'entrée du token Draw est redirigée dans la candidate en mémoire. [Journal natif PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211).

## Gates restantes / politique

**B Runtime WinUAE, C véritable AMOS Compiler et D Amiga physique : NON TESTÉS.** Dans les Gates B/C, il faudra prouver la fermeture normale, l'absence de freeze/Guru après une permutation et l'absence de libération prématurée ; un `End` avec notifications définitivement absentes doit rester fail-closed mais peut conserver des ressources, donc ce cas n'est **pas une garantie d'absence de fuite**. Les essais doivent être faits sur la même candidate canonique après permission **distincte** de remplacer `dist/AMOSPro_AGA.Lib` et le seul ASC actif ; `LAST_GOOD` ne sera jamais promu automatiquement.


## Campagne Runtime/Compiler à préparer — pas exécutée

**Ne pas lancer B/C avec l'actuelle Lib 96 908 octets** : elle n'inclut ni le token `Aga Bob Draw` ni B7. Après une autorisation explicite de remplacement de la seule bibliothèque canonique et du seul ASC actif, reconstruire **exactement B7** avec le builder SHA indiqué, comparer le SHA du binaire placé dans `APSystem`, puis utiliser **68030/JIT activé** pour l'essai fonctionnel (68020/JIT coupé réservé aux benchmarks). Essais séparés et journaux distincts : 1) ouverture, DB, deux Bobs multi-banques, retour Draw 1, Swap 1, Close ; 2) mêmes opérations mais sortie par `End` sans Close explicite ; 3) changement de page/Swap répété, Safe/Disp différés, fermeture et réouverture ; 4) mêmes cas dans le **vrai AMOS Compiler V2**, sans confondre modèle de dispatch Gate A et binaire compilé. Comparer registres, pixels, allocation Chip, gestion des événements, retour AMOS, absence de freeze/Guru. Un `End` sur notification définitivement absente **n'est pas garanti sans fuite** : tests CPU montrent uniquement le refus de libération prématurée. Ne pas déclarer une Gate B ou C PASS sans logs Runtime/Compiler de la candidate B7 exacte.


## Bascule de la candidate B7 dans le seul slot de travail — autorisation du 17/11/2026

Le jalon B7 exact est livré sous `dist/AMOSPro_AGA.Lib`, **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, identique à la candidate source-only ayant passé la Gate A. **Ce n'est pas une promotion de `LAST_GOOD`.** L'unique programme de campagne est [`tests/current/M19_P0J_B7_DRAW_BC_01.asc`](../tests/current/M19_P0J_B7_DRAW_BC_01.asc), 3 982 octets, SHA256 `f411f13f8213a8ce7b72d7bf205a19cfca7d3ae3ff10087752ddf24f8af7e3af`. L'ancien programme AP20 V2 islands B/C validé est préservé dans l'historique du commit `0423b159` sans modification de son contenu, mais retiré de `tests/current/` (un seul ASC).

**B7 Gate A PASS : 88 contrôles MC68020. Gate B Runtime : NON TESTÉE. Gate C vrai AMOS Compiler : NON TESTÉE. Gate D matériel : NON TESTÉE.** La CI de livraison vérifie la reconstruction B7 et la politique des chemins. Le test utilisateur doit confirmer les quatre images sur deux banques, le mask, le clipping, Draw=1, Swap=1, retour après Close et l'absence de freeze/Guru avec **WinUAE 68030/JIT activé**. Voir la [notice WinUAE](../tests/current/README.md) pour les deux journaux attendus ; les notifications Safe/Disp réellement asynchrones et la sortie `End` sans Close restent des cas supplémentaires à qualifier après le premier banc.
