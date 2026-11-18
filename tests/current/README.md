# M19 P0j-b7 — banc End sans Close (Gates B/C à exécuter)

**Un seul ASC actif :** [`M19_P0J_B7_END_NO_CLOSE_BC_02.asc`](M19_P0J_B7_END_NO_CLOSE_BC_02.asc), **3 785 octets**, SHA256 `35b2cfbfc7e2661bd5c7736811619547ca32127dc7e9d97794bc3403780118ae`. ASCII pur, sans dépendance IFF/ABK. [Contrat et critères](../../docs/M19_P0J_B7_END_NO_CLOSE_BC_2026-11-18.md).

**Bibliothèque B7 inchangée :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, 86 commandes / 181 entrées AP20, quatre groupes natifs MC68020. Gate A B7 : **PASS 88 contrôles MC68020** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)). **Gates B/C du nouveau scénario End : NON TESTÉES**, Gate D physique : NON TESTÉE.

L'[ASC précédent Draw + Swap + Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a078ed085ae14352135cfe909c3c6f06e34befca/tests/current/M19_P0J_B7_DRAW_BC_01.asc) n'a pas été modifié : ses octets restent dans l'historique Git, pas dans `tests/passed/` sans preuves archivées complètes. La capture de rendu compilé déjà communiquée concerne **ce banc précédent**, pas l'actuel test End. `LAST_GOOD` R84 reste protégée (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`).

## Exécution WinUAE / AMOS

1. Synchroniser `main` et vérifier que la **copie réellement installée dans `APSystem`** a l'empreinte B7 ci-dessus. Ne pas remplacer `LAST_GOOD`.
2. Démarrer WinUAE **AGA PAL, 68030/JIT ON**. S'assurer que les **banques AMOS 24 et 25 sont libres**. Ouvrir un programme vierge, puis **Project → Merge ASCII** de `tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc`. Ne pas faire `Load` sur le texte ASCII.
3. Lancer le programme en Runtime (Gate B). Observer les quatre Bobs — deux masqués rouges dont un rogné à gauche, deux opaques jaunes dont un rogné à droite — sur le fond bleu foncé. Au bout d'environ 120 VBL, le code doit **terminer par `End`**, sans appeler `Aga Screen Close`, `Amos To Front` ou `Erase` dans la voie nominale.
4. Sauvegarder immédiatement `RAM:M19_B7_END_RUNTIME.TXT` **hors RAM:**, noter si l'écran AGA a disparu, si AMOS a repris la main, si WinUAE a gelé ou affiché un Guru. Un nouveau lancement sans reset est un contrôle utile, mais une banque encore réservée (`ERR 2`) n'est pas, à elle seule, une preuve de fuite Chip ; relever le cas au lieu d'effacer les banques silencieusement.
5. Compiler **le même ASC avec le véritable AMOS Compiler V2**, puis exécuter le nouveau binaire dans la même configuration. Sauvegarder séparément `RAM:M19_B7_END_COMPILED.TXT`. La sortie doit revenir au **contexte appelant** du programme compilé (Workbench/CLI selon lancement), sans écran AGA bloqué, freeze ni Guru. Ne pas confondre cette sortie avec un retour à l'éditeur AMOS.

## Journaux et verdict

En voie nominale, les journaux doivent indiquer `PRG_STATE 1` (Runtime) ou `PRG_STATE -1` (Compiled), `PRE_END_OK 1`, `DRAW 1`, `SWAP 1`, deux images présentes, `MASK_FLAG 1`, `SCREEN_OPEN_BEFORE_END 1` et `EXPLICIT_SCREEN_CLOSE 0`.

**Le marqueur `PRE_END_OK 1` prouve uniquement que le programme a atteint l'instruction `End`, jamais que le callback s'est terminé.** Le fichier est fermé **avant** l'appel End. Le champ `POST_END_STATUS UNOBSERVABLE_IN_PROGRAM` est intentionnel : aucun `RESULT PASS` automatique n'est produit. Le **PASS B/C exige l'observation du retour effectif à l'environnement appelant, sans Guru/freeze, suivie si possible d'un nouveau lancement**. Ce banc ne mesure pas directement les allocations Chip ni un délai de notification Safe/Disp réel.

Si l'un des contrôles de préparation échoue, le programme suit **`_FAIL:`** : fermeture et nettoyage explicites, puis message `M19 B7 END TEST NOT REACHED, ERR <code>`. **Ce chemin d'erreur n'est pas une validation du callback End.** Codes 1=AGA absente, 2=banques occupées, 3=Open, 4=Double Buffer, 5–12=préparation, 13=Draw, 14=Swap, 15=ouverture log, 16=fermeture log.

**Fournir** les deux journaux Runtime/Compiled, l'observation visuelle **après la sortie End**, la configuration WinUAE et tout message Guru/ERR. Les Gates B/C du parcours End restent **NON TESTÉES** jusqu'à réception des preuves correspondantes.
