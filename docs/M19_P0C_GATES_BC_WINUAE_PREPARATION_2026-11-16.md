# M19 P0c — Gates B Runtime / C AMOS Compiler : préparation WinUAE (16/11/2026)

**Statut : PREPARE, Gates B/C NON TESTEES.** Ce document concerne exclusivement le pont public `Aga Screen Close` du candidat M19 P0c **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` (82 commandes / 92 entrees AP20). La Gate A MC68020 est PASS, avec services AMOS/Exec/graphics mockes. Aucune validation WinUAE ou Compiler ne peut etre deduite de cette Gate A.

## Fichiers de reference et interdictions

- **Banc a importer, non modifie :** [`tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc`](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc). Preflight AMOS `--strict-target` PASS dans la CI de Gate A ; syntaxe Runtime/Compiler reel **non validee**. Aucun IFF ni ABK requis.
- **Candidat temporaire :** artefact `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED` de la [CI 43925480841](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925480841), disponible jusqu'au **30/11/2026** d'apres les metadonnees de l'artefact. Le ZIP sert seulement au transport depuis GitHub Actions : extraire `AMOSPro_AGA.Lib`, **ne pas le copier dans `dist/`**.
- **Bibliotheque P0b officielle inchangee :** `dist/AMOSPro_AGA.Lib`, 82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9` ; seul ASC actif `tests/current/M19_P0B_MC68020_MASK_BANK.asc` intact.
- **`LAST_GOOD` R84 inchangee** : aucune promotion, aucun deplacement d'archive, aucune branche ou nouveau programme dans `tests/current/`.

## Preparation avant les essais

1. Faire une copie de securite **hors depot** du `AMOSPro_AGA.Lib` effectivement installe dans le slot `APSystem` de la machine emulee. Relever son SHA256. Ne pas changer la bibliotheque P0b suivie sur GitHub.
2. Extraire le candidat du workflow CI, verifier qu'il fait **87 020 octets** et que son SHA256 vaut exactement `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`. Arreter si cela diverge.
3. Installer **temporairement** ce fichier sous son nom `AMOSPro_AGA.Lib` dans le slot AGA `APSystem` de l'environnement WinUAE, redemarrer AMOS et verifier **la copie installee elle-meme** (taille + SHA), pas seulement l'archive telechargee.
4. WinUAE **AGA PAL, 68030 avec JIT ON** pour ces deux Gates fonctionnelles ; relever Chip/Fast, version AMOS Professional et AMOS Compiler V2 reellement utilises. MC68020/JIT OFF reste reserve aux benchmarks.
5. Dans un programme AMOS **vide**, `Project -> Merge ASCII` sur le fichier de `tests/design/` sans le copier dans `tests/current/` ni modifier l'ASC. Enregistrer la configuration et une capture du test exact. Le titre SHA imprime par l'ASC est une **etiquette**, pas une preuve du binaire charge.

## Gate B — Runtime distinct

1. Lancer le banc en **Runtime**. `PRG_STATE` doit etre **1**. Si le programme retourne `PRG_STATE 0`, il s'agit de l'interpreteur strict : ne **pas** le compter comme Gate B.
2. Observer successivement `Open -> Close`, `Open -> Double Buffer -> Close` **sans Swap en vol**, puis `Open -> Close` apres le DB. Chaque fermeture doit revenir sans Guru ni gel ; AMOS doit redevenir operationnel. Consigner les observations et, si possible, les valeurs Chip/Fast avant/apres.
3. Copier `RAM:M19_P0C_RUNTIME.TXT` hors WinUAE. Attendus : `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CLOSE_FIRST 1`, `CLOSE_WITH_DB 1`, `CLOSE_REOPEN 1`.
4. Verifier a l'ecran la ligne `LOG ... OPEN 0 CLOSE 0` : les codes d'ouverture/fermeture du fichier de rapport **ne sont pas stockes dans ce fichier**. Si un `Close` gele, **aucun rapport final n'est garanti** ; noter l'etape visible, l'etat WinUAE et la capture. Ne jamais fabriquer un PASS a partir d'un fichier precedent.

## Gate C — veritable AMOS Compiler distinct

1. Compiler un **nouvel executable** avec le vrai AMOS Compiler V2 depuis le **meme ASC**, sur la meme installation experimentale de P0c. Noter les options Compiler, le chemin de l'executable et la presence de banques embarquees (aucune n'est requise par ce banc).
2. Executer ce binaire sous WinUAE 68030/JIT ON. Le mode attendu est `PRG_STATE -1`. Verifier les trois fermetures et le retour effectif sans Guru/freeze, puis `RAM:M19_P0C_COMPILED.TXT` avec les memes drapeaux et `RUN_MODE COMPILED`.
3. Conserver separement journaux et captures Runtime/Compiler, versions/outils, SHA de la Lib **installee**, et erreurs precises. Le programme compile n'est **pas** une Gate C s'il ne revient pas de `Aga Screen Close`.

## Controle automatique des journaux (ne remplace pas WinUAE)

Depuis un dossier contenant le depot, apres avoir copie les deux fichiers `RAM:` depuis WinUAE :

```powershell
python -B tools/check_m19_p0c_winuae_logs.py --self-test
python -B tools/check_m19_p0c_winuae_logs.py --installed-lib "CHEMIN_REEL_APSystem/AMOSPro_AGA.Lib" --runtime "M19_P0C_RUNTIME.TXT" --compiled "M19_P0C_COMPILED.TXT"
```

Le script exige que la copie **indiquee** par `--installed-lib` ait la taille et le SHA exacts du candidat, et controle pour chaque journal l'identite, le mode `PRG_STATE` et les sept champs de resultat. Il refuse un journal Runtime reutilise comme Compiled, un champ manquant/duplique ou un FAIL. **`LOG PREFLIGHT PASS` ne signifie ni Gate B PASS ni Gate C PASS** : les retours visuels, l'absence de gel/Guru et la provenance du binaire charge restent a attester humainement.

## Matrice de decision et sortie

| Observation | Decision |
|---|---|
| Runtime termine, logs corrects, retour AMOS et absence de Guru/freeze observes | Gate B PASS, **uniquement** pour P0c candidat et ce scenario |
| Executable nouvellement compile, logs distincts, retour sans Guru/freeze | Gate C PASS, **uniquement** pour ce binaire et ce scenario |
| Gel, Guru, mauvaise empreinte, `PRG_STATE` incorrect, log incomplet | FAIL / NON TESTE selon le cas ; conserver le dernier point reussi et les captures |
| `End` natif sans armement Bob public | **Ne prouve pas** le cleanup Chip sur `End` : `program_end_arm_entry` reste prive |

**Apres les essais :** restaurer le `AMOSPro_AGA.Lib` P0b sauvegarde dans `APSystem`, redemarrer AMOS et reverifier SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`. Le candidat P0c ne doit pas remplacer le binaire officiel sur `main` sans decision explicite ulterieure.
