# M19 P0 Bank Free — Gate B Runtime WinUAE (journaux du 20/11/2026)

**Statut : PASS fonctionnel d'après les deux journaux Runtime fournis par l'auteur.** La preuve est limitée aux chemins exécutés et aux compteurs de l'ASC ; elle ne constitue ni un contrôle visuel, ni une mesure du binaire installé, ni une Gate C AMOS Compiler.

## Version et banc

- **Candidate de travail :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **117 896 octets**, SHA256 attendu `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, 89 commandes / 185 entrées AP20, source [builder M19 P0](../tools/build_m19_b8_s1_bank_free_in_memory.py).
- **Test ASC :** [`tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), 12 837 octets, 405 frames / neuf étapes, trois phases Bank Free et réactivation.
- **Fichiers reçus dans la conversation :** `M19_P0_BANK_FREE1.TXT` et `M19_P0_BANK_FREE2.TXT`, chacun **1 043 octets**, **48 lignes**, fins de ligne CRLF. SHA256 du contenu brut de **chacun** : `5dd8d1c7e15fb13bb0ba1ad7aa083c8928fb5b5af1f459df0d03631308e411e8`.
- **Identité :** les deux fichiers sont **strictement identiques octet par octet**. Ils sont cohérents avec deux exécutions réussies du même banc, mais aucune donnée interne (horodatage / numéro d'exécution) ne prouve qu'ils correspondent à deux lancements indépendants.

## Vérification exhaustive des compteurs

| Contrôle | Journal 1 | Journal 2 | Verdict |
|---|---:|---:|---|
| `RUN_MODE` / `PRG_STATE` | RUNTIME / 1 | RUNTIME / 1 | conforme |
| `RESULT` / `ERR` / `VERDICT` | 1 / 0 / PATH_OK | 1 / 0 / PATH_OK | conforme |
| `FRAMES_TARGET` / `FRAMES_OK` | 405 / 405 | 405 / 405 | conforme |
| `STAGES_TARGET` / `STAGES_OK` | 9 / 9 | 9 / 9 | conforme |
| Bobs par étape (45 frames chacune) | 2, 1, 0, 2, 4, 8, 16, 64, 16 | identique | conforme |
| `DOUBLE_BUFFER` / `OFF_COMMANDS_ISSUED` | 1 / 50 | 1 / 50 | conforme |
| `FILL_FAILS` / `COPY_FAILS` | 0 / 0 | 0 / 0 | conforme |
| `CLEAR_OK` / `CLEAR_FAILS` | 403 / 0 | 403 / 0 | conforme |
| `UPDATE_OK` / `UPDATE_FAILS` | 405 / 0 | 405 / 0 | conforme |
| `SWAP_FAILS` | 0 | 0 | conforme |
| `BANK_FREE_CALLS` | 3 | 3 | conforme |
| `BANK_FREE_CLEAR_OK` / `BANK_FREE_UPDATE_OK` | 3 / 3 | 3 / 3 | conforme |
| `BANK_FREE_SWAP_OK` / `BANK_FREE_REARM` | 3 / 1 | 3 / 1 | conforme |
| `BANK_FREE_BANK1_LENGTH` / `BANK_FREE_BANK2_LENGTH` | 612 / 456 | 612 / 456 | conforme |
| `RETRY_VBL` | 363 | 363 | informatif ; aucune défaillance associée |
| `CLOSE_RETURNED` / `BANKS_ERASED` | 1 / 2 | 1 / 2 | conforme |

**Interprétation :** les compteurs enregistrent une exécution Runtime complète des 405 frames, des appels `Aga Bob Bank Free N`, puis des opérations de Clear/Update/Swap et réactivation sans erreur. La répétition du Bank Free et la conservation des longueurs AGBO passent les contrôles du banc. Le nombre de reprises `RETRY_VBL 363` ne constitue pas un benchmark de vitesse.

## Limites de la preuve

1. Le champ `LIB_SHA256` des fichiers est **une étiquette fixe générée par l'ASC**, pas un SHA calculé sur la bibliothèque réellement chargée dans WinUAE.
2. Aucun horodatage/identifiant de passage ne distingue les deux fichiers byte-identiques ; la preuve d'un **second lancement autonome sans redémarrage AMOS** reste déclarative.
3. Les fichiers ne mesurent pas directement la quantité de Chip RAM libérée et ne prouvent pas la **qualité visuelle** (absence de traînées), faute de capture/observation transmise.
4. Aucun essai **Gate C AMOS Compiler** sur cette candidate P0 ; Gate D Amiga physique non testée.
5. La promotion explicite de P0 a ensuite rendu `dist/AMOSPro_AGA_LAST_GOOD.Lib` byte-identique à la Lib P0. L'ancien binaire R84 reste reconstructible depuis son builder historique et son commit Git ; cette promotion ne valide pas la Gate C ni un test visuel.

## Qualification

- **Gate A : PASS** — 225 vérifications MC68020 simulées en CI ([campagne initiale](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)).
- **Gate B : PASS fonctionnel d'après les journaux Runtime reçus**, périmètre et limites précisés ci-dessus.
- **Gate C : NON TESTÉE / reportée.**
- **Gate D : NON TESTÉE.**

M19 reste ouvert (prochaines API Bob) et M20 reste en attente. Ceci ne modifie pas le banc ASC ni la Lib installable.
