# Test AMOS actif — M16/R51 : vérifier la relocation Rjsr

**Un seul test actif :** [`M16_R51_RJSR_RELOCATION_PROBE_01.asc`](M16_R51_RJSR_RELOCATION_PROBE_01.asc), aligné sur la bibliothèque **R51** dans [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib).

Charger dans un programme AMOS vierge avec **Project → Merge ASCII**, lancer **en interprété**. La fonction R51 examine les octets du marqueur `Rjsr FnOne` sans l'exécuter. Pas de banque 11 nécessaire, ni d'écran AGA. **Aucune image n'est capturée.**

**Interprétation du résultat** : `1` = opcode `JSR absolute long` installé avec adresse non nulle et paire ; `2` = `FE11` n'a pas été converti ; `3` = opcode ou adresse anormale ; `0` = paramètres de test incorrects. Une valeur `1` ne prouve pas que l'adresse pointe vers la bonne routine AMOS.

Le précédent test R50 a **Gate B FAIL (Software Failure 80000004)** et est archivé dans [`tests/diagnostics/`](../diagnostics/M16_R50_FNONE_RJSR_PROBE_01.asc). **R51 Gate A CPU/CI PASS, Gate B non testée, Gate C non testée.** Ne pas compiler ni promouvoir. R46 C1 reste `LAST_GOOD`.
