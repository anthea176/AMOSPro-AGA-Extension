# M19 P2e.0 — AMAL original vers Bob AGA (WinUAE Runtime)

**ASC actif unique** : [M19_P2E0_AMAL_BRIDGE.asc](M19_P2E0_AMAL_BRIDGE.asc) — 5 632 octets, SHA256 `bf1d53b54736e990f30ca3a5e79605f2cc88a7a4d0d9886ab166b9a48fe09fa4`.
**Bibliothèque de travail inchangée** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 entrées AP20. **LAST_GOOD P1e protégée**, non promue.

## Exécuter le test

1. Vérifier que l'unique `AMOSPro_AGA.Lib` P2d est installée dans `APSystem`, redémarrer AMOS Professional sous WinUAE AGA (68020 minimum ; la configuration P2d testée était 68030 / JIT activé).
2. Dans un programme vierge : **Project → Merge ASCII** et sélectionner [`M19_P2E0_AMAL_BRIDGE.asc`](M19_P2E0_AMAL_BRIDGE.asc). Les banques **24, 27 et 28** doivent être libres.
3. **Exécuter uniquement en Runtime** (pas d'AMOS Compiler pour ce test individuel). Observer la position et le changement de couleur du Bob. À la sortie, récupérer **`RAM:M19_P2E0_AMAL_BRIDGE.TXT`** avant un nouvel essai.

Le test utilise 240 cycles `Synchro` en mode `Synchro Off` ; les huit octets AMAL (flags, X, Y, image) pilotent un Bob AGA via `Aga Bob` et `Aga Swap`. Il contrôle les getters de Bob, le déplacement X/Y, l'alternance des deux images et des pixels capturés **sur l'ancienne page visible devenue arrière après Swap**. Il arrête AMAL avant d'effacer la banque 28 et ferme l'écran AGA.

**Attendu** : `RESULT 1`, `ERR 0`, `VALID_SAMPLES >= 32`, `PIX_SAMPLES >= 2`, `MOVE_X 1`, `MOVE_Y 1`, `IMAGE1 1`, `IMAGE2 1`, `FLAG_X/Y/A > 0`, `CLOSE_RETURNED 1`, `VERDICT PASS`. `PRG_STATE 1` = Runtime. En cas de refus, joindre le log intégral et la capture/messages AMOS, notamment les erreurs **13** (coordonnées), **14** (getters), **15** (Swap), **16** (capture), **17** (pixel), **19–21** (couverture). Le préflight ne vaut pas Gate B.

## Précédent test P2d

Le précédent ASC P2d a obtenu **Runtime PASS 43/43** (`PRG_STATE 1`, `ERR 0`, `CLOSE_RETURNED 1`). Son fichier exact reste accessible dans [l'historique Git du dernier commit qui le contenait](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/7f78e93b11220199cda4bebff9168fea160ce74d/tests/current/M19_P2D_BOB_AUTO_UPDATE.asc), **sans déplacement automatique vers `tests/passed/`**. Le Compiler est reporté à l'exemple final regroupant P2a–P2e.

[Contrat et protocole P2e.0](../../docs/M19_P2E0_AMAL_BRIDGE_2026-11-21.md).
