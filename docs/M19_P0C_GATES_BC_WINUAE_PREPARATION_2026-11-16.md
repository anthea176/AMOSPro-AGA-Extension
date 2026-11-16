# M19 P0c — Gates B Runtime / C AMOS Compiler : préparation WinUAE (16/11/2026)

**Statut : PREPARE, Gates B/C NON TESTEES.** La Gate A MC68020 (services AMOS/Exec/graphics simulés) a validé en mémoire le pont `Aga Screen Close` P0c, **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` (82 commandes / 92 entrées AP20). Cela ne constitue pas une bibliothèque distribuée ni une Gate B/C.

## Verrou de distribution du dépôt (normatif)

- **Une seule Lib distribuée :** `dist/AMOSPro_AGA.Lib` sur `main`, jamais un artefact CI téléchargé, un ZIP, un dossier expérimental ou une Lib renommée.
- **Un seul ASC actif :** `tests/current/*.asc`, en cohérence avec le binaire livré. Le [brouillon P0c](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc) est conservé sans changement et n'est **pas** le banc actif.
- **Protection demandée pour ce jalon :** `dist/AMOSPro_AGA.Lib` reste actuellement **P0b**, 82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, et `tests/current/M19_P0B_MC68020_MASK_BANK.asc` reste l'unique test actif. `LAST_GOOD` R84 et les archives restent intacts.
- **Conséquence :** il est **interdit de lancer la campagne P0c** en remplaçant temporairement la Lib installée par un artefact GitHub Actions, ou en important un ASC de `tests/design/` comme s'il était actif. Les artefacts d'anciennes exécutions GitHub Actions sont historiques ; le workflow courant vérifie les candidats en mémoire et ne publie plus de `.Lib`.

## Activation ultérieure — uniquement après autorisation explicite de bascule P0b → P0c

1. Vérifier les sources P0c sur `main`, le builder [`build_m19_p0c_screen_close_in_memory.py`](../tools/build_m19_p0c_screen_close_in_memory.py), la cible **MC68020 minimum**, la Gate A et l'identité attendue du candidat. Le build officiel doit être reproductible par le dépôt, pas issu d'un ZIP.
2. Livrer **directement sur `main`** le candidat autorisé sous `dist/AMOSPro_AGA.Lib` avec la taille/SHA exacts ; assurer le seul banc de campagne correspondant sous `tests/current/`, sans toucher aux tests historiques ou `LAST_GOOD`. Ce changement est **hors du périmètre de cette préparation**.
3. Relever le commit précis, vérifier les deux fichiers sur `main`, puis synchroniser le clone local Windows. Installer la **seule Lib canonique** dans le slot AGA `APSystem` de WinUAE et redémarrer AMOS. Vérifier le SHA de la copie réellement installée, pas le titre affiché dans l'ASC.
4. WinUAE **AGA PAL, 68030/JIT ON** pour les Gates fonctionnelles ; relever RAM Chip/Fast, versions AMOS Professional / Compiler et paramètres de la machine. Utiliser `Project -> Merge ASCII` sur l'ASC **actif**, sans modifier ses octets.

## Gate B — Runtime (après activation seulement)

Exécuter successivement `Open -> Close`, `Open -> Double Buffer -> Close` **sans Swap en vol**, puis `Open -> Close` après le DB. Vérifier retour à AMOS sans Guru, freeze ni fermeture partielle. Attendre `RAM:M19_P0C_RUNTIME.TXT`, `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS` et `CLOSE_FIRST 1`, `CLOSE_WITH_DB 1`, `CLOSE_REOPEN 1`. Capturer le résultat et la ligne écran `LOG ... OPEN 0 CLOSE 0`, car les erreurs d'ouverture/fermeture du journal ne sont pas enregistrées dans ce fichier.

## Gate C — vrai AMOS Compiler (après Gate B)

Compiler un **nouvel exécutable** depuis le **même ASC actif** avec le vrai AMOS Compiler V2 et la même Lib installée, puis exécuter sous WinUAE. Attendre `RAM:M19_P0C_COMPILED.TXT`, `RUN_MODE COMPILED`, `PRG_STATE -1`, les mêmes flags de succès et l'absence de gel/Guru. Conserver journaux, captures, configuration et SHA du binaire réellement chargé. Le texte `CANDIDATE SHA256` de l'ASC n'est qu'une étiquette.

## Contrôle statique des journaux (lorsque les Gates auront été exécutées)

```powershell
python -B tools/check_m19_p0c_winuae_logs.py --self-test
python -B tools/check_m19_p0c_winuae_logs.py --installed-lib "CHEMIN_APSystem/AMOSPro_AGA.Lib" --runtime "M19_P0C_RUNTIME.TXT" --compiled "M19_P0C_COMPILED.TXT"
```

Le validateur de logs refuse les modes ou SHA incohérents, mais ne remplace ni l'exécution WinUAE ni l'observation du retour effectif à AMOS. Un `LOG PREFLIGHT PASS` n'est pas une Gate B/C PASS.

**Limite inchangée :** le callback privé `End` n'est pas armé par une API publique ; ce banc ne prouve pas le nettoyage de contextes Bob Chip à `End`. Aucune promotion automatique, aucune nouvelle branche, aucune modification de P0b ou de `LAST_GOOD` dans cette préparation.
