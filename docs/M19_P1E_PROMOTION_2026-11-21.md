# Promotion M19 P1e — LAST_GOOD — 21 novembre 2026

## Décision et binaire exact

L'auteur a expressément demandé : « non pas de compile promot la lib, met a jour les CI et on continu sur le chantier P2 ». Promotion sur `main` uniquement, sans essai Compiler demandé, sans nouvelle branche, archive ou release.

| Identité | M19 P1e |
| --- | --- |
| Lib active | `dist/AMOSPro_AGA.Lib` |
| LAST_GOOD | `dist/AMOSPro_AGA_LAST_GOOD.Lib` |
| Octets / Git blob | Identiques, **124 444 octets** ; `5bb0c476c2b286495a1d0cf7d4415dbbc4eec369` |
| SHA256 des deux Libs | `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42` |
| CPU natif minimal | MC68020 |
| Commandes et entrées AP20 | 96 / 196 |
| Builder déterministe | [`tools/build_m19_p1e_bank_edit_in_memory.py`](../tools/build_m19_p1e_bank_edit_in_memory.py) |
| Banc ASC corrigé | [`tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), SHA256 `5172de5ef2c0e3e44d5566f47170ae8a9692bcc30d04490c9d972e1a3ae62e1f` |

## Preuve des Gates

**A — PASS** : contrôles MC68020 avec services Amiga simulés, intégrité de la Lib reconstruite. [CI P1e source](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44892222083).

**B — PASS** : deux passages Runtime WinUAE dans la même session AMOS, journaux `M19_P1E_BANK_EDIT(1).TXT` et `M19_P1E_BANK_EDITbis.TXT` remis par l'auteur. **2 412 octets chacun, strictement identiques par comparaison binaire et SHA256** : `3059b4fada16af884616756877ce0512831b752a8a299ad27db922d46b2644f3`.

| Champ du journal | Runtime 1 | Runtime 2 |
| --- | --- | --- |
| PRG_STATE / RESULT / ERR | 1 / 1 / 0 | 1 / 1 / 0 |
| FRAMES_OK / STAGES_OK | 405 / 9 | 405 / 9 |
| QUERY_VALUES_OK / BAD | 42 / 0 | 42 / 0 |
| PRIORITY_CAPTURE_OK / PIXELS_OK | 8 / 8 | 8 / 8 |
| LIMIT_FRAMES_OK / PIXELS_OK | 8 / 24 | 8 / 24 |
| EDIT_FRAMES_OK / PIXELS_OK / REJECT_OK | 3 / 9 / 2 | 3 / 9 / 2 |
| EDIT_SAMPLE 1 et 2 | 1 / 6 / 1 | 1 / 6 / 1 |
| EDIT_SAMPLE 3 | 1 / 1 / 1 | 1 / 1 / 1 |
| CLOSE_RETURNED / BANKS_ERASED | 1 / 4 | 1 / 4 |
| VERDICT | PATH_OK | PATH_OK |

Les FAIL intermédiaires `ERR 60` (capture CBlock 8×1 réutilisée en 16×1) et `ERR 61` (sonde X=120 chevauchant un Bob conservé) ont été corrigés dans l'ASC uniquement, commit [`a4d3b09`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/a4d3b09af5553b4381a0971aaa93f33d17645894), sans modification binaire. Le `LIB_SHA256` dans le texte de l’ASC est une étiquette et ne prouve pas à lui seul le SHA du binaire installé sous WinUAE.

**C — NON TESTÉE**, véritable AMOS Compiler explicitement reporté par l'auteur. **D — NON TESTÉE**, matériel Amiga réel. Les Gates ne sont pas transférables.

## Protection de la LAST_GOOD

La prédécesseure P0 SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, blob `6e23a1dc783145adb41f1a9b02fc6fc8f3b80ff2`, reste retrouvable dans Git. Le contrôle de livraison n'autorise que les transitions exactes préalablement approuvées R84→P0 et P0→P1e. Une future promotion P2 nécessitera une nouvelle instruction expresse.

## Reprise du chantier P2

Première cible prévue : collisions Bob–Bob, d'abord rectangles puis masques pixel-exacts. Vérifier banque/image AGBO, états OFF, hotspot, limites globales/locales, coordonnées signées, ordre et deux pages ; aucune collision ne déclenche de Swap. Retournements H/V non destructifs prévus ensuite. Les signatures AP20, ABI et codes de retour restent à définir avant une éventuelle implémentation native. [Contrat P2](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p2--fonctions-avancées--compatibilité-progressive).
