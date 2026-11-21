# M19 P2a — Collisions Bob–Bob sous WinUAE ; P1e préservée

**P2a active — test WinUAE :** [nouvelle bibliothèque](../../dist/AMOSPro_AGA.Lib), **129 544 octets**, SHA256 `e2d149f67da9eb3a8c7222113338a8e0ad3f08fb512792a54b825987e88d92fe`, **97 commandes / 198 entrées AP20**. Nouvelle fonction `Aga Bob Col(A,B,Mode)` : `0` rectangles, `1` masques, renvoie 1/0/-1. [Exemple de test autonome](../../examples/bob_collision.asc) à charger par **Project → Merge ASCII** ; sortie `RAM:M19_P2A_BOB_COL.TXT`. Gate A native et préflight PASS ; Gate B WinUAE et Gate C Compiler NON TESTÉES.

**P1e ancienne active, maintenant LAST_GOOD et banc de régression** — [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), **124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`. 96 commandes, 196 entrées AP20, cinq groupes MC68020. [Gate A native PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44892222083).

**`LAST_GOOD` P1e promue le 21/11/2026 :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) = **124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, binaire strictement identique à la Lib active. Gate A native PASS et Gate B Runtime WinUAE PASS 2/2. Gate C AMOS Compiler et Gate D physique NON TESTÉES. [Rapport de promotion](../../docs/M19_P1E_PROMOTION_2026-11-21.md).

**ASC unique** — [M19_B8_BOB_CLEAR_UPDATE_BC_01.asc](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **27 589 octets ASCII LF**, SHA256 `5172de5ef2c0e3e44d5566f47170ae8a9692bcc30d04490c9d972e1a3ae62e1f`. 405 frames, trois phases Bank Free, 42 getters, quatre phases hotspot, huit mesures de priorité 24 lectures de clipping et trois frames d’édition AGBO. [Banque AGBO 26](M19_P1B_HOTSPOT_BANK26.abk) — 200 octets, SHA256 `8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325`.

## Installation sous WinUAE

1. Sur Windows, synchroniser `main` avec `git pull origin main`. Copier **uniquement** `dist/AMOSPro_AGA.Lib` dans l'emplacement habituel de l'extension AGA sous `APSystem` dans l'environnement Amiga. Vérifier le SHA256 de la copie quand c'est possible. **Redémarrer AMOS** après copie. `LAST_GOOD` P0 ne doit pas changer.
2. Copie `tests/current/M19_P1B_HOTSPOT_BANK26.abk` dans **le répertoire courant d'AMOS**, pour que `Load "M19_P1B_HOTSPOT_BANK26.abk",26` puisse le trouver. **Banques 24 à 27 libres**, pas de données à préserver dans ces numéros.
3. WinUAE **AGA PAL, MC68030, JIT ON**, programme AMOS vierge, puis **`Project → Merge ASCII`** du fichier `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` ; ne pas utiliser `Load` pour ouvrir le source ASCII.
4. Lancer **Runtime** (`PRG_STATE 1`). Vérifier les neuf étapes de Bobs **2/1/0/2/4/8/16/64/16** et les trois phases Bank Free, **puis quatre phases supplémentaires** du Bob masqué n°1 issu de la banque 26 :
   - position logique (110,100) : **image dessinée à (106,97)** ; le point de référence de couleur 7 reste à (110,100) ;
   - position logique (2,2) : **image partiellement coupée en haut à gauche**, origine (-2,-1) ;
   - position logique (32767,32767) : **image totalement hors écran**, réussite de l'Update **sans dessiner** ;
   - position logique (140,90) : **image dessinée à (136,87)**, correctement réactivée.
5. Après les mesures de priorité, le banc lit les pixels (112,103), (113,103) et (114,103) sur chaque page arrière avant le Swap. Les trois frames d’édition AGBO suivent. Fais deux Runtime dans la même session AMOS. Sauvegarde `RAM:M19_P1E_BANK_EDIT.TXT` sous un nom distinct après chaque lancement.

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
| `LIMIT_FRAMES_OK` / `LIMIT_PIXELS_OK` / `LIMIT_REJECT_OK` | `8` / `24` / `8` |
| `EDIT_FRAMES_OK` / `EDIT_PIXELS_OK` / `EDIT_REJECT_OK` | `3` / `9` / `2` |
| `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `4` |

Si le chargement de l'ABK échoue : `ERR 26` (vérifier répertoire, nom, banque 26 libre). Si ses métadonnées hotspot ne correspondent pas : `ERR 27`. Des erreurs **28 à 33** concernent les phases supplémentaires Clear/Update/Swap/getters/comptage. Les codes P1c vont de 34 à 42. `39` signale un échec de capture ou un en-tête inattendu. `40` signale une mauvaise couleur. Le champ `PRIORITY_SAMPLE` enregistre les couleurs lues.

## Sondes P1d

| Réglage, deux pages par cas | Gauche / centre / droite |
| --- | --- |
| Limite globale d’un pixel | `1 / 4 / 1` |
| Limite locale du Bob 1 disjointe de la limite globale | `1 / 5 / 1` |
| Les deux Bobs entièrement coupés | `1 / 1 / 1` |
| Limites effacées | `5 / 4 / 5` |

`ERR 43–46` concerne Clear, réglage ou Update. `47` indique un échec de capture, `48` une couleur inattendue, `49` un total incorrect. Les lignes `LIMIT_SAMPLE` détaillent les couleurs mesurées.

## Sondes P1e

Après insertion de l’ID 3 et capture d’une image de couleur 6, le banc supprime l’intervalle 1–2. Deux Bobs partageant l’ID 1 doivent disparaître. Le Bob utilisant l’ID 3 doit garder sa position et son image. Les sondes aux coordonnées (112,103), (116,103) et (124,103) doivent renvoyer `1 / 6 / 1` sur chacune des deux pages. Après la suppression de la dernière image, la banque doit mesurer 32 octets. La réinsertion de l’ID 3 crée une image transparente et ne réactive pas le Bob. Après réactivation explicite, la troisième sonde doit renvoyer `1 / 1 / 1`.

Pour éviter les faux FAIL, la banque CBlock 27 est effacée entre les captures 8×1 (priorité/clipping) et 16×1 (édition), puis recréée. Le Bob supprimé n°3 est positionné à X=124, hors de l’emprise X=116..123 du Bob conservé. Les journaux WinUAE antérieurs ont relevé `ERR 60` (format CBlock incompatible) puis `ERR 61` (sonde X=120 chevauchant le Bob conservé) ; ces deux échecs concernent l’ancien banc et ne qualifient pas P1e.

Les deux refus mesurés couvrent l’insertion sur un ID occupé et la suppression pendant une frame prête. La génération de la banque conserve sa valeur lors de chaque refus. Les codes 50–62 et les lignes `EDIT_SAMPLE` localisent une éventuelle divergence.

## Gates

| Gate | P1e |
| --- | --- |
| A — MC68020 sous Unicorn, services simulés | **PASS**, commandes natives sur deux placements et préflight de l’ASC |
| B — AMOS Runtime WinUAE | **PASS 2/2** : 405/405 frames, 9/9 pixels P1e, ERR 0, PATH_OK |
| C — véritable exécutable AMOS Compiler | **NON TESTÉ**, reporté sur instruction explicite de l’auteur |
| D — Amiga physique | **NON TESTÉ** |

[Résultats des deux passages P1d](../../docs/M19_P1D_LIMIT_BOB_RUNTIME_2026-11-21.md) · [Résultats des trois passages P1c](../../docs/M19_P1C_PRIORITY_GATES_BC_2026-11-21.md).

Préflight de la campagne : `python -B tools/test_m19_b8_clear_update_asc_static.py`, `python -B tools/test_current_ram_log.py`, `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`. Ces contrôles ne remplacent pas WinUAE.

[Gate B P1a précédente](../../docs/M19_P1A_RUNTIME_B_2026-11-21.md) · [Builder source P1b](../../tools/build_m19_p1b_hotspot_in_memory.py).
