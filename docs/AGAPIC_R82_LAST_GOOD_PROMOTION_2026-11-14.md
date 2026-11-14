# Promotion `LAST_GOOD` — R82 v0.13.27 AGAPIC v2 (14/11/2026)

## Autorisation et périmètre

L'auteur a explicitement autorisé la promotion par **« tu peux promouvoir! »**
après transmission des journaux **WinUAE Runtime** et **AMOS Compiler**, et
validation visuelle du rendu AGAPIC v1/v2. Promotion **sur la branche
`main` uniquement**. Aucun nouveau binaire, token, correctif AMOS, PR,
branche, tag GitHub, publication GitHub Release ou Aminet n'est demandé.

La bibliothèque R82 déjà active dans `dist/AMOSPro_AGA.Lib` devient la
nouvelle **`dist/AMOSPro_AGA_LAST_GOOD.Lib`** par réutilisation du
**même Git blob existant** ; aucun octet du binaire R82 n'est modifié.

## Preuves de validation

| Contrôle | Statut | Données établies |
|---|---|---|
| **Gate A — MC68020/CI** | **PASS** | Source native, ABI, AP20, 69 Image Draw + 52 Init/Capture + 63 Apply/Fade + 70 Region + 19 cas aux offsets définitifs. [CI ciblée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43630405052) |
| **Gate B — WinUAE Runtime** | **PASS** | `RUN_MODE RUNTIME`, `PRG_STATE 1`, CPU 68030, `RESULT 1`, `VERDICT PASS`, tous indicateurs à 1, `ERR 0`, `CLOSE_RETURNED 1`, delta Chip/Fast 0/0. [Journal brut](evidence/AGAPIC_R82_RUNTIME_2026-11-14.TXT) |
| **Gate C — AMOS Compiler** | **PASS** | `RUN_MODE COMPILED`, `PRG_STATE -1`, CPU 68030, mêmes contrôles, `ERR 0`, `CLOSE_RETURNED 1`, delta Chip/Fast 0/0. [Journal brut](evidence/AGAPIC_R82_COMPILED_2026-11-14.TXT) |
| **Affichage WinUAE** | **CONFIRMÉ** | Capture auteur : panneaux multicolores, masques, images et régions recadrées visibles sans anomalie fatale apparente ; observation visuelle, pas une comparaison pixel à pixel |
| **AMOS pur interprété (`PRG_STATE 0`)** | **NON DOCUMENTÉ** | Les deux journaux sont `1` et `-1` ; ne pas inférer une troisième exécution |
| **Gate D — Amiga physique** | **NON TESTÉE** | Ni matériel réel, ni performance comparative chiffrée |

**La qualification est limitée au banc AGAPIC R82 transmis en 320×256×8,
CPU 68030** ; elle ne prouve pas tous les modes d'écran, CPU, configurations
ou l'ensemble des 74 commandes.

[Rapport WinUAE détaillé](AGAPIC_R82_WINUAE_RUNTIME_COMPILER_2026-11-14.md) ·
[Gate A native](AGAPIC_V2_R82_P1_GATE_A_2026-11-14.md).

## Identité stricte des binaires

| Propriété | Valeur |
|---|---|
| Version promue | **R82 v0.13.27** AGAPIC v2, MC68020 minimum |
| Binaire actif | `dist/AMOSPro_AGA.Lib` |
| Référence `LAST_GOOD` | `dist/AMOSPro_AGA_LAST_GOOD.Lib` — **blob identique** au binaire actif |
| Git blob SHA commun | `a19c5cf7bd80418b210cf29f69054c8b6a428a31` |
| SHA256 commun | `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36` |
| Taille | **64 112 octets** |
| API | **74 commandes / 81 entrées AP20** |
| Dernière unité Compiler V2 | **60 972 octets** / plafond **65 534** |
| Marge 16 bits | **4 562 octets** |
| Constructeur | `tools/build_agapic_v2_r82_full_preview.py` — reconstruit byte-exact le binaire |

**R81 v0.13.26 devient la version antérieure historique** : 59 972 octets,
SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`, Git blob `8fc00057b78b2c406af5d0c25c72aaf26102b869`.
Elle reste reconstructible via `tools/build_c2p_r81_opt020.py`, consultable
à son [dernier commit avec `LAST_GOOD` R81](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/aed079ec05102c992d8440f86522e8b8875df8e7/dist/AMOSPro_AGA_LAST_GOOD.Lib).
**Aucune copie supplémentaire dans `dist/` ni modification des archives figées.**

## Garde-fous de promotion

- `active_library.LAST_GOOD_SHA` et
  `verify_artifacts.HASHES["dist/AMOSPro_AGA_LAST_GOOD.Lib"]` épinglés
  sur le nouveau SHA R82.
- Test de promotion exige **`active == LAST_GOOD == build_r82()`**,
  74 commandes, 81 entrées AP20 et l'ABI MC68020.
- R81/R73/R68 restent éprouvés par leurs **constructeurs et SHA historiques**.
  Le seul ASC actif R82 et ses deux fichiers ABK ne changent pas.
- Déclenchement sur `release: R82` du workflow
  **Artifact integrity** puis de la **régression complète**.
  Un contrôle CI ne vaut PASS qu'après publication effective des résultats.

**Statut promotion : référence `LAST_GOOD` migrée vers R82 sur `main`,
avec qualification A/Runtime B/Compiler C sur le périmètre constaté et
Gate D non testée.**
