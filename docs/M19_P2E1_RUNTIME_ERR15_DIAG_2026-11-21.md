# M19 P2e.1 — Premier log à modes distincts : Runtime ERR 15 (21 novembre 2026)

## Preuve reçue, sans correction

- **Journal utilisateur** : [M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT](evidence/M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT), **567 octets CRLF**, SHA256 `aa9dc89dcd0790e6ca68c25754dd39968d1318d74621a0bd911d275331f7330f`, conservé byte-exact dans Git.
- Il contient `TEST M19 P2E1 AMAL TWO BOBS`, `PRG_STATE 1`, `RUN_MODE RUNTIME`, `RESULT 0`, **`ERR 15`**, `VERDICT FAIL`, `CLOSE_RETURNED 1`.
- **`FRAME 2`**, `VALID_SAMPLES 1`, **`SWAPS 2`** (swap d'initialisation puis 1 frame acceptée), `BG0 1`, `BG1 1`.
- `PIX0 0`, `PIX1 0` : la vérification pixel débute seulement au deuxième Swap ; ces zéros ne prouvent **aucun** défaut pixel.
- Deux canaux actifs : X/Y/image canal 0 **98/101/1**, canal 1 **194/159/2** à l'échec. `RAW0_LAST=RAW1_LAST=1792` (`$0700`), `BYTE0_LAST=BYTE1_LAST=7` ; les six flags comptent 2 lectures.
- Les compteurs `CHG0_X 1`, `CHG1_X 1`, `CHG1_Y 1` corroborent un état AMAL en évolution ; l'état précis des buffers et du masque à l'échec reste **indéterminé**.
- Le log identifie le nouveau format de journalisation `_RUNTIME` apparu dans l'[ASC actif précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/03a571ebd6061b5b93cf10bf3498d538a17aa9e6/tests/current/M19_P2E1_AMAL_TWO_BOBS.asc), **9 134 octets**, Git blob `ac151e107eda820594d16c7821f9e02592fa1b72`. Le log n'inclut pas de SHA d'exécutable ; ne pas affirmer une identité binaire au-delà du scénario/format.

## Analyse source P2d (hypothèses, non preuves)

L'ASC marque `ERR 15` exclusivement si **l'appel `Aga Swap` de la boucle** retourne 0. Le succès des deux `BG` et du premier Swap indique que l'écran a été initialisé et qu'au moins une présentation de Bobs a eu lieu. Aucun code d'échec `ERR 13` (bornes) ou `ERR 14` (getters) n'a été déclenché.

Le code natif `tools/m19_p2d_bob_auto_update_emit.py` effectue un **Update des Bobs avant le Swap** lorsque le mode automatique est actif. Il peut refuser sans présentation :

1. Si `Safe` reste **pending** sur le buffer arrière (`tools/m19_b8_back_selector_emit.py` refuse explicitement d'attendre).
2. Si la transaction B8 préflight/dessin/Finish échoue ou passe en état `DIRTY` (voir `tools/m19_b8_atomic_registered_update_emit.py` et `tools/m19_p0j_swap_barrier_emit.py`).
3. Si le Swap natif contrôlé refuse la présentation d'un frame `READY` ; ce cas est représenté dans `tools/test_m19_p2d_bob_auto_update_model.py` comme récupérable.

**Le journal ne discrimine pas ces causes**. Le passage antérieur à 240 frames avec un ancien nom de log ne prouve pas que le masque, `Amos To Back`, l'état `Safe` ou la Lib sont responsables du nouvel échec. Le passage au nom de log propre est lui-même sans modification de l'algorithme de dessin.

## Nouveau banc diagnostic, sans modification native

[ASC actif M19_P2E1_AMAL_TWO_BOBS.asc](../tests/current/M19_P2E1_AMAL_TWO_BOBS.asc), **10 421 octets**, Git blob `a150f85f952b20c1292b143b5ae9c1b8d016d3e0` :

- Sur **un refus initial** de `Aga Swap` dans la boucle des frames, la version diagnostique enregistre le refus et **attend un VBL avant chaque tentative de reprise**, au plus **4 VBL** / frame. Il n'exécute pas de nouvel `Aga Bob`, `Aga Bob Update` ou dessin dans ces reprises.
- Il journalise `SWAP_REFUSALS`, `SWAP_RECOVERED`, `RETRY_VBLS`, `SWAP_RETRY_LIMIT`, `FIRST_REFUSAL_FRAME`, `LAST_REFUSAL_FRAME`, `LAST_REFUSAL_TRIES`, `LAST_SWAP_RESULT`.
- Si le Swap **reste refusé**, `ERR 15`, `RESULT 0`, `VERDICT FAIL` ; pas de boucle illimitée. Les autres oracles (deux Bobs, 240 frames, pixels, images, cleanup) ne changent pas.
- Si le test finit avec **`ERR 0` et `SWAP_REFUSALS > 0`**, les reprises ont été nécessaires et sont **visibles dans le journal**, pas considérées comme invisibles ni comme une démonstration du mécanisme interne exact.
- Si `ERR 15` persiste malgré les 4 tentatives, examiner la transaction native B8 et les masques ; ne pas augmenter indéfiniment les retries ni réinitialiser `DIRTY` au hasard.

Le journal Runtime futur reste **`RAM:M19_P2E1_AMAL_RUNTIME.TXT`** (Compiler : `RAM:M19_P2E1_AMAL_COMPILED.TXT`). Le fichier du test précédent dans `docs/evidence` ne sera jamais réécrit.

**Validation** : préflight CI à exécuter sur l'ASC diagnostique ; **WinUAE Runtime/Compiler du nouveau banc NON TESTÉS**. Le PASS antérieur P2e.0, le PASS antérieur P2e.1 et le FAIL actuel sont **des observations de périmètres/version distincts**. Lib active P2d et LAST_GOOD P1e inchangées.
