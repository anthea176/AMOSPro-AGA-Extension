# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 20 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — **M19 B8 S1 SafePort**, **116 104 octets**, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`, 88 commandes / 184 entrées AP20, cinq groupes MC68020 `[142,153,156,177,181]`, PC16 max 29 962. [Builder S1 byte-exact](../tools/build_m19_b8_safe_retry_in_memory.py). B8 ancienne conservée dans Git. |
| **ASC unique de campagne** | [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **11 092 octets**, provenance SHA S1 ; **aucun VBL artificiel dans la boucle**, [protocole WinUAE](../tests/current/README.md). |
| **Validation S1** | **Gate A native MC68020 PASS**, **119 tests** SafePort à 1/2/3 VBL et échecs, deux relocations, [CI 44780312459](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44780312459) ; OS/Gfx simulés. **Gate B WinUAE Runtime NON TESTÉE sur S1 ; Gate C AMOS Compiler NON TESTÉE ; Gate D physique NON TESTÉE.** Ancienne B8 : 405/405 Runtime seulement avec attentes VBL artificielles. |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` — intacte, aucune promotion B8. |

La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. Priorité — qualifier Clear et Update

**API S1 disponible dans la candidate de travail :** `_OK=Aga Bob Clear` restaure le snapshot du back physique ; `_OK=Aga Bob Update` prévalide les images, sauvegarde le décor courant puis dessine tous les Bobs activés sans Swap implicite. Un échec bloque `Aga Swap` par `DIRTY` ; le contrôle de reprise après `Clear` est natif Gate A uniquement. Le premier `Update` exige actuellement au moins un `Aga Bob` SET préalable pour armer le callback End B7 sans dessin. [Rapport B8](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).

**Campagne à réaliser sur WinUAE** : installer la Lib S1 et importer l'ASC sans VBL supplémentaire ; installer la Lib S1 dans le slot `APSystem`, redémarrer AMOS, utiliser `Project → Merge ASCII` sur l'ASC unique, obtenir deux journaux Runtime consécutifs et un nouveau binaire AMOS Compiler avec son propre journal, vérifier les 405 images, 9 étapes, 403 `Clear` et 405 `Update`, et l'absence de traînées, Guru ou freeze au `Close`. Ne pas présenter des résultats de CI ou de préflight comme des Gates B/C.

**Points techniques restant à traiter après les preuves B/C :** premier `Update` sans SET préalable (zéro Bob), génération d'écran et protection ABA hors hooks `Close/End`, coût des deux snapshots complets sur les 1 à 8 plans, et essais sur matériel réel.

## 3. Travaux après M19

| Sujet | Objectif |
| --- | --- |
| **Bobs et animations** | Stabiliser le cycle `Clear → Update → Swap`, les banques et les erreurs, puis optimiser uniquement sur mesures. |
| **Sprites AGA / AMAL** | Évaluer slots matériels, DMA, collisions et intégration éventuelle avec AMAL. |
| **Tilemaps / scrolling (M20)** | Tuiles, caméra, dirty rectangles et Fast/Chip RAM. |
| **Dual playfield (M21)** | Plans indépendants, palettes et scrolling. |
| **Entrées (M22)** | Vérifier d'abord les commandes joysticks natives, sans inventer une API AGA. |
| **C2P / Copper (M23/M24)** | Évaluer accélérations et API avec preuve CPU, WinUAE et Compiler. |

Historique non normatif : [Roadmap archivée](ROADMAP_HISTORY_2026-11-17.md) · [reprise technique](NEXT_SESSION.md).
