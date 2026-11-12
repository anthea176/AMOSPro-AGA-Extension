# Test AMOS actif — M16/R52 : cible effective de `Rjsr FnOne`

**Seul test actif :** [`M16_R52_FNONE_TARGET_PROBE_01.asc`](M16_R52_FNONE_TARGET_PROBE_01.asc), correspondant a [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **R52 v0.12.7, diagnostic uniquement**.

Charger avec **Project -> Merge ASCII** dans un programme vierge et lancer en **interprete** sous WinUAE. Aucun ecran ni banque 11 requis. La fonction R52 **saute le `Rjsr`** puis verifie que la cible du `JSR` est localisee dans une memoire reconnue par `exec.library/TypeOfMem` ; elle compare ensuite les six octets attendus de `FnOne` (`7601 7400 4E75`). Aucune banque/aucun ecran n'est modifie.

Resultat attendu, selon le chargeur en place : **`RESULT 1`** si les trois instructions sont conformes ; **`RESULT 2`** si elles different ; **`RESULT 3`** si `TypeOfMem` ne reconnait pas la cible (ce qui ne prouve pas systematiquement qu'elle est inaccessible, par exemple zone ROM) ; **`RESULT 4`** si le `JSR` ou le pointeur sont invalides ; **`RESULT 0`** si les arguments ne correspondent pas.

R51 a eu **Gate B PASS utilisateur** pour la seule relocation, sans capture reelle. Ancien test R51 archive [ici](../diagnostics/M16_R51_RJSR_RELOCATION_PROBE_01.asc). R52 : **Gate A CPU/CI PASS**, Gate B non testee, Gate C non testee. Ne pas compiler ni promouvoir R52 ; R46 C1 reste `LAST_GOOD`.
