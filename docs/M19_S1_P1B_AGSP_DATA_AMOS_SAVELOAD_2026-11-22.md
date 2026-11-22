# S1-P1b — Sonde AMOS DATA Save / Load pour la banque AGSP

**Date :** 22 novembre 2026 — **Statut : sonde préparée et préflight statique en CI ; WinUAE Runtime / Compiler à tester par l'auteur.**

## But

Tester le **vrai contrat AMOS Professional des banques DATA** avec un fichier binaire AGSP v1, indépendamment des futures commandes `Get AGA Sprite`. La banque a un en-tête de fichier `AmBk`, banque n°10, drapeau DATA=1, nom `AGASPRT `, puis un payload interne `AGSP` 192 octets (une image 16×16, 2 plans, 3 couleurs opaques RGB24 + transparent).

**Ce test ne valide ni une nouvelle Lib, ni un chargement d'IFF, ni une commande Sprite, ni le DMA.** C'est une vérification de compatibilité du stockage DATA `Save/Load` sous AMOS.

Fichiers :
- [Source AMOS ASCII](../tests/design/agsp_s1/AGSP_DATA_BANK_SAVELOAD.asc) — `SOURCE_TAG M19_S1P1B_DATA_ABK_V1` ;
- [banque binaire AGSP_1IMG_16X16.ABK](../tests/design/agsp_s1/AGSP_1IMG_16X16.ABK) — **212 octets**, SHA256 `0e6dcaa50d32ff957c2eb5e22394f870230c7d759642cfe1bf1db2cfc28a64bb`, Git blob `535b7ae0b7897e3d87ac634d264c967c252e3fc1`;
- [générateur Python déterministe](../tools/m19_s1p1b_agsp_fixture.py), relié au [codec AGSP officiel du projet](../tools/m19_s1_agsp_bank.py).

## Préparation WinUAE / AMOS

1. Utiliser **AMOS Professional sous WinUAE 68020, PAL, JIT OFF** ; la sonde DATA ne nécessite pas d'extension AGA nouvelle (conserver P2d installée si elle est déjà présente). Créer un programme vierge ; vérifier que **la banque 10 est libre**, sinon sauvegarder votre environnement et ne pas lancer cette sonde.
2. Copier le fichier **binaire** `AGSP_1IMG_16X16.ABK` dans le répertoire de travail vu par AMOS. **Ne pas le traiter comme du code ASCII**.
3. Ouvrir le programme vierge : **Project → Merge ASCII** et sélectionner `AGSP_DATA_BANK_SAVELOAD.asc`, puis exécuter le Runtime. Lire `RAM:M19_S1P1B_AGSP_RUNTIME.TXT` (ou `...INTERPRETED.TXT` si `Prg State=0`).
4. Compiler **le même ASC** avec le véritable AMOS Compiler ; exécuter séparément, puis récupérer `RAM:M19_S1P1B_AGSP_COMPILED.TXT`. Préciser version de Compiler, CPU/JIT et empreinte de la Lib installée si elle intervient dans votre session.

La sonde utilise uniquement `Load`, `Save`, `Length`, `Start`, `Peek`, `Peek$`, `Deek`, `Leek`, `Erase`, `Trap` et `Prg State`, selon des usages déjà présents dans les tests du dépôt. Les instructions `Save "nom",banque` et `Load "nom",banque` correspondent au [manuel AMOS Professional sur les banques](https://amospromanual.dev/05-09-memory-banks.html).

Elle charge la banque depuis le disque puis vérifie **longueur=192**, identifiant AGSP, version, entrée, pixels planaires et valeurs RGB24. Elle enregistre `RAM:AGSP_S1P1B_RESAVED.ABK`, efface la banque et recharge ce fichier, puis revérifie les mêmes octets. En fin de test, elle efface uniquement la **banque 10 qu'elle a chargée elle-même**.

## Résultat attendu dans chacun des deux modes

~~~text
TEST M19 S1P1B AGSP DATA BANK
SOURCE_TAG M19_S1P1B_DATA_ABK_V1
PRG_STATE  1                     (Runtime ; -1 pour Compiler)
RUN_MODE RUNTIME                  (COMPILED pour Compiler)
RESULT  1
ERR  0
LOAD_OK  2
SAVE_OK  1
ERASE_OK  2
CHECK_OK  2
VERDICT PASS_DATA_BANK_ONLY
~~~

En cas d'échec, fournir le journal **tel quel** et la première erreur affichée sous AMOS. Les codes : `1` banque 10 occupée ; `2` chargement ; `3` taille ; `4..11` contenu ; `12` sauvegarde ; `13` effacement. Une CI de syntaxe et de génération de fixture **n'équivaut pas à Gate B ou C**.

## Provenance et garanties

L'enveloppe DATA **n'est pas une banque Sprite OCS**. Aucun élément n'est affecté aux canaux matériels ; les 3 RGB24 sont des couleurs locales de l'image AGSP. Le contenu est déterministe, vérifié par `parse_abk`, `parse_payload` et sa SHA256. Le protocole n'utilise pas la caméra, la palette matérielle, le Copper ou les Bobs.

**Avant de qualifier S1-P1b comme API native fonctionnelle**, il reste à relier l'adaptateur écran, la capture MC68020 et le repack multi-images à une transaction de banque DATA AMOS : `Lst.Cree`, `Bnk.Change`, `Lst.Del` et le vrai wrapper AP20. Le cycle `Save/Load` de ce fichier seul n'est qu'une preuve d'interopérabilité DATA.
