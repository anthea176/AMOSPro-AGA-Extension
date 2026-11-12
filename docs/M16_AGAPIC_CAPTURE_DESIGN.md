# M16 — Capture AGAPIC et ergonomie des banques (contrat en discussion)

**12/11/2026. Statut : conception validée et développement commencé par le modèle hôte ; aucun nouveau token AP20 ni commande 68000 livrés.** M16 reste en développement. Référence figée : R46 v0.12.1-C1 `LAST_GOOD` Compiler-safe, sans changement de binaire tant que les contrats ne sont pas approuvés. Branche `main` uniquement.

## Décisions déjà validées

- La future capture lit **uniquement le back buffer AGA privé**. Aucun `Swap`, changement de palette ou attente VBL implicite.
- **Refus intégral de toute capture hors écran — décision utilisateur validée.** Le rectangle demandé doit être entièrement compris dans la zone logique du back buffer : `X >= 0`, `Y >= 0`, `Width > 0`, `Height > 0`, `Width <= ScreenWidth`, `Height <= ScreenHeight`, `X <= ScreenWidth-Width`, `Y <= ScreenHeight-Height`. Vérifier les valeurs complètes et les débordements arithmétiques avant toute opération, sans troncature 16 bits. **Aucun clipping de capture** : si une condition échoue, retourner `0`, **ne créer aucune banque**, ne modifier ni banque existante ni pixels/palette/back buffer. Les erreurs d'écran absent/invalide ou de coordonnées sont des refus, jamais une capture partielle.
- **Transparence par index validée :** `TransparentIndex=-1` crée une image entièrement opaque **sans masque** ; `TransparentIndex=0..(2^Depth-1)` crée un **masque 1 bit distinct des plans couleur**, avec bit `0` pour les pixels dont la couleur est égale à l'index choisi (transparents), bit `1` pour tous les autres (visibles). La profondeur `Depth` est celle du back buffer AGA (1 à 8 plans) ; les valeurs hors plage, notamment `<-1` ou `>=2^Depth`, sont rejetées (`0`, aucune banque créée). L'index couleur `0` reste visible si l'index transparent n'est pas `0`. Palette et pixels du back buffer restent inchangés ; aucune transparence alpha partielle.
- **Une commande de notre extension qui crée une banque doit refuser tout numéro déjà occupé**, sans distinction de type de banque, sans écrasement implicite et sans effacer de contenu existant. Retour d'échec proposé : `0`. Une éventuelle nouvelle allocation incomplète sera nettoyée sans toucher aux banques déjà présentes. La routine AMOS `Bnk.Reserve` remplace normalement une banque occupée : ne pas l'appeler tant qu'une collision est possible.
- Cette politique de protection s'appliquera également à **toute future création de banques de fontes dans notre extension**. Elle ne change pas le comportement de `Make Bank Font` de l'extension **AMCAF**, qui est un composant tiers.

## Signatures proposées — pas encore validées

```amos
_OK=Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)
_OK=Aga Image Draw(Bank,X,Y,Mode)
_OK=Aga Font Bank Select(Bank)
```

- **Capture :** créer une banque DATA AMOS au format AGAPIC v1, normalement allocable en Fast RAM, depuis un rectangle du back buffer. Compression RLE et masque 1 bit indépendant. Dernier paramètre **validé** : `-1` pour opaque (sans masque), sinon index de couleur à traiter comme transparent, borné par la profondeur AGA ; le masque 1 bit séparé préserve les couleurs d'origine. **Bords validés : rectangle strictement contenu dans l'écran, aucun clipping, échec `0` sans banque créée.** Les limites mémoire restent à valider. L'emplacement effectif en Fast RAM n'est pas prouvé par les flags seuls.
- **Draw :** consulter la banque vivante par **numéro**, puis vérifier son type, son nom, son adresse, sa longueur et son en-tête AGAPIC avant décodage. Actuellement la commande exige `Start(Bank),Length(Bank)` ; la nouvelle signature est une **proposition** et la compatibilité avec le token existant devra être explicitement décidée.
- **Font Select :** même simplification proposée pour la sélection d'une banque AMCAF `BankFont` déjà existante : le nouvel argument serait `Bank` au lieu de `Start(Bank),Length(Bank)`. **Sélection ≠ création**. Ne pas modifier l'extension AMCAF.

## Étape de développement engagée — modèle de capture (HOST ONLY)

La capture est maintenant représentée par [`tools/m16_agapic_capture_model.py`](../tools/m16_agapic_capture_model.py) et contrôlée par [`tools/test_m16_agapic_capture_model.py`](../tools/test_m16_agapic_capture_model.py), exécuté dans la CI M16. Le modèle :

- extrait des pixels indexés des **1 à 8 bitplanes planaires** avec `BytesPerRow` aligné sur les WORDs, y compris X non aligné ; réutilise **le vrai codec AGAPIC v1** `pack_image` plutôt qu'un autre format ;
- encode `TransparentIndex=-1` sans masque, ou produit un masque 1 bit indépendant avec bit 0 pour l'index transparent ;
- refuse dimensions invalides, rectangle hors écran, index impossible, mémoire bitmap incohérente et collision avec **toute banque** avant insertion de la moindre nouvelle banque ;
- simule une **préférence Fast RAM et un repli Chip RAM** avec capacités factices, sans conclure sur le placement Amiga ni sur les frais réels de l'allocateur AMOS ; produit une enveloppe ABK conforme pour contrôler le round-trip.

**Périmètre strict :** ces tests ne font exécuter **aucune instruction 68000**, n'appellent **pas** `Bnk.Reserve`, ne mesurent aucune vitesse sur Amiga, et ne prouvent ni l'emplacement physique de l'allocation ni le fonctionnement du Compiler. **La R46 C1 officielle n'est pas modifiée ; M16 non clôturé.** Prochaine étape : inspecter et valider l'ABI banque/AMOS Compiler, développer la routine native et ses tests Gate A CPU avant tout essai WinUAE.

## R47 — moteur RLE 68000 expérimental (sans banque AMOS)

[`tools/m16_capture_r47_core_emit.py`](../tools/m16_capture_r47_core_emit.py) génère un véritable cœur CPU 68000 pour capturer **une ligne** de 1 à 8 plans et produire des paquets RLE AGAPIC v1. Il code un masque 1 bit indépendant (index -1 opaque, sinon couleur transparent), les 16-pixel groups et la répétition RLE ; toutes les lectures viennent des bitplanes, sans Blitter ni modification de la source. La fonction prend une zone mémoire de sortie bornée et renvoie sa longueur ou 0 sur refus. Elle émet des paquets littéraux unitaires, valides mais moins compacts que l'encodeur hôte sur certaines images.

[`tools/test_m16_capture_r47_core.py`](../tools/test_m16_capture_r47_core.py) utilise Capstone et **Unicorn M68K** pour vérifier le code machine réel, les sorties RLE via le décodeur AGAPIC existant, la transparence, les bords, la sauvegarde des registres, l'absence d'écriture dans les bitplanes et le refus d'un tampon insuffisant. **En attente du verdict CPU/CI.**

**Il ne crée pas encore de banque AMOS** : la future commande doit assembler l'en-tête et la table des lignes, puis appeler l'allocateur AMOS sans écraser un numéro existant, via une liaison relogeable compatible Compiler. Aucune bibliothèque `.Lib`, aucun token AP20 ni exemple validé n'est modifié ; R46 C1 `LAST_GOOD` reste immuable. La qualification sous WinUAE ne peut commencer qu'après raccordement de l'allocateur.

## Obligation : mettre les exemples à jour avec les commandes livrées

L'utilisateur a expressément demandé de **ne pas oublier les exemples** lors du changement de syntaxe. Inventaire initial des sources touchées :

| Élément | Ancienne utilisation observée | Action une fois l'API validée et testée |
|---|---|---|
| `examples/font_bank_r38.asc` | Deux appels `Aga Font Bank Select(Start(25),Length(25))` | Garder l'exemple R38 validé comme référence ; créer un exemple courant avec l'appel simplifié et ses contrôles d'erreur |
| `examples/compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc` | `Aga Image Draw(_BASE,_LEN,...)`, `Aga Font Bank Select(Start(25),Length(25))` | Conserver la recette R46 C1 historique et créer un **nouveau** test tout-en-un adapté à la nouvelle bibliothèque, interprété et compilé |
| `examples/COMPILER_R46_ALL_IN_ONE.zip` | Archive de distribution du test R46 C1 | Conserver intact le ZIP versionné et construire un **nouveau ZIP** cohérent avec le nouvel ASC, les ABK, la documentation et le binaire cible |
| `examples/README.md`, `examples/README.fr.md` et `examples/compiler_r46_all_in_one/README.md` | Décrivent les anciennes signatures et le bundle | Documenter les exemples courants avec la nouvelle API tout en identifiant les anciens comme historiques |
| `README.md`, `README.fr.md`, `INSTALL.md`, `INSTALL.fr.md` | Documentation utilisateur | Mettre en cohérence signatures, exemples d'utilisation et version installable au moment de la promotion |
| `tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc`, `tests/passed/M16_R46_IMAGE_DRAW_01.asc`, `tests/passed/M14_R38_FONT_BANK_01.asc` | Recettes ayant effectivement passé WinUAE | **Ne rien modifier** ; créer des tests de nouvelle version dans `tests/current/`, puis archiver après PASS |

**Attention aux tests négatifs :** les contrôles historiques sur `Length(Bank)-1` ou pointeur nul ne correspondent plus à la nouvelle API par numéro. Les remplacer dans les **nouveaux** tests par des banques inexistantes, numéros invalides, mauvaises banques et conflits de numéro à la création. Ne pas affirmer que les anciens tests prouvent le bon fonctionnement des nouvelles signatures.

## Décisions restant ouvertes avant le moindre code

1. Valider définitivement les trois signatures et décider si l'ancienne signature de `Aga Image Draw` et celle de `Aga Font Bank Select` restent proposées en parallèle ou sont remplacées, en tenant compte de l'ABI AMOS Compiler.
2. Capture : **refus des rectangles partiellement ou totalement hors écran déjà décidé**, à tester y compris X/Y négatifs, dimensions nulles et overflow ; transparence par index et masque indépendant validés ; restent à définir les limites de dimensions et taille compressée maximale, ainsi que le repli mémoire.
3. Garantir une allocation de taille correcte, nettoyer les échecs, rejeter les banques occupées **avant** toute action destructive ; vérifier l'accès aux banques en interprété **et Compiler**.
4. Préparer tests CPU / WinUAE interprété / exécutable compilé, exemple de capture→dessin→`Save`→`Load`→dessin, et nouveau bundle cohérent. Aucun code de l'extension ni fichier `.asc` exécutable modifié avant accord explicite sur la fonction en cours.
