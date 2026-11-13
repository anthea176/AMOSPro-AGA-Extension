# M18/R68 — Protocole Gate B WinUAE (AMOS interprété)

**13 novembre 2026 — À FAIRE, pas un résultat.** Gate A native M68000 48 cas PASS et CI bloquante PASS ; **aucune Gate B WinUAE R68 réalisée** ; **ne pas tester AMOS Compiler avant la clôture de M18**.

## Deux livrables actifs seulement

- [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **R68 v0.13.13**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, 51 064 octets, **64 commandes / 71 entrées AP20**, unique candidate NON PROMUE.
- [`tests/current/M18_R68_CBLOCK_CHIP_01.asc`](../tests/current/M18_R68_CBLOCK_CHIP_01.asc) : seul ASC actif, test CBlock Chip en AMOS interprété.
- [R63 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) protégée, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba` ; aucune modification et aucune promotion.

## Procédure

1. Configurer **WinUAE AGA**, écran **PAL 320×256×256**, AMOS Professional ; **banques 11, 12, 13 libres**. Les réglages CPU/JIT sont à noter pour les comparaisons.
2. Sauvegarder localement l'ancienne bibliothèque installée, remplacer `APSystem/AMOSPro_AGA.Lib` par R68, **conserver le même slot d'extension** (14 s'il est celui déjà utilisé), redémarrer AMOS.
3. Dans l'éditeur AMOS : **New** (programme vierge) → **Project → Merge ASCII** → `M18_R68_CBLOCK_CHIP_01.asc`. Exécuter **en interprété uniquement** ; **aucun AMOS Compiler**.
4. Photographier si possible **l'écran graphique pendant les 175 VBL** puis **la console de fin**. Le test n'écrit pas d'ABK.
5. Relever toutes les lignes de résultat et les six durées CPU8/CPU16/Blitter. Si le programme bloque, transmettre l'étape et la capture ; ne pas inférer de PASS.

## Assertions attendues

| Contrôle console | Valeur attendue |
|---|---|
| `OPEN/DB/SWAPS` | `1 1 1 1` |
| `CAP24/RECAP/SAME` | `1 1 1` : recapture sans réallocation |
| `BLIT/CPU8/WORD DRAW` | `1 1 1` |
| `REST24/32` | `1 1` |
| `LEN 24/32` | `552 552` (en-tête 40 + 8 plans × 4 octets/ligne × 16 lignes) |
| `PLANE EQ BLIT/CPU8/WORD` | `1 1 1` : comparaison RAW octet par octet |
| `BYTE MISMATCH` | `0 0 0` |
| `BAD 8/DIM/WORD/OUT` | `0 0 0 0` |
| `BAD BANK/MODE/X` | `0 0 0` |
| `BENCH ERR` | `0` |
| `CHIP REC/CURRENT` | Identiques, aucune réallocation sur recapture |
| `CHIP START/END` | Identiques après fermeture + `Erase` |
| `NOS/CLOSE` | `0 -1` |
| Verdict | **`RESULT 1` puis `CLOSE RETURNED`** |

**Rendu attendu :** fond bleu, blocs colorés 24×16 à X8 (CPU8) et X96 (Blitter), 32×16 à X160 (CPU16), tous avec intérieur index **0 opaque** (noir) ; un second rendu à Y152 ; **X240 intact bleu**.

## Interprétation des mesures

L'ASC utilise un bloc **32×16 identique**, banque 12 déjà créée, X16,Y80 pour capture et X160,Y152 pour dessin : **300 appels par méthode**, deux séries distinctes (capture et restitution). `Timer` renvoie des ticks de durée grossièrement 1/50 s en PAL. Mesures incluant l'appel AMOS, les vérifications de banque, `Safe` / `WaitBlit`, **sans coût de création**.

Comparer sur **68020 et 68030 sans JIT**, plusieurs essais avec paramètres identiques ; **ne pas annoncer CPU8/CPU16/Blitter plus rapide sans résultats mesurés et répétables**. Les tests natifs Unicorn simulent les appels OS et ne mesurent **pas le DMA matériel réel**.

## Gates séparées

**Gate A : PASS**, 48 cas M68000 sur deux dispositions ABI simulées ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43469372550)). **Gate B interprétée : EN ATTENTE**. **Gate C Compiler AMOS réelle : une seule fois à la fin M18**. **Gate D Amiga AGA physique : NON TESTÉE**. Aucune promotion automatique de `LAST_GOOD`.
