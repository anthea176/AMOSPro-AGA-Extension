# M19 B7-m2 — cycle de vie Bob, Gates B/C PASS sur WinUAE

**Programme actif unique :** [M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc](M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10911 octets**, SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`. Le précédent test à décor texturé a été retiré de `tests/current/`, mais reste [accessible dans le commit historique cb3d97a](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc). Sa Gate B passée **ne vaut pas validation automatique de ce nouveau programme**.

**Lib active pour les Gates B/C validées :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **M19 B7-m2**, 102 400 octets, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`, 86 commandes / 181 AP20, cible **MC68020+**. `LAST_GOOD` R84 reste protégée. Gate A B7-m2 PASS ; Gate B B7-m2 PASS sur deux lancements successifs sans `Erase All` ni redémarrage ; Gate C AMOS Compiler PASS sur une exécution complète. [Journaux et limites](../../docs/M19_B7M2_GATES_BC_2026-11-19.md).


## Gate C AMOS Compiler — PASS (19/11/2026)

**Corrigé :** `Prg State=-1` définit maintenant `RUN_MODE COMPILED` et n'active plus `ERR 1`. Une valeur `Prg State` inattendue reste refusée. La même boucle graphique (405 frames, neuf étapes, 50 Off), les banques 24/25, le Close et le journal sont inchangés ; seul le titre du journal indique dynamiquement le mode.

1. `git pull origin main`, puis réimporter le **même ASC mis à jour** avec `Project → Merge ASCII` dans un programme vide. Ne pas réutiliser l'ancien programme compilé ni l'ancien source déjà chargé.
2. Compiler ce programme sous AMOS Compiler avec la Lib B7-m2 actuelle (aucun changement de `.Lib`). Exécuter le **binaire produit** sous WinUAE AGA PAL 68030/JIT ON.
3. Récupérer `RAM:M19_B7M1_BOB_LIFECYCLE.TXT` : vérifier `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. Le nom RAM conserve B7M1 uniquement pour comparaison historique.
4. **Exécution compilée reçue et PASS** : la relance du même binaire compilé n'a pas été fournie. Si ce cas doit être qualifié séparément, conserver deux journaux (le même chemin RAM est écrasé à chaque exécution).

**Résultat observé :** journal utilisateur `M19_B7M1_BOB_LIFECYCLE(4).TXT` : `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `OFF_COMMANDS_ISSUED 50`, `FILL_FAILS/COPY_FAILS/DRAW_FAILS/SWAP_FAILS 0`, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. **Gate C fonctionnelle PASS sur cette exécution.** Le premier essai `PRG_STATE -1 / ERR 1` provenait d'un refus volontaire de l'ancien banc, pas d'un défaut natif. [Preuves détaillées](../../docs/M19_B7M2_GATES_BC_2026-11-19.md).

## Lancer sous WinUAE

1. Mettre à jour son dépôt **`main`** (`git pull`). Copier la Lib B7-m2 depuis `dist/AMOSPro_AGA.Lib` dans `APSystem` après sauvegarde de B7-m1, conserver le même slot d'extension et redémarrer AMOS. **AGA PAL, 68030/JIT ON**, AMOS Professional : **Runtime déjà validé** ; pour Gate C, **compiler le même ASC avec AMOS Compiler puis exécuter le vrai programme compilé sous WinUAE**. Le programme reconnaît maintenant `Prg State=-1` comme `RUN_MODE COMPILED`. Gate C fonctionnelle PASS sur le journal compilé fourni ; ne pas extrapoler à une relance compilée ou à un contrôle pixel exhaustif.
2. Ouvrir **un programme vide** puis **Project → Merge ASCII** du nouvel ASC. Les banques **24 et 25 doivent être libres** ; le programme les refuse si elles sont occupées et n'appelle jamais `Erase All`.
3. Lancer sans intervention : neuf étapes de **45 images chacune**, repérées par le texte en haut de l'écran. Vérifier particulièrement la disparition du Bob rouge à l'étape 2, la disparition complète à l'étape 3, la réactivation étape 4, puis la densité 64 à l'étape 8 et sa réduction à 16 à l'étape 9.
4. Après **405 frames**, retour à AMOS, fermeture et effacement uniquement des deux banques créées. Récupérer **`RAM:M19_B7M1_BOB_LIFECYCLE.TXT`** et l'envoyer avec un commentaire sur le rendu. **Sauvegarder le premier journal sur le PC avant la seconde exécution** (l'ASC réécrit le même chemin RAM), puis **relancer sans `Erase All`** et conserver le deuxième journal.

## Les neuf étapes visibles

| Étape | Bobs attendus | Action fonctionnelle |
|---|---:|---|
| 1 | 2 | Bob 1 rouge masqué, Bob 2 jaune opaque |
| 2 | 1 | `Aga Bob Off 1` : Bob 2 seul |
| 3 | 0 | `Aga Bob Off 2` : écran sans Bob, décor préservé |
| 4 | 2 | Réactiver les **mêmes IDs** 1 et 2, depuis leurs banques d'origine |
| 5 | 4 | Ajouter IDs 3 et 4 |
| 6 | 8 | Ajouter IDs 5 à 8 |
| 7 | 16 | Ajouter IDs 9 à 16 |
| 8 | 64 | Ajouter IDs 17 à 64, banques alternées, masques/opaques |
| 9 | 16 | `Aga Bob Off` sur IDs 17 à 64 : disparition des 48 objets |

Chaque frame restaure **uniquement** les anciennes zones des objets sur la bonne page arrière, avec clipping et source propre de décor à `y=32..63`. Les IDs sont réenregistrés pour les objets actifs, puis `Aga Bob Draw` et `Aga Swap` sont vérifiés. Aucune commande Bob n'est envoyée pour les IDs désactivés ; l'état `Off` est exercé dans le moteur, pas simulé par un dessin de couleur de fond.

**Aucune mesure de FPS ni Timer**. La scène est volontairement autonome, créée à partir de deux images AGBO (banques 24 et 25), sans IFF externe ni nouvelle API.

## Journal et verdict

Attendu en Runtime : `RUN_MODE RUNTIME`, `PRG_STATE 1` ; en Compiler : `RUN_MODE COMPILED`, `PRG_STATE -1` ; dans les deux cas : `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `DOUBLE_BUFFER 1`, `OFF_COMMANDS_ISSUED 50`, **neuf fois `STAGE_FRAMES_OK 45`** avec `EXPECT_BOBS` = 2/1/0/2/4/8/16/64/16, `FILL_FAILS 0`, `COPY_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. Vérifier également `LOG OPEN 0 CLOSE 0` sur l'écran AMOS.

**Attention :** `EXPECT_BOBS` indique le nombre *demandé* au moteur, et `OFF_COMMANDS_ISSUED` le nombre de commandes envoyées, pas un comptage des sprites effectivement visibles. Le constat graphique sous WinUAE reste nécessaire. `CLOSE_RETURNED` atteste le retour de l'appel, pas une preuve de l'absence totale de fuites système.

En cas d'échec : `ERR 3` = banques occupées ; `ERR 13` = Copy ; `ERR 14` = Draw ; `ERR 15` = Swap ; `ERR 17` = texte AGA. Aucun Swap n'est appelé après échec de Copy/Draw, et les commandes Off de stages suivants sont bloquées en cas d'erreur.

## Statut de validation

- **Gate A B7-m2 : PASS** — 75 groupes de vérifications MC68020 ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44413813790)).
- **Gate A B7-m1 historique : PASS** — [194 tests natifs MC68020 du cycle de vie](../../docs/M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md) en complément des tests multiframe.
- **Préflight ASC : PASS** — syntaxe statique stricte, 21 tests du préflight, modèle de **405 scènes graphiques sur deux buffers**, 6 305 segments Copy simulés et 50 Off modélisés. Ces simulations ne valident pas les vrais pixels matériels.
- **Gate B B7-m2 de cet ASC : PASS** — deux journaux Runtime 405/405 frames, 9/9 étapes, 50 Off, ERR 0, PATH_OK, relance sans `Erase All` ni redémarrage confirmée par l'auteur ; rendu vérifié à l'étape 8/9.
- **Gate C Compiler B7-m2 : PASS fonctionnelle** — `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, 405/405 frames, neuf étapes, `PATH_OK`, fermeture et deux banques libérées, une exécution documentée. Relance compilée et revue visuelle exhaustive non testées. [Journaux](../../docs/M19_B7M2_GATES_BC_2026-11-19.md).
- **Gate D Amiga physique : NON TESTÉE.**

[Prochaine étape M19](../../docs/M19_NEXT_BOB_LIFECYCLE_2026-11-18.md)


## Retour WinUAE du 18/11/2026 : relance FAIL

Deux journaux du meme programme sur B7-m1 : premier lancement
Runtime PASS 405/405, 9/9, ERR 0, rendu graphique confirme ; deuxieme
lancement SANS Erase All FAIL des le premier Draw (ERR 14, DRAW_FAILS 1,
FRAMES_OK 0). La Gate B de premiere execution est PASS ; la validation
du cycle de vie complet est **FAIL**. Le retour a AMOS et les banques
effacees ne prouvent pas la reinitialisation de la table de Bobs native.

Ce comportement reste **historique pour B7-m1**. La nouvelle candidate B7-m2
corrige la fermeture en Gate A : [CI 44413813790](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44413813790), 75 groupes de vérifications.
[Rapport technique](../../docs/M19_B7M2_CLOSE_RESET_GATE_A_2026-11-18.md).
La **bascule vers la seule Lib B7-m2 est autorisée le 18/11/2026**, sans Compiler,
promotion ni nouveau token. Le chemin ASC/log conserve B7M1 dans son nom
pour permettre la comparaison ; son contenu et LIB_SHA256 indiquent B7-m2.
Première et deuxième exécution B7-m2 PASS en Runtime, sans `Erase All` ; puis une exécution du vrai binaire AMOS Compiler PASS. [Bilan et limites](../../docs/M19_B7M2_GATES_BC_2026-11-19.md).
