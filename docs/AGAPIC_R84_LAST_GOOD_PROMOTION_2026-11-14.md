# R84 v0.13.29 — Promotion LAST_GOOD (14/11/2026)

## Autorisation et identité

**Accord explicite utilisateur : « on peux promote ! »** suivi de l'instruction de **ne pas refaire de test WinUAE** et de s'appuyer sur l'exécution compilée. La promotion R84 est donc effectuée avec le périmètre des preuves ci-dessous, sans prétendre qu'une Gate B corrigée distincte a été exécutée.

- **Branche : `main` uniquement**. Pas de nouvelle branche, tag, GitHub Release ou Aminet.
- **Binaire promu :** `dist/AMOSPro_AGA.Lib` R84 v0.13.29, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **76 commandes / 85 entrées AP20**, trois unités natives **C2P 5 558 / IFF 2 508 / AGA-AGAPIC 56 580 octets**. Aucune modification de ce binaire par la promotion.
- **Destination `LAST_GOOD` :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **même blob Git R84 `9c6c52a1d857c89089b2540b438b76efbf80c77b`**. Identité binaire exigée par les scripts de contrôle SHA.
- **Ancienne référence R83 :** 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, 74 commandes / 83 entrées, trois modules natifs. Reproductible via `tools/build_aga_r83_modular.py` depuis R82 épinglée, visible dans l'[historique Git juste avant promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/3c65fed54567d28c845979c23667585bd7cc6808/dist/AMOSPro_AGA_LAST_GOOD.Lib). Les octets historiques n'ont pas été modifiés.
- **Test AMOS unique actif :** `tests/current/AGAPIC_R84_V1_V2_01.asc`, copie identique gelée dans `tests/passed/AGAPIC_R84_V1_V2_01.asc`. Test R83 archivé précédemment.
- **Constructeur de R84 :** `tools/build_aga_r84_agapic.py` reconstruit R83 depuis sa source déterministe, puis R84, et contrôle les SHA finaux. Il ne dépend plus d'une R83 présente sous le pointeur `LAST_GOOD`.

## Gates réellement confirmées

| Gate | Verdict | Preuve |
|---|---|---|
| A — native CPU/CI | **PASS** | 44 cas Info et 47 cas Capture sur MC68020 émulé, ABI AP20, dispatch, mémoire, RLE |
| B — WinUAE Runtime corrigée | **NON ATTESTÉE SÉPARÉMENT** | Aucun journal corrigé `PRG_STATE 1` ; ne pas déclarer PASS |
| C — AMOS Compiler | **PASS** | Journal utilisateur `AGAPIC_R84_COMPILED(1).TXT`, programme compilé avec une banque ; `RESULT 1`, `VERDICT PASS`, `ERR 0`, 4/8 plans, `CLOSE_RETURNED 2` |
| Interpréteur strict | **NON TESTÉ** | `PRG_STATE 0` |
| D — Amiga AGA réel | **NON TESTÉ** | Aucun essai physique |

**RAM du journal compilé :** Chip 0 ; Fast **−11 920 octets**. Le programme de test laisse quatre fichiers ABK sur le RAM disk avant la mesure ; l'écart ne doit être qualifié ni de fuite native démontrée ni de retour mémoire neutre. [Analyse détaillée](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md).

## Limites et suivi

La promotion est une **décision explicite de l'auteur**, non une certification supplémentaire. Ne pas requalifier automatiquement les anciennes captures Runtime ERR 2 / ERR 17 en PASS : elles correspondaient aux erreurs de banc `Start`/ `Length`, corrigées dans l'ASC. Aucune nouvelle exécution WinUAE ne doit être imposée au titre de cette promotion.

**Aucune fonctionnalité nouvelle, branche expérimentale, archive historique, tag, release ou publication n'est modifiée ou créée par cette promotion en dehors du circuit unique et de sa documentation.**
