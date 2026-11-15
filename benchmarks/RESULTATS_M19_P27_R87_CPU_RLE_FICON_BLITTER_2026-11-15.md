# M19 P2.7 — R87 : résultats WinUAE AGAPIC RLE, FICON8 planaire et Blitter

**Campagne : 15 novembre 2026.** Test source strictement identique : [`M19_P27_R87_CACHE_CPU_BLITTER_01.asc`](../tests/passed/M19_P27_R87_CACHE_CPU_BLITTER_01.asc), **Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`**, SHA256 `6afda81385d1bac54cbf42dd02f8b1145248a4e5a707c5f8152410c18c975e23` (10 009 octets). Même octets que l'ASC actuellement dans `tests/current/` en attendant la prochaine campagne. **R87 v0.13.32 reste candidate, non promue**.

## Sources exactes et validation

- [Journal Runtime brut](M19_P27_RUNTIME.TXT) : 839 octets CRLF, SHA256 `85c5f38559d2d9ec04ec2e413bf37574a0349cf5bbc2dab6aeeec267d0fdf375`, Git blob `52cf0522d279537421c2976f3673995b9ae0bfaa`.
- [Journal Compiled brut](M19_P27_COMPILED.TXT) : 840 octets CRLF, SHA256 `8adfcec76a573b9027c7c539ba449c6072a03da6c0e2d7eb91a4dabb244e6178`, Git blob `0db40ffb486b110fd9d9076cc17fe469395b8ea4`.
- **Gate A (moteur existant)** : native MC68020 9/9 PASS et préflight strict AMOS 21 tests PASS ; [GitHub Actions P2.7](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43727962202) **SUCCESS**. Il s'agit d'une validation source/statique du nouveau banc, **pas** d'un backend natif P2.8.
- **Gate B P2.7 : PASS**, journal `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`.
- **Gate C P2.7 : PASS**, journal `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`.
- Dans **les deux modes** : `PARITY_OK 9`, `PARITY_BAD 0`, `MASK_RUNS 12`, `RLE_CALLS 3584`, `FICON_CALLS 3584`, `BLIT_RUNS 4`, `BLIT_STAGES 4`, `BLIT_CALLS 1024`, `OPAQUE_ICON_CALLS 1024`, `CLOSE_RETURNED 1`, mémoire Chip et Fast identique avant/après. **Gate D Amiga physique : NON TESTÉE.**

Les neuf parités viennent de **comparaisons octet pour octet de captures AGAPIC du même rectangle de 32×32** après deux rendus, opaque/masqué, X décalé, clipping et copie opaque. Elles montrent leur équivalence **pour les neuf scènes testées**, pas un oracle indépendant exhaustif, ni la compatibilité d'un masque alpha indépendant de la couleur zéro. Les journaux attestent la chaîne de version **attendue**, `LIBRARY_EXPECTED` : ils **ne contiennent pas le SHA du binaire réellement installé** ni les paramètres CPU/JIT observés.

## Mesures : AGAPIC v1/v2 RLE vs FICON8 CPU pré-décodé

**Mêmes pixels 16×16, masque index 0, mêmes positions ; 64 répétitions × 2 passes inversées AB/BA.** La préparation des banques, `Aga Blit Fill`, les captures, Swap et VBL sont exclus des chronos. L'opération RLE valide/décode et dessine ; FICON8 dessine directement depuis le format planaire déjà disponible. Les deux méthodes font 3 584 appels de dessin dans chaque exécution.

| Bobs | Runtime RLE | Runtime FICON8 | Gain Runtime | Compiled RLE | Compiled FICON8 | Gain Compiled |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 79 ticks | 32 ticks | **59,49 %** | 74 ticks | 29 ticks | **60,81 %** |
| 8 | 157 | 65 | **58,60 %** | 149 | 56 | **62,42 %** |
| 16 | 317 | 128 | **59,62 %** | 299 | 113 | **62,21 %** |
| **Somme** | **553** | **225** | **59,31 %** | **522** | **198** | **62,07 %** |

**Facteur de débit draw-only** : environ **×2,46 en Runtime**, **×2,64 en Compiled** sur l'ensemble des trois charges. C'est un **gain de temps de rendu** pour ce motif, pas une accélération de FPS affichés garantie.

Détail des deux passes (ticks bruts) :

| Bobs | Runtime RLE pass 0/1 | Runtime FICON pass 0/1 | Compiled RLE pass 0/1 | Compiled FICON pass 0/1 |
|---:|---|---|---|---|
| 4 | 39 / 40 | 16 / 16 | 37 / 37 | 16 / 13 |
| 8 | 79 / 78 | 33 / 32 | 74 / 75 | 28 / 28 |
| 16 | 158 / 159 | 64 / 64 | 150 / 149 | 56 / 57 |

À la conversion **PAL nominale** de 20 ms/tick, pour 16 Bobs et 128 compositions par méthode : Runtime RLE **49,53 ms** / FICON8 **20,00 ms** par composition ; Compiled RLE **46,72 ms** / FICON8 **17,66 ms** par composition. La mesure exclut fond, présentation, synchronisation et autres travaux de frame : **ne pas présenter 50 ou 56,6 comme des FPS effectivement affichés.** Le tick `Timer` reste grossier (20 ms nominal) ; l'ensemble et les passes inversées limitent le bruit sans le supprimer.

## Mesures séparées : 8 Bobs opaques FICON8 CPU vs Aga Blit Copy

Source du Blitter **déjà mise en place dans le même back buffer**, 4 opérations de staging réalisées **hors chrono**, **64 × 2 passes**, 1 024 appels par méthode.

| Mode | FICON8 opaque CPU | Blitter opaque | Réduction temps | Facteur de débit |
|---|---:|---:|---:|---:|
| Runtime | 72 ticks (36 / 36) | 42 ticks (21 / 21) | **41,67 %** | **×1,71** |
| Compiled | 61 ticks (30 / 31) | 33 ticks (16 / 17) | **45,90 %** | **×1,85** |

**Ne pas assimiler cet essai à un Blitter AGAPIC masqué.** Ni mise en Chip permanente, ni coût des mises à jour, ni gestion de deux buffers, ni transparence par masque 1 bit indépendant ne sont comptés dans ce gain.

## Décision technique fondée sur les mesures

**Priorité P2.8 : cache AGAPIC décompressé en mots planaires (et masque de visibilité indépendant), puis backend de dessin CPU et Blitter Chip→Chip mesuré réellement.** Ne pas se limiter à réduire les appels BASIC/Batch : le banc P2.6 n'avait gagné que **2,42 % Runtime** et **0,43 % Compiled**.

Contrat à démontrer **avant tout changement du binaire R87** :
1. **Sémantique inchangée** pour AGAPIC v1/v2, index de couleur 0 parfois opaque, alpha indépendant, découpage non multiple de 16, X arbitraire et clipping aux quatre bords. FICON8 n'est pas une représentation complète de l'alpha AGAPIC.
2. **Pré-décodage hors frame** dans une banque/cache appartenant explicitement à AMOS ; budget Fast/Chip, validation des bornes/TypeOfMem, remplissage atomique, marqueurs ready et mécanisme explicite de re-staging après mutation/Erase/Load/Swap de banque. Pas de pointeur vivant de manière implicite après Erase.
3. **Vrai Blitter masqué** : reprendre `tools/m18_ficon16_chip_blit_emit.py` et `tools/m18_ficon_chip_ap20_emit.py` en vérifiant ABI/Compiler, Safe du back buffer privé, WaitBlit, source Chip et absence de modification du front. Comparer avec un **CPU planaire sans RLE** : la différence marginale Blitter n'est pas celle RLE→cache.
4. **Bench P2.8** : validation pixels avant mesures ; mêmes objets pour AGAPIC RLE, cache CPU et cache Chip/Blitter ; 4/8/16 puis 32 Bobs, temps de staging séparé et amorti ; enfin une vraie frame avec restauration du décor sur deux buffers, Swap et Wait VBL explicités, FPS observés.
5. **Gate A hôte + 68020 + ABI avant WinUAE B/C**, puis matériel D facultatif distinct. Si les bénéfices en contexte complet ne sont pas démontrés, conserver le backend historique.

**GitHub : `main` uniquement.** `dist/AMOSPro_AGA.Lib` R87 (73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`) **inchangée**, R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`) **protégée**. Aucune promotion, branche, tag ou release.
