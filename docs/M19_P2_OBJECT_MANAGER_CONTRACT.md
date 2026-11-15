# M19 P2 — Contrat proposé du gestionnaire d'objets AGA (avant toute API)

> **15/11/2026 — Contrat de conception de reference pour le prototype P2.0 BASIC ; API native NON VALIDEE.**
> L'auteur a autorisé le **prototype P2.0 en AMOS BASIC** (« ok go »). **Gate B P2.0 WinUAE Runtime 68030 : PASS** sur le banc 8 plans (voir [rapport](M19_P2_WINUAE_RUNTIME_2026-11-15.md)). **Aucune signature AP20, aucun format de banque public, aucune implémentation native n'est approuvée.** [ASC P2.0 archivé](../tests/passed/M19_P2_OBJECTS_01.asc). Étude de performance active : [4/8/16 Bobs](../tests/current/M19_P2_BENCH_BOBS_01.asc), Gate B benchmark en attente.
> Dépôt `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**. Référence : R84 v0.13.29 `LAST_GOOD` inchangée (76 commandes / 85 entrées AP20, MC68020+).

## 1. Base factuelle et limites

- **P0 :** deux canaux `AMAL ... To adresse` en `Synchro Off` / `Synchro` manuel, deux Bobs logiciels FICON8, Gate B WinUAE Runtime PASS sur le code initial (211 frames) ; l'alternance d'image à chaque frame faisait clignoter les couleurs et son retrait a corrigé le rendu visuel. [Rapport P0](M19_P0_RUNTIME_DIAGNOSTIC_2026-11-14.md).
- **P1 :** deux Bobs AGAPIC v1/v2, cadence d'images 16/24 frames, fond reconstruit, priorité changée, clipping, pixel témoin et double buffer. **Gate B Runtime/WinUAE 68030 PASS : 240 frames, 46 chevauchements, sonde 1/1, aucun échec de dessin/Swap, delta Chip/Fast nul**. [Rapport P1](M19_P1_WINUAE_RUNTIME_2026-11-15.md).
- **Non démontré par P0/P1 :** gestionnaire d'objets réutilisable, création/destruction dynamique, génération d'IDs, plusieurs écrans, AMAL Compiler, fréquence 50 FPS, 4–7 plans, sprites matériels et Amiga physique. La capture fixe WinUAE ne démontre pas la fluidité continue.
- L'écran est **privé à l'extension** (Intuition), indépendant des écrans AMOS. Les commandes natives `Bob` et `Sprite` d'AMOS n'ont pas de contrat établi pour cet écran. Les Bobs de P0/P1 sont des **images logicielles**, et non des Bobs AMOS natifs.

## 2. Choix de conception proposés

| Sujet | Proposition P2 | Raison / point de vigilance |
|---|---|---|
| Première implémentation | **Gestionnaire en AMOS BASIC**, données par tableaux/structures BASIC ; les commandes R84 exécutent le dessin | Mesurer l'utilité d'un backend natif avant de consommer le budget AP20/Compiler V2 |
| Objet | Identifiant logique + type source **AGAPIC** ou **FICON8** | Réutilise les sources existantes ; pas de nouveau format d'image |
| Position | X/Y en pixels, origine et hotspot déclarés séparément | Clipping partiel autorisé sans fausse bordure ; aucune coordonnée matérielle sprite |
| Ordre | Z entier croissant = devant ; égalité résolue par **ordre de création stable** | Un ordre déterministe rend tests et capture de pixel reproductibles |
| Visibilité | Visible/masqué indépendant de la position | La disparition d'un objet ne doit pas l'effacer directement dans le buffer affiché |
| Animation | Source de mouvement = BASIC **ou** AMAL manuel ; image courante = entrée d'une **table de frames** | L'index `A` d'AMAL ne doit pas être confondu avec un numéro de banque AGAPIC |
| Dessin | Composition sur back buffer **Safe** : décor/fond complet, Bobs triés, autres effets, puis **Swap explicite par l'application** | Aucun rendu autonome dans un timer/VBL/interrupt ; pas de mise à jour directe du front |
| Banques | Les banques d'images appartiennent **à l'application**. Le gestionnaire les référence mais ne les efface pas | Plusieurs objets peuvent partager une image ; prévenir les destructions prématurées |
| Sprites matériels | **Exclus du backend P2** ; prévus comme type conceptuel futur en P3 | Ressources DMA, palette, canaux et priorité de ViewPort différents ; un Z logiciel ne garantit pas l'ordre matériel |

**Important :** cette table définit un **contrat de travail proposé**. Elle ne fixe ni une signature AMOS, ni un nombre maximum d'objets, ni une représentation binaire/ABI, ni des identifiants persistants entre exécutions.

## 3. Fiche d'objet logique (pas une structure mémoire définitive)

| Champ | Sens | Règle envisagée |
|---|---|---|
| `ObjectId` | Référence fournie au programme | Entier positif, unique dans le contexte écran actif. Ne pas réattribuer un ID pendant ce contexte dans le prototype BASIC (évite un ancien ID dirigé vers un nouvel objet). |
| `Kind` | `AGAPIC` / `FICON8` | Valider source et profondeur avant utilisation ; type `SPRITE_HW` réservé à une étude P3 distincte. |
| `Frames[]` | Liste ordonnée de références images | AGAPIC = numéros de banques DATA (images v1/v2) ; FICON8 = couple `(banque, IconID)`. Une frame peut être partagée. |
| `FrameIndex` | Image affichée | Index logique dans `Frames[]`, séparé du canal AMAL et du numéro de banque. L'animation ne fait pas de capture ou de palette implicite. |
| `X,Y` | Position logique | Coordonnées écran en pixels ; signed pour autoriser positions négatives/partiellement visibles. Rejeter les débordements arithmétiques. |
| `HotspotX,Y` | Point d'ancrage dans la frame | Position de dessin = `(X-HotspotX, Y-HotspotY)` ; modèle local, pas d'adaptation automatique du sprite Intuition. |
| `Z`, `CreationOrder` | Priorité de composition | Tri stable ; égalités par ordre de création. Aucun effet matériel AGA de profondeur automatique. |
| `Visible`, `Mode` | Visibilité et masquage | Invisible = pas de draw ; mode 0 opaque / 1 masqué selon **le format source** et son masque réellement disponible. |
| `MotionSource` | BASIC ou AMAL | En AMAL : canal + tampon mémoire associé, mis à jour par `Synchro` **dans BASIC** ; aucun événement graphique en interruption. |
| `Alive` | Durée de vie | Créé, actif, supprimé. Une suppression retire l'objet de la composition ; un nouvel appel avec cet ID doit échouer proprement. |

### Provenance des dimensions et de la palette

- **AGAPIC :** demander largeur, hauteur et profondeur à `Aga Bank Image Info(Bank,Champ)` pour une banque vivante ; les vérifications doivent être répétées si une source est remplacée. `Aga Bank Image Draw(Bank,X,Y,Mode)` résout lui-même la banque et refuse ses erreurs. La capture AGAPIC v2 peut contenir une palette/ModeID, mais **dessiner une image ne l'applique pas** : décision explicite de l'application et compatibilité écran à vérifier.
- **FICON8 :** source fixe **16×16, 8 plans**, banque FICON8 et `IconID` à partir de 1 ; rendu par `Aga F Icon`. Option cache `Aga F Chip Stage` + `Aga F Blit` uniquement après preuve de gain ; ce n'est pas le format AGAPIC. Le type ne sera admis que sur écran à 8 plans.
- **Première cible P2 :** 320×256×256 / 8 plans comme P1. Les autres profondeurs nécessitent des essais spécifiques et ne sont pas déclarées validées. Le gestionnaire ne convertit ni la profondeur, ni les couleurs, ni la palette en cachette.

## 4. Opérations conceptuelles — **aucune nouvelle syntaxe AMOS décidée**

1. **Ouvrir le contexte** après `Aga Screen Open` et `Aga Double Buffer` réussis ; vider la table logique, mémoriser la configuration d'écran, préparer au besoin les tampons AMAL **hors boucle de dessin**.
2. **Créer un objet** en validant type/source/frames/hotspot et en allouant un ID logique. Refuser un identifiant ou une banque invalides sans modifier les autres objets ; pas de création ou capture d'images implicite.
3. **Modifier** X/Y, frame, visibilité, priorité, et éventuellement rattacher/détacher un canal AMAL déjà autorisé. Une propriété invalide doit laisser le dernier état cohérent.
4. **Avancer les mouvements** une fois par tick : `Synchro` manuel si AMAL actif, lecture `Deek` des tampons, conversion X/Y ou A en indices logiques (mapping explicitement défini). Le séquenceur BASIC des frames 16/24 ticks P1 reste une alternative simple.
5. **Dessiner la liste** : reprendre l'état courant des objets (snapshot par frame), trier par `(Z,CreationOrder)`, dessiner les visibles. Cette opération **ne fait ni `Aga Swap`, ni attente VBL, ni modification de palette**.
6. **Supprimer un objet** : désolidariser ses liaisons AMAL, ne plus le dessiner, invalider l'ID ; **ne jamais `Erase` sa banque image** si elle appartient au programme ou est partagée.
7. **Fermer le contexte** explicitement avant la fermeture de l'écran : couper les canaux AMAL possédés, rendre inaccessibles leurs tampons, libérer uniquement les ressources du gestionnaire. Réouvrir l'écran impose un nouveau contexte et de nouvelles références logiques.

Le détail de l'**arrêt AMAL par canal** et de la cohabitation avec les canaux du programme est à vérifier avant l'implémentation. Les prototypes P0/P1 utilisent `Amal Off` global : ce comportement ne doit **pas** devenir silencieusement la politique d'une bibliothèque réutilisable.

## 5. Synchronisation et traitement d'un frame

```text
cadence application (éventuellement Aga Wait Vbl)
    -> Synchro manuel (optionnel, aucun dessin)
    -> Update positions/images, snapshot logique
    -> demande de fond complet dans le back buffer AGA
           refus 0 : Safe absent OU argument/état invalide
           retry borné + VBL, jamais boucle infinie
    -> dessiner les objets visibles dans l'ordre Z stable
           AGAPIC : Aga Bank Image Draw
           FICON8 : Aga F Icon (ou cache F Blit explicitement préparé)
    -> si une opération échoue : NE PAS Swap le frame incomplet
           prochaine tentative : reconstituer le fond ET tous les objets
    -> Aga Swap explicite par l'application (retry borné)
```

- **`Aga Wait Vbl` n'est pas le signal `Safe`.** Les commandes R84 vérifient leur propre état de sécurité ; un retour `0` n'identifie pas à lui seul la cause. Un retour refusé au milieu d'un frame rend celui-ci incomplet : on n'effectue pas un Swap partiel.
- **Aucun Blitter/C2P, dessin, allocation ou libération en interruption**. La logique AMAL doit rester en mode `Synchro Off` avant déclaration, puis `Synchro` à un point décidé par BASIC.
- **Fond complet en P2** comme en P1. Pas de restauration de rectangle d'arrière-plan ni de *dirty rectangles* tant que leur bénéfice et les deux buffers ne sont pas prouvés.
- **Une seule présentation par frame terminé**, pas de Swap automatique sur ajout, suppression ou déplacement d'un objet.
- Le gestionnaire de projet doit distinguer le canal d'animation et la notification `Disp` de l'écran : **aucune lecture/consommation parallèle** des ports Safe/Disp appartenant à la bibliothèque.

## 6. Propriété mémoire, erreurs et fermeture

- **Sources image :** seules des banques AMOS DATA existantes sont référencées ; pour tester une banque **absente**, utiliser `Length(N)`, jamais `Start(N)`. `Start(N)` ne sert qu'à l'adresse d'une banque effectivement réservée, notamment les tampons AMAL. Le gestionnaire ne doit pas conserver un pointeur brut vers une banque image après `Erase`, `Load` ou réallocation.
- **Tampons AMAL :** 8 octets par canal dans les essais P0/P1 (flags WORD, X WORD, Y WORD, A WORD). Adresse paire, durée de vie couvrant tout le fonctionnement des canaux. Arrêt de leurs écritures avant `Erase` / fermeture.
- **Erreurs attendues :** ID périmé, image effacée, banque autre format, profondeur incompatible, frame inexistant, z ou coordonnées hors domaine, contexte écran absent/fermé, état non `Safe`, canal AMAL déjà utilisé, mémoire insuffisante. Proposer un mécanisme de diagnostic **BASIC d'abord** ; ne pas inventer une convention de retour AP20.
- **Référence/ownership :** la table manager *n'est pas propriétaire* des banques AGAPIC/FICON8 ; le programme s'engage à garder les images vivantes pendant l'utilisation. Une banque supprimée de l'extérieur doit provoquer refus propre à la prochaine vérification/dessin, sans dessiner sur un pointeur périmé.
- **Ctrl+C / erreur AMOS :** la séquence normale doit être testée (`Amal Off` approprié, écran fermé, retour AMOS, ressources libérées). Un arrêt brutal peut contourner le cleanup BASIC : ne **pas prétendre** à un nettoyage garanti avant d'avoir conçu et testé le hook adéquat.
- **Performance :** initialiser les tables et sources avant les frames ; mesurer `Aga Bank Image Draw` (CPU/RLE) et `Aga F Icon` avant d'envisager une routine native. L'unité AGA R84 fait **56 580 octets**, marge Compiler V2 documentée **8 954 octets** ; ajouter plusieurs fonctions natives est un choix coûteux à justifier.

## 7. Prototype P2.0 recommandé, toujours sans commande native

| Test sous WinUAE Runtime | Attendu |
|---|---|
| >=4 objets logiques | 2 AMAL et >=2 pilotés en BASIC, image AGAPIC et FICON8, transparence et opaque |
| IDs et suppression | Création, suppression au milieu de la démonstration, ID ancien refusé, ajout sans confusion |
| Positions / hotspot | Cas central, coordonnées décalées, affichage partiel sur les 4 bords, disparition hors écran |
| Z / stabilité | Tri stable, permutation contrôlée, pixel témoin différent sur chevauchement |
| Image / visibilité | Sélecteur de frames valide/invalide ; masquage puis réaffichage sans traînée |
| Banque absente | Refus propre sans Guru, sans effacement des banques préexistantes |
| Buffer / swap | Rendu seulement sur Safe, fond entier à chaque frame, Swap explicite, aucun frame incomplet présenté |
| Retour / mémoire | 240 frames cibles, `RESULT`, `ERR`, journal RAM, Chip/Fast avant/après, fermeture nette |

**Ordre de validation retenu pour P2.0 :** prototype AMOS BASIC + preflight statique (un seul ASC actif, P1 archivé octet pour octet), puis Gate B WinUAE ; **ensuite** mesurer le cout CPU/Chip et decider si une API native vaut le budget. Les tests Compiler Gate C et Amiga physique Gate D restent des portes distinctes.

## 8. Points soumis à validation avant implémentation

1. Garder le **gestionnaire P2.0 en BASIC** pour l'essai initial, plutôt que créer immédiatement une commande native.
2. Conserver **les banques sources sous propriété de l'application**, et le gestionnaire responsable uniquement de ses objets et éventuels tampons AMAL.
3. Utiliser **un ordre Z logiciel stable**, sans promettre le même ordre pour de futurs sprites matériels AGA.
4. Distinguer **mouvement AMAL, choix de frame, rendu et Swap** ; aucune action de dessin dans une interruption.
5. Attendre un banc Runtime et des benchmarks avant de décider **la surface d'API AP20** (une ou plusieurs instructions), les limites d'objets, les codes de retour, l'ABI, la mémoire et le budget Compiler.

**Statut P2.0 : prototype BASIC validé sous WinUAE Runtime 68030, sans API native validée.** Le test P2.0 remplace P1 dans `tests/current/` en archivant l'ancien banc exact ; le document seul n'autorise aucune modification de `dist/`, de l'ABI ou d'une archive historiseee.

### Références projet

- [Plan M19 et jalons](M19_SPRITES_BOBS_AMAL_PLAN.md)
- [Rapport P1 Runtime 68030](M19_P1_WINUAE_RUNTIME_2026-11-15.md)
- [Architecture privée R84](ARCHITECTURE.md) et [protection Safe du Blitter](M12_SAFE_BLITTER_R27.md)
- [API publique R84](../README.fr.md), [règles permanentes](../EXTENSION_SOURCE_RULES.md)
- [Test P2.0 validé archivé](../tests/passed/M19_P2_OBJECTS_01.asc) · [Benchmark actif 4/8/16 Bobs](../tests/current/M19_P2_BENCH_BOBS_01.asc) · [Test P1 validé archivé](../tests/passed/M19_P1_AGAPIC_BOBS_01.asc)
