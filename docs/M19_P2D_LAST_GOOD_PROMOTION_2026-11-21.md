# Promotion M19 P2d — LAST_GOOD, clôture du moteur Bob — 21 novembre 2026

## Autorisation et identité binaire

L'auteur demande expressément le **21/11/2026** la promotion de la bibliothèque P2d, après **validation du banc P2 ALL IN ONE en Runtime et avec le véritable AMOS Compiler**, et prépare personnellement une nouvelle release GitHub suivie d'une mise à jour Aminet.

| Propriété | Valeur vérifiée |
| --- | --- |
| Bibliothèque active | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **136 020 octets** |
| Bibliothèque protégée promue | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **octets strictement identiques** |
| Git blob des deux Libs | `8a849b89aae57c2cda0b4db8771034a0978d3e78` |
| SHA256 des deux Libs | `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` |
| API | **100 commandes / 203 entrées AP20** |
| Cible CPU | **Motorola MC68020 / 68EC020 minimum**, AGA |
| Source déterministe | [`tools/build_m19_p2d_in_memory.py`](../tools/build_m19_p2d_in_memory.py), aucune nouvelle reconstruction pour la promotion |
| Ancienne LAST_GOOD P1e | **124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, Git blob `5bb0c476c2b286495a1d0cf7d4415dbbc4eec369`, **préservée dans Git** |
| Identifiant binaire interne | `$VER: AMOSPro_AGA M19 P2d` (**inchangé**) |
| Version publique recommandée | **0.14.0**, **tag/release à publier MANUELLEMENT par l'auteur** |

**Action autorisée :** copier dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` les octets Git **déjà validés** de `dist/AMOSPro_AGA.Lib`, sans modifier le fichier source, les commandes, les tokens, le titre interne, ni `dist/AMOSPro_AGA.Lib`. Contrôle de livraison verrouillé sur **P1e → P2d uniquement**, avec les blobs avant/après exacts. Aucun tag Git, aucune release GitHub/Aminet, aucun upload public par l'assistant.

## Preuves de Gates et limites

| Gate | État | Preuve |
| --- | --- | --- |
| **A — CPU natif, AP20 et CI** | **PASS** | Source P2d déterministe, émulation MC68020, contrôles API/ABI et intégrité |
| **B — WinUAE Runtime** | **PASS** | [`M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT`](evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT), 1 632 octets CRLF, `PRG_STATE 1` |
| **C — vrai AMOS Compiler** | **PASS** | [`M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT`](evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT), 1 633 octets CRLF, `PRG_STATE -1` |
| **D — Amiga AGA physique** | **NON TESTÉE** | Ne pas déclarer une validation matérielle réelle |
| Mode interprété strict | **NON TESTÉ** | Le Runtime WinUAE n'est pas l'interprété strict |

Dans **chacun des deux logs B/C** : `SOURCE_TAG P2_FULL_V1_20261121`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `VALID_SAMPLES 240`, `SWAPS 252`, **8 collisions P2a**, **20 pixels Flip P2b**, **10 pixels Planes P2c**, **Auto Update P2d 1→0**, fermeture AGA `CLOSE_RETURNED 1`.

**Nuance indispensable :** `SWAP_REFUSALS 121`, `SWAP_RECOVERED 121`, `RETRY_VBLS 121` dans chaque mode. Tous les premiers refus se résolvent après un VBL supplémentaire dans ce scénario ; **ne pas présenter ces résultats comme « zéro refus », ni comme une garantie de performance**.

## Promotion protégée et suite

- `tools/active_library.py` garde l'exactitude builder/AP20 et lie désormais `LAST_GOOD_SHA` à `P2D_SHA`.
- `tools/check_aga_delivery_paths.py` n'autorise cette transition que si le commit parent possède **P1e** dans `LAST_GOOD`, **P2d** dans la Lib active, et si le commit proposé possède **P2d dans les deux fichiers**, sans autres candidats autorisés.
- `tools/test_r73_last_good_promotion.py` et `tools/verify_artifacts.py` surveillent la nouvelle LAST_GOOD, tout en conservant la reconstruction des anciennes bibliothèques.
- **Clôture fonctionnelle du chantier Bob P0–P2** : [exemple intégré public inchangé](../examples/bob_p2_all_in_one/README.fr.md), [source de régression unique](../tests/current/M19_P2_ALL_IN_ONE.asc), [copie historique](../tests/passed/M19_P2_ALL_IN_ONE.asc), deux journaux conservés.
- **Prochain chantier : Sprites matériels AGA**, distincts des Bobs : reprendre [l'audit S0](AGA_HARDWARE_SPRITES_S0_AUDIT_2026-11-21.md), vérification NDK/Intuition/Copper/curseur et contrats ABI, avant S1 (Sprite matériel 16 pixels). **Pas de code Sprite dans la release Bob**.
- **Publication 0.14.0** : préparer un paquet `AMOSProAGA.lha` et sa notice `AMOSProAGA.readme` ; l'auteur décide et publie le tag, la release GitHub et l'envoi Aminet. Voir [les brouillons](releases/0.14.0_GITHUB_RELEASE.md).

Les anciens tests partiels, candidats et rapports restent historiques. **La promotion P2d ne prétend pas que toutes les API historiques ont été requalifiées sur ce binaire par le seul exemple intégré.**
