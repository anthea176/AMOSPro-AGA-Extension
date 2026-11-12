# M16/R49 — test du pont Rjsr `Bnk.GetAdr`

La R48 a passé Gate B (interprété WinUAE, `RESULT 1`) : token et ABI de `Aga Image Capture` reconnus. La R47, elle, déclenchait `Non dimensioned array` et un crash WinUAE distinct ; la cause exacte est encore inconnue.

R49 ne capture aucune image : **une unique invocation interne `Rjsr Bnk.GetAdr` (index 297) sur la banque 11**, avec les six arguments AMOS identiques à R48. Le 68000 préserve les registres requis et consomme les cinq paramètres empilés dans `A3` ; `D3` contient l'index de masque. **Zéro appel** à `Bnk.Reserve`, `Bnk.Eff`, `Bnk.Change`, aucune écriture de banque, aucune ouverture d'écran et aucune allocation.

- [Candidate courante](../dist/AMOSPro_AGA.Lib) : version R49 0.12.4, 32 012 octets, SHA256 `c18a0992ee148beb437aecc2c1c865338630b40e34bc989c72dfb26313d5657e`.
- [Archive R49](../dist/experimental/AMOSPro_AGA_M16_v0.12.4_R49_GETADR_PROBE.Lib), identité binaire obligatoire avec la candidate.
- [Test AMOS actif](../tests/current/M16_R49_GETADR_PROBE_01.asc).

**Gate A CPU/CI PASS** : 7 cas de sonde 68000, simulacre strict de `Bnk.GetAdr`, contrôle A3/A7/D2/D3, non-mutation ; [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43255559816). Cela **ne teste pas** le mécanisme réel du relocateur AMOS. **Gate B de R49 : en attente**. **Gate C Compiler : non testée**. R46 C1 `LAST_GOOD` toujours immuable.

Sous WinUAE isolé : utiliser directement `dist/AMOSPro_AGA.Lib`, redémarrer AMOS, ouvrir le test de `tests/current/` avec **Project → Merge ASCII**, lancer en **interprété**. `RESULT 1` si banque 11 libre ; `RESULT 2` si elle est déjà utilisée ; `RESULT 0` indique argument inattendu. En cas de crash, conserver dernier repère et minidump. Ne pas utiliser l'ancienne recette de capture R47.

## Gate B utilisateur — FAIL le 12/11/2026

Le programme R49 a affiché `R49 BANK GETADR PROBE` puis `BEFORE GETADR` et WinUAE x64 6.0.3 a **planté** (fenêtre `Crash detected. MiniDump saved as` ; fichier `winuae_x64_6.0.3_R_2026.11.12_17.14.44.dmp` indiqué localement). Aucun `AFTER GETADR` ni `RESULT`. C'est un crash du **processus WinUAE**, pas une validation de l'appel. Le dump n'a pas été fourni pour cette occurrence. **R49 Gate B FAIL** ; ne pas la retester sans correction. Le cas R48 sans l'appel avait réussi dans la même démarche, donc l'interaction `Rjsr`/banque est l'hypothèse principale, sans PC Amiga ni preuve de la cause bas niveau. Suite : [contrôle sûr `Rjsr FnOne`](M16_R50_FNONE_RJSR.md) avant toute nouvelle tentative d'accès aux banques.
