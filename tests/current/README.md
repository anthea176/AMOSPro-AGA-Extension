# M19 B8 S1 — Clear/Update SafePort borné : campagne WinUAE Runtime et AMOS Compiler

**BIBLIOTHÈQUE ACTIVE DE TEST** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **116 104 octets**, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`, reconstruite **octet pour octet** par `tools/build_m19_b8_safe_retry_in_memory.py::build_b8_safe_retry()`. **88 commandes / 184 entrées AP20**, 5 unités MC68020, PC16 max 29 962. Nouveaux tokens numériques `Aga Bob Clear` (182) et `Aga Bob Update` (183), résultats 1/0, **pas de Swap implicite**. La B7-m2 antérieure reste dans l'historique Git, `LAST_GOOD` R84 est intacte.

**SEUL ASC ACTIF S1** : [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **11 092 octets**, ASCII LF, sans asset externe ni banque présumée libre. Banque 24 et 25 doivent être libres. Le programme s'appuie sur le banc B7-m2 validé, mais **Gate B Runtime S1 validée par deux journaux à 405/405 frames ; Gate C Compiler reportée**. Préflight et oracle statique : `python -B tools/test_m19_b8_clear_update_asc_static.py` et `python -B tools/amos_preflight.py --strict-target tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`.

## Exécution Runtime — Gate B déjà validée (protocole conservé pour référence)

1. Sur le PC Windows : `git pull origin main`, puis copier **uniquement** le nouveau `dist/AMOSPro_AGA.Lib` dans le slot AGA existant de `APSystem` sous WinUAE, en remplaçant la bibliothèque de travail précédente. **Redémarrer AMOS**. Ne pas toucher à `AMOSPro_AGA_LAST_GOOD.Lib`.
2. Configuration ciblée : **WinUAE AGA PAL, MC68030/JIT ON**, comme pour la dernière campagne B7-m2 (ne pas assimiler à une validation sur MC68020 réel). Dans un programme **vide**, `Project → Merge ASCII` du nouvel ASC : ne pas charger le fichier ASC par `Load`.
3. Lancer le programme. Vérifier visuellement le décor mouvant, les Bobs masqués/opaques, les étapes **2, 1, 0, 2, 4, 8, 16, 64, 16** et la disparition des anciens Bobs sans traînée. Vérifier le retour à AMOS après `Aga Screen Close`.
4. Récupérer `RAM:M19_B8_CLEAR_UPDATE.TXT` et en sauvegarder une copie **avant** le second lancement. Relancer dans la même session AMOS sans `Erase All` ni redémarrage, puis conserver un **deuxième** journal et une capture du rendu.

## Exécution compilée — Gate C reportée (aucun nouvel essai demandé)

Cette Gate n'est **pas validée pour S1** et est reportée à la demande de l'auteur. Ne pas relancer AMOS Compiler dans la campagne actuelle. Si une future distribution compilée exige une qualification, reprendre alors ce protocole dans une campagne distincte.

## Résultats Runtime S1 effectivement obtenus

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

**IMPORTANT : ne rajouter aucun `Aga Wait Vbl` dans la boucle `For _STEP=1 To 45`.** Le correctif S1 attend au maximum 3 VBL *dans la Lib*, uniquement quand SafePort n'a pas encore livré son message ; pas de Swap implicite. Un autre échec reste bloquant (`DIRTY`). Réimporter le fichier GitHub plutôt que réutiliser la variante locale du test avec VBL. Le banc saute volontairement `Clear` sur les **deux premières frames**, car aucune sauvegarde physique de la page correspondante n'existe avant son premier `Update`. Au moins un `Aga Bob` est défini avant le premier `Update` pour amorcer le callback End B7 **sans dessin préalable**. Le cas d'un `Update` initial sans Bob retourne 0 dans la candidate actuelle et n'est pas présenté comme pris en charge.

**Si échec :** `ERR 14` = Update, `ERR 18` = Clear, `ERR 15` = Swap, `ERR 13` = Copy warmup, `ERR 16` = Fill, `ERR 17` = texte ; aucune présentation après refus d'Update ou de Clear. Envoyer les journaux et la capture du moment d'échec. Un champ `LIB_SHA256` dans le journal est une étiquette de provenance de l'ASC, pas une lecture directe du binaire installé.

## Gates

- **Gate A MC68020 : PASS** — [CI S1 44780312459](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44780312459), **119 contrôles du Clear SafePort 1–3 VBL sur deux relocations**, plus non-régressions B7/B8 (OS/Blitter simulés).
- **Gate B Runtime WinUAE : PASS sur deux journaux S1.** 405/405 frames, 9/9 étapes, 403 Clear, 405 Update, 50 Off, ERR 0, PATH_OK. Aucun VBL artificiel dans la boucle de l'ASC du dépôt. Ce résultat ne constitue pas une Gate C.
- **Gate C AMOS Compiler : NON TESTÉE sur S1 et reportée à la demande de l'auteur.** Ne plus la solliciter pour clôturer la validation Runtime.
- **Gate D matériel physique : NON TESTÉE.**

Documentation technique : [M19 B8](../../docs/M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md) et [NEXT_SESSION](../../docs/NEXT_SESSION.md).
