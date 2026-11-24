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
| T02 | Premier Auto Update avec Safe pending | Open/Double Buffer → 1er Bob Set → Auto Update(1) → Swap sans Fill | B8 pool non lié, Safe pending sans message puis délivré ; Bob actif | A,B,C | Le premier Bind ne touche aucun plan non Safe ; après notification disponible, nouvel essai possible sans Close forcé | Refus permanent quand la notification existe, ou SavePort jamais acquitté |
| T03 | Décor modifié avec Bobs et snapshot | Fond A dessiné → Bob Update → modification fond B par Blit Fill ou Plot → Clear/Update | Pages physiques séparées, snapshot valide/invalide, Bob On/Off | A,B,C | Le contrat explicite Clear→décor→Update est respecté ; aucun ancien fond A ressuscité après édition valide | Une modification autorisée disparait par Restore du snapshot A |
| T04 | IFF Load après Swap | Open/Double Buffer → Swap → Iff Load immédiatement, sans Blit Fill ni Wait Vbl | Safe pending sans message / message disponible ; IFF indexé valide | A,B,C | Aucune écriture si non Safe ; reprise explicite quand Safe acquis ; image chargée sur back uniquement | Écriture dans le front/non Safe, retour success malgré décodage partiel |
| T05 | Refus puis reprise et comptage Safe | Enregistrer DB flags → commande graphique → GetMsg non disponible → VBL → nouvel essai | Safe pending, puis notification disponible / retardée, Disp simultanément pending | A,B,C | 0 sans DMA tant que notification absente ; retour correct après arrivée ; Disp flag conservé ; aucun verrou infini | WaitVbl traité comme acquittement sans GetMsg ou flag Disp effacé |
| T06 | Écritures croisées sans Bobs | Après chaque Swap, Blit Copy/Fill/Clear, Text, Plot/Draw/Box/Circle, AGAPIC Draw, F Blit, C2P Convert | Chaque writer isolé avec/ sans Safe, clipping négatif/bord, profondeur 1..8 selon API | A,B,C | Safe identique pour tous, front immuable, pixels et plans attendus, aucun résultat 1 trompeur | Une seule commande écrit sur ancienne page affichée ou contourne Safe |
| T07 | Régression intégrée P2d existante | Relancer inchangé tests/current/M19_P2_ALL_IN_ONE.asc sous P2d exacte | 240 frames, 2 AMAL/Bobs, modes plans, Flip, collisions, Close | B,C | RESULT 1, ERR 0, VALID_SAMPLES 240, CLOSE_RETURNED 1 ; refus bornés et tous RECOVERED ; chiffres 121/121 historiques mais non exigés partout | Échec pixel ou refus non récupéré ; ne pas modifier le test pour obtenir PASS |
| T08 | B8 DIRTY/READY/CLEAN sous échec | Provoquer refus Update (source banque invalide, Safe non acquis), puis Clear, Update, Swap | Pool lié/non lié, snapshots absents/valides, motif de refus conservé | A,B,C | DIRTY interdit Swap ; état récupérable uniquement par chemin autorisé ; READY persiste après refus du Swap OS ; aucun pixel partiel | Remettre CLEAN de façon aveugle après erreur et présenter une frame incomplète |
| T09 | Dessin et fontes avec Bobs | Font Select / Bank Font → Text → Bob Update puis changement palette → Swap | Police système/AMCAF, ColorMap et snapshots B8 sur chaque bitmap | A,B,C | Pixel-index et ordre d'affichage corrects ; aucune fuite font, les effets de palette ne corrompent pas les fonds | Texte écrasé par snapshot obsolète ou police dangling |
| T10 | Banques et rechargement | AGBO Get/Mask/Save/Load/Free, AGAPIC info/capture, FICON Stage, CBlock Create/Restore | Banque 5..65535 réellement libre, flags AMOS normalisés à zéro après Load | A,B,C | Revalidation adresse et longueur après Load ; aucun pointeur Chip périmé ; FREE ne modifie pas d'autres banques | Use-after-free, corruption de répertoire, retour succès sur banque manquante |
| T11 | Caches FICON/AGPC et Bobs | FICON8 → FICHIP8 → F Blit/Cache Blit → Swap avec Bobs actifs | Banque en Chip, clips, Bob snapshot présent et absent | A,B,C | WaitBlit avant libération, pixels corrects, écriture autorisée sur back Safe, snapshot cohérent | DMA sur Fast, cache libéré prématurément, changement de décor perdu |
| T12 | IFF tronqué et rollback | Chargeur IFF : BMHD/CMAP/BODY invalides, BODY ByteRun1 court/long ; comparer les plans avant/après refus | Sans Bob puis avec B8 snapshot ; Safe acquis uniquement si utile | A,B,C | Refus propre sans écriture partielle ; si atomicité impossible, contrat explicitement documenté et testifié | Plans modifiés malgré échec ou mémoire hors bornes ; les deux passes divergent |
| T13 | CBlock Capture/Draw/Restore | Capture avant Swap → Swap → Draw/Restore sur back changé | Méthode CPU8/CPU16/Blitter ; alignement 8/16px et dimensions exactes | A,B,C | BitMap source/destination identifiés à l'appel, WaitBlit, transparence non implicite, aucun fond obsolète | Capture lit le front, Restore écrit avant Safe ou restaure mauvais bitmap |
| T14 | Fermer/rouvrir et End | Plusieurs cycles Open → DB → Bobs/B8/C2P/Copper/Font → Close → Open puis End | Même adresse OS possible, pool alloué, owner étranger, Screen Close refusé | A,B,C | FreeMem exactement une fois, callback B8 désarmé, état et epochs réinitialisés, nouvel écran indépendant | Double Free, fuite persistante, vieux snapshot considéré comme valide après reopen |
| T15 | S1-P1e Sprite — GEL | Aga Sprite Bank / Get AGA Sprite, impact des futurs changements de Safe | S1-P1e candidate préservée ; aucune installation/test | A,B,C | Aucun résultat nouveau ; reprendre seulement sur autorisation distincte après P2d corrigée | Ne pas déclarer PASS B/C/D ni produire un nouveau binaire |
| T16 | Copper et affichage | Copper Clear/Wait/Move/End/On/Off + Swap/Close | UserCopperList installée, écran fermé/rouvert, absence de pending message | A,B,C | Liste retirée/restaurée, aucune écriture fantôme, pas d'ownership stale | Copper reste actif au Close ou interfère avec page non Safe |
| T17 | Séquence RPG réelle de décor | Open → IFF Load du décor → Bob Bank/Mask → Bob Auto Update → 240 Swap/animations | Sans pré-Init par Fill ; puis contrôle avec Fill sur les deux pages | A,B,C | Écran et snapshot corrects dès 1ère frame ; pas de refus non récupéré ; mêmes pixels en B/C | Le pré-remplissage masque la panne, les deux versions ne convergent pas |
| T18 | RPG bord opaque / VBL différentiel | Comparer P2_DIM_20X18, P2_EDGE_20X18, P2_SWAP_VBL_20X18 et P2_EDGE_SWAPVBL_20X18 sans modifier leur source | Côté arrière local (19,17), compteur refus Swap, Safe et DIRTY | B,C | Conserver échecs et succès séparés, comptages cohérents ; si un refus dépasse 4 tentatives, cause attribuée par instrumentation | Classifier un pixel valide comme succès de tout le programme ou confondre ERR15 et erreur interne |
| T19 | Back Fill legacy sans Safe après Swap | Open/Double Buffer → Swap réussi → aucun Fill/GetMsg intermédiaire → Aga Back Fill couleur, puis inspection séparée des deux BitMap | Safe pending sans message ; puis message disponible ; scénario témoin utilisant Aga Blit Fill protégée | A,B,C | **Critère de sécurité cible** : aucune écriture sur page non Safe, front inchangé, reprise explicite après acquisition Safe ; distinguer la commande legacy sans valeur de retour de la fonction Blit Fill | Le code P2d actuel ne contient pas de garde Safe dans Back Fill : un essai qui atteint RectFill pendant pending doit être traité comme **FAIL de sécurité**, même si l'image paraît correcte |

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
