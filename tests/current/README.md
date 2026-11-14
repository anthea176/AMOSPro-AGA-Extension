# R76 C2P Convert - test actif avec journal RAM (14/11/2026)

**Gate B RPG R76 : PASS sur retour utilisateur.** Les deux scripts M0 RPG fonctionnent sous WinUAE apres la correction R76. **Gate B C2P Convert : NON TESTEE**. Le code de log RAM/identification CPU ajoute au test actif reste lui-meme a valider sous AMOS.

**Un seul ASC actif** : [C2P_R76_CONVERT_01.asc](C2P_R76_CONVERT_01.asc). Le binaire [R76 0.13.21](../../dist/AMOSPro_AGA.Lib), 54 144 octets, est la candidate en cours. R73 LAST_GOOD reste intacte.

## Test WinUAE interprete

1. Installer la R76 dans le slot AGA existant et conserver LIBS:c2p.library v1.9 ; redemarrer AMOS. CPU 68020+ et AGA requis, banque DATA 12 libre.
2. Importer l'ASC dans un programme vide avec Merge ASCII, puis executer en interprete **uniquement** (Gate C Compiler reservee a la fin du chantier C2P).
3. Les cinq profondeurs 16/32/64/128/256 couleurs doivent afficher deux conversions et deux swaps avec une bande sur la deuxieme frame. Les retours attendus par profondeur restent O/DB/C 1 1 1 et CONV/SW 1 1 1 2 1 1 POST 0.
4. Sur le dernier ecran, appuyer sur Echap apres la capture de la mire (attente interactive conservee). L'ecran se ferme ; l'ASC enregistre le fichier RAM:C2P_R76_INTERPRETED.TXT, affiche un resume et revient a AMOS par End **sans Do/Wait Vbl/Loop final**.
5. Examiner le fichier : TEST, VERSION, RUN_MODE, PRG_STATE, CPU, CPU_ATTNFLAGS, RESULT, VERDICT, PASS_DEPTH, FAIL_DEPTH, CLOSE_COUNT, CHIP/Fast Free. Verifier aussi LOG OPEN ERR 0 et CLOSE ERR 0 en console. Faire une capture de la mire et conserver une copie du journal sur un disque, RAM: etant volatile et le fichier ecrase au prochain essai du meme mode.

**Attention** : le log ne garantit pas une trace en cas de Guru ou de blocage avant l'epilogue. Un test ne passe pas parce que le fichier existe : ses resultats et la mire doivent etre controles. Le test C2P modifie n'a encore aucune Gate B WinUAE validee.

[Protocole des logs RAM](../../docs/AMOS_RAM_TEST_LOGGING.md) - [Rapport R76 RPG](../../docs/C2P_R76_RPG_REGRESSION_2026-11-14.md).
