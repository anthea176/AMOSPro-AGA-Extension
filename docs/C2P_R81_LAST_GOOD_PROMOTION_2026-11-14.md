# Promotion LAST_GOOD — R81 v0.13.26 C2P OPT020 (14/11/2026)

## Autorisation et périmètre

L'auteur a explicitement répondu **« promotion ok »** après avoir transmis les journaux WinUAE Runtime et AMOS Compiler de **R81**. Promotion limitée à la branche **`main`**. **Aucune nouvelle version, branche, PR, tag, release GitHub, publication Aminet, recompilation AMOS ou campagne de mesures de vitesse** n'est demandée.

L'actuelle candidate R81 est **promue telle quelle** ; la promotion ne modifie ni les commandes, ni l'ABI AP20, ni l'ASC de test actif, ni les sources natives.

## Preuves de qualification

| Gate | Statut | Périmètre précis |
| --- | --- | --- |
| **A — CPU natif / CI** | **PASS** | MC68020, ABI et AP20, 22 scénarios Blit, 14 Zoom, 15 lignes IFF, garde CPU68000, liens et registres. [CI générale R81](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43617105778) |
| **B — WinUAE Runtime** | **PASS** | [Journal `C2P_R81_RUNTIME.TXT`](C2P_R81_RUNTIME_GATE_B_2026-11-14.md) : `PRG_STATE 1`, CPU 68030, IFF 320×256×8/256 couleurs, 14/14 pixels, IFF/Chunky/Blit/Zoom/refus/Close/ReOpen/Échap PASS, `ERR 0`, Chip/Fast delta **0/0**, `CLOSE_RETURNED` |
| **C — AMOS Compiler** | **PASS** | [Journal `C2P_R81_COMPILED.TXT`](C2P_R81_COMPILER_GATE_C_2026-11-14.md) : `PRG_STATE -1`, CPU 68030, même scénario 8 plans, 14/14 pixels, `ERR 0`, Chip/Fast delta **0/0**, `CLOSE_RETURNED` |
| **D — Amiga physique** | **NON TESTÉE** | Aucun essai sur matériel Amiga réel revendiqué |

La qualification B/C porte sur **ce scénario** : elle ne généralise pas le PASS Runtime/Compiler aux profondeurs 4–7 plans, aux autres IFF, à tous les CPU ou à toutes les 70 commandes. **Aucun gain de vitesse quantifié n'est revendiqué.**

## Identité stricte des binaires

| Propriété | Valeur |
| --- | --- |
| Version | **R81 v0.13.26** — C2P OPT020 (MC68020 minimum) |
| Source des octets | `dist/AMOSPro_AGA.Lib`, constructeur déterministe `tools/build_c2p_r81_opt020.py` |
| `dist/AMOSPro_AGA_LAST_GOOD.Lib` | **Même blob Git et mêmes octets que le binaire de travail R81** |
| Taille | **59 972 octets** |
| SHA256 commun | `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4` |
| Git blob SHA commun | `8fc00057b78b2c406af5d0c25c72aaf26102b869` |
| Surface publique | **70 commandes / 77 entrées AP20** |
| Noyaux optimisés | Entrées natives **73 (Blit)**, **74 (Zoom)** et **75 (IFF → Chunky)** |

**Pas de reconstruction pour la copie** : le pointeur `LAST_GOOD` réutilise strictement le **blob SHA existant** de la bibliothèque active. La reproductibilité est vérifiée séparément par le constructeur R81 à SHA épinglé.

## Archives et garde-fous

- **Ancienne LAST_GOOD : R73 v0.13.18**, 51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`, Git blob `2d764b08cdde34b3b1dcbe2c698a8cc2499dd3d0` ; [ancienne référence accessible dans l'historique Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7a11afc284840e61de52d83c2d0de7b368b696e/dist/AMOSPro_AGA_LAST_GOOD.Lib). Aucun doublon d'archive créé.
- Les anciens constructeurs R68/R73 et les sources historiques R78/R79/R80 restent **inchangés** ; ils continuent de reconstruire leurs propres sorties à SHA épinglé, sans dépendre du pointeur mobile `LAST_GOOD`.
- Les contrôles d'intégrité `tools/active_library.py`, `tools/verify_artifacts.py`, `tools/build_aga_current.py`, ainsi que les régressions AP20, P1/P2/P3 et Compiler V2, doivent exiger l'égalité **`active == LAST_GOOD == build_r81()`** et préserver les validations historiques.
- L'unique ASC actif reste `tests/current/C2P_R80_IFF_CHUNKY_01.asc` (son identifiant et ses rapports indiquent R81). Les archives et `tests/passed/` restent intacts.
- **Contrôle de promotion sur commit `release: R81`** : workflow GitHub `Artifact integrity`, puis régression historique complète `pre_release_full`, sans requalification manuelle supplémentaire du Compiler. La preuve CI exacte sera liée après son achèvement.

**Statut : promotion R81 `LAST_GOOD` autorisée et préparée ; validation CI du SHA de promotion à constater.**
