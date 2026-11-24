# Audit AGA — passage 9 : chaîne de preuves Runtime/Compiler et critères de clôture

**24 novembre 2026 · `main` uniquement · source auditée `edccbbd26362fa5e954c8aefe856fe7e7bad583f`.** Aucune nouvelle Gate A/B/C/D n'a été exécutée durant cet audit. **Sources natives, deux bibliothèques, ASC de tests et journaux originaux intouchés ; chantier Sprite S1-P1e GELÉ.**

Ce rapport examine des **fichiers de preuve existants** en les reliant aux **programmes ASC exacts** et aux défauts trouvés statiquement. Un PASS d'un banc particulier **ne vaut pas** une validation de toutes les commandes ni d'une autre bibliothèque.

## 1. État exact des bibliothèques : ne pas inverser les fichiers

| Référence | Chemin courant | Octets | SHA256 fichier | Git blob du fichier |
|---|---|---:|---|---|
| **P2d à auditer / LAST_GOOD protégée** | `dist/AMOSPro_AGA_LAST_GOOD.Lib` | **136 020** | `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` | `8a849b89aae57c2cda0b4db8771034a0978d3e78` |
| **S1-P1e Sprite candidate, GELÉE** | `dist/AMOSPro_AGA.Lib` | **142 000** | `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106` | `5a3605e8347f4ef6cc5c18f1f31826acace8b303` |

**La Lib active dans `dist/` n'est plus P2d.** Les historiques R27/R66/R82/R88 et la [promotion P2d du 21/11](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md) sont des documents datés : leurs expressions « active »/« LAST_GOOD identiques » s'appliquent à leur commit historique, **pas à l'état courant**.

Le [`tests/current/README.md`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/current/README.md) dit encore explicitement que « Lib P2d et LAST_GOOD P2d protégées et identiques depuis la promotion ». **Cette phrase est devenue fausse pour `main` depuis la livraison S1-P1e.** Ce README se trouve dans le répertoire des tests gelés : **ne pas le modifier pendant l'audit** ; la présente note constitue la correction opératoire et devra être réconciliée lors d'une autorisation ultérieure. **AGA-012 — P2 documentation/identité binaire** ; aucun défaut du moteur imputé.

## 2. Registre vérifié des preuves primaires disponibles

Fichiers conservés **tels quels**, sans remplacement ni réécriture. Git blob SHA ≠ SHA256 du contenu.

| N° | Banc, source, mode | Fichier original Git / Git blob | Observations probantes | Portée et limite |
|---|---|---|---|---|
| E01 | P2 ALL IN ONE, **Runtime WinUAE**, `PRG_STATE 1` | [`M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT) ; `4bf3931fbaf487f7cee92b0768c22e925f981fe2` ; **1 632 octets CRLF** | `SOURCE_TAG P2_FULL_V1_20261121` ; `RESULT 1 ERR 0`, `VALID_SAMPLES 240`, `SWAPS 252`, **121 refus / 121 récupérés**, `CLOSE_RETURNED 1`, PASS | Gate **B PASS du seul ASC P2**, **pas** de IFF/Back Fill/Pattern/Bank changes |
| E02 | Même source, **vrai AMOS Compiler**, `PRG_STATE -1` | [`M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT) ; `caeb6f02e7d5a4ba53d3845a311e1de921233ff8` ; **1 633 octets CRLF** | `SOURCE_TAG` identique, `RESULT 1 ERR 0`, `VALID_SAMPLES 240`, `SWAPS 252`, **121/121**, `CLOSE_RETURNED 1`, PASS | Gate **C PASS de cette campagne**, indépendamment de B |
| E03 | P2e.1 AMAL, Runtime, **échec initial** | [`M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/evidence/M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT) ; `841e57401aa2d184a075b7fea191d9556d8dfdf6` ; **567 octets** | `RESULT 0 ERR 15 FRAME 2 VALID_SAMPLES 1 SWAPS 2`, `CLOSE_RETURNED 1 VERDICT FAIL` | **FAIL conservé**, la reprise ultérieure ne l'efface pas |
| E04 | P2e.1 AMAL, Runtime, **nouvelle exécution avec reprise** | [`M19_P2E1_AMAL_RUNTIME_PASS_RETRY_2026-11-21.TXT`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/evidence/M19_P2E1_AMAL_RUNTIME_PASS_RETRY_2026-11-21.TXT) ; `c19f7de1029174e8bbfc01eb1389d058ffcc17c3` ; **769 octets** | `RESULT 1 ERR 0 VALID_SAMPLES 240 SWAPS 241`, **120 refus / 120 récupérés**, PASS | Confirme un scénario de reprise fonctionnel, ne prouve pas la cause d'E03 |
| E05 | P2e.0 AMAL bridge, Runtime | [`M19_P2E0_AMAL_BRIDGE_RUNTIME_2026-11-21.TXT`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/docs/evidence/M19_P2E0_AMAL_BRIDGE_RUNTIME_2026-11-21.TXT) ; `a3f29214ea067a1a2ac24ce71097242d8862cf2e` ; **397 octets** | `RESULT 1 ERR 0 VALID_SAMPLES 240 SWAPS 241`, `CLOSE_RETURNED 1`, PASS | Preuve historique bridge seulement |
| E06 | P2 EDGE 20×18 / SwapVBL 20×18, résultats **rapportés** | [`README_EDGE_SAFE.md`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/proto/rpg_bob_dim/README_EDGE_SAFE.md) et [`README_SWAP_EDGE.md`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/proto/rpg_bob_dim/README_SWAP_EDGE.md) | EDGE FAIL rapporté `ERR 15 FRAME 221` ; **111 refus / 110 récupérés** ; **123 contrôles du pixel (19,17) corrects**. SwapVBL PASS rapporté sans refus | **TXT originaux absents de Git** : niveau de preuve inférieur aux E01–E05 ; ne pas fabriquer de logs ni inférer Compiler PASS |

**Asc source exact P2 :** [`tests/current/M19_P2_ALL_IN_ONE.asc`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/current/M19_P2_ALL_IN_ONE.asc), **25 056 octets**, Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`, identique au [`examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc). Les fichiers E01 et E02 donnent `SOURCE_TAG P2_FULL_V1_20261121` ; la procédure [`tests/current/README.md`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/current/README.md) consigne leurs SHA256 et leur provenance. **Leur texte n'enregistre pas un SHA de Lib chargée en Amiga à chaque lancement** : l'association à P2d vient de la qualification et des preuves de livraison, **non d'une mesure intégrée à chaque journal**. Ne pas transformer une constante de test en mesure runtime.

## 3. Ce que signifie exactement `ERR 15` dans le prototype RPG

Dans [`P2_EDGE_20X18.asc` lignes 256–280](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/proto/rpg_bob_dim/P2_EDGE_20X18.asc#L256-L280) :
1. `Aga Swap` est appelé ; si retour différent de 1, le programme incrémente `SWAP_REFUSALS`.
2. Il essaie au plus **quatre fois**, chaque fois après `Aga Wait Vbl`, d'obtenir un retour 1.
3. Si tous les essais échouent, **le code du banc lui-même affecte `_ERR=15`** puis va au nettoyage. Ce n'est **pas** une exception OS ou un code d'erreur renvoyé directement par la bibliothèque.
4. [`ERR 81` et `ERR 82`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/proto/rpg_bob_dim/P2_EDGE_20X18.asc#L323-L348) sont les erreurs explicites de CBlock Capture et de valeur pixel de bord, distinctes d'`ERR 15`.

Le rapport EDGE indique que les **123 contrôles de pixel ont réussi avant le refus de Swap non récupéré à la frame 221**. Il serait donc incorrect d'attribuer le résultat EDGE à un défaut de pixel opaque ou à un CBlock corrompu. **Mais ce résultat ne départage pas** un Safe pending non acquitté, un B8 DIRTY, un refus du Swap OS ni une autre condition d'Update. **AGA-002 reste une piste structurelle native P1, pas une attribution certaine de cette panne EDGE**.

Le banc P2 officiel [lignes 134–152](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/edccbbd26362fa5e954c8aefe856fe7e7bad583f/tests/current/M19_P2_ALL_IN_ONE.asc#L134-L152) initialise par **`Aga Blit Fill` les deux fonds physiques avant les Bobs** : son succès E01/E02 **ne couvre pas** le premier Bind B8 après Open/Swap sans Fill ni le chargement de décor IFF immédiatement après Swap.

## 4. Correspondance des 19 scénarios aux preuves existantes

**Important :** pour chacun de T01–T19, « campagne actuelle » = **NON EXÉCUTÉE** au cours de cet audit. La colonne historique ci-dessous indique seulement ce que les anciens journaux couvrent partiellement.

| Test | Correspondance des preuves anciennes | Ce qu'il reste obligatoirement à vérifier |
|---|---|---|
| **T01** Open et premier Swap | P2 ASC fait Open, DB et Swap mais prépare par Fill | Swap initial **sans Fill**, message Safe présent/absent |
| **T02 A–E** premier Bind B8 | E01/E02 couvrent des Swaps sur pool préparé ; E06 donne une différence VBL | Premier Bind **pool absent**, GetMsg et refus attribué à Safe vs B8 |
| **T03** Clear→décor→Swap | Comportements B8 de vieux bancs, aucun crossover complet | Fond nouveau sur **chacune des pages**, sans restauration d'ancien snapshot |
| **T04** Swap→IFF immédiat | Aucun essai E01–E06 | P0 Safe sur IFF, write back et palette séparée |
| **T05** Safe pending/reprise | E01/E02 : 121 refus récupérés, sans instrumentation DB/GetMsg | Safe absent/arrivé/acquitté, Disp conservé, retry conditionnel |
| **T06** writers croisés et Screen Pattern | E01/E02 couvrent Blit Fill et quelques dessins | Writer par writer après Swap, **Pattern sur vrai Screen.RastPort** |
| **T07** référence P2 ALL IN ONE | **E01 et E02 PASS historique sur ASC exact** | Rejouer seulement après correctif autorisé, mesurer SHA Lib installée |
| **T08** CLEAN/READY/DIRTY | Logs E01/E02 ne publient pas ces états internes | Transitions injectées et rollback après erreur |
| **T09** font/palette/B8 | Aucun log de ce croisement | ColorMap seul vs pixels B8, font ownership et Close |
| **T10** banques / Chip / reload | Anciennes Gates Bank Free et diagnostic R88 (autres binaires) | Validation P2d après Erase/Load externe, cache/owner/stamp |
| **T11** FICON/FICHIP/AGPC/B8 | Gates M18 historiques (autres binaires) | Restaging/ready/Chip et Clear/Swap avec P2d |
| **T12** IFF malformé et transaction | Aucun log E01–E06 | BODY première/deuxième passe, plans et palette au refus |
| **T13** CBlock / Safe / DB | E01/E02 pixels de Bob et CBlock ; E06 EDGE pixel | CBlock sur bitmap changeant, Safe pending, refus et publication |
| **T14** Close/End/Open | E01/E02 et E03/E04 : `CLOSE_RETURNED 1` | Callback, propriétaires B8/C2P/Copper/Font, ABA et State LEA |
| **T15** Sprite | Gate A S1 historique distincte | **SUSPENDU**, B/C/D non exécutées |
| **T16** Copper | Anciennes Gates R18 distinctes | Actif/rétablissement/Close dans P2d et réouverture |
| **T17** RPG décor IFF / premier Bob | E06 RPG simplifié : **pas d'IFF ni ABK externe** | Scénario RPG **réel** avec IFF, bank et premier Bind |
| **T18** EDGE/SwapVBL | E06 : PASS/FAIL **rapportés**, logs non archivés | Variante combinée EDGE+preSwap VBL, Compiler, cause exacte ERR15 |
| **T19** Back Fill après Swap | Aucun essai E01–E06 | Garde Safe inexistante (statique P0), pixel/front sous exécution encadrée |

**Bilan de couverture :** E01/E02 apportent un seul PASS B et un seul PASS C sur le programme intégré exact. E03 est un FAIL important conservé. Les comptes rendus E06 ne remplacent pas les journaux originaux. **Aucun des 19 nouveaux scénarios transversaux n'a sa nouvelle Gate B/C acquise.**

## 5. Hiérarchie de preuve et conditions pour fermer chaque anomalie

| Classification cible | Preuve minimale acceptable | Ce qui ne suffit pas |
|---|---|---|
| **P0 statique sécurité** | Entrée AP20 exacte + instruction d'écriture/DMA + démonstration qu'aucun GetMsg/contrôle Safe ne la précède ; puis Gate A CPU simulant Safe absent/arrivé | Une capture écran normale ou un PASS intégré après Fill |
| **P0 Runtime confirmé** | Scénario WinUAE reproductible, source ASC exacte, état Safe/bitmaps établi, preuve réelle d'accès non Safe/corruption | Déduire corruption d'un manque de garde dans le code seul |
| **P1 progression confirmée** | Trace Gate A premier Bind refusé avec message disponible mais non acquitté, comparaison témoin GetMsg ; reproduction B selon instrumentation sûre | `ERR 15` seul, nombre de VBL, ou succès d'un autre banc |
| **P1 interaction B8** | Scénario **dans le contrat Clear→décor→Swap** perdant le fond, CRC/index sur les deux pages, owner/snapshot comparés | Dessin sans Clear (hors contrat) |
| **P1 cycle de vie** | Close/End/échec/réouverture avec suivi allocation/free/owner et éventuellement même adresse OS réutilisée | `CLOSE_RETURNED 1` seul |
| **VM → Conforme** | Code natif **effectivement lié** revu, conditions d'erreur couvertes, Gate A/B/C utiles et logs complets, SHA du **binaire réellement testé** | Inventaire API, builder existant ou anciens PASS d'une autre version |
| **CI/protocole P2** | Identités de fichiers et SHA vérifiés, conservation des 7 LEA Input State, HUNK/AP20, absence de mutation d'ASC validé | Élargir arbitrairement la liste SHA pour obtenir du vert |

La clôture de l'audit **n'exige pas que toutes les commandes soient PASS** : elle exige un statut individuel **conforme / anomalie identifiée / validation manquante** et une preuve/limite pour chacune, puis une décision explicite de correction et de Gates. **La clôture de la réparation** exige ensuite les Gates et la non-régression P2d dans les modes concernés. Les deux événements sont distincts.

## 6. Ordre proposé après décision (aucune correction appliquée)

1. **P0 avant P1 :** SafePort commun ou gardes des écrivains directs `IFF Load`, `Back Fill`, et évaluation du `Screen Pattern` après Swap.
2. **B8** : acquisition Safe avant premier Bind / progression sans blocage et transitions READY/DIRTY, sans changer l'ordre de publication du Swap.
3. **Snapshots/banques** : conserver l'obligation Clear→décor→Swap ; tester la sécurité des changements de ressources externes sans transformer les opérations hors contrat en tests de conformité.
4. **Lifecycle** : C2P, polices, Copper, B8, Close/End et réouverture avec ownership et génération, ainsi que les 7 LEA clavier/souris.
5. **Validation** : source ASCII → Gate A MC68020/ABI/CPU + tests négatifs → WinUAE Runtime Gate B → vrai Compiler Gate C → **aucune promotion de LAST_GOOD avant autorisation**, Sprite S1 toujours gelé.

**Aucune nouvelle bibliothèque ni correction native/CI ni test lancé.** Préserver les preuves E01–E06, y compris le FAIL E03, les fichiers `tests/current/`, `tests/passed/` et `tests/proto/`.

## 7. Complément passage 10 — qu'établit réellement `CLOSE_RETURNED 1` ?

[Revue Close/End et source exacte du banc](AUDIT_AGA_CLOSE_END_RESSOURCES_2026-11-24.md). Dans `tests/current/M19_P2_ALL_IN_ONE.asc`, `_CLOSE_RETURNED=1` est écrit immédiatement après `Aga Screen Close`, et **sans contrôle de ressources**. Ce champ prouve le **retour à l'ASC**. Il ne prouve pas le bilan Alloc/Free, le détachement réel des ports Safe/Disp, la destruction C2P/Chip, les hooks B8 ni l'état de réouverture ; ce sont des points T14 encore sans Gate B/C dédiée. **AGA-013 P2 (test/oracle, pas moteur) ; aucune requalification des PASS originaux E01/E02.**
