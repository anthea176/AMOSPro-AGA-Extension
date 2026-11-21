# Tests courants — P2 ALL IN ONE conservé comme régression

L'exemple **P2a–P2e** est publié sous [`examples/`](../../examples/bob_p2_all_in_one/README.fr.md) après validation des **Gates B Runtime et C vrai AMOS Compiler** sur WinUAE le 21 novembre 2026.

**ASC unique conservé pour les tests et les CI :** [M19_P2_ALL_IN_ONE.asc](M19_P2_ALL_IN_ONE.asc), **25 056 octets**, Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`. La [copie publique sans version](../../examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc) contient **exactement les mêmes octets**. La copie [tests/passed](../passed/M19_P2_ALL_IN_ONE.asc), créée lors du commit précédent, reste intacte.

**Journaux originaux, CRLF conservés :** [Runtime (1 632 octets)](../../docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT), SHA256 `864f6b17652033b99f06ec34df3ce85f3a1579bbb52c033d67d62e178852c627` ; [Compiler (1 633 octets)](../../docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT), SHA256 `296f562f73a83d91f419d60a4538e35ef05d55f0c159012949fc5482ce88bf41`.

Dans les deux modes : `RESULT 1`, `ERR 0`, `SWAPS 252`, `COL_CHECKS 8`, `FLIP_PIX0/1 8/12`, `PLANES_PIX0/1 5/5`, `VERDICT PASS`. **121 refus initiaux de Swap récupérés après un VBL** dans chaque essai. Gate D physique et interprété strict non testés.

**Lib P2d et LAST_GOOD P1e inchangées.** Banques **24, 27 et 28** libres requises. [Rapport technique complet](../../docs/M19_P2_ALL_IN_ONE_2026-11-21.md).

**Politique conservée : exactement un ASC de campagne sous `tests/current/`, archives `tests/passed/` protégées, exemples publics à nom sans version M/R et aucune promotion de bibliothèque implicite.** Cette copie de référence pourra être remplacée par une nouvelle campagne décidée explicitement.
