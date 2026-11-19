# M19 B8 — Aga Bob Clear / Update : modèle, primitives CPU020 et architecture AP20 (19 novembre 2026)

## État réel

**Développement en cours, SOURCE-ONLY.** Aucun token `Aga Bob Clear` ou `Aga Bob Update` n'est installé dans `dist/AMOSPro_AGA.Lib`. La bibliothèque active **B7-m2 reste 102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`. Son scénario Bob Lifecycle dispose de Gates A/B/C PASS ; aucun résultat n'est transféré aux nouvelles fonctions.

Le modèle exécutable `tools/m19_bob_clear_update_model.py` et son test `tools/test_m19_bob_clear_update_model.py` servent d'**oracle de comportement**. Les primitives natives, leurs tests CPU020 et la candidate AP20 source-only sont documentés plus loin ; ils ne constituent **pas** encore les commandes utilisables dans AMOS.

## Contrat fonctionnel retenu pour le prototype

- **`Aga Bob Clear` (nom et fonction numérique 1/0 proposés, non exportés)** : restaurer le fond du **back buffer physique courant**, tel qu'il a été sauvegardé avant la dernière étape de dessin sur cette page. Le front affiché et l'autre page ne doivent pas changer. `Clear` ne fait pas de Swap et ne désactive pas les Bobs.
- **`Aga Bob Update` (fonction numérique 1/0 proposée, non exportée)** : prévalider toutes les images actives et leurs générations de banque, restaurer la page arrière si elle contient les Bobs d'une frame précédente, capturer son fond puis dessiner **1 à 64 Bobs** dans l'ordre des IDs. Un programme ayant déjà appelé `Clear` peut dessiner son nouveau décor avant `Update` ; cette mise à jour ne doit pas effacer ce nouveau décor.
- **Aucun `Aga Swap` implicite.** Un `Update` réussi place la frame en `READY` ; seul l'appel `Aga Swap` du programme la présente. Tout `Update` échoué place la frame en `DIRTY` et interdit le Swap.
- **Récupération après échec** : un `Clear` peut lever `DIRTY` seulement si une sauvegarde complète/valide de cette même page existe et a été restaurée. En l'absence de sauvegarde, la fermeture de l'écran est nécessaire. **C'est un changement proposé au garde B5**, non implémenté dans B7-m2.
- Les banques AGBO de B7-m2 et les masques transparents indépendants sont conservés. Les pixels index 0 restent opaques en l'absence de masque ; coordonnées négatives et clipping sont supportés. Les anciennes références de banque ne sont jamais dessinées après remplacement ou `Erase`.

## Algorithme de départ : fond sauvegardé indépendamment sur les deux pages

Chaque page physique dispose d'un snapshot propre. Pour la première implémentation de référence, on copie **tout le fond** avant de dessiner. Après un Swap, la page affichée devient frontale ; lorsqu'elle redevient inactive, `Clear` restaure son snapshot. Cette solution évite les Bobs fantômes et les erreurs de superposition (l'ordre de rendu des 64 Bobs est stable).

Coût théorique par page planaire non compressée : `2 × ceil(largeur / 16) × hauteur × profondeur` octets. À **320×256×8**, c'est **81 920 octets par page**, soit **163 840 octets pour les deux snapshots**, hors métadonnées, AGBO, buffers AGA et alignement. Le modèle compte ce coût, sans réaliser d'allocation Amiga. **Les performances CPU020 et les ressources Chip/Fast n'ont pas été mesurées.** Avant de connecter le code natif, vérifier si une restauration par rectangles sauvegardés, plus économe, doit remplacer le snapshot plein écran.

## Résultats du modèle

Exécuter `python -B tools/test_m19_bob_clear_update_model.py`. Les **14 tests fonctionnels** vérifient : double buffering sans Swap caché, `Clear` par page et idempotence, Off/réactivation et déplacements, fond dynamique entre Clear et Update, chevauchements, masques, index 0, clipping, 64 objets, **405 frames réparties en neuf étapes**, dimensionnement planar, perte/recréation de banque, faute en milieu de dessin, budget insuffisant avant premier pixel et Close → Open.

Ces tests sont réalisés sur **matrices de pixels Python** ; ils **ne valident pas** `graphics.library`, les signaux `Safe`/`Disp`, le vrai bitmap AGA, le DMA, le Blitter, l'ABI AMOS/AP20, le CPU MC68020, WinUAE ou AMOS Compiler.

## B8 — Avancement natif MC68020 vérifié (19/11/2026)

Après le modèle Python (14 tests de pixels), **trois briques natives privées** ont été implémentées dans `tools/`. Elles sont **source-only** ; aucune des commandes `Aga Bob Clear` et `Aga Bob Update` n'est encore disponible dans AMOS.

| Composant | Source et preuve | Résultats MC68020 |
| --- | --- | --- |
| Copie planaire capture/restauration, 1 à 8 plans | [Émetteur](../tools/m19_b8_planar_snapshot_emit.py) · [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44605103071) | **36 cas PASS**, 2 adresses natives ; `TypeOfMem` simulé |
| Sélection du **back BitMap**, refus en cas de Safe en attente | [Émetteur](../tools/m19_b8_back_selector_emit.py) · [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44606589452) | **34 cas PASS**, 2 adresses ; aucun accès/écriture au front |
| Pool de deux sauvegardes, `AllocMem`/`FreeMem`, propriétaire A5, rollback transactionnel | [Émetteur](../tools/m19_b8_snapshot_pool_emit.py) · [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607135635) | **52 cas PASS**, 2 adresses ; appels Exec simulés |

**Attention à la portée des preuves :** le CPU exécuté est bien l'émulateur MC68020 Unicorn, mais les fonctions Exec, les ports graphiques et les allocations réelles sont simulés. Ce ne sont **pas** des tests Runtime WinUAE ou AMOS Compiler. Le pool exige une taille correcte fournie par un appelant de confiance ; il ne calcule pas encore lui-même la géométrie réelle. Le sélecteur refuse `DBState.Safe pending` sans attendre : le protocole de récupération `SafePort` reste à intégrer à `Clear`/`Update`. La libération automatique `Screen Close`/`End` reste à raccorder.

### Contraintes AP20 et décision d'architecture

Une première candidate AP20 B8 à **quatre unités** empilait les trois briques dans l'unité BOBS :

- [Builder de vérification 4 unités](../tools/build_m19_b8_page_services_in_memory.py) : **105 976 octets**, SHA256 `3a654b1f4a3c1d74ba2c15ca59f233c4b077de2f1e7c844540c71aaf463b14a8`, taille de l'unité BOBS **32 492 octets**, portée PC16 maximale **32 510**, marge seulement **256 octets** ; [Gate A AP20 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607378131).
- Cette marge est **insuffisante** pour les wrappers natifs complets `Clear` et `Update`. Cette variante reste un test de capacité **non installé** et n'est **pas** la cible retenue pour la suite.
- **Cible B8 retenue : cinquième unité native AP20, source-only.** [Builder](../tools/build_m19_b8_fifth_group_in_memory.py), [test](../tools/test_m19_b8_fifth_group_gate_a.py), [CI 44607784087 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607784087). **106 020 octets**, SHA256 `4b5371726c5eb5ac8bd1d9092c42efc41b0d74e9c8940019b9e0f6d8d0f96be3`, **182 entrées AP20**, **86 commandes publiques inchangées**, unités natives `[142,153,156,177,181]`. La cinquième unité de **3 606 octets** porte copie, sélection et pool. Les **181 anciennes entrées et quatre groupes B7-m2 restent octet pour octet inchangés**, les déplacements PC16 existants restent à **28 938** et **aucun nouveau token** n'a été déclaré.
- L'ancienne cinquième unité de **diagnostic** avait ses propres [Gates B/C PASS](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md) ; **cela ne valide pas** la nouvelle cinquième unité B8. Gate A B8 prouve seulement l'émission source, la structure AP20, le CPU isolé et l'absence de régression de layout détectée.
- La distribution conserve **exclusivement** `dist/AMOSPro_AGA.Lib` B7-m2 (**102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`), l'ASC actif et la R84 `LAST_GOOD` strictement inchangés.

### B8 — Coordination privée des snapshots MC68020 : Gate A PASS (19/11/2026)

**Nouvelle étape vérifiée sur `main` :** [émetteur `m19_b8_page_manager_emit.py`](../tools/m19_b8_page_manager_emit.py), [banc CPU](../tools/test_m19_b8_page_manager_gate_a.py), [builder AP20 en mémoire](../tools/build_m19_b8_page_manager_in_memory.py), [CI 44611440112 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44611440112). **58 scénarios MC68020 PASS**, deux placements du code natif, Exec/AllocMem/FreeMem/TypeOfMem simulés. Vérifications : réservation de deux pages transactionnelle, sélection du back uniquement après Safe, allocation par taille `BytesPerRow × Rows × Depth` identique sur les deux BitMap, liaison propriétaire A5/Screen*/DBState*/BitMap*, capture/restauration physique page par page, indicateur de snapshot valide indépendant pour chaque page, bascule de front, refus d'un propriétaire étranger, double Close sans double FreeMem, rollback sur échec d'AllocMem, refus de géométrie modifiée, de plans front/back qui se chevauchent (y compris partiellement) et invalidation d'un snapshot après échec de capture.

Le gestionnaire conserve les **3 572 octets des primitives B8 précédentes à l'identique**, et expose uniquement des entrées *privées* `b8_service_bind/capture/restore/close_entry`. La candidate source-only AP20 cinq unités construite en mémoire : **111 396 octets**, SHA256 `98166666ebe11c8c7210b3f734c5615567a9eb221c7ecf440fa1c005f97add37`, **86 commandes**, **182 entrées AP20**, groupes `[142,153,156,177,181]`, cinquième groupe **9 000 octets**, portée PC16 maximale **28 938** comme B7-m2, anciennes sections/stubs byte-exact. **Aucun token Clear/Update, aucun nouveau binaire installé, pas de nouvelle Gate B/C.**

**Limites bloquantes pour la suite :** liaison réelle au cycle `Screen Close`/`End` et au protocole `Safe/Disp`/Blitter ; une tentative pendant Safe pending est refusée sans attente. Le compteur d'époque privé n'est **pas** une génération certifiée par AmigaOS et ne détecte pas une destruction/recréation d'écran à la même adresse sans hook de fermeture. `TypeOfMem` est une vérification de présence mémoire, **pas** une preuve de durée de vie/contiguïté pour tous les objets. Le caller devra garantir un écran vivant, stable et des appels sérialisés. Le gestionnaire n'efface pas encore `DIRTY` dans la barrière B5 et ne dessine pas de Bob. Le vrai WinUAE et le vrai AMOS Compiler **n'ont pas exécuté cette candidate**.

**Protections confirmées en CI :** `dist/AMOSPro_AGA.Lib` B7-m2 SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`, `LAST_GOOD` R84 SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` et l'ASC validé SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec` inchangés. Pas de promotion ni d'installation.

### Prochaine étape technique après coordination privée

1. **Raccorder le gestionnaire privé désormais testé** aux vrais événements Safe/Disp et au Blitter, puis au cycle de vie réel Screen/DBState ; vérifier la génération d'écran et les refus après destruction/recréation. Ne pas exposer la copie sans une page inactive et réellement Safe.
2. Raccorder le pool à **`Screen Close` et `End`** : chaque allocation doit être libérée une fois et le reset du Bob Lifecycle B7-m2 doit rester correct.
3. Raccorder **`Clear`** (restauration de la page arrière) et **`Update`** (préflight de toutes les banques/images, Clear nécessaire, capture du fond, puis Draw), avec garde `DIRTY/READY`, **sans Swap implicite**, et tester fonds dynamiques et passages de page.
4. Ajouter les deux **tokens AP20 publics avec stubs proches de la cinquième unité**, de véritables signatures AMOS/Compiler vérifiées et un banc ASC dédié ; réaliser la Gate A complète avant **une nouvelle autorisation distincte** de remplacement de la Lib active. Aucun PASS Runtime/Compiler n'est transférable.

**Statut au 19/11 : briques natives privées Gate A PASS, candidate AP20 cinq unités SOURCE-ONLY PASS ; commandes AMOS publiques Clear/Update NON IMPLÉMENTÉES, Gates B/C NON TESTÉES.**

## Conditions bloquantes pour l'implémentation native B8

1. Identifier dans les sources B7-m2 les **deux BitMap physiques** de l'écran privé, leurs plans réels, le propriétaire A5 et les transitions `Safe`/`Disp` ; refuser sans toucher à la mémoire toute page non-Safe.
2. Définir l'allocation, la durée de vie, le mapping et la libération des **snapshots par écran et par page**, avec vérification de la plage entière via l'API Exec. Ne jamais utiliser un pointeur Fast comme source DMA.
3. Prévalider les 64 images/masques et la génération des banques **avant** premier DMA. Conserver l'état `DIRTY` si la restauration échoue, refuser `Swap`, vérifier le callback `End` et Close sans double libération.
4. Les **émetteurs MC68020 et la cinquième unité privée AP20 sont disponibles en source-only**. Il faut maintenant le **raccordement complet**, valider les signatures des tokens AMOS/Compiler et les essais mémoire/Safe/Disp. Le coût CPU, la géométrie sûre des allocations et les nouvelles Gates B/C restent inconnus.
5. **Gate A native, puis autorisation distincte de bascule de Lib**, puis Gates B Runtime et C Compiler sur l'ASC exact. Aucun changement de `LAST_GOOD` ni de l'ASC actuellement validé dans cette étape.

**Statut : modèle Python 14 tests PASS ; primitives natives 36 + 34 + 52 cas MC68020 PASS ; candidate AP20 cinq unités source-only PASS ; API publique Clear/Update NON implémentée.**
