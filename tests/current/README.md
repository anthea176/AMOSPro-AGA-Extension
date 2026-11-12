# Test AMOS actif — M16/R49 : pont des banques (diagnostic)

**Un seul test actif :** [`M16_R49_GETADR_PROBE_01.asc`](M16_R49_GETADR_PROBE_01.asc). Il correspond exactement à la candidate dans [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), version R49 0.12.4.

Importer le fichier par **Project → Merge ASCII** dans un programme AMOS vide, puis lancer **en interprété**, dans la configuration WinUAE de test. **Aucun écran ni banque à créer.** La routine vérifie l'ABI des 6 paramètres, puis appelle **une seule fois `Bnk.GetAdr` en lecture sur le numéro 11**.

- `RESULT 1` : appel interne correct, banque 11 libre.
- `RESULT 2` : appel interne correct, banque 11 déjà occupée ; elle reste inchangée.
- `RESULT 0` : arguments incorrects ; aucune banque appelée.

Le test **n'effectue aucune capture, allocation, modification ni suppression de banque**. Ne pas compiler : Gate B de R49 en attente, Gate C non testée. La R48 précédente a passé sa propre Gate B et est conservée dans [`tests/diagnostics`](../diagnostics/M16_R48_TOKEN_ABI_PROBE_01.asc). L'ancien test R47 n'est plus actif. La R46 C1 validée reste [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).
