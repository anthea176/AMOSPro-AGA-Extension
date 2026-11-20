# M19 P1a — Gate B WinUAE : trois fonctions de lecture Bob X/Y/I

**Bibliothèque active de TEST :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`, **92 commandes / 188 entrées AP20**, cinq groupes natifs MC68020, PC16 max **31 092**. [Builder exact](../../tools/build_m19_p1a_getters_in_memory.py). **Gate A P1a : PASS 110 contrôles MC68020** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829640179)).

**`LAST_GOOD` protégée :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib), **P0**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`. Ne pas remplacer, promouvoir ou installer `LAST_GOOD` à la place de la candidate pendant ce test.

**Un seul ASC de campagne :** [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **14 871 octets**, ASCII LF. Il conserve le cycle P0 **405 frames en neuf étapes** et **trois phases Bank Free/réactivation**, sans aucun VBL artificiel dans la boucle. Ajoute **14 cas × 3 getters = 42 valeurs** : Bob absent, Off, IDs 0/65, lecture X/Y/image, Free des banques 24/25, conservation des autres Bobs, réactivation.

## Installation / Runtime WinUAE (Gate B)

1. Sur ton Windows, `git pull origin main` ; copier **uniquement** `dist/AMOSPro_AGA.Lib` dans le slot d'extension AGA de `APSystem` sous WinUAE. Vérifier si possible la SHA256 de la copie **sur le disque Amiga ou sur l'image montée**. **Redémarrer AMOS Professional** : un fichier copié sans redémarrage ne garantit pas le chargement de la nouvelle Lib. Ne pas modifier `LAST_GOOD`.
2. WinUAE : **AGA PAL, MC68030, JIT ON**, conformément au dernier environnement P0. Banques **24 et 25 libres**. Dans un programme vierge, choisir **`Project → Merge ASCII`**, puis `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` ; ne pas utiliser `Load` pour ouvrir le texte.
3. **Runtime** (`PRG_STATE 1`) : vérifier la succession visuelle des 9 étapes **2/1/0/2/4/8/16/64/16 Bobs** ; vérifier que le programme se ferme proprement, sans freeze ni traînée. Les getters sont évalués dans le programme et comparés à des valeurs exactes (y compris **-32769**). Le résultat et les erreurs sont inscrits dans **`RAM:M19_P1A_BOB_GETTERS.TXT`**.
4. **Copier le premier journal hors de RAM:** sous un nom distinct, puis **relancer le même programme sans redémarrer AMOS ni `Erase All`**. Conserver le deuxième journal et relever les éventuelles différences de rendu/fermeture. L'étiquette `LIB_SHA256` dans le journal est écrite par l'ASC ; elle **ne mesure pas** le binaire réellement chargé.

## Résultats attendus (pour chaque lancement)

| Champ | Attendu |
| --- | --- |
| `RUN_MODE` / `PRG_STATE` | `RUNTIME` / `1` |
| `RESULT` / `ERR` / `VERDICT` | `1` / `0` / `PATH_OK` |
| `FRAMES_OK` / `STAGES_OK` | `405` / `9` |
| `CLEAR_OK` / `UPDATE_OK` / `OFF_COMMANDS_ISSUED` | `403` / `405` / `50` |
| `CLEAR_FAILS` / `UPDATE_FAILS` / `SWAP_FAILS` | `0` / `0` / `0` |
| `BANK_FREE_CALLS` | `3` |
| `BANK_FREE_CLEAR_OK` / `BANK_FREE_UPDATE_OK` / `BANK_FREE_SWAP_OK` | `3` / `3` / `3` |
| `BANK_FREE_REARM` / `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `1` / `2` |
| **`QUERY_CASES`** | **14** |
| **`QUERY_VALUES_OK`** | **42** |
| **`QUERY_VALUES_BAD`** | **0** |

Les dernières positions exactes vérifiées sont les Bobs actifs n°1 `(0,66,image 1)` et n°2 `(40,66,image 1)`, plus une réactivation du n°1 à `(124,88,image 1)`. Après Off ou Bank Free, les fonctions retournent **-32769**. Une lecture incorrecte marque **`ERR 25`**, **`RESULT 0`**, **`VERDICT FAIL`** ; ce n'est pas une réussite même si les 405 frames se sont affichées.

## Statuts

- **P1a Gate A : PASS** — 110 contrôles natifs MC68020, ABI, AP20 et modèles de relocalisation ; AmigaOS/Blitter simulés, **pas** WinUAE ni un vrai AMOS Compiler.
- **P1a Gate B Runtime : NON TESTÉE**, à réaliser avec les **deux journaux distincts** et une observation visuelle.
- **Gate C Compiler : NON TESTÉE** ; n'exécuter aucun `Compiler` pour qualifier P1a avec l'ancienne Gate C P0/B7.
- **Gate D Amiga physique : NON TESTÉE.**

Préflight statique : `python -B tools/test_m19_b8_clear_update_asc_static.py`, `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, `python -B tools/test_current_ram_log.py`. La qualification Runtime réelle ne peut pas être obtenue via la CI.

[Rapport source P1a](../../docs/M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md) · [historique P0](../../docs/M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md).
