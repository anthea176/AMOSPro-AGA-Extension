# Outils Python actifs — R27 0.9.3 M12 (Gates A+B PASS sur scénarios CPU et AMOS/WinUAE)

## M13 — R28 palette AGA RGB (source en préflight, aucun binaire R28)

- [\`m13_palette_r28_emit.py\`](m13_palette_r28_emit.py) : charge CMAP sans modifier BODY, \`Palette Set\` par \`LoadRGB32\`, \`Palette Get\` par \`GetRGB32\` ; contrôles ColorMap/count/bitplanes, RGB8 et modes HAM/EHB.
- [\`build_m13_palette_r28.py\`](build_m13_palette_r28.py) : builder **en mémoire** depuis l'archive R27 WinUAE-PASS, 3 fonctions AP20 ajoutées en fin de HUNK, ancien code conservé ; \`--emit-base64\` pour audit après PASS.
- [\`test_m13_palette_r28.py\`](test_m13_palette_r28.py) : CPU 68000 Unicorn/Capstone, ABI/ressources, IFF palettes seuls, plages et refus, absence d'écriture bitplane ; **Gate A CI en cours, Gate B WinUAE NON TESTÉE**.
- [Contrat M13](../docs/M13_PALETTE_R28.md). **Fades, cycling et sauvegarde restent à réaliser.** Lib courante R27 0.9.3 inchangée.

## M12 — R27 Safe Blitters (Gate A CPU/CI 403 cas PASS et Gate B AMOS/WinUAE 40 swaps PASS)

- [`m12_blit_safe_r27_emit.py`](m12_blit_safe_r27_emit.py) : même garde `GetMsg(SafePort)` non bloquante avant DMA dans Copy/Fill, préserve `D6`/ABI et le bit Disp.
- [`build_m12_blit_safe_r27.py`](build_m12_blit_safe_r27.py) : builder **en mémoire** reproductible depuis [R26 figée](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib). [Candidate R27 courante](../dist/AMOSPro_AGA.Lib) = [archive versionnée](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), 14 252 octets, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`. **Même table de 31 commandes, neuf segments modifiés : 19/20/21 Blitters plus 6/17/18/31/32/33 relocalisés pour R23.**
- [`test_m12_blit_safe_r27.py`](test_m12_blit_safe_r27.py) : **403 scénarios CPU 68000 PASS** dont Copy/Fill/Clear Safe/Disp, aucun DMA après rejet, ABI, BSR Clear et relocations clavier/souris R23 ; [CI finale 28/28 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220). **Gate B AMOS/WinUAE PASS** sur [40 swaps originaux archivés](../tests/passed/M12_R27_SAFE_BLIT_01.asc).
- [Rapport M12, captures et réserves](../docs/M12_SAFE_BLITTER_R27.md) · [test WinUAE archivé sans modification](../tests/passed/M12_R27_SAFE_BLIT_01.asc) : `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, clignotement des rectangles et sortie normale à la ligne 167. **Aucun `.asc` dans `tests/current/`.** R26/R25/R24 et `LAST_GOOD` R10 intacts ; Compiler, matériel et FPS non validés.


## M11 — R26 `Aga Text` 0.9.2 : validation WinUAE initiale et multi-swap 40 images PASS

- [`build_m11_text_r26.py`](build_m11_text_r26.py) : builder **en mémoire** reproductible depuis R25 figée ; **à la clôture de R26**, la candidate `dist/AMOSPro_AGA.Lib` était égale à [l'archive R26](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. Il ne modifie aucun binaire en étant exécuté.
- [`m11_text_r26_emit.py`](m11_text_r26_emit.py) : nouvelle routine 68000 `TextExtent` + `InitRastPort` + `Text`, sécurité Safe/Disp non bloquante sans `WaitPort` ni `ReplyMsg`.
- [`test_m11_text_r26.py`](test_m11_text_r26.py) : **64 cas CPU 68000 PASS** (ABI, back buffer, Safe/Disp, clipping) lors de la [CI R26 complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061). **Gate B AMOS/WinUAE PASS** sur le [test R26 original archivé](../tests/passed/M11_R26_AGA_TEXT_01.asc), texte vert visible sur fond bleu, `RESULT 1`, fermeture propre.
- [Contrat et résultats R26](../docs/M11_TEXT_R26.md) · [test texte initial PASS](../tests/passed/M11_R26_AGA_TEXT_01.asc) · [test multi-swap PASS archivé](../tests/passed/M11_R26_SAFE_SWAP_02.asc). **40 alternances A/B confirmées**, `PROBE0 39 SWAP0 0`, toutes erreurs nulles, `RESULT 1`. `tests/current/` ne contient aucun `.asc` après archivage du test R27. La R26 et les archives R25/R24/`LAST_GOOD` R10 restent inchangées ; Compiler, matériel réel et longue durée non testés.

### Historique de conception M11 (avant l'implémentation R26 ; non applicable à l'état courant)


- Le diagnostic [`M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc), qui supposait que `Text` AMOS viserait notre écran Intuition AGA, a été **écarté avant exécution WinUAE** et classé historique sans modification des octets.
- **Aucun test actif** dans `tests/current/`. La prochaine étape est une inspection en lecture seule de la source R25 : `BitMap` du back buffer, `RastPort`, `Aga Swap` et cycle de vie. Envisager `graphics.library/Text` seulement avec une cible graphique explicitement liée à ce back buffer. [Étude](../docs/M11_TEXT_COMPAT.md).
- Aucun builder R26 créé. Binaires R25/R24, `LAST_GOOD` R10 et archives `tests/passed/` intacts.


## M10 — R25 0.9.1 : collisions AABB (Gate A CPU/CI + Gate B WinUAE PASS sur scénario)

- [Émetteur natif 68000](m10_rect_overlap_r25_emit.py) : huit entiers, `D3=bh` et `A3+28`, aucun état/OS, arithmétique signée 32 bits sans `x+w` dangereux.
- [Builder reproductible, sans écriture](build_m10_rect_overlap_r25.py) depuis l'archive validée R24 et [préflight CPU](test_m10_rect_overlap_r25.py) : cas de bords, un pixel, inclusions, tailles invalides, extrêmes, symétrie et non-régression R24.
- [Test AMOS visuel R25 archivé et validé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) · [contrat R25](../docs/M10_RECT_OVERLAP_R25.md). Rectangle bleu fixe, mobile vert/rouge ; `FRAMES 409`, `DRAWERR 0`, `RESULT 1`, fermeture correcte. **Gate A CPU/CI PASS 704 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209)), **Gate B AMOS/WinUAE PASS** sur le scénario utilisateur. Aucun `.asc` actif dans `tests/current/`. CI et contrôle statique ne valent pas validation du Compiler ou du matériel.

## M9 — R24 0.9.0 : Hotspot Hit (Gate A CPU/CI + Gate B WinUAE PASS)

- [Émetteur pur 68000](m9_hotspot_r24_emit.py) : six paramètres, bords fin exclusive, arithmétique 32 bits sans débordement, aucun état ni appel OS.
- [Builder pur R24](build_m9_hotspot_hit_r24.py) : depuis R23 **archivée et validée**, ajout d'une seule entrée AP20 + séparateur `GetP`. `dist/AMOSPro_AGA.Lib` candidate R24 et son archive sont comparées en CI.
- [Test CPU préflight](test_m9_hotspot_hit_r24.py) : contrôles 68000 ABI/A3, frontières, zones superposées, int32, R23 inchangée. **Gate A CPU/CI PASS 402 cas (CI (archive CI privée, run #42908096685)), Gate B WinUAE PASS sur le test R24 archivé.** [Contrat](../docs/M9_HOTSPOT_R24.md) · [test WinUAE exact](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc).

## M8 — R23 0.8.7 : IDCMP clavier/souris (Gate A + B PASS sur scénarios testés)

- [`m8_idcmp_r23_emit.py`](m8_idcmp_r23_emit.py) : dispatcher 68000 non bloquant des messages `IDCMP_MOUSEBUTTONS` et `RAWKEY`, FIFO clavier 16 places.
- [`build_m8_idcmp_r23.py`](build_m8_idcmp_r23.py) : builder **pur**, depuis l'archive R22 PASS, reconstruit la candidate R23 sans écrire les archives. Mode `--emit-base64` réservé à la vérification de l'artifact.
- [`test_m8_idcmp_r23_preflight.py`](test_m8_idcmp_r23_preflight.py) : couverture CPU/emulateur native de la capture des clics courts et de la préservation des touches, sans preuve WinUAE.
- [Contrat R23](../docs/M8_IDCMP_R23.md) · [test WinUAE exact archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc). **Gate A CPU/CI PASS (15 cas, CI (archive CI privée, run #42899343161)), Gate B WinUAE PASS** sur clics rapides, FIFO clavier et Ctrl+C à `_WAITK=Aga Wait Key` avec fermeture Intuition. Archive R22 et `LAST_GOOD` R10 inchangées ; Compiler/hardware/stress non testés.

## M8 — R22 0.8.6 : transitions souris natives (CPU + WinUAE PASS sur scénario)

- `m8_mouse_edges_emit.py` : génération déterministe des routines 68000 `Aga Mouse Pressed/Released`, fronts indépendants et contrôle du focus sans toucher à la file clavier.
- `build_m8_mouse_edges_r22.py` : construction reproductible depuis l'archive R21, deux entrées AP20 nouvelles, petite réinitialisation sur ouverture d'écran ; archives et LAST_GOOD inchangées.
- `test_m8_mouse_edges_r22.py` : tests CPU 68000, ABI, états sticky, clavier intact, focus, refus et réouverture.
- [Contrat R22](../docs/M8_MOUSE_EDGES_R22.md) · [test AMOS validé et archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Gate A/CI PASS (25 scénarios, CI (archive CI privée, run #42893816454)) ; Gate B WinUAE PASS sur capture utilisateur.

## M8 — R21 0.8.5 RMBTRAP (CPU/CI PASS 11 cas ; WinUAE PASS utilisateur)

- `build_m8_rmbtrap_r21.py` : builder depuis R20 archivée, change **un seul octet** de code dans `NewWindow.Flags` de `Aga Screen Open` ; R21 archivée, R22 courante sur `main`.
- `test_m8_rmbtrap_r21.py` : simule CPU 68000 et intercepte les flags transmis à `OpenWindow()`; contrôle régressions des boutons R20 et autres segments immuables.
- [Dossier technique R21](../docs/M8_RMBTRAP_R21.md) · [test AMOS archivé](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc).

## M8 — R20 0.8.4 Mouse Buttons (CPU/CI PASS 21 cas ; WinUAE boutons OK mais menu Intuition défectueux)

- `build_m8_mouse_buttons_r20.py` : nouveau builder depuis l'archive R19 figée, ne modifie que l'entrée 29 (`GetP`) et ajoute l'entrée 30 `Aga Mouse Buttons` ; `dist/AMOSPro_AGA.Lib` R20 figée (builder historique ne réécrit pas la candidate R21).
- `test_m8_mouse_buttons_r20.py` : tests CPU 68000 sous Unicorn (appels input.device simulés, masques, ABI/SP, erreurs, R19 inchangé).
- [R20 boutons](../docs/M8_MOUSE_BUTTONS_R20.md), [test AMOS historique](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc).
- **R19 reste archivée :** ne plus exécuter son builder historique en écriture de `dist/` R20 ; la fonction pure `build()` est conservée pour les tests.

## M8 — R19 0.8.3 Mouse X/Y, PASS CPU/CI et AMOS interprété/WinUAE

- `build_m8_mouse_position_r19.py` — builder historique R19 (archive figée) depuis l'archive R18 figée ; reproduit R19 sans écraser la bibliothèque R21 de `main`.
- `test_m8_mouse_position_r19.py` — 76 cas CPU 68000 **PASS et CI générale PASS** (CI générale #42878271256 (archive CI privée)) : coordonnées signées, 320/640/1280, fenêtres déplacées, écran fermé, écran étranger, ABI D3/D2/A3/SP.
- `test_amos_copper_syntax.py` — contrôle statique étendu aux appels nus des fonctions `Aga Mouse X/Y` ; elles doivent être utilisées dans une expression.
- [`M8_MOUSE_R19.md`](../docs/M8_MOUSE_R19.md), [`M8_STATUS.md`](../docs/M8_STATUS.md) — spécification de l'API et procédure WinUAE.

## M7 — R18 0.8.2 Copper Wait/Move/End, PASS CPU/CI et WinUAE (archivé)

- `m7_copper_contract.py` — API de validation Python pour une liste utilisateur de 64 instructions au maximum : `Clear/Wait/Move/End/On/Off` ; autorise seulement COLOR00..COLOR31, RGB4 et les WAIT bornés. **Aucun code Amiga n'est exécuté.**
- `test_m7_copper_contract.py` — tests de grammaire, limites et erreurs ; **pas une preuve 68000/WinUAE**.
- `test_amos_copper_syntax.py` — vérification automatisée : les fonctions Copper AP20 doivent apparaître dans une expression et non comme instructions isolées.
- `build_m7_copper_raster_r18.py` — builder **historique R18**, régénère uniquement son archive validée ; l'appel direct n'écrase plus la Lib R19 courante.
- `test_m7_copper_raster_r18.py` — 26 scénarios CPU 68000 Gate A PASS (ABI/A3, WAIT croissants, COLOR00..31, CEND, refus de liste active). **Gate B WinUAE PASS** sur le test raster corrigé.
- `build_m7_copper_on_off_r17.py` — builder **historique R17**, ne doit plus écraser le candidat R18 ; conserve sa propre archive.
- `test_m7_copper_on_off_r17.py` — tests CPU Intuition MakeScreen/RethinkDisplay, propriétaires, retour ABI, cas d'erreur, retrait et libération.
- `build_m7_copper_clear_r16.py` — builder **historique R16** depuis R15, désormais limité à la régénération de son archive ; ne doit pas écraser l'actif R18.
- `test_m7_copper_clear_r16.py` — test CPU/ABI 68000, simulation OS, pointeurs Screen, allocation et chemins d'échec ; **ne prouve pas WinUAE**.
- Références : [`M7_COPPER_R18.md`](../docs/M7_COPPER_R18.md), [`M7_COPPER_R17.md`](../docs/M7_COPPER_R17.md), [`M7_STATUS.md`](../docs/M7_STATUS.md), [`M7_COPPER_R16.md`](../docs/M7_COPPER_R16.md) et [`M7_COPPER_DESIGN.md`](../docs/M7_COPPER_DESIGN.md).

## Rappel — M6 R15 validé

La racine de `tools/` conserve les builders, tests CPU et outils génériques utilisés ; les anciennes versions restent dans `obsolete/`.

## M6 — R15 Clear validé sous AMOS interprété/WinUAE

- `build_m6_blit_clear_r15.py` — génère le candidat R15 `dist/AMOSPro_AGA.Lib` et son archive R15 depuis **l'archive R14 figée**, sans modifier les versions validées.
- `test_m6_blit_clear_r15.py` — CPU 68000, wrapper A3+12, BSR vers Fill, contenu pixel par pixel, rejets, non-régression R14 Fill et R13 Copy.
- `build_m6_blit_fill_r14.py` — builder **historique R14**, toujours reproductible depuis R13 archivée ; son exécution en ligne de commande ne doit plus écraser le candidat R15.
- `test_m6_blit_fill_r14.py` — contrôles CPU 68000, bitplanes, couleur, bounds, masques, minterms, ABI et sauvegarde de Copy.
- `build_m6_blit_copy_r13.py` — ancien builder R13, conservé pour reproduire la version **déjà validée** de Copy depuis R12 archivée ; ne pas l'exécuter directement comme livraison active R14.
- `test_m6_blit_copy_r13.py` — CPU 68000 (Unicorn), ABI A3/GetP, géométrie, sélection back buffer, appel BltBitMap et WaitBlit. Ce n'est pas une validation graphique sous WinUAE.
- `.github/workflows/artifact-integrity.yml` — vérifie R15, reconstruit le candidat actif, rejoue les tests CPU R14/R13 et contrôle la protection des archives / `LAST_GOOD`.

## M5 — R12 stable et références

- `build_newscreen_a0_r12.py`, `build_ntsc_pal_r10.py`, `ap20_utils.py`, `audit_ap20.py` : construction et vérification R12/R10.
- `test_newscreen_a0_r12.py`, `test_ntsc_pal_r10.py`, `verify_artifacts.py`, `check_no_blocking_waits.py` : contrôles d'intégrité.
- `validate_ilbm.py`, `build_m5_generic.py`, `build_m5_generic_r2.py`, `m68k_emit.py`, `test_m5_generic.py`, `test_m5_generic_r2.py` : composants génériques IFF/CPU.
- `inspect_winuae_dump.py` : diagnostic WinUAE.

`tools/obsolete/` conserve les anciennes générations. Ne pas promouvoir ni écraser la R10 `LAST_GOOD`. Consulter [les détails du R15 Clear](../docs/M6_BLITTER_R15.md), avec R14 Fill et R13 Copy déjà validés sous WinUAE.
