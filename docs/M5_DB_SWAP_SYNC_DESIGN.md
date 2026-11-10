# M5 — suivi des notifications Double Buffer (chantier après R7)

## État runtime confirmé — 10 novembre 2026

**R7 / 0.5.8 : PASS 5/5 sous WinUAE sur la géométrie Fallout
640×512, 4 plans, ModeID 167936, sans IFF Load et sans Swap.**

Test exécuté : `tests/current/M5_DB_POINTER_R7.asc`.

Observations de la capture :
- `OPEN RETURNED 1` ;
- `DB RETURNED 1` ;
- `Aga Wait Key` : raw code 64 ;
- `Aga Screen Close` : terminé ;
- retour normal dans AMOS et `End` ; cinq répétitions sans crash.

Ce PASS valide **l'allocation Double Buffer et la fermeture sans
permutation**. Il ne valide ni `ChangeScreenBuffer`, ni les
notifications Safe/Disp, ni un chargement IFF suivi de Swap.

## Source officielle (AmigaOS V39+)

Les messages `dbi_SafeMessage` et `dbi_DispMessage` sont des
**réponses** envoyées par le système à leurs ports. Après
`GetMsg()`, **NE PAS les transmettre à `ReplyMsg()`** :
ils ont déjà été replied par graphics/Intuition.

Ceci diffère des messages `IDCMP` de la Window, qui doivent
être traités par `GetMsg -> ReplyMsg` exactement une fois.

La documentation `AllocDBufInfo()` précise :

- Safe : ancien bitmap réutilisable pour écrire ;
- Disp : nouveau bitmap affiché, nouveau Swap autorisé ;
- attendre les deux réponses encore en vol **avant de libérer
  ScreenBuffers et MsgPorts**, après la dernière permutation ;
- `WaitBlit()` termine les opérations du Blitter, **pas** les
  échanges asynchrones de messages.

Références :
- https://d0.se/autodocs/graphics.library/AllocDBufInfo
- https://d0.se/autodocs/intuition.library/ChangeScreenBuffer
- https://developer.amigaos3.net/sites/default/files/downloads/2024-02/RKRM%20changes%20and%20additions-%282024-02-21%29.pdf

## Correctif à préparer, pas encore implémenté

**Une seule branche : `codex/intuition-input-r1`.**
Nouvelle révision future dans `dist/experimental/`, sans créer
de nouvelle branche/PR.

Contrat exigé avant construction :

1. Conserver un état explicite Safe/Disp **en attente** dans le
   `DBState` partagé (l'offset +20 existe, mais son utilisation
   réelle dans la R7 doit être vérifiée avant écriture).
2. `Aga Swap` :
   - dépiler les réponses déjà arrivées par `GetMsg` ;
   - ne **pas** les `ReplyMsg` ;
   - ne pas autoriser de nouveau `ChangeScreenBuffer` tant que
     la notification Disp requise n'est pas arrivée ;
   - interdire la réutilisation de l'ancien buffer tant que Safe
     n'est pas arrivé ;
   - ne marquer des notifications en vol qu'après un
     `ChangeScreenBuffer` réussi.
3. `Aga Screen Close`, cleanup d'extension et Ctrl+C :
   drainer toutes les notifications encore attendues ;
   attendre de façon coopérative (`WaitTOF` entre les polls)
   sans `WaitPort`, sans Exec `Wait` et sans boucle CPU ;
   ne libérer aucun `ScreenBuffer` / `MsgPort` tant que le
   système peut encore répondre vers eux.
4. Traiter explicitement les échecs de `ChangeScreenBuffer`,
   les null pointers, le double Close, l'absence de message,
   les réponses retardées et le risque de blocage en fermeture.
   Établir une politique sûre en cas de notification absente
   **avant** d'implémenter un timeout ou une libération.
5. Tests 68000 CPU couvrant toutes ces transitions, chaque
   notification consommée **une seule fois** et aucun
   `ReplyMsg` supplémentaire pour les réponses Safe/Disp.
6. Comparer byte-for-byte les segments Generic ILBM R2 et
   PicInfo à la base R7, sans changement de loader.
7. Seulement après CI : tests WinUAE progressifs,
   d'abord un seul Swap à écran sans chargement, puis
   répétition/Close, enfin Fallout IFF.

**Statut : R7 est validé pour Open + Double Buffer + Close sans
Swap. Le chemin Swap/Close reste bloqué en runtime.**

## Validation utilisateur R8 — 10/11/2026

**PASS 5/5 en WinUAE** : 640×512×4, un `Aga Swap` réussi, `Aga Wait Key=68`, puis `Aga Screen Close` et retour AMOS, sans IFF. Les Swaps multiples, Ctrl+C pendant Swap et IFF Fallout ne sont pas couverts. R8 déjà synchronisée sur la branche unique, binaire 8 772 octets, SHA256 `112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2`. CI R8 indépendante encore à confirmer ; PR #4 reste Draft.

