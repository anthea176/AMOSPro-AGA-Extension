# Test actif — M19 P2.8 R88 : cache AGAPIC / Blitter masqué / FPS complets

**ASC actif unique** : [`M19_P28_R88_CACHE_BLIT_FPS_01.asc`](M19_P28_R88_CACHE_BLIT_FPS_01.asc) (350 lignes, Git blob `a9ee1aaa64d9b588e5b2d6e6134d63ec848e6181`).

**Attention :** cet ASC utilise une **API expérimentale R88 v0.13.33 qui n'existe pas dans R87** : `Aga Cache Blit(CacheBank,X,Y,Mode)`. **R88 est archivée uniquement dans `dist/experimental/` et n'est pas promue ; `dist/AMOSPro_AGA.Lib` reste R87.** Sa construction en mémoire et ses 130 scénarios AP20 sous émulation 68020 ont passé Gate A ; les Gates WinUAE B/C sont **NON TESTÉES**.

## Paquet expérimental

**Candidate active sur `main` :** [R88 à installer](../../dist/AMOSPro_AGA.Lib) (mêmes octets que l'[archive expérimentale R88 Gate A](../../dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib)) et [quatre banques ABK de test](../fixtures/m19_p28/). Vérification des cinq SHA256 par [`tools/verify_p28_archive.py`](../../tools/verify_p28_archive.py). **R88 candidate active, R87 conservée dans `dist/experimental/` et R84 `LAST_GOOD` inchangée. Ce n'est pas une promotion.**

La [R88 candidate active](../../dist/AMOSPro_AGA.Lib) et les [ABK](../fixtures/m19_p28/) sont disponibles directement sur GitHub ; l'artifact Actions reste une alternative. Télécharger **l'artifact GitHub Actions** `M19_P28_R88_GATE_A_ONLY_WINUAE_BUNDLE` de la [CI P2.8](../../.github/workflows/m19-p28-agapic-planar-cache-gate-a.yml), qui comprend :

- `AMOSPro_AGA.Lib` — **R88 expérimentale**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`, **75 040 octets**.
- `M19_P28_R88_CACHE_BLIT_FPS_01.asc` — le programme de référence.
- `AGAPIC_P28_V1_BANK10.abk`, `AGPC_P28_V1_BANK11.abk`, `AGAPIC_P28_V2_BANK12.abk`, `AGPC_P28_V2_BANK13.abk` — les **mêmes pixels 16×16×8** et **masque alpha indépendant** dans les deux formats v1/v2. Le cache AGPC doit être chargé en vraie **Chip RAM** : le wrapper vérifie `TypeOfMem(MEMF_CHIP)`.

Conserver une sauvegarde locale de la bibliothèque installée ; installer **R88 dans le slot APSystem habituel**, redémarrer AMOS. Placer les quatre ABK dans le **répertoire courant** du programme. Ouvrir un AMOS vide et utiliser **Project → Merge ASCII**. Exécuter d'abord en Runtime, puis compiler exactement le même ASC avec **AMOS Compiler V2**. En cas de message d'erreur AMOS, relever la ligne et le message. En cas de Guru, ne pas déclarer PASS.

## Validation intégrée à l'ASC

1. **Huit comparaisons complètes de captures 32×32** : RLE AGAPIC v1/v2 vs Blitter R88 sur le même écran 320×256, couleurs identiques, modes opaques/masqués, X impair et clipping quatre côtés. `PARITY_OK 8`, `PARITY_BAD 0` impératifs avant le benchmark. L'alpha couvre la couleur 0 opaque et une couleur non nulle invisible.
2. **Dessin seul :** 4/8/16 Bobs, 64 répétitions × 2 passes AB/BA, 12 fenêtres, **3 584 dessins RLE et 3 584 dessins Blitter**. Fill, VBL, Swap et staging exclus.
3. **Frames complètes :** 4/8/16 Bobs, **24 frames × 2 passes × 2 méthodes**, 12 fenêtres, **288 Swap réussis**. Le chronomètre inclut `Aga Wait Vbl`, `Aga Blit Fill`, les dessins, les retries et `Aga Swap`. Le coût du pré-décodage/Load reste **hors frames** : ce sont des FPS en cache chaud, pas un temps de démarrage. Aucun FPS n'est annoncé avant mesure.
4. Fermeture AGA, retour AMOS, nettoyage des banques 10..15 uniquement après vérification qu'elles étaient libres, RAM Chip/Fast avant/après.

**Journaux :** `RAM:M19_P28_RUNTIME.TXT` et `RAM:M19_P28_COMPILED.TXT`. Attendu : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `PARITY_OK 8`, `REJECT 2`, `MICRO_RUNS 12`, `RLE_CALLS 3584`, `CACHE_CALLS 3584`, `FRAME_RUNS 12`, `FRAMES_TOTAL 288`, `SWAPS 288`, `CLOSE_RETURNED 1`. Reporter les ticks individuels `DRAW_PASS0/1` et `FRAME_PASS0/1`, la fréquence WinUAE et les retries.

**État actuel :** préflight AMOS strict **PASS (statique)**, Gate A native R88 **PASS 130 cas** ; **WinUAE Runtime/Compiled R88 NON TESTÉES** ; Amiga physique non testé. Le [P2.7 Runtime+Compiled PASS](../passed/M19_P27_R87_CACHE_CPU_BLITTER_01.asc) reste archivé octet pour octet et n'est plus l'ASC actif.

**Aucune modification de `dist/AMOSPro_AGA.Lib` R87 ni `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84, aucune promotion automatique.**
