# Test AMOS courant — M13 R30 0.10.2 AGAPAL Bank Init

**Essai WinUAE interrompu :** l'ASC original présentait `Type mismatch` à `_STILL=Peek$(_PTR,6)` (résultat chaîne vers une variable numérique). Affectation et comparaison corrigées en `_STILL$`. **Gate B toujours en attente**, bibliothèque R30 inchangée. Relancer le test complet ; ne pas promouvoir `LAST_GOOD`.

**Un seul fichier actif :** [`M13_R30_AGAPAL_BANK_INIT_01.asc`](M13_R30_AGAPAL_BANK_INIT_01.asc). Gate A 39 scénarios CPU PASS, export strict PASS et [CI de publication 32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43021754766). **Gate B WinUAE NON TESTÉE** ; Compiler et Amiga réel NON TESTÉS.

Copier [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) R30 0.10.2 (17 824 octets, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`) dans `APSystem` sous son nom exact, relancer AMOS, créer un programme vide et faire **Project → Merge ASCII** avec le test. **Attention : écrase banques 10 et 11, et `RAM:R30_AGAPAL_TEST.ABK`.**

Attendu : `INIT 1 REINIT 1`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `REST0 80 REST7 5456 INDEX 1`, `RESULT 1`, `CLOSE RETURNED`. La banque est sauvée/rechargée avec `Save`/`Load` natifs AMOS. `LAST_GOOD` reste R29 jusqu'à confirmation d'un PASS sous WinUAE.
