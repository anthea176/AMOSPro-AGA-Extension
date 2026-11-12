# Test AMOS actif — M16/R50 : `Rjsr` bibliothèque principale

**Seul test actif :** [`M16_R50_FNONE_RJSR_PROBE_01.asc`](M16_R50_FNONE_RJSR_PROBE_01.asc), correspondant à [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) (**R50**, diagnostic uniquement).

Importer par **Project → Merge ASCII** dans un programme AMOS vide, puis exécuter **en interprété** dans la configuration WinUAE de test.

**Résultat attendu :** `AFTER RJSR FNON 1`, puis `RESULT 1`. Une autre valeur ou un crash constitue un FAIL.

La R50 garde les 6 paramètres de `Aga Image Capture` mais la fonction ne capture rien : elle appelle une seule fois `Rjsr FnOne` (index 322, routine interne AMOS retournant 1), **sans accès aux banques ni mémoire, et sans écran AGA**. Elle différencie un problème générique de liaison `Rjsr` du crash spécifique `Bnk.GetAdr` en R49. L'ancienne R49 a **Gate B FAIL (crash WinUAE)** et se trouve dans [`tests/diagnostics/`](../diagnostics/M16_R49_GETADR_PROBE_01.asc), non dans `current`. La R48 Gate B PASS reste archivée.

**Ne pas compiler ni promouvoir R50.** La R46 C1 validée reste [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).
