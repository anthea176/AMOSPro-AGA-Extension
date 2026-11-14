# Test M19 P1 : Bobs AGAPIC, masques et AMAL manuel

**Unique ASC actif :** [M19_P1_AGAPIC_BOBS_01.asc](M19_P1_AGAPIC_BOBS_01.asc). **P0 archivé** sans changement dans [tests/passed/M19_P0_AMAL_BOBS_01.asc](../passed/M19_P0_AMAL_BOBS_01.asc). Le PASS Runtime P0 concerne la première variante alternant les images ; la correction d'image fixe a été confirmée visuellement, sans second journal.

**Binaire : R84 v0.13.29 LAST_GOOD inchangé** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucune nouvelle API ni nouvelle dépendance.

**État P1 : prototype ASC et préflight structurel préparés. Aucune Gate B WinUAE P1, Gate C Compiler ni Gate D physique attestées.**

## Tester sur AMOS / WinUAE

1. Vérifier que les **banques 11 à 19 sont libres**. Importer [M19_P1_AGAPIC_BOBS_01.asc](M19_P1_AGAPIC_BOBS_01.asc) via **Project → Merge ASCII**. Exécuter avec la R84 installée et un CPU **68020 minimum**.
2. Le programme ouvre un écran privé **320×256 en 256 couleurs** et crée six images AGAPIC de **24×24** (v1/v2, index 0 transparent ou opaque). Il teste la superposition par deux captures **1×1** d'un pixel avec ordre de dessin inversé.
3. La démonstration montre **deux Bobs animés** par AMAL manuel (mouvement horizontal/vertical), avec changements d'image toutes les **16/24 frames** et inversion de l'ordre de dessin toutes les 60 frames. On doit voir une image opaque derrière, un objet fixe devant et **quatre images partiellement coupées aux bords**.
4. Laisser le programme terminer ses **240 frames logiques** : **Échap** quitte aussi, mais avant 180 frames la preuve reste incomplète (`ERR 29`). Le fond doit rester propre **sans traînées ni clignotement rapide**.
5. Après le retour à AMOS, transmettre le journal **`RAM:M19_P1_AGAPIC_BOBS_RUNTIME.TXT`** et signaler tout affichage anormal, plantage ou erreur de ligne.

## Résultats attendus

| Test | Valeur pour PASS |
|---|---|
| Capture / métadonnées | `CAP_OK 6`, `META_OK 6` |
| Pixel témoin (ordre de dessin) | `PROBE_OK 1`, `PIXEL_DIFF 1` |
| Mouvement | `FRAME_OK >= 180`, `MOVE_X0 > 0`, `MOVE_Y1 > 0` |
| Animation | `FRAME_SWITCH0 >= 4`, `FRAME_SWITCH1 >= 4` |
| Composition | `ORDER_FLIPS >= 2`, `OVERLAP_FRAMES > 0` |
| Clipping | `CLIP_OK = FRAME_OK` |
| Rendu et fermeture | `DRAW_FAIL 0`, `SWAP_FAIL 0`, `CLOSE_RETURNED 1`, `RESULT 1`, `ERR 0` |

Le contrôle RLE confirme que **le pixel observé diffère** quand l'ordre est inversé ; il ne valide pas tous les pixels du frame. Les deltas Chip/Fast sont mesurés **avant** l'écriture du fichier RAM:. Cette itération P1 ne teste que **8 plans/256 couleurs**. AMOS Compiler sera évalué à la fin du chantier.

[Plan](../../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Roadmap](../../docs/ROADMAP.md) · [Résultats P0](../../docs/M19_P0_RUNTIME_DIAGNOSTIC_2026-11-14.md)
