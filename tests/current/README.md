# M19 P1b — Hot Spot Bob : banc WinUAE Runtime / Compiler

**Bibliothèque installable active de TEST :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **119 176 octets**, SHA256 `2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4`. **92 commandes / 188 entrées AP20**, cinq groupes MC68020. [Builder déterministe](../../tools/build_m19_p1b_hotspot_in_memory.py), [rapport P1b](../../docs/M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md). **Gate A MC68020 intégrée PASS (98 contrôles)** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44836896149)) ; **Gate B Runtime WinUAE PASS** ([résultats](../../docs/M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md#résultats-runtime-winue)) ; **Gates C vrai Compiler et D matériel à tester**.

**`LAST_GOOD` protégée :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) = **P0**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`. Ne pas remplacer, promouvoir ni utiliser ce binaire à la place de la candidate de test.

**Un seul ASC de campagne :** [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **17 566 octets, ASCII LF**. Il conserve la boucle historique P0/P1a **405 frames / 9 étapes** et **trois phases Bank Free**, ainsi que les **14 × 3 = 42 lectures X/Y/image**, puis ajoute **quatre phases hotspot**. **Ressource requise :** [`M19_P1B_HOTSPOT_BANK26.abk`](M19_P1B_HOTSPOT_BANK26.abk), banque AmBk AGBO v1 **200 octets**, contenu AGBO **180 octets**, une image masquée **8 × 6 × 8 plans**, `hotspot_x=4, hotspot_y=3`. SHA256 ABK `8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325`.

## Installation sous WinUAE

1. Sur Windows, synchroniser `main` avec `git pull origin main`. Copier **uniquement** `dist/AMOSPro_AGA.Lib` dans l'emplacement habituel de l'extension AGA sous `APSystem` dans l'environnement Amiga. Vérifier le SHA256 de la copie quand c'est possible. **Redémarrer AMOS** après copie. `LAST_GOOD` P0 ne doit pas changer.
2. Copie `tests/current/M19_P1B_HOTSPOT_BANK26.abk` dans **le répertoire courant d'AMOS**, pour que `Load "M19_P1B_HOTSPOT_BANK26.abk",26` puisse le trouver. **Banques 24, 25 et 26 libres**, pas de données à préserver dans ces numéros.
3. WinUAE **AGA PAL, MC68030, JIT ON**, programme AMOS vierge, puis **`Project → Merge ASCII`** du fichier `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` ; ne pas utiliser `Load` pour ouvrir le source ASCII.
4. Lancer **Runtime** (`PRG_STATE 1`). Vérifier les neuf étapes de Bobs **2/1/0/2/4/8/16/64/16** et les trois phases Bank Free, **puis quatre phases supplémentaires** du Bob masqué n°1 issu de la banque 26 :
   - position logique (110,100) : **image dessinée à (106,97)** ; le point de référence de couleur 7 reste à (110,100) ;
   - position logique (2,2) : **image partiellement coupée en haut à gauche**, origine (-2,-1) ;
   - position logique (32767,32767) : **image totalement hors écran**, réussite de l'Update **sans dessiner** ;
   - position logique (140,90) : **image dessinée à (136,87)**, correctement réactivée.
5. À la fin, le programme ferme l'écran, efface les trois banques et écrit `RAM:M19_P1B_HOTSPOT.TXT`. Copier ce journal hors de RAM sous un nom distinct. Relancer une **seconde fois sans redémarrer AMOS ni faire `Erase All`**, sauvegarder le second journal, et relever tout artefact ou défaut d'affichage.

**Attention :** `LIB_SHA256` dans le journal est une **étiquette fixe du source ASC**, pas une mesure cryptographique du fichier réellement chargé. Les getters X/Y/I vérifient les coordonnées *logiques*, tandis que le hotspot s'applique au **dessin** ; le journal ne vérifie pas les pixels de la sortie WinUAE. La **vérification visuelle** des deux décalages reste indispensable pour Gate B. La CI MC68020 compare les pixels avec le modèle, pas un émulateur Amiga réel.

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
| `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `3` |

Si le chargement de l'ABK échoue : `ERR 26` (vérifier répertoire, nom, banque 26 libre). Si ses métadonnées hotspot ne correspondent pas : `ERR 27`. Des erreurs **28 à 33** concernent les phases supplémentaires Clear/Update/Swap/getters/comptage. L'ancienne campagne peut toujours émettre ses erreurs historiques.

## Gates

| Gate | P1b |
| --- | --- |
| A — vrai MC68020 sous Unicorn + OS/Blitter simulés | **PASS (98 contrôles intégrés)**, + 258 contrôles natifs du helper |
| B — vrai AMOS Runtime WinUAE, deux essais + visuel | **PASS fonctionnel** |
| C — véritable exécutable AMOS Compiler | **NON TESTÉ** |
| D — Amiga physique | **NON TESTÉ** |

Préflight de la campagne : `python -B tools/test_m19_b8_clear_update_asc_static.py`, `python -B tools/test_current_ram_log.py`, `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`. Ces contrôles ne remplacent pas WinUAE.

[Gate B P1a précédente](../../docs/M19_P1A_RUNTIME_B_2026-11-21.md) · [Builder source P1b](../../tools/build_m19_p1b_hotspot_in_memory.py).
