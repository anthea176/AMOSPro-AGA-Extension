# M19 B7-m1 — test fonctionnel Bob Off/On et 64 Bobs (Gate B à réaliser)

**Programme actif unique :** [M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc](M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10 866 octets**, SHA256 `faed496a977a151850255f39f0ac134bd80014975b6dcd7942b27b351c05645d`. Le précédent test à décor texturé a été retiré de `tests/current/`, mais reste [accessible dans le commit historique cb3d97a](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc). Sa Gate B passée **ne vaut pas validation automatique de ce nouveau programme**.

**Lib à conserver :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **M19 P0j-b7-m1**, 102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, 86 commandes / 181 AP20, cible **MC68020+**. Aucun nouveau binaire ou changement de `LAST_GOOD`.

## Lancer sous WinUAE

1. Mettre à jour son dépôt **`main`** (`git pull`). La Lib B7-m1 déjà installée dans `APSystem` reste utilisable. **AGA PAL, 68030/JIT ON**, AMOS Professional en **Runtime uniquement** ; ne pas essayer le Compiler pour cette campagne.
2. Ouvrir **un programme vide** puis **Project → Merge ASCII** du nouvel ASC. Les banques **24 et 25 doivent être libres** ; le programme les refuse si elles sont occupées et n'appelle jamais `Erase All`.
3. Lancer sans intervention : neuf étapes de **45 images chacune**, repérées par le texte en haut de l'écran. Vérifier particulièrement la disparition du Bob rouge à l'étape 2, la disparition complète à l'étape 3, la réactivation étape 4, puis la densité 64 à l'étape 8 et sa réduction à 16 à l'étape 9.
4. Après **405 frames**, retour à AMOS, fermeture et effacement uniquement des deux banques créées. Récupérer **`RAM:M19_B7M1_BOB_LIFECYCLE.TXT`** et l'envoyer avec un commentaire sur le rendu. **Relancer une seconde fois sans `Erase All`** pour contrôler la stabilité du cycle de vie.

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

Attendu : `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `DOUBLE_BUFFER 1`, `OFF_COMMANDS_ISSUED 50`, **neuf fois `STAGE_FRAMES_OK 45`** avec `EXPECT_BOBS` = 2/1/0/2/4/8/16/64/16, `FILL_FAILS 0`, `COPY_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. Vérifier également `LOG OPEN 0 CLOSE 0` sur l'écran AMOS.

**Attention :** `EXPECT_BOBS` indique le nombre *demandé* au moteur, et `OFF_COMMANDS_ISSUED` le nombre de commandes envoyées, pas un comptage des sprites effectivement visibles. Le constat graphique sous WinUAE reste nécessaire. `CLOSE_RETURNED` atteste le retour de l'appel, pas une preuve de l'absence totale de fuites système.

En cas d'échec : `ERR 3` = banques occupées ; `ERR 13` = Copy ; `ERR 14` = Draw ; `ERR 15` = Swap ; `ERR 17` = texte AGA. Aucun Swap n'est appelé après échec de Copy/Draw, et les commandes Off de stages suivants sont bloquées en cas d'erreur.

## Statut de validation

- **Gate A B7-m1 : PASS** — [194 tests natifs MC68020 du cycle de vie](../../docs/M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md) en complément des tests multiframe.
- **Préflight ASC : PASS** — syntaxe statique stricte, 21 tests du préflight, modèle de **405 scènes graphiques sur deux buffers**, 6 305 segments Copy simulés et 50 Off modélisés. Ces simulations ne valident pas les vrais pixels matériels.
- **Gate B de ce nouvel ASC : NON TESTÉE** jusqu'au retour WinUAE.
- **Gate C vrai AMOS Compiler / Gate D Amiga physique : NON TESTÉES.**

[Prochaine étape M19](../../docs/M19_NEXT_BOB_LIFECYCLE_2026-11-18.md)


## Retour WinUAE du 18/11/2026 : relance FAIL

Deux journaux du meme programme sur B7-m1 : premier lancement
Runtime PASS 405/405, 9/9, ERR 0, rendu graphique confirme ; deuxieme
lancement SANS Erase All FAIL des le premier Draw (ERR 14, DRAW_FAILS 1,
FRAMES_OK 0). La Gate B de premiere execution est PASS ; la validation
du cycle de vie complet est **FAIL**. Le retour a AMOS et les banques
effacees ne prouvent pas la reinitialisation de la table de Bobs native.

Correctif B7-m2 source-only en cours de Gate A :
[rapport de defaut et diagnostic](../../docs/M19_B7M2_CLOSE_RESET_GATE_A_2026-11-18.md).
Tant qu'aucune bascule de Lib n'est autorisee, ne pas interpreter un
nouvel essai sous B7-m1 comme une validation du correctif.
