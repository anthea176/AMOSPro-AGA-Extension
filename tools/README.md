# Outils Python actifs — R23 0.8.7 validée CPU/CI et WinUAE sur scénario ; archives R22/R21 protégées

## M10 — R25 0.9.1 : collisions AABB (Gate A CPU/CI PASS, WinUAE en attente)

- [Émetteur natif 68000](m10_rect_overlap_r25_emit.py) : huit entiers, `D3=bh` et `A3+28`, aucun état/OS, arithmétique signée 32 bits sans `x+w` dangereux.
- [Builder reproductible, sans écriture](build_m10_rect_overlap_r25.py) depuis l'archive validée R24 et [préflight CPU](test_m10_rect_overlap_r25.py) : cas de bords, un pixel, inclusions, tailles invalides, extrêmes, symétrie et non-régression R24.
- [Test AMOS visuel actuel](../tests/current/M10_R25_RECT_OVERLAP_VISUAL_01.asc) et [contrat WinUAE](../docs/M10_RECT_OVERLAP_R25.md) : rectangle fixe bleu, rectangle mobile vert/rouge. **Gate A CPU/CI PASS 704 cas** ([CI préflight](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42915887294)); **Gate B WinUAE NON TESTÉE**.

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
