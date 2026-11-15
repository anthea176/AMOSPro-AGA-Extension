# Test actif unique — M19 P2.7 R87 : AGAPIC RLE / FICON8 / Blitter

**Un seul ASC actif** : [M19_P27_R87_CACHE_CPU_BLITTER_01.asc](M19_P27_R87_CACHE_CPU_BLITTER_01.asc) (402 lignes, SHA Git `e1062818abdfeb2d7e699d8c1dc9e9696250af65`).

**Bibliothèque inchangée** : `dist/AMOSPro_AGA.Lib`, **R87 v0.13.32**, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. Ne pas toucher à `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`).

**Objectif : choisir un backend rapide avant d'ajouter du code natif.** Le même motif 16×16 (indices 0/5/6) est produit en AGAPIC v1 et v2 via capture et en FICON8 via `Aga F Icon Bank Put`. Neuf tests comparent la totalité de deux captures identiquement encodées, sur modes opaque/masqué, X décalé, clipping X/Y et copie opaque au Blitter. En cas de divergence : **FAIL et aucun benchmark**.

Mesures dans un seul programme :

- **4/8/16 Bobs masqués** : AGAPIC v1/v2 RLE individuel vs **FICON8 planaire pré-décodé en Fast/Chip** (CPU), **64 répétitions × 2 passes AB/BA**, 12 séries, **3 584 appels par méthode**.
- **8 Bobs opaques** : FICON8 CPU vs `Aga Blit Copy`, 64 répétitions × 2 passes inversées, 4 séries, 1 024 appels par méthode. Source déjà affichée dans un emplacement non recouvert du **même back buffer**, staging avant la mesure. **Ce n'est PAS un Blitter masqué AGAPIC**, ni un cache Chip persistant. Le coût de staging est exclu : c'est une **borne de comparaison**, pas un FPS réel.
- Aucune allocation, capture, Fill, Wait VBL ou Swap dans les fenêtres chronométrées. Chaque appel doit renvoyer 1.

**WinUAE :** 68020 / 14 MHz / AGA PAL / JIT OFF, AMOS Professional et Compiler V2 ; installer R87 puis redémarrer AMOS ; ouvrir un programme vierge → **Project → Merge ASCII**, exécuter en Runtime puis compiler **le même ASC**. Fichiers :

- `RAM:M19_P27_RUNTIME.TXT`
- `RAM:M19_P27_COMPILED.TXT`

Attendu : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `PARITY_OK 9`, `PARITY_BAD 0`, `MASK_RUNS 12`, `RLE_CALLS 3584`, `FICON_CALLS 3584`, `BLIT_RUNS 4`, `BLIT_STAGES 4`, `BLIT_CALLS 1024`, `OPAQUE_ICON_CALLS 1024`, `CLOSE_RETURNED 1`.

**Statuts** : préflight strict `amos-pro-aga-rules` local **PASS**, modèle hôte des neuf scènes **PASS** ; CI native/statique à vérifier ; **Gates WinUAE B/C P2.7 NON TESTÉES**.

Le benchmark P2.6 qui a passé Runtime et Compiled est [archivé octet pour octet](../passed/M19_P26_R87_DRAW_BENCH_01.asc), résultats dans [benchmarks](../../benchmarks/RESULTATS_M19_P26_R87_DRAW_2026-11-15.md). [Protocole P2.7 détaillé](../../docs/M19_P27_AGAPIC_CACHE_BACKENDS_2026-11-15.md).
