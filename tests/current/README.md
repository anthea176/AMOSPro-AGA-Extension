# M19 P2d — Banc WinUAE de mise à jour automatique des Bobs

[AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) M19 P2d, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. La référence protégée [LAST_GOOD](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) est P1e.

1. Copier la Lib dans `APSystem`, puis redémarrer AMOS Pro dans WinUAE en AGA, 68030 avec JIT activé.
2. Dans un programme vierge, importer [M19_P2D_BOB_AUTO_UPDATE.asc](M19_P2D_BOB_AUTO_UPDATE.asc) via **Project → Merge ASCII**. Laisser libres les banques 24, 25 et 27.
3. **P2d Runtime déjà testé : PASS 43/43** sur journal utilisateur du 21/11/2026. La Gate C individuelle est reportée par l'auteur au futur exemple global P2a–P2e (interprété + compilé). Si vous relancez P2d, sauvegarder `RAM:M19_P2D_BOB_AUTO_UPDATE.TXT` avant un autre essai.

Le banc contrôle la présence du Bob produit par Swap seul, la restauration de chaque page après Bob Off et le retour au mode manuel. Il vérifie 40 pixels, le refus de deux modes invalides et le refus de changer de mode avec une page prête. Attendu `PROBE_PREALLOC 1`, `CHECKS 43`, `ERR 0`, `CLOSE_RETURNED 1` et `VERDICT PASS`. `PRG_STATE 1` identifie le Runtime et `PRG_STATE -1` le compilé.

En cas d’échec, `STEP` indique la phase (1 auto, 2 restauration, 3 Swap manuel, 4 Update manuel). `ERR 15` signale un Swap refusé et `ERR 16` une capture refusée. Pour `ERR 17`, `PIXEL`, `VALUE` et `EXPECTED` identifient la première différence. Voir le [contrat P2d](../../docs/M19_P2D_BOB_AUTO_UPDATE_MODEL.md) pour les contrôles MC68020 et AP20.

Le [banc P2c](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/ee0fce258a917d9ee0af015029af8dc285bfe4f7/tests/current/M19_P2C_BOB_PLANES.asc) a passé 34/34 en Runtime avec sa propre Lib.

Le nouveau pont AMAL est [une sonde expérimentale P2e.0](../design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt), **pas** un second ASC de campagne actif et pas une nouvelle bibliothèque. [Protocole](../../docs/M19_P2E0_AMAL_BRIDGE_2026-11-21.md).
