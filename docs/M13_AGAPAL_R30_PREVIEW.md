# M13 / R30 0.10.2 — candidate AGAPAL native (Gate A PASS, WinUAE en attente)

## R30 0.10.2 — AGAPAL Bank Init, candidate Gate A PASS / Gate B WinUAE à tester (11/11/2026)

**API :** `_OK=Aga Palette Bank Init(Start(bank),N)` (deux entiers, retour 1/0). Uniquement sur banque DATA AMOS déjà réservée, de taille exacte `16+776×N`, `N=1..256`, numéro de banque 5..65535. Écrit le nom `AGAPAL  ` et l'en-tête/index, met à zéro les 768 octets RGB24 de chaque emplacement. Réinitialiser efface les couleurs. Le contrôle `TypeOfMem` ne garantit pas que l'adresse appartient à une allocation : transmettre seulement `Start(bank)` d'une banque DATA existante.

**Candidate :** `dist/AMOSPro_AGA.Lib` = R30 **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`, identique à l'archive `dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib`. **`LAST_GOOD` reste R29 0.10.1**, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, sans modification. **Gate A : 39 scénarios 68000 PASS**, export strict PASS, [CI de staging 32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43021205300). CI du commit candidat à recontrôler. **Gate B interprété/WinUAE, C Compiler et D Amiga réel : NON TESTÉES.**

**Test actif unique :** `tests/current/M13_R30_AGAPAL_BANK_INIT_01.asc` (initialisation 8 palettes, refus, `Save`/`Erase`/`Load` ABK). Aucune capture/import de couleurs ni aucun fade/cycling ajouté ; discussion obligatoire pour toute fonction suivante.

---



**Checkpoint historique avant Gate A :** l'utilisateur a approuvé la signature `Aga Palette Bank Init(Start(10),8)`. Depuis, les 39 tests CPU et l'export strict R30 ont passé Gate A : la candidate est publiée dans `dist/`. R29 reste `LAST_GOOD` ; le prototype en commandes AMOS natives reste indépendant.

**Checkpoint de conception antérieur : prototype de format uniquement.** Les spécifications de la structure sont approuvées. Les fichiers `tools/agapal_r30_layout.py`, `tools/test_agapal_r30_layout.py` et `tests/design/R30_AGAPAL_ABK_PREVIEW_01.asc` permettent d'en tester le modèle et la compatibilité théorique avec les banques AMOS. **Aucune nouvelle instruction AP20 ni aucune bibliothèque R30 n'est produite.** R29 0.10.1 est toujours la version en `dist/AMOSPro_AGA.Lib` et `LAST_GOOD`, validée WinUAE et Personal Paint. Ne pas qualifier le modèle ABK Python de validation runtime.

## Enveloppe AMOS ABK standard — sans format propriétaire de conteneur

Une banque DATA AMOS occupe un bloc mémoire précédé d'un en-tête AMOS de 24 octets. Les champs utiles, par rapport à l'adresse `Start(bank)`, sont :

| Position | Taille | Sens |
|---|---:|---|
| `Start-24` | 4 | adresse de la prochaine banque dans la liste AMOS |
| `Start-20` | 4 | longueur de la banque + 16 |
| `Start-16` | 4 | numéro de la banque |
| `Start-12` | 2 | flags (DATA permanente / CHIP) |
| `Start-10` | 2 | réservé AMOS, ne jamais modifier |
| `Start-8` | 8 | nom de la banque : ASCII `AGAPAL  ` |
| `Start` | variable | données internes AGAPAL |

Le `Save "Fichier.abk",bank` AMOS remplace cet en-tête par 20 octets sur disque : signature `AmBk` (4), numéro WORD (2), flags WORD (2), longueur LONG contenant `taille des données + 8` (4), nom sur 8 octets ; puis les données binaires. Par conséquent, pour 8 palettes : **6 224 octets de données + 20 octets ABK = 6 244 octets sur disque**. La valeur du champ de longueur sera `6 232`. Ces détails sont décrits dans le manuel officiel [Memory Bank Structures](https://amospromanual.dev/99-appendix-e-memory-bank-structures.html).

`Reserve As Data` utilise de préférence la Fast RAM et replie en Chip RAM si nécessaire. `Save` / `Load` conservent les banques permanentes. Les banques de 1 à 4 étant utilisées par des éléments AMOS courants, prendre un numéro **≥5** (10 dans le prototype). Voir [Memory Banks](https://amospromanual.dev/05-09-memory-banks.html). L'en-tête système `Start-24` ... `Start-10` n'est **jamais modifié** par notre code : seule la zone du nom `Start-8`, prévue par AMOS à cet effet, est renommée.

## Contenu AGAPAL v1 (big-endian 68000)

| Offset relatif à `Start(bank)` | Taille | Valeur |
|---|---:|---|
| 0 | 6 | signature ASCII `AGAPAL` |
| 6 | 2 | version WORD = 1 |
| 8 | 2 | nombre d'emplacements WORD = N |
| 10 | 2 | flags WORD = 0 (réservé) |
| 12 | 4 | réservé LONG = 0 |
| 16 | 8 × N | descripteurs de palettes dans l'ordre 0 ... N-1 |
| 16+8N | 768 × N | données RGB24 (256 × R,G,B) pour chaque palette |

Un descripteur contient : offset LONG relatif au début du contenu AGAPAL, nombre de couleurs WORD (0 = emplacement vide ; 1 à 256 lorsque peuplé) et flags WORD (0 actuellement). **Chaque emplacement réserve 768 octets**, les indices commencent à **0**, les couleurs vides sont mises à zéro. L'offset de la palette `i` est `16+8N+768i`. Exemples pour N=8 : offset de palette 0 = 80, palette 7 = 5 456. Taille totale `16 + 776N`. L'encodage des offsets relatifs évite les pointeurs absolus invalidés par `Bank Swap`, `Load`, `Bank To Fast` et autres déplacements.

## Prototype AMOS à tester sous WinUAE

1. Importer [`tests/design/R30_AGAPAL_ABK_PREVIEW_01.asc`](../tests/design/R30_AGAPAL_ABK_PREVIEW_01.asc) en `Project → Merge ASCII`. **Le test écrase la banque 10 et le fichier `RAM:R30_AGAPAL_TEST.ABK`**.
2. Le script appelle uniquement les commandes **natives AMOS** : `Reserve As Data`, `Start`, `Poke$`, `Doke`, `Loke`, `Poke`, `Save`, `Erase`, `Load`, `Peek$`, `Deek`, `Leek` et `List Bank`. Il ne nécessite **aucune modification de la bibliothèque R29**.
3. Il réserve 6 224 octets, écrit le nom `AGAPAL  ` et initialise huit palettes vides. Il sauvegarde un ABK natif, efface la banque, recharge le fichier, vérifie les offsets et affiche `ABK SAVE/LOAD RESULT 1`. Vérifier `BANK 10 PALETTES 8 BYTES 6224`, `OFFSET0 80`, `OFFSET7 5456` et la ligne de `List Bank` (F si Fast RAM, C si Chip).
4. **Pas encore testé en WinUAE.** Un PASS de ce prototype attesterait la structure/ABK AMOS sous l'interpréteur, **pas l'instruction AP20 `Aga Palette Bank Init`**, encore non implémentée.

## Point bloquant pour la fonction R30 native

La signature de départ `_OK=Aga Palette Bank Init(10,8)` utilisait un **numéro de banque AMOS**. La nouvelle routine 68000 doit trouver l'adresse et la taille de la banque réservée, en respectant la liste de banques AMOS et `Bank Swap`. Dans `AMOSPro-AGA-Extension` sur `main`, la table AP20/R29 est vérifiée, **mais le point d'entrée natif stable de recherche d'une banque AMOS à partir de son numéro n'a pas encore été établi sur source**. La seule structure publique `Start-24 ... Start` ne fournit pas l'adresse du début de la liste depuis A5.

**Règle de sûreté :** ne pas inventer un offset dans A5, ne pas scanner arbitrairement la RAM, ne pas substituer silencieusement une adresse à un numéro de banque et ne pas publier une fonction qui retourne succès sans modifier la banque. Chercher une API AMOS validée de recherche de banque, ou discuter explicitement une autre signature avec l'utilisateur **avant** de produire une version AP20 R30. Aucune nouvelle branche ni aucun autre dépôt.

**Résolu pour R30 :** le pointeur `Start(bank)` évite toute recherche interne AMOS. `Aga Palette Bank Init` a passé Gate A CPU et l'export strict ; son binaire et les deux README sont publiés. **La sauvegarde/lecture ABK sous WinUAE est à valider par l'utilisateur**, puis promotion obligatoire de `LAST_GOOD` si PASS. Les fonctions d'import/capture et les fades seront discutées individuellement plus tard.

## Décision utilisateur sur l'ABI et sources R30

**Signature approuvée :** `_OK=Aga Palette Bank Init(Start(10),8)`. Le premier paramètre est l'adresse de données fournie par la fonction native `Start(bank)` ; le second est le nombre d'emplacements, actuellement limité à 1..256 pour éviter des allocations ou initialisations excessives. Le code vérifie les marqueurs d'une banque DATA native, la taille exacte `16+776N`, le numéro de banque 5..65535, et `TypeOfMem` pour le début/fin du bloc avant écriture. `TypeOfMem` **ne prouve pas la propriété de l'allocation** : passer uniquement une adresse obtenue depuis une banque existante, non libérée. Le résultat entier vaut 1 si initialisée, 0 si rejet sans modification ; ce contrôle est un contrat de Gate A à vérifier.

Sources : `tools/m13_agapal_r30_emit.py` (68000), `tools/build_m13_agapal_r30.py` (construction mémoire depuis R29), `tools/test_m13_agapal_r30.py` (Unicorn 68000). `dist/` et `LAST_GOOD` restent R29 jusqu'à Gate A validée puis Gate B utilisateur. Ce développement ne comprend pas encore capture, import/export IFF, fade ou cycling.

## Gate B : test de la candidate R30

Installer [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) R30 0.10.2 dans `APSystem`, relancer AMOS et importer [`tests/current/M13_R30_AGAPAL_BANK_INIT_01.asc`](../tests/current/M13_R30_AGAPAL_BANK_INIT_01.asc) via **Project → Merge ASCII** depuis un programme vide. **Le test remplace les banques 10/11 et `RAM:R30_AGAPAL_TEST.ABK`.** Il vérifie l'initialisation (8 palettes), offsets 80/5456, rejets 0/257 et mauvaise taille, réinitialisation, sauvegarde/chargement ABK AMOS. Attendu : `INIT 1 REINIT 1`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `REST0 80 REST7 5456 INDEX 1`, `RESULT 1`, `CLOSE RETURNED`. Le `TypeOfMem` de la fonction filtre des adresses absurdes, mais seul un vrai `Start(bank)` d'une banque réservée est admissible.
