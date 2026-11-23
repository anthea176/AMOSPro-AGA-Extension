# S1-P1b — Sonde AMOS DATA Save / Load pour la banque AGSP

## Verdict du 23/11/2026 : Runtime B PASS, Compiler C non requis

Le journal original [`M19_S1P1B_AGSP_RUNTIME_2026-11-23.TXT`](evidence/M19_S1P1B_AGSP_RUNTIME_2026-11-23.TXT), **195 octets CRLF**, SHA256 `8874d8676b8639e124936688d67e9288f4320f040909a194ca9c27d2e19ea46f`, confirme **`RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `LOAD_OK 2`, `SAVE_OK 1`, `ERASE_OK 2`, `CHECK_OK 2`, `PASS_DATA_BANK_ONLY`**.

La banque réellement sauvegardée par AMOS et transmise par l'auteur, [`AGSP_S1P1B_RESAVED_2026-11-23.ABK`](evidence/AGSP_S1P1B_RESAVED_2026-11-23.ABK), est un fichier **`AmBk` de 212 octets** : son SHA256 `0e6dcaa50d32ff957c2eb5e22394f870230c7d759642cfe1bf1db2cfc28a64bb` et son Git blob `535b7ae0b7897e3d87ac634d264c967c252e3fc1` sont **identiques à la fixture d'origine**. Payload `AGSP` v1, 192 octets, banque DATA n°10, une image 16×16 à 2 plans, palette RGB24 exacte. Ce test établit la compatibilité du fichier AGSP avec le **`Load/Save` AMOS Runtime**.

**Décision explicite auteur : on saute le Compiler.** La Gate C de cette sonde est **NON TESTÉE**, elle ne sera pas redemandée et n'est pas un prérequis de S1-P1c. On passe au raccordement des trois modules MC68020 existants à la gestion transactionnelle des banques AMOS/AP20 ; un nouveau test Runtime sera nécessaire pour cette **nouvelle fonction**, sans confondre ce PASS DATA avec une capture AGA fonctionnelle. Aucune promotion de Lib, aucune preuve de l'affichage DMA.


**Date :** 22 novembre 2026 — **Mise à jour 23/11/2026 : Gate B Runtime PASS ; Gate C Compiler volontairement sautée à la demande de l'auteur, donc NON TESTÉE.**

## But

Tester le **vrai contrat AMOS Professional des banques DATA** avec un fichier binaire AGSP v1, indépendamment des futures commandes `Get AGA Sprite`. La banque a un en-tête de fichier `AmBk`, banque n°10, drapeau DATA=1, nom `AGASPRT `, puis un payload interne `AGSP` 192 octets (une image 16×16, 2 plans, 3 couleurs opaques RGB24 + transparent).

**Ce test ne valide ni une nouvelle Lib, ni un chargement d'IFF, ni une commande Sprite, ni le DMA.** C'est une vérification de compatibilité du stockage DATA `Save/Load` sous AMOS.

Fichiers :
- [Source AMOS ASCII](../tests/proto/agsp_bank/AGSP_BANK_SAVELOAD.asc) — `SOURCE_TAG M19_S1P1B_DATA_ABK_V1` ;
- [banque binaire AGSP_1IMG_16X16.ABK](../tests/proto/agsp_bank/AGSP_1IMG_16X16.ABK) — **212 octets**, SHA256 `0e6dcaa50d32ff957c2eb5e22394f870230c7d759642cfe1bf1db2cfc28a64bb`, Git blob `535b7ae0b7897e3d87ac634d264c967c252e3fc1`;
- [générateur Python déterministe](../tools/m19_s1p1b_agsp_fixture.py), relié au [codec AGSP officiel du projet](../tools/m19_s1_agsp_bank.py).

## Préparation WinUAE / AMOS

1. Utiliser **AMOS Professional sous WinUAE 68020, PAL, JIT OFF** ; la sonde DATA ne nécessite pas d'extension AGA nouvelle (conserver P2d installée si elle est déjà présente). Créer un programme vierge ; vérifier que **la banque 10 est libre**, sinon sauvegarder votre environnement et ne pas lancer cette sonde.
2. Copier le fichier **binaire** `AGSP_1IMG_16X16.ABK` dans le répertoire de travail vu par AMOS. **Ne pas le traiter comme du code ASCII**.
3. Ouvrir le programme vierge : **Project → Merge ASCII** et sélectionner `AGSP_BANK_SAVELOAD.asc`, puis exécuter le Runtime. Lire `RAM:M19_S1P1B_AGSP_RUNTIME.TXT` (ou `...INTERPRETED.TXT` si `Prg State=0`).
4. **Pas de passage au Compiler pour cette sonde** : l'auteur a explicitement demandé de le sauter. Le fichier compilé n'est ni attendu ni revendiqué.

La sonde utilise uniquement `Load`, `Save`, `Length`, `Start`, `Peek`, `Peek$`, `Deek`, `Leek`, `Erase`, `Trap` et `Prg State`, selon des usages déjà présents dans les tests du dépôt. Les instructions `Save "nom",banque` et `Load "nom",banque` correspondent au [manuel AMOS Professional sur les banques](https://amospromanual.dev/05-09-memory-banks.html).

Elle charge la banque depuis le disque puis vérifie **longueur=192**, identifiant AGSP, version, entrée, pixels planaires et valeurs RGB24. Elle enregistre `RAM:AGSP_S1P1B_RESAVED.ABK`, efface la banque et recharge ce fichier, puis revérifie les mêmes octets. En fin de test, elle efface uniquement la **banque 10 qu'elle a chargée elle-même**.

## Résultat Runtime observé

~~~text
TEST M19 S1P1B AGSP DATA BANK
SOURCE_TAG M19_S1P1B_DATA_ABK_V1
PRG_STATE  1
RUN_MODE RUNTIME
RESULT  1
ERR  0
LOAD_OK  2
SAVE_OK  1
ERASE_OK  2
CHECK_OK  2
VERDICT PASS_DATA_BANK_ONLY
~~~

En cas d'échec, fournir le journal **tel quel** et la première erreur affichée sous AMOS. Les codes : `1` banque 10 occupée ; `2` chargement ; `3` taille ; `4..11` contenu ; `12` sauvegarde ; `13` effacement. Le **PASS Runtime B est maintenant attesté** par le journal et la banque sauvegardée fournis ; le préflight CI seul ne prouvait ni B ni C. **Gate C volontairement NON TESTÉE.**

## Provenance et garanties

L'enveloppe DATA **n'est pas une banque Sprite OCS**. Aucun élément n'est affecté aux canaux matériels ; les 3 RGB24 sont des couleurs locales de l'image AGSP. Le contenu est déterministe, vérifié par `parse_abk`, `parse_payload` et sa SHA256. Le protocole n'utilise pas la caméra, la palette matérielle, le Copper ou les Bobs.

**Avant de qualifier S1-P1b comme API native fonctionnelle**, il reste à relier l'adaptateur écran, la capture MC68020 et le repack multi-images à une transaction de banque DATA AMOS : `Lst.Cree`, `Bnk.Change`, `Lst.Del` et le vrai wrapper AP20. Le cycle `Save/Load` de ce fichier seul n'est qu'une preuve d'interopérabilité DATA.
