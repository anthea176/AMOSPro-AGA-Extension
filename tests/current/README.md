# M19 P0 — test Runtime WinUAE de la Lib Bank Chip Select/Free

**Bibliothèque active de test :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, [builder exact](../../tools/build_m19_b8_s1_bank_free_in_memory.py). **89 commandes / 185 entrées AP20**, cinq groupes MC68020, PC16 max 31 092. `Aga Bob Bank Free N` est une **instruction sans retour**. R84 `LAST_GOOD` n'a pas été remplacée.

**Seul ASC actif :** [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **12 837 octets**, ASCII LF. Il conserve la campagne B8 de **405 frames**, puis ajoute **3 phases** Bank Free/réactivation. Pas de VBL supplémentaire dans la boucle de 45 frames.

## Gate B Runtime — résultats reçus le 20/11/2026

**PASS fonctionnel d'après les deux journaux fournis** : 405/405 frames, neuf étapes, 403 Clear, 405 Update, trois appels Bank Free (Clear/Update/Swap tous à 3/3), une réactivation, aucun échec et `VERDICT PATH_OK`. Les fichiers `M19_P0_BANK_FREE1.TXT` et `M19_P0_BANK_FREE2.TXT` ont chacun **1 043 octets** et le même SHA256 `5dd8d1c7e15fb13bb0ba1ad7aa083c8928fb5b5af1f459df0d03631308e411e8` : ils sont **byte-identiques**, sans horodatage ni numéro de passage distinct. `RETRY_VBL 363` n'est pas un échec.

[Rapport de validation Gate B, avec limites et preuve des compteurs](../../docs/M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md). Le rendu visuel n'est pas vérifiable depuis les journaux et le SHA de la Lib affiché est une étiquette ASC.

## Procédure Runtime WinUAE reproductible

1. Sous Windows : `git pull origin main`, puis copier **uniquement** `dist/AMOSPro_AGA.Lib` dans le slot AGA existant de l'`APSystem` sous WinUAE. Vérifier si possible le SHA de cette copie. **Redémarrer AMOS**. Ne pas toucher à `AMOSPro_AGA_LAST_GOOD.Lib`.
2. Configuration : **AGA PAL, MC68030/JIT ON** comme pour les derniers essais. Les banques AMOS **24 et 25** doivent être libres. Dans un **programme vide**, utiliser `Project → Merge ASCII` pour importer le fichier ASC (ne pas utiliser `Load`).
3. Lancer le programme en **Runtime**. Observer les étapes de Bobs **2, 1, 0, 2, 4, 8, 16, 64, 16**, puis les trois phases : Free banque 24 (deux appels, idempotence), Free banque 25 et réactivation d'un Bob de la banque 24 après une nouvelle sélection. Aucune traînée ni ancien Bob résiduel.
4. Copier `RAM:M19_P0_BANK_FREE.TXT` hors de RAM: **avant le second lancement**. Relancer sans redémarrer AMOS ni `Erase All`, conserver le second journal et vérifier le retour à AMOS après `Aga Screen Close`.

## Valeurs attendues

| Champ du journal | Attendu |
|---|---|
| `RUN_MODE` / `PRG_STATE` | `RUNTIME` / `1` |
| `RESULT` / `ERR` / `VERDICT` | `1` / `0` / `PATH_OK` |
| `FRAMES_OK` / `STAGES_OK` | `405` / `9` (base B8) |
| `CLEAR_OK` / `UPDATE_OK` | `403` / `405` (base B8) |
| `CLEAR_FAILS` / `UPDATE_FAILS` / `SWAP_FAILS` | `0` / `0` / `0` |
| `OFF_COMMANDS_ISSUED` | `50` |
| `BANK_FREE_CALLS` | `3` |
| `BANK_FREE_CLEAR_OK` / `BANK_FREE_UPDATE_OK` | `3` / `3` |
| `BANK_FREE_SWAP_OK` / `BANK_FREE_REARM` | `3` / `1` |
| `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `2` |

`BANK_FREE_BANK1_LENGTH` et `BANK_FREE_BANK2_LENGTH` conservent les tailles AGBO avant Free : le programme vérifie qu'elles ne changent pas après les libérations. Le `LIB_SHA256` dans le journal **est une étiquette écrite par l'ASC**, pas une vérification du binaire chargé.

**En cas d'échec :** `ERR 14` = Update B8, `18` = Clear B8, `15` = Swap, `19` = banque vide, `20` = Clear après Free, `21` = Update après Free, `22` = AGBO modifié, `23/24` = compteurs Bank Free incorrects. Conserver les journaux et une capture du rendu.

## État de qualification

- **Gate A native MC68020 PASS : 225 contrôles** (104 préparation Chip + 121 Bank Free), deux relocations, AmigaOS/Blitter simulés. [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756).
- **Gate B Runtime WinUAE P0 : PASS fonctionnel d'après les journaux reçus.** Deux fichiers complets et conformes aux 405 frames/3 phases Free ; **byte-identiques**, preuve indépendante de second lancement et inspection visuelle non établies. [Rapport](../../docs/M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md).
- **Gate C AMOS Compiler P0 : NON TESTÉE, reportée.** Pas d'essai Compiler demandé pour cette campagne Runtime.
- **Gate D matériel : NON TESTÉE.**

Préflight purement statique : `python -B tools/test_m19_b8_clear_update_asc_static.py` puis `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`.

Rapport : [M19 P0 Bank Free](../../docs/M19_P0_BANK_FREE_GATES_2026-11-20.md).
