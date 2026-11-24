# Audit AGA — cahier de non-régression transversal (scénarios non exécutés)

**Établi le 23 novembre 2026** — dépôt `anthea176/AMOSPro-AGA-Extension`, branche `main`, **HEAD source audité `45516f8772a24b5d7ad887d2a0f2b7cee5203e98`**. **Aucun test nouveau lancé / aucune Lib modifiée.**

Ce document fixe les campagnes **avant** de programmer des sondes. Les scénarios ci-dessous sont des *spécifications*, pas des programmes AMOS exécutables. Les versions et syntaxes exactes seront dérivées des bancs validés, pas inventées depuis ce texte.

## Préconditions, provenance, Gates

- **Référence P2d** : `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, **100 commandes**. À utiliser sur environnement WinUAE isolé pour diagnostiquer le socle 2D.
- **S1-P1e conservée mais gelée** : `dist/AMOSPro_AGA.Lib`, 142 000 octets, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`, 102 commandes ; aucune Gate B/C Sprite.
- Préciser CPU MC68020 minimum, configuration WinUAE chipset AGA, profondeur 1..8, OS, version de Compiler, banque et IFF effectivement installés. Aucun paramètre incertain ne sera présenté comme connu.
- **Gate A** : simulation native Exec/Graphics/B8, SafePort absent/arrivant, bits de DB, retour D3/D2, absence de DMA et respect ABI. Ce n'est **ni WinUAE ni Amiga Compiler**.
- **Gate B** : AMOS Professional Runtime WinUAE, programme exact, `Prg State=1` dans les journaux historique ; noter explicitement `0` si mode interprété pur testé.
- **Gate C** : exécutable produit par **vrai AMOS Compiler**, `Prg State=-1`, même programme et mêmes assets, sans reprendre automatiquement le PASS B.
- **Gate D** : Amiga AGA physique, hors portée actuelle ; ne jamais l'annoncer PASS.
- **Gel strict** : ne pas ajouter de tests sous `tests/current/` et ne pas modifier de Lib tant que le protocole, le bilan d'audit et l'autorisation spécifique ne sont pas validés.

## 19 scénarios à implémenter, comparer et journaliser (T19 ajouté le 24 novembre)

| ID | Scénario | Séquence minimale | Variantes / injection | Gates | PASS attendu | FAIL / alerte |
|---|---|---|---|---|---|---|
| T01 | Open / premier Swap sans Fill | Aga Screen Open → Double Buffer → Swap ; sans aucune écriture préliminaire | Sans Bob actif ; Safe initial disponible / pending | A,B,C | Swap publié légalement ou refus sûr ; jamais de page avant altérée ; état récupérable | Tenter un Swap sans aucune acquisition de Safe ou le confondre avec Bob Update |
| T02 | Premier Auto Update avec Safe pending **(5 variantes A–E)** | A : premier Swap sans Bob ; B : au moins 1 Bob, Auto Update(1), pool B8 absent, Safe pending, **VBL puis Swap sans acquittement** ; C : même cas avec **GetMsg par Blit Fill protégé** avant Swap ; D : Safe pending, notification absente ; E : pool déjà initialisé | Conserver DB+20, owner, statut CLEAN/READY/DIRTY, D3, appels GetMsg/ChangeScreenBuffer/WaitBlit ; distinguer **premier Bind** et régime établi | A,B,C | A : voie directe Swap atteignable ; B : résultat et origine de chaque refus consignés, aucun accès non-Safe ; C : en présence des mêmes autres prérequis valides, progression après acquittement ; D : refus 0 légitime sans écriture ; E : fonctionnement du service Safe après Bind mesuré | Refus inexpliqué après acquittement, boucle indéfinie, DMA non Safe, confusion entre échec Bank et Safe ; **aucune variante non exécutée ne vaut PASS** |
| T03 | Décor modifié avec Bobs **dans le contrat P2d** | Fond A + Bob Update/Swap → retour sur page arrière contenant Bob → **Aga Bob Clear réussi** → modification du décor B par Blit Fill/Plot → Aga Swap en Auto Update | Snapshot valide page 0/1, Bob On/Off ; **contrôle négatif séparé : dessin sans Clear = hors contrat** | A,B,C | Clear restaure l'ancien fond, le décor B est capturé comme nouveau fond, les pixels restent après Swap et futur Clear/Update ; deux pages cohérentes | Perte du décor B **malgré Clear réussi** ou snapshot incohérent = P1 à confirmer ; perte après dessin **sans Clear** non suffisante pour déclarer un bug |
| T04 | IFF Load directement après Swap (P0 Safe) | Open/DB → Swap réussi → vérifier DB+20 bit0 pending → Aga Iff Load sur ILBM témoin distinct **sans Blit Fill ni GetMsg préalable** ; contrôle avec Blit Fill protégé et Safe acquis avant IFF | Safe pending sans message, message arrivé mais non acquitté, puis GetMsg effectif ; garder les identités physiques front/back et CRC des plans | A,B,C | **Critère de sécurité visé (pas comportement P2d garanti)** : aucun BODY écrit sur page non Safe ; IFF ne doit modifier que le back sûr ; palette RGB32 observée séparément sur ColorMap commun | Atteinte du chemin d'écriture BODY tandis que DB+20 bit0=1 = violation de discipline Safe statique ; pixel avant ou plans non Safe modifiés = FAIL de sécurité ; ne pas confondre avec changement de palette |
| T05 | Refus puis reprise et comptage Safe | Enregistrer DB flags → commande graphique → GetMsg non disponible → VBL → nouvel essai | Safe pending, puis notification disponible / retardée, Disp simultanément pending | A,B,C | 0 sans DMA tant que notification absente ; retour correct après arrivée ; Disp flag conservé ; aucun verrou infini | WaitVbl traité comme acquittement sans GetMsg ou flag Disp effacé |
| T06 | Écritures croisées sans Bobs | Après chaque Swap, Blit Copy/Fill/Clear, Text, Plot/Draw/Box/Circle, AGAPIC Draw, F Blit, C2P Convert | Chaque writer isolé avec/ sans Safe, clipping négatif/bord, profondeur 1..8 selon API | A,B,C | Safe identique pour tous, front immuable, pixels et plans attendus, aucun résultat 1 trompeur | Une seule commande écrit sur ancienne page affichée ou contourne Safe |
| T07 | Régression intégrée P2d existante | Relancer inchangé tests/current/M19_P2_ALL_IN_ONE.asc sous P2d exacte | 240 frames, 2 AMAL/Bobs, modes plans, Flip, collisions, Close | B,C | RESULT 1, ERR 0, VALID_SAMPLES 240, CLOSE_RETURNED 1 ; refus bornés et tous RECOVERED ; chiffres 121/121 historiques mais non exigés partout | Échec pixel ou refus non récupéré ; ne pas modifier le test pour obtenir PASS |
| T08 | B8 DIRTY/READY/CLEAN sous échec | Provoquer refus Update (source banque invalide, Safe non acquis), puis Clear, Update, Swap | Pool lié/non lié, snapshots absents/valides, motif de refus conservé | A,B,C | DIRTY interdit Swap ; état récupérable uniquement par chemin autorisé ; READY persiste après refus du Swap OS ; aucun pixel partiel | Remettre CLEAN de façon aveugle après erreur et présenter une frame incomplète |
| T09 | Police / palette et snapshots B8 — séparer index et RGB | Séquence Clear → décor → Bob Update/Swap avec police OS et BankFont AMCAF ; puis **Palette Set/Bank Apply/Cycle seules sans nouveau dessin**, et relevé des mêmes pixels indexés/ColorMap | Palettes RGB24 distinctes, bitmaps avant/arrière physiques, bank font remplacée, Erase source AMCAF après copie et nouveau Close | A,B,C | Les index de pixel et snapshots B8 restent identiques sous **palette seule** ; RGB change sur les deux pages ; Clear requis seulement avant changement de pixels du décor ; police précédente libérée sur remplacement | Index modifiés par commande palette seule, snapshot restauré incorrectement, police libérée trop tôt/dangling, couleur apparente confondue avec changement de pixels |
| T10 | Banques AGBO, cache Chip et rechargement externe | Bank Select/Mask/Save/Load ; **Aga Bob Bank Free en CLEAN**, puis re-sélection ; refus READY/DIRTY ; variante négative Erase Bank/Load externe même numéro, éventuelle adresse réutilisée ; AGAPIC capture et FICON stage isolés | Bank DATA AMOS conservée par Bank Free, TypeOfMem/owner, stamps, 64 Bob slots, variantes P2b, snapshots B8 | A,B,C | Libération Bank Free ne détruit pas DATA AGBO, désactive seulement la banque cible et attend fin DMA ; re-sélection recalcule son cache ; toute banque morte/refus doit éviter déréférencement | Use-after-free, cache Chip réutilisé après remplacement sans revalidation, double free, banque différente altérée ; ne pas conclure sur Poke/Erase hors contrat sans protocole distinct |
| T11 | Caches FICON/AGPC et Bobs | FICON8 → FICHIP8 → F Blit/Cache Blit → Swap avec Bobs actifs | Banque en Chip, clips, Bob snapshot présent et absent | A,B,C | WaitBlit avant libération, pixels corrects, écriture autorisée sur back Safe, snapshot cohérent | DMA sur Fast, cache libéré prématurément, changement de décor perdu |
| T12 | IFF malformé : première/deuxième passe et ColorMap | BODY ByteRun1 court/long, CMAP/BMHD incohérents, contrôle d'entrée ILBM ; comparer **plans et ColorMap séparément** avant/après refus, puis IFF valide après Safe acquis | Sans Bob puis avec B8 snapshot ; input BODY privé inchangé entre passes ; vérifier absence d'écriture lors du premier parsing et de l'allocation palette | A,B,C | Rejet malformed avant phase d'écriture ; image et palette conservées si refus précède l'écriture ; si échec tardif démontré, documenter explicitement l'absence de rollback et l'état exact | Mutation de plans sur échec de prévalidation, palette altérée au refus, deuxième passe divergente réellement reproduite, écriture hors bornes ; **AGA-007 non avérée sans preuve** |
| T13 | CBlock Capture/Draw/Restore avec refus Safe | Capture avant Swap → Swap → Draw/Restore sur back changé ; variante Capture avec Safe pending + GetMsg absent, puis présent | Méthode CPU8/CPU16/Blitter ; alignement 8/16px, bornes, profondeur, snapshot Bob ; vérifier pointeurs et dernière coordonnée capture | A,B,C | Refus Safe sans copie/coordonnées publiées ; puis Capture valide, Draw/Restore sur le bon back ; WaitBlit et pixel 0 opaque selon contrat | Capture lit le front, publie les coordonnées sur refus Safe, Restore écrit sur bitmap non Safe ou restaure le mauvais fond |
| T14 | Fermer/rouvrir et End — avec et sans callback B8 | A : Open/DB → Close **sans aucun Bob ni root B8** → Open ; B : Open/Bob/B8/C2P/Copper/Font → Close → Open ; C : Close refusé avec Safe/Disp pending puis récupération ; D : End avec callback enregistré | Owner/pool et Bitmap OS réutilisant la même adresse ; fonts OS/BankFont, Copper actif ou erreur d'installation, C2P actif ; tracer vrais appels Close, FreeMem, font release et postclose | A,B,C | A : ancien Close invoqué malgré root B8 nul ; B/D : callback et ressources nettoyés une seule fois ; C : écran encore vivant et ressource retenue sur refus, récupération sûre ; nouvel écran indépendant | Écran resté ouvert malgré Close sans Bob, double Free, callback/root stale, vieille police/bitmap considéré valide après réouverture |
| T15 | S1-P1e Sprite — GEL | Aga Sprite Bank / Get AGA Sprite, impact des futurs changements de Safe | S1-P1e candidate préservée ; aucune installation/test | A,B,C | Aucun résultat nouveau ; reprendre seulement sur autorisation distincte après P2d corrigée | Ne pas déclarer PASS B/C/D ni produire un nouveau binaire |
| T16 | Copper activation, échec et retrait conservateur | Clear → Wait/Move → End → On → Off → Swap/Close ; injecter échecs MakeScreen et RethinkDisplay sur On puis Off, retenter Off, Close | UserCopperList possédée et liée au Screen ; vérifier bit actif positionné avant appels OS comme prévu R18, rollback UCopIns/Screen.UserData et absence de libération anticipée | A,B,C | Après échec On, édition bloquée jusqu'à Off ; après échec Off, liste conservée pour nouvel essai ; retrait réussi puis FreeCopList/FreeMem une seule fois | Écriture Copper malgré activation incertaine, UCopIns détachée mais mémoire libérée sous l'affichage, double free ou interférence avec Close |
| T17 | RPG : premier décor IFF et Bind Bob sans Fill artificiel | Open → DB → Swap → **IFF Load directement**, puis Bob Bank/Mask → Bob Auto Update → Swap/animations ; témoin identique avec Blit Fill protégé acquittant Safe avant IFF et premier Bind | ROOT B8 absent/existant, Safe pending, deux pages physiques, ERR 15 historique, ColorMap globale ; conserver journaux FAIL/PASS d'origine | A,B,C | Page back sûre avant écriture du décor, premier Bind B8 progressant quand Safe est acquis, snapshots et palettes cohérents, aucune ERR non récupérée ; comparer Runtime et Compiler exacts | Refus coincé sans GetMsg, écriture IFF sans Safe, image divergente entre pages ou root B8 jamais lié ; ne pas attribuer automatiquement ERR 15 à une seule cause |
| T18 | RPG bord opaque / VBL différentiel | Comparer P2_DIM_20X18, P2_EDGE_20X18, P2_SWAP_VBL_20X18 et P2_EDGE_SWAPVBL_20X18 sans modifier leur source | Côté arrière local (19,17), compteur refus Swap, Safe et DIRTY | B,C | Conserver échecs et succès séparés, comptages cohérents ; si un refus dépasse 4 tentatives, cause attribuée par instrumentation | Classifier un pixel valide comme succès de tout le programme ou confondre ERR15 et erreur interne |
| T19 | Back Fill legacy **SetRast(-234)** après Swap | Open/DB → Swap réussi → DB+20 bit0 pending → **Aga Back Fill couleur** sans commande acquittant Safe ; comparer avec Aga Blit Fill protégé | Message Safe absent, puis disponible non consommé, puis acquitté ; inspecter les deux BitMaps et les appels graphics SetRast/WaitBlit | A,B,C | **Critère de sécurité visé** : aucun SetRast sur bitmap non Safe, page avant intacte, reprise après Safe acquis ; Back Fill est une instruction sans retour (ne pas attendre de valeur 0/1) | Atteindre **SetRast(-234)** sous pending non acquitté = violation Safe, même si l'image paraît correcte ; altération du front ou d'une page réellement non Safe = FAIL matériel |

**Statut général de T01–T19 dans cet audit : NON EXÉCUTÉS.** T07 et T18 réutilisent des **preuves historiques** ci-dessous, sans les requalifier automatiquement pour la nouvelle matrice. T15 est **SUSPENDU**.

## Matrice de variantes obligatoires pour chaque commande liée à l'écran

| Axe | Valeurs à couvrir | Observables nécessaires |
|---|---|---|
| Position dans le cycle | Premier appel après Open ; immédiatement après Swap sans Fill ; avant/pendant Bob Update ; après plusieurs swaps | Front index, physical Back BitMap*, compteur présentation |
| SafePort | Déjà acquis ; pending et GetMsg vide ; message arrivé ; Safe+Disp pending | `DB+20` avant/après, port consulté, GetMsg retourné, aucun pixel non Safe touché |
| Bobs | 0 actif / 1 actif / 2 actifs / 64 actifs ; sans pool / pool initialisé | B8 owner et epoch, transitions CLEAN/READY/DIRTY, retour fonction |
| Snapshot | absent / valide page 0 / valide page 1 / invalide / après édition du décor | Valid-mask, CRC ou échantillons des deux fonds, Restore effectivement effectué |
| Erreur | Banque absente, données invalides, mémoire insuffisante, refus Safe, Close partiel | Aucun overflow, allocation relâchée, pas de succès partiel, récupération possible |
| Cycle de vie | Close simple, double Close, réouverture, End, identité OS réutilisée | Aucune référence Chip/Screen périmée, Frees équilibrés |
| Mode | Runtime B, Compiler C ; CPU et OS explicitement renseignés | SHA256 Lib **réellement installée**, `PRG_STATE`, source tag et identifiant du scénario |

## Contenu minimal d'un journal de test futur

Chaque nouveau programme devra consigner **exactement** les champs qu'il produit ; ne pas lui attribuer des champs absents. Contrat de journal recommandé :

```text
SOURCE_TAG <identifiant unique de l'ASC>
LIB_SHA256 <mesure externe ou VERIFIED_BY_HOST, jamais une valeur constante présentée comme mesure>
PRG_STATE <0|1|-1>
RUN_MODE <INTERPRETED|RUNTIME|COMPILED>
TEST_ID Txx
RESULT <0|1>
ERR <code explicite ou zero>
FIRST_FAILED_STEP <etape>
FRAME <numero>
SWAPS <nombre>
SWAP_REFUSALS <nombre>
SWAP_RECOVERED <nombre>
SAFE_PENDING_BEFORE <0|1>
SAFE_PENDING_AFTER <0|1>
B8_STATUS_BEFORE <CLEAN|READY|DIRTY|N_A>
B8_STATUS_AFTER <CLEAN|READY|DIRTY|N_A>
PIXEL_CHECKS <nombre>
PIXEL_MISMATCH <nombre>
CLOSE_RETURNED <0|1>
VERDICT <PASS|FAIL>
```

Les champs de diagnostic internes `SAFE_PENDING_*` et `B8_STATUS_*` nécessitent une **instrumentation de Gate A ou un accès de sonde sûr et validé** ; ne jamais lire aveuglément les offsets mémoire ou fabriquer des valeurs par défaut. En Runtime, un banc dépourvu de ces mesures doit indiquer `N_A`, pas attribuer la cause à Safe ou DIRTY.

## Interprétation des résultats

1. **Écriture sans Safe** = FAIL critique, même si un screenshot final semble correct.
2. **Retour 0 légitime** et sortie propre peuvent être PASS d'un scénario de refus ; à distinguer du FAIL d'une présentation valide jamais récupérée.
3. Une erreur avec page **partiellement modifiée** est FAIL si le contrat prévoit un refus atomique.
4. Après READY, un Swap OS refusé doit conserver une frame prête ; après DIRTY, aucun Swap ne doit présenter une frame partielle.
5. Échec Runtime et succès Compiler (ou inversement) = **anomalie indépendante**, pas un PASS croisé.
6. Résultat **pixel seul PASS** ne vaut pas scénario PASS si `ERR` ou `RESULT` global indique FAIL.
7. Temps de VBL ajoutés uniquement pour diagnostic : pas de conclusion sur le framerate.

## Preuves existantes, non transférables

| Banc déjà exécuté | Journal / provenance | B | C |
|---|---|---|---|
| `M19_P2_ALL_IN_ONE.asc` P2d exact | [Runtime original](evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT) et [Compiler original](evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT) ; 121 refus et 121 récupérations | PASS historique | PASS historique |
| P2e.1 ancien AMAL | [FAIL initial](evidence/M19_P2E1_AMAL_RUNTIME_FAIL_ERR15_2026-11-21.TXT) et [PASS avec reprise](evidence/M19_P2E1_AMAL_RUNTIME_PASS_RETRY_2026-11-21.TXT) | FAIL puis PASS distincts | Non inféré |
| P2_DIM 16/20, P2_SWAP_VBL 20x18 | [Compte rendu](../tests/proto/rpg_bob_dim/README_SWAP_EDGE.md) et [EDGE_SAFE](../tests/proto/rpg_bob_dim/README_EDGE_SAFE.md) | PASS rapportés, TXT non archivé | Non inféré |
| P2_EDGE_20X18 | [Compte rendu](../tests/proto/rpg_bob_dim/README_EDGE_SAFE.md) | FAIL rapporté frame 221, `ERR 15`, 111 refus/110 récupérations ; 123 pixels bord OK | Non inféré |
| P2_EDGE_SWAPVBL_20X18 | [Prototype](../tests/proto/rpg_bob_dim/P2_EDGE_SWAPVBL_20X18.asc) | **Non testé** | **Non testé** |

## Règles de livraison des preuves

Les journaux et sources de PASS/FAIL déjà présents dans `docs/evidence/`, `tests/passed/` et `tests/proto/` sont **immutables**. Les journaux RPG manquants doivent être récupérés tels quels auprès de leur source (taille, horodatage, SHA si disponibles) **sans reconstruire leur contenu de mémoire**. Les nouvelles campagnes resteront en prototype jusqu'à autorisation distincte.

**Aucune nouvelle commande native, aucune correction, aucun lancement de test et aucune promotion de Lib** ne sont autorisés par ce document.

[Rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Matrice des 102 commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md)

## Ajout 24 novembre 2026 — provenance T19

T19 découle du lien AP20 réel de `Aga Back Fill` : [index 22 → UNIT142+$00C9E](AUDIT_AGA_AP20_LIAISONS_P2D_2026-11-24.md), contrairement à `Aga Blit Fill` qui possède le garde Safe dans la routine native. Cette absence de garde était **déjà documentée dans R27**, mais n'était pas isolée par un scénario du présent cahier. **T19 est uniquement une spécification, non un ASC écrit ou un test lancé.** Il ne saurait autoriser une écriture risquée sur matériel physique ; toutes les prochaines sondes nécessitent un accord distinct.

## Requalification T03 — 24 novembre 2026

[Contrat officiel P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md) : `Aga Bob Clear` → dessin du décor → `Aga Swap`, Auto Update actif. La [transaction B8](../tools/m19_b8_clear_update_tx_emit.py) emploie `cleared` pour **empêcher la restauration d'un vieux snapshot** après un Clear réussi. La variante « modifier le décor sans Clear préalable » est **un contrôle hors contrat**, non un FAIL à attribuer automatiquement à l'extension. T03 reste **non exécuté** dans ses deux variantes ; aucun statut Gate B/C nouveau.

## Affinement T02 — 24 novembre 2026, passage natif AGA-002

Le premier `Aga Swap` en Auto Update avec Bob actif passe par `p2d_service_update` puis `L_BOBS_0D738 → L_BOBS_0C51E → L_BOBS_0BE32`. Le garde natif `L_BOBS_0BE32` refuse **`DB+20 bit0 = 1`** sans `GetMsg`. Le Swap original possède une consommation Safe/Disp, mais n'est pas atteint après ce refus. Un simple `Aga Wait Vbl` ne vide pas le port Safe. Les variantes **T02-A à T02-E** séparent la première allocation du pool B8, un pool déjà prêt et l'état du message OS. [Preuves et préconditions détaillées (passage 5)](AUDIT_TRANSVERSAL_AGA_2026-11-23.md#9-passage-5--24-novembre-2026--fermeture-de-la-chaîne-native-aga-002-sans-gate-b).

**Statut T02 A–E : SPÉCIFIÉ, NON EXÉCUTÉ.** Aucun changement de l'ASC actif ni accès direct aux offsets natifs depuis AMOS ; la sonde Safe/DB doit faire l'objet d'un protocole sûr et d'une autorisation distincte.

## Affinements du passage 6 — 24 novembre 2026

[T09/T13/T14/T16](AUDIT_AGA_LIFECYCLE_COPPER_CBLOCK_C2P_2026-11-24.md) reposent sur la lecture des **entrées réellement liées dans P2d**, pas simplement sur les anciens builders. Le test T14 comprend désormais la fermeture **sans Bob ni root B8**, dont le chemin vers l'ancien Close existe statiquement. Le test T16 traite le drapeau « actif avant MakeScreen » comme **fail-safe intentionnel**, et non comme erreur automatiquement comptée. CBlock/C2P refusent les écritures sur page non Safe dans leurs wrappers natifs ; vérifier la coordonnée de capture et le bitmap réel avec T13. Le compteur reste **19 scénarios**, **0 scénario exécuté dans cet audit**.

## Passage 7 — tests affinés (24 novembre 2026)

[Rapport source IFF/Back Fill/AGBO/Palette](AUDIT_AGA_SWAP_IFF_BACKFILL_B8_PALETTES_2026-11-24.md) : `Aga Swap` réussi pose `DB+20=3` (Safe/Disp pending) ; `Aga Iff Load` et `Aga Back Fill` n'ont pas de `GetMsg` local. **La primitive réelle de Back Fill est `SetRast(-234)` et non `RectFill`** (erreur de lecture LVO corrigée). T04/T19 séparent message absent, disponible non acquitté et acquis ; T17 distingue premier Bind sans Fill et témoin ayant acquitté Safe. T09 teste **ColorMap seul sans invalider les plans B8**. T10 sépare Bank Free (cache uniquement, garde CLEAN) des `Load/Erase Bank` externes dont la sûreté reste inconnue. T12 doit établir une divergence réelle des deux passes IFF avant de classer AGA-007 comme anomalie.

**Compteur inchangé : T01–T19 = 19 scénarios, tous NON EXÉCUTÉS pendant cet audit.** Aucune sonde ASC créée, aucun changement des journaux historiques, aucune nouvelle Gate A/B/C.
