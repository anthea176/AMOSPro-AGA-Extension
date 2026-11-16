# M19 P0c — Gates B Runtime / C AMOS Compiler : campagne active (16/11/2026)

**Statut actualisé le 16/11/2026 : Gate A PASS, Gates B/C PASS selon les deux journaux utilisateur.** [Rapport et limites de la preuve](M19_P0C_GATES_BC_2026-11-16.md). Le protocole ci-dessous reste applicable pour reproduire les essais. L'auteur a **autorisé la bascule P0b → P0c sur `main`**. Le candidat expérimental source-native MC68020 de `Aga Screen Close` est maintenant la **bibliothèque de travail active et unique** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 82 commandes et 92 entrées AP20. **Ce n'est pas une promotion** : `LAST_GOOD` reste R84 et n'est pas modifiée.

## Installation de la candidate canonique

- **Bibliothèque à installer :** exclusivement `dist/AMOSPro_AGA.Lib` depuis le **même commit `main` que ce document**. Pas de ZIP, pas d'artefact CI parallèle, pas de binaire extrait de `tests/design/`.
- **Banc actif unique :** [`tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`](../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc). Seuls ses commentaires d'en-tête changent par rapport au [brouillon initial non validé](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc). La syntaxe réelle WinUAE/AMOS Compiler reste à éprouver.
- **Cible :** code natif **MC68020/68EC020 minimum** ; **WinUAE AGA PAL 68030, JIT activé** pour Gates B/C. MC68020 avec JIT désactivé réservé aux benchmarks.
- **Preuves :** [Gate A CPU020 et ABI](M19_P0C_SCREEN_CLOSE_BRIDGE_GATE_A_2026-11-16.md) et [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43934651866) avec services AmigaOS simulés. **Les deux journaux B/C sont désormais reçus et conformes ; l'identité réelle de la Lib installée et les captures/versions machine ne sont pas contenues dans ces TXT.**

Avant le test, synchroniser le clone Windows avec `main`. Sauvegarder **hors dépôt** le fichier `AMOSPro_AGA.Lib` actuellement installé dans le slot AGA `APSystem`, copier la Lib de `dist/` sous son nom original `AMOSPro_AGA.Lib`, **vérifier taille et SHA de la copie installée** puis redémarrer AMOS. Garder le même numéro de slot d'extension. Relever versions AMOS Professional / Compiler V2, RAM Chip/Fast et paramètres WinUAE.

## Gate B — Runtime WinUAE

1. Dans un programme vide, **Project → Merge ASCII** depuis `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` ; ne pas charger l'ASC par `Load`.
2. Exécuter en **Runtime**, confirmer `PRG_STATE 1` (si `0`, interpréteur strict : ce n'est pas cette Gate B).
3. Observer trois cycles de fermeture : `Open → Close` simple, `Open → Double Buffer → Close` **sans Swap en vol**, puis `Open → Close` après ce DB.
4. Le programme doit terminer sans freeze/Guru, **revenir à AMOS**, et produire `RAM:M19_P0C_RUNTIME.TXT` avec `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CLOSE_FIRST 1`, `CLOSE_WITH_DB 1`, `CLOSE_REOPEN 1`.
5. Sur l'écran de fin, vérifier également `LOG ... OPEN 0 CLOSE 0` : les erreurs d'écriture/fermeture du journal ne sont pas enregistrées dans le journal lui-même. Si Close gèle, aucune sortie finale n'est garantie : conserver dernière étape visible, capture et configuration sans inventer un PASS.

## Gate C — vrai AMOS Compiler V2

Compiler **un nouvel exécutable** depuis **le même ASC actif**, avec la même bibliothèque réellement installée. Noter la version et les options du Compiler, le chemin et les éventuelles banques embarquées (ce banc n'en exige aucune).

Lancer l'exécutable sous WinUAE et contrôler l'absence de Guru/freeze, le retour effectif et le fichier `RAM:M19_P0C_COMPILED.TXT` : `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, les trois flags `CLOSE_... 1` et `LOG ... OPEN 0 CLOSE 0` à l'écran. Garder les logs **séparés** et une capture par mode. Le SHA affiché dans l'ASC est une **étiquette** : seule la vérification de la Lib installée établit la provenance.

## Analyse statique des deux journaux

```powershell
python -B tools/check_m19_p0c_winuae_logs.py --self-test
python -B tools/check_m19_p0c_winuae_logs.py --installed-lib "CHEMIN_APSystem/AMOSPro_AGA.Lib" --runtime "M19_P0C_RUNTIME.TXT" --compiled "M19_P0C_COMPILED.TXT"
```

Le script contrôle les identités/modes/champs, **mais ne prouve pas** à lui seul Gate B/C : la vraie exécution, les captures, le retour à AMOS et l'absence de gel restent nécessaires.

## Portée et protections

- Le callback privé `program_end_arm_entry` **n'est pas armé** par les commandes publiques P0b/P0c. Un test de `End` de programme ne démontre pas encore le nettoyage Chip des Bobs ; **aucun Bob affichable nouveau** n'est ajouté.
- P0b (**82 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) conserve ses résultats Gates A/B/C **historiques** et son ASC exact dans l'historique de `main` ; on ne modifie ni `tests/passed/` ni le brouillon `tests/design/`. Le binaire P0b est reproductible par son builder source figé.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 (67 904 octets ; SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`) demeure **protégée**. Aucun tag/release/promotion automatique.

**Verdict après réception : Gate A PASS ; Gate B Runtime et Gate C Compiler PASS selon les journaux, pour ce scénario uniquement.** Interpréteur strict et Gate D NON TESTÉS ; preuve visuelle/installation non jointe. [Rapport](M19_P0C_GATES_BC_2026-11-16.md).
