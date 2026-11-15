# M19 — Contrat de conception des Bobs AGA multi-images

**Décision utilisateur du 15/11/2026 — contrat fonctionnel retenu, NON implémenté.**
Dépôt : `anthea176/AMOSPro-AGA-Extension`, branche `main` exclusivement.
Ce document définit la cible de développement, **pas** une API déjà disponible dans R88. Aucun token AP20, programme AMOS, binaire ni test Compiler n'est créé par cette documentation. R84 v0.13.29 `LAST_GOOD` reste protégée ; R88 v0.13.33 reste expérimentale, sans promotion automatique.

## 1. Objectif et périmètre

Retrouver l'ergonomie des Bobs AMOS classiques, mais sur l'écran AGA privé de l'extension, avec **1 à 8 bitplanes (jusqu'à 256 couleurs)**, plusieurs images numérotées dans **une seule banque ABK**, masques individuels et objets animables. **L'auteur crée ses Bobs sous AMOS** directement à partir d'un écran AGA : **aucun convertisseur PC imposé**.

**Séparation impérative :**
- **Bobs animés :** format dédié, images planaires **non compressées**, source prête pour le Blitter en **vraie Chip RAM** ; pas de RLE par frame, pas de cache Fast/RLE à piloter.
- **Grandes illustrations / images fixes :** conserver telles quelles les fonctionnalités **AGAPIC v1/v2**, RLE et lecture Fast RAM déjà existantes. **Aucune refonte AGAPIC requise.**
- Réutiliser les travaux Blitter R87/R88 uniquement après vérification de leur compatibilité avec dimensions variables, masques et allocation Chip ; ne pas confondre le cache AGPC 16x16 expérimental avec le futur moteur Bob.

## 2. Commandes utilisateur visées

| Commande proposée | Contrat fonctionnel |
| --- | --- |
| `Aga Bob Bank N` | Choisit la banque AMOS n°N ; si libre, la crée au **format Bob AGA** ; si existante, exige ce format. Prépare automatiquement ses données pour le Blitter en Chip RAM, sans effacer une autre banque. |
| `Get AGA Bob I,X1,Y1,X2,Y2` | Capture le rectangle de l'écran AGA privé dans **l'image n°I** de la banque active ; crée ou remplace cette image en conservant les autres. |
| `Make AGA Bob Mask I,C` | Construit/remplace le **masque 1 bit indépendant** de l'image I ; les pixels d'index C sont transparents. |
| `No AGA Bob Mask I` | Désactive/supprime le masque de I ; les pixels, **dont l'index 0**, restent visibles. |
| `Aga Bob N,X,Y,I` | Crée ou met à jour l'**objet Bob n°N** à (X,Y) en utilisant l'image I de la banque actuellement sélectionnée. L'objet mémorise la **banque d'origine** et la conserve après changement de banque active. |
| `Aga Bob Bank Free N` | Libère la **préparation Chip interne** de la banque N et invalide/désactive les Bobs qui en dépendent ; **ne supprime pas** la banque AMOS utilisée par `Save`/`Load`. |

**Noms et grammaire sont des cibles** : le tokeniseur AMOS Professional et AMOS Compiler V2 doivent encore valider leur enregistrement exact. Ne pas présenter les lignes ci-dessous comme du BASIC exécutable dans R88.

**Choix de syntaxe retenu :** `Get AGA Bob I,X1,Y1,X2,Y2` avec **cinq paramètres numériques, sans `To`**. Pour ce nouveau contrat, les coordonnées de coin sont **inclusives** : `0,0,31,31` = 32×32 pixels. Tester pixel par pixel les cas 1×1, bords et largeurs non multiples de 16 ; ne pas transposer la convention de `Screen Copy`.

**Identifiants distincts :** N° de banque AMOS ≠ n° d'image dans cette banque (1-based) ≠ n° d'objet Bob (indépendant). Une image peut alimenter plusieurs Bobs sans duplication de ses pixels en Chip. Pour un Bob déjà existant, `Aga Bob` met à jour position/image et éventuellement sa banque source selon la banque sélectionnée lors de l'appel ; il **ne recrée pas** une copie graphique.

## 3. Exemple de création et sauvegarde

```text
Aga Bob Bank 10

Get AGA Bob 1,0,0,31,31
Get AGA Bob 2,32,0,63,31
Get AGA Bob 3,64,0,95,31

Make AGA Bob Mask 1,0
Make AGA Bob Mask 2,0
No AGA Bob Mask 3

Save "HERO.ABK",10
```

La capture doit venir de l'**écran AGA privé** (pas `Screen Open` OCS). L'origine exacte visible/inactive sous double buffering reste à verrouiller par test ; le chemin `Aga Bank Image Capture` actuel utilise le back buffer inactif mais n'est pas directement une capture multi-images. Les données de la banque sauvegardée doivent pouvoir être rechargées par le `Load` standard AMOS (enveloppe ABK/DATA correcte).

Le masque n'impose **jamais** « couleur 0 toujours transparente ». `Make AGA Bob Mask I,0` rend l'index 0 transparent **pour cette image seulement** ; `No AGA Bob Mask I` permet un index 0 opaque. Une image sans masque est opaque par défaut. Les pixels couleur et les bits de masque sont stockés séparément.

## 4. Exemple de chargement et utilisation multi-banques

```text
Load "HERO.ABK",10
Load "ENEMIES.ABK",11

Aga Bob Bank 10
Aga Bob 1,100,80,1

Aga Bob Bank 11
Aga Bob 2,200,80,3

Aga Bob Bank Free 10
```

- Les numéros **10 et 11 sont de vrais numéros de banques AMOS**, choisis par l'auteur, pas une plage secrète ou la banque native OCS n°1.
- L'objet Bob 1 demeure associé à la banque 10 ; Bob 2 à la banque 11. La sélection de la banque 11 ne « rebinde » pas Bob 1.
- `Save "HERO.ABK",10` et `Load "HERO.ABK",10` sont les commandes **AMOS natives**, pas de nouvelle commande AGA de fichier.
- La banque n°10 peut avoir été chargée en Fast par `Load` : **`Aga Bob Bank 10` déclenche sa préparation Chip**. Ne pas promettre qu'un `Load` AMOS non intercepté alloue de lui-même de la Chip.

## 5. Contrat mémoire, ownership et sécurité

1. **Banque AMOS officielle** : le fichier ABK multi-images porte le contenu planar non compressé, métadonnées, index des images et masques. Elle appartient à AMOS et reste sauvegardable/rechargeable. Elle peut résider en Fast **ou** en Chip.
2. **Représentation DMA** : lors de `Aga Bob Bank N`, si les pixels/masques de la banque AMOS sont déjà en **Chip valide, stable et correctement alignée**, le moteur peut les utiliser directement **uniquement si leur durée de vie est sécurisée** ; sinon, il alloue une **copie privée en Chip** et y prépare les données une fois, **hors boucle d'animation**.
3. **Vérification réelle** : avant tout accès DMA/Blitter, vérifier la **plage complète** de données source et masque avec `TypeOfMem` / `MEMF_CHIP` (ou contrat OS équivalent validé), pas seulement les flags de l'ABK. Refuser un pointeur Fast pour le Blitter.
4. **Une association interne par banque AMOS** : registre interne n°N → identité/validité du contenu AMOS, images, pointeurs Chip, taille/allocation. **Aucune seconde banque AMOS numérotée** imposée au programmeur. Plusieurs objets référencent la même représentation sans copies par Bob.
5. **Création/capture** : `Aga Bob Bank N` prépare ou initialise une banque vide sans écraser une banque occupée d'un autre format ; `Get AGA Bob` ajoute/remplace l'image I, met à jour le répertoire interne et les données Chip correspondantes, sans perdre les autres images. Le contenu officiel sauvegardé doit rester synchronisé avec les modifications.
6. **Libération** : `Aga Bob Bank Free N` invalide les références des objets liés avant libération de la mémoire Chip privée (après fin du DMA concerné). La banque AMOS reste intacte. Un nouvel `Aga Bob Bank N` re-prépare la même banque si elle existe.
7. **`Erase` / re`Load` / remplacement** : le code **ne doit jamais dessiner depuis un pointeur périmé** ; valider l'identité/la taille/le format de la banque au point d'entrée et sécuriser les Bobs dépendants. Les commandes natives AMOS n'étant pas interceptées par défaut, **après remplacement d'une banque dans un programme**, l'usage contractuel passe par `Aga Bob Bank N` pour réassocier/préparer. Détection complète d'une mutation in-place par `Poke` **non garantie** ; ne pas autoriser cette pratique dans le contrat initial.
8. **Erreur mémoire/format** : aucun demi-état actif ni écriture partielle dans les buffers affichés ; échec contrôlé, diagnostic exploitable, nettoyage de l'allocation transitoire, pas de recours obligatoire à AMCAF.
9. **Profondeur/masque** : 1..8 bitplanes, tailles variables, stride planar word-aligné pour DMA, masques indépendants et clipping pixel exact. Une palette commune compatible avec l'écran AGA actif est exigée à ce stade ; **pas de changement automatique de palette par Bob**.

**Pas de `Bank To Chip`, `WLOAD` ou `Reserve As Chip Data` à écrire par l'utilisateur.** Les commandes AMCAF peuvent rester des outils externes facultatifs, **pas des dépendances** de l'API Bob. Aucun format RLE pour ces Bobs animés ; AGAPIC continue à servir les illustrations fixes.

## 6. Cadence, affichage, animation et nettoyage

- La sélection/création de banque et la préparation Chip sont **hors boucle de rendu**. Pas de recopie complète ou de décompression à chaque frame.
- `Aga Bob N,X,Y,I` agit sur un objet persistant ; le coût de changement d'image/position ne doit pas dupliquer les données source. Un même sprite peut être utilisé par plusieurs Bobs simultanément.
- Dessiner dans le **back buffer AGA prévu**, en respectant `Safe` et l'ordre de `Aga Swap` ; la sémantique de `Aga Bob Update` / `Aga Bob Clear` / `Aga Bob Draw`, la restauration du fond et les priorités doivent être testées ; **aucun swap implicite** ; AMAL est réservé à P2.
- En cas de banque effacée, remplacée ou libérée, les Bobs rattachés ne doivent pas continuer à lire une source désallouée.

## 7. Vérifications bloquantes avant développement natif / promotion

| Contrôle | Exigence |
| --- | --- |
| Syntaxe AMOS/AP20/Compiler | Vérifier les six commandes de base, puis les noms P0 ajoutés (`Aga Bob Off`, `Aga Bob Update`, `Aga Bob Clear`, `Aga Bob Draw`) et leurs arguments ; `Get AGA Bob` conserve cinq paramètres sans `To`. |
| Banque ABK | Créer plusieurs images, tailles/positions variables, sauvegarder, `Erase`, `Load`, resélectionner ; garantir que toutes les images et masques reviennent identiques. |
| Mémoire | `Load` en Fast réel, préparation Chip unique, contrôle `MEMF_CHIP`, 0 duplication par Bob, libération et re-préparation ; Chip insuffisante : échec propre. |
| Pixels | Tests 1×1, 17/31/32/37 pixels, positions X non alignées, quatre bords, 1/4/8 plans, index 0 opaque, masque index non nul, pixels masqués. |
| Objets | Deux banques indépendantes, plusieurs Bobs partageant une image, changement de banque active, changement frame/position, suppression/libération. |
| Double buffer | Contrôle fond, redraw, swap, transparence et performances **frame complète**, comparaison avec moteur existant. |
| Sécurité | Banque absente, mauvais format, ID inexistant, `Erase`/`Load` sur même n°, pointeur périmé, allocations partielles, fermeture AGA sans Guru. |
| Tests réels | **Gate A** préflight/native, **Gate B** AMOS interprété WinUAE, **Gate C** AMOS Compiler, **Gate D** Amiga physique si disponible, **séparées**. |

Garder **un seul test ASC actif** dans `tests/current/`. Ne pas retoucher les tests passés. **Aucun résultat Gate A/B/C n'est revendiqué pour ces nouvelles commandes** tant que leurs programmes et binaires exacts n'ont pas été exécutés.

## 8. Feuille de route fonctionnelle P0 / P1 / P2 — comparaison au manuel AMOS

**Périmètre de cette feuille de route : conception, NON implémentation.** Les commandes ci-dessous sous préfixe `Aga` ou `Get AGA` sont des **noms d'API envisagés**, jamais des tokens AMOS validés ni des fonctionnalités R88. La sélection et la préparation Chip de `Aga Bob Bank N`, le format ABK non compressé et la sauvegarde/lecture native restent les décisions de base des sections 1 à 7.

**Sources AMOS consultées** : [7.02 Blitter Objects](https://amospromanual.dev/07-02-blitter-objects.html), [7.03 Updating Objects](https://amospromanual.dev/07-03-updating-objects.html), [7.04 Detecting Collisions](https://amospromanual.dev/07-04-detecting-collisions.html), [7.01 Hot Spot](https://amospromanual.dev/07-01-hardware-sprites.html). Les noms sans « AGA » ci-dessous sont des **commandes natives AMOS** ; les équivalents AGA sont de nouvelles propositions et doivent être audités côté AP20 et Compiler.

### P0 — Bobs réellement utilisables sur écran AGA

Objectif : plusieurs images 256 couleurs dans une banque ABK, masques et Bobs persistants, préparation Chip autonome, animation BASIC pilotée par `Aga Swap` **sans double swap**.

| Fonction native AMOS de référence | Équivalent AGA à développer / comportement visé |
| --- | --- |
| `GET BOB`, banque Object, `LOAD`/`SAVE` | **Déjà retenu** : `Aga Bob Bank N`, `Get AGA Bob I,X1,Y1,X2,Y2` (5 paramètres, bornes inclusives), `Save` et `Load` natifs ; banque ABK AGA multi-images, pas Object OCS. |
| `MAKE MASK` / `NO MASK` | **Déjà retenu** : `Make AGA Bob Mask I,C` (index transparent explicite, masque 1 bit) / `No AGA Bob Mask I` (image opaque). |
| `BOB` | **Déjà retenu** : `Aga Bob N,X,Y,I` crée ou met à jour l'**état** d'un Bob (banque source mémorisée ; plusieurs objets partagent la même image). |
| `BOB OFF` | **À ajouter au contrat P0** : `Aga Bob Off N` et, si nécessaire, une forme « tous » ; désactivation de l'objet et de son rendu sans libérer la banque source. Définir si l'objet reste réactivable et l'état des animations futures. |
| `BOB UPDATE` | **À ajouter au contrat P0** : `Aga Bob Update` pour traiter tous les Bobs actifs **sans faire de `Aga Swap` implicite**. Ne pas copier la sémantique OCS, car `BOB UPDATE` natif bascule lui-même les buffers. |
| `BOB CLEAR` / `BOB DRAW` | **À ajouter au contrat P0** : `Aga Bob Clear` / `Aga Bob Draw` (noms provisoires) pour restauration du fond et rendu des Bobs sur le **back buffer AGA de l'extension**. Tester le comportement sur deux buffers, fond statique et décor changeant. Pas de double restauration ou de swap caché. |

**Ordre de développement P0 :**
1. **P0a — Banque** : confirmer les tokens AP20/Compiler ; format multi-images planaire sans RLE, création/capture, indexation, remplacement d'une image, `Save`/`Erase`/`Load` et identification exacte de banque. **Aucune banque AMOS supplémentaire pour la Chip**.
2. **P0b — Masque + Chip** : index transparent paramétrable, index 0 éventuellement opaque, capture 1/4/8 bitplanes et largeurs non alignées ; `Aga Bob Bank N` prépare en Chip une fois par version de banque. Vérifier `MEMF_CHIP` sur les plages source/masque avant DMA, refus propre en mémoire insuffisante ; libération via `Aga Bob Bank Free N`.
3. **P0c — Objets** : `Aga Bob` persistant, position/image/banque liées à l'objet, `Aga Bob Off`, plusieurs instances d'une même image sans duplication des données graphiques, ordre stable initial par identifiant Bob.
4. **P0d — Frame complète** : `Aga Bob Clear` / `Aga Bob Draw` et/ou `Aga Bob Update`, correction du fond, clipping, `Safe`, dessin dans le buffer inactif et **un unique `Aga Swap` explicite côté utilisateur**. Mesurer toute la frame (fond + Bobs + Swap, attente VBL comptée séparément), pas seulement le dessin.
5. **Validation** : test ASC minimal lisible, préflight, Gate A native, puis WinUAE AMOS interprété (B), puis vrai AMOS Compiler (C) ; aucun statut PASS transmis entre Gates. Tester les banques effacées/rechargées et `Aga Screen Open/Close`/ABI.

**À verrouiller en P0 avant de publier une API :** `Aga Bob Update` et `Aga Bob Draw` pourraient se recouvrir ; décider précisément si `Update` invoque `Clear + Draw`, et si `Clear` restaure effectivement le fond ou si le programme reconstruit intégralement chaque frame. **Aucun `Aga Swap` implicite.** Les noms `Aga Bob Draw` / `Aga Bob Clear` ci-dessus désignent le traitement de tous les objets, **pas** l'ancien exemple provisoire `Aga Bob Draw(Bank,Image,X,Y,Mode)`.

### P1 — Ergonomie et fonctions de jeu

| Fonction AMOS | Adaptation AGA envisagée |
| --- | --- |
| `X BOB`, `Y BOB`, `I BOB` | Fonctions de lecture AGA (noms exacts non décidés) : coordonnées et frame du Bob, erreurs propres pour un objet inexistant. |
| `HOT SPOT` | Point d'ancrage **par image** dans la banque AGA ; effet sur position, clipping, tri par Y et futurs retournements ; conserver dans l'ABK. |
| `PRIORITY ON/OFF`, `PRIORITY REVERSE ON/OFF` | Ordre de rendu par numéro ou coordonnée Y, normal/inversé ; profondeur Z ou tri spécifique seulement si contrat explicite. Tester Bobs qui se croisent. |
| `PASTE BOB` | Dessin **immédiat d'une image de la banque sélectionnée**, sans objet persistant, dans le back buffer AGA. Distinct de `Aga Bob` et de l'étape de mise à jour. |
| `LIMIT BOB` | Zone visible/clipping configurable pour un objet ou l'ensemble ; **précision au pixel AGA**, ne pas importer la limitation OCS d'arrondi X à 16 pixels. |
| `DEL BOB`, `INS BOB` | Édition des images de la banque : suppression/insertion, indexation et références d'objets cohérentes. Le manuel OCS renumérote les images suivantes ; **choisir et tester explicitement** si AGA réindexe ou conserve des identifiants stables avant ajout de la commande. |
| `GET BOB PALETTE` | **Pas de commande nouvelle imposée** : la banque AGA emploie la palette active et les commandes de palettes AGA déjà existantes ; contrôler la compatibilité des indices/ModeID. |

La priorité P1 **n'autorise pas** une modification silencieuse du format ABK P0 : prévoir dès P0 champs de hotspot et métadonnées extensibles, réservés/ignorés avant implémentation.

### P2 — Fonctions avancées / compatibilité progressive

| Fonction AMOS | Adaptation AGA envisagée |
| --- | --- |
| `BOB COL`, `COL` | Collisions Bob–Bob (d'abord rectangles, puis **masques bit à bit** pour l'exactitude pixel), interrogation des Bobs touchés. N'inventer aucune compatibilité avec les sprites matériels OCS sans moteur dédié. |
| `HREV`, `VREV`, `REV` | Retournements sans modifier définitivement les images partagées ; gestion de hotspot/masque, test de deux objets affichant la même image dans des sens différents. Éviter l'ancien coût de retournement mutable signalé par le manuel. |
| `SET BOB` | Modes avancés de restauration de fond, sélection des plans et mode Blitter/masque ; **ne pas recopier directement** les valeurs OCS dans les chemins AGA 8 plans. |
| `AMAL` | Intégration future aux objets AGA uniquement après vérification des canaux, hooks et ABI AMOS/Compiler ; **aucune compatibilité AMAL revendiquée** à P0/P1. |
| `BOB UPDATE ON/OFF`, `UPDATE` général | Gestion d'une mise à jour automatique seulement si elle respecte le rendu AGA privé. Ne pas mêler le système Sprite OCS natif et le gestionnaire Bob AGA sans contrat spécifique. |

**Hors périmètre de la première réalisation** : `PUT BOB` (le manuel recommande `PASTE BOB` et précise que `PUT BOB` est adapté au simple buffer), simulation d'`AUTOBACK` OCS, commandes de collisions Sprite/BOB natives et synchronisation implicite des écrans AMOS. Elles ne sont pas des prérequis pour les Bobs AGA.

### Structure interne anticipée dès P0

Un **objet Bob** doit pouvoir retenir au minimum : ID, banque AMOS d'origine, ID image, X/Y, visibilité, état actif, hotspot effectif, ordre Z initial et état du rendu par buffer. Une **banque AGA** retient son répertoire d'images, largeur/hauteur/profondeur, pixels planaires, masque, hotspot/métadonnées futures, validité/génération et allocation Chip privée. Un changement de banque active n'altère pas les Bobs déjà créés.

**Barrières anti-régression :** ne pas réécrire AGAPIC/RLE pour les illustrations fixes, ne pas lier cette API à AMCAF, ne pas produire de nouvelles commandes sans preuve token/AP20, ne pas confondre `BOB UPDATE`/`SCREEN SWAP` OCS avec `Aga Bob Update`/`Aga Swap` AGA, ne pas toucher à R84 `LAST_GOOD`, et ne pas annoncer de Gate B/C sans exécution.

## 9. État actuel du projet et références

- R84 v0.13.29 `dist/AMOSPro_AGA_LAST_GOOD.Lib` : figée ; **aucune promotion automatique**.
- R88 v0.13.33 : candidate expérimentale, `Aga Cache Blit` limité à 16×16×8 et exigeant de la Chip réelle. **Ce n'est pas le moteur Bob multi-images demandé**. Le diagnostic P2.8 a montré qu'un ABK peut être chargé en Fast malgré des flags demandant Chip.
- L'extension sait déjà gérer AGAPIC v1/v2 par banque pour les illustrations ; le nouveau format Bob est **distinct** et ne doit pas casser son API.

Références : [README API](../README.fr.md), [AGAPIC](M16_AGAPIC_FORMAT_DESIGN.md), [contrat objets P2](M19_P2_OBJECT_MANAGER_CONTRACT.md), [cache M18](M18_FAST_ICON_CACHE.md), [incident Chip R88](M19_P28_R88_CHIP_BANK_DIAGNOSTIC_2026-11-15.md), [exemple AMOS OCS effectiveBobs](https://github.com/alain-treesong/amiga_coding_in_amos/tree/main/snippet-014_effectiveBobs).

**À développer :** format binaire ABK multi-images (enveloppe + répertoire), API/AP20, capture, masque, gestionnaire de Bobs, préparation Chip, sauvegarde/lecture, tests et benchmarks. **Documentation seule à ce stade.**

## 10. Chantier séparé — Sprites matériels AGA

Le moteur Bob logiciel décrit ici n'est **pas** un moteur de Sprites DMA. L'auteur demande de traiter également les **Sprites matériels AGA**. Le plan détaillé est consigné séparément dans [Sprites AGA — S0/S1/S2/S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md) : audit Intuition/Chip/DMA/Copper, premier Sprite 16 px, paires attachées/largeur 32–64 px, puis multiplexage et collisions. Les 8 canaux matériels AGA, les « computed Sprites » AMOS et les objets Bob AGA ne sont **pas interchangeables**. Ne pas étendre implicitement l'API Bob ni changer sa priorité P0.
