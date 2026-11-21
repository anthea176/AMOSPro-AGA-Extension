# M19 P2e.0 — AMAL original vers Bob AGA (WinUAE Runtime)

**ASC actif unique** : [M19_P2E0_AMAL_BRIDGE.asc](M19_P2E0_AMAL_BRIDGE.asc) — 6 795 octets, SHA256 `62c94e9560134c0602b6e79b8cb2c78bf5adf207364d85d5a8953201ba61125f`.
**Bibliothèque de travail inchangée** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 entrées AP20. **LAST_GOOD P1e protégée**, non promue.

## Validation actuelle et suite non active (21/11/2026)

**Le troisième ASC P2e.0 de 6 795 octets a passé la Gate B Runtime** sur le journal utilisateur `M19_P2E0_AMAL_BRIDGE(2).TXT` (397 octets, SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`) : `RESULT 1`, `ERR 0`, `VALID_SAMPLES 240`, `SWAPS 241`, `PIX_SAMPLES 29`, `CHG_X/Y/A 239/119/7`, `CLOSE_RETURNED 1`, `VERDICT PASS`. Les champs `FLAG_X/Y/A` issus du mot `Deek` restent diagnostics, non bloquants : `FLAG_WORD_LAST=1792=$0700`. `Peek(_ADDR)` est a qualifier par observation de l'octet fort.

**L'unique ASC actif reste P2e.0**. [P2e.1 deux canaux en conception](../../docs/M19_P2E1_AMAL_TWO_BOBS_DESIGN_2026-11-21.md) n'est disponible qu'en [texte non actif](../design/M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt), en attendant preflight officiel et autorisation de bascule. Il n'y a pas de nouvelle Lib ni de test Compiler.

## Résultat du premier Runtime et correction de diagnostic

**Premier essai WinUAE P2e.0 : FAIL** sur l'ancien ASC de 5 632 octets, SHA256 `bf1d53b54736e990f30ca3a5e79605f2cc88a7a4d0d9886ab166b9a48fe09fa4`. Journal reçu : `PRG_STATE 1`, `FRAME 1`, `SWAPS 1`, `LAST_X 97`, `LAST_Y 101`, `LAST_IMAGE 1`, `ERR 15` (premier `Aga Swap` avec Bob refusé), `CLOSE_RETURNED 1`, `VERDICT FAIL`. Les coordonnées/image AMAL atteignent les getters Bob ; **la cause précise du refus n'est pas prouvée**.

**ASC révisé** : ajoute `Aga Blit Fill(96,100,48,32,0)` sur les **deux back buffers physiques** avant le premier Bob, conformément au scénario initial P2d validé. Le backend B8 refuse une page encore en attente de Safe ; ce refus est une **hypothèse causale**, pas un diagnostic établi. Le nouveau journal expose `BG0`, `BG1` et `SWAP_RESULT` ; `ERR 22/23` indique que l'initialisation de la première/seconde page a été refusée. Le test révisé **n'a pas encore été relancé sur WinUAE**.

## Deuxième essai Runtime et critères corrigés

**Second journal utilisateur :** `M19_P2E0_AMAL_BRIDGE(1).TXT`, 342 octets, SHA256 `918f262be52ba0f12bc1435c8c129be9afc4f972997f4eb238822107c8f6be1d`, obtenu sur l'ASC précédent (6 089 octets). **Runtime fonctionnel pour 240/240 frames, 241 Swaps, 29 vérifications pixel, deux images et les deux axes animés ; sortie propre** : `BG0 1`, `BG1 1`, `SWAP_RESULT 1`, `MOVE_X/Y 1`, `IMAGE1/2 1`, `PIXEL_VALUE 90`, `PIXEL_EXPECTED 90`, `CLOSE_RETURNED 1`. Mais le verdict précédent est **FAIL (`ERR 21`)**, car `FLAG_X/Y/A` valent tous 0.

Le manuel AMOS décrit à l'offset +0 des bits de changement X/Y/A, mais ils **ne se sont pas manifestés dans le mode manuel `Synchro Off` de cette campagne**. Cause non établie. Le nouvel ASC ne falsifie pas les flags : il conserve `FLAG_X/Y/A`, ajoute `FLAG_WORD_LAST`, et comptabilise **`CHG_X`, `CHG_Y`, `CHG_A` en comparant les vraies valeurs de deux cycles consécutifs**. Le code `ERR 21` exige désormais trois compteurs de changements non nuls. **Le correctif a ensuite passé Runtime sous WinUAE (voir validation actuelle en tête)** ; aucun PASS final P2e.0 ne peut être annoncé.

## Exécuter le test

1. Vérifier que l'unique `AMOSPro_AGA.Lib` P2d est installée dans `APSystem`, redémarrer AMOS Professional sous WinUAE AGA (68020 minimum ; la configuration P2d testée était 68030 / JIT activé).
2. Dans un programme vierge : **Project → Merge ASCII** et sélectionner [`M19_P2E0_AMAL_BRIDGE.asc`](M19_P2E0_AMAL_BRIDGE.asc). Les banques **24, 27 et 28** doivent être libres.
3. **Exécuter uniquement en Runtime** (pas d'AMOS Compiler pour ce test individuel). Observer la position et le changement de couleur du Bob. À la sortie, récupérer **`RAM:M19_P2E0_AMAL_BRIDGE.TXT`** avant un nouvel essai.

Les valeurs de vérification supplémentaires attendues sont `BG0 1` et `BG1 1` ; elles ne garantissent pas à elles seules que le Swap des Bobs réussira.

Le test utilise 240 cycles `Synchro` en mode `Synchro Off` ; les huit octets AMAL (flags, X, Y, image) pilotent un Bob AGA via `Aga Bob` et `Aga Swap`. Il contrôle les getters de Bob, le déplacement X/Y, l'alternance des deux images et des pixels capturés **sur l'ancienne page visible devenue arrière après Swap**. Il arrête AMAL avant d'effacer la banque 28 et ferme l'écran AGA.

**Attendu** : `RESULT 1`, `ERR 0`, `CHG_X > 0`, `CHG_Y > 0`, `CHG_A > 0`, `VALID_SAMPLES >= 32`, `PIX_SAMPLES >= 2`, `MOVE_X 1`, `MOVE_Y 1`, `IMAGE1 1`, `IMAGE2 1`, `FLAG_X/Y/A` non bloquants, `CLOSE_RETURNED 1`, `VERDICT PASS`. `PRG_STATE 1` = Runtime. En cas de refus, joindre le log intégral et la capture/messages AMOS, notamment les erreurs **13** (coordonnées), **14** (getters), **15** (Swap), **16** (capture), **17** (pixel), **19–21** (couverture). Le préflight ne vaut pas Gate B.

## Précédent test P2d

Le précédent ASC P2d a obtenu **Runtime PASS 43/43** (`PRG_STATE 1`, `ERR 0`, `CLOSE_RETURNED 1`). Son fichier exact reste accessible dans [l'historique Git du dernier commit qui le contenait](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/7f78e93b11220199cda4bebff9168fea160ce74d/tests/current/M19_P2D_BOB_AUTO_UPDATE.asc), **sans déplacement automatique vers `tests/passed/`**. Le Compiler est reporté à l'exemple final regroupant P2a–P2e.

[Contrat et protocole P2e.0](../../docs/M19_P2E0_AMAL_BRIDGE_2026-11-21.md).
