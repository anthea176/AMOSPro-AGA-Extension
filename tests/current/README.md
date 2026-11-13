# OPT020/P1e — R69 en service, P2/R70 bloquée

**Binaire unique de travail :** `dist/AMOSPro_AGA.Lib` **R69 v0.13.14**, 51 240 octets, SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`. P1e Gate A/CI et Gate B WinUAE interprétée **PASS** ; benchmarks R60/R69 **interprétés et compilés PASS** sur 68020 14 MHz JIT OFF (jusqu'à 3,39× en opaque 32×20 compilé). R69 non promue.

**R68 LAST_GOOD protégée** : `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Ne modifier ni `LAST_GOOD`, ni archives, ni `tests/passed/`.

**ASC actif unique :** [`OPT020_P1E_R69_INTERPRETED_01.asc`](OPT020_P1E_R69_INTERPRETED_01.asc). Banque `M16_AGAPIC_SAMPLE_BANK10.abk` ; ce programme P1e est déjà validé sous WinUAE. L'ancien ASC R70 est conservé dans [l'historique du commit du diagnostic](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/208d7b30c091ac2be4e38003166976f2ee3b59af/tests/current/OPT020_P2_R70_INTERPRETED_01.asc), **ne pas l'exécuter normalement**.

## Incident P2/R70

Le 13/11/2026, l'ASC R70 a provoqué un blocage graphique suivi d'une alerte Workbench **AMOS / `80000004` (Illegal Instruction)**, deux reproductions. **Gate B P2 FAIL ; pas de Gate C R70 ni de benchmark P2**. Après 256 cas Musashi incluant la vraie banque 64×40 (PASS), la cause réelle doit être isolée par l'adresse de l'instruction (PC) dans le débogueur WinUAE, plutôt que par de nouveaux appels au hasard.

[Rapport détaillé et méthode de collecte PC](../../docs/OPT020_P2_R70_GURU_80000004_2026-11-13.md). Sources/constructeur P2 et Git historique intacts ; aucune nouvelle bibliothèque R70 ajoutée au dépôt.

**Pour retrouver un environnement stable** : copier la R69 active dans le slot AGA d'`APSystem`, puis redémarrer entièrement AMOS. Utiliser **68020 14 MHz JIT OFF** comme lors des mesures validées. Ne pas lancer le Compiler pendant l'enquête.
