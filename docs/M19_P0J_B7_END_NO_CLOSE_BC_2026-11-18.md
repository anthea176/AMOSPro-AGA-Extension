# M19 P0j-b7 — test WinUAE End sans Aga Screen Close (18/11/2026)

**Statut : PRÉPARÉ ; Gate B Runtime et Gate C véritable AMOS Compiler NON TESTÉES pour ce scénario.** La Gate A native B7 est déjà PASS (88 contrôles MC68020, [CI 44185874211](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)), incluant des notifications Safe/Disp simulées. Elle ne valide pas les événements AmigaOS réels.

## Version et périmètre immuables

| Élément | Référence |
| --- | --- |
| Extension active | `dist/AMOSPro_AGA.Lib` — 102 072 octets, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b` |
| Source B7 | `tools/build_m19_p0j_end_lifecycle_in_memory.py` — 86 commandes, 181 sections AP20, quatre groupes MC68020 |
| **Unique ASC actif** | [`M19_P0J_B7_END_NO_CLOSE_BC_02.asc`](../tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc) — 3 785 octets, SHA256 `35b2cfbfc7e2661bd5c7736811619547ca32127dc7e9d97794bc3403780118ae` |
| Banc antérieur | [`M19_P0J_B7_DRAW_BC_01.asc`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a078ed085ae14352135cfe909c3c6f06e34befca/tests/current/M19_P0J_B7_DRAW_BC_01.asc), byte-identique dans l'historique Git ; capture compilée fournie lors de la campagne précédente |
| Protection | R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` intacte ; aucune promotion ni nouvelle Lib |

## Parcours prévu

Le banc réutilise la séquence validée du scénario Draw précédent : écran AGA PAL 320×256×256, double buffering, deux banques 24/25, masque index 0, quatre Bobs (dont deux rognés), appel `Aga Bob Draw`, puis un seul `Aga Swap` réussi. Il maintient ensuite l'image pendant 120 VBL.

**La différence discriminante :** sur le chemin de succès, il **ne fait aucun `Aga Screen Close`, aucun `Amos To Front` et aucun `Erase`**. Il écrit et ferme un journal `BEFORE_END` puis exécute directement l'instruction AMOS `End`, afin de solliciter le callback natif B7. **Le chemin d'erreur** conserve volontairement `Aga Screen Close` et le nettoyage, mais il ne doit pas être confondu avec un End validé.

## Critères expérimentaux

1. **Runtime** : `RAM:M19_B7_END_RUNTIME.TXT` contient `PRG_STATE 1`, `PRE_END_OK 1`, `DRAW 1`, `SWAP 1`, `EXPLICIT_SCREEN_CLOSE 0`. Observer le retour à AMOS sans écran persistant, blocage ni Guru.
2. **Compiled** : sur un nouvel exécutable issu du **même ASC**, `RAM:M19_B7_END_COMPILED.TXT` contient `PRG_STATE -1` et les mêmes champs Draw/Swap. Observer le retour au lanceur du binaire compilé (Workbench/CLI selon contexte) sans freeze/Guru.
3. **Répétition** : tenter un deuxième lancement dans la même session. S'il échoue parce que les banques 24/25 restent réservées, enregistrer `ERR 2` ; ne pas le qualifier automatiquement de fuite Chip ou de panne du callback.
4. **Mémoire / notifications** : pour démontrer la libération réelle des ScreenBuffers et MsgPorts ou les délais Safe/Disp, prévoir une mesure ou un banc instrumenté supplémentaire. Le journal pré-End **ne peut pas** constater ces événements postérieurs.

Les deux journaux sont fermés **avant `End`**. Le marqueur `PRE_END_OK 1` n'est **pas une preuve de terminaison réussie** ; le champ `POST_END_STATUS UNOBSERVABLE_IN_PROGRAM` interdit un faux verdict automatique. Une capture avant End prouve les pixels, non la fermeture. Le verdict PASS B/C nécessite **les observations de sortie et les journaux de la bonne version**, pas seulement un préflight statique.

## Validation préalable

[Préflight AMOS](../tools/amos_preflight.py) en mode `--strict-target` sur l'ASC exact, puis [test statique dédié](../tools/test_m19_p0j_b7_end_asc_static.py) vérifiant SHA du programme, token Draw et Swap, chemin succès End et nettoyage uniquement en erreur. La CI de politique des chemins doit confirmer **un seul ASC dans `tests/current/`** et l'intégrité des références historiques.

**WinUAE de validation :** AGA PAL, 68030/JIT ON. Distinguer les deux Gates B et C, sauvegarder les deux fichiers de `RAM:` avant tout reset. [Procédure opératoire](../tests/current/README.md).

**Aucune modification du code natif, du builder B7, de la bibliothèque active ou de `LAST_GOOD` n'est demandée par ce test.** Il n'autorise pas une promotion de release.
