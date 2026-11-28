# S2c-P1e — qualification fonctionnelle Runtime et Compiler

**28/11/2026 — S2c-P1e Gates B Runtime et C Compiler fonctionnelles PASS** (PRG_STATE=1/-1, RESULT=1 ERR=0 CLEAN_ERR=0, PASS_S2C_MIXED). Chaque mode : 3 Open/Close, 12 Show, 450 Change, 450 Move, 3 Off, 9 retraits auto, 3 saturations -206, AGAPIC 6/6, AGSP 4 plans 6/6 et 3 refus. Chip/Fast sans perte nette ; Fast temporaire 1464 octets récupérée. Attribution à la Lib active par contexte, SHA installé, visuel complet, relance indépendante et D non attestés. L'auteur demande de renforcer le contraste des prochaines campagnes. S2c-E1 reste active (160896 octets, SHA256 `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310`), aucune promotion de LAST_GOOD.

## Identification et preuves

Lib attendue : commit [d70e39e](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/d70e39eae2d695b4f14d0295a9a39313d7742864), blob 9110fe94f0d937207038d77d6df250b99392c54c, titre S2c-E1. ASC SHA256 48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec ; ABK SHA256 6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246. SOURCE_TAG M19_S2C_MIXED_V1. CPU_ATTNFLAGS 32823 dans les deux journaux. Configuration WinUAE PAL AGA 68030 JIT ON attendue, non mesurée par ce log.

| Preuve originale CRLF | Octets | SHA256 |
| --- | ---: | --- |
| [Runtime](evidence/M19_S2C_P1E_RUNTIME_PASS_2026-11-28.TXT) | 801 | `5afeed50bfabbe4aaf8adcad7738db68d117bc92df444e26ab04b5f88c7291f9` |
| [Compiler](evidence/M19_S2C_P1E_COMPILED_PASS_2026-11-28.TXT) | 802 | `4202232de91b133dbd8cbffc63ca8fbc8ecd64fa1832babfff739be5ec789c74` |

| Mémoire (octets) | B Runtime | C Compiler |
| --- | ---: | ---: |
| Chip avant/après | 1837272 | 1801520 |
| Fast avant/après | 138250536 | 137957440 |
| Fast après chaque écran | 138249072 | 137955976 |
| Perte nette Chip/Fast | 0/0 | 0/0 |

AGAPIC : W19 H9 depth8 colors256 mode135168, INFO_BAD=-1, DUP_RC=0, DRAW_RC=1, OWN=0. AGSP : FREE_RC=1, OWN=0. FULL_RC=-206. Aucun échec fonctionnel ni fuite nette détectés. Le visuel est insuffisamment discriminant selon l'auteur : couleurs à renforcer, pas de validation exhaustive de l'apparence, de relance sans reset, de SHA de copie installée ou de DMA physique. Prg State=0 non testé.

Gate A : preuves combinées exactes du rapport [P1e](M19_S2C_P1E_VIEWPORT_CHAIN_2026-11-28.md). Requalification intégrale 46124380826 : in_progress/en cours ; CI post-activation relevé {"queued":5,"success":37,"skipped":1,"in_progress":5}. Aucun changement de Lib ni de campagne, ni promotion/release.

**Chantier suivant : 0.15.0-alpha.1 (M19 S2d)** : capture/repack puis affichage Sprite 16/32/64px ; largeur commune par contexte, API existante, couleur franche et motifs asymétriques. Source-only jusqu'à preuve Gate A et bascule explicitement autorisée. Cible publique 0.15.0 ; objectif final 1.0.0. Ne pas renommer les binaires historiques.
