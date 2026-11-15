# M19 P2.0 — Résultat AMOS Runtime / WinUAE 68030 (15/11/2026)

> **Gate B : PASS**, exclusivement pour le prototype de gestionnaire BASIC P2.0 en 320×256, 256 couleurs / 8 plans, tel que décrit par le journal utilisateur `M19_P2_OBJECTS_RUNTIME.TXT`. Programme de référence : [`tests/current/M19_P2_OBJECTS_01.asc`](../tests/current/M19_P2_OBJECTS_01.asc). Bibliothèque de référence : **R84 v0.13.29 LAST_GOOD**, inchangée (76 commandes, 85 entrées AP20).

## 1. Contexte

Le premier chargement P2.0 avait rencontré un `Syntax error` en raison de labels `SORT_OBJECTS` et analogues confondus avec des mots-clés AMOS. L'ASC actif a ensuite reçu des labels et appels `Gosub` à préfixe `_` (commit `18b01a6`). Le préflight a été renforcé (commit `c65c820`) : collision de labels et sous-routines valides après `End`. Le fichier journal maintenant transmis atteste une exécution **Runtime PASS** après ces corrections ; il ne contient toutefois pas de hash du source importé, et ne prouve donc pas son identité octet par octet avec le fichier Git.

L'auteur a fourni **un fichier de résultats**, pas de vidéo ni de capture de cette exécution. Les observations visuelles continues (fluidité, absence de scintillement, fond intégralement propre sur toutes les frames) ne sont donc pas établies indépendamment par ce seul journal.

## 2. Journal reçu

| Champ | Valeur |
|---|---:|
| `TEST` | `M19_P2_OBJECTS_01` |
| `VERSION` | `R84 V0.13.29 LAST_GOOD` |
| `RUN_MODE` / `PRG_STATE` | `RUNTIME` / 1 |
| `CPU` / `CPU_ATTNFLAGS` | `68030` / 32823 |
| `RESULT` / `VERDICT` / `ERR` | **1 / PASS / 0** |
| `CAP_OK` / `ICON_OK` | 6 / 4 |
| `PROBE_OK` / `PIXEL_DIFF` | 1 / 1 |
| `CREATE_COUNT` / `NEXT_ID` | 5 / 5 |
| `DELETE_COUNT` / `STALE_ID_REJECT` | 1 / 1 |
| `BAD_FRAME_REJECT` / `BAD_BANK_REJECT` | 1 / 1 |
| `HIDE_OK` / `SHOW_OK` | 1 / 1 |
| `Z_CHANGE` / `STABLE_TIE` | 2 / 1 |
| `CLIP_OK` / `CULLED` | 4 / 2 |
| `FOUR_VISIBLE_FRAMES` | 217 |
| `FRAME_OK` | 240 |
| `MOVE_X0` / `MOVE_Y1` | 239 / 239 |
| `FRAME_SWITCH0` / `FRAME_SWITCH1` | 15 / 10 |
| `DRAW_FAIL` / `SWAP_FAIL` | **0 / 0** |
| `CHIP_BEFORE` / `CHIP_AFTER` / `CHIP_DELTA` | 1 703 536 / 1 703 536 / **0** |
| `FAST_BEFORE` / `FAST_AFTER` / `FAST_DELTA` | 135 768 920 / 135 768 920 / **0** |
| `CLOSE_RETURNED` | **1** |

Toutes les conditions prévues dans [`tests/current/README.md`](../tests/current/README.md) sont atteintes.

## 3. Interprétation technique

- **Objets logiciels et images :** six sources AGAPIC et quatre FICON8 préparées ; quatre objets initialement actifs, puis suppression de l'ID 4 et création du nouvel ID 5 (cinq créations, une suppression au total). L'ancien ID est refusé.
- **Animation AMAL/BASIC :** les deux positions AMAL ont évolué 239 fois, 15 et 10 changements d'image ont été comptés. Le mode `Synchro Off` et le déclenchement `Synchro` depuis BASIC font partie du code testé.
- **Composition :** deux modifications de Z et vérification de stabilité sur égalité. `PIXEL_DIFF 1` valide la **différence du pixel témoin** quand l'ordre de dessin est inversé, sans prouver le contenu intégral des buffers.
- **Robustesse fonctionnelle :** un masquage/réaffichage, un rejet d'index de frame, un rejet de banque manquante, quatre placements partiellement hors écran et deux cullings ont atteint les compteurs attendus.
- **Stabilité instrumentée :** 240 frames, `DRAW_FAIL 0`, `SWAP_FAIL 0`, fermeture signalée. Les deltas Chip/Fast à zéro correspondent aux points de mesure du banc, **après initialisation des tableaux BASIC** et avant écriture du rapport RAM: ; ce n'est ni une mesure du pic mémoire ni une preuve générale d'absence de fuite.
- **Journal :** le fichier transmis existe et contient les lignes de résultat. Il n'inclut pas les valeurs affichées hors fichier `LOG OPEN ERR` ou `LOG CLOSE ERR`.

## 4. Portée des validations

| Porte / configuration | Statut |
|---|---|
| P2.0 Gate B AMOS Runtime/WinUAE / 68030 / 8 plans | **PASS** — selon le journal fourni |
| P2.0 exécution strictement interprétée (`PRG_STATE 0`) | **NON TESTÉE** |
| P2.0 Gate C AMOS Compiler | **NON TESTÉE** |
| P2.0 Gate D Amiga AGA physique | **NON TESTÉE** |
| 4–7 plans, haute charge, cadence 50/60 FPS | **NON TESTÉS** |
| Sprites matériels AGA | **NON IMPLÉMENTÉS** : sujet P3 |

**CI distincte :** sur le commit `c65c820`, [Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337384) et [R84 native Gate A ciblée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337256) sont toutes deux **PASS**. Ces validations ne remplacent pas une mesure de performance ou une exécution Compiler M19.

## 5. Décision recommandée pour la suite

Le prototype démontre que la gestion des Bobs logiciels **peut fonctionner sans nouvelles commandes AP20** dans le périmètre testé. **Il n'établit aucun gain à porter ce gestionnaire en code natif.** Avant de définir une API, mesurer le temps/frame, les appels de rendu et le coût de tri pour plusieurs charges sur 68020+ (par exemple 4, 8 et 16 Bobs), tout en conservant la gestion de `Safe`, `Disp` et `Aga Swap` sous contrôle de l'application.

Ensuite seulement décider s'il faut un gestionnaire natif. Les sprites matériels AGA restent le sujet P3, avec gestion DMA/Chip/Intuition distincte.

**Modifications de cette consignation : documentation uniquement.** Ne pas modifier l'ASC actif, la R84, `LAST_GOOD`, l'ABI, les banques archivées ou démarrer une branche différente de `main`.

[Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md) · [Contrat P2](M19_P2_OBJECT_MANAGER_CONTRACT.md) · [Roadmap](ROADMAP.md) · [Test actif](../tests/current/M19_P2_OBJECTS_01.asc)
