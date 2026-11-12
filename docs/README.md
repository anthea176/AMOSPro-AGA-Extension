# Documentation — AMOSPro-AGA-Extension

**État courant (12/11/2026) : M15bis/R44 v0.11.5 `Aga Mouse Cursor` CANDIDATE Gate A PASS.** 516 scénarios CPU 68000, [CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43208679398), export source strict. [Bibliothèque R44 courante](../dist/AMOSPro_AGA.Lib), 27 460 octets, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`, et [test AMOS/WinUAE R44 actif](../tests/current/M15BIS_R44_MOUSE_CURSOR_01.asc) ; **Gate B PASS confirmée par l'utilisateur (500 bascules, ERR 0, DROP 0, RESULT 1)**. [R43 `LAST_GOOD` préservée](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 27 092 octets, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, Gates A/B PASS et [test archivé](../tests/passed/M15_R43_CIRCLE_01.asc). Gates C/D non testées. [Reprise](NEXT_SESSION.md).. Clôture et promotion différées après la démo M15/M15bis.

## Où commencer ?

| Besoin | Document |
|---|---|
| **Que développons-nous ensuite ?** | [M15bis/R44 — Aga Mouse Cursor, Gates A/B PASS](M15BIS_MOUSE_CURSOR_R44_DESIGN.md) · [candidate R44](../dist/AMOSPro_AGA.Lib) · [test WinUAE R44 validé, en attente d'archivage](../tests/current/M15BIS_R44_MOUSE_CURSOR_01.asc). **R43 reste LAST_GOOD** jusqu'à l'essai de la démo réunissant M15+M15bis. M16 images compressées en Fast RAM ensuite, pas de code M16 engagé · [roadmap](ROADMAP.md). |
| **État exact, binaire et tests actuels** | [Reprise / état courant](NEXT_SESSION.md) · [Rapport M10 R25](M10_RECT_OVERLAP_R25.md) · [Historique M8](M8_STATUS.md) |
| **Copper — architecture et sécurité** | [M7 Copper](M7_COPPER_DESIGN.md) · [R18 raster RGB4, PASS WinUAE](M7_COPPER_R18.md) · [R17 On/Off, PASS WinUAE 3/3](M7_COPPER_R17.md) · [R16 Clear validée](M7_COPPER_R16.md) · [préflight Python](../tools/m7_copper_contract.py) |
| **M9 zones cliquables — R24 PASS WinUAE** | [R24 Hotspot Hit, Gate A+B PASS](M9_HOTSPOT_R24.md) · [Test exact R24 archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc) · [Contrat M8–M10](INTERACTIONS_COLLISIONS.md) |
| **M10 collisions AABB — R25 PASS WinUAE** | [Contrat et validation R25](M10_RECT_OVERLAP_R25.md) · [Test exact R25 archivé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) · [Roadmap](ROADMAP.md) |
| **M11 — R26 AGA Text : Gates A+B PASS sur deux tests** | [Contrat et résultats Safe/Disp](M11_TEXT_R26.md) · [test texte archivé](../tests/passed/M11_R26_AGA_TEXT_01.asc) · [test multi-swap archivé](../tests/passed/M11_R26_SAFE_SWAP_02.asc) · `tests/current/` vide |
| **M12 — R27 Blitters Safe : Gates A+B PASS** | [Rapport M12, capture et réserves](M12_SAFE_BLITTER_R27.md) · [archive R27 0.9.3](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib) · [test original WinUAE archivé](../tests/passed/M12_R27_SAFE_BLIT_01.asc) |
| **M13 — R28 palette RGB24 (candidate)** | [Contrat](M13_PALETTE_R28.md) · [archive R28](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib) · [CI CPU Gate A 159 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618) · [test AMOS R28 en cours](../tests/current/M13_R28_PALETTE_01.asc) · **Gate B non testée** |
| **Souris X/Y et suite interactions** | [R23 IDCMP PASS WinUAE](M8_IDCMP_R23.md) · [R22 Pressed/Released PASS WinUAE](M8_MOUSE_EDGES_R22.md) · [R21 RMBTRAP PASS WinUAE](M8_RMBTRAP_R21.md) · [R20 boutons](M8_MOUSE_BUTTONS_R20.md) · [R19 X/Y PASS](M8_MOUSE_R19.md) · [Interactions M8–M10](INTERACTIONS_COLLISIONS.md) |
| **Architecture de l'extension** | [Architecture technique actuelle](ARCHITECTURE.md) |
| **API et exemples AMOS** | [README principal](../README.md) |
| **Règles de développement** | [EXTENSION_SOURCE_RULES](../EXTENSION_SOURCE_RULES.md) · [Build](BUILD.md) · [Intégrité](ARTIFACT_INTEGRITY.md) |
| **Dernier jalon validé en AMOS/WinUAE** | [M12 R27 (Blitters Safe)](M12_SAFE_BLITTER_R27.md) ; [M11 R26 (texte AGA)](M11_TEXT_R26.md) ; [M10 R25 (collision AABB)](M10_RECT_OVERLAP_R25.md) |

## Anciennes études et preuves

**Archives techniques, non directives actuelles.** Les rapports restent à leurs emplacements historiques pour ne pas casser les références croisées et les fichiers de validation. Le [texte d'architecture historique R10/R12](history/ARCHITECTURE_LEGACY_20261110.md) est le seul document actuellement recopié dans `history/` ; l'[architecture principale](ARCHITECTURE.md) a été réécrite pour décrire la situation actuelle.

### Fondations M0–M4

[Prototype M0](PROTOTYPE_M0.md) · [M1](PROTOTYPE_M1.md) · [Validation M2](M2_VALIDATION.md) · [M3 écran](M3_SCREEN_DESIGN.md) · [M3a](M3A_PROTOTYPE.md) · [M3b](M3B_PLAN.md) · [R1 du prototype M3b](M3B_V004_R1_FIX.md) · [M4 VBL](M4A_WAITVBL.md) · [M4 Double Buffer](M4B_STATUS.md) · [Audit M4 R5](M4B_R5_AUDIT.md) · [Contrat runtime M4](M4B_RUNTIME_SAFETY.md).

### IFF/ILBM M5, clavier, retours d'expérience

[Statut historique M5](M5_STATUS.md) · [Chargeur ILBM](GENERIC_ILBM.md) · [Generic R2](GENERIC_R2.md) · [Inventaire images](ILBM_INVENTORY.md) · [Synchronisation DB](DB_SYNC_R8_TECHNICAL.md) · [Pointeur DB R7](DB_POINTER_R7.md) · [Input Ctrl+C R6](INTUITION_CTRL_C_R6.md) · [Diagnostic R8](R8_INPUT_FOCUS_AUDIT.md) · [R9 paramètres](PICINFO_A3_R9.md) · [R10 repli PAL](R10_NTSC_PAL_FALLBACK.md) · [R11 écran](R11_SCREEN_POSITION.md) · [R12 correction](R12_NEWSCREEN_A0.md).

### Blitter M6 et résultats

[Copie R13](M6_BLITTER_R13.md) · [Fill R14](M6_BLITTER_R14.md) · [Clear R15](M6_BLITTER_R15.md) · [Statut M6](M6_STATUS.md) · [tests AMOS passés](../tests/passed/).

### Données de tests

Les rapports `*_BUILD.json`, `*_CPU_TESTS.json` et `test_console_output.txt` restent à l'emplacement historique. Ils sont des **preuves et entrées de vérification**, pas de nouveaux builds. Les scripts actifs sont indexés dans [tools/README.md](../tools/README.md).

## Règle d'entretien documentaire

1. `ROADMAP.md` : **quoi et pourquoi**, jalons, dépendances, critères d'acceptation. **Pas de journal de corrections R10→R15**.
2. `NEXT_SESSION.md` : dernier état confirmé, liens vers le STATUS du jalon. Ne pas supposer qu'il est à jour sans vérifier le HEAD de `main`.
3. `M*_STATUS.md` : **résultats et limites** des builds et tests ; clôture d'un jalon = archive, pas une nouvelle « priorité active » dans ses anciens documents.
4. Documents techniques M7, puis M8, etc. : conception et contrats dédiés, reliés depuis la roadmap.
5. Ne pas modifier `PROMPT_REPRISE_UNIVERSELLE.md` pour le rattacher à un build ; il demeure générique. Ne pas renommer en masse les rapports ou fichiers JSON sans audit des références.
