# OPT020 — P0 : ouverture du chantier natif 68020+

**Date : 13 novembre 2026 — branche `main` uniquement.** Phase **P0 : audit et contrat de validation**, sans nouvelle bibliothèque et sans prototype 020 exécuté. La R68 v0.13.13 demeure `LAST_GOOD` promue et installable : [51 064 octets / SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), Gates A/B/C PASS, Gate D physique non testée. [CI rapide et complète de promotion : PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43487718297).

## 1. Décision confirmée et périmètre

Le chantier `OPT020` intervient **après M18/R68**, **avant** l'intégration indépendante de `c2p.library`. Son **minimum natif** est **68020 / 68EC020** ; les 68030/040/060 doivent pouvoir exécuter ce même code. **La compatibilité du prochain binaire avec un 68000 seul n'est plus exigée**, conformément à la [roadmap](ROADMAP.md). Cela ne demande **pas** de réécrire par principe toutes les routines 68000 qui fonctionnent déjà sur 020.

Le but est un **gain mesuré, reproductible** sur les routines CPU critiques, avec maintien du résultat pixel exact, des comportements opaques/masqués, du nettoyage, de l'ABI AP20 et de la compatibilité AMOS interprété/Compiler. **Aucun gain n'est actuellement démontré par le simple changement de cible CPU.**

**Hors périmètre P0 :** nouvelle commande AP20, nouveau numéro de révision, nouvel exécutable Compiler, remplacement de R68, sélection automatique CPU8/CPU16/Blitter, fusion avec c2p, optimisation spécifique 040/060, publication Aminet, branche/PR et promotion `LAST_GOOD`.

## 2. État technique vérifié dans les sources

| Zone actuelle | Source / preuves | Conséquence pour OPT020 |
|---|---|---|
| Émetteur d'opcodes | [`tools/m68k_emit.py`](../tools/m68k_emit.py) : encodeur explicitement **68000** | Prévoir un **chemin d'émission 68020 distinct**, avec assemblage/désassemblage vérifiés ; ne pas modifier aveuglément l'encodeur 000 historique |
| Rendu AGAPIC partiel | [`tools/m18_image_region_emit.py`](../tools/m18_image_region_emit.py) : validation RLE en deux passes, calcul de coordonnées, peinture CPU, `MULU.W` dans le noyau | **Premier candidat d'audit et de prototype** : mesurer les coûts de décodage et d'écriture des plans ; examiner indexation 020 et opérations sur 32 bits sans présumer leur rapidité |
| Dessin AGAPIC complet | [`tools/m16_image_draw_r45_emit.py`](../tools/m16_image_draw_r45_emit.py), version corrigée assemblée par les builders R46+ | Comparateur fonctionnel et éventuel second candidat ; ne pas perdre clipping, masques, couleur index 0 ni flags de banques 0/1/3 |
| Fast Icons 16×16 | [`tools/m18_ficon16_native_aligned_emit.py`](../tools/m18_ficon16_native_aligned_emit.py), [`m18_ficon16_native_shifted_emit.py`](../tools/m18_ficon16_native_shifted_emit.py) | Prototyper seulement si un goulot CPU encore mesurable existe ; ne pas casser le staging Chip ni l'ABI |
| CBlock R68 | [`tools/m18_cblock_copy_emit.py`](../tools/m18_cblock_copy_emit.py) : boucle `MOVE.B` / `MOVE.W` et voie Blitter | **Ne pas commencer par une réécriture systématique** : [PERF-02](M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md) montre un avantage fréquent au Blitter ; vérifier la possibilité de gains CPU020 sur des tailles ciblées |
| Validation native | [`tools/test_m18_cblock_copy_native.py`](../tools/test_m18_cblock_copy_native.py) et autres tests existants configurés en **`UC_CPU_M68K_M68000`** | Les Gates A historiques 68000 ne peuvent **pas** prouver l'exécution réelle d'opcodes 020. Obtenir un exécuteur 68020 vérifié ou un banc WinUAE dédié avant de déclarer un Gate A 020 |

### Baseline CBlock déjà mesurée, non réinterprétée

[PERF-02](M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md) est **en AMOS interprété, sans JIT**, 128 Mo de Fast Z3 ; 68020 à 14 MHz et 68030 à 28 MHz. Par exemple : **64×48 / 240 appels** = capture `56` ticks CPU16 contre `47` Blitter sur 020, puis `43` contre `38` sur 030. Pour **16×16 / 1 200 appels**, capture 030 = `66` CPU16 contre `68` Blitter. Les ticks sont des durées cumulées et les écarts de 1 à 3 ticks ne fondent pas une sélection automatique.

Les mesures R60 AGAPIC et R68 CBlock ne portent **pas** sur le même algorithme : aucune comparaison directe des temps par méthode ne permet de quantifier à elle seule un gain 020. Les benchmarks 68030 avec **JIT ON** restent dans un profil séparé.

## 3. Contrat technique 68020

1. **Minimum 68020/68EC020** : pas de dépendance MMU, FPU, `MOVE16` 68040 ni instruction exclusive 030+. Le support des 030/040/060 doit rester compatible avec les seules instructions autorisées au 020.
2. **Prérequis CPU** : préparer la vérification en code 68000-sûr de `ExecBase.AttnFlags & AFF_68020` (**bit 1**), **avant toute instruction 020**. Contrôler réellement l'offset et le contrat d'appel avec les en-têtes NDK et les sources de l'extension avant émission. Le binaire R68 en place n'est pas modifié à cette étape. [Référence AmigaOS NDK ExecBase](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0609.html).
3. **Opérations 020 à évaluer, pas à imposer** : multiplication 32×32, indexation avec facteur d'échelle, instructions de champs de bits. Elles doivent être **assemblées pour 68020**, désassemblées et exécutées sur une cible capable de les émuler réellement ; éviter une prétendue optimisation qui serait encore du pur 68000. L'accès à la Chip RAM reste potentiellement dominant.
4. **ABI et mémoire** : conserver `A3`, `D2/D3`, les registres sauvegardés, A7, les branches relogeables AP20/`Rbsr`, l'enveloppe Compiler V2, le contrôle des tailles et les gardes du back buffer Intuition AGA privé, `Safe`/`WaitBlit`, Fast/Chip.
5. **R68 et son API restent inchangées en P0** : `Method=0` CPU8, `1` CPU16 et `2` Blitter demeurent des choix **explicites** ; aucun mode AUTO. Toute future modification de signature ou ajout de méthode nécessite une décision séparée.

## 4. Plan d'essais (portes de validation)

| Étape | Réalisation | Preuve attendue |
|---|---|---|
| **P0 — en cours** | Audit source + résultats disponibles, environnement/test 020 à choisir, contrat et goulot prioritaire documentés | Ce document et roadmap ; **aucune Gate 020 revendiquée** |
| **P1** | Prototype autonome en mémoire de la boucle critique `Aga Image Region` : variante 000 de référence vs variante 020, sans toucher aux segments validés | Source et encodage 020 reproductibles ; pixels/masques/clipping/canaries identiques ; **exécution 68020 réelle** vérifiée avant qualification Gate A |
| **P2** | Mesures répétées sous WinUAE **68020 14 MHz JIT OFF**, puis **68030 28 MHz JIT OFF**, mémoire/fréquence/mode identifiés pour chaque paire A/B | Au moins cinq passages, médianes, nombre d'appels, dimensions, opaque/masqué, temps de capture/dessin distingués, intégrité et RAM sans fuite ; profil JIT distinct |
| **P3** | Si le gain est reproductible et les cas limites protégés : intégrer dans **une seule** `dist/AMOSPro_AGA.Lib` candidate versionnée, testée avec **un seul** `tests/current/*.asc` | Gate A CPU020 effective + structure AP20/HUNK, B interprété, C compilé (nouvel exécutable), D physique si disponible ; puis autorisation explicite et régression complète avant nouvelle promotion |

**Critère de décision :** ne retenir une optimisation que si elle est plus rapide dans des scénarios identiques **sans** perte de fiabilité et avec un gain suffisamment supérieur à la variabilité du `Timer`. Un assemblage `-m68020` ou un simple décodage Capstone n'est **pas** un test d'exécution 68020. Les résultats historiques 000 restent valables pour R68, pas pour une candidate 020 encore inexistante.

## 5. Fichiers protégés / statut

- `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` : **R68 identiques**, ne pas écrire pour P0.
- `tests/current/M18_R68_COMPILER_FINAL_01.asc` : **seul ASC actif conservé**, pas de nouvel ASC pour P0.
- `tests/passed/`, `archive/`, `dist/experimental/` : **aucune modification**.
- Aucun nouveau binaire, aucune modification API, aucun Compiler ou WinUAE exécuté par l'assistant dans cette phase.

**Étape d'implémentation suivante :** concevoir et valider le **banc d'exécution réelle 68020** et le premier noyau autonome de référence/variante `Aga Image Region` avant toute nouvelle bibliothèque.

**P1 ouvert (13/11/2026) :** [sous-noyau opaque 16 pixels AGAPIC et validation native 68020](OPT020_P1_BITFIELD_PROTOTYPE_2026-11-13.md). La qualification CPU indépendante est en attente au commit initial, aucune version R69 ni test WinUAE revendiqués.

**Résultat P1 du 13/11/2026 :** le [noyau opaque 16 pixels AGAPIC](OPT020_P1_BITFIELD_PROTOTYPE_2026-11-13.md) a été exécuté dans Musashi sur 68000, 68EC020 et 68020 : **768/768 PASS** ([CI 43489837368](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43489837368)). Cela qualifie la faisabilité du sous-noyau uniquement, **pas** le moteur RLE complet, un gain réel de temps ou les Gates AMOS B/C/D.
