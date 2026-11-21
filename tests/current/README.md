# M19 P1c — Priorité des Bobs sous WinUAE

**P1c active** — [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), **119 916 octets**, SHA256 `658717f41e73ea0410ddcea682929d357df1a80fefd40d8ae0dece037a37613c`. 93 commandes, 190 entrées AP20, cinq groupes MC68020. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44886543740).

**`LAST_GOOD` protégée :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) = **P0**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`. Ne pas remplacer, promouvoir ni utiliser ce binaire à la place de la candidate de test.

**ASC unique** — [M19_B8_BOB_CLEAR_UPDATE_BC_01.asc](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **20 821 octets ASCII LF**, SHA256 `47dd0e205ccaac793aef6103008ee9fe1e9d01771326a14d4b491ae9e952b7ae`. Il exécute 405 frames, trois phases Bank Free, 42 lectures X/Y/image, quatre phases hotspot et huit mesures de priorité. [Banque AGBO 26](M19_P1B_HOTSPOT_BANK26.abk) — 200 octets, SHA256 `8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325`.

## Installation sous WinUAE

1. Sur Windows, synchroniser `main` avec `git pull origin main`. Copier **uniquement** `dist/AMOSPro_AGA.Lib` dans l'emplacement habituel de l'extension AGA sous `APSystem` dans l'environnement Amiga. Vérifier le SHA256 de la copie quand c'est possible. **Redémarrer AMOS** après copie. `LAST_GOOD` P0 ne doit pas changer.
2. Copie `tests/current/M19_P1B_HOTSPOT_BANK26.abk` dans **le répertoire courant d'AMOS**, pour que `Load "M19_P1B_HOTSPOT_BANK26.abk",26` puisse le trouver. **Banques 24 à 27 libres**, pas de données à préserver dans ces numéros.
3. WinUAE **AGA PAL, MC68030, JIT ON**, programme AMOS vierge, puis **`Project → Merge ASCII`** du fichier `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` ; ne pas utiliser `Load` pour ouvrir le source ASCII.
4. Lancer **Runtime** (`PRG_STATE 1`). Vérifier les neuf étapes de Bobs **2/1/0/2/4/8/16/64/16** et les trois phases Bank Free, **puis quatre phases supplémentaires** du Bob masqué n°1 issu de la banque 26 :
   - position logique (110,100) : **image dessinée à (106,97)** ; le point de référence de couleur 7 reste à (110,100) ;
   - position logique (2,2) : **image partiellement coupée en haut à gauche**, origine (-2,-1) ;
   - position logique (32767,32767) : **image totalement hors écran**, réussite de l'Update **sans dessiner** ;
   - position logique (140,90) : **image dessinée à (136,87)**, correctement réactivée.
5. Après le hotspot, vérifier le chevauchement des deux Bobs. L’ASC capture le pixel (113,103) sur la page arrière avant chaque Swap. Les deux Bobs utilisent des couleurs distinctes à ce point. La hauteur logique de l’ancre du Bob 1 est supérieure à celle du Bob 2, et leurs origines de dessin sont dans l’ordre inverse. Exécuter deux Runtime dans la même session AMOS, sauvegarder chaque `RAM:M19_P1C_PRIORITY.TXT` sous un nom distinct avant de relancer et noter le rendu des phases hotspot.

Le champ `LIB_SHA256` reprend l’empreinte attendue dans l’ASC. Vérifier l’empreinte de la Lib installée. Les quatre phases hotspot gardent leur contrôle visuel. Les huit mesures P1c comparent un pixel lu dans la page arrière à sa couleur attendue.

## Résultats attendus, chaque lancement

| Champ de journal | Attendu |
| --- | --- |
| `RUN_MODE` / `PRG_STATE` | `RUNTIME` / `1` |
| `RESULT` / `ERR` / `VERDICT` | `1` / `0` / `PATH_OK` |
| `FRAMES_OK` / `STAGES_OK` | `405` / `9` |
| `CLEAR_OK` / `UPDATE_OK` | `403` / `405` |
| `CLEAR_FAILS` / `UPDATE_FAILS` / `SWAP_FAILS` | `0` / `0` / `0` |
| `OFF_COMMANDS_ISSUED` / `BANK_FREE_CALLS` | `50` / `3` |
| `BANK_FREE_CLEAR_OK` / `BANK_FREE_UPDATE_OK` / `BANK_FREE_SWAP_OK` | `3` / `3` / `3` |
| `BANK_FREE_REARM` | `1` |
| `QUERY_CASES` / `QUERY_VALUES_OK` / `QUERY_VALUES_BAD` | `14` / `42` / `0` |
| `HOTSPOT_BANK` / `HOTSPOT_META_X` / `HOTSPOT_META_Y` | `26` / `4` / `3` |
| `HOTSPOT_FRAMES_OK` / `HOTSPOT_CLEAR_OK` / `HOTSPOT_UPDATE_OK` / `HOTSPOT_SWAP_OK` | `4` / `4` / `4` / `4` |
| `HOTSPOT_GETTERS_OK` / `HOTSPOT_LOAD_ERR` | `12` / `0` |
| `PRIORITY_DEFAULT_OK` / `PRIORITY_SET_OK` / `PRIORITY_REJECT_OK` | `1` / `7` / `16` |
| `PRIORITY_CAPTURE_OK` / `PRIORITY_PIXELS_OK` / `PRIORITY_SWAP_OK` | `8` / `8` / `8` |
| Couleurs, deux lectures par mode (0, 1, 2, 3) | `5,5,4,4,4,4,5,5` |
| `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `4` |

Si le chargement de l'ABK échoue : `ERR 26` (vérifier répertoire, nom, banque 26 libre). Si ses métadonnées hotspot ne correspondent pas : `ERR 27`. Des erreurs **28 à 33** concernent les phases supplémentaires Clear/Update/Swap/getters/comptage. Les codes P1c vont de 34 à 42. `39` signale un échec de capture ou un en-tête inattendu. `40` signale une mauvaise couleur. Le champ `PRIORITY_SAMPLE` enregistre les couleurs lues.

## Gates

| Gate | P1c |
| --- | --- |
| A — MC68020 sous Unicorn, services simulés | **PASS**, 36 scénarios P1c et 98 contrôles intégrés P1b |
| B — AMOS Runtime WinUAE | **PASS sur les mesures, deux journaux** |
| C — véritable exécutable AMOS Compiler | **PASS sur les mesures, un journal** |
| D — Amiga physique | **NON TESTÉ** |

[Résultats des trois passages et portée](../../docs/M19_P1C_PRIORITY_GATES_BC_2026-11-21.md).

Préflight de la campagne : `python -B tools/test_m19_b8_clear_update_asc_static.py`, `python -B tools/test_current_ram_log.py`, `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`. Ces contrôles ne remplacent pas WinUAE.

[Gate B P1a précédente](../../docs/M19_P1A_RUNTIME_B_2026-11-21.md) · [Builder source P1b](../../tools/build_m19_p1b_hotspot_in_memory.py).
