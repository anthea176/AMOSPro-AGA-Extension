# Test actif C2P/P2 — disposition mémoire sous WinUAE (14/11/2026)

La bibliothèque R73 v0.13.18 promue `LAST_GOOD` est **inchangée** dans `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib`. Les Gates A/B/C de R73 restent PASS (Gate D non testée). Le test de clôture R73 est consultable dans l'[historique Git au commit cf30d8d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cf30d8d48c73c64bb369810cde9ac2c0a350195d/tests/current/OPT020_P3_R73_INTERPRETED_01.asc).

**Unique ASC actif :** `C2P_P2_R73_BITMAP_01.asc`. N'utilise aucune banque auxiliaire, aucun nouveau token C2P et aucune conversion.

1. Lancer l'ASC dans AMOS **interprété** sous WinUAE AGA 68020+ : `Aga Screen Open(320,256,256,$00021000)`, `Aga Double Buffer`, `Aga Swap` avec retries bornés, puis une boucle `Aga Key` non bloquante ; **Alt+Tab ne ferme pas l'écran**.
2. Pendant l'attente clavier, relever `SB0/SB1` en lecture seule via `tools/c2p_p2_winuae_gdb.py` (WinUAE 6.1 beta 18+ avec serveur GDB) et sauvegarder `c2p_p2_observation.json`. [Guide exact](../../docs/C2P_P2_WINUAE_GDB_PROBE_2026-11-14.md).
3. Une fois le relevé effectué, revenir dans l'écran AGA et appuyer sur **Échap** (RAWKEY `$45`, décimal `69`) pour terminer. Contrôler `RESULT 1`, `CLOSE RETURNED`, mémoire Chip avant/après identique. Ceci est un test de cycle de vie, pas une preuve de conversion.

**Statut actuel :** 18 tests synthétiques hôte PASS ; **Gate B P2 réelle pas encore exécutée**, Gate C/D C2P non testées. `tests/passed/` et les archives restent intacts.
