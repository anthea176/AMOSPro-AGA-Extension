# R84 v0.13.29 — Gate C AMOS Compiler, preuve WinUAE (14/11/2026)

## Provenance et périmètre

Source fournie par l'auteur : `AGAPIC_R84_COMPILED(1).TXT` (`TEST AGAPIC_R84_V1_V2_01`). L'auteur précise avoir **compilé le programme avec une banque intégrée** ; aucune compilation sans banque n'est attestée. Exécutable AMOS compilé, **`PRG_STATE -1`**, `CPU_ATTNFLAGS 32823` (68030 signalé par Exec).

| Indicateur du journal | Valeur |
|---|---|
| `VERSION` | R84 v0.13.29 candidate (titre du banc, avant promotion) |
| `RUN_MODE / PRG_STATE` | COMPILED / -1 |
| `RESULT / VERDICT / ERR` | **1 / PASS / 0** |
| `PASS_4 / PASS_8` | **1 / 1** |
| `CAPTURE_OK / META_OK` | 1 / 1 |
| `RLE_EQUAL_OK / MASK_EQUAL_OK` | 1 / 1 |
| `PALETTE_OK / RELOAD_OK / INVALID_OK` | 1 / 1 / 1 |
| `DRAW_OK / REGION_OK / SWAP_OK` | 1 / 1 / 1 |
| `CLOSE_COUNT / CLOSE_RETURNED` | 2 / 2 |
| `CHIP_BEFORE / AFTER / DELTA` | 1 862 320 / 1 862 320 / **0** octet |
| `FAST_BEFORE / AFTER / DELTA` | 140 599 040 / 140 587 120 / **−11 920 octets** |

**Verdict Gate C : PASS** sur ce périmètre. Les deux profondeurs (4 et 8 plans), les captures opaque/masquée v1/v2, la lecture des métadonnées, les flux RLE identiques, les palettes, le Save/Load ABK, les erreurs contrôlées, les dessins/régions, la fermeture et `ERR 0` sont confirmés par le journal.

## Analyse du code de test et du delta mémoire

La source AMOS `tests/current/AGAPIC_R84_V1_V2_01.asc` sauvegarde explicitement les quatre fichiers suivants, avant les mesures mémoire finales :
`RAM:R84_V1_4.abk`, `RAM:R84_V2_4.abk`, `RAM:R84_V1_8.abk`, `RAM:R84_V2_8.abk`.
Elle efface ensuite les **banques AMOS** 11 à 15 mais **ne supprime pas ces fichiers dans `RAM:`**. Cette rétention consomme potentiellement de la Fast RAM, et la banque incluse à la compilation fait partie du contexte de test. Le delta de **−11 920 octets** reste réel : il **ne prouve pas à lui seul une fuite native** et ne permet pas non plus d'affirmer que l'extension n'en produit aucune. **Aucun nouvel essai WinUAE demandé à l’auteur.**

Le code du banc utilise maintenant **`Length(N)`** pour contrôler une banque potentiellement absente et **`Start(N)`** uniquement pour obtenir une adresse de banque créée, suivie de `Leek/Peek`. L'erreur `Bank not reserved` de la première version du banc venait du contrôle `Start` sur banque absente ; elle ne constitue pas une preuve de dysfonctionnement du code natif R84.

## Limites à conserver dans toute communication

La Gate A CPU/CI R84 est PASS et la Gate C Compiler documentée ci-dessus est PASS. **Aucun journal Runtime `PRG_STATE 1` sur le banc corrigé n’a été fourni** : Gate B corrigée **non attestée séparément**, et non déclarée PASS. Interprétation stricte `PRG_STATE 0` et Gate D Amiga physique non testées.

[Rapport de promotion](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Gate A native](AGAPIC_R84_GATE_A_2026-11-14.md).
