# R88 v0.13.33 — archive expérimentale P2.8, Gate A uniquement

Cette archive est **NON PROMUE**, **NON LAST_GOOD**, **NON QUALIFIÉE WinUAE**. Elle est la copie figée de la candidate active R88. Les mêmes octets R88 sont désormais présents dans **`dist/AMOSPro_AGA.Lib` (candidate active)**, en remplacement de l'ancienne R87 ni `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R84).

La bibliothèque archivée `AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib` est la candidate reconstruite depuis `tools/build_m19_p28_r88_in_memory.py`, exactement **75 040 octets**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`. Les sources et le binaire sont sur la branche **main uniquement**.

Les quatre banques ABK vérifiées sont dans [tests/fixtures/m19_p28](../../tests/fixtures/m19_p28/), et le seul ASC actif est [M19_P28_R88_CACHE_BLIT_FPS_01.asc](../../tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc). Les tests hôte/MC68020 et la Gate A ciblée sont PASS. **Gate B Runtime et Gate C Compiled sur WinUAE : NON TESTÉES.**

Pour tester, **copier temporairement** ce binaire expérimental sous le nom d'installation `AMOSPro_AGA.Lib` dans le slot APSystem approprié, après sauvegarde de la R87 locale ; placer les quatre ABK dans le répertoire courant AMOS. Importer l'ASC via `Project → Merge ASCII`. Revenir ensuite à R87. **R88 est désormais le binaire actif non promu ; R87 est archivée, R84 LAST_GOOD inchangée ; aucune promotion ni release.**

La reproductibilité (SHA256/taille des cinq fichiers, R87 active et R84 `LAST_GOOD`) est vérifiée par `python -B tools/verify_p28_archive.py`. L'ancien artifact Actions de 14 jours n'est plus l'unique support des ressources.
