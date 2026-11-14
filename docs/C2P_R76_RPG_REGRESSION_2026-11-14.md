# R76 — régression RPG R73 → R74/R75 : corruption clavier/souris

**Incident du 14 novembre 2026, réparé au niveau natif en R76 v0.13.21.**

## Constat et reproduction

Les programmes `M0_R73_INPUT_DIAG_01.asc` et `M0_R73_MENU_01.asc` fonctionnent avec la bibliothèque `LAST_GOOD` réinstallée (taille 51 608 octets, celle de R73), mais se bloquent ou produisent un Guru `80000006` avec R74. La taille seule ne prouve pas l'identité SHA de la copie locale. **Aucun script ne dépend de C2P** ; tous deux utilisent l'écran AGA et les entrées clavier/souris.

**Cause vérifiée dans les fichiers natifs R73/R74/R75 :** R74 ajoute 138 octets dans l'entrée 08 (hooks de nettoyage) avant le bloc statique clavier/souris de 144 octets en fin de l'entrée 33. L'adresse réelle change de `State+$2E9C` à `State+$2F26`, mais sept instructions `LEA 11932(a2),an` continuent de viser l'ancien emplacement. Dès `Aga Screen Open`, une boucle de 36 `CLR.L (A0)+` efface 144 octets à cette **mauvaise adresse, dont 138 octets de code natif exécutable**. Même sans appel C2P.

| Entrée AP20 | Instruction(s) réparée(s) |
|---|---|
| 06 — `Aga Screen Open` | `+$02E2` |
| 31 — `Aga Mouse Pressed` | `+$0038`, `+$0048` |
| 32 — `Aga Mouse Released` | `+$0038`, `+$0048` |
| 33 — traitement clavier/souris | `+$003E`, `+$022C` |

## Correction R76

**Seulement les sept opérandes WORD** `$2E9C → $2F26`. Aucune longueur d'entrée, aucun branchement relatif, aucun token public et aucune commande C2P modifiés. Le constructeur `tools/build_c2p_r76_rpg_fix.py` calcule la destination à partir des octets réels du bloc de données, vérifie les sept opcodes attendus et compare les sources SHA-épinglées. Les constructeurs historiques R73/R74/R75 sont préservés.

- Candidate **`dist/AMOSPro_AGA.Lib` — R76 v0.13.21, 54 144 octets, SHA256 `9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897`** ; 66 commandes / 73 entrées AP20.
- **`dist/AMOSPro_AGA_LAST_GOOD.Lib` — R73 v0.13.18, 51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`** — intangible.
- **Gate A CPU natif 24/24 PASS** : le véritable code `Screen Open`, `Mouse Pressed` et `Mouse Released` a été exécuté sous CPU68000 et CPU68020. Les binaires R74/R75 **reproduisent l'écrasement des octets de code**, R73 et R76 n'écrivent que dans les 144 octets de données. [CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43591570595).
- **12 scénarios de fermeture d'écran et `End` R73/R74/R75 PASS**, utiles mais insuffisants pour déceler la corruption survenue dès Screen Open.
- **Gate B WinUAE RPG R76 : NON TESTÉE.** Rejouer **les deux programmes RPG d'origine** en mode interprété avec R76, contrôler que le blocage/Guru ne se reproduit plus et que clavier, souris et retour AMOS fonctionnent. Cela prime sur la reprise de la Gate B C2P Convert.
- Gate C Compiler et Gate D matériel : NON TESTÉES ; aucune promotion de `LAST_GOOD`.

**R74/R75 restent des candidats historiques connus défaillants pour les RPG utilisant les entrées**, malgré la Gate B R74 limitée à `Aga C2P Open`. Ne pas demander de GDB, de PowerShell, ni modifier les scripts d'origine pour masquer la régression.

**Règle permanente ajoutée :** chaque insertion/suppression de bytes dans le monolithe native AP20 impose non seulement le recalcul de tous les liens PC-relatifs, mais aussi **de tous les accès à données statiques par déplacements absolus à partir du pointeur `State`**, avec test de non-écrasement du code sur les vrais opcodes 68k.

## Mise a jour du 14/11/2026 - confirmation utilisateur et prevention permanente

**Gate B RPG WinUAE R76 : PASS sur retour de l'auteur (« ca marche nickel »)**, a la suite de la demande de tester M0_R73_INPUT_DIAG_01.asc puis M0_R73_MENU_01.asc. Le blocage/Guru observe sur R74/R75 n'est plus signale sur la R76. Aucune capture ni fichier RAM n'accompagne cette confirmation. Cela **ne valide pas la Gate B C2P Convert**, ni les Gates C Compiler et D Amiga physique. R76 reste candidate ; **R73 LAST_GOOD intacte**.

La CI dispose d'un nouveau **controle independant du builder**, tools/test_current_input_state_offsets.py, lance directement sur dist/AMOSPro_AGA.Lib. Il calcule l'adresse de la zone clavier/souris depuis la disposition reelle du monolithe AP20, verifie les 7 LEA, et applique 8 mutations negatives (les sept operandes + un decalage de zone). Tout changement de structure exige un nouvel audit, jamais une desactivation du controle.

Les tests ASC actifs doivent maintenant creer un rapport texte RAM: en mode interprete/compile/runtime (Prg State) et journaliser le CPU signale par Exec, puis retourner a AMOS par End. Le nouveau code de log de C2P_R76_CONVERT_01.asc reste a verifier sous WinUAE. Regles : EXTENSION_SOURCE_RULES.md ; reference : docs/AMOS_RAM_TEST_LOGGING.md.
