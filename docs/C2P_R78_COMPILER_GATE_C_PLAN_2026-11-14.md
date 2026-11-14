# C2P-5 — Plan de validation AMOS Compiler, candidate R78 (14/11/2026)

**Statut : À EXÉCUTER SOUS WINUAE — Gate C NON TESTÉE.** La Gate B du même ASC est **PASS** avec journal utilisateur et deltas Chip/Fast 0. Ce plan n'est pas une preuve d'exécution.

## Version figée pour la Gate C

- **Bibliothèque candidate :** R78 v0.13.23, `dist/AMOSPro_AGA.Lib`, 55 772 octets, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`, **68 commandes / 75 entrées AP20**.
- `LIBS:c2p.library` externe **v1.9** demeure nécessaire ; ne pas la remplacer pour cet essai.
- **Un seul ASC de référence :** `tests/current/C2P_R78_BLIT_01.asc`. Ne **pas** dupliquer un second ASC actif, ajouter de commandes ou modifier la bibliothèque. **Aucun nouveau build natif**.
- **WinUAE :** chipset AGA, CPU 68020+ (les journaux R78 précédents indiquaient 68030), mêmes réglages pertinents que pour la Gate B si possible. Ne pas supposer qu'ils sont les mêmes sans relever le profil effectif.
- **R73** `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure protégée, 51 608 octets SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.

## Procédure — une seule compilation pour les fonctions C2P livrées

1. Vérifier la bibliothèque installée sous AMOS (candidate R78 ci-dessus), la présence de `c2p.library` v1.9, et libérer les banques DATA **12 et 13** avant le test.
2. Importer **le même ASC R78** par **Merge ASCII dans un programme vide**, comme pour la Gate B ; enregistrer le source AMOS local si nécessaire, sans en changer la logique.
3. **Compiler le programme une fois avec AMOS Compiler**, selon le processus déjà utilisé pour [R73 Gate C](OPT020_P3_R73_COMPILER_GATE_C_2026-11-14.md). Conserver les éventuels avertissements/erreurs du Compiler, le nom de l'exécutable et, si disponible, son fichier de sortie. **Ne pas exécuter seulement l'ASC interprété**.
4. Lancer **l'exécutable compilé** sous WinUAE (avec AGA et `LIBS:c2p.library`) ; vérifier les cinq profondeurs et les opérations `Open → Blit → Convert → Swap → Close → Open → Blit → Convert → Swap → Close`. La copie des sprites est visible et clippée aux bords.
5. Sur l'écran final 256 couleurs, **Échap** doit quitter la boucle après `Amos To Back` puis revenir au bilan. **Ne pas conclure à un Guru sur un problème de premier plan** ; relever ce qui est affiché si Échap n'est pas reçu. **Ne pas valider une exécution interrompue par Ctrl+C**.
6. Copier le journal de `RAM:` hors de RAM avant un second lancement. Le programme dérive son nom de `Prg State` : `RAM:C2P_R78_COMPILED.TXT` si **-1**, `RAM:C2P_R78_RUNTIME.TXT` si **1**, ou `RAM:C2P_R78_INTERPRETED.TXT` si **0**. **Le libellé RUNTIME seul ne prouve pas que le programme était compilé** : conserver aussi la preuve de compilation et d'exécution de l'exécutable.
7. Relever les compteurs, `RESULT`, `VERDICT`, les mesures Chip/Fast **avant/après au sein du même essai compilé**, `ERR`, `NOS`, et les erreurs d'ouverture/fermeture du journal affichées à l'écran.

## Critères Gate C

| Contrôle | Attendu |
|---|---|
| Exécutable AMOS Compiler réellement produit et lancé | Preuve explicite requise |
| `RESULT`, `VERDICT`, `PASS_DEPTH` | `1`, `PASS`, `5` |
| `BLIT_COPY_OK`, `BLIT_PIXEL_OK`, `BLIT_REJECT_OK`, `BLIT_REOPEN_OK` | `5` chacun |
| `C2P_CLOSE_OK`, `EMPTY_CLOSE_OK`, `REOPEN_OK`, `CLOSE_COUNT` | `5` chacun |
| `ERR` et `NOS` | `0` et `0` |
| Fin du programme | `CLOSE_RETURNED 5`, retour normal, pas de Guru |
| Bilan mémoire | Deltas Chip/Fast **0 attendus**, écarts à analyser sans conclure automatiquement à une fuite |
| Journal | Fichier réel, erreurs I/O nulles, mode/CPU/identité R78 présents |

**Gates :** A **PASS**, B **PASS**, C **NON TESTÉE** avant preuve compilée, D **NON TESTÉE**. Après succès C, la **promotion** de R78 vers `LAST_GOOD` reste une **décision explicite et distincte de l'auteur**. Aucun tag, release ni publication Aminet n'est inclus dans ce test. AGAPIC v2 viendra seulement après le jalon C2P et l'accord correspondant.

[Gate B R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) · [Roadmap](ROADMAP.md) · [Protocole de logs](AMOS_RAM_TEST_LOGGING.md).
