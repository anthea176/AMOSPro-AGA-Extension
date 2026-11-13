# M18/R68 — Gate C AMOS Compiler PASS (WinUAE, 13/11/2026)

## Preuve de validation

Le test intégré M18-R68-COMPILER-GATE-C a été exécuté sous WinUAE en mode AMOS compilé, selon la capture de l'auteur annotée « Compilé » et sa confirmation. La console affiche **RESULT 1** et **CLOSE RETURNED**. Cette Gate C réelle est distincte des simulations CPU/CI.

Source d'essai : [M18_R68_COMPILER_FINAL_01.asc](../tests/passed/M18_R68_COMPILER_FINAL_01.asc), copie immuable de l'ASC actif (Git blob 1fcac1a490f9172f165adc6e267b32d638eb199f). Bibliothèque candidate R68 v0.13.13 : 51 064 octets, SHA256 ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed (64 commandes / 71 AP20). L'identité SHA du fichier installé dans WinUAE n'a pas été mesurée indépendamment.

## Relevé de la console compilée

| Contrôle | Observé |
|---|---|
| BANK FICON/CHIP, PUT | 1 1 ; 1 |
| OPEN/DB/SWAPS | 1 1 1 1 |
| DRAW SOURCE NONALIGN/ALIGN | 1 1 |
| CAPTURE NONALIGN/ALIGN | 1 1 |
| PIXELS 288 BYTE EQ2/EQ3 | 1 1 |
| BAD X/Y/NEG/ID/BANK/0 | 0 0 0 0 0 0 |
| CHIP BEFORE/AFTER CAPTURE | 1736192 / 1736192 |
| FAST BEFORE/AFTER CAPTURE | 140758624 / 140758624 |
| ABK SAVE/LOAD LEN | 1164 / 1164 |
| ABK RELOADED EQ2/EQ3 | 1 1 |
| STAGE2/3 READY2/3/4 | 1 1 1 1 0 |
| CPU/MASKED/OPAQUE/UNREADY | 1 1 1 0 |
| NOS/CLOSE | 0 -1 |
| CHIP/FAST AFTER RAM FILE | 1907856 / 140769032 |
| CBLOCK CAP/REST/RECAP/SAME | 1 1 1 1 |
| CBLOCK DRAW CPU8/BLIT/CPU16 | 1 1 1 |
| CBLOCK LEN | **1064** |
| BAD MODE/ALIGN/DIM | 0 0 0 |
| CBLOCK AFTER CLOSE | 0 |
| Résultat final | **RESULT 1 — CLOSE RETURNED** |

R68 conserve les méthodes obligatoires explicites : 0 CPU8, 1 CPU16, 2 Blitter. La banque 32×32×8 plans vaut 40 + 8×4×32 = 1064 octets. La capture confirme les contrôles du programme et le retour de la fermeture ; elle ne montre pas le rendu graphique et ne documente pas les paramètres CPU/JIT de la compilation. La boucle finale Do / Wait Vbl / Loop garde la console ouverte.

**Gates A/B/C PASS** pour les scénarios documentés. **Gate D Amiga AGA physique NON TESTÉE**. Promotion R68 en LAST_GOOD expressément approuvée par l'auteur, mais conditionnée au PASS de la régression complète prépromotion sur main. Ne pas relancer le Compiler pour le même test.

[Gate B intégrée interprétée](M18_R68_INTEGRATED_GATE_B_68030_JIT_2026-11-13.md) · [Contrat CBlock](M18_CBLOCK_DESIGN.md).
