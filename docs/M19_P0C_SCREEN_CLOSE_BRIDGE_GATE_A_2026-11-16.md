# M19 P0c — pont public Screen Close et callback AMOS End : Gate A expérimentale (16/11/2026)

## Identité immuable et statut

| Élément | Preuve |
|---|---|
| Base officielle inchangée | M19 P0b, 82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9` |
| Builder source | [`tools/build_m19_p0c_screen_close_in_memory.py`](../tools/build_m19_p0c_screen_close_in_memory.py), sur base P0b/R88 figée |
| Candidat **expérimental en mémoire** | **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` |
| API / segments | **82 commandes, 92 entrées AP20** ; mêmes tokens et mêmes signatures que P0b |
| Cible | **MC68020 / 68EC020 minimum** ; WinUAE fonctionnel conseillé 68030/JIT ON |
| Gate A native | **PASS**, tests CPU020/ABI et wrapper V2, systèmes AMOS/Exec/graphics/Intuition **simulés** |
| Gate B / Gate C / Gate D | **NON TESTÉES** pour le candidat P0c |

La candidate P0c **ne remplace ni** `dist/AMOSPro_AGA.Lib` (P0b installé) **ni** `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R84). Aucun nouveau token ou commande de rendu Bob n'est disponible. L'ASC de campagne P0b reste le seul `tests/current/*.asc`.

## Liaison BOBS → véritable AGA Screen Close

Le constructeur vérifie le titre, le SHA et le layout de l'AP20 source P0b avant toute modification. Il n'autorise **que deux différences** dans les parts AP20 : (1) stub public de la commande `Aga Screen Close` (index **8**) redirigé vers le groupe **BOBS n°90**, et (2) ajout source-native MC68020 à la fin de ce groupe. Les **octets du groupe AGA n°91 sont inchangés**, tout comme les autres entrées.

- L'ancien `Aga Screen Close` est **groupe 91, offset natif 2008**, après dispatcher V2 de 34 octets.
- Le vrai init natif AGA place l'adresse de son état en `A5+0x1C8`; l'état réside à l'offset **0x1C2** de cette même unité. Le code natif Close est à **0x7FA**, soit **+0x638 octets** depuis l'état. La liaison est une adresse calculée **à l'exécution** dans l'unité AGA effectivement chargée, sans `BSR.W` inter-unités.
- Le wrapper [`m19_p0c_screen_close_bridge_emit.py`](../tools/m19_p0c_screen_close_bridge_emit.py) vérifie la signature de l'ancien prologue et `TypeOfMem`, appelle le [garde de pré-fermeture P0c](../tools/m19_p0c_screen_preclose_emit.py), puis **JSR vers le vrai ancien Close uniquement après** libération des buffers Chip et `WaitBlit`.
- Si l'état, GfxBase, le CPU ou la signature est invalide, le wrapper refuse la fermeture destructive. Aucune fermeture partielle volontaire ou saut vers une adresse inventée.
- Le constructeur vérifie le round-trip HUNK/AP20 V2, les `RBSR` et `GetP` existants, tous les tokens, la continuité du préfixe BOBS, le décodage CPU020 et le déplacement signé interpréteur ; le maximum RBSR est **27 928**, sous 32 767.

**Source autoritative :** les émetteurs P0a/P0b et les marqueurs AP20 figés du builder. Le fichier `src/R88/AMOSPro_AGA_R88_AGA_NATIVE.s` est une **restitution partielle pour audit**, pas un fichier de production à réassembler ou patcher.

## AMOS End : callback privé vérifié, armement restant à exposer

Le code source [`m19_p0c_program_end_bridge_emit.py`](../tools/m19_p0c_program_end_bridge_emit.py) ajoute **deux entrées privées** en fin de BOBS :

- `program_end_arm_entry` : appelé *après* préparation réelle d'un contexte Chip par banque. Il valide le propriétaire `A5`, la signature originale du callback et les slots `A5+0x1CC` et `A5+0x1D0`, puis enregistre le callback BOBS, sans écraser un callback tiers.
- `program_end_bridge_entry` : lors de `End`, retrouve par l'état AGA le callback original à l'offset **0x5A** de l'unité AGA (delta **−0x168** depuis l'état), appelle le cleanup Chip, **restaure les slots d'origine avant** d'appeler le vrai End natif AGA.
- En échec, le callback préserve les contextes sans appeler l'ancienne fermeture destructive. Les appels multiples, les programmes étrangers, les signatures corrompues et l'absence de GfxBase sont couverts.

**Limite de livraison : `program_end_arm_entry` n'est pas encore appelé automatiquement par une instruction AMOS publique.** Les commandes P0b de création/capture/masque ne font **pas** de staging Chip et ne peuvent donc ni armer ce callback, ni valider le nettoyage Chip au travers d'un programme utilisateur réel. Les tests CPU déclenchent l'armement **explicitement** dans le banc. Ne pas présenter ce callback comme fonctionnel pour n'importe quel programme AMOS ni comme une Gate B/C.

## Gates A observées

- [CI source/ap20 et CPU native](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43924796276) : **38 scénarios PASS** avec la vraie routine AGA `Close` inchangée et deux placements unitaires distants ; **54 scénarios PASS** avec vrai callback AGA `End` après armement privé ; **116 scénarios PASS** pour toutes les commandes P0b.
- [CI avec initialisation AGA d'origine exécutée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925071225) : **PASS**. La préparation de la fixture appelle désormais la véritable entrée native AGA Init (`APex`) et vérifie les pointeurs `State/End` qu'elle installe.
- Les précédents tests P0c restent en CI : **42 pré-fermeture**, **64 registre par banque**, **120 AGBO→Chip**, **64 allocations Chip**.
- Les services OS et le chargeur AMOS sont simulés dans Unicorn. Le *vrai* code natif AGA Close/End et Init, issu de la candidate figée, est exécuté ; **cela ne prouve ni WinUAE ni le vrai AMOS Compiler**.

## Préparation Gate B / C WinUAE — aucun résultat encore

Le test de validation séparé [`tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc`](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc) réalise trois étapes : ouverture/fermeture simple, ouverture/fermeture après création d'un double buffer **sans Swap en vol**, puis réouverture/fermeture. Aucun IFF ni ABK requis. Le test est **non validé par AMOS** ; seul son preflight statique est exigé avant les essais.

1. Télécharger l'artefact CI `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED` depuis le [workflow Gate A P0c](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-p0a-r88-get-gate-a.yml), **sans remplacer le binaire P0b du dépôt**. Conserver une sauvegarde du `AMOSPro_AGA.Lib` installé. Vérifier le SHA256 du fichier extrait : `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`.
2. WinUAE AGA/PAL, CPU **68030/JIT ON** pour la validation fonctionnelle. Installer **temporairement la Lib expérimentale** dans le slot d'extension AMOS Professional, redémarrer AMOS, programme vide puis `Project → Merge ASCII` sur l'ASC de design.
3. Lancer un test **Runtime distinct** et recueillir `RAM:M19_P0C_RUNTIME.TXT`, retour écran/AMOS et absence de Guru, freeze et fuite mémoire observée. Résultat attendu : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CLOSE_FIRST 1`, `CLOSE_WITH_DB 1`, `CLOSE_REOPEN 1`.
4. Compiler **un nouvel exécutable** depuis cet ASC avec la même bibliothèque puis lancer une **Gate C distincte**, recueillir `RAM:M19_P0C_COMPILED.TXT`, `PRG_STATE -1`, et les mêmes flags. Refaire la vérification SHA du binaire réellement installé plutôt que se fier à une chaîne imprimée par l'ASC.
5. Si divergence : noter le dernier `Close` retourné, mode Runtime/Compiler, CPU/JIT, copie du log et capture WinUAE ; restaurer la bibliothèque P0b protégée. Ne pas promouvoir `LAST_GOOD`.

Le journal écrit `CANDIDATE SHA256` à titre **d'étiquette du programme**, pas de preuve que le binaire installé possède effectivement cette empreinte.

**À ne pas faire :** conclure sur le nettoyage réel d'un contexte Chip Bob à partir de ce test. L'exposition publique de `registry_prepare` avec armement automatique et le dessin des Bobs sont les prochains jalons distincts. Aucun essai Amiga physique (Gate D).
