# S2a-P1 — qualification réelle Runtime et Compiler

27/11/2026. Binaire et campagne actifs par [4719388](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/4719388fbc67e80a12973e686937d0cda1c12553), SHA256 Lib `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2`, ASC `d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb`, ABK `4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa`. Attribution de la Lib exacte par contexte de livraison/essai, pas par hash mesuré sur WinUAE.

| Journal original | Prg State | CHANGED/MOVED | OPENED/CLOSED | Chip avant=après | Fast avant=après | Verdict |
| --- | ---: | --- | --- | ---: | ---: | --- |
| [M19_S2A_RUNTIME1.TXT](evidence/M19_S2A_RUNTIME1.TXT) | 1 | 100/100 | 2/2 | 1793432 | 138104640 | PASS_S2A_FRAME_CHANGE |
| [M19_S2A_RUNTIME2.TXT](evidence/M19_S2A_RUNTIME2.TXT) | 1 | 100/100 | 2/2 | 1791088 | 138097000 | PASS_S2A_FRAME_CHANGE |
| [M19_S2A_COMPILED.TXT](evidence/M19_S2A_COMPILED.TXT) | -1 | 100/100 | 2/2 | 1757400 | 137826344 | PASS_S2A_FRAME_CHANGE |

Chaque journal distinct : CPU_ATTNFLAGS 32823, SHOWN 3, OFF_COUNT 1, AUTO_CLOSE 2, tous les codes API=1, CHIP_CYCLE_LOSS=FAST_CYCLE_LOSS=CHIP_SCREEN_LOSS=FAST_SCREEN_LOSS=0, RESULT=1 ERR=CLEAN_ERR=0. Mémoire disponible identique au début et à la fin de chaque exécution ; ne pas comparer les baselines de processus différents comme une fuite de Sprite.

Empreintes SHA256 des fichiers CRLF originaux vérifiées :
- M19_S2A_RUNTIME1.TXT: `07d661a5f31458ae4826f3b140dbc10dc19a7e73f07ed8c96c34d1a908e24c55`
- M19_S2A_RUNTIME2.TXT: `2f23bef4003a307d63d704757846f580a69ab7e44768f58a08dccb90452f1d05`
- M19_S2A_COMPILED.TXT: `8ef145f258233ea8d2976600b575a9bf5b2fabeddba816edd89cd21ff4672181`

**Validation visuelle et décision auteur, 27/11/2026 :** « oui lanimation est ok on peux continuer ». B Runtime 2/2 PASS stricts, C Compiler réel 1/1 PASS strict, A [10 jobs PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45907171922), [CI après activation](https://github.com/anthea176/AMOSPro-AGA-Extension/actions?query=branch%3Amain+sha%3A4719388fbc67e80a12973e686937d0cda1c12553) 39 succès, 1 skipped, 0 échec. D physique non testée. Pas de preuve universelle de sécurité DMA.

**Clôture S2a :** aucun nouvel essai identique demandé. Conserver la Lib, ASC et les deux banques exacts. P2m historique reste dans Git. Ne pas promouvoir LAST_GOOD sans décision explicite. S2b engagé en source-only : [multi-Sprite](M19_S2B_MULTI_SPRITE_2026-11-27.md). Aucun nouveau binaire installable.
