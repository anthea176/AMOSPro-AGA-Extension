# Diagnostic Copy : coût de Blitter Wait — M17/R57

**Programme à lancer uniquement en AMOS interprété :** [`copy_wait_32c_r57.asc`](copy_wait_32c_r57.asc). Aucun IFF ni ABK à fournir. Comme pour le benchmark précédent, les extensions **AMCAF** (instruction `Blitter Wait`) et **AGA R57** doivent déjà être installées. **Ne pas modifier le binaire** `dist/AMOSPro_AGA.Lib` ni recompiler ce test : les résultats interprétés et compilés précédents sont presque identiques.

## Objectif et méthode

Comparer sur **le même rectangle 64×48 et 1 200 appels par passage** :

- **A** : `Screen Copy 0,SX,SY,SX+64,SY+48 To 0,DX,DY`, suivi d'un unique `Blitter Wait` après la série.
- **W** : le **même `Screen Copy`** suivi de **`Blitter Wait` après chaque copie** (à l'intérieur du chronomètre).
- **G** : `Aga Blit Copy(SX,SY,DX,DY,64,48)` R57, qui appelle `graphics.library/BltBitMap` puis `graphics.library/WaitBlit` à chaque copie.

Trois répétitions indépendantes par méthode et cas. `Screen Copy` emploie des **bornes de fin exclusives** (`SX+W`, `SY+H`) ; `Bar` emploie des coordonnées finales inclusives (`SX+W-1`, `SY+H-1`).

| Cas | Source | Destination | Particularité |
|---|---|---|---|
| 0 — ALIGNED | (16,24) | (176,24) | Cas témoin du benchmark précédent |
| 1 — SHIFT X +1 | (17,24) | (177,24) | Même géométrie, coordonnées X décalées d'un pixel |
| 2 — DEST Y +72 | (16,24) | (176,96) | Alignement X conservé, destination plus bas |

Toutes les copies sont **sans recouvrement**, dans un écran PAL **320×256×32 couleurs (5 bitplanes)**. Les préparations (nettoyage, dessin du motif source, attente de fin d'activité, sécurisation du back buffer) sont **hors chronométrage**. Il n'y a pas de `Swap` ni de `Wait Vbl` dans les boucles mesurées. Les blocs A, W et G effectuent les mêmes 1 200 copies de la même géométrie ; `Timer` donne **20 ms/tick**. Au total : 3 géométries × 3 méthodes × 3 passages × 1 200 = **32 400 copies**.

Le programme affiche **trois ticks bruts** pour **A**, **W**, **G** et chaque cas, `AGA ERR 0` attendu, puis `COPY WAIT FINISHED - CLOSE RETURNED`. La boucle finale `Do / Wait Vbl / Loop` conserve les résultats sans `Wait Key`. Une capture de l'écran suffit.

## Interprétation

Sur le cas aligné initial, le benchmark précédent mesurait en interprété **A 35 ticks / G 69 ticks** (médianes sur 1 200 copies). Si **W** se rapproche de **G**, la synchronisation explicite ajoutée à chaque appel (et le coût de l'instruction AMCAF elle-même) devient une hypothèse forte. Si **W** reste proche de **A**, les frais de `WaitBlit`, les contrôles AGA ou le chemin interne `BltBitMap` méritent un examen plus approfondi.

**Attention :** `Blitter Wait` (AMCAF) et `WaitBlit` (graphics.library) ne sont pas nécessairement des primitives identiques. De même, les back buffers privés AGA et l'écran natif AMOS ne suivent pas forcément les mêmes chemins. Ces mesures isolent un **surcoût observable d'attente**, pas une preuve définitive de cause. Elles ne justifient **pas** de supprimer `WaitBlit` du code R57 ; sa synchronisation et la garde `Safe` restent protégées.

**État : AMOS interprété / WinUAE PASS sur capture utilisateur du 12/11/2026.** `AGA ERR 0`, `COPY WAIT FINISHED - CLOSE RETURNED`. Médianes aligné **A/W/G = 35/35/69 ticks** ; X +1 **85/85/85** ; destination Y +72 **35/35/69**. [Résultats bruts et conclusions](RESULTATS_COPY_WAIT_R57_2026-11-12.md). **L'ajout de `Blitter Wait` AMCAF à chaque copie AMOS ne suffit pas à expliquer l'écart.** R57 Gates A/B/C déjà acquises ; Gate D matérielle non testée. Le [benchmark Copy initial](copy_32c_r57.asc), ses [résultats interprétés et compilés](RESULTATS_COPY_32C_R57_2026-11-12.md), le [test actif unique](../tests/current/M17_R57_RAST_FILL_01.asc) et `LAST_GOOD` restent intacts.
