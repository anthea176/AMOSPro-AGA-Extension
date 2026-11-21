# M19 P2 ALL IN ONE — campagne finale avant exemple public

**Un seul banc actif** : [M19_P2_ALL_IN_ONE.asc](M19_P2_ALL_IN_ONE.asc), **25 056 octets ASCII**, Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`, tag `P2_FULL_V1_20261121`. Bibliothèque de travail **M19 P2d**, `dist/AMOSPro_AGA.Lib`, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, **100 commandes / 203 AP20**, CPU MC68020+. **LAST_GOOD P1e intacte**.

## Ce que teste réellement le banc

| Jalon | API / mécanisme | Contrôle bloquant |
| --- | --- | --- |
| **P2e** | Deux canaux AMAL 0/1, mémoire 8 octets chacun, Bobs masqués 16×16 F/L | **240** cycles, **29 pixels par Bob**, changements X/Y/image et retours getters |
| **P2a** | `Aga Bob Col(A,B,0/1)` | **8 assertions** : collision rectangle/masque, rectangles seuls, aucune collision, mode invalide et indépendance vis-à-vis de Plans |
| **P2b** | `Aga Bob Flip(N,Mode)` | **4 orientations par Bob**, silhouettes F/L **32×32**, **20 comparaisons de pixels** (opaques/transparents), rejet du mode 4 |
| **P2c** | `Aga Bob Planes(N,Masque)` | Masques **255/255, 1/2, 0/0, 129/66, 255/255**, **10 pixels bitplane**, rejets -1 et 256 |
| **P2d** | `Aga Bob Auto Update(1)` puis `(0)` et `Aga Swap` | Reprise **bornée à 4 VBL** en cas de refus, compteur visible, désactivation finale ; **252 Swaps réussis attendus** |

Le moteur affiche les deux petits F/L mobiles d'abord, puis les grands F/L dans les 4 orientations, puis les 5 combinaisons de plans. Aucune image carrée. Des palettes explicites rendent les plans sélectionnés visibles. L'écran AGA vient devant AMOS par `Amos To Back`, et est fermé/restauré à la fin.

## Lancement sous WinUAE

1. Utiliser la **Lib P2d inchangée** dans `APSystem`, redémarrer AMOS Pro, WinUAE AGA avec MC68020+.
2. Dans un **programme vierge**, `Project → Merge ASCII` du **seul** `tests/current/M19_P2_ALL_IN_ONE.asc`. Banques 24, 27 et 28 libres.
3. Lancer d'abord en **Runtime**. Observer l'animation et les orientations H/V/HV des deux F/L 32×32. Les formes de couleur 0 lorsque le masque de plans vaut 0 sont attendues.
4. Sauvegarder le journal avant de relancer. En cas d'échec, envoyer journal et capture écran.

| Mode (`Prg State`) | Fichier de log |
| --- | --- |
| Interprété strict (0) | `RAM:M19_P2_FULL_INTERPRETED.TXT` |
| Runtime (1) | `RAM:M19_P2_FULL_RUNTIME.TXT` |
| Compiler (-1) | `RAM:M19_P2_FULL_COMPILED.TXT` |
| Mode inconnu | `RAM:M19_P2_FULL_UNKNOWN.TXT` |

**Résultat attendu si tout fonctionne :** `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VALID_SAMPLES 240`, `SWAPS 252`, `COL_CHECKS 8`, `FLIP_STAGES 4`, `FLIP_PIX0 8`, `FLIP_PIX1 12`, `PLANES_STAGES 5`, `PLANES_PIX0 5`, `PLANES_PIX1 5`, `AUTO_ENABLE 1`, `AUTO_DISABLE 1`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

**Refus de Swap :** `SWAP_REFUSALS`, `SWAP_RECOVERED`, `RETRY_VBLS` restent journalisés, y compris après une réussite. Ne pas assimiler le PASS final à zéro refus. Les champs `PHASE_LAST` et `LAST_REFUSAL_PHASE` identifient le jalon en cours ou le dernier refus.

## État des Gates

- **P2e.1 antérieur : Gate B Runtime PASS** : 240 cycles, 241 Swaps, **120 refus tous récupérés après 1 VBL**, 29 pixels ×2, fermeture propre. [Journal exact conservé](../../docs/evidence/M19_P2E1_AMAL_RUNTIME_PASS_RETRY_2026-11-21.TXT), 769 octets CRLF, SHA256 `1a6e32042f6f0e664f84d983b26e95deaecae51311340430dca7f44fd06fe1d8`.
- **P2a–P2e intégrés dans cet ASC : Gate B WinUAE NON TESTÉE**, Gate C vrai AMOS Compiler NON TESTÉE, Gate D physique NON TESTÉE. Préflight et tests géométriques sont des contrôles statiques uniquement.
- Le banc antérieur de 10 421 octets reste dans [l'historique Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/299b0f78a7e23c7fdabcdd401755839eb5e90fa2/tests/current/M19_P2E1_AMAL_TWO_BOBS.asc).

**AUCUNE promotion automatique** : ce banc reste dans `tests/current/`. Il ne sera déplacé vers `examples/` **qu'après essai réel et approbation de l'auteur**. Ne modifier ni `dist/AMOSPro_AGA.Lib` ni `dist/AMOSPro_AGA_LAST_GOOD.Lib`.
