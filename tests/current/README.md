# R77 C2P Close — Gate B fonctionnelle WinUAE PASS, focus du test corrige (14/11/2026)

**Candidat :** [R77 v0.13.22](../../dist/AMOSPro_AGA.Lib), **54 360 octets**, SHA256 `81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11`, 67 commandes / 74 AP20. **Gate A native PASS (12 cas CPU)** ; **Gate B fonctionnelle WinUAE R77 PASS sur le journal utilisateur** (5/5 profondeurs, fermetures, refus des doubles fermetures et reouvertures). **Correction `Amos To Back` du test actif non encore retestee sous WinUAE**. Gate C Compiler et Gate D physique non testees. R73 LAST_GOOD intacte. R76 Gates A/B avaient PASS (cinq profondeurs et journaux RAM).

**Un seul ASC actif :** [C2P_R77_CLOSE_01.asc](C2P_R77_CLOSE_01.asc). Importer via **Merge ASCII dans un programme vide**, après installation R77 dans le slot AGA habituel et redémarrage AMOS. Conserver `LIBS:c2p.library` v1.9, CPU 68020+ AGA et banque DATA 12 libre. **Ne pas compiler** (Gate C réservée à la fin du chantier C2P).

## Attendus du test

1. Cinq profondeurs 16/32/64/128/256 couleurs ; deux conversions C2P et swaps explicites avant le cycle de fermeture.
2. Pour chaque profondeur, `_CL1=Aga C2P Close` doit retourner **1** ; `_DEAD=Aga C2P Convert` **0**, et le second `_CL2=Aga C2P Close` **0**.
3. Sans fermer l'écran AGA, `_REOPEN=Aga C2P Open(12)` doit retourner **1** ; une troisième conversion et le Swap **1** ; `_CL3=Aga C2P Close` **1**.
4. `Aga Screen Close` et retour à AMOS sans double libération ; après fermeture, `Aga C2P Convert` et `Aga C2P Close` doivent retourner **0**. Capture de la mire et du bilan.
5. Le test fait desormais **`Amos To Back` avant d'afficher la mire et d'attendre `Aga Key=69` (Echap)** ; apres fermeture de l'ecran AGA, il restaure **`Amos To Front`**. Echap doit etre recu sans bascule Amiga+A manuelle. **Ne pas sortir par Ctrl+C** : cela interrompt le programme avant `Erase 12` et peut laisser la banque en memoire. Ce correctif de focus doit encore etre verifie sous WinUAE.
6. Après Échap, programme terminé normalement par `End`, journal dans **`RAM:C2P_R77_RUNTIME.TXT`** si `Prg State=1` (autres modes selon Prg State). Vérifier `RESULT 1`, `VERDICT PASS`, `PASS_DEPTH 5`, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `CLOSE_COUNT 5`, `ERR 0`, `NOS 0`, mémoire Chip/Fast avant/après et erreurs d'ouverture/fermeture du journal à 0.

Le journal RAM est **volatile** : le copier hors de RAM avant un reboot ou un second essai du même mode. En cas de Guru, la sortie du journal n'est pas garantie.

[Contrat R77](../../docs/C2P_R77_CLOSE_CONTRACT_2026-11-14.md) · [Protocole RAM](../../docs/AMOS_RAM_TEST_LOGGING.md) · [R76 Gate B](../../docs/C2P_R76_CONVERT_WINUAE_GATE_B_2026-11-14.md).

**Rapport deja confirme :** [Gate B fonctionnelle R77](../../docs/C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md) ; `C2P_R77_RUNTIME.TXT` : `RESULT 1`, `PASS_DEPTH 5`, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `ERR 0`, `NOS 0`, `CHIP_DELTA 0`, `FAST_DELTA -81944` (81 944 octets de Fast RAM en plus apres le test). L'auteur a confirme un Ctrl+C anterieur a cause du focus, d'ou la banque 12 possiblement encore allouee. Un second essai propre permettrait de confirmer le delta Fast nul sans bloquer R78.
