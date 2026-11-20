# M19 B8 — Aga Bob Clear / Update : campagne unique WinUAE Runtime et AMOS Compiler

**BIBLIOTHÈQUE ACTIVE DE TEST** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **115 744 octets**, SHA256 `00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae`, reconstruite **octet pour octet** par `tools/build_m19_b8_first_update_in_memory.py::build_b8_first_update()`. **88 commandes / 184 entrées AP20**, 5 unités MC68020, PC16 max 29 962. Nouveaux tokens numériques `Aga Bob Clear` (182) et `Aga Bob Update` (183), résultats 1/0, **pas de Swap implicite**. La B7-m2 antérieure reste dans l'historique Git, `LAST_GOOD` R84 est intacte.

**SEUL ASC ACTIF** : [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **11 092 octets**, ASCII LF, sans asset externe ni banque présumée libre. Banque 24 et 25 doivent être libres. Le programme s'appuie sur le banc B7-m2 validé, mais **cette variante B8 est nouvelle : ses Gates B/C ne sont PAS encore validées**. Préflight et oracle statique : `python -B tools/test_m19_b8_clear_update_asc_static.py` et `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`.

## Exécution Runtime — Gate B à qualifier

1. Sur le PC Windows : `git pull origin main`, puis copier **uniquement** le nouveau `dist/AMOSPro_AGA.Lib` dans le slot AGA existant de `APSystem` sous WinUAE, en remplaçant la bibliothèque de travail précédente. **Redémarrer AMOS**. Ne pas toucher à `AMOSPro_AGA_LAST_GOOD.Lib`.
2. Configuration ciblée : **WinUAE AGA PAL, MC68030/JIT ON**, comme pour la dernière campagne B7-m2 (ne pas assimiler à une validation sur MC68020 réel). Dans un programme **vide**, `Project → Merge ASCII` du nouvel ASC : ne pas charger le fichier ASC par `Load`.
3. Lancer le programme. Vérifier visuellement le décor mouvant, les Bobs masqués/opaques, les étapes **2, 1, 0, 2, 4, 8, 16, 64, 16** et la disparition des anciens Bobs sans traînée. Vérifier le retour à AMOS après `Aga Screen Close`.
4. Récupérer `RAM:M19_B8_CLEAR_UPDATE.TXT` et en sauvegarder une copie **avant** le second lancement. Relancer dans la même session AMOS sans `Erase All` ni redémarrage, puis conserver un **deuxième** journal et une capture du rendu.

## Exécution compilée — Gate C à qualifier séparément

Dans le programme vierge, réimporter le même ASC après installation de la Lib B8 ; **compiler un nouvel exécutable avec AMOS Compiler**, puis lancer cet exécutable sous WinUAE AGA PAL 68030/JIT ON. Ne pas réutiliser l'ancien exécutable B7. Conserver le journal compilé distinct des deux journaux Runtime et relever tout freeze/Guru, notamment `Aga Screen Open`, `Aga Bob Update` et `Aga Screen Close`.

## Journal attendu si tout fonctionne (aucun PASS WinUAE encore attribué)

| Champ | Attendu |
|---|---|
| `RUN_MODE` | `RUNTIME` en Gate B, `COMPILED` en Gate C |
| `PRG_STATE` | `1` Runtime, `-1` Compiler |
| `RESULT` / `ERR` / `VERDICT` | `1` / `0` / `PATH_OK` |
| `FRAMES_OK` / `STAGES_OK` | `405` / `9` |
| `CLEAR_OK` / `CLEAR_FAILS` | `403` / `0` |
| `UPDATE_OK` / `UPDATE_FAILS` | `405` / `0` |
| `SWAP_FAILS` | `0` |
| `OFF_COMMANDS_ISSUED` | `50` |
| `CLOSE_RETURNED` / `BANKS_ERASED` | `1` / `2` |

Le banc saute volontairement `Clear` sur les **deux premières frames**, car aucune sauvegarde physique de la page correspondante n'existe avant son premier `Update`. Au moins un `Aga Bob` est défini avant le premier `Update` pour amorcer le callback End B7 **sans dessin préalable**. Le cas d'un `Update` initial sans Bob retourne 0 dans la candidate actuelle et n'est pas présenté comme pris en charge.

**Si échec :** `ERR 14` = Update, `ERR 18` = Clear, `ERR 15` = Swap, `ERR 13` = Copy warmup, `ERR 16` = Fill, `ERR 17` = texte ; aucune présentation après refus d'Update ou de Clear. Envoyer les journaux et la capture du moment d'échec. Un champ `LIB_SHA256` dans le journal est une étiquette de provenance de l'ASC, pas une lecture directe du binaire installé.

## Gates

- **Gate A MC68020 : PASS** — [CI 44635843744](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44635843744), 59 contrôles premier Update, plus 36 intégration et 60 non-régression avec OS/Blitter simulés.
- **Gate B Runtime WinUAE : NON TESTÉE sur B8.**
- **Gate C AMOS Compiler : NON TESTÉE sur B8.**
- **Gate D matériel physique : NON TESTÉE.**

Documentation technique : [M19 B8](../../docs/M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md) et [NEXT_SESSION](../../docs/NEXT_SESSION.md).
