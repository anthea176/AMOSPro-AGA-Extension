# Audit transversal AMOSPro AGA Extension — passage 1 (gel des corrections)

**Date de référence : 23 novembre 2026** · **Dépôt :** `anthea176/AMOSPro-AGA-Extension` · **Branche : `main` exclusivement**  
**HEAD source audité :** [`45516f8772a24b5d7ad887d2a0f2b7cee5203e98`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/45516f8772a24b5d7ad887d2a0f2b7cee5203e98)  
**Statut : AUDIT OUVERT — aucune correction autorisée. Sprite S1-P1e GELÉ.**

> Ce document est un **rapport de lecture seule** et non une validation Runtime. Les résultats ici sont associés au HEAD de référence, même si de futurs commits ne modifient que la documentation. Il complète la [matrice 102 commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) et le [cahier de non-régression](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md). L'inventaire 102/102 ne signifie pas 102/102 fonctions démontrées correctes.

## 0. Gel et provenance

| Référence | Taille | SHA256 du fichier | Provenance / statut |
|---|---:|---|---|
| `dist/AMOSPro_AGA.Lib` | 142 000 | `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106` | Candidate **S1-P1e**, 102 commandes / 208 entrées AP20 ; builder [S1-P1e](../tools/build_m19_s1p1e_get_sprite_ap20.py), source native MC68020 ; Gate A source/CI PASS, **B/C/D capture Sprite non testées** |
| `dist/AMOSPro_AGA_LAST_GOOD.Lib` | 136 020 | `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` | **P2d protégée**, 100 commandes / 203 entrées AP20 ; [builder P2d](../tools/build_m19_p2d_in_memory.py), [master ASM MC68020](../src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s) ; Gates B/C **du seul banc intégré** PASS |

Empreintes *Git blob* au HEAD gelé (à ne pas confondre avec SHA256 du fichier) : S1-P1e `5a3605e8347f4ef6cc5c18f1f31826acace8b303`, P2d `8a849b89aae57c2cda0b4db8771034a0978d3e78`.

**Fichiers intouchables pendant le gel :** deux Lib dans `dist/`, sources `src/`, builders et scripts `tools/`, unique banc `tests/current/M19_P2_ALL_IN_ONE.asc`, `tests/passed/`, `tests/proto/`, `examples/`, preuves `docs/evidence/`. La présente publication ajoute **uniquement des documents d'audit**. Aucun programme AMOS/WinUAE/Compiler exécuté au cours de cette lecture.

**Hiérarchie de preuve :** (1) octets/source *effectivement liée* (master et unités `src/native/m19_p2d/`) ; (2) builders/emitters dont l'assemblage source est vérifié identique ; (3) journaux *originaux* archivé(s) ; (4) comptes rendus de journaux reçus mais non archivés ; (5) hypothèses. Les commentaires historiques des émetteurs ne prouvent pas qu'un patch est ou n'est pas installé.

## 1. Constats avérés dans les sources natives

### AGA-001 — `Aga Iff Load` : chemin de copie sans acquisition Safe visible — **P0, risque potentiel**

Dans l'[unité native IFF Load](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L321-L458) :
- `L_UNIT142_01254` (lignes 321–402) contrôle les dimensions écran/bitplanes, puis sélectionne le **bitmap arrière** via `DB+8` et le pointeur ScreenBuffer.
- `L_UNIT142_01360` (lignes 403–494) décode BODY ; `move.b d0,(a6)+` écrit directement dans les plans lorsque `100(a5)` déclenche la passe d'écriture. Le prétraitement est exécuté deux fois (validation/décodage puis écriture).
- **Aucune consommation `GetMsg(SafePort)`, ni test du flag pending `DB+20 bit0`, n'a été identifiée dans la routine examinée, entre la sélection de la page et les écritures.** Les commandes graphiques protégées emploient habituellement cette acquisition.

**Preuve : lacune statique sur ce chemin d'écriture.** Le déclenchement d'une écriture alors que la page est *effectivement* non-Safe et les conséquences réelles nécessitent encore Gate A ciblée et Gate B. La gravité P0 est liée au risque potentiel de concurrence avec l'affichage, **pas à une corruption mémoire déjà reproduite**. Vérifier en plus l'entrée AP20 de ce token pour exclure un garde supérieur, avant conclusion définitive.

**Défaut associé à vérifier :** une erreur de décodage lors de la seconde passe pourrait laisser une page partiellement modifiée sans rollback/snapshot transactionnel. La preuve d'une erreur atteignant effectivement ce stade manque (AGA-007).

### AGA-002 — `Aga Swap` / B8 : refus avant acquittement de Safe — **P1, enchaînement structurel**

Sources :
- [Wrapper public Auto Update P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_p2d_bob_auto_update_emit.py#L76-L132) : lorsque des Bobs sont actifs, `p2d_service_update` précède `guarded_swap_entry`. Si l'Update renvoie 0, le Swap original n'est pas appelé.
- [Premier Update B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_first_update_emit.py#L140-L170) : la voie initiale fait **Bind → Arm → Update**.
- [Sélecteur back B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_back_selector_emit.py#L53-L90) : rejette immédiatement un Safe pending, **sans `GetMsg`**.
- [Routine de Swap originale](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s#L22-L55) : après contrôle de DB pending, acquitte Safe/Disp via `GetMsg` dans `L_UNIT142_00C3C`, puis effectue `ChangeScreenBuffer` et remet les indicateurs pending.
- [Acquisition B8 existante](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_safe_lifecycle_emit.py#L72-L131) : `GetMsg(SafePort)` existe **après** constitution du contexte/pool, mais ne secourt pas le **Bind initial** si le sélecteur le refuse déjà.

**Conséquence potentielle :** si le Safe pending est prêt à être acquitté mais que B8 le refuse avant d'atteindre le Swap original, le même appel ne peut pas avancer. Le code de reprise de [`Aga Bob Clear`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_safe_retry_emit.py#L32-L120) est borné à trois `WaitTOF` et exige déjà un pool et un snapshot valides ; il ne constitue pas une correction générale du premier Bind.

**Nuance :** un autre appel (`Aga Blit Fill`, etc.) peut consommer SafePort entre deux tentatives ; le caractère permanent du blocage n'est pas établi. Un refus de Swap `0` n'est pas automatiquement une corruption ou un bug ; les refus répétés sans récupération sont à isoler.

### AGA-003 — Décor externe et snapshots B8 — **P1, compatibilité non prouvée**

Les [snapshots B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_page_manager_emit.py#L261-L349) sont associés aux **bitmaps physiques** et possèdent des bits de validité. [`Aga Bob Clear/Update`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_clear_update_tx_emit.py#L217-L329) gère `cleared`, `pending`, `txepoch`, restaure un ancien fond et capture le nouveau. En revanche, les chemins examinés `Aga Blit Fill`, `Aga Plot`, `Aga Image Draw`, `Aga Iff Load` et `Aga C2P Convert` ont chacun leur écriture arrière, **sans notification B8 explicite identifiée dans leurs sources inspectées**.

**Risque :** après sauvegarde du fond, une modification externe du décor sur cette page peut être écrasée par un Restore ultérieur. Il faut clarifier le **contrat utilisateur** (Clear obligatoire avant dessin du décor ?) avant de qualifier ce cas d'anomalie plutôt que d'usage hors séquence. Tester d'abord une modification visiblement distincte, puis inspecter la page après Clear/Update/Swap.

### AGA-004 — Close / End / réouverture et identité de pages — **P1 à qualifier**

Les sources [pool](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_snapshot_pool_emit.py#L63-L149) et [gestionnaire](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_page_manager_emit.py#L219-L361) contrôlent owner, Screen*, DBState*, BitMap*, dimensions et epoch locale ; la [transaction B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_clear_update_tx_emit.py#L181-L211) évoque elle-même le risque **ABA** en cas de réutilisation de pointeurs après destroy/reopen sans fermeture attendue. L'[ancien Close UNIT142 R83](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_SAFEWAIT_MC68020.s) et les chemins Bob/End doivent être suivis **jusqu'aux cibles effectivement liées**, pas supposés sûrs sur un seul commentaire. Absence de fuite ou double Free **non démontrée**.

### AGA-005 — CI générale : empreinte S1-P1e refusée — **P2, confirmé**

Au HEAD gelé, le job [`verify`](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45275935053/job/138047605608) échoue dans `tools/test_compiler_bridge_v2_probe.py:135` : l'assertion `Current must be an exact SHA-pinned V2 library` ne comprend pas l'empreinte S1-P1e. Les jobs `native-cpu-and-delivery-policy` et `p1a-mc68020-only` du même commit ont réussi. **C'est une incohérence de politique CI, distincte de l'anomalie 2D et qui ne justifie pas de modifier la Lib pendant le gel.**

### AGA-006 — `Aga Blit Copy/Fill/Clear`, primitives graphiques individuelles — **contrôles locaux présents ; coordination globale manquante**

[Émetteur R27 Safe](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m12_blit_safe_r27_emit.py#L17-L57) : vérifie `DB+20`, consomme au plus un message Safe via `GetMsg`, échoue sans DMA si absent ; [Draw/Plot/Box/Circle/Text](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m15_plot_r40_emit.py#L113-L153) suivent des vérifications analogues ; [AGAPIC Image Draw](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m16_image_draw_r45_emit.py#L183-L255) et [C2P Convert](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/c2p_r75_convert_emit.py#L89-L149) acquièrent également Safe avant écriture.

**Conformité *locale* statiquement soutenue** pour les chemins cités (sous réserve de leurs wrappers *effectivement liés*), **pas conformité de leurs interactions B8**, ni validation B/C des séquences croisées. `WaitBlit` n'équivaut pas à acquittement de `SafePort`. `Aga Back Fill`, `Aga Cache Blit`, `Aga F Blit` et les autres chemins d'écriture doivent être tracés de leur token à leur garde réel.

### AGA-007 — IFF BODY : transaction de publication / écritures partielles — **P1 potentiel**

La [routine IFF](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s#L47-L80) traite le BODY une fois, puis revient le traiter avec le mode écriture activé. Les vérifications de borne peuvent provoquer une sortie d'échec pendant le décodage de la seconde passe : risque de **page partiellement écrite** sans restauration. **À prouver** par un IFF valide pour la première passe mais provoquant une erreur de la seconde (si un tel état peut être déclenché), ou à déclasser après démonstration que les deux passes sont déterministes et ne divergent pas.

### AGA-008 — Incomplétude des essais croisés — **P1 de couverture**

Le [banc public P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc#L134-L152) prépare les deux pages par `Aga Blit Fill` avant les Bobs. Il couvre une séquence valide, **pas** la première capture IFF immédiatement après Swap ni un premier Update B8 sur Safe pending sans Fill. Manquent aussi les états *sans snapshot*, *snapshot invalidé*, *Close puis réouverture*, *décor IFF rechargé après Swap* et les variantes CBlock/AGBO.

## 2. Éléments Runtime / Compiler conservés comme preuves

| Essai exact | Preuve disponible | Résultat / limite |
|---|---|---|
| P2 ALL IN ONE Runtime P2d | [TXT original](evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT), `PRG_STATE 1` | **Gate B PASS**, `RESULT 1`, `ERR 0`, 240 échantillons, 252 Swap, **121 refus et 121 récupérations**, `CLOSE_RETURNED 1` |
| Même ASC, vrai Compiler P2d | [TXT original](evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT), `PRG_STATE -1` | **Gate C PASS** pour ce scénario, avec 121 refus récupérés |
| P2e.1 AMAL Runtime échec | [TXT original](evidence/M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT) | **FAIL** `ERR 15`, frame 2 ; ne pas remplacer par le log PASS ultérieur |
| P2e.1 AMAL Runtime reprise | [TXT original](evidence/M19_P2E1_AMAL_RUNTIME_PASS_RETRY_2026-11-21.TXT) | **PASS** 240/240, 120 refus et 120 récupérations |
| Variantes RPG 16×16 / 20×16 / 20×18 | [README prototypes](../tests/proto/rpg_bob_dim/README_SWAP_EDGE.md) | Résultats Runtime PASS **rapportés**, journaux originaux non archivés dans Git à ce HEAD |
| 20×18 avec VBL avant Swap | [README EDGE_SAFE](../tests/proto/rpg_bob_dim/README_EDGE_SAFE.md) | **PASS rapporté**, 0 refus, 240 VBL avant Swap ; pas une mesure 50 fps |
| 20×18 bord opaque | [README EDGE_SAFE](../tests/proto/rpg_bob_dim/README_EDGE_SAFE.md) | **FAIL rapporté** `ERR 15`, frame 221, 111 refus dont 110 récupérés ; les 123 tests du pixel (19,17) avaient réussi. **Cause Safe vs DIRTY indéterminée** |
| `P2_EDGE_SWAPVBL_20X18.asc` | [Source de diagnostic](../tests/proto/rpg_bob_dim/P2_EDGE_SWAPVBL_20X18.asc) | Préflight statique rapporté PASS ; **Gate B/C non exécutées** sur la variante combinée |
| Candidate S1-P1e Get Sprite | [Rapport S1-P1e](M19_S1_P1E_GET_AGA_SPRITE_2026-11-23.md) | Gate A native CPU/CI PASS de référence ; **aucune Gate B/C/D pour la nouvelle capture**. En pause |

Les logs **rapportés mais non archivés** doivent être conservés à leur provenance originale ; aucun chiffre ne doit être copié dans `docs/evidence/` comme s'il provenait d'un fichier complet vérifié.

## 3. Lecture des états internes et dépendances

| État | Sens observé | Règle de revue |
|---|---|---|
| `CLEAN=0` | Pas de frame Bob prête dans le garde ; aucun verrou DIRTY | Ne signifie pas nécessairement que SafePort est acquis |
| `DIRTY=1` | Update préparé/échoué, page non publiable | Refuser Swap ; proposer un chemin de récupération explicitement sûr |
| `READY=2` | Bob frame préparée pour la page et l'identité courantes | Swap réussi remet l'état à zéro ; refus préserve READY |
| `DB+20 bit0` | Notification de page arrière Safe encore pending | Une attente VBL ne vide **pas à elle seule** SafePort ; `GetMsg` ou refus justifié requis |
| `DB+20 bit1` | Disp pending | Ne pas l'effacer pendant l'acquisition Safe ; laisser le propriétaire l'acquitter |
| `B8 valid` | Snapshot valable pour un bitmap physique précis | Invalider/réviser après toute écriture de décor incompatible avec une restauration |
| `B8 epoch` | Génération locale de bind | N'est pas à elle seule une preuve de génération Open/Close OS distincte |

Sources : [Swap P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_p0j_swap_barrier_emit.py#L136-L179) ; [Safe B8](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_safe_lifecycle_emit.py#L72-L131) ; [snapshot + epoch](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_page_manager_emit.py#L219-L349) ; [transaction](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/tools/m19_b8_clear_update_tx_emit.py#L217-L329).

## 4. Matrice décisionnelle / corrections envisagées (PAS APPLIQUÉES)

1. **P0** : auditer le garde Safe de **tous** les écrivains de bitplanes, confirmer IFF, définir un protocole unique d'acquisition avant écriture et un refus sans écriture partielle.
2. **P1** : réconcilier l'acquittement de Safe avant premier Bind B8 / Update automatique / Swap, sans masquer les refus légitimes ni ajouter d'attente infinie.
3. **P1** : définir le contrat des décorations entre Clear / Update / autres auteurs ; mettre à jour les snapshots de façon transactionnelle ou invalider explicitement.
4. **P1** : tracer Close/End et génération des objets OS, propriétaire, FreeMem, réouverture, sans supposer qu'un pointeur réutilisé identifie la même ressource.
5. **Validation** : Gate A par chemins/états injectés, puis Gate B Runtime et Gate C vrai Compiler **sur le même ASC exact et le SHA de Lib relevé** ; ne pas confondre les Gates.
6. **Sprite** : conserver S1-P1e 142 000 octets, suspendre les essais/corrections et vérifier plus tard sa compatibilité avec tout protocole graphique commun corrigé.
7. **CI** : traiter AGA-005 indépendamment après accord, sans changer les tests validés ni promouvoir LAST_GOOD automatiquement.

## 5. Clôture et limites de ce passage

- **Inventaire API :** 102 noms retrouvés, documentés individuellement dans la matrice ; toutes les familles couvertes conceptuellement.
- **Audit détaillé de tous les chemins liés : INCOMPLET**, notamment IFF wrapper AP20, CBlock, FICON/FICHIP/Cache Blit, Copper, polices, palette, C2P, AGBO, fin de cycle Screen/End et interactions post-Swap.
- **Audit statique :** sources relues et défauts/risques séparés. Aucune assertion de corruption confirmée par Runtime.
- **Exécution :** **aucune** Gate A/B/C/D nouvelle pendant cet audit.
- **Correctifs :** **aucun**. Le développement reste gelé, conformément au plan de l'auteur.

L'audit ne pourra être clos que lorsque **chaque commande** a un statut `conforme` / `anomalie identifiée` / `validation manquante` appuyé par une preuve *native liée* et un test approprié. Pour l'instant la majorité est en `validation manquante`.
