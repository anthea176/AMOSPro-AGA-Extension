# Reprise actuelle — AMOSPro AGA Extension

## 21 novembre 2026 — Retour visuel P2e.1 : écran AGA masqué et Bobs carrés

Retour utilisateur : l'écran AGA n'apparaît pas sans raccourci **Amiga+A** ; les carrés ne sont pas adaptés à une vérification visuelle du retournement Bob. L'ASC actif P2e.1 est corrigé **uniquement au niveau du banc** : ajout de `Amos To Back` après initialisation des deux back buffers, remplacement des images carrées par des **F/L masqués 16×16**. ASC actif : 8800 octets, Git blob `edcbbdc9d863dd96f6b5ad22abe44ba0d4c37aaf`. **Ancien préflight du banc 8430 octets ne qualifie plus le nouvel ASC** ; nouveau préflight CI et Runtime à réaliser. **Aucun PASS WinUAE P2e.1 acquis** par ce changement.

Une démo publique visuelle [FLIP_VISUAL.asc](../examples/aga_bob_flip/FLIP_VISUAL.asc) montre un **F 32×32 asymétrique** en modes normal/H/V/HV et applique `Amos To Back`. Elle n'est ni l'ASC actif, ni un test WinUAE passé. Le programme P2e.1 conserve les oracles pixels des deux bobs. Lib P2d et LAST_GOOD inchangées, repo `main` uniquement.


## 21 novembre 2026 — P2e.1 actif pour Gate B Runtime WinUAE

L'auteur a demandé de poursuivre et de **basculer la campagne**. Le nouvel unique ASC [M19_P2E1_AMAL_TWO_BOBS.asc](../tests/current/M19_P2E1_AMAL_TWO_BOBS.asc), 8 430 octets, SHA256 `3ecef4545829e0a705a1a4b09178ec53f981d29ab290d5ecdca579c895d4336a`, pilote deux canaux AMAL 0/1 et deux Bobs AGA 16×16 avec une banque AGBO commune et 16 octets de tampon AMAL. **Préflight officiel strict PASS** sur la source exacte, sans erreur/avertissement ; deux canaux, un Synchro et un seul Swap explicite par frame. **Gate B P2e.1 NON TESTÉE**, Gate C réservée au futur exemple global P2.

**P2e.0 Gate B PASS** conservée, ASC exact dans l'[historique Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/55ca846e9a44065b0e1ba3e8c9a68041ce37746e/tests/current/M19_P2E0_AMAL_BRIDGE.asc), log original [docs/evidence](evidence/M19_P2E0_AMAL_BRIDGE_RUNTIME_2026-11-21.TXT), 397 octets CRLF, SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`. Pas de copie dans `tests/passed/`, aucun autre ASC sous `tests/current/`.

La Lib **P2d inchangée** (136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`) et LAST_GOOD **P1e protégée** (`7922f558...`). Lire [la notice P2e.1](../tests/current/README.md), récupérer `RAM:M19_P2E1_AMAL_TWO_BOBS.TXT` après Runtime. Ne pas annoncer un PASS WinUAE sans nouveau journal.


## 21 novembre 2026 — P2e.0 Runtime PASS ; P2e.1 source de conception preparee

Le journal exact utilisateur `M19_P2E0_AMAL_BRIDGE(2).TXT` (397 octets, SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`) confirme **Gate B Runtime PASS** de l'ASC P2e.0 courant : `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VALID_SAMPLES 240`, `SWAPS 241`, `PIX_SAMPLES 29`, `CHG_X/Y/A 239/119/7`, `CLOSE_RETURNED 1`, `VERDICT PASS`. Le mot de flags `1792=$0700` impose un suivi diagnostique de l'octet fort (`Peek(_ADDR)` propose), pas de validation des flags a cette date. Gate C finale reportee, Gate D non testee.

**Suite source-only :** P2e.1 deux canaux AMAL et deux Bobs 16x16, tampons de 8 octets separes dans une banque de 16 octets, un seul `Synchro` et un seul `Aga Swap` par tick. [Plan](M19_P2E1_AMAL_TWO_BOBS_DESIGN_2026-11-21.md), [banc texte non active](../tests/design/M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt) de 8 420 octets, SHA256 `f0054af6f44ec6cfbbb1dcc233322c516e3e026954f3149d3e60149177a35537`. **Controle structurel local PASS uniquement** ; preflight officiel, WinUAE Runtime et Compiler P2e.1 NON TESTES. Ne pas deplacer ni remplacer l'ASC courant sans decision distincte. Bibliotheque P2d et LAST_GOOD P1e inchangees.


## 21 novembre 2026 — P2e.0 second Runtime : animation correcte, ERR 21 sur flags

L'auteur fournit le second journal `M19_P2E0_AMAL_BRIDGE(1).TXT`, **342 octets** SHA256 `918f262be52ba0f12bc1435c8c129be9afc4f972997f4eb238822107c8f6be1d` : `PRG_STATE 1`, `FRAME 241`, `VALID_SAMPLES 240`, `SWAPS 241`, `BG0/BG1 1/1`, `SWAP_RESULT 1`, `PIX_SAMPLES 29`, `MOVE_X/Y 1`, `IMAGE1/2 1`, `CLOSE_RETURNED 1`. **Aucun refus du Swap ; 29 vérifications de pixels conformes.** Le verdict du programme est encore **FAIL, `ERR 21`**, uniquement parce que `FLAG_X/Y/A 0`. Le manuel indique ces bits à l'offset +0, mais leur absence sous `Synchro Off` / `Synchro` n'est pas élucidée.

**ASC actif corrigé** [`M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc), **6 795 octets**, SHA256 `62c94e9560134c0602b6e79b8cb2c78bf5adf207364d85d5a8953201ba61125f` : `FLAG_X/Y/A` restent des observations non bloquantes, et `CHG_X/Y/A` comptabilisent les différences de valeurs effectives entre deux cycles. `ERR 21` repose désormais sur ces transitions, sans inventer de flags. **Gate B du nouvel ASC non testée**, Gate C individuelle reportée. Lib P2d et LAST_GOOD P1e inchangées ; aucune branche ajoutée.

## 21 novembre 2026 — P2e.0 premier Runtime FAIL ; banc diagnostique corrigé

Le journal utilisateur **P2e.0 initial** (300 octets SHA256 `f2f6914bd719c0409346c0bebdba451775b1d9491c293f442e8a8334a8c5b650`) apporte `PRG_STATE 1`, `ERR 15`, `FRAME 1`, `SWAPS 1`, `LAST_X 97`, `LAST_Y 101`, `LAST_IMAGE 1`, `CLOSE_RETURNED 1`, `VERDICT FAIL`. Le premier `Aga Swap` après placement du Bob échoue. Les trois valeurs AMAL sont correctes ; le rendu n'a pas été présenté. La cause du refus n'est **pas** démontrée.

**ASC de campagne corrigé** [`M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc), **6 089 octets**, SHA256 `27e8a13215b9d286ce7d43b52fa7f11c1238f277e9300b8fd7256998c61a4e12`. Il initialise le fond sur chacune des deux pages physiques via `Aga Blit Fill(96,100,48,32,0)`, comme dans P2d Runtime PASS. Les sorties `BG0`, `BG1`, `SWAP_RESULT` discriminent refus de préparation / refus du Swap. **Gate B du correctif en attente** ; CI préflight à confirmer. La source AMAL, la Lib P2d `ce5fb614...` et LAST_GOOD P1e `7922f558...` ne changent pas. Aucun Compiler individuel.

## 21 novembre 2026 — P2e.0 activé pour Runtime WinUAE

**Bascule explicitement demandée par l'auteur** : unique ASC actif [`M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc), 5 632 octets, SHA256 `bf1d53b54736e990f30ca3a5e79605f2cc88a7a4d0d9886ab166b9a48fe09fa4`. Script source local vérifié octet-identique au Git blob après écriture, préflight officiel strict PASS ; **Gate B Runtime P2e.0 NON TESTÉE**, Gate C individuelle non demandée. [Protocole WinUAE](../tests/current/README.md).

Le test P2d précédent, **Runtime PASS 43/43**, reste accessible [octet pour octet dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/7f78e93b11220199cda4bebff9168fea160ce74d/tests/current/M19_P2D_BOB_AUTO_UPDATE.asc) ; pas d'archivage automatique. Les bibliothèques `dist/AMOSPro_AGA.Lib` P2d (`ce5fb614...`) et `LAST_GOOD` P1e (`7922f558...`) sont inchangées. P2e.0 lit les 8 octets AMAL de la banque 28, contrôle X/Y/image/flags, applique un seul `Aga Swap` par frame et vérifie la page arrière précédente. Prochain élément requis : retour WinUAE réel `RAM:M19_P2E0_AMAL_BRIDGE.TXT`.

## 21 novembre 2026 — P2d Runtime PASS, P2e.0 AMAL expérimental

Le journal original reçu pour P2d rapporte `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `PROBE_PREALLOC 1`, `CHECKS 43`, `CLOSE_RETURNED 1`, `VERDICT PASS` (SHA256 `28f7ebfff3d77e7cc65469df3c246f23487eb1696376d2e078be5543eb13ee7b`). **Gate B Runtime PASS 43/43** sur ce banc. Pas de Gate C individuelle : l'auteur souhaite un futur exemple intégrant toutes les fonctions P2, à tester en interprété et avec AMOS Compiler.

[P2e.0 AMAL](M19_P2E0_AMAL_BRIDGE_2026-11-21.md) : pont AMAL original via 8 octets (flags, X, Y, image) vers un Bob AGA, sans token ni nouveau binaire. [ASC expérimental](../tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt) source-only : **aucune validation Runtime ni Compiler P2e.0**. L'unique ASC actif P2d, sa Lib et LAST_GOOD P1e sont inchangés. Reste : preflight officiel sur l'ASC P2e.0 et WinUAE ciblé avant P2e.1 multi-canaux.

## 21 novembre 2026 — P2d installable, Bob Auto Update

[Lib P2d active](../dist/AMOSPro_AGA.Lib), 136 020 octets, 100 commandes, 203 entrées AP20, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. [Campagne WinUAE](../tests/current/README.md) de 43 contrôles, Runtime et AMOS Compiler à qualifier. Gate A MC68020 PASS. LAST_GOOD P1e.

## 21 novembre 2026 — P2d Auto Update, raccordement natif en mémoire

La [candidate MC68020 P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md) ajoute `Aga Bob Auto Update(Mode)` et raccorde Update au Swap explicite. Elle se reconstruit à 136 020 octets, 100 commandes et 203 entrées AP20, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Le banc natif couvre les deux implantations et les refus de rendu ou de présentation. Lib installable P2c, ASC actif P2c et LAST_GOOD P1e.

## 21 novembre 2026 — P2c Runtime PASS, lancement de P2d

P2c passe 34/34 en Runtime WinUAE, `PRG_STATE 1`, `ERR 0`, `CLOSE_RETURNED 1` et `VERDICT PASS`. [Preuve Runtime](M19_P2C_BOB_PLANES_MODEL.md). Gate C Compiler non testée.

[P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md) définit un mode facultatif qui prépare la page arrière à l’appel explicite de Swap. Les neuf tests hôtes vérifient le rendu, la conservation d’une page prête après refus de présentation et la récupération après échec. P2c reste la candidate installable et P1e la référence LAST_GOOD.

## 21 novembre 2026 — P2c installable, Bob Planes

**Lib active** [M19 P2c](../dist/AMOSPro_AGA.Lib), 135 596 octets, SHA256 `eebd7175035f6e6afbd7ed4d2bf5363bd6f816887993db22b848f8d5cfe48d3d`, 99 commandes et 202 entrées AP20. `Aga Bob Planes(N,Masque)` sélectionne les plans de destination par Bob sans modifier le masque AGBO. Gate A passe à deux implantations avec restauration de fond et Flip. [Banc WinUAE de 34 contrôles](../tests/current/README.md). Runtime et AMOS Compiler P2c à qualifier. LAST_GOOD P1e.

## 21 novembre 2026 — P2b validée sous WinUAE, poursuite P2c

Les deux journaux fournis pour le banc P2b corrigé indiquent `CHECKS 21`, `ERR 0`, `CLOSE_RETURNED 1` et `VERDICT PASS`. Empreintes SHA256 des journaux d'origine :

- Runtime `PRG_STATE 1` — `748bf3b6aba0dfa700f70921db9938465c6d9b53d8e725f6a27e9ae23907aa70`.
- AMOS Compiler `PRG_STATE -1` — `91997cdea916bae6ed93f1028333e76517beb2d126cddb244192c0fffd8caf38`.

P2c commence par le [modèle hôte de sélection des plans par Bob](M19_P2C_BOB_PLANES_MODEL.md), 7 tests PASS. Le raccordement natif au peintre AGA doit être qualifié en opaque et masqué avant l’update automatique et AMAL.

## 21 novembre 2026 — P2b installable, Bob Flip

**Lib active** [M19 P2b](../dist/AMOSPro_AGA.Lib), 135 352 octets, SHA256 `96f4bc7e1d604d57d615e198eb43ca6abc800cdc3853c6e9ac2827ad6a86e448`, 98 commandes et 200 entrées AP20. `Aga Bob Flip(N,Mode)` sélectionne normal, H, V ou HV pour un Bob actif. Cache Chip par slot, partagé par le rendu et les collisions, revalidé par identité de banque et génération. Gate A native PASS à deux implantations. [Banc et journal attendus](../tests/current/README.md). Runtime et Compiler P2b PASS 21/21 sur le banc corrigé `562f243`. LAST_GOOD P1e.

## 21 novembre 2026 — P2b noyau planaire privé et préparation Chip

**Gate A privée MC68020 PASS.** [Contrat et preuve](M19_P2B_BOB_ORIENTATION_HOST.md) · [émetteur](../tools/m19_p2b_planar_orientation020_emit.py) · [banc natif](../tools/test_m19_p2b_planar_orientation020_gate_a.py). Deux entrées privées, 562 octets, SHA256 `c4632d93c8af5c856dafd5e27d2003bc805830ff29c3644c412a94735acace69`. Plans et masque retournés dans une destination séparée, préparation par Exec simulé et libération sur refus. 216 sorties comparées octet pour octet sur deux implantations MC68020. Le noyau natif P2a accepte le masque produit et respecte le clipping du banc. **Suite** : cache par identité de banque, génération, image et orientation, état par Bob et validation des cycles Update, Bank Free, Close et End. Lib active P2a, LAST_GOOD P1e et ASC de campagne préservés.

## 21 novembre 2026 — P2a Runtime PASS sur le premier ASC, P2b modèle hôte

**P2a :** le journal utilisateur `M19_P2A_BOB_COL.TXT` indique `PRG_STATE 1`, `ERR 0`, `CHECKS 8`, `VERDICT PASS`. Le format correspond au premier ASC de collision, qui écrit le verdict après le retour de `Aga Screen Close`. La ligne `CLOSE_RETURNED` est propre au banc republié sous `tests/current/`. Gate C Compiler et Gate D matérielle non testées.

**P2b :** [modèle et contrat](M19_P2B_BOB_ORIENTATION_HOST.md), **6 tests hôtes P2b et 40 régressions hôtes P2a PASS**. Orientation par Bob, couleurs et visibilité transformées ensemble, hotspot signé effectif, limites P1d et collisions. Suite : qualifier le noyau privé MC68020 et le cycle des variantes Chip avant de fixer une API publique. La Lib active P2a, LAST_GOOD P1e et l'ASC de campagne gardent leurs empreintes.

## 21 novembre 2026 — Livraison initiale P2a, Gate A PASS

**Lib active** : [dist/AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib), **129 544 octets**, SHA256 `e2d149f67da9eb3a8c7222113338a8e0ad3f08fb512792a54b825987e88d92fe`, 97 commandes/198 AP20 ; [exemple](../tests/current/M19_P2A_BOB_COL.asc), [guide](M19_P2A_PUBLIC_CANDIDATE_2026-11-21.md). API `Aga Bob Col(A,B,Mode)` : collisions rectangle (0) et masque (1). Gate A publique source-native sur deux relocations PASS (5 tests), préflight ASC PASS. **Suivant : lancer le test sous WinUAE**, récupérer `RAM:M19_P2A_BOB_COL.TXT` (attendu `VERDICT PASS`, `CHECKS 8`). Gate B WinUAE / C Compiler / D physique NON TESTÉES. **LAST_GOOD P1e protégée** 124 444 octets, inchangée, aucune promotion.


## 21 novembre 2026 — P2a : UNE requête native MC68020 de collision, Gate A privée PASS

**[Rapport P2a intégral](M19_P2A_FULL_QUERY_NATIVE_2026-11-21.md) · [Émetteur de l'unique appel MC68020](../tools/m19_p2a_collision_query020_emit.py) · [9 tests d'intégration](../tools/test_m19_p2a_collision_query020_gate_a.py) · [CI native 91/91 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44905618103).** L'entrée privée de **484 octets**, SHA256 `c7bc01b85932eaa98bf9143733382e8c40f736f3989c12633775d63605609cb9`, pilote en **un seul appel 68020** les contrôles réels P0f/P0j-b3, l'extraction des hotspots signés par P0j-b1/P1b (874 octets), le clipping écran et les zones P1d (packer 1 742 octets), puis le noyau de collision rectangle/masque (764 octets). D3=1 hit, 0 no hit, -1 refus, D2=0. Le banc a détecté puis corrigé la préservation d'A3 ; ABI, sélection de banque, source Chip et pile sont testées sous Unicorn MC68020.

**Tests : 91/91 PASS** = 17 géométrie hôte, 23 AGBO hôte, 9 noyau collision, 9 P0f apparié, 8 paire Chip P0j, 8 packer P1d, 8 hotspots P1b natifs, 9 requête en appel unique. **Statut source-only : pas de token AP20, pas de nouvelle Lib, pas de changement à l'ASC ni à la P1e LAST_GOOD.** Gate A de la chaîne native privée PASS ; **Gate A d'intégration dans la Lib et Gates B Runtime WinUAE / C vrai Compiler / D physique NON TESTÉES.** Prochain verrou : rattacher les dimensions écran / la table P1d à la **vraie AGA State propriétaire**, puis audit ABI/AP20 avant éventuelle API publique.


## 21 novembre 2026 — M19 P2a : deux images Chip résolues par les vrais P0f et P0j-b3

[Émetteur 946 octets](../tools/m19_p2a_pair_chip_resolve_emit.py) · [8 nouveaux tests natifs](../tools/test_m19_p2a_pair_chip_resolve_gate_a.py) · [rapport](M19_P2A_PAIR_CHIP_RESOLVE_2026-11-21.md) · [CI P2a 66/66 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44903500981). Noyau source-only MC68020 SHA256 7ee9fa70673b8827bde31d12e1023982a7439f80c77c34e84d9c73438e678548. Le nouveau pont assemble les deux lectures natives P0f, la résolution de leurs deux images/masques Chip via P0j-b3 et une seconde vérification P0f, puis publie **120 octets** atomiquement. Deux implantations testées, tampon inchangé sur tout refus, sélection de banque et ABI préservées.

**66 tests PASS** : 40 hôtes, 9 noyau collision MC68020, 9 pont P0f apparié MC68020 et 8 pont P0f+P0j-b3 MC68020. **Cache Chip préexistant obligatoire.** Reste : hotspots signés P1b, clipping écran et limites P1d, deux descripteurs de collision de 40 octets, puis appel du noyau 764 octets. Gate A privée P0f/P0j PASS, chaîne collision intégrée non testée ; WinUAE B / Compiler C / matériel D non testés. Pas de Lib, LAST_GOOD ou ASC modifiés.


## 21 novembre 2026 — M19 P2a : paire de Bobs contrôlée par le vrai P0f, 328 octets natifs

[Émetteur](../tools/m19_p2a_pair_checked_read_emit.py) · [Banc de validation](../tools/test_m19_p2a_pair_checked_read_gate_a.py) · [Rapport privé](M19_P2A_PAIR_CHECKED_READ_2026-11-21.md) · [CI P2a PASS (58 tests)](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901815788). **MC68020 source-only, 328 octets**, SHA256 `3e2cdedb603fb090f0bfd4b46cf3ecc1e3684ace2ddf922b7b3076c6efa6d5dd`. Le pont appelle deux fois le **vrai `identity_check` P0f** avec `A5` propriétaire et `Bnk.GetAdr` simulé ; il publie atomiquement deux enregistrements natifs P0e de 24 octets après validation des deux banques, générations et stamps. Deux placements, 9/9 tests MC68020 PASS ; le noyau antérieur de collisions 764 octets reste validé indépendamment (9/9). Registres et sélection de banque préservés.

**Statuts :** 17 + 23 hôtes, 9 noyau MC68020 et 9 pont P0f MC68020 = **58/58 PASS** ; la policy CPU/livraison PASS. **Reste à faire :** résoudre les images et masques via le P0j-b3 *sur un tampon sûr*, construire deux descripteurs de 40 octets avec limites P1d et joindre le noyau de collision. Pas d'API AP20/Lib/ASC P2a ; Gate A chaîne native complète/B WinUAE/C Compiler/D physique : NON TESTÉES. P1e LAST_GOOD 124 444 octets reste intacte.


## 21 novembre 2026 — M19 P2a noyau MC68020 isolé PASS

[Source du noyau MC68020](../tools/m19_p2a_collision020_emit.py) · [Banc natif](../tools/test_m19_p2a_collision020_gate_a.py) · [Rapport de validation](M19_P2A_COLLISION020_NATIVE_2026-11-21.md) · [CI PASS 44901130823](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44901130823). Noyau privé **764 octets**, SHA256 `2546b269cad753c6b401c5d3cf3330e0f96545e64506a023d381b60c154450b7`, deux modes : 0 rectangle, 1 masque AGBO. ABI D2=0 et D3=1/0/-1, registres AMOS et mémoire source préservés. **9 tests natifs MC68020 PASS sur 2 implantations, dont 720 comparaisons aléatoires et 240 cas de masques non alignés**, ajoutés aux 40 tests hôtes préexistants. Contrôle CPU / livraison PASS (CI 44901130811). Une première CI a trouvé A3 clobber ; corrigé via A6 préservé, puis relancé PASS.

**Portée stricte :** CPU 68020 émulé et **descripteurs déjà validés par le banc**, pas de capture réelle des objets/banks à partir d'AMOS, pas de token AP20, pas de `.Lib` P2a, pas de WinUAE ni Compiler. **P1e LAST_GOOD demeure inchangée** (124 444 octets SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`) et ASC de campagne inchangé. **Gate A du noyau isolé PASS ; Gate A intégration AP20 non testée, Gate B/C/D P2a non testées.** Suite : pont natif contrôlé entre objets actifs/stamps/banques P1e et ces 40 octets de descripteur.


## 21 novembre 2026 — P2a : raccord source réel PASS (sans API native)

[Modèle raccord AGBO/P1e](../tools/m19_p2a_agbo_bridge.py) · [23 tests supplémentaires](../tools/test_m19_p2a_agbo_bridge.py) · [CI 40/40 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44899748782) · [contrat source et API proposée](M19_P2A_COLLISIONS_HOST_2026-11-21.md).

Formats vérifiés par les sources : **64 enregistrements P0e de 24 octets**, stamps P0f de 16 octets (pointeur/génération/tête de liste/taille), AGBO v1 (32 octets en-tête, 40 octets entrée image, masque MSB à pas 16 pixels), table P1d de **65 × 16 octets**. Les 23 tests supplémentaires couvrent les refus sur génération/stamp périmés, OFF, suppression d'image, plusieurs banques, hotspots et limites, plus la banque ABK 26 réelle source-pinnée. Vérification sur données **hôtes de référence**, pas lecture mémoire WinUAE. Lien à l'ABI de `Aga Bob Col(A,B,Mode)` **proposé uniquement**, non approuvé ni intégré : 0 rectangle/1 masque, retour 1/0/-1 à auditer.

**P1e LAST_GOOD et campagne ASC strictement inchangées.** P2a Gate A native/B Runtime/C Compiler/D physique : non testées. Prochaine tâche : noyau MC68020 source-only et preuves contre le modèle avant tout token AP20.


## 21 novembre 2026 — M19 P2a collisions Bob–Bob (modèle hôte)

[Contrat P2a](M19_P2A_COLLISIONS_HOST_2026-11-21.md) · [Modèle Python](../tools/m19_p2a_bob_collision_model.py) · [17 tests](../tools/test_m19_p2a_bob_collision_model.py) · [CI dédiée](../.github/workflows/m19-p2a-bob-collisions-host.yml). Rectangles puis masques, hotspots et clipping global/local. Tests Python source-only ; aucune modification P1e LAST_GOOD ni ASC, aucun token AP20, aucune Gate native P2a / Runtime / Compiler / physique revendiquée. Raccord aux données AGBO P1e à préparer après vérification des champs source.

## 21 novembre 2026 — M19 P1e LAST_GOOD, ouverture P2

**Autorisation expresse de l’auteur :** « non pas de compile promot la lib, met a jour les CI et on continu sur le chantier P2 ». Promotion sur `main` de la Lib active P1e en `LAST_GOOD` par copie Git blob strictement identique (**124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, blob `5bb0c476c2b286495a1d0cf7d4415dbbc4eec369`). L’ancienne P0 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` est conservée dans l’historique Git.

**Gate A native MC68020 : PASS ; Gate B Runtime WinUAE : PASS 2/2.** Deux journaux distincts `M19_P1E_BANK_EDIT(1).TXT` et `M19_P1E_BANK_EDITbis.TXT`, de 2 412 octets chacun, identiques par comparaison octet pour octet (SHA256 `3059b4fada16af884616756877ce0512831b752a8a299ad27db922d46b2644f3`). Dans chacun : `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `EDIT_FRAMES_OK 3`, `EDIT_PIXELS_OK 9`, `EDIT_REJECT_OK 2`, `CLOSE_RETURNED 1`, `BANKS_ERASED 4`, `VERDICT PATH_OK`. Le champ `LIB_SHA256` des logs est une étiquette produite par l’ASC, pas un contrôle autonome du fichier installé dans WinUAE. **Gate C vrai Compiler NON TESTÉE et non demandée ; Gate D physique NON TESTÉE.** [Rapport](M19_P1E_PROMOTION_2026-11-21.md).

**P2** : commencer par les collisions Bob–Bob, modèle rectangulaire de référence puis test exact des masques, avant tout changement d’API ou de binaire. Retournements H/V non destructifs ensuite. Pas de nouvelle Lib ni remplacement de l’ASC dans cette phase de cadrage. [Contrat P2](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p2--fonctions-avancées--compatibilité-progressive).


## 21 novembre 2026 — M19 P1e Del Bob / Ins Bob pour WinUAE

La bascule autorisée installe **P1e** dans `dist/AMOSPro_AGA.Lib` sur `main`. Taille 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, 96 commandes, 196 entrées AP20, cinq groupes MC68020, PC16 maximal 14 130. [Builder](../tools/build_m19_p1e_bank_edit_in_memory.py) · [Gate A native PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44892222083) · [Campagne WinUAE](../tests/current/README.md). Cet état était celui de la bascule initiale ; voir la promotion P1e et la Gate B PASS documentées en tête de page.

## 21 novembre 2026 — M19 P1d Limit Bob, Lib de travail pour WinUAE

Signature approuvée par l’auteur. [Contrat](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1d--limit-bob) · [Builder](../tools/build_m19_p1d_limit_bob_in_memory.py) · [Banc MC68020](../tools/test_m19_p1d_limit_bob_gate_a.py).

**P1d active** — 121 432 octets, SHA256 `47fc7c5d056211a62a50b5405b8952db0bb715ace72a8dc257c4a90def2eb785`, 94 commandes, 192 entrées AP20, cinq groupes et PC16 maximal 32 530. Gate A locale PASS sur 76 scénarios natifs et deux placements. Le banc vérifie les pixels et les masques, les quatre modes de tri, les refus avant DMA, l’ouverture et la restauration du décor des deux pages via Update/Clear. Services Amiga simulés.

P1d est livrée sur `main` avec le [banc WinUAE](../tests/current/README.md). P0 reste `LAST_GOOD`. **Gate B Runtime PASS sur les mesures des deux passages**, 24/24 pixels de clipping sur chaque passage. [Résultats et portée](M19_P1D_LIMIT_BOB_RUNTIME_2026-11-21.md). Gates C et D à tester.

**P1e** — [Contrat Del Bob / Ins Bob](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1e--del-bob-et-ins-bob) approuvé. Les opérations AGBO et le repackeur privé MC68020 sont testés sur 132 scénarios natifs. Les deux commandes passent le [banc intégré MC68020](../tools/test_m19_p1e_bank_edit_gate_a.py) avec services Amiga simulés sur deux placements. Candidate reconstruite en mémoire, 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`. P1d était la Lib active avant la bascule P1e.

## 21 novembre 2026 — M19 P1c Bob Priority installée dans la Lib de travail

L'auteur a approuvé `_OK=Aga Bob Priority(Mode)` à quatre modes. Implémentation MC68020 dans le [builder P1c](../tools/build_m19_p1c_bob_priority_in_memory.py) à partir de P1b reconstruite octet pour octet. [Contrat](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1c--priorité-daffichage-des-bobs). Le mode 0 conserve le parcours historique. Les autres modes utilisent les coordonnées Y logiques et les ID des Bobs actifs. Le réglage revient à 0 à l'ouverture réussie d'un écran.

**Candidate P1c** — 119 916 octets, SHA256 `658717f41e73ea0410ddcea682929d357df1a80fefd40d8ae0dece037a37613c`, 93 commandes et 190 entrées AP20, groupes [142,153,156,179,183], PC16 maximal 32 144. [Banc Gate A](../tools/test_m19_p1c_bob_priority_gate_a.py). **Gate A locale PASS** sur 36 scénarios natifs répartis sur deux placements, avec l’ABI et le dispatch AP20 modélisés, les quatre modes, les hotspots, les refus avant DMA et les deux pages via Update/Clear. Régression P1b intégrée : 98 contrôles PASS.

**Bascule autorisée par l’auteur le 21/11/2026.** P1c est la Lib de travail sur `main`. P0 reste `LAST_GOOD`. [Banc WinUAE](../tests/current/README.md) — huit sondes de priorité sur les deux pages, quatre phases hotspot et 405 frames de régression. **Gates B Runtime et C Compiler PASS sur les mesures du banc**, deux journaux Runtime et un compilé. [Résultats et portée](M19_P1C_PRIORITY_GATES_BC_2026-11-21.md). Gate D à tester.

## 21 novembre 2026 — M19 P1b Hot Spot — Gate B Runtime WinUAE PASS

**Autorisation utilisateur :** « go jusqua la lib » = aller jusqu'à la **bascule du seul binaire actif** P1b et du banc WinUAE, pas une promotion de `LAST_GOOD`. Réalisation exclusivement sur `main`. [Commit de bascule `2af4844`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/2af4844d803430a550a825a309a2862b51f5e9d6).

**Identité exacte :** `dist/AMOSPro_AGA.Lib` **P1b 119 176 octets**, SHA256 `2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4`, blob Git `8bc11d556971ea7a90bd57b00f231ca26cac0958`. 92 commandes / 188 AP20 entrées, unités MC68020 `[142,153,156,177,181]`, PC16 max31444, 352 octets natifs ajoutés. [Builder P1b déterministe](../tools/build_m19_p1b_hotspot_in_memory.py) reconstruit intégralement P1a puis modifie uniquement le BRA source-identifié dans BOBS et ajoute son pont hotspot après `explicit_image_resolve_entry`, vers le Safe Blitter d'origine. Getters P1a conservent X/Y logiques, aucun nouveau token. **`LAST_GOOD` P0 117 896 octets SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, blob `6e23a1dc783145adb41f1a9b02fc6fc8f3b80ff2`, inchangée.**

**Gate A P1b : PASS intégrée** [CI 44836896149](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44836896149), **98 contrôles** du vrai code MC68020 avec Amiga/Blitter simulés et deux implantations ; 258 contrôles natifs supplémentaires du helper. Résolution AGBO/génération, cache Chip, masque, pixels, clipping, 64 Bobs, objet invisible no-op, background front inchangé. [Rapport](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md).

**Unique ASC actif modifié** : `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, **17 566 octets ASCII LF**, neuf étapes et 405 frames P0 + trois Bank Free + 14×3 getters conservés, **quatre phases hotspot** supplémentaires, journal `RAM:M19_P1B_HOTSPOT.TXT` ; ressource `tests/current/M19_P1B_HOTSPOT_BANK26.abk`, **200 octets, hotspot (+4,+3)**, SHA256 `8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325`. Bank26 doit être libre et l'ABK copiée dans le répertoire courant AMOS AVANT d'exécuter ASC via `Project → Merge ASCII`. [Procédure et valeurs attendues](../tests/current/README.md). 405 frames + 4 phases, `HOTSPOT_FRAMES_OK 4`, `HOTSPOT_GETTERS_OK 12`, `BANKS_ERASED 3`, `VERDICT PATH_OK` attendu.

**Gate B P1b Runtime WinUAE : PASS fonctionnel.** Deux lancements dans la même session AMOS et quatre observations visuelles confirmés par l'auteur. Les deux journaux donnent `PRG_STATE 1`, 405/405 frames, 42/42 getters P1a, 4/4 phases hotspot, 12/12 getters hotspot, trois banques effacées et `PATH_OK`. [Rapport Gate B](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md#résultats-runtime-winue). **Gates C véritable Compiler et D Amiga physique à tester.**

**CI globale :** des régressions historiques verrouillées sur une ancienne SHA active étaient rouges après bascule ; les adaptateurs R82/R84 et README bilingues ont été mis à jour pour reconnaître l'empreinte P1b sans modifier les octets historiques. Ne déclarer que les CI effectivement PASS ; P1c (priorités) et P1d (`Limit Bob`) restent à décider.


## 21 novembre 2026 — M19 P1b Hot Spot, premier jalon natif MC68020 PASS (source-only)

**Référence actuelle :** P1a `dist/AMOSPro_AGA.Lib` **118 816 octets** SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a` ; P0 `dist/AMOSPro_AGA_LAST_GOOD.Lib` **117 896 octets** SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` ; **un seul ASC** sous `tests/current` (`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, 14 871 octets). **Aucune modification** de ces trois fichiers lors du travail P1b. Gate A P1a PASS, Gate B P1a PASS fonctionnel sur deux journaux, Gates C/D P1a non testées.

**Livraison P1b (source-only) :** [helper natif](../tools/m19_p1b_hotspot_origin_emit.py) qui lit les hotspots AGBO v1 signed16 offsets +28/+30, calcul `X_draw=X_Bob-hot_x`, `Y_draw=Y_Bob-hot_y`, et garde clipping/signed16 avant tout DMA ; [modèle de frame](../tools/m19_p1b_hotspot_draw_model.py) préservant bob X/Y, masque et double buffer ; [test](../tools/test_m19_p1b_hotspot_source_gate_a.py), [workflow dédié](../.github/workflows/m19-p1b-hotspot-source-gate-a.yml). **CI 44835297656 PASS**, cinq tests dont **258 cas natifs MC68020** sur deux implantations, tests de masques, stages, source/stack/ABI ; [politique CPU 44835297650 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44835297650). Rapport : [M19 P1b — Gate A partielle](M19_P1B_HOTSPOT_SOURCE_GATE_A_2026-11-21.md).

**Limite explicite :** la primitive demande une entrée AGBO et des dimensions logiques **déjà validées** ; elle **n'est PAS encore branchée** dans le code installé. Le rendu natif actuel P1a ignore les hotspots non nuls. `D3=0` sur objet entièrement hors écran signifie **no-op réussi**, à traiter comme tel par le futur branchement. **Gate A complète du rendu P1b non acquise ; Gates B/C/D P1b non testées.**

**Prochaine action :** relier le pointeur AGBO vérifié après `explicit_image_resolve_entry` au helper avant `private_bob_blit_entry`, sans altérer les X/Y logiques des 64 Bobs ni les bytes P0/P1a installés ; valider rendu réel MC68020/Blitter simulé et sécurité de `Clear → Update → Swap`, préparer builder P1b en mémoire puis seulement envisager la bascule après autorisation. **La CI globale historique `Artifact integrity` échoue encore sur un ancien allowlist P1a**, indépendamment de la Gate A source-only P1b, ne pas annoncer intégrité globale PASS.


## 21 novembre 2026 — P1a Gate B Runtime PASS ; lancement M19 P1b Hot Spot

**P1a : Gate A MC68020 PASS (110 contrôles), Gate B Runtime WinUAE PASS fonctionnel** sur deux journaux distincts et une capture à l'étape 4/9. [Preuves détaillées et limites](M19_P1A_RUNTIME_B_2026-11-21.md) : chaque log **1 168 octets / 54 lignes**, `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `QUERY_CASES 14`, `QUERY_VALUES_OK 42`, `QUERY_VALUES_BAD 0`, trois appels Bank Free, `CLOSE_RETURNED 1`, `VERDICT PATH_OK`. Différence unique : `RETRY_VBL` 363 et 362. Le SHA étiqueté dans l'ASC ne prouve pas les octets chargés dans WinUAE.

**Cible active et protection inchangées :** `dist/AMOSPro_AGA.Lib` **P1a 118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a` ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` **P0 117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` ; seul ASC sous `tests/current` : `M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, 14 871 octets. **Gate C vrai Compiler P1a NON TESTÉE, D Amiga physique NON TESTÉE.** Aucune promotion P1a autorisée.

**Décision auteur :** « oui allons y » après proposition d'enregistrer la Gate B P1a puis d'engager **M19 P1b application des hotspots au rendu Bob**. Procéder d'abord **en source-only** après inspection du véritable trajet `AGBO → staging Chip → renderer Safe Blit` et de l'ABI, avec tests MC68020/masques/clipping. Ne pas éditer la Lib active, `LAST_GOOD`, les ASC actuels/passés ni les archives pour cette première phase. Les priorités, `Limit Bob`, Sprites et M20 restent en attente.


## 20 novembre 2026 — Bascule autorisée M19 P1a dans la seule Lib active ; WinUAE Gate B à faire

**Autorisation :** « va y » en réponse à la proposition explicite de bascule P1a pour Gate B WinUAE (ou poursuite de P1b) ; intervention **limitée** à l'unique `dist/AMOSPro_AGA.Lib` et à l'unique ASC de campagne, tests statiques et documents sur **`main`**. La Lib active P1a est reconstruite depuis les sources Gate A puis installée **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`, blob Git `21a8620ad56a94627eb211b2faa7c5bed3f5d334`. **`LAST_GOOD` P0 protégée, 117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` ; aucun changement**. [Commit bascule `d5fa6b1`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/d5fa6b1b4664817afe2419e5f7138a10e43f9405).

**Nouveau test sur le même chemin actif** [`tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **14 871 octets**, programme ASCII unique. Il conserve la boucle P0 de 405 frames, 403 Clear, 405 Update, 50 Off, trois Bank Free et réactivation, en ajoutant **14 vérifications de chaque fonction X/Y/I = 42 valeurs**, erreurs **25**, journal `RAM:M19_P1A_BOB_GETTERS.TXT`. Pas de déplacement ou nouvelle archive ; ancien ASC P0 intact dans Git au commit parent.

**Gate A P1a : 110 contrôles MC68020 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829640179)). **Gates B Runtime / C Compiler / D physique P1a NON TESTÉES** ; les anciens PASS de P0 et B7 ne sont pas transférables. [Protocole WinUAE détaillé](../tests/current/README.md) : AGA PAL, MC68030 JIT ON, `git pull origin main`, copier uniquement `dist/AMOSPro_AGA.Lib` dans APSystem, redémarrer AMOS, `Project → Merge ASCII` dans un programme vide, **deux Runtime successifs sans redémarrage ni `Erase All`**, sauvegarder les deux journaux et observer aucune traînée/freeze, retour AMOS après Close. Attendus `QUERY_CASES 14`, `QUERY_VALUES_OK 42`, `QUERY_VALUES_BAD 0`, `RESULT 1`, `ERR 0`, `VERDICT PATH_OK`.

**CI :** les workflows historiques de l'ancienne P0 vérifient parfois une SHA active fixe et doivent être adaptés **sans modifier leurs sources ni résultats historiques**. Les nouveaux contrôles doivent conserver l'identité de P0 `LAST_GOOD`. Ne pas déclarer toutes les CI PASS sans preuves. **M19 P1b Hot Spot non engagé en natif**, M20/Sprites en attente.



## 20 novembre 2026 — M19 P1a getters X/Y/I Gate A MC68020 PASS, candidate source-only

**Ordre validé :** `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)` sont des **fonctions numériques à un argument N**, avec `D3=-32769` en cas de refus (ID absent/off, propriétaire étranger, etc.), hors domaines de X/Y signés et d'image. L'auteur a confirmé « ok go » après la proposition explicite. **Le code natif et les 3 tokens AP20 sont développés, mais aucun binaire n'est installé.**

**Preuve :** [rapport P1a complet](M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md), [Gate A MC68020 110 vérifications PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430), [politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476435). **Candidate générée uniquement en mémoire**, **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`, **92 commandes/188 entrées AP20**, groupes `[142,153,156,177,181]`, PC16 max `31092` ; source native ajoutée au cinquième groupe B8 (838 octets). Les signatures 1-argument `00` et `GetP` sont vérifiées. Les stubs sont 185, 186, 187 (B8 group181 offsets 13894,13942,13990). Builder [`build_m19_p1a_getters_in_memory.py`](../tools/build_m19_p1a_getters_in_memory.py), emitter [`m19_p1a_bob_getters_emit.py`](../tools/m19_p1a_bob_getters_emit.py), [test](../tools/test_m19_p1a_getters_gate_a.py).

**Incident résolu dans P1a :** le point d'entrée de lecture en BOBS est `relay_read_entry` ; les nouveaux stubs de fin de table dépassaient PC16 vers le groupe BOBS (`-44510`) et le builder les a refusés. La solution sûre les route vers le **cinquième groupe B8**, déjà atteignable, avec un pont vérifiant callback A5+1CC/+1D0, marqueur source B8RG, TypeOfMem et signature native. **Les octets BOBS d'origine restent inchangés.** Deux placements CPU020 simulés pour l'interpréteur et le Compiler, **pas un vrai Compiler**.

**Protections vérifiées :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` P0 restent 117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **même blob Git**. Un seul ASC actif `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` (12 837 octets), ni tests passés ni archives modifiés. **P1a Gates B Runtime, C vrai Compiler et D réel NON TESTÉES.** L'audit global historique `Artifact integrity` reste indépendant et ne doit pas être déclaré PASS sans résultat complet.

**Suite :** demander une décision **distincte de bascule** P1a de la seule Lib active et du test ASC pour une Gate B WinUAE ; **ne pas remplacer LAST_GOOD P0**. Ou avancer sur P1b Hot Spot en source-only avant bascule. P1c/P1d, Sprites et M20 en attente.



## 20 novembre 2026 — M19 P1 engagée, première Gate A source-only PASS

**Instruction de l'auteur :** poursuivre M19 avec **P1** après la promotion de P0. Première tranche réalisée **sur `main` uniquement** : [commit code `8fe77df`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/8fe77df60ecb807974b98e676a642a5c601dae07), [CI P1 source-only PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44827972362), [rapport et suites](M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md), [chantier mis à jour](../Chantier%20BOB.md). 

**P1a Lecture X/Y/Image :** test de `object_read` sur le **vrai code natif privé P0e MC68020** dans Unicorn à deux adresses de relocation : 64 slots de 24 octets (banque, image, X/Y signés, activité), refus sans écriture en cas d'ID absent/off/propriétaire étranger, réactivation. **Aucune nouvelle fonction publique n'existe** ; noms possibles `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)` sous réserve de validation de syntaxe et d'une politique de refus non ambiguë (X/Y peuvent valoir -1 et 0).

**P1b Hot Spot :** le format **AGBO v1 existant** porte déjà `hotspot_x/y` signés dans les 40 octets par image. Ajout de `set_hotspot(payload,image_id,x,y)` dans [modèle hôte](../tools/m19_p0a_multi_bob_abk.py), sans modifier le format : copie transactionnelle, conservation des pixels/masques/autres images, incrémentation de génération seulement si valeur changée, Save/Load ABK vérifié. **Le dessin natif n'utilise pas encore ces champs** ; aucune commande `Hot Spot` AGA installée.

**Protections :** la Lib active P0 et `LAST_GOOD` restent byte-identiques, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` ; `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`, tests passés et archives inchangés. **P1 Gate B/C/D NON TESTÉES**. La CI `Artifact integrity` du HEAD P0 antérieur restait rouge sur une assertion SHA R84 du test historique R71, indépendamment des tests P1 PASS ; ne pas l'attribuer au P1.

**Prochaine étape :** décider des signatures et des erreurs de lecture X/Y/I, puis builder **AP20 uniquement en mémoire** avec shims MC68020 et test ABI/relocation, sans installer une autre `.Lib` ni toucher à `LAST_GOOD`. Enchaîner ensuite hotspot natif + application au rendu, puis priorités, `Limit Bob` et `Del/Ins Bob` ; Sprites et M20 toujours en attente.



## 20 novembre 2026 — M19 P0 terminée, LAST_GOOD promue avant P1

**Décision de l'auteur :** P0 est terminée et sa bibliothèque de travail est promue LAST_GOOD avant d'engager **M19 P1**. Sur `main`, [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) et [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) sont désormais **byte-identiques**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, 89 commandes/185 entrées AP20, MC68020 minimum. [Commit de promotion `71ff386`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf). **R84**, ancienne LAST_GOOD, reste source-reproductible en **67 904 octets** SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` et consultable dans le Git précédent. Aucun artefact secondaire et aucune archive modifiée.

**Validation à la promotion :** Gate A **PASS** (225 contrôles MC68020), Gate B **PASS fonctionnel selon les deux journaux Runtime reçus** (405/405 frames, 9/9 étapes, 3 Bank Free, zéro échec, fermeture AMOS) ; **Gate C AMOS Compiler P0 NON TESTÉE et reportée** ; Gate D physique NON TESTÉE. Les deux journaux sont identiques et ne prouvent pas un second lancement distinct, ni une inspection visuelle ; leur champ SHA est une étiquette ASC. [Rapport Runtime](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md).

**Sécurité :** les builders historiques R82/R83/R84 restent figés par SHA, et la politique n'admet que cette transition R84→P0 du fichier protégé. Le seul ASC `tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc` est inchangé ; ni test passé ni archive touché. **M19 P1 est la prochaine étape à concevoir, pas encore implémentée** : fonctions Bob X/Y/Image, hotspot, priorité et clipping. M20 attend.


## 20 novembre 2026 — Gate B M19 P0 Bank Free PASS fonctionnel (journaux fournis)

**État de référence :** M19 P0 Bank Select/Free demeure l'unique Lib de test sur `main` : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **117 896 octets**, SHA256 attendu `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, builder [M19 P0 exact](../tools/build_m19_b8_s1_bank_free_in_memory.py). **Gate A : PASS 225 tests MC68020** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)).

**Gate B Runtime WinUAE : PASS fonctionnel d'après les deux journaux transmis le 20/11/2026** (`M19_P0_BANK_FREE1.TXT`, `M19_P0_BANK_FREE2.TXT`). Chaque fichier a 1 043 octets, 48 lignes, SHA256 `5dd8d1c7e15fb13bb0ba1ad7aa083c8928fb5b5af1f459df0d03631308e411e8`. Ils sont **octet par octet identiques** : `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `CLEAR_OK 403`, `UPDATE_OK 405`, `BANK_FREE_CALLS 3`, `BANK_FREE_REARM 1`, échecs 0, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. **Limites** : pas d'identifiant indépendant des lancements, pas de preuve visuelle dans le journal, `LIB_SHA256` est une étiquette ASC et non un hash de la Lib chargée. [Compte rendu précis Gate B](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md) et [protocole](../tests/current/README.md).

**Gate C AMOS Compiler P0 : reportée, NON TESTÉE. Gate D Amiga physique : NON TESTÉE.** R84 `LAST_GOOD` reste protégée. **Régressions CI historiques : PASS** sur la version du code `05c283a6` : [Artifact integrity 44823490337](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490337) et [AGA native CPU / chemins 44823490306](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490306). Ces contrôles hôtes ne remplacent ni la Gate B Runtime ni la Gate C Compiler. **M19 reste en cours** (prochaines fonctions Bob) ; M20 reste en attente.


## 20 novembre 2026 — P0 Bank Free installée sur main, Gate A PASS

**Lib active :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **89 commandes / 185 entrées AP20**, cinq unités natives MC68020, PC16 maximum 31 092. Source [builder exact](../tools/build_m19_b8_s1_bank_free_in_memory.py). **Gate A : PASS 225 contrôles** (104 sélection Chip + 121 Bank Free), deux relocations et AmigaOS/Blitter simulés ; [CI 44801203756](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756). Le binaire est en `dist/` sur `main` depuis [`9fb051c`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/9fb051c304c79d30259dd9ba86f0fe7566566925).

**Nouveau contrat :** `Aga Bob Bank N` prépare immédiatement en Chip une banque AGBO peuplée ; `Aga Bob Bank Free N` est une instruction publique sans retour qui désactive les Bobs de N, refuse pendant READY/DIRTY, attend `WaitBlit`, libère le cache Chip et garde la banque AMOS pour `Save`/`Load`. [Rapport P0](M19_P0_BANK_FREE_GATES_2026-11-20.md).

**ASC de campagne unique :** [`tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **12 837 octets**, reprend les 405 frames de B8 S1, ajoute trois phases Free/réactivation et journalise dans `RAM:M19_P0_BANK_FREE.TXT`. [Protocole WinUAE](../tests/current/README.md). **Gate B Runtime et C Compiler NON TESTÉES sur P0** : les deux passes 405/405 de S1 sont historiques, sans transfert de qualification. R84 `LAST_GOOD` reste intacte : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. M19 continue, M20 attend.


## 20 novembre 2026 — M19 P0 repris : préparation Chip à la sélection de banque

L'auteur a confirmé que **M19 est toujours en cours**, et a demandé de commencer par la préparation Chip de `Aga Bob Bank N` avant `Aga Bob Bank Free N`. Développement sur **`main` seulement** : [source MC68020 append-only](../tools/m19_b8_s1_bank_prestage_emit.py), [builder AP20 en mémoire](../tools/build_m19_b8_s1_bank_prestage_in_memory.py), [banc native](../tools/test_m19_b8_s1_bank_prestage_gate_a.py), [rapport](M19_P0_BANK_PRESTAGE_2026-11-20.md). **Gate A MC68020 PASS : 104 contrôles sur deux relocations ([CI 44796391673](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44796391673))**, candidate AP20 **116 548 octets**, SHA256 `577fe698f040a13ea0a12c88fc80f31fd316eed011a305955eb5be635c8613bf`, source-only ; aucun nouveau token ou binaire installé, aucune intervention sur l'unique ASC actif ni `LAST_GOOD`.

Base inchangée : B8 S1 **116 104 octets**, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`, Gate A précédente PASS / Gate B Runtime PASS sur deux journaux / Gate C reportée. La candidate de préparation vérifie l'AGBO original, prépare en Chip les banques **non vides**, réutilise le cache si identité/génération inchangées et exige un End sécurisé ; aucune copie Chip au choix d'une banque vide. `Bank Free` et M20 attendent les résultats et les décisions étape par étape.

**Attention historique :** la section « démarrage M20 P0 » suivante décrit un prototype déjà enregistré ; elle n'autorise pas la poursuite de M20 tant que les Bobs M19 ne sont pas terminés.


## 20 novembre 2026 — Runtime S1 confirmé, démarrage M20 P0

**M19 B8 S1 : Gate A native PASS et Gate B Runtime WinUAE PASS sur deux journaux transmis.** Ils portent l'étiquette SHA256 S1 (ce champ est écrit par l'ASC et ne lit pas la Lib installée), RUN_MODE RUNTIME, PRG_STATE 1, RESULT 1, ERR 0, FRAMES_OK 405/405, STAGES_OK 9/9, CLEAR_OK 403, UPDATE_OK 405, 50 commandes Bob Off, aucun échec Fill/Copy/Clear/Update/Swap, CLOSE_RETURNED 1, BANKS_ERASED 2 et VERDICT PATH_OK. L'ASC du dépôt ne contient pas de VBL de diagnostic ajouté dans la boucle. **Gate C AMOS Compiler S1 : reportée par décision de l'auteur ; aucune validation revendiquée.** Gate D matériel non testée. R84 LAST_GOOD protégée.

**M20 P0 livré sur main en source host-only** : [modèle pixel](../tools/m20_tilemap_model.py), [banc](../tools/test_m20_tilemap_model.py), [protocole et réserves](M20_TILEMAP_P0_HOST_MODEL.md), [CI 44789691639 : 13 tests PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44789691639). Modélise tilemap 16×16, caméra indépendante pour chaque page physique, repaints des strips et des tuiles modifiées, Bobs opaques et DIRTY/READY avec Swap explicite. **N'est PAS une implémentation MC68020/AMOS ni une validation Gate A/B/C M20.** Aucune nouvelle API, Lib ou ASC ; S1 116 104 octets SHA256 3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a et R84 LAST_GOOD inchangées.

**Prochain chantier sans test Compiler demandé :** étude du rendu planaire des tuiles 16×16, du clipping bitplane, des masques, de l'accès Fast/Chip et de la synchronisation avec B8 S1. Le contrat des nouvelles commandes nécessitera une décision explicite avant exposition publique.


## 20 novembre 2026 — S1 ACTIF, SafePort borné, Gate A PASS ; Gates B/C WinUAE à réaliser

**Bascule native S1 autorisée (« ok go ») et vérifiée sur `main`:** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **116 104 octets**, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`, MC68020+, **88 commandes / 184 entrées AP20**, cinq unités natives `[142,153,156,177,181]`, PC16 maximal `29962`. [Émetteur append-only](../tools/m19_b8_safe_retry_emit.py) + [builder exact](../tools/build_m19_b8_safe_retry_in_memory.py) + [119 tests natifs](../tools/test_m19_b8_safe_retry_gate_a.py). L'ancien natif B8 `00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae` reste byte-exact en préfixe et reconstruisible, les tokens publics inchangés. Seul le stub public `Aga Bob Clear` (index 182) appelle désormais `WaitTOF` **au maximum 3 VBL** si SafePort reste pending, puis retente le Clear natif exact ; autres refus toujours bloquants, pas de Swap implicite, jamais de succès simulé.

**Gate A native S1 PASS** [CI 44780312459](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44780312459) — 119 cas CPU020 sur deux relocations, latence 1/2/3 VBL, Safe jamais reçu, manque de snapshot, propriétaire inconnu, absence de graphics.library, callback non autorisé, et tests B7/B8 précédents. Les services OS/Gfx et notifications sont **simulés**. **Gates B Runtime WinUAE, C vrai AMOS Compiler, D matériel : NON TESTÉES sur S1.**

**Preuve d'origine du défaut sous WinUAE sur l'ancienne B8 :** Runtime et Compiler sans VBL de diagnostic `ERR 18`, 316/405 frames, 314 Clear ; puis Runtime 317/405 avec VBL ponctuel stage8 frame2, 360/405 avec VBL stage8, enfin **Runtime `PATH_OK` 405/405, 403 Clear, 405 Update, 50 Off, 0 échec** avec VBL aux stages8/9. Cela démontre une dépendance au timing, pas une preuve définitive de l'origine interne du refus.

**Seul ASC actif :** [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc) **11 092 octets**, **aucun VBL ajouté à la boucle `For _STEP=1 To 45`**. Faire `git pull origin main` sur Windows, copier S1 dans le slot AGA `APSystem`, redémarrer AMOS, `Project → Merge ASCII` depuis **ce nouveau fichier** et non l'ancien ASC local modifié ; lancer deux fois Runtime puis compiler un nouvel exécutable, conserver les 3 logs `RAM:M19_B8_CLEAR_UPDATE.TXT`. Attendu `ERR 0 / PATH_OK / 405 FRAMES / 9 STAGES / 403 CLEAR / 405 UPDATE` ; ceci n'est **pas encore obtenu sur S1**. Le R84 `LAST_GOOD` 67 904 octets SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` reste protégé.

**L'entrée B8 du 20 novembre qui suit est historique**, décrivant l'ancienne Lib avant S1.


## 20 novembre 2026 — M19 B8 LIVRÉE sur `main` pour Gates B/C

**Bascule explicitement autorisée par « allons y » :** la bibliothèque active de travail [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) est maintenant **M19 B8 — 115 744 octets**, SHA256 `00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae`, **88 commandes et 184 entrées AP20**, cinq unités natives MC68020 (groupes `[142,153,156,177,181]`), portée PC16 maximale **29 962**. La [candidate B8](../tools/build_m19_b8_first_update_in_memory.py) est source-reconstructible octet pour octet. La bascule initiale est enregistrée par le [commit 157a2cb](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/157a2cba27f731a9271f9e41b810dd5eb26cdae1). Les garde-fous et références historiques ont été adaptés pour accepter ce nouveau SHA sans changer les anciennes sources.

**Seul test actif :** [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), 11 092 octets, [protocole WinUAE/Compiler](../tests/current/README.md). Il teste 9 étapes × 45 frames, 403 `Clear` après initialisation de deux pages, 405 `Update`, 405 Swap et 50 désactivations, avec modification dynamique du décor après `Clear`. La création d'un Bob initial arme le callback B7 sans dessiner. **Les deux premiers appels `Update` ne sont pas précédés de `Clear`**, car aucun snapshot n'existe encore.

**Preuves exactes :** [CI 44635843744](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44635843744) **Gate A native MC68020 PASS** (59 vérifications premier Update, 36 intégrations B7/B8, 60 régressions B7, OS/Blitter simulés). **Gates B Runtime WinUAE et C véritable AMOS Compiler : NON TESTÉES sur B8** ; rien n'est installé ni exécuté sur l'émulateur Windows par la CI. La B7-m2 précédente, elle, a ses propres Gates B/C PASS ; elles ne sont pas transférables. R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, intacte.

**Prochain contrôle réel :** `git pull origin main` sur Windows, copier la Lib active dans l'emplacement AGA d'`APSystem`, redémarrer AMOS, importer l'ASC par `Project → Merge ASCII`, deux exécutions Runtime consécutives + compilation d'un nouvel exécutable et récupération de trois journaux `RAM:M19_B8_CLEAR_UPDATE.TXT`. Attendus : `ERR 0`, `PATH_OK`, `FRAMES_OK 405`, `STAGES_OK 9`, `CLEAR_OK 403`, `UPDATE_OK 405`. Ne pas annoncer B/C sans ces logs et les captures/freeze diagnostics.



## 19 novembre 2026 — M19 B8 : premier Update sans Draw préalable, Gate A native intégrée PASS

**SOURCE-ONLY sur `main`, AUCUNE installation :** [émetteur du bootstrap B7 + entrée B8 premier Update](../tools/m19_b8_first_update_emit.py), [builder complet AP20](../tools/build_m19_b8_first_update_in_memory.py) et [banc MC68020 du premier Update](../tools/test_m19_b8_first_update_gate_a.py). [**CI 44635843744 PASS : 59 contrôles MC68020**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44635843744), deux implantations indépendantes avec services OS/graphismes simulés. Le banc valide le vrai chemin setter Bob B7 → armer End sans dessin → Bind B8/AllocMem des deux sauvegardes → Arm callback → préflight B7 → capture du back → vrai Draw B7 → Finish READY → Clear/restauration → Close et deux FreeMem, ainsi que le refus/rollback si aucun End B7 n'est amorcé. Les 36 contrôles B7/B8 intégrés antérieurs et 60 régressions du trampoline passent également. Le banc a détecté puis fait corriger un défaut de retour D2 du wrapper Bob (commit `cb0885e`).

**Candidate HUNK/AP20 réellement reconstruite en mémoire : 115 744 octets**, SHA256 `00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae`, **88 commandes / 184 entrées**, groupes `[142,153,156,177,181]`, PC16 max **29 962**. Deux fonctions numériques nouvelles **uniquement dans la candidate** : `Aga Bob Clear` (index 182), `Aga Bob Update` (index 183). L'ancien setter public Bob (stub 174) est redirigé vers une routine qui arme B7 End **sans dessiner**, après un SET réussi. Il faut donc qu'un `Aga Bob` SET ait été exécuté avant le premier Update ; sans SET préalable, la commande retourne actuellement **0** (refus propre, aucun dessin). Ce cas limite doit être pris en compte dans la campagne WinUAE et dans le contrat public final. Pas de Swap implicite. Une nouvelle session Open/Close via un autre chemin contournant le hook reste un risque ABA non qualifié.

**Gates B/C/D B8 NON TESTÉES.** `dist/AMOSPro_AGA.Lib` B7-m2 (102 400 octets, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`), seul ASC de campagne et R84 `LAST_GOOD` inchangés, vérifiés en CI. **Ne pas basculer la Lib automatiquement : autorisation explicite distincte requise** pour placer cette candidate dans l'unique `dist/AMOSPro_AGA.Lib` et lancer les Gates Runtime WinUAE et AMOS Compiler. [Rapport B8 détaillé](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


## 19 novembre 2026 — M19 B8 : Clear/Update atomique privé, Gate A intégrée PASS

**Code sur `main` et uniquement en mémoire :** [étapes `Clear/Prepare/Finish/Abort`](../tools/m19_b8_clear_update_tx_emit.py), [entrée atomique Update déjà enregistré](../tools/m19_b8_atomic_registered_update_emit.py), [builder exact](../tools/build_m19_b8_atomic_registered_update_in_memory.py), [banc CPU natif B7+B8](../tools/test_m19_b8_atomic_integrated_b7_gate_a.py). [**CI 44628023301 : PASS, 80 contrôles MC68020**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44628023301) sur la transaction et le préflight B7 source-vérifié ; [**CI 44628948845 : PASS, 48 contrôles atomiques + 36 contrôles B7/B8 intégrés + 60 régressions B7**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44628948845), deux relocations. Les vrais B7 préflight 64 images, Draw, Close et B8 copies sont exécutés dans le banc intégré **avec OS/graphismes simulés**, pas AMOS Runtime/Compiler. `Safe`, restauration par page, décor dynamique, `DIRTY/READY`, A5, rollback et Close répété sont couverts.

**Candidate SOURCE-ONLY AP20 actuelle : 115 180 octets**, SHA256 `62b9d3236197d5b7340237278719d3caa17b0b3df456c4bbe300c03d801dcae2` ; **86 commandes / 1104 AP20**, groupes `[142,153,156,177,181]`, PC16 max **29 558**. **Ne pas installer**, pas de nouveaux tokens. L'Update privé fonctionne **seulement après enregistrement B7 End existant** ; reste à créer un bootstrap du premier Update qui capture le décor avant le moindre Bob, puis l'API AMOS complète et un ASC de campagne après autorisation distincte. B7-m2, unique ASC validé et `LAST_GOOD` R84 inchangés. [Rapport détaillé](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


## 19 novembre 2026 — M19 B8 : trampoline natif B7 Close/Draw/End ↔ B8, Gate A PASS

**Livré sur `main`, source-only, rien à installer :** [émetteur B7 local](../tools/m19_b8_b7_hook_emit.py), [relais de B8 au callback B7](../tools/m19_b8_cross_unit_arm_emit.py), [builder AP20 en mémoire](../tools/build_m19_b8_b7_trampoline_in_memory.py), [tests MC68020](../tools/test_m19_b8_b7_trampoline_gate_a.py). [**CI 44619276851 PASS — 60 contrôles MC68020**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44619276851) sur deux implantations natives distinctes ; relai indirect sans `BSR` PC16 inter-unités, vérification callback End/marqueur `B8RG`/propriétaire A5, chaîne B7 `Draw`/`Close`/`End`, maintien des snapshots sur Safe/Disp pending et libération une seule fois après fermeture confirmée. L'échec intermédiaire dans le banc était un chevauchement entre le code de la cinquième unité et les allocations de la fixture ; test corrigé et relancé PASS.

**Candidate AP20 strictement en mémoire : 113 192 octets**, SHA256 `40de1b32206de8d784249b60a43d7f5f047828a2657c6651d4cb73bfeef09750`, **86 commandes**, **1104 AP20**, cinq unités `[142,153,156,177,181]`, PC16 max **29 558**. Seuls les anciens stubs Close 179 et Draw 180 sont redirigés, dans l'image non installée. Les natifs B7-m2 originaux restent préservés en préfixe et l'API publique est inchangée.

**Prochaine étape :** rendre l'enregistrement B8 effectif dans un orchestrateur `Clear/Update` avec rollback et garde `DIRTY/READY`, traiter la génération `Open/Close` (ABA), puis préparer un seul banc ASC ; ne remplacer `dist/AMOSPro_AGA.Lib` **qu'après une autorisation distincte**. B7-m2 installée, ASC validé et R84 `LAST_GOOD` inchangés, confirmés par CI. Gates B/C/D pour B8 **NON TESTÉES**. [Rapport technique](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


## 19 novembre 2026 — M19 B8 : Safe/WaitBlit et post-Close/End privés, Gate A PASS

**Sur `main` :** [`m19_b8_safe_lifecycle_emit.py`](../tools/m19_b8_safe_lifecycle_emit.py), [banc natif](../tools/test_m19_b8_safe_lifecycle_gate_a.py), [builder AP20](../tools/build_m19_b8_safe_lifecycle_in_memory.py) ; [**CI 44614557930 : PASS, 36 scénarios MC68020**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44614557930) sur deux implantations. `Exec/GetMsg` consommé une seule fois pour une notification Safe disponible (refus si absente), préservation du bit Disp, `graphics.library/WaitBlit`, revalidation de la page arrière et capture/restauration. Entrée privée post-Close/End : deux `FreeMem` au plus, seulement si le Screen réel est déjà nul ; propriétaire étranger, écran ouvert et double cleanup refusés/sûrs. **Les OS, notifications et succès Close/End sont modélisés ; aucun hook public B7-m2 n'est encore raccordé.**

**Candidate AP20 SOURCE-ONLY : 112 276 octets**, SHA256 `8800e55f0ea0865a3b8042cb8457f27bfbf7684b84ca7d90874baec472c6a744`, **86 commandes / 1104 entrées**, cinquième groupe 9 870 octets, PC16 maximal 28 938 inchangé ; les quatre anciens groupes/181 sections B7-m2 sont byte-exact. **Nouveau chantier : relier réellement Close/End B7-m2 au nettoyage B8 sans casser les callbacks/relocations, valider les échecs Safe/Disp et l'ABA, puis `Clear`/`Update` et `DIRTY/READY`.** Gates B/C/D B8 non établies, aucun `Aga Bob Clear/Update` public ni modification de `dist/AMOSPro_AGA.Lib`, `LAST_GOOD` ou de l'ASC actif. [Rapport](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


## 19 novembre 2026 — M19 B8 : gestionnaire natif privé de deux snapshots, Gate A PASS

**Réalisé sur `main` :** nouveau [coordonnateur MC68020](../tools/m19_b8_page_manager_emit.py), [test natif](../tools/test_m19_b8_page_manager_gate_a.py) et [builder AP20 source-only](../tools/build_m19_b8_page_manager_in_memory.py). [**CI 44611440112 : PASS 58 cas MC68020**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44611440112), deux placements et appels système simulés. Le service coordonne les deux BitMap réels et leur géométrie, propriétaire A5, allocations transactionnelles, captures/restaurations sur le back uniquement, validité séparée par page, refus Safe pending, pages aliasées, propriétaire étranger, snapshots périmés et rollback. Le Close privé est idempotent et sans double FreeMem ; il n'est **pas encore relié** au vrai `Screen Close`/`End`.

**Candidate AP20 en mémoire uniquement :** **111 396 octets**, SHA256 `98166666ebe11c8c7210b3f734c5615567a9eb221c7ecf440fa1c005f97add37`, **86 commandes / 1104 entrées**, cinq groupes `[142,153,156,177,181]`, cinquième groupe 9 000 octets, portée PC16 max 28 938 inchangée. Toutes les 181 anciennes sections B7-m2 restent byte-exact ; **aucun token public Clear/Update**.

**Prochain chantier :** brancher Close/End et un protocole réel Safe/Disp/WaitBlit, qualifier réouverture et ABA d'écran, puis les wrappers `Clear`/`Update` et le verrou DIRTY/READY. **Gates B/C/D non testées pour B8**. `dist/AMOSPro_AGA.Lib` B7-m2 (102 400 octets, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`), seul ASC validé (SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`) et R84 `LAST_GOOD` restent inchangés. [Rapport B8](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


## 19 novembre 2026 — M19 B8 : primitives CPU020 et cinquième unité AP20 privées PASS

**En cours, rien à installer.** Après le modèle Python 14 tests, les trois primitives natales sont testées sous Unicorn MC68020 : [copie de plans 36 cas](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44605103071), [sélecteur du back BitMap/Safe 34 cas](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44606589452), [pool de deux allocations `AllocMem/FreeMem` 52 cas](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607135635), avec appels système simulés. La candidate AP20 **4 unités** ([CI 44607378131](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607378131)) a laissé seulement **256 octets** de marge PC16 : abandon de cette organisation. La **nouvelle cinquième unité native source-only** [CI 44607784087 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44607784087) est reconstruite par [`build_m19_b8_fifth_group_in_memory.py`](../tools/build_m19_b8_fifth_group_in_memory.py) : **106 020 octets**, SHA256 `4b5371726c5eb5ac8bd1d9092c42efc41b0d74e9c8940019b9e0f6d8d0f96be3`, 1104 entrées AP20, 86 commandes, 5 groupes `[142,153,156,177,181]` ; préservation octet pour octet des 181 entrées et quatre unités B7-m2, PC16 max 28 938 inchangé. **Aucun token `Aga Bob Clear`/`Aga Bob Update` ; pas de Code d'API publique ni de Gate B/C transférée.** À faire : gérer les pages et `Safe/Disp` avec allocations réelles, raccorder Close/End, exposer puis tester Clear/Update en MC68020 et AMOS/Compiler. [Rapport et prérequis](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md). Bibliothèque B7-m2, ASC validé et R84 `LAST_GOOD` inchangés.


## 19 novembre 2026 — M19 B8 Clear/Update : référence pixel livrée, API native non intégrée

Après Gates A/B/C **PASS sur Bob Lifecycle B7-m2**, début du chantier P0 `Clear`/`Update` sur `main`. [Rapport B8](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md) ; [modèle deux pages](../tools/m19_bob_clear_update_model.py) ; [14 tests de référence](../tools/test_m19_bob_clear_update_model.py) **PASS en Python et [CI 44603406407](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44603406407)** ; politique CPU et chemins de livraison [CI 44603406558](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44603406558) PASS. Test de 405 frames, 64 Bobs, masques, chevauchements, fond dynamique sur deux pages, rejet des sources périmées et restauration après échec simulé. C'est **un modèle logiciel de vérité de pixels, PAS une Gate A native** : aucune nouvelle entrée AP20, aucun code MC68020 de Clear/Update, aucun test AMOS/WinUAE. Cible de prototype : `Clear` restaure le fond de la page arrière, `Update` prévalide/capture/dessine sans Swap implicite, fermeture propre après allocation de l'historique. Le coût d'un snapshot 320×256×8 plans est **81 920 octets/page** (163 840 pour deux), performance native encore inconnue. Bibliothèque **B7-m2 102 400 octets** SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6` et **ASC validé 10 911 octets** inchangés. R84 `LAST_GOOD` inchangée, pas d'installation native ou promotion.


## 19 novembre 2026 — B7-m2 : Gates A/B/C PASS, cycle de vie Bob clôturé sur le banc dédié

**Rapport vérifié :** [`M19_B7M2_GATES_BC_2026-11-19.md`](M19_B7M2_GATES_BC_2026-11-19.md). Lib active unique `dist/AMOSPro_AGA.Lib` B7-m2, **102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6` ; 86 commandes / 181 entrées AP20, quatre unités natives, source `tools/build_m19_b7m2_close_reset_in_memory.py::build_close_reset()`. **Gate A native MC68020 PASS** (75 groupes, [CI 44413813790](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44413813790)). **Gate B Runtime PASS** : deux lancements successifs dans la même session AMOS, sans `Erase All` ni redémarrage WinUAE (405/405 frames, 9/9 étapes, 50 Off, zéro erreur Fill/Copy/Draw/Swap, `ERR 0`, `PATH_OK` ; `RETRY_VBL` 337 et 335). **Gate C Compiler PASS fonctionnelle** : vrai exécutable compilé avec `RUN_MODE COMPILED`, `PRG_STATE -1`, `RESULT 1`, `ERR 0`, 405/405 frames, 9/9 étapes, 50 Off, 356 reprises VBL, `CLOSE_RETURNED 1`, `BANKS_ERASED 2`, `PATH_OK`. L'ancien essai compilé `ERR 1` était bloqué volontairement par le banc Runtime-only : corrigé avant le succès C. La relance du binaire compilé et les pixels complets de son rendu ne sont pas vérifiés ; **Gate D physique NON TESTÉE**. Le seul ASC `tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc` est conservé **inchangé** (10 911 octets, SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`). **`LAST_GOOD` R84 inchangée ; pas de promotion, branche, nouvelle Lib ni nouvelle API.**


## 19 novembre 2026 — Gate B B7-m2 PASS ; Gate C : banc débloqué (préflight statique attendu)

L'auteur fournit deux journaux WinUAE Runtime B7-m2 successifs dans la **même session AMOS, sans Erase All ni redémarrage** : `PRG_STATE 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `OFF_COMMANDS_ISSUED 50`, `PATH_OK` sur les deux runs. Captures : étape 8/9 64 Bobs visible. **Gate B B7-m2 PASS** pour ce scénario de cycle de vie. Un premier essai Compiler a renvoyé `PRG_STATE -1`, `ERR 1`, zéro frame : l'ASC Runtime-only avait un refus explicite `If _PRG=-1 / _ERR=1 : Goto _CLEANUP`. Le banc est corrigé sur `main` pour attribuer `_MODE$="COMPILED"` au mode -1 et réserver `ERR 1` aux modes inconnus. Le chemin de l'unique ASC reste `tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc`, désormais **10911 octets**, SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`. La Lib B7-m2 reste strictement identique (102 400 octets, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`). **Gate C vrai binaire AMOS Compiler : NON TESTÉE après correction ; prochain essai nécessaire.** Aucun changement `LAST_GOOD`, aucune promotion. [Procédure](../tests/current/README.md).


## 18 novembre 2026 — Bascule B7-m2 autorisée, Gate B WinUAE à effectuer

L'auteur a autorisé la bascule de l'unique `dist/AMOSPro_AGA.Lib` sur `main` vers **B7-m2**, 102 400 octets, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`, builder `tools/build_m19_b7m2_close_reset_in_memory.py::build_close_reset()`. Gate A native MC68020 **PASS** ([CI 44413813790](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44413813790)), 75 groupes, quatre unités, 86 commandes / 181 entrées. Le test actif `tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc` conserve son chemin et son journal historiques, mais affiche le SHA B7-m2, 10 866 octets, SHA256 `92a8dd65f5768cceaeed1cf0226e1e0e23077ec3ea9e18c2a373e9aaeba17675`. Rejouer deux fois les 405 frames sous WinUAE AGA PAL 68030/JIT ON, sauver les journaux séparément. Ancien B7-m1 : premier lancement PASS, second FAIL ERR 14. **B7-m2 Gate B encore non exécutée**. `LAST_GOOD` R84 inchangée, aucun nouveau token, aucun Compiler Gate C ni matériel Gate D. [Notice de test](../tests/current/README.md).


## 18 novembre 2026 — B7-m1 : relance FAIL, preparation B7-m2 Close-reset

Deux journaux WinUAE Runtime confirment : premier lancement PASS (405/405,
9/9, ERR 0, rendu visuel correct), deuxieme sans Erase All FAIL
(ERR 14, DRAW_FAILS 1, 0 frame). La Gate B complete n'est pas acquise.
La chaine B5 -> B7-m1 a contourne l'ancien reset des 64 slots Bob lors
de Aga Screen Close. Un suffixe source-only B7-m2, un builder AP20 en
memoire et un test CPU020 Close -> nouvelle ouverture -> Draw ont ete
prepares et Gate A MC68020 PASS (75 groupes de controles,
[CI 44413813790](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44413813790)).
Candidate source-only B7-m2 : 102 400 octets,
SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`.
Bibliotheque B7-m1, ASC actif et LAST_GOOD inchanges.
Aucune bascule binaire, aucun test Compiler. Voir le rapport
[Close/reset B7-m2](M19_B7M2_CLOSE_RESET_GATE_A_2026-11-18.md).


## 18 novembre 2026 — test Bob Off/On prêt pour Gate B Runtime

**Livrable actif :** [`tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc`](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10 866 octets**, SHA256 `faed496a977a151850255f39f0ac134bd80014975b6dcd7942b27b351c05645d`, pour **B7-m1 installée strictement inchangée** (102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`). [Notice WinUAE](../tests/current/README.md). Programmé en neuf étapes de 45 frames (2/1/0/2/4/8/16/64/16) avec `Aga Bob Off` (50 commandes émises), réactivation, masques, 2 banques (24/25), restitution locale par back buffer et journal **`RAM:M19_B7M1_BOB_LIFECYCLE.TXT`**. Aucun `Timer`, aucun benchmark, aucun essai Compiler.

**Validation :** préflight AMOS strict PASS ; 21 tests du préflight PASS ; modèle graphique de **405 scènes sur deux buffers, 6 305 segments Copy et 50 Off modélisés PASS** ; [Gate A native B7-m1 194 contrôles PASS](M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md). **Gate B du nouveau test NON TESTÉE**, Gate C Compiler et Gate D matériel NON TESTÉES. L'ancien programme décor 720 images est [conservé au commit cb3d97a](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) avec sa Gate B antérieure PASS. `LAST_GOOD` R84, l'exemple public et les sources natifs restent intacts. Branche **`main` uniquement**.

## 18 novembre 2026 — M19 Bob Off/On : nouvelle Gate A native PASS

**Décision en cours :** l'auteur souhaite poursuivre le développement de l'extension, **sans nouveau benchmark**, après publication de [l'exemple quatre Bobs](../examples/bob_local_restore/README.fr.md). Le prochain jalon technique porte sur `Aga Bob Off`, réactivation, multi-banques et cycle de vie MC68020.

**Réalisé sur `main` :** nouveau [test source `tools/test_m19_b7m1_bob_lifecycle_gate_a.py`](../tools/test_m19_b7m1_bob_lifecycle_gate_a.py) et [workflow dédié](../.github/workflows/m19-bob-lifecycle-gate-a.yml), sans modification native ni nouvelle Lib. La source vérifie **octet pour octet** que `build_multiframe()` produit `dist/AMOSPro_AGA.Lib` B7-m1 (**102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`). **[Gate A CI 44404123651](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44404123651) PASS : 194 contrôles fonctionnels comptabilisés**, deux placements natifs MC68020 (émulation Unicorn ; AmigaOS, DMA et Safe/Disp simulés).

**Scénarios PASS en Gate A :** Off Bob 1 puis Bob 2, Draw sans Bob actif, réactivation masquée/opaque dans les mêmes banques ; progressions **1/4/8/16/64** Bobs sur banques 10/11 ; réduction **64 → 16** par Off ; identité source périmée inactive ignorée et active refusée **avant Blitter** ; garde `DIRTY` empêchant `Aga Swap` ; Close/End et libérations au plus une fois. [Rapport précis](M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md). Un premier essai CI a refusé une coordonnée de banc **320** alors que le framebuffer simulé fait **65 pixels** ; la correction a ensuite PASS (ce n'était pas une anomalie du moteur).

**Suivant :** **Gate B fonctionnelle** sur un **seul ASC** (Off/On + persistance + masques, aucune mesure FPS), à préparer avant tout test WinUAE. La démo publique et l'ancien test validé dans `tests/current/` restent inchangés. **Gate B de ce nouveau jalon NON TESTÉE, Gate C vrai Compiler NON TESTÉE, Gate D matériel NON TESTÉE.** `LAST_GOOD` R84, archives, API et Lib B7-m1 inchangées ; uniquement `main`.

## 18 novembre 2026 — clôture des benchmarks, exemple Bob local et reprise M19

**Consigne de l'auteur :** arrêter les benchmarks. La dernière démonstration (quatre Bobs sur décor multicolore) devient un **programme d'exemple interactif** : [`examples/bob_local_restore/BOB_LOCAL_RESTORE.asc`](../examples/bob_local_restore/BOB_LOCAL_RESTORE.asc), **8 001 octets**, SHA256 `08edb560c4ca5c409c7d6e7f74110d05018d4f522160ea799ff43b9f3a7d470e`. Écran PAL 320×256×256, titre fixe via `Aga Text` dans y=0..31, source de fond intacte y=32..63, restauration locale sur chacune des deux pages, quatre Bobs multi-banques 24/25. Sortie touche/clic et borne automatique 2 400 frames, retour à AMOS, sans IFF, nouveau Timer ni log de benchmark. [Notices FR/EN](../examples/bob_local_restore/README.fr.md).

**Validation :** préflight AMOS strict **PASS**, 21 contrôles du préflight **PASS** ; oracle Python de **360 compositions pixel-exactes** sur deux pages, 1 696 copies simulées et 252 traversées de tuile **PASS**. C'est un **nouvel ASC** ; sa Gate B WinUAE **NON TESTÉE** malgré la Gate B PASS du banc source 720/720. Compiler C et matériel D NON TESTÉES. Dernier banc exact conservé intact dans `tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc` comme référence de régression, sans nouvelle mesure.

**Poursuite de l'extension :** [`M19_NEXT_BOB_LIFECYCLE_2026-11-18.md`](M19_NEXT_BOB_LIFECYCLE_2026-11-18.md) : qualifier `Aga Bob Off`, réactivation, multi-banques 1..64, échecs DIRTY/Swap et Close/End. Débuter par inspection source et tests MC68020 Gate A, sans nouvelles API ni benchmark. **Lib B7-m1 inchangée** : 102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, R84 LAST_GOOD protégée, branche `main` uniquement.

## 18 novembre 2026 — B7-m1 décor texturé : Gate B Runtime PASS

**Journal WinUAE reçu :** `M19_B7M1_DECOR_BENCH.TXT` (**1 216 octets**, SHA256 `d789cc71067795a801b17e2a455fa57f0db9db4468480877940056d20ec7b720`), `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, **`FRAMES_OK 720/720`**, `FILL_FAILS 0`, `COPY_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `CLOSE_CALLED 1`, `BANKS_ERASED 2`, `VERDICT PATH_OK`. Confirmation de l'auteur : **« graphiquement pas de soucis »** ; nouveau banc réel décor et quatre Bobs mobiles **Gate B PASS**. Un deuxième lancement de ce banc n'est pas documenté.

**Résultats sur 2×120 frames par cas :** A décor complet + Bobs = **239/240 ticks, 25,05 FPS** ; B décor complet seul = **240/239 ticks, 25,05 FPS** ; C restauration locale + Bobs = **123/122 ticks, 48,98 FPS**. Durée C **−48,85 %**, cadence **+95,51 %** ; surface copiée **−96,62 %**, malgré 520 Copy contre 360 en A/B. **`RETRY_VBL 719`** : durées incluant Safe/Disp, ne mesurent pas la vitesse isolée du Blitter. [Rapport avec les six séries](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md).

**Référence inchangée :** seul ASC [`tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) **9 624 octets**, SHA256 `8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904` ; Lib [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) B7-m1 **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`. **Gate A PASS, Gate B PASS sur ce scénario ; Gate C vrai Compiler et Gate D matériel NON TESTÉES**. Aucune promotion `LAST_GOOD`, changement de branche, source natif ou archive.

## Historique du 18 novembre 2026 — préparation du benchmark décor avant la Gate B

**Banc précédent à fond uni = Gate B PASS :** fichier de résultats WinUAE `M19_B7M1_CLEAR_BENCH.TXT` (SHA256 `91f272adb39713bef53359a3d75f210d5299c96d24abf0904b355fab5357258c`), `RESULT 1`, `ERR 0`, **720/720 frames**, zéro échec Fill/Draw/Swap, retour AMOS ; l'auteur confirme « ça fonctionne nickel ». Séries A **239/240 ticks**, B **240/239**, C **123/122** : C réduit le temps moyen mesuré de **48,85 %** (25,05→48,98 FPS moyens recalculés). `RETRY_VBL 719` : les résultats incluent la synchronisation Safe/Disp, **pas** le seul coût du Blitter. [Rapport détaillé](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md). L'ASC exact de ce test reste [conservé en historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/2d019a555447ab3cd294d1c4b4e69928d7afd9db/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc).

**Nouvelle campagne autorisée :** même chemin actif unique [`tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), **9 624 octets**, SHA256 `8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904`, décor non uniforme auto-généré par le Blitter (sans IFF) + quatre Bobs mobiles. A/B/C/C/B/A, 120 frames par série ; A et B copient trois fois la bande témoin 320×64, C restaure seulement les anciennes zones à partir de cette bande **sur chaque back buffer**, avec découpage y modulo 64. Journal `RAM:M19_B7M1_DECOR_BENCH.TXT` : `RUN_TICKS`, `RUN_WAITS`, `RUN_COPIES`, `RUN_COPY_PIXELS`. **PREFLIGHT PASS** et oracle exact de **720 scènes, 84 découpages de tuile, 2 480 copies simulées PASS**. [Protocole Runtime](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md).

**Gates :** nouveau banc décor **B NON TESTÉ**, vrai AMOS Compiler **C NON TESTÉ**, Amiga réel **D NON TESTÉ**. **Lib B7-m1 totalement inchangée** : `dist/AMOSPro_AGA.Lib` 102 360 octets SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`. `LAST_GOOD` R84, archives et autres dépôts protégés ; uniquement `main`.

## 18 novembre 2026 — benchmark B7-m1 A/B/C : ASC actif PREFLIGHT PASS, Runtime à mesurer

**Retour WinUAE du banc précédent :** journal B7-m1 `FRAMES_OK 120`, `ERR 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `PATH_OK`. L'auteur indique **quatre exécutions réussies sans Erase All ni traînées** et un affichage correct de deux Bobs mobiles + deux fixes/clippés ; ralentissement perçu non mesuré. **Gate B PASS pour ce scénario uniquement**, ni pour le nouveau benchmark ni pour le Compiler. [Rapport historique](M19_P0J_B7_ANIM_RUNTIME_2026-11-18.md).

**Nouveau banc sur `main` :** même chemin unique [`tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), maintenant **7 555 octets**, SHA256 `0f18cb608f75cda0390f86d25169bd4312561efd4d2051435a6803ceff42f689`, variante A/B/C (A Fill+4 Bobs, B Fill seul, C anciennes zones+4 Bobs) ; **six séries de 120 frames** dans l'ordre A B C C B A. Tous les Bobs A/C sont maintenant mobiles. `Timer` mesure les ticks à 50 Hz, sans Wait Vbl artificiel en frame réussie. Pour C, première paire de frames réinitialise les deux pages ; anciennes positions mémorisées séparément pour chaque back buffer. **PREFLIGHT PASS**, oracle géométrique double buffer 240 frames PASS. [Protocole](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md).

**Résultat à fournir :** `RAM:M19_B7M1_CLEAR_BENCH.TXT` avec `RUN_TICKS`, `RUN_FPS_X10`, `RETRY_VBL` et `ERR`, plus observation graphique (traînées/clipping). **Gate B du benchmark NON TESTÉE.** B7-m1 `dist/AMOSPro_AGA.Lib` conserve 102 360 octets, SHA256 838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403. Aucun changement à R84 LAST_GOOD, Compiler, API, archives ou branche.

## 18 novembre 2026 — B7-m1 distribuée dans la Lib de travail, Gate B Runtime à effectuer

**Bascule explicitement autorisée (« va y ») :** la candidate **M19 P0j-b7-m1** remplace la seule `dist/AMOSPro_AGA.Lib` sur `main`, **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, reconstruite octet pour octet par `tools/build_m19_p0j_end_lifecycle_in_memory.py::build_multiframe()`. 86 commandes / 181 sections AP20 / quatre unités MC68020 ; End réarmé via B7 → P0c → B7. La B7 historique SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b` reste reconstituable par `build()`, pas une autre Lib distribuée. `LAST_GOOD` R84 protégée.

**Seul ASC actuel :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) reste sous le même chemin pour garder le banc de campagne, mais porte désormais la provenance B7-m1, **4 730 octets**, SHA256 `a5a263e38faa2dfba75bf94beac4915c6ddea85e8c345f9a2f7eb0316d8190dd`. Four Bobs (banques 24/25), 120 frames, Clear → Draw → Swap ; Close explicite, effacement des banques et log `RAM:M19_B7_ANIM_RUNTIME.TXT`. Aucune seconde Lib ni second ASC.

**Gates :** [Gate A MC68020 B7-m1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44384533532) **PASS 793 contrôles multiframe**, deux placements natifs, services OS simulés ; R84 et sources B7 conservés. **Gate B WinUAE 68030/JIT ON NON TESTÉE** sur cette candidate, **Gate C non demandée/non testée**, D non testée. Le `ERR 14` précédemment observé concerne l'ancienne B7. Sous WinUAE, copier la nouvelle Lib depuis GitHub dans `APSystem`, lancer **seulement en Runtime**, sauvegarder le log avant reset puis relancer sans `Erase All`. [Protocole](../tests/current/README.md). Pas de promotion LAST_GOOD ni publication.

## Historique du 18 novembre 2026 — B7-m1 Gate A avant la bascule

**Correctif source-only :** le P0c d'origine refuse le callback B7 installé au premier Draw. Une nouvelle entrée b7_multiframe_draw_entry vérifie les pointeurs End, le contexte AMOS et la signature AGA, remplace temporairement B7/B7 par P0c/P0c, puis délègue au wrapper B7 qui réarme son callback. Refus des callbacks tiers et des paires incohérentes. [Rapport](M19_P0J_B7_MULTIFRAME_GATE_A_2026-11-18.md).

**Preuve native :** [CI 44383118836](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44383118836) PASS : 793 contrôles multiframe, 120 Draw/Swap dans chacun des deux placements MC68020, quatre Bobs, callbacks étrangers, signature, Close/End et Safe/Disp. Les 88 contrôles B7 historiques passent aussi. [CI CPU/chemins 44383118843](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44383118843) PASS. Les notifications Safe/Disp entre Swap et Draw sont acquittées par le mock : pas une preuve WinUAE.

**Protections :** unique Lib installable B7 strictement inchangée (102 072 octets, SHA256 f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b) ; R84 LAST_GOOD, ASC actif et archives inchangés. La candidate B7-m1 n'est construite qu'en mémoire, sans nouvelle Lib. Gate B/C de B7-m1 NON TESTÉES, aucun Compiler ni promotion. Le résultat ERR 14 reste celui de la B7 installée.

## 18 novembre 2026 — animation B7 Runtime uniquement

**Un seul ASC actif :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), 4 718 octets, SHA256 0f92b7ee5e1d60b1c0ab78c0d96a7d1aaebb97f3db12696a62c9a73783ad7cb6. Banc **120 frames**, quatre Bobs sur banques 24/25 : deux mobiles en aller-retour, deux fixes rognés, masque rouge et image opaque jaune, effacement du back buffer avant chaque Draw et Swap explicite. **Gate B animation NON TESTÉE ; pas de nouvel essai Compiler**. [Notice de campagne](M19_P0J_B7_ANIM_RUNTIME_2026-11-18.md).

**B7 inchangée :** dist/AMOSPro_AGA.Lib 102 072 octets, SHA256 f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b ; 86 commandes et 181 entrées AP20, Gate A MC68020 PASS 88 cas. R84 LAST_GOOD, archives et autres dépôts intacts. Le banc animation appelle **Aga Screen Close explicitement**, retourne à AMOS et efface ses seules banques 24/25. Pour la première exécution, Erase All dans une session ne contenant aucune banque utile est acceptable ; la deuxième exécution doit réussir **sans Erase All**. Journal RAM:M19_B7_ANIM_RUNTIME.TXT (FRAMES_OK 120, erreurs Fill/Draw/Swap nulles). PATH_OK seul n'est pas une preuve visuelle.

**Banc précédent :** [End sans Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0e7be49a079f75f0ac628625d567b86a3afa042d/tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc) reste inchangé dans l'historique Git. Le premier parcours rendait la main à l'éditeur ; la relance échouait avec ERR 2, expliqué par les banques AMOS encore réservées, et Erase All permettait de relancer. Cela n'établit pas une fuite de Chip RAM.


## Historique du 18 novembre 2026 — banc End sans Close (remplacé)

**Bibliothèque inchangée** : `dist/AMOSPro_AGA.Lib`, 102 072 octets, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, 86 commandes/181 entrées AP20/quatre unités. **Gate A native MC68020 PASS (88 contrôles).** Nouvelle priorité : vérifier sous WinUAE le callback automatique `End` **sans** instruction `Aga Screen Close` sur la voie nominale. [Procédure et critères](M19_P0J_B7_END_NO_CLOSE_BC_2026-11-18.md).

**Ancien ASC actif, conservé en historique** : [`tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0e7be49a079f75f0ac628625d567b86a3afa042d/tests/current/M19_P0J_B7_END_NO_CLOSE_BC_02.asc), 3 785 octets, SHA256 `35b2cfbfc7e2661bd5c7736811619547ca32127dc7e9d97794bc3403780118ae`. Réutilise quatre Bobs multi-banques masqués/opaques, Draw et Swap, puis écrit et ferme le journal **avant** `End`. Les logs `RAM:M19_B7_END_RUNTIME.TXT` et `RAM:M19_B7_END_COMPILED.TXT` portent `PRE_END_OK 1` mais **ne prouvent pas** une fermeture réussie. Il faut constater la sortie réelle vers AMOS (Runtime) ou le contexte appelant du binaire compilé, sans écran restant, Guru ni freeze, et tenter une relance. **Gates B/C de ce scénario : NON TESTÉES.**

Le [test B7 Draw + Swap + Close précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a078ed085ae14352135cfe909c3c6f06e34befca/tests/current/M19_P0J_B7_DRAW_BC_01.asc) est conservé **octet pour octet dans l'historique Git** ; la capture compilée communiquée précédemment concerne uniquement ce scénario. Ne pas déplacer ni retoucher les archives protégées sans autorisation distincte. **R84 LAST_GOOD et `dist/AMOSPro_AGA.Lib` inchangées, aucune autre branche ni nouvelle API.**


## Bascule B7 canonique pour les Gates B/C — 17 novembre 2026

**Sur autorisation explicite (« ok go »)**, la candidate B7 Gate A MC68020 PASS est maintenant livrée comme **unique bibliothèque de travail installable** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, reconstruite octet pour octet par [`build_m19_p0j_end_lifecycle_in_memory.py`](../tools/build_m19_p0j_end_lifecycle_in_memory.py). **86 commandes, 181 entrées AP20, 4 unités natives, PC16 max 28 600 octets.** `Aga Bob Draw` est exposée comme **fonction numérique 0/1 sans argument**, avec verrou `Aga Swap` et callback `End` B7. La CI refait la chaîne B7 depuis les sources figées et vérifie l'empreinte de la Lib réellement présente dans `dist/`.

**Historique, ancien ASC actif avant le banc End :** [`M19_P0J_B7_DRAW_BC_01.asc`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a078ed085ae14352135cfe909c3c6f06e34befca/tests/current/M19_P0J_B7_DRAW_BC_01.asc) (3 9104 octets, SHA256 `f411f13f8213a8ce7b72d7bf205a19cfca7d3ae3ff10087752ddf24f8af7e3af`), capture dans deux banques AMOS libres 24/25, masque index 0, quatre Bobs persistants dont deux clippés, un Draw puis Swap explicite, Close, logs `RAM:M19_B7_RUNTIME.TXT` et `RAM:M19_B7_COMPILED.TXT`. [Notice B/C](../tests/current/README.md) : WinUAE AGA PAL 68030/JIT activé, import via Project → Merge ASCII dans un programme vierge, installer le B7 unique dans `APSystem`, vérifier son SHA **sur la copie installée**, tester d'abord Runtime puis un nouvel exécutable du vrai AMOS Compiler V2.

**Statuts : B7 Gate A PASS (88 cas [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)) ; Gates B/C/D NON TESTÉES sur B7.** Le précédent test `M19_AP20_ISLANDS_01.asc`, déjà validé B/C avec l'ancienne Lib, n'a jamais été modifié et demeure [accessible au commit précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/0423b15982853630653565cee634c7d4ab5f072a/tests/current/M19_AP20_ISLANDS_01.asc) ; il est retiré de la campagne active pour n'y laisser qu'un seul fichier. **R84 LAST_GOOD (67 904 octets), archives et autre dépôt inchangés.** Un `End` avec Safe/Disp réellement différés reste un scénario Runtime/Compiler distinct non encore qualifié.



## M19 P0j-b7 — sécurisation native du callback End : Gate A PASS (88 contrôles)

Le diagnostic B6 sur **les vraies instructions natives R88** a PASS en CI ([run 44185013731](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185013731)) : Safe/Disp manquants entraînent un refus coopératif borné par `WaitTOF`, sans destruction prématurée des ScreenBuffers ou des ports ; les réponses tardives sont consommées une seule fois. **Blocage prouvé :** quand `End` finit par fermer l'écran, B6 laisse la barrière Bobs `DIRTY` persistante, contrairement à `Aga Screen Close`.

**Historique du prototype B7 avant l'autorisation de bascule** : conserver B6 (candidate 101 476 octets, SHA256 `3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91`) et les 86 tokens / 181 entrées AP20 / quatre unités ; ajouter un wrapper MC68020 de `Aga Bob Draw` qui enregistre un callback End protégé, puis contrôler la fermeture réelle. Après un End incomplet Safe/Disp, rester `DIRTY`, garder le callback pour une tentative ultérieure, **ne jamais libérer de ScreenBuffer/MsgPort en attente**. Après fermeture réelle, réinitialiser le verrou ; sous conflit de callbacks ou signature AGA End corrompue, refuser le Draw et bloquer Swap. B7 ne touche pas à la fonction AGA End historique, seulement à l'appel BOBS et à l'ancien stub Draw dans le HUNK AP20 reconstruit en mémoire.

[Source B7, tests et limites](M19_P0J_END_LIFECYCLE_GATE_A_2026-11-17.md). **Gate A MC68020 PASS : 88 contrôles** sur deux placements ([CI 44185874211](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)), après **44 contrôles de diagnostic B6** ; candidate B7 **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, source native BOBS **21 544 octets**, SHA256 `4f5305f4b42e0af0b30e557adaf38b92fb2347e598dc123c9e7bb11002a4afbf`, **86 commandes, 181 sections, quatre unités**, portée PC16 maximale 28 600 octets. Le workflow de politique CPU/chemins est également PASS. **Gates B/C/D non testées.** Cette ligne décrit la Gate A source-only historique avant la bascule autorisée signalée en tête de cette page ; le binaire et l'ASC ont depuis été remplacés pour les essais B/C, mais `LAST_GOOD` et les archives restent inchangés.


## M19 P0j-b6 — fonction numérique `Aga Bob Draw` : Gate A PASS (52 contrôles)

[Builder AP20 et protocole](M19_P0J_PUBLIC_DRAW_API_GATE_A_2026-11-17.md). Le constructeur B6 dérive strictement de la candidate B5 SHA256 `a5a08853f331b7c70d8e71eb95911bee3d8944f18feb107fda2249f10477d55e`, sans changer la source MC68020 des quatre unités ni les 180 sections précédentes. **Un seul token AMOS supplémentaire** est proposé : `_OK=Aga Bob Draw`, fonction numérique, **zéro argument**, résultat `1` si rendu complet ou `0` si refus. Son nouveau stub AP20 (index 180) pointe sur `guarded_frame_draw_entry` B5 ; le Swap public reste lui-même protégé. Le banc B6 doit vérifier GetP/ABI et relocalisation interpréteur + modèle Compiler sur deux implantations natives, images masquées, erreurs avant/après DMA et absence de Swap après refus.

**Gate A MC68020 PASS (52 contrôles)** ([CI 44183835343](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44183835343)) : candidate en mémoire **101 476 octets**, SHA256 `3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91` ; **86 commandes, 181 entrées AP20, 4 unités**, PC16 max 28 000. Gates B/C/D non exécutées. Le test AMOS actif, `dist/AMOSPro_AGA.Lib`, `LAST_GOOD` R84 et les archives ne sont pas modifiés ; ce token expérimental n'est **pas disponible dans la Lib installable**. La véritable signature AMOS Compiler V2 et les séquences Screen Close/End après Safe pending restent à valider indépendamment.

## M19 P0j-b5 — verrou de Swap après échec d'une frame (Gate A PASS 86 contrôles)

[Émetteur natif et protocole de tests](M19_P0J_SWAP_BARRIER_GATE_A_2026-11-17.md). Les trois points d'entrée **privés** sont `guarded_frame_draw_entry`, `guarded_swap_entry` et `guarded_close_entry`. La première routine active une barrière **DIRTY avant tout risque de DMA** et passe à READY seulement après le rendu complet P0j-b4 ; un refus laisse DIRTY persistant. La deuxième redirige **dans une candidate AP20 construite uniquement en mémoire** le token public existant `Aga Swap`, vérifie DIRTY/owner/State/DB/front et appelle seulement si autorisé la routine native AGA Swap originelle (signature figée, cible calculée à partir de A5+$1c8). La troisième raccorde la fermeture native P0c, sans réinitialiser DIRTY si l'écran reste ouvert. Deux stubs AP20 supplémentaires sont placés après BOBS pour respecter la portée PC16 ; **85 commandes inchangées, aucune `Aga Bob Draw` publique**.

**Politique conservatrice provisoire :** même un échec du préflight avant DMA exige Close/Reopen avant un nouveau Swap. Un Draw réussi ne peut pas lever un échec précédent. Pas de reconstruction partielle silencieuse, pas de Swap implicite. Le code n'est **ni distribué ni installé** ; Gate A MC68020 **PASS : 86 contrôles** ([CI 44182795423](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44182795423)), candidate **101 460 octets**, SHA256 `a5a08853f331b7c70d8e71eb95911bee3d8944f18feb107fda2249f10477d55e`, 85 commandes / 180 sections AP20 / quatre unités ; B/C/D non exécutées. `dist/AMOSPro_AGA.Lib`, ASC actif, `LAST_GOOD` et archives inchangés. Le futur retour AMOS public proposé est `_OK=Aga Bob Draw` (1 après rendu complet, 0 après échec), **syntaxe/token non publiés et non encore validés par le véritable Compiler**.

## M19 P0j-b4 — parcours Safe/Blitter 64 Bobs sans shadow : Gate A PASS

[Rapport et contrat d'échec](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md). **Gate A MC68020 PASS (104 contrôles natifs renforcés)** sur deux implantations AP20 V2, [CI 44179811049](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44179811049) ; premier banc 60 contrôles [CI 44174998272](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44174998272). Le parcours privé exécute P0h/P0j-a avant DMA, P0j-b2 Chip par banque, P0j-b3 masque/image par banque, puis le peintre P0d Safe/WaitBlit ; **64 Bobs pixel-exacts sur banques 10/11, zéro écriture de `bank_active_state`, aucun Swap**. **Candidate source-only en mémoire : 100 596 octets**, SHA256 `b6a318118d0f8c58ab839d905c4094b8de27b6f481d411c647626266d69a6a7b`, 85 commandes / 178 entrées / quatre unités. Source BOBS 20 104 octets, SHA256 `6cde37acbee13004acf4cf23582b267a11247c28c85011896de7570c190b60e8`.

**Risque bloquant avant Draw public :** si un échec survient après le premier Blit, le back buffer peut être partiel ; la commande n'a pas de Swap implicite, mais `Aga Swap` n'est **pas verrouillé** contre une présentation explicite ultérieure. Les tests renforcés de masque corrompu avant DMA, clipping pixel-exact et échec SafePort au deuxième Bob ont **PASS dans la Gate A 104 contrôles**. Le back partiel du cas tardif est confirmé, et le mock ne valide pas Close AGA complet avec Safe pending. Définir une politique vérifiable de page arrière invalide / reconstruction et un statut AMOS public avant toute exposition de `Aga Bob Draw`. **Gates B/C/D pour B4 non exécutées ; aucun binaire, ASC, LAST_GOOD ni archive touchés.**

## M19 P0j-b3 — descripteur d'image Chip par banque (source-only)

[Nouveau résolveur P0j-b3](M19_P0J_EXPLICIT_IMAGE_RESOLVE_GATE_A_2026-11-17.md) : reçoit D3=banque d'origine, D0=image, et rejoint l'ancien P0d après validation directe du cache Chip, sans sélection globale. **Gate A MC68020 PASS : 52 contrôles**, [CI 44174319362](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44174319362), masque transparent réel en Chip compris. Source BOBS **19 338 octets** SHA256 `ac4252e15ec04467d6789869f0f247c49249c5799276bfc07099811529d51437`, candidate AP20 **99 832 octets** SHA256 `90b5d69743bb93c5de9f97039e802e9bedd6866302e7b655efdde4c4a2f5e585`, uniquement en mémoire. B/C/D non effectuées. Le peintre P0d et le parcours de 64 Bobs restent à raccorder à cette nouvelle voie.


## M19 P0j-b2 — préparation Chip explicite, source-only

[Source et banc P0j-b2](M19_P0J_EXPLICIT_BANK_STAGE_GATE_A_2026-11-17.md). Deux fonctions privées MC68020 chargent la banque par numéro et réutilisent les validations P0c et le registre Chip sans modifier le shadow sélectionné. **Gate A MC68020 PASS : 46 vérifications**, [CI M19 44172967134](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44172967134). Source BOBS **19 208 octets**, SHA256 `1e2f5102e384e717326b3038ee3efda0ed331c2cd644e1e4d7a643e280db26ff`; candidate AP20 en mémoire **99 672 octets**, SHA256 `8e1ef5daccde882aa78adb93c13108ee0d085063540920cbecfa80b4dddaad8d` (85 commandes, 178 entrées, quatre unités). Deux banques préparées avec sélection inchangée et cache réutilisé sans copie ; P0d reste à adapter, Gates B/C non testées. Lib officielle/ASC/R84 protégés.


## M19 P0j-b1 — accès Chip explicite par banque, premier sous-jalon

[Implémentation + banc P0j-b1](M19_P0J_EXPLICIT_BANK_LOOKUP_GATE_A_2026-11-17.md). Nouvelle entrée native privée `explicit_bank_lookup_entry` : vérifie directement AGBO, génération et P0c Chip par numéro de banque, **sans consulter ni modifier `bank_active_state`**. Test source-only sur deux banques déjà préparées ; **Gate A MC68020 PASS : 68 cas**, [CI M19 44170930154](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44170930154). Code natif 18 802 octets SHA256 `6f8d3d3edc887e707288d49981019c58b640b7a1f20b2b235bf73fafaebca7cf` ; candidate AP20 source-only **99 280 octets**, SHA256 `757025bbcf846694d8ecc0377a28fa08344d9b82964501dfdc4a7f0c4b6c171e` ; B/C non exécutées. Le banc surveille les écritures dans `bank_active_state` pendant le lookup : zéro écriture autorisée. La préparation Chip et le résolveur d'image doivent encore devenir explicites avant la nouvelle commande Draw. Lib installable / ASC / LAST_GOOD protégés.


## M19 P0j-a — prévalidation des images de toute la frame (source-only)

[Implémentation et limites P0j-a](M19_P0J_IMAGE_PREFLIGHT_GATE_A_2026-11-17.md). Source native MC68020, 64 objets, banque source individuelle, ID et géométrie d'image contrôlés avant le premier Chip/Blit. Nouveau wrapper privé P0j devant le rendu P0i inchangé. **Gate A MC68020 PASS : 68 contrôles**, [CI M19 44167065047](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44167065047). Source natif P0j SHA256 `a91a0b99a05811a7f333738e1327b90a90dfe1aa947ec712d4290f568b88f618` (18 176 octets) ; candidate AP20 V2 source-only **98 652 octets**, SHA256 `4d43956a5dfbc1ae9cb1baf7058f48e6748f8bf80ef948fcc6b0a1872960a4ab`, 85 commandes/178 entrées/quatre unités ; B/C non exécutées. Les tests couvrent image absente n°64, profondeur, stride, masque et longueur des pixels corrompus avant le premier Blit. **La projection temporaire de sélection P0i est encore présente : étape explicite par banque restante.** Lib/ASC et LAST_GOOD inchangés.


## M19 P0i — rendu privé multi-banques, source-only (17/11/2026)

[Implémentation / protocole P0i](M19_P0I_MULTIBANK_DRAW_GATE_A_2026-11-17.md). Routage de chaque Bob vers la banque AGBO enregistrée (10/11 test), cache Chip P0c, Blitter P0d Safe/WaitBlit ; précontrôle P0h des 64 objets avant rendu, pas de Swap. Le shadow privé de sélection est restauré sur tous les chemins mais **le prototype n'est pas réentrant** : aucune commande publique Draw. **Gate A MC68020 PASS : 76 contrôles**, [CI M19 44163799991](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44163799991). Candidate AP20 strictement source-only **97 820 octets / SHA256 `004a04f9819fc2df9498ec8887e3de8a6533a7f620f04743c1fa1ae6ee872fa4`**. **64 Bobs réellement peints**, 32 issus de la banque 10, 32 de la banque 11, rendu pixel-exact et deux allocations Chip réutilisées. La sélection est restaurée, front non modifié et aucun Swap. Le prototype utilise néanmoins un shadow privé temporairement projeté (**non réentrant**) et peut laisser le back buffer partiel en cas de Bob invalide tardif : **ne pas exposer `Aga Bob Draw` avant correction**. Gates B/C/D non testées pour P0i. Bibliothèque canonique et ASC inchangés.


## M19 P0h — précontrôle de frame 64 Bobs (source-only)

[Source + protocole de validation P0h](M19_P0H_FRAME_PREFLIGHT_GATE_A_2026-11-17.md). Nouveau `frame_bank_preflight_entry` privé MC68020 : contrôles de 1 à 64, objets inactifs sautés, banques périmées refusées **avant tout dessin**, API et R84 inchangées. Repack AP20 par îlots pour rester loin de la limite PC16 du P0g. **Gate A MC68020 PASS : 60 contrôles**, [CI M19 44153906156](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44153906156). Candidate source-only **97 248 octets / SHA256 `2c5c371754a3b54c797c7b413769ef2536db92cdad7eba3db8185bb88dea7782`**. Aucun dessin ni préparation Chip multi-banques ici ; Gates B/C non testées pour P0h. La Lib installable reste à **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`.


## M19 P0g — nouvelle lecture privée avant Draw (17/11/2026)

Développement source-only sur `main` : [P0g lecture sécurisée](M19_P0G_CHECKED_READ_GATE_A_2026-11-17.md). Un nouveau point d'entrée BOBS relie l'`identity_check` existant à la lecture d'un objet persistant ; il refuse les banques effacées/rechargées **sans sortie partielle**, conserve la lecture brute pour distinguer inactif/périmé et ne modifie aucune commande publique. **Gate A MC68020 PASS : 52 tests, deux implantations**, [CI 44150293973](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44150293973). Candidate source-only 96 752 octets, SHA256 `e1f8f8c04e24a38651ade50b6878cffb1dd288a766b104fb5c9fa9ae314d9536`; B/C/D de cette candidate non testées. La bibliothèque installable reste la quatre-unités SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, l'ASC actif et R84 LAST_GOOD inchangés.


## M19 — nettoyage des sondes cinq unités après Gates B/C (17/11/2026)

**État actif sur `main` :** bibliothèque canonique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) revenue à la version **quatre unités fonctionnelles**, **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, **85 commandes, 178 entrées AP20**. Seul ASC actif : [`M19_AP20_ISLANDS_01.asc`](../tests/current/M19_AP20_ISLANDS_01.asc). **Gates A/B/C PASS historiques de cette image exacte**, selon les [preuves à quatre unités](M19_AP20_V2_GATES_BC_2026-11-17.md).

**Expérience à cinq unités : Gate A/B/C PASS** pour le scénario dédié `M19_AP20_UNIT5_01.asc`, résultats de deux sondes (`UNIT5_SUM 5222400` et `UNIT5_TAIL 5898757`) et quatre Bobs confirmés par les journaux Runtime (`PRG_STATE 1`) et Compiler (`PRG_STATE -1`). Observation utilisateur : image identique à la précédente, **sans nouvelle capture**. [Rapport, empreintes et limites](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md). Les sondes et les 40 Kio ne font plus partie de la bibliothèque installable, car l'unité n'avait aucune autre fonction native utile. La capacité d'ajout d'un cinquième groupe reste démontrée par l'historique et son builder, **mais non présente dans le binaire épuré**.

**`LAST_GOOD` R84 et les archives restent protégés ; aucune promotion.** La prochaine unité native supplémentaire devra être une fonctionnalité réelle et être validée indépendamment. Les sections suivantes constituent des jalons antérieurs et non le statut actuel.


## M19 AP20 V2 — CINQUIÈME UNITÉ NATIVE, GATE A MC68020 PASS (17/11/2026)

**Nouvelle expérience source-only validée sur `main` :** l'unité n°5 est **ajoutée en fin de code AP20**, sans modifier les octets ni les offsets relatifs des **178 entrées existantes** et des quatre unités déjà validées en B/C. La candidate expérimentale fait **138 044 octets**, SHA256 **`967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1`**, avec **87 commandes (dont deux fonctions de diagnostic), 181 entrées AP20 et cinq unités**. Le nouveau bloc est de 41 060 octets, dont une table de **40 Kio effectivement lue** ; son second point d'entrée est à l'offset **41 012 octets (`$A034`)**, au-delà du PC16 signé. Toutes les liaisons PC16 existantes restent identiques, maximum **854 octets**.

**Gate A réelle MC68020 : PASS**, y compris exécution de deux fonctions au travers de BSR.W interpréteur et deux modèles de relocation JSR.L Compiler, sortie `D3/D2`, pile, registres et test négatif sur les données, lors des CI [initiale 44135037050](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44135037050) et [candidate SHA-pinnée 44135445819](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44135445819). [Rapport et sources](M19_AP20_V2_FIFTH_UNIT_GATE_A_2026-11-17.md). Cette simulation n'est **pas** une compilation AMOS réelle.

**Gates B/C de la candidate à CINQ unités NON TESTÉES :** `dist/AMOSPro_AGA.Lib` reste la candidate à **quatre unités**, 96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, et **l'unique ASC actif `tests/current/M19_AP20_ISLANDS_01.asc` reste inchangé**. Les Gates A/B/C PASS précédentes et la capture de la version compilée concernent **seulement ce banc à quatre unités**. La prochaine bascule vers cinq unités demande une autorisation explicite et la validation avec le vrai Compiler V2. `LAST_GOOD` R84 protégée, Gate D NON TESTÉE, Bobs persistants/Draw/End toujours non validés.

Les sections en dessous sont des checkpoints antérieurs et ne doivent pas faire croire que les Gates B/C de la cinquième unité sont déjà PASS.

## M19 AP20 V2 — VALIDATION RUNTIME / VRAI COMPILER (17/11/2026, dernier statut)

**Gates A, B et C : PASS sur le scénario de dispatch/Blitter `M19_AP20_ISLANDS_01.asc`.** Deux journaux fournis par l'auteur le 17/11/2026 : **Runtime `PRG_STATE 1`, `RESULT 1` / `ERR 0`** et **Compiled `PRG_STATE -1`, `RESULT 1` / `ERR 0`**. Les quatre Bobs, le masque et le clipping gauche/droite passent les assertions dans les deux modes. **L'auteur précise explicitement que la capture d'écran transmise provient de la version COMPILÉE** : preuve visuelle de Gate C seulement. [Rapport d'évidence, hashes des TXT et de l'image](M19_AP20_V2_GATES_BC_2026-11-17.md).

**Candidate inchangée** : `dist/AMOSPro_AGA.Lib`, 96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, 85 commandes / 178 entrées AP20, portée PC16 854 octets, quatre unités natives. **Gate D NON TESTÉE ; ajout d'une cinquième unité, objets Bobs persistants, `Aga Bob Draw` et nettoyage `End` NON VALIDÉS.** Le SHA mentionné dans les TXT est un texte fixe du banc, pas une preuve indépendante du SHA de la copie installée.

**CI :** le test historique `tools/test_opt020_p1e_benchmark_static.py` a été corrigé le 17/11/2026 pour reconnaître la candidate AP20 dans le chemin post-R82, sans comparer l'ancienne R69 à la bibliothèque active. [CI Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/artifact-integrity.yml) pour vérifier l'état de la campagne. **Pas de promotion de `LAST_GOOD` R84**, pas d'archive ou d'autre branche. P0d reste reconstructible par son builder historique.

**Les paragraphes « Gate B/C en attente » figurant plus bas datent du checkpoint de bascule AVANT la réception des journaux. Le verdict actif est celui indiqué ci-dessus.**

## M19 — AP20 V2 ISLANDS, BIBLIOTHÈQUE DE TEST ACTIVE (17/11/2026)

**Bascule de test expressément autorisée par l'auteur le 17/11/2026** sur `main`, **sans promotion LAST_GOOD**. La bibliothèque canonique unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) est la candidate **AP20 V2 par îlots**, **96 908 octets / SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`** ; 85 commandes publiques, 178 entrées AP20, quatre unités natives conservées. Source figée P0f SHA `6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45` ; [builder](../tools/build_m19_ap20_islands_in_memory.py) et [rapport](M19_AP20_V2_DISPATCH_ISLANDS_2026-11-16.md). PC16 max **854** au lieu de **32 576** dans P0f. **Gate A MC68020 et CI M19 PASS** ([run 43973879479](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879479)), mais acceptation des stubs et unités entrelacés par le **vrai AMOS Compiler V2 NON TESTÉE**.

**Unique programme de validation actif :** [`tests/current/M19_AP20_ISLANDS_01.asc`](../tests/current/M19_AP20_ISLANDS_01.asc), dérivé du test visuel P0d avec quatre Bobs, masque, clipping, Swap, Close. [Préparation WinUAE, journaux et verdicts](../tests/current/README.md). Gates B Runtime et C vrai Compiler (WinUAE 68030/JIT ON) **EN ATTENTE DU TEST UTILISATEUR**, Gate D physique NON TESTÉE. P0d reste disponible dans le commit historique précédent et via [son builder source](../tools/build_m19_p0d_bob_blit_in_memory.py) : **91 300 octets / SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`**, Gates B/C précédemment PASS sur son propre test. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 inchangée** (67 904 octets / SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Pas de nouvelle API Draw, ni d'archive, ni de binaire alternatif.

**Critère de décision :** valider d'abord `Prg State 1` et la visibilité des quatre Bobs, puis **`Prg State -1` produit par le vrai Compiler**, avec deux journaux et même SHA installé. Ne pas confondre ce palier de dispatch avec une validation des Bobs persistants/End P0f ni des Sprites matériels.

Les sections P0d/P0e/P0f ci-dessous sont les checkpoints historiques antérieurs à la bascule de test ; elles ne décrivent plus le binaire de travail actif.

## M19 — chantier infrastructure AP20 V2 : dispatch par îlots source-only (16/11/2026)

**Priorité actuelle avant de poursuivre P0e/P0f Draw et les Sprites matériels :** tester une réorganisation durable AP20 V2, sans déplacer les grands blocs natifs. [Rapport technique](M19_AP20_V2_DISPATCH_ISLANDS_2026-11-16.md). Source nouvelle sur `main` : [remappeur](../tools/ap20_v2_island_dispatch.py), [builder](../tools/build_m19_ap20_islands_in_memory.py), [banc MC68020](../tools/test_ap20_v2_island_dispatch.py). **Gate A ciblée MC68020 et workflow M19 complet PASS** ([CI run 43973879479](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879479), commit de test `0639440`) ; politique CPU/chemins PASS ([run 43973879253](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879253)). Le vrai AMOS Compiler reste une preuve distincte.

**Candidate exclusivement reconstruite en mémoire** depuis P0f SHA `6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45` : **96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`**, **85 commandes publiques inchangées**, 178 entrées AP20, quatre unités natives conservées octet pour octet. Portée PC16 maximale **854 octets**, contre **32 576** dans P0f. Les entrées sont déplacées près de leur unité et `GetP` est replacé avant chacune ; cela suppose encore que le vrai Compiler accepte l'entrelacement des entrées et unités. **Gates B/C/D des îlots NON TESTÉES.** Les tests CPU ne simulent que l'accès au point d'entrée et la relocation, pas tout le code graphique.

**Protection stricte :** `dist/AMOSPro_AGA.Lib` reste **P0d** (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`), `tests/current/M19_P0D_BOB_BLIT_01.asc` unique et inchangé, `LAST_GOOD` R84 protégée. **Aucune bascule ni promotion autorisée par ce travail source-only.** La prochaine décision doit porter sur un test spécifique de compatibilité Runtime et vrai AMOS Compiler après autorisation de bascule du binaire unique et de son ASC ; ne pas déclarer l'architecture pérenne avant cette preuve.

## M19 P0f — banque AGBO figée par Bob, Set relié : Gate A MC68020 PASS (16/11/2026)

**Nouveau palier source-only sur `main` :** `Aga Bob N,X,Y,I` (uniquement dans la candidate en mémoire) capture désormais **l'adresse payload, la génération AGBO, la liste de banques AMOS et la taille** au moment de la création de chaque objet ; un helper privé `identity_check` vérifie par **`Bnk.GetAdr`** la banque réelle, même lorsque la sélection courante a changé. Le registre de 64 objets P0e reste octet pour octet identique ; 64 cachets de 16 octets sont ajoutés dans AGA. L'enregistrement **capture d'abord, publie l'objet ensuite, publie le cachet en dernier**, sans modifier l'ancien objet si validation ou insertion refusée. **Aucune nouvelle copie Chip ni Swap.**

**Gate A native PASS :** [50 tests](../tools/test_m19_p0f_bank_stamp_native.py) d'identité de banque, [44 tests](../tools/test_m19_p0f_object_identity_native.py) transactionnels et [40 tests](../tools/test_m19_p0f_public_bound_native.py) du vrai wrapper AMOS, sous MC68020 en deux implantations simulées ; [CI M19](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43971958606). Builder final [`tools/build_m19_p0f_public_bound_in_memory.py`](../tools/build_m19_p0f_public_bound_in_memory.py) : **96 744 octets / SHA256 `6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45`**, **85 commandes/95 entrées AP20**, **PC16 max 32 576, marge 190**, groupe AGA 61 604 sous la limite. **Deux octets de ciblage BOBS modifiés par variante source** ; le chemin P0e original et la P0d active restent inchangés. [Rapport complet](M19_P0F_BANK_IDENTITY_GATE_A_2026-11-16.md).

**À faire :** `Aga Bob Draw` doit distinguer objets inactifs vs banque périmée, prévalider tous les objets, réutiliser Safe/Chip/Blitter sans créer de banque ni Swap. Le contrôle identifie pointeur+génération mais **pas ABA avec même adresse et même génération** ; garantir l'époque d'allocation si exigée. Le reset `Aga Screen Close` P0e efface les objets mais pas encore les 64 cachets ; `End` doit être raccordé **sans hook concurrent** avec `program_end_arm/bridge` P0d. **P0f Gates B/C/D NON TESTÉES. Ne pas livrer la .Lib P0f avant la Gate A du Draw et de End et une autorisation distincte de bascule.**

**Protections inchangées :** `dist/AMOSPro_AGA.Lib` reste **P0d** (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`), `tests/current/M19_P0D_BOB_BLIT_01.asc` toujours seul, `LAST_GOOD` R84 préservée. Les sections P0e qui suivent sont des jalons historiques, non le statut actuel.

## M19 P0e — groupe AP20 réparti et Close reset : Gates A MC68020 PASS (16/11/2026)

**Le problème PC16 est résolu pour le palier `Aga Bob N,X,Y,I` + `Aga Bob Off N`.** La candidate expérimentale est **source-only**, construite en mémoire, **non installée**. Déplacement du gros pont 470 octets du groupe BOBS vers le groupe AGA, après le registre 64 objets (2 332 octets) ; BOBS conserve un relais de 332 octets, puis un nouveau wrapper Screen Close de 24 octets. Les anciens groupes natifs P0d, ses 83 commandes, son dessin Safe/Chip/Blitter et son ABI sont conservés **octet pour octet en préfixe**. La distance interpréteur RBSR maximale est **32 576**, marge **190 octets** (contre 32 760, marge 6 avant répartition).

**Candidate mémoire source vérifiée : 94 532 octets / SHA256 `8185ae2d056da209a88c0b91e315d1cbb97acabadf7b55352e8cd7a348c1b207`** ; **85 commandes / 95 entrées AP20**. Builders : [`tools/build_m19_p0e_split_public_in_memory.py`](../tools/build_m19_p0e_split_public_in_memory.py) et [`tools/build_m19_p0e_split_close_in_memory.py`](../tools/build_m19_p0e_split_close_in_memory.py). [Gate A pont native PASS 56 cas](../tools/test_m19_p0e_split_bridge_gate_a.py) ; [Gate A reset avant original Screen Close PASS 16 cas](../tools/test_m19_p0e_split_close_gate_a.py), deux implantations MC68020 avec vraie initialisation et vraie fermeture natives AGA, services OS simulés. [CI M19 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43969689292). **Ce PASS n'est PAS un essai WinUAE ni un vrai exécutable AMOS Compiler.** [Rapport complet](M19_P0E_SPLIT_AP20_CLOSE_GATE_A_2026-11-16.md).

**À faire impérativement avant toute candidate P0e installable :**
- `Aga Bob Draw` : itération des objets 1..64, partage d'images Chip sans recopie, *banque source de chaque objet* (pas celle sélectionnée par le programme courant), Blitter vers le back buffer Safe P0d, clipping/masque, aucun Swap implicite.
- Stocker l'**identité/génération de la banque source** lors de `Aga Bob` (la sixième Long du slot est actuellement réservée) puis refuser tout `Erase/Load` périmé. Ne jamais recréer une banque absente pendant Draw. Cette absence de verrou d'identité est un blocage de sûreté, **pas une option de confort**.
- Reset au callback `End` **sans conflit avec les hooks d'End déjà armés par P0d**, ni régression de la commande publique P0d `Aga Bob Blit`.
- Nouvelle Gate A du moteur complet et de chaque nouvelle entrée AP20 (marge actuelle seulement 190 octets), avant **demande séparée d'autorisation de bascule `.Lib`/ASC** ; Gates B Runtime, C véritable Compiler et D matériel indépendantes.

**Protections :** `dist/AMOSPro_AGA.Lib` **P0d inchangée** (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`), son seul ASC `tests/current/M19_P0D_BOB_BLIT_01.asc` inchangé, `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 intacte. Les sections précédentes ci-dessous sont des checkpoints historiques ; elles peuvent contenir une ancienne contrainte PC16 ou un ancien état sans Close reset.

## M19 P0e — wrappers publics Set/Off Gate A, réserve PC16 épuisée (16/11/2026)

**Dernier palier sur `main` :** les deux nouveaux tokens expérimentaux **`Aga Bob N,X,Y,I`** et **`Aga Bob Off N`** ont été ajoutés **uniquement à un constructeur de bibliothèque en mémoire**, depuis la source exacte du pont P0e (sha `f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de`). [Wrappers natifs MC68020](../tools/m19_p0e_public_object_ops_emit.py), [builder AP20 V2](../tools/build_m19_p0e_public_object_ops_in_memory.py), [tests CPU020/ABI](../tools/test_m19_p0e_public_object_ops_gate_a.py) et [rapport détaillé](M19_P0E_PUBLIC_OBJECT_OPS_GATE_A_2026-11-16.md). **Gate A PASS : 48 contrôles** natifs des wrappers publics et deux placements mémoire, plus les 60 contrôles préexistants du pont, tokens/GetP/HUNK/Compiler V2 statiques vérifiés. Les services Amiga/WinUAE ne sont pas exécutés ; **B/C P0e NON TESTÉES**. `Aga Bob Draw` et l'effacement des objets lors de `Close/End` **ne sont PAS implémentés**.

**Candidate privée non installée :** **94 232 octets, SHA256 `a1aab227dd8c1e19be88f11878513f341edfc92bf19f33520a029625a3827969`**, **85 commandes / 95 entrées AP20**, +38 octets natifs BOBS. **RBSR PC16 maximal 32 760, marge seulement 6 octets**. Le stub **n°0**, spécial/ancien, est la contrainte dominante ; on ne peut pas le déplacer librement. [Banc négatif Draw](../tools/test_m19_p0e_pc16_draw_rejection.py) : l'ajout naïf d'un troisième stub de seulement huit octets ferait **32 768**, dépassement signé et refus ; ce contrôle structurel empêche les ajouts non sûrs. **Prochain travail : redistribuer les unités natives AP20 pour récupérer de la portée depuis le stub 0, avant tout nouveau token**. En particulier déplacer/compactifier le pont privé BOBS, voire le faire résider dans le groupe AGA via une ancre validée et un petit trampoline ; conserver source/ABI/End/Close et tester les deux modes. Pas de simple `append` supplémentaire au groupe BOBS.

**Priorités après restructuration :** écrire `Aga Bob Draw` (objets 1..64, banques historiques distinctes, sélection/restauration contrôlée, staging Chip sûr après Erase/Load, Blitter P0d Safe/masque/clipping, **sans Swap implicite**) ; intégrer `object_reset` à la fermeture écran et au callback End **avant** destruction de l'AGA State ; nouvelle Gate A complète avant toute demande de bascule candidate installable. L'actuelle sélection de banque P0d est privée et sa revalidation reste nécessaire. Ne pas confondre les wrappers PASS avec un moteur de Bobs persistants livré.

**Protection maintenue :** seule `dist/AMOSPro_AGA.Lib` **P0d** (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`) reste installable, avec ses Gates B/C utilisateur PASS. `tests/current/M19_P0D_BOB_BLIT_01.asc` est toujours le seul ASC actif ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 jamais modifiée. Les sections ci-dessous sont des jalons historiques.

## M19 P0e — pont BOBS-AGA source-only, Gate A MC68020 PASS (16/11/2026)

**Pont de relocation V2 développé sur `main` et testé**, toujours **sans nouvelle bibliothèque installée**. [Émetteur](../tools/m19_p0e_v2_object_bridge_emit.py) : **502 octets natifs MC68020 ajoutés en mémoire au groupe BOBS**, cinq entrées privées (`put_selected`, `put`, `off`, `read`, `reset`). La variante `put_selected` lit **le vrai `bank_active_state` BOBS** sous garde CPU, conserve le numéro de banque dans un objet P0e stocké côté AGA ; les autres entrées utilisent l'ABI du registre de 64 Bobs. Le pont obtient la base native AGA via **`A5+$1C8`** (initialisation AGA réelle), vérifie `State-$168` signature End, `State+56130` code P0e, `TypeOfMem` sur les pointeurs et les 16 octets de la signature P0e, avant `JSR` dans la seconde unité. Aucune adresse absolue imposée et aucun Swap/DMA.

**[Gate A MC68020 du pont PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43966602587)** : **60 contrôles** natifs, **vraie initialisation AGA source-pinnée exécutée** et BOBS/AGA placés séparément en deux implantations simulant interpréteur/Compiler. Refus : CPU<020, propriétaire A5 étranger, banque nulle, état écran fermé, cible/signature altérée, pointeur non mappé, sauvegarde ABI/stack et absence de mutation après échec. Les services OS restent simulés : **pas de Gate B/C du nouveau pont**. [Builder mémoire](../tools/build_m19_p0e_v2_bridge_in_memory.py) source exact : **94 144 octets SHA256 `f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de`**, **83 commandes et 93 entrées AP20 inchangées**, groupe BOBS 23 614, AGA 58 912, et **PC16 maximal 32 698 (seulement 68 octets sous limite de contrôle 32 766)**. [Rapport détaillé et blocages](M19_P0E_V2_CROSS_UNIT_BRIDGE_GATE_A_2026-11-16.md).

**Prochaine étape (pas encore autorisée en livraison installable) :** créer une structure AP20 V2 permettant plusieurs **nouveaux tokens publics** sans dépasser PC16 ; `Aga Bob N,X,Y,I` appellera le pont vers l'objet avec banque sélectionnée ; `Aga Bob Off N` le désactivera ; `Aga Bob Draw` parcourra 1..64 et réutilisera **P0d Safe/Chip/Blitter**, sans Swap implicite. Ajouter au **vrai Close/End** le reset d'objets AVANT destruction de AGA State ; vérifier `Erase/Load` et l'identité de banque avant le rendu. Nouvelle Gate A de candidate complète requise **avant demande de bascule .Lib/ASC**. Toutes les mentions plus anciennes d'un « pont manquant » ci-dessous sont des checkpoints historiques.

**Protections :** `dist/AMOSPro_AGA.Lib` **P0d toujours active** (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`), **Gates A/B/C P0d PASS**, le seul ASC `tests/current/M19_P0D_BOB_BLIT_01.asc` inchangé et `LAST_GOOD` R84 intacte. Aucune promotion ni autre branche.

## M19 P0e — registre privé des Bobs persistants : Gate A MC68020 PASS (16/11/2026)

**Cible active toujours P0d**, `dist/AMOSPro_AGA.Lib` (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`), seul ASC `tests/current/M19_P0D_BOB_BLIT_01.asc`, R84 `LAST_GOOD` intacte. Les **Gates B/C P0d sont désormais PASS** selon deux fichiers TXT reçus directement (`PRG_STATE=1` et `-1`, `RESULT=1`, `ERR=0`) **et confirmation visuelle explicite de l'auteur** des quatre Bobs, masque et clipping. [Preuves et limites](M19_P0D_GATES_BC_2026-11-16.md) : aucune capture jointe ni SHA indépendant de la copie installée ; Gate D physique NON TESTÉE.

**Nouveau travail P0e livré sur `main` — source-only privé, non installé :** [`tools/m19_p0e_object_table_emit.py`](../tools/m19_p0e_object_table_emit.py) gère **64 objets** indexés, banque/image/X/Y/actif, ordre par ID, réutilisation de la même image, Off, relecture et reset ; **2 332 octets natifs MC68020**, pas de nouvelle banque AMOS, pas de copie Chip, pas de DMA. [Gate A CPU020 PASS : 316 cas / deux placements](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43964286301) avec contrôle ABI, propriétaires A5, bornes, Off, reset, CPU refusé. [Builder source P0e](../tools/build_m19_p0e_object_table_in_memory.py) **Gate A AP20 PASS** : ajout privé en fin de groupe AGA V2 92, groupe 58 912 octets (limite 65 534), candidate **en mémoire uniquement 93 632 octets / SHA256 `588345837105bdade12f8ab289b8a46f22cd1be5f9a14c8f88ca9f2220e28790`**, table P0d 83 commandes/93 entrées inchangée ; déplacement RBSR max 32 196 identique. [CI AP20](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43964566218). **Aucun token `Aga Bob`, `Aga Bob Off` ou `Aga Bob Draw` n'a été installé.**

**Prochaine étape technique :** établir et tester un pont de relocation sûr entre le registre P0e du groupe AGA et le registre de banque sélectionnée/staging/painter P0d du groupe BOBS ; l'objectif public reste `Aga Bob N,X,Y,I` (banque source capturée à la création), `Aga Bob Off N`, puis `Aga Bob Draw` (tous les objets actifs dans le back buffer après restauration du fond par l'application, aucun Swap implicite). **Ne pas ajouter les nouveaux objets dans BOBS** : marge PC16 existante de seulement 570 octets. Inspecter l'ancre source-validée du callback End AGA sans l'utiliser avant preuve CPU/Compiler. À implémenter et soumettre à Gate A complète **avant toute nouvelle autorisation de bascule .Lib/ASC**. Rapport détaillé : [`docs/M19_P0E_OBJECTS_GATE_A_2026-11-16.md`](M19_P0E_OBJECTS_GATE_A_2026-11-16.md).

## M19 P0d — candidate installable active pour Gates B et C (bascule autorisée le 16/11/2026)

**Bascule P0c → P0d expressément autorisée par l'auteur**, sur `main`. Seule bibliothèque de campagne : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **91 300 octets**, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`, **83 commandes / 93 entrées AP20**, reconstruite octet pour octet par [`tools/build_m19_p0d_bob_blit_in_memory.py`](../tools/build_m19_p0d_bob_blit_in_memory.py) depuis la base P0c source-vérifiée. Seul ASC actif : [`tests/current/M19_P0D_BOB_BLIT_01.asc`](../tests/current/M19_P0D_BOB_BLIT_01.asc). L'ancien ASC P0c demeure dans l'historique Git sans duplication ni archivage forcé ; son code est remplacé uniquement dans `tests/current/`.

**Première fonction publique :** `_OK=Aga Bob Blit(_I,_X,_Y)` (image AGBO de la banque choisie, préparation Chip paresseuse au premier appel, masque indépendant, vrai back buffer AGA Safe, Blitter/WaitBlit, aucun Swap implicite, callback End armé et synchronisé). **Ce n'est pas encore l'API des objets Bob persistants.**

**Statuts : Gate A native MC68020 PASS (108 scénarios publics, API/ABI et code réel exécuté sous Unicorn, OS/graphics/DMA simulés)** ; préflight ASC strict PASS ; **Gate B Runtime WinUAE NON TESTÉE ; Gate C réel AMOS Compiler NON TESTÉE ; Gate D physique NON TESTÉE**. [Rapport et provenance](M19_P0D_PUBLIC_BOB_BLIT_GATE_A_2026-11-16.md) · [protocole d'installation et contrôle visuel](../tests/current/README.md). Tester WinUAE AGA PAL 68030/JIT ON, installer et vérifier SHA du fichier réel en `APSystem`, puis import dans un programme vide via `Project → Merge ASCII`, exécuter Runtime `PRG_STATE 1` et Compiler `PRG_STATE -1`, observer quatre Bobs/clipping, lire `RAM:M19_P0D_RUNTIME.TXT` et `RAM:M19_P0D_COMPILED.TXT`.

**Protections :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` **strictement inchangée** ; ni promotion, ni release, ni autre dépôt ou branche. P0c Gates B/C historiques valent uniquement pour le test Screen Close de P0c. **Toutes les sections plus anciennes ci-dessous (P0d source-only / P0c active) sont des checkpoints historiques, non le statut installable actuel.**


## M19 P0d — premier Bob public AP20/MC68020 Gate A PASS (16/11/2026)

**Nouveau jalon sur `main`, SOURCE-ONLY :** fonction expérimentale `_OK=Aga Bob Blit(_I,_X,_Y)`, **premier Bob immédiat** sur le back buffer AGA avec `Aga Swap` strictement explicite. L'objet Bob persistant `Aga Bob N,X,Y,I` du contrat fonctionnel **n'est pas encore développé**. La sélection `Aga Bob Bank N` accepte toujours une banque vide ; à la première fonction `Aga Bob Blit`, le wrapper [source MC68020](../tools/m19_p0d_public_blit_emit.py) prépare la banque AGBO en Chip après vérification, arme le callback P0c `End`, réutilise les données aux appels suivants, reconstruit après changement de génération et lance [le pont Safe/Blitter P0d](../tools/m19_p0d_safe_bank_blit_emit.py). **Écart assumé du contrat cible :** préparation initiale différée au premier dessin, et non dès la sélection de banque, afin de préserver le cas création de banque vide ; à évaluer pour la future API de préparation anticipée.

**[Gate A publique CPU020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43959009697) :** **108 scénarios** du wrapper public natif + ABI AMOS (3 paramètres numériques, `A3` avancé de 8), `End` armé, 2 banques, profondeur 1/4/8, masques, clipping, restaging, Safe, refus sans Double Buffer/CPU 020. Régressions privées : 720+90+84 scénarios. [Politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43959010076). Tous les appels OS/graphismes et DMA sont **simulés dans les Gates A**. [ASC de conception](../tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc) **préflight strict PASS**, pas activé et sans test WinUAE/Compiler.

**Candidate AP20 V2 uniquement en mémoire** par [builder P0d source-backed](../tools/build_m19_p0d_bob_blit_in_memory.py) : **91 300 octets**, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`, **83 commandes, 93 entrées**, fonction `aga bob blit` index **88**, BOBS groupe **91**, entrée native **22 688**, ancien groupe AGA conservé au nouveau numéro 92. **Marge RBSR signée faible : déplacement maximal 32 196** ; ne pas poursuivre par ajout aveugle d'autres fonctions au même groupe. Rapport complet : [`docs/M19_P0D_PUBLIC_BOB_BLIT_GATE_A_2026-11-16.md`](M19_P0D_PUBLIC_BOB_BLIT_GATE_A_2026-11-16.md).

**Prochaine étape :** obtenir **autorisation explicite de bascule** P0c→P0d dans `dist/AMOSPro_AGA.Lib` et du seul ASC `tests/current/` **après** Gate A ; ensuite WinUAE **B Runtime** et **C vrai Compiler** avec banc visuel autonome et logs. **Aucune bascule ni promotion faite.** Canonique actuel P0c : 87 020 octets, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` inchangé ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 intacte. Les sections P0d précédentes ci-dessous sont les checkpoints du moteur privé avant ce wrapper public.

## M19 P0d — image AGBO réelle préparée → back buffer AGA Safe → Blitter : Gate A privée PASS (16/11/2026)

**État exact sur `main` :** trois nouveaux composants sources natifs **MC68020 minimum**, tous **privés et non intégrés à la .Lib installable** :

- [Résolveur image AGBO → allocation Chip P0c](../tools/m19_p0d_bank_image_resolve_emit.py) : valide par `registry_lookup_entry` la banque AMOS sélectionnée, l'identité/génération AGBO et les bornes de l'image/masque avant de produire un descripteur de 36 octets. **988 octets** natifs append-only ; [90 scénarios CPU020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43953867237) sur deux placements du code, incluant banque modifiée, invalide ou non sélectionnée, opaque et masquée.
- [Peintre Chip → graphics.library Blitter](../tools/m19_p0d_private_blit_emit.py) : maintenant **2 214 octets** ; [720 scénarios pixel-exacts + 4 refus PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43954837037) en 1/4/8 plans, largeurs 1/17/31/32/37, pixels non alignés, masques indépendants. **Correctif nécessaire issu du banc intégré : clipping selon la largeur/hauteur logiques de l'écran, non `BitMap.BytesPerRow*8` qui inclut le padding**. Dimensions logiques passées par A3, validées contre les dimensions physiques ; A3 préservé par l'appelant.
- [Pont Safe / buffer inactif → peintre](../tools/m19_p0d_safe_bank_blit_emit.py) : **664 octets** de wrapper ; [84 scénarios CPU020 intégrés PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43954837037), écran 65 pixels avec stride physique 96, toutes géométries, deux placements V2 simulés, les deux orientations du double buffer, SafePort prêt ou indisponible, masque, absence de Swap implicite et fermeture P0c. Lit **l'état AGA réel `A5+0x1C8`**, `State+32` DBState et le `ScreenBuffer.sb_BitMap` opposé au front, après contrôle de `Safe`. Utilise `GetMsg` non bloquant, **aucun `ReplyMsg`, WaitPort ou `Aga Swap`**.

**[CI complète M19 Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43954837037)** et [politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43954837048). Les trois bancs exécutent réellement les instructions 68020 sous Unicorn, mais **AMOS/Exec/Intuition/graphics et les effets DMA sont simulés**. Pas de preuve d'exécution WinUAE Runtime (Gate B), véritable AMOS Compiler (Gate C) ou Amiga physique (Gate D) pour le nouveau rendu. La Gate A du **préfixe P0c installé** reste indépendante de la Gate A des nouveaux appendices privés.

**Blocage avant un Bob visible depuis AMOS :** aucun token public ne déclenche encore le `registry_prepare_entry`, `program_end_arm_entry` puis `safe_bank_blit_entry`. La sélection publique actuelle `Aga Bob Bank N` gère seulement métadonnées et banque ; elle ne prépare pas encore Chip. Une intégration AP20 / Compiler V2 avec signature d'API **à valider spécifiquement** est nécessaire, suivie d'une Gate A de **l'ensemble exact candidat** et d'une bascule explicitement autorisée de la seule `dist/AMOSPro_AGA.Lib` et du seul ASC `tests/current/` avant Gates B/C. Pas de nouveau binaire alternatif ni artefact CI installable.

**Protections :** `dist/AMOSPro_AGA.Lib` P0c **87 020 octets, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`**, `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 sont inchangés. Aucun nouveau `.asc` actif, aucune promotion, aucun dépôt/branche supplémentaire. La section P0d suivante documente le premier peintre **20104 octets avant correction du clipping** : elle est conservée comme checkpoint historique, pas comme état du noyau courant.

## M19 P0d — premier noyau Blitter Bob AGA privé : Gate A MC68020 PASS (16/11/2026)

**Source-only sur `main`** : [`tools/m19_p0d_private_blit_emit.py`](../tools/m19_p0d_private_blit_emit.py) construit un noyau privé de dessin **2 0104 octets, MC68020 minimum**, sans token AP20, sans nouvelle `.Lib`, sans ASC supplémentaire. [Banc natif](../tools/test_m19_p0d_private_blit_native.py) : **720 scénarios pixel-exacts** (profondeurs 1/4/8, largeurs 1/17/31/32/37, masques transparence index 0/non nul ou opaque, clipping, deux placements du code) + **4 refus** (source Fast, profondeur incompatible, stride invalide, CPU sans AFF_68020). [CI ciblée complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43952569895), incluant le noyau sous Unicorn MC68020 et le garde ABI. Les services Exec/graphics et les transferts Blitter sont **simulés** : cette Gate A ne valide ni le DMA réel, ni WinUAE, ni le Compiler.

**Contrat privé du peintre :** source AGBO planaire *déjà préparée en vraie Chip par P0c*, masque 1 bit indépendant, BitMap back **déjà sécurisé par Safe**, `BltBitMapRastPort` opaque ou `BltMaskBitMapRastPort` masqué, `WaitBlit` avant retour, aucun `Aga Swap` automatique. Le noyau refuse les profondeurs source/écran différentes et ne gère pas le buffer, la sélection d'image, l'identité/génération de banque, les objets persistants ou la récupération des notifications Safe. **Un appelant natif vérifié doit encore le relier au registre P0c et au vrai back buffer AGA**, avec contrôle intégral des plages source/masque et de leur propriété avant DMA. Ne pas présenter ce noyau privé comme un Bob déjà affichable par une commande AMOS.

**Prochaine action :** auditer le chemin `Aga Bob Bank` existant et l'ABI AP20, puis intégrer une préparation Chip déclenchée en contexte public et un rendu Bob unique dans le back buffer sûr. Passer Gate A **sur le candidat complet** avant de demander une bascule explicitement autorisée de `dist/AMOSPro_AGA.Lib` et du seul ASC actif. Tests réels Gates B/C uniquement après cette bascule. **P0c 87 020 octets / SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`**, `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`, et R84 `LAST_GOOD` restent inchangés ; aucune promotion, pas d'archive, ni de nouveau binaire.

## M19 P0c — journaux Gates B et C PASS (16/11/2026)

Deux fichiers transmis par l'auteur : **`M19_P0C_RUNTIME.TXT`** (`PRG_STATE 1`) et **`M19_P0C_COMPILED.TXT`** (`PRG_STATE -1`). Dans **les deux** : `RESULT 1`, `ERR 0`, `VERDICT PASS` et `CLOSE_FIRST`, `CLOSE_WITH_DB`, `CLOSE_REOPEN` à **1**. **Gate A MC68020 PASS ; Gate B Runtime et Gate C Compiler PASS selon ces journaux** pour les trois séquences de fermeture. [Preuves, SHA256 des deux TXT et limites](M19_P0C_GATES_BC_2026-11-16.md).

Bibliothèque de travail **inchangée** : `dist/AMOSPro_AGA.Lib` P0c, **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; seul ASC `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` **inchangé**. Les TXT n'attestent ni l'empreinte de la copie installée dans WinUAE, ni les captures/CPU/JIT/ligne d'écran, ni le retour après dernier `End`. Callback End privé, interpréteur strict et Gate D **NON TESTÉS**. `LAST_GOOD` R84 intacte, aucune promotion. **Les sections antérieures ci-dessous sont des checkpoints historiques.**

## M19 P0c — CANDIDATE ACTIVE pour Gates B/C (autorisation du 16/11/2026)

**Bascule autorisée sur `main`** : binaire unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; **104 commandes / 92 entrées AP20**, source [builder P0c](../tools/build_m19_p0c_screen_close_in_memory.py) dérivée du P0b figé. **Seul ASC actif** : [`tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`](../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc) ; son design reste inchangé. Gate A native MC68020 PASS ; Gates B Runtime WinUAE et C vrai AMOS Compiler **NON TESTÉES**, Gate D NON TESTÉE. CPU 68030/JIT ON pour essais fonctionnels. **Aucune promotion `LAST_GOOD`** (R84 SHA inchangé), ni publication/ZIP/artefact CI. Le test actif P0b quitte `tests/current/` et reste accessible par Git, sans archivage forcé.

**Actions :** installer la Lib canonique dans le slot AGA d'AMOS, redémarrer, importer l'ASC par `Project → Merge ASCII`, exécuter Runtime puis Compiler et recueillir deux journaux distincts. [Protocole complet](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md). **Les sections P0c/P0b qui suivent sont des checkpoints historiques antérieurs à cette bascule**, et ne désignent plus la candidate ou l'ASC actif.



## M19 P0c — Screen Close public + callback End privé : Gate A MC68020 PASS (16/11/2026)

**CORRECTIF DE DISTRIBUTION (16/11/2026) :** ne plus distribuer P0c par l'artefact CI `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED`, ni l'exécuter directement depuis `tests/design/`. La règle est **une seule Lib dans `dist/AMOSPro_AGA.Lib` et un seul ASC dans `tests/current/` sur `main`**, uniquement après autorisation explicite du remplacement de P0b. Le workflow conserve les vérifications Gate A **en mémoire** sans exporter de `.Lib`. P0b, son test actif et `LAST_GOOD` restent inchangés ; **Gates B/C P0c en attente**. [Consignes à jour](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md).

**Nouveau candidat expérimental source-only (NON INSTALLÉ dans `dist/`)** : [builder AP20 V2](../tools/build_m19_p0c_screen_close_in_memory.py), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 104 commandes, 92 entrées AP20. Seuls le stub public `Aga Screen Close` (token 8) et le groupe BOBS 90 append-only changent ; groupe AGA 91 et API P0b restent intacts. Le vrai AGA Init, la vraie routine Screen Close et le vrai callback AMOS End sont exécutés sous Unicorn MC68020 avec services OS mockés. Pont `A5+0x1C8` → AGA State → ancienne routine Close (`+0x638`) sans BSR.W inter-unités ; libération Chip via `WaitBlit` **avant** l'ancienne fermeture. [Source Screen Close](../tools/m19_p0c_screen_close_bridge_emit.py) et [source End privé](../tools/m19_p0c_program_end_bridge_emit.py).

**[CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925480841) :** 38 scénarios réel Close, 54 scénarios End privé, 42 preclose, 64 registre, 120 AGBO/Chip, 64 Chip, 116 P0b ; [ASC de design préflight PASS](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc). [Rapport de Gate A](M19_P0C_SCREEN_CLOSE_BRIDGE_GATE_A_2026-11-16.md). L'artefact `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED` produit par cette **ancienne exécution** est une preuve historique ; il ne constitue pas un canal de distribution autorisé et les futurs runs n'en produisent plus.

**Verrou maintenu :** le callback `End` n'est armé que par l'entrée **privée** `program_end_arm_entry`, après staging Chip ; les commandes AMOS P0b ne préparent pas de Chip Bob et **ne l'appellent pas**. Il n'existe toujours pas de véritable rendu Bob ni de commande publique staging. **Gate B Runtime et Gate C Compiler P0c NON TESTÉES** ; aucune affirmation de fonctionnement de la Lib installée. Le test de design reste NON ACTIF ; ne lancer aucune Gate B/C P0c avant une bascule explicitement autorisée de la bibliothèque et de l'unique ASC courant. `dist/AMOSPro_AGA.Lib` P0b (104 376 octets) et R84 `LAST_GOOD` inchangées.

## M19 P0c — garde de pré-fermeture AGA natif, Gate A privée PASS (16/11/2026)

**Nouvelle source native MC68020 :** [`tools/m19_p0c_screen_preclose_emit.py`](../tools/m19_p0c_screen_preclose_emit.py), émetteur **source-only**, append-only sur le [registre P0c](../tools/m19_p0c_bank_registry_emit.py). Il ajoute `screen_preclose_entry` : vérification CPU/état, récupération de la base graphique **depuis `A5+0x1C8` → `State+8`** (et non le A4 du caller), contrôle de l'adresse de l'état, nettoyage des contextes Chip via `registry_close_entry`. Si le nettoyage échoue, il retourne **0 sans fermer l'écran** et sans écraser les allocations. Si le registre est vide, la fermeture répétée retourne **1**. **Le vrai `CloseWindow`/`CloseScreen` n'est jamais exécuté par cette entrée privée.**

**[CI Gate A privée PASS — 42 scénarios MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43920983278)** ([test](../tools/test_m19_p0c_screen_preclose_native.py)), unité BOBS privée **11 294 octets**, préfixes natifs P0b/P0c immuables. En régression dans la même CI : **64 PASS** registre, **120 PASS** AGBO/Chip, **116 PASS** API P0b, politique CPU/livraison séparée. Erreur initiale corrigée : une adresse temporaire `State+8` était prise à tort pour `GfxBase` en l'absence de celui-ci ; une variable de frame distincte évite tout appel `WaitBlit` sur ce faux pointeur.

**Point de liaison précisément identifié (non résolu)** : le token AP20 **`Aga Screen Close` est n°8, ciblant le groupe AGA V2 n°91, offset 2008**. Le registre BOBS est dans le groupe n°90. Le source `src/R88/*AGA_NATIVE.s` n'est qu'une **restauration mnémotechnique partielle d'audit** : interdit de l'utiliser pour patcher le vrai code de production. Le module AGA R88 comporte **56 580 octets de natif**, donc un simple `BSR.W` depuis BOBS n'est pas une solution à supposer. **Aucun hook automatique n'a été installé** sur la véritable commande de fermeture ni sur l'**End AMOS**. La fermeture du test est un modèle d'ordre d'appels et **non** l'exécution du Close historique réel.

**Suite bloquante :** retrouver/construire une liaison **source-auditée** entre le groupe AGA et l'entrée privée BOBS, avec contexte `GfxBase` vivant, et tester sur le *même candidat exact* l'entrée publique `Aga Screen Close`, le cleanup de sortie du programme et les relocations V2, avant toute nouvelle `.Lib` ou essai WinUAE/Compiler. Le binaire **P0b 104 376 octets** (SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`), R84 `LAST_GOOD` et l'unique ASC P0b validé restent **intacts**.

## M19 P0c — registre natif automatique de Chip par banque : Gate A privée 64 PASS (16/11/2026)

L'[émetteur du registre MC68020](../tools/m19_p0c_bank_registry_emit.py) ajoute **quatre points d'entrée privés** au préfixe P0b/P0c inchangé : préparation, lookup, libération d'une banque et fermeture globale. Un nœud **Exec AllocVec 32 octets, MEMF_PUBLIC|MEMF_CLEAR** par banque référence le contexte Chip 20 octets, sans banque AMOS supplémentaire ; l'état natif persistant mémorise **A5 propriétaire + tête de liste**. Une nouvelle entrée n'est chaînée **qu'après** réussite de la validation AGBO et de la préparation Chip. Les libérations attendent le Blitter via le helper P0c existant ; les boucles sont bornées à **256 contextes** et la fermeture est idempotente. Deux banques simultanées, états périmés, échecs d'allocation, ABI et nettoyage après effacement d'ABK sont couverts.

**[CI Gate A CPU MC68020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43917996936) : 64 scénarios registre, 120 validation AGBO, 64 helper Chip, 116 régression P0b, 11 094 octets de l'unité native privée ; [règles CPU/livraison PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43918000042).** Les services système **AMOS/Exec/graphics sont mockés**. Pas de nouvelle `.Lib`, aucun nouveau token AP20, aucune validation WinUAE/Compiler P0c.

**Limite bloquante :** l'entrée privée `registry_close_entry` est testée, mais **PAS raccordée à `Aga Screen Close`** du binaire installable. Un écran réellement fermé par la Lib actuelle n'appelle pas ce cleanup. Il reste à valider l'insertion de ce callback dans le cycle natif Open/Close (avec GfxBase toujours disponible), et l'invalidation robuste après `Erase`/`Load`/réutilisation d'adresse (ABA), avant le rendu Blitter. Le test actif P0b reste seul, bibliothèque P0b **104 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9` et R84 `LAST_GOOD` inchangées.

## M19 P0c — banque AGBO vérifiée + staging Chip privé : Gate A 120 PASS (16/11/2026)

Le nouvel [émetteur natif privé](../tools/m19_p0c_checked_bank_stage_emit.py) **MC68020 uniquement** ajoute au préfixe source P0b inchangé le contrôle de la banque AMOS réellement sélectionnée, la vérification de **toutes** les images/masques et des bits hors largeur, puis appelle le [noyau Chip privé](../tools/m19_p0c_chip_stage_emit.py). Trois chemins privés (staging, lookup d'identité/génération, release après `WaitBlit`) ont été éprouvés avec **deux contextes Chip indépendants sur deux banques**. [Banc CPU020](../tools/test_m19_p0c_checked_bank_stage_native.py) : **120 scénarios PASS**, 10 044 octets de code natif groupé, deux placements CPU 020 ; [CI ciblée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43916465599). Le noyau Chip précédent conserve **64 PASS**, P0b **116 PASS**. [Rapport](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md).

**Limites impératives :** Gate A **privée et simulée** (services Exec/AMOS/graphics mockés), aucun token AP20 ni `.Lib` P0c, pas de vraie allocation Chip WinUAE ni de dessin Blitter/objet Bob. Le **registre natif automatique des contextes par numéro de banque** et son cleanup à la fermeture restent à intégrer ; les deux contextes testés sont pour l'instant fournis explicitement au wrapper privé. Après `Erase`/`Load`, une **resélection de banque** reste obligatoire ; une réutilisation de l'adresse identique (« ABA ») ne peut pas être exclue par le seul couple pointeur/génération. Ne pas promettre la détection des `Poke` arbitraires. La bibliothèque P0b validée (104 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) et la R84 `LAST_GOOD` sont inchangées.

## M19 P0c — staging Chip natif privé : Gate A MC68020 PASS (16/11/2026)

**Suite source-only de P0b** : [émetteur natif MC68020](../tools/m19_p0c_chip_stage_emit.py) (1 304 octets) et [banc Unicorn CPU020](../tools/test_m19_p0c_chip_stage_native.py) : **64 cas PASS** sur les allocations `AllocVec(MEMF_CHIP|MEMF_PUBLIC)`, `TypeOfMem`, `CopyMem`, remplacement atomique, `WaitBlit` avant `FreeVec`, garde CPU, registres/pile et identités périmées. [CI Gate A privée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021013) et [rapport de détail](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md). **Exec/graphics sont MOCKÉS : pas encore de véritable allocation Chip WinUAE ni de commande AP20 P0c.** Ne pas annoncer un Bob affichable. Le seul binaire installable reste P0b (104 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) et les résultats Gate B Runtime / Gate C Compiler P0b demeurent valides. `LAST_GOOD` R84 n'a pas été promue.

**Prochaine intégration bloquante :** wrapper validant tout AGBO + banque AMOS, véritable table native des contextes Chip et invalidation, puis dessin Blitter des Bobs masqués à dimensions variables (sans `Swap` implicite). Le test unique `tests/current/M19_P0B_MC68020_MASK_BANK.asc` et les archives restent intacts.

## M19 P0b — Gates A, B Runtime et C validées (16/11/2026)

**État courant de main :** bibliothèque unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), 104 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, 104 commandes / 92 entrées AP20. **Gate A MC68020 PASS** (116 scénarios commandes + 104 noyau), **Gate B Runtime WinUAE PASS** (`PRG_STATE 1`), **Gate C véritable AMOS Compiler PASS** (`PRG_STATE -1`), suivant les deux journaux fournis le 16/11. [Rapport et empreintes de l'ABK](M19_P0B_GATES_BC_2026-11-16.md). Interpréteur strict (`PRG_STATE 0`) et matériel physique NON TESTÉS. Ne pas confondre les anciennes mentions « NON TESTÉS » ci-dessous avec ce résultat plus récent.

**Suite du chantier :** préparer une représentation *privée* des images AGBO en vraie Chip RAM, vérifier les plages DMA entières et la durée de vie de l'allocation, puis seulement développer le dessin Blitter et les objets persistants. Le code natif actuel `Aga Bob Bank` gère sélection/métadonnées : il ne prépare pas encore de Chip DMA. Le format AGBO v1, les quatre commandes P0a/P0b validées et R84 `LAST_GOOD` sont conservés sans modification/promotion. Le test M19 P0b reste l'unique ASC actif.

## Historique M19 P0b — livraison initiale Gate A (avant Gates B/C)

**Livraison active sur `main` :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) (**104 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, 104 commandes / 92 entrées AP20) avec [ASC unique `tests/current/M19_P0B_MC68020_MASK_BANK.asc`](../tests/current/M19_P0B_MC68020_MASK_BANK.asc) et [notice](../tests/current/README.md). **Deux nouvelles instructions :** `Make AGA Bob Mask I,C` et `No AGA Bob Mask I` ; index transparent explicite (0 peut être opaque), masque 1 bit indépendant, préservation des autres images, transaction atomique. [CPU Gate A MC68020 PASS — 116 scénarios pour Make/No + 104 noyau](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43758224492), source candidate reconstruite/validée en CI [43758332071](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43758332071). **Runtime P0a : PASS sur journal utilisateur ; Runtime P0b et vrai AMOS Compiler P0b : NON TESTÉS.** WinUAE fonctionnel **68030/JIT ON** ; 68020/JIT OFF uniquement pour benchmark. Aucun IFF/ABK initial requis : génération par le test AMOS. `LAST_GOOD` R84 et archives inchangées, **aucune promotion**. Les sections P0a ci-dessous sont historiques.


## ACTIF M19 P0a — bibliothèque et ASC en chemins canoniques

**Livraison M19 P0a sur main :** `dist/AMOSPro_AGA.Lib` **79 660 octets**, SHA256
`e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0`.
**Seul ASC de campagne :** `tests/current/M19_P0A_MC68020_BANK_GET.asc` ; voir
[`tests/current/README.md`](../tests/current/README.md). L'ancien R88 est conservé
à l'octet près dans `dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib`.
Le builder P0a reprend cette **archive R88** par SHA, jamais la bibliothèque active.
**R84 LAST_GOOD inchangée, aucune promotion.** Nouvelle bibliothèque : **Gate A MC68020 PASS** ;
**Gates B/C NON TESTÉES**. Tests fonctionnels WinUAE **68030 + JIT ON** ;
68020/JIT OFF uniquement pour benchmark. Le nouvel ASC est autonome ; aucune
ressource IFF ou ABK initiale nécessaire. **Les anciens paragraphes ci-dessous
restent un historique et ne désignent plus la bibliothèque ni l'ASC actifs.**


## Configuration WinUAE de l'auteur — validation fonctionnelle / benchmarks

**Gates B/C : WinUAE MC68030 + JIT activé**, en AGA PAL, interprété/Runtime puis AMOS Compiler réel. **MC68020 + JIT désactivé : benchmarks seulement.** Les documents historiques de tests 68020/JIT OFF restent des archives et ne remplacent pas ce choix. **Cible de génération native inchangée : MC68020 minimum.**


## M19 P0a — livraison GitHub disponible, candidate MC68020 non promue

**Livree sur `main` :** [Lib MC68020](../dist/experimental/AMOSPro_AGA_M19_P0A_MC68020_GATE_A.Lib) (**79 660 octets**, SHA256 `e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0`), [ZIP WinUAE avec exemple](../dist/experimental/AMOSPro_AGA_M19_P0A_MC68020_GATE_A_WINUAE.zip), [ASC autonome](../examples/m19_p0a_68020/M19_P0A_MC68020_BANK_GET.asc) et [notice](../examples/m19_p0a_68020/README.fr.md). **Aucune ressource externe necessaire** ; l'ABK est cree dans RAM: par le test. Le publisher reconstruite la meme candidate depuis R88, passe Gate A CPU MC68020 (74 cas) et preflight ASC, verifie SHA et la met dans `dist/experimental/` avec une archive ZIP. R88 `dist/AMOSPro_AGA.Lib`, ASC R88 actif et R84 `LAST_GOOD` conserves, **aucune promotion**. **Gate B WinUAE, Gate C vrai AMOS Compiler, Gate D physique : NON TESTEES.** L'exemple sert a produire les nouveaux journaux `RAM:M19_P0A_INTERPRETED.TXT`, `RAM:M19_P0A_RUNTIME.TXT` et `RAM:M19_P0A_COMPILED.TXT`; ne pas annoncer PASS avant execution reelle.


## M19 P0a — MC68020 exclusif : Gate A 74/74 PASS

**Décision utilisateur du 15/11/2026 : aucun nouveau noyau 68000/68010, aucun fallback, aucune double voie CPU000/CPU020.** Implémentation MC68020/68EC020 exclusive de `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2`, capture par **`BFEXTU` + `BFINS`** (champs de bits de largeur variable 1..16, sans lecture au-delà de X2). Les deux points d'entrée refusent un CPU inférieur avant de manipuler la banque ou la mémoire AGA. Seule la base figée R88 est conservée comme patrimoine ; les parties nouvelles sont 68020 exclusivement.

**GATE A CPU MC68020 PASS**, [exécution GitHub Actions 43754375272](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43754375272), commit exact `27fb718c127ed82cd610a3f5d622274046f82fa7` : **52 scénarios Get + 22 Bank**, deux dispositions CPU020 (interprétée et Compiler V2 simulée) sous Unicorn, **44 tests hôte/statiques PASS**, décodage Capstone M68K_020, préflight de la transaction et préservation des pixels / images / masques. Les anciennes Gates A CPU000 restent un **historique obsolète pour ce chantier** et ne servent pas de preuve 020.

**Candidate uniquement en mémoire :** 79 660 octets ; SHA256 `e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0` ; **80 commandes / 90 entrées AP20**. Aucun écrit dans `dist/`, R88 v0.13.33 et R84 `LAST_GOOD` inchangées, ASC actif intact. **Gate B WinUAE, Gate C vrai Compiler, Gate D physique : NON TESTÉES.** La préparation Chip pour le moteur d'affichage Bob reste à coder ; ne pas prétendre que les Bobs sont déjà affichables sous AMOS. Source de règles : [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md).


## M19 P0a — Get AGA Bob Gate A CPU PASS (source R88 uniquement)

**Candidate en mémoire et non installée :** `Aga Bob Bank N` + `Get AGA Bob I,X1,Y1,X2,Y2`. [CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43753489991) **PASS sur commit `8352aaef331caeccac5cd45aa0631614846568d0`** : 50 scénarios CPU MC68000 Get pixel-exacts, 20 scénarios CPU Bank, 42 tests hôte/statiques ; deux dispositions natives simulées. Candidate de **79 640 octets**, SHA256 `988a1d2151fd9c53c03d047af3eac23c5dc8ba4c1152ca2338635c9410deb526`, 80 commandes / 90 entrées AP20. [Rapport complet](M19_P0A_R88_GET_AGA_BOB_GATE_A.md). Source native figée **R88** `7c575a02087d550611b8e966a7708b5f6a8c4b71`, **aucun exemple/code R89/R90**. R88 `dist`, R84 `LAST_GOOD`, tests actifs et passés **intacts** ; **WinUAE Gate B, AMOS Compiler réel Gate C, physique D NON TESTÉES**. La préparation des Bobs pour le Blitter en Chip est encore à implémenter ; pas de promotion automatique.

## M19 P0a — `Aga Bob Bank N` AP20 depuis R88 : GATE A CPU PASS

Commande **expérimentale** `Aga Bob Bank N` (instruction 1 argument) ajoutée par builder **en mémoire** `tools/build_m19_p0a_r88_bank_in_memory.py` à partir de la Lib **R88 SHA256 69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc**. [Gate A 68000 + AP20 / Compiler-style relocation](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43751680955) **PASS : 20 cas CPU**, et **36 contrôles hôte+statiques PASS**, commit testé `0b1eea12aabbb42caabe03e1eeced9e8dd24145b`. Binaire reconstruit **en mémoire uniquement**, 76 408 octets, SHA256 `82060e0fedf3357f64426817348b218381dc8ed3b640552bd89c0ca433e79d74`, 79 commandes / 89 entrées AP20 ; [rapport](M19_P0A_R88_BANK_SELECT_GATE_A.md). **AUCUNE Gate B/C**, aucun `Get AGA Bob`, préparation Chip non implémentée, aucun binaire installé ni promotion. R88, ASC actif, R84 `LAST_GOOD` intacts. Le groupe BOBS R88 était de 7 038 octets et son offset d'append est **7004**, pas 5186 (R87). Aucun code ni exemple R89/R90 utilisé.


## M19 P0a — transaction native 365 (source R88 uniquement)

**Étape 3, code natif privé :** `tools/m19_p0a_amos_bank_transaction_emit.py` (874 octets 68000/68020 déterministes) et ses [7 tests de préflight statique](../tools/test_m19_p0a_amos_bank_transaction_emit.py) ; [audit complet](M19_P0A_NATIVE_BANK_TRANSACTION_2026-11-15.md). La source AMOS Professional 365 `marc365` épingle `Cur_Banks(A5)=$05EA` et `Lst.Cree`/`Lst.Del`/`Bnk.Change`, d'où un remplacement de banque **sans Bnk.Reserve destructif et sans seconde banque AMOS numérotée** : stage privé → contrôle d'identité → publication → notification → libération. **32/32 contrôles locaux PASS** (25 modèle + 7 statiques) ; **aucune Gate A CPU**, **aucune Gate B/C**, **aucune commande AP20**. `dist`, R84 LAST_GOOD, R88 et `tests/current/` inchangés. Le code et les exemples R89/R90 sont hors périmètre.


## M19 P0a — capture transactionnelle (depuis R88 uniquement)

Deuxième étape P0a : `tools/m19_p0a_capture_transaction.py` et `tools/test_m19_p0a_capture_transaction.py` ajoutés, avec 14 nouveaux tests hôte PASS (25 au total avec les 11 tests du format AGBO). Capture bitmap planaire Safe, stride physique, coins inclusifs, banques multiples, remplacement d'image sans perte, échec d'allocation sans mutation et resélection obligatoire après `Erase`/`Load`. [Rapport](M19_P0A_CAPTURE_TRANSACTION_2026-11-15.md). **Ce modèle n'est ni une instruction AP20, ni une Gate A native.** La transaction de remplacement d'une banque AMOS Professional 365 reste à vérifier sur son implémentation exacte avant toute mutation native. Aucun binaire, ASC, R84 `LAST_GOOD` ou builder R88 modifié.


## M19 P0a — développement depuis R88 (modèle de banque ABK, pas de nouvelle Lib)

Suite à la demande explicite de reprendre **M19 Bobs multi-images uniquement depuis R88**, la première brique **P0a hôte** est ajoutée : `tools/m19_p0a_multi_bob_abk.py`, 11 tests locaux PASS dans `tools/test_m19_p0a_multi_bob_abk.py`, format et limites dans [`M19_P0A_ABK_FORMAT_2026-11-15.md`](M19_P0A_ABK_FORMAT_2026-11-15.md). Provenance figée : R88 `7c575a02087d550611b8e966a7708b5f6a8c4b71`, sans emploi de code ni d'exemple des builds ultérieurs. Payload `AGBO` v1 multi-images non compressées, masque indépendant, AMOS `AmBk` DATA, contrôle des corruptions, remplacement atomique dans le modèle. **Aucune commande AP20 ajoutée, aucune Gate A native/B/C, aucun nouveau ASC, aucune modification de `dist` ni de `LAST_GOOD`.** Prochaine étape technique : résoudre l'agrandissement non destructif des banques AMOS avant `Aga Bob Bank`/`Get AGA Bob` natifs.


> **Consolidation documentaire (15/11/2026) :** les 33 corrections approuvées sont réunies dans [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md). Les 1 903 lignes précédentes sont conservées [en archive non normative](EXTENSION_SOURCE_RULES_HISTORIQUE_2026-11-15.md). Aucun binaire, builder, ASC ni test validé n'a été modifié par cette consolidation ; `LAST_GOOD` R84 reste protégée, aucune promotion automatique. Le checkpoint de travail documenté ci-dessous décrit R88 ; **ne pas supposer que c'est encore le HEAD ou le dernier chantier**, vérifier les commits de `main`, le builder et `dist/AMOSPro_AGA.Lib`. Les étapes de Bob multi-images restent distinctes du cache AGPC R88 et des Sprites matériels AGA. L'historique chronologique ci-après est conservé pour provenance, pas comme suite d'instructions concurrentes.

---

**NOUVEAU CHANTIER DOCUMENTÉ — SPRITES MATÉRIELS AGA (15/11/2026), PAS DE CODE NI DE TEST :** [contrat S0/S1/S2/S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md). Deux moteurs **séparés** : Bobs logiciels M19 (Blitter, banque multi-images 256 couleurs, priorité P0) versus **Sprites matériels AGA** (8 canaux DMA, largeur 16/32/64 via FMODE, 3 couleurs+transparent, paires attachées 15+transparent, choix de tranches de palette AGA, Chip/Copper/Intuition). **S0 audit** écran privé/ressources/ownership avant API ; **S1** Sprite 16 px ; **S2** attaché/largeurs/coordonnées/palettes ; **S3** multiplexage/AMAL facultatif/collisions. Les « 56 computed Sprites » du manuel AMOS OCS ne sont PAS 56 canaux AGA. Ne pas installer de nouvelle API sans vérification AP20/Compiler et Gates distinctes. R84 LAST_GOOD et R88 inchangées. Note de liaison ajoutée au [plan M19 historique](M19_SPRITES_BOBS_AMAL_PLAN.md) et au [contrat Bob](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md).

---

**FEUILLE DE ROUTE M19 P0/P1/P2 (15/11/2026) — DOCUMENTATION UNIQUEMENT :** le [contrat Bobs AGA](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) contient désormais l'inventaire fonctionnel tiré des chapitres 7.01–7.04 du manuel AMOS. **P0 :** banques/capture/mask/Chip, objets persistants, `Aga Bob Off`, `Aga Bob Update`, `Aga Bob Clear`/`Aga Bob Draw` ; rendu dans le back buffer AGA, **pas de `Aga Swap` implicite**. **P1 :** lecture X/Y/image, hotspot, priorités, Paste, Limit, édition de banque. **P2 :** collisions, HREV/VREV/REV, Set Bob, intégration AMAL, automatisation éventuelle. Les nouveaux noms AGA sont des propositions **non implémentées** ; préflight/token AP20/Compiler avant codage. **R84 LAST_GOOD inchangée, R88 candidate inchangée ; aucune nouvelle Gate validée.**

---

**M19 Bobs AGA — CONTRAT UTILISATEUR MIS À JOUR (15/11/2026), CONCEPTION UNIQUEMENT :**
- **API cible** (non implémentée) : `Aga Bob Bank N`, `Get AGA Bob I,X1,Y1,X2,Y2` (**sans `To`**, bornes inclusives), `Make AGA Bob Mask I,C`, `No AGA Bob Mask I`, `Aga Bob N,X,Y,I`, `Aga Bob Bank Free N`. `Save`/`Load` AMOS natifs pour les ABK.
- **Banques multi-images 1..8 bitplanes/256 couleurs** : Bobs planaires **non compressés** et masques séparés ; pas de RLE dans les Bobs animés. **AGAPIC/RLE/Fast existant conservé pour les grandes images**, sans refonte.
- **Numéros de banques AMOS choisis par l'auteur** : `Aga Bob Bank N` sélectionne/crée la banque et prépare automatiquement les données DMA en **vraie Chip RAM** si nécessaire. `Load` AMOS peut rester en Fast : la préparation est déclenchée explicitement par `Aga Bob Bank N`, **sans commande AMCAF, copie manuelle ni seconde banque numérotée**.
- **Sécurité** : une entrée Chip associée par banque, réutilisable par plusieurs Bobs ; `Aga Bob Bank Free` libère seulement les ressources internes, invalide les Bobs dépendants. Après un `Load`/`Erase` natif qui remplace une banque, la resélection `Aga Bob Bank N` est contractuelle. Vérifier `MEMF_CHIP` réel, la durée de vie des pointeurs, `Safe`/`Swap`, la sauvegarde ABK, le Compiler.
- **État** : aucune nouvelle commande testée ni build produite ; R88 reste candidate, R84 `LAST_GOOD` protégée ; aucune promotion, branche, release ou modification du test ASC actif.
- [**Contrat complet M19 Bobs AGA**](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md).

---

## M19 P2.8 — diagnostic WinUAE du 15/11/2026 : banque AGPC en Fast RAM

**R88 v0.13.33 Gate A PASS (130 cas) ; WinUAE Runtime B FAIL sur le banc original, `ERR 12`**. Le journal `M19_P28_DIAG_RUNTIME.TXT` montre `B11/B13 LENGTH 360`, `AGPCACHE`, flags AGPC 3, mais `CHIP_AFTER_LOAD=CHIP_BEFORE=1 796 336` et `FAST_AFTER_LOAD-FAST_BEFORE=-768` : les deux banques de 384 octets (avec enveloppe AMOS) resident en Fast RAM. `Aga Cache Blit` renvoie 0 dans les deux modes sur les deux banques, conforme au refus `MEMF_CHIP` du coeur M18. **Diagnostic termine sans Guru : `DIAG_DONE 1`, `ERR 0`, `CLOSE_RETURNED 1`** ne constituent pas une Gate B PASS.

**ASC actif corrige (tests/courant)** : [`M19_P28_R88_CACHE_BLIT_FPS_01.asc`](../tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc), Git blob `001396551cad6fed57903b714bc374e0988f63ea`, staging AGPC en **vraies banques Chip Data 11/13** (via temp 20, copie exacte du payload 360 octets et du nom AGPCACHE, sans modifier les flags AMOS). **Correction PREPAREE uniquement** : nouvelle Gate B WinUAE attendue ; Gate C Compiler non testee. Les binaires R88 candidat, R87 archive et R84 `LAST_GOOD` sont inchanges. Pas de branche, promotion, tag ni release. [Rapport du diagnostic](M19_P28_R88_CHIP_BANK_DIAGNOSTIC_2026-11-15.md).

---

## CANDIDATE ACTIVE R88 — correction du chemin (15/11/2026)

**`dist/AMOSPro_AGA.Lib` contient R88 v0.13.33** (**75 040 octets**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`). La **R87 v0.13.32 précédente** est archivée sans changement dans `dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib` (**73 184 octets**). Les quatre banques P2.8 restent dans `tests/fixtures/m19_p28/`, l'unique ASC dans `tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc`. **Gate A native R88 PASS ; Gates WinUAE B/C NON TESTÉES.** R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` intacte et non remplacée. Aucun tag, release, promotion ni branche. [Contrat du changement](M19_P28_R88_ACTIVE_CANDIDATE_2026-11-15.md).

---

## ARCHIVAGE R88 GATE A SUR GITHUB — uniquement expérimental

La bibliothèque **R88 v0.13.33 (75 040 octets, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`)** est conservée sur `main` sous [`dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib`](../dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib). Les **quatre banques ABK v1/v2** du banc sont également conservées durablement sous [`tests/fixtures/m19_p28/`](../tests/fixtures/m19_p28/). [Vérificateur SHA/taille](../tools/verify_p28_archive.py) et [CI de génération](../.github/workflows/m19-p28-agapic-planar-cache-gate-a.yml) : Gate A PASS. **R87 candidate active et R84 `LAST_GOOD` restent intactes, WinUAE Runtime et Compiler R88 non testés, aucun binaire promu.**

---

## CHANTIER ACTUEL — P2.8 R88 expérimental : Gate A native PASS, banc WinUAE préparé

**R88 v0.13.33 est construite en mémoire uniquement** : **75 040 octets**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`. 78 commandes / 88 entrées AP20 ; nouvelle commande tentative `Aga Cache Blit(CacheBank,X,Y,Mode)`, **16×16×8 seulement, cache AGPC en Chip RAM**, alpha 1-bit indépendant des couleurs, v1/v2. **Gate A 68020 PASS : 130 cas Interpreter + Compiler V2 emulé**, en complément des 288 oracles host et 48 cas M18 core. L'ancien échec d'oracle venait d'un stride physique de 18 octets contre 10 attendus à tort par le test ; correction et rerun PASS [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43730486672). **Ce n'est PAS WinUAE/AMOS Compiler réel.**

**Nouveau seul ASC actif** : `tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc` (350 lignes, Git blob `a9ee1aaa64d9b588e5b2d6e6134d63ec848e6181`, préflight AMOS strict PASS). **Quatre banques sources** v1/v2 AGAPIC/AGPC générées par `tools/m19_p28_winuae_bundle.py`, même motif et masque indépendant. La CI fournit une archive séparée **`M19_P28_R88_GATE_A_ONLY_WINUAE_BUNDLE`** avec la **bibliothèque expérimentale R88**, l'ASC, les quatre ABK et les consignes d'installation. **Pas d'écriture dans dist, aucune promotion.**

L'ASC compare **8 captures complètes** avant 12 séries de dessin seul (4/8/16, 64 répétitions AB/BA) et 12 séries de **frames complètes** (4/8/16, 24 frames par série, 288 Swap), incluant fond, Wait Vbl et Swap. Récupérer **`RAM:M19_P28_RUNTIME.TXT` / `RAM:M19_P28_COMPILED.TXT`**, puis analyser gains de dessin et FPS réels séparément. **Gates B/C R88 NON TESTÉES, aucun gain P2.8 encore démontré.**

**R87 active inchangée** `dist/AMOSPro_AGA.Lib` (73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`), **R84 `LAST_GOOD` inchangée**. main exclusivement, pas de branche, tag, release ou promotion.

---

## CHANTIER EN COURS — M19 P2.8 P0 (alpha independant)

**Sources nouvelles sur `main` :** `tools/m19_p28_agapic_planar_cache.py` et `tools/test_m19_p28_agapic_planar_cache.py` ; [contrat P2.8](M19_P28_AGAPIC_PLANAR_CHIP_ALPHA_2026-11-15.md) ; [workflow Gate A](../.github/workflows/m19-p28-agapic-planar-cache-gate-a.yml). Convertir AGAPIC v1/v2 en snapshot planaire **avec alpha independant des indices couleur**, garder l'ownership en banque DATA et rejeter les buffers/preparations incomplets. Cas 16×16×8 : bloc 288 octets compatible avec le **coeur M18/P5 natif existant**, mais **PAS avec l'ancien wrapper AP20**, qui imposait `alpha == OR des plans couleur` et doit etre remplace avant toute API publique AGPC. **Gate A native a executer en CI** ; **AUCUN nouveau binaire R88, AUCUNE Gate B/C P2.8, AUCUN FPS mesure pour P2.8**.

**Priorite suivante apres Gate A :** pont AGPC/AP20 pour une vraie banque Chip verifiee `TypeOfMem`, puis images hors 16×16, un benchmark complet avec fond, double buffering, Swap et cout de staging inclus. R87 et R84 `LAST_GOOD` restent identiques ; main exclusivement, aucune promotion.

---

## PRIORITÉ ACTUELLE — M19 P2.8 : cache AGAPIC planaire et vrai rendu masqué

**Constat P2.7 (WinUAE réel, 15/11/2026)** : le rendu AGAPIC RLE coûte **553 contre 225 ticks FICON8** en Runtime, **522 contre 198** en Compiled (somme 4/8/16 Bobs), soit **−59,31 % / −62,07 %**. La copie Blitter **opaque, pré-stagée** économise **41,67 % / 45,90 %** par rapport au CPU opaque. **Les neuf captures comparées sont identiques en Runtime et Compiled** (`PARITY_OK 9`, `PARITY_BAD 0`), `RESULT 1`, `ERR 0`, mémoire stable, fermeture réussie. **P2.7 Gate B Runtime PASS / Gate C Compiled PASS**. [Résultats détaillés](../benchmarks/RESULTATS_M19_P27_R87_CPU_RLE_FICON_BLITTER_2026-11-15.md), [log Runtime](../benchmarks/M19_P27_RUNTIME.TXT), [log Compiled](../benchmarks/M19_P27_COMPILED.TXT).

**Étape à développer :** cache AGAPIC pré-décodé, **sans perte du masque alpha indépendant** (y compris couleur zéro opaque), préparation hors frame, propriété AMOS de la mémoire, validité après Erase/Load et Blitter masqué Chip→Chip (reprendre M18 pour ABI, Safe et WaitBlit). Benchmarker **cache CPU vs vrai cache Chip/Blitter**, staging inclus/amorti, puis la frame complète avec Swap, décor et FPS. **P2.8 reste NON IMPLÉMENTÉ / NON TESTÉ.** Pas de modifications de l'actuel binaire R87 avant nouveaux tests natifs, aucune promotion automatique, branche `main` uniquement, R84 `LAST_GOOD` protégée.

**Source P2.7 archivée** `tests/passed/M19_P27_R87_CACHE_CPU_BLITTER_01.asc` **inchangée** (Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`). Une copie reste dans `tests/current/` comme référence unique jusqu'à la préparation du prochain ASC ; ne pas l'interpréter comme un nouveau test à refaire.

---

## HISTORIQUE — M19 P2.7, préparation du banc cache et Blitter

**Un seul ASC actif** : `tests/current/M19_P27_R87_CACHE_CPU_BLITTER_01.asc` (Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`). R87 v0.13.32 inchangée, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. Le programme crée le **même motif** 16×16 en AGAPIC v1/v2 et FICON8, vérifie **9 comparaisons intégrales** (opaque, masqué, X décalé, clipping, copie Blitter), puis chronomètre 4/8/16 Bobs masqués et un transfert opaque Blitter 8 Bobs. **Ne pas confondre copie Blitter opaque déjà stagée et rendu AGAPIC masqué natif**. **Gate A nouveau modèle/préflight local : PASS ; Gate B/C P2.7 NON TESTÉES.** WinUAE demandé : MC68020 14 MHz, PAL, JIT OFF, même ASC en Runtime et AMOS Compiler V2. Journaux `RAM:M19_P27_RUNTIME.TXT` et `RAM:M19_P27_COMPILED.TXT`. [Contrat P2.7](M19_P27_AGAPIC_CACHE_BACKENDS_2026-11-15.md).

**P2.6 désormais qualifié** : Runtime et Compiled `RESULT 1 / ERR 0 / VERDICT PASS` dans les journaux transmis ; gains Batch **2,42 % / 0,43 %** cumulés. ASC **archivé octet pour octet** dans `tests/passed/M19_P26_R87_DRAW_BENCH_01.asc`. [Résultats](../benchmarks/RESULTATS_M19_P26_R87_DRAW_2026-11-15.md). **Ne pas refaire le smoke ou le Batch pour P2.7.** R84 `LAST_GOOD` intangible. main seulement, pas de branche/tag/release/promotion.

---

## HISTORIQUE — M19 P2.6 R87 : préparation du banc BASIC vs Batch (15/11/2026)

**À tester maintenant :** `tests/current/M19_P26_R87_DRAW_BENCH_01.asc` (**267 lignes**, Git blob `c6c03b24bb273027492776ba24e53193ec52198b`). Uniquement **4/8/16 Bobs**, 64 répétitions, passes AB puis BA, **12 séries draw-only**, sans Z-sort, Fill, Swap, VBL ou allocation *pendant les chronos*. Le programme journalise les ticks bruts `BASIC_TICKS`, `BATCH_TICKS`, `PASS0_N` et `PASS1_N` dans `RAM:M19_P26_RUNTIME.TXT` puis `RAM:M19_P26_COMPILED.TXT`. **P2.6 Runtime/Compiled NON TESTÉ**, aucun gain présumé. Configuration WinUAE 68020/14 MHz/PAL/JIT OFF. [Protocole](M19_P26_R87_DRAW_PERFORMANCE_2026-11-15.md).

**Le smoke P2.5 R87 a déjà PASS en Runtime et Compiled** (`RESULT=1`, `ERR=0`, `VERDICT=PASS`, `DRAW=3`, `REJECT=3`, mémoire Chip/Fast stable). Son fichier source est maintenant archivé **sans modification** : `tests/passed/M19_P25_R87_BOBS_SMOKE_01.asc`, Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`. Les journaux P2.5 ne sont **pas** des benchmarks ; ne pas relancer un nouveau smoke à la place de P2.6. Le brouillon P2.4 reste en `tests/design/` non validé.

**Candidate R87 v0.13.32 inchangée** : `dist/AMOSPro_AGA.Lib`, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. R84 `LAST_GOOD` intouchable. **main uniquement**, pas de tag, branche supplémentaire, release ou promotion.

---

## HISTORIQUE — M19 P2.5 R87, smoke AMOS après audit du skill

Le nouveau **seul test actif** est `tests/current/M19_P25_R87_BOBS_SMOKE_01.asc` (Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`, 209 lignes) : base du véritable test R86 P2.3 PASS, retrait du Probe R87, des fausses validations pixel et du benchmark non qualifié. Vérification des banques **avant tout Erase** via `_BANKS_SAFE`. Préflight strict `amos-pro-aga-rules` **PASS**, 21 tests du checker **PASS** en local ; nouvelle CI dédiée à contrôler. **Gates B/C R87 NON TESTÉES.**

L'ancien `M19_P24_BOBS_PIXELS_BENCH_01.asc` est déplacé **octet pour octet** dans `tests/design/M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc`. Il comportait 611 lignes et n'a jamais été validé en Runtime/Compiler ; il n'est plus l'ASC actif ni un test `passed`. Ses travaux de pixel oracle et de benchmark reprendront une fois le smoke R87 validé sous AMOS.

**Fichiers attendus WinUAE pour le test actuel :** `RAM:M19_P25_RUNTIME.TXT` puis `RAM:M19_P25_COMPILED.TXT` (68020/14 MHz/PAL/JIT OFF). Résultat ciblé : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `CLOSE_RETURNED 1`. [Guide et problèmes corrigés](M19_P25_R87_AMOS_SMOKE_REVIEW_2026-11-15.md).

La candidate `dist/AMOSPro_AGA.Lib` **R87 v0.13.32 est inchangée** ; R84 `LAST_GOOD` reste intouchable. Pas de branche, tag, release ou promotion.

---

## CHANTIER ACTIF — M19 P2.5 R87 : suppression du témoin BOBS (15/11/2026)

**Branche `main` uniquement.** Le nouveau constructeur `tools/build_m19_p25_no_probe.py` retire définitivement **du candidat R87** le token `Aga Bob Probe`, son stub et la routine `PROBE_CODE` ; `Aga Bob Batch` reste identique, indice AP20 **82**, groupe BOBS **85**, 77 commandes et 87 entrées AP20. Le nouveau test natif MC68020 `tools/test_m19_p25_no_probe.py` vérifie ABI, absence de Probe, contenu moteur, portée BSR.W, pixels, sécurité du front, erreurs et R84 historique. Le workflow R86 obsolète est désactivé en push pour éviter un retour arrière automatique.

**État validé du chantier :** candidate R87 v0.13.32 enregistrée dans `dist/AMOSPro_AGA.Lib` (**73 184 octets**, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`) ; **CI native MC68020 Gate A 9/9 PASS** ([run 43719479059](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43719479059)), P2.4 statique PASS. Aucun binaire R86 ne reste actif, ses preuves demeurent historiques. **R84 `LAST_GOOD` absolument inchangée.** Le seul ASC actif `tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc` est ciblé **R87** (plus d'appel au Probe). Les anciens logs R86 P2.3 **ne valident pas** R87. **Gates B/C R87 NON TESTÉES**, aucun gain de performance présumé. Nouvelle validation sous WinUAE 68020/14 MHz/JIT OFF via `RAM:M19_P24_RUNTIME.TXT` et `RAM:M19_P24_COMPILED.TXT`. Aucune branche/tag/release ou promotion.

[Contrat R87](M19_P25_R87_NO_PROBE_2026-11-15.md) · [Test actuel](../tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc).

---

## HISTORIQUE — M19 P2.4, banc pixels + benchmark non validé (15/11/2026)

**Nettoyage obligatoire avant toute version publiable après les essais P2.4 :** retirer du **binaire natif** la commande temporaire `Aga Bob Probe` (token public, stub AP20, routine `PROBE_CODE` et toutes références embarquées), sans supprimer le moteur `Aga Bob Batch`. Mettre à jour le générateur, les offsets et les références de groupe AP20, contrôler ABI/relocations/portée BSR.W et limite 65 534 octets, puis construire la **nouvelle candidate uniquement dans `dist/AMOSPro_AGA.Lib`**, sans toucher à R84 `LAST_GOOD`. Rejouer les tests statiques/MC68020 et obtenir de **nouveaux** résultats WinUAE Runtime et Compiled : les Gates R86 ne sont pas transférables automatiquement au binaire nettoyé. Les tests et rapports restent archivés dans `tests/passed/`, `tools/` et `docs/` pour la non-régression : seule la sonde de diagnostic embarquée doit disparaître. Aucun tag, release ou promotion sans validation explicite.

- **Branche main uniquement** ; aucun tag, aucune release, aucune promotion. Binaire **R86 v0.13.31** dans `dist/AMOSPro_AGA.Lib` : 73 232 octets, SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`. **R84 LAST_GOOD** reste figée : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.
- **Test actif unique** : `tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc`. **L'ancien ASC P2.3 archivé sans changement** : `tests/passed/M19_P23_BOBS_BATCH_01.asc`, blob Git `19ad2044252783454f4082c118e53b34a6b83478`. Le P2.3 dispose déjà de **Gates A/B/C PASS** ; son rapport demeure [M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md).
- **Nouveau P2.4** : 19 indices de couleur vérifiés par décodage d'une capture AGAPIC v1 1×1 (pas de faux flag `CLIP`/`MASK`/`ORDER`), front contrôlé après Swap explicite, parité d'images complètes BASIC/Batch 144×144 sur **4/8/16 Bobs**, comparaison de tous les octets RLE.
- **Mesure unique prévue** : draw-only, **64 itérations × 2 passages AB/BA** pour 4/8/16 Bobs ; **12 sous-runs et 3 584 dessins par méthode**. Aucun Swap, Wait VBL, fond, capture, tri Z ou allocation dans les plages chronométrées. `Timer` en ticks ; ne pas comparer directement les ms P2.1, périmètres différents. WinUAE cible 68020/14 MHz/PAL/JIT OFF.
- **Gates P2.4 WinUAE B Runtime/C Compiled : PENDING**, nouveaux journaux attendus `RAM:M19_P24_RUNTIME.TXT` et `RAM:M19_P24_COMPILED.TXT`. Ne pas annoncer de gain sans mesures réelles. **Gate statique P2.4 PASS** ([run 43701540717](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43701540717) : 19 points, 256 indices et 3 cas de parité modélisés). Cette validation est distincte des Gates WinUAE.
- **CI générale historique** : dernier diagnostic `build_aga_r84_agapic.py` refuse encore le SHA de la candidate R86 lors d'un test de reconstruction R84 ; chantier d'outillage séparé, aucune modification de la bibliothèque R84.

[Contrat de validation P2.4](M19_P24_PIXEL_ORACLE_BENCH_PLAN_2026-11-15.md).

---

## HISTORIQUE — M19 P2.3 R86 : Gates A/B/C PASS, pas de promotion (15/11/2026)

**Branche `main` uniquement**, aucun tag, release ou changement de branche. **Candidate active** `dist/AMOSPro_AGA.Lib` R86 v0.13.31 : **73 232 octets**, SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`, **78 commandes / 88 entrées AP20**, blocs C2P 5 558 / IFF 2 508 / BOBS 5 226 / AGA 56 580. `Aga Bob Batch(DescriptorBank,Count)` fonctionne dans le scénario livré, `Aga Bob Probe` est conservée. **R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` toujours figée** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`).

**Gates :** A native MC68020 **8/8 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700178749)), **B WinUAE Runtime PASS** (`PRG_STATE 1`, `RESULT 1`, `ERR 0`), **C WinUAE Compiled PASS** (`PRG_STATE -1`, `RESULT 1`, `ERR 0`). Les deux journaux fournis établissent `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `CLOSE_RETURNED 1`, mémoire Chip/Fast revenue au point initial dans chaque exécution. **BASIC_TICKS 13 / BATCH_TICKS 13 dans les deux modes : aucun gain démontré** sur quatre itérations avec fond inclus.

**Périmètre réel :** les flags `ORDER`/`CLIP`/`MASK` de cet ASC sont mis à 1 après retour positif et ne vérifient pas indépendamment les pixels WinUAE ; les comparaisons de pixels sont celles de la Gate A native. Les logs affichent la chaîne de version ASC, **pas le SHA256 du binaire chargé**. Gate D Amiga physique non exécutée ; ne pas promouvoir `LAST_GOOD`.

**Seul test actif** : `tests/current/M19_P23_BOBS_BATCH_01.asc` ; blob Git `19ad2044252783454f4082c118e53b34a6b83478`, **ne pas modifier le test couvert par ces journaux**. Ancien témoin P2.2 déjà archivé octet pour octet dans `tests/passed/M19_P22_4UNIT_PROBE_01.asc`. Si un nouveau test est décidé, archiver d'abord le P2.3 sans le modifier puis ne garder qu'un ASC dans `tests/current/`.

**Suite recommandée** : nouveau banc ciblé avec oracles de pixels WinUAE pour transparence, chevauchement et clipping ; comparaison BASIC/Batch sur durée suffisante et sans confondre le coût du fond ou le cache Z. **Aucune campagne supplémentaire n'a encore été exécutée.** Le contrôle général `Artifact integrity` peut rester en échec pour des tests historiques/expérimentaux sans remettre en cause la CI ciblée ; vérifier sa cause exacte au besoin.

**État CI générale au 15/11/2026 : FAIL**, [run 43700905076](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700905076). La vérification **R86 à quatre unités** dans `test_generate_current_native_source.py` passe désormais (`STRICT R86 FOUR-UNIT SOURCE PROVENANCE PASS`), mais l'étape suivante réexécute le constructeur historique `build_aga_r84_agapic.py` qui refuse encore le SHA de la R86 active (`AssertionError: Unknown active dist binary during historical R84 rebuild`). **C'est un garde-fou de compatibilité des outils historiques, pas un échec du moteur R86 ou des Gates A/B/C**. Adapter ce contrôle de façon ciblée lors d'un chantier CI dédié, sans altérer la R84 figée et sans contourner la validation d'origine.

**Rapport signé par les deux journaux** : [M19 P2.3 R86 Runtime / Compiled](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md) · [Contrat API](M19_P23_BOBS_BATCH_CONTRACT.md).

---

## HISTORIQUE — M19 P2.3 R86 avant les journaux WinUAE (15/11/2026)

Sur `main` exclusivement, deux nouvelles commandes actuelles : `Aga Bob Batch(DescriptorBank,Count)` et témoin `Aga Bob Probe`. R86 v0.13.31: 78 commandes publiques, 88 entrées AP20, quatre unités natives. Le constructeur `tools/build_m19_p23_bob_batch.py` produit **uniquement** `dist/AMOSPro_AGA.Lib` avec `--write-dist` ; `LAST_GOOD` R84 reste intouchable (67904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). CI dédiée : `.github/workflows/m19-p23-bobs-batch-gate-a.yml`. Ne pas annoncer un PASS sans le résultat d'exécution de la nouvelle CI.

**Test actif unique** : `tests/current/M19_P23_BOBS_BATCH_01.asc`. Ancien témoin R85 à archiver dans `tests/passed/` avec les mêmes octets. Le Batch dessine en groupe sur le back buffer, ne fait pas Swap/Wait VBL, et peut laisser un frame partiel en cas d'erreur sur un Bob tardif : **si résultat 0, ne pas Swap**. Tests WinUAE Runtime et Compiled **en attente des vrais journaux** `RAM:M19_P23_RUNTIME.TXT` et `RAM:M19_P23_COMPILED.TXT` ; performance pas encore mesurée.

**Point CI préexistant** : `Artifact integrity` échoue déjà sur le jalon expérimental `Experimental Compiler V2 68000 bridge Gate A` (run 43698493395), indépendamment du test spécifique BOBS R85. [Contrat API](M19_P23_BOBS_BATCH_CONTRACT.md).

---


## ÉTAT ACTUEL — M19 P2.2 R85, témoin quatrième bloc PASS (15/11/2026)

**Correction de l'organisation : seul ASC actif = [`tests/current/M19_P22_4UNIT_PROBE_01.asc`](../tests/current/M19_P22_4UNIT_PROBE_01.asc)**, déplacé sans modification depuis `tests/design/`. **Ne plus chercher le nouveau test dans `tests/design/`.** Précédent P2.1 PASS archivé exactement dans [`tests/passed/M19_P21_ZCACHE_BENCH_01.asc`](../tests/passed/M19_P21_ZCACHE_BENCH_01.asc), blob Git `f75af1a84b4c658d5f1cb330d58d248413e72cc7`. Le source P2.2 correspond au blob Git `cd564aa660f8927b1c4d0b63456de58b5535fae0`.

**Journaux fournis** `M19_P22_4UNIT_RUNTIME.TXT` (`PRG_STATE 1`) et `M19_P22_4UNIT_COMPILED.TXT` (`PRG_STATE -1`) : **RESULT 1, VERDICT PASS, ERR 0, AGA_DETECT -1, BOB_PROBE 1, CLOSE_RETURNED 1** pour chacun. **Gate B Runtime du témoin PASS ; Gate C Compiled du témoin PASS.** [Rapport avec logs bruts](M19_P22_4UNIT_WINUAE_RUNTIME_COMPILED_2026-11-15.md). Ce résultat atteste le routage du quatrième groupe, pas `Aga Bob Batch`, pas un rendu d'images.

**Binaire de travail :** `dist/AMOSPro_AGA.Lib` R85 v0.13.30 (67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`). **R84 `LAST_GOOD`** protégée dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucune promotion. `main` exclusivement, aucune autre branche.

**Suite technique :** implémenter un véritable rendu groupé dans le quatrième bloc BOBS, puis valider cette fonctionnalité séparément. Les anciens états et liens cités plus bas sont des **notes historiques** et ne changent pas le test actif.

---


## HISTORIQUE — M19 P2.2, avant essais Runtime et Compiled (15/11/2026)

**Consigne explicite :** le binaire de travail est directement **[`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib)**, **pas dans `build/` ni un sous-dossier**. Version expérimentale **R85 v0.13.30** : 67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`, 77 commandes, 87 entrées AP20, quatre blocs C2P 5 558 / IFF 2 508 / BOBS 40 / AGA 56 580. **[`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib)** reste R84 v0.13.29, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, conservée **octet pour octet**, jamais écrasée.

**État technique :** **Gate A native/MC68020 PASS** (CI [43696972204](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43696972204)). Routage des 4 groupes : entrée publique `Aga Bob Probe` (index 82), groupes C2P=83, IFF=84, BOBS=85, AGA=86. Le témoin renvoie 1, **aucun rendu de Bob/BATCH encore** ; **Gates B WinUAE et C Compiler R85 NON TESTÉES**. Le constructeur `tools/build_m19_p22_fourth_unit_probe.py --write-dist` ne modifie que la Lib active après contrôle SHA de LAST_GOOD ; `--emit-base64` sert à constituer exactement le blob Git.

**Suite :** importer [`tests/design/M19_P22_4UNIT_PROBE_01.asc`](../tests/design/M19_P22_4UNIT_PROBE_01.asc) avec le **candidat R85**, jamais avec R84. Contrôler Gate B Runtime 68020 puis Gate C Compiler avant l'API de dessin groupé `Aga Bob Batch`. Un seul test actif reste `tests/current/M19_P21_ZCACHE_BENCH_01.asc` (P2.1 PASS) ; le témoin est volontairement dans `tests/design`. `main` seulement, ni nouvelle branche ni promotion LAST_GOOD.

[Contrat et historique du quatrième bloc](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md).

---


## M19 P2.2 — QUATRIÈME GROUPE NATIF BOBS, témoignage AP20 isolé (15/11/2026)

**Accord de l'auteur : « on se lance »** pour le quatrième bloc natif. Le premier incrément est volontairement **une preuve d'infrastructure** : `tools/build_m19_p22_fourth_unit_probe.py` reconstruit en mémoire une **bibliothèque expérimentale à quatre groupes** à partir de R84 v0.13.29 `LAST_GOOD`, conserve les 76 commandes R84 et les trois corps C2P/IFF/AGA, ajoute seulement `Aga Bob Probe` (témoin qui renvoie 1, **aucun dessin de Bob**). Le véritable `Aga Bob Batch(Bank,Count)` n'est **pas** encore implémenté et ne doit pas être présenté comme disponible.

**Gate A :** `tools/test_m19_p22_fourth_unit_probe.py` utilise l'émulateur Unicorn MC68020 pour l'interpréteur, le dispatcher V2, l'exécution du témoin et les retours ABI. [Workflow dédié](../.github/workflows/m19-p22-fourth-unit-gate-a.yml) : en cas de succès, dépose un fichier **expérimental téléchargeable** `M19_P22_4UNIT_PROBE_GATE_A_ONLY`. **En attendant le résultat CI, les Gates A/B/C P2.2 sont non validées.** Témoin AMOS volontairement placé sous `tests/design/M19_P22_4UNIT_PROBE_01.asc` ; **ne pas l'utiliser avec R84 seule**.

**Protection :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent strictement inchangés, tout comme l'unique ASC actif `tests/current/M19_P21_ZCACHE_BENCH_01.asc` (P2.1 PASS). `main` seulement, aucune branche/tag/release. [Contrat et statut](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md). Prochaine étape si Gate A PASS : Gate B WinUAE et Gate C Compiler avec binaire expérimental, puis étude de la boucle Batch AGAPIC/FICON8 et de ses appels inter-unités.

---


## M19 P2.1 — DERNIER BENCHMARK TERMINÉ : Gate B Runtime 68020 PASS (15/11/2026)

**Journal utilisateur :** `M19_P21_ZCACHE_RUNTIME.TXT`, `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68020`, `CPU_ATTNFLAGS 3`, `RESULT 1`, `VERDICT PASS`, `ERR 0` ; profil 14 MHz/JIT OFF précisé par l'auteur (non enregistré par le programme). **240 frames, 9 088 dessins, cinq invalidations, douze séries complètes**, `SORT_CALLS_TOTAL 1225`, `CACHE_BUILDS_TOTAL 17`, `CACHE_HITS_TOTAL 1188`, erreurs Sort/Fill/Draw/Swap 0/0/0/0, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, deltas Chip/Fast 0, `CLOSE_RETURNED 1`.

**Résultats (moyenne P0/P1, Timer PAL nominal 20 ms/tick) :** temps de composition BASE → CACHE : **4 Bobs 60,17 → 56,67 ms/frame (−5,8 %)** ; **8 Bobs 96,33 → 81,33 (−15,6 %)** ; **16 Bobs 189,67 → 132,00 (−30,4 %)**. Présentation VBL/Swap compris : 4 Bobs 80 → 61 ms, 8 Bobs 101 → 100 ms, 16 Bobs 200,5 → 140 ms.

**Conclusion :** le cache de l'ordre `(Z, ID)` avec invalidation explicite est recommandé dans le gestionnaire BASIC ; aucun changement de production n'est autorisé par ce test. Le dessin et le fond demeurent coûteux à 16 Bobs. **Fin du dernier essai demandé ; ne pas proposer une nouvelle campagne de benchmark.** Aucune API native décidée, R84 v0.13.29 `LAST_GOOD` intacte, `main` uniquement. Gates Compiler M19 et matériel physique non testées.

**Rapport officiel :** [Résultats M19 P2.1 Z-cache 68020/noJIT](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md). Seul ASC actif inchangé : [M19_P21_ZCACHE_BENCH_01.asc](../tests/current/M19_P21_ZCACHE_BENCH_01.asc).

---


## M19 P2.1 — dernier essai Z BASE vs CACHE, profil 68020 sans JIT (15/11/2026)

**Décision auteur :** « dernier essai », directement sous profil **WinUAE MC68020 14 MHz, PAL, JIT OFF**. **Un seul ASC actif** : [tests/current/M19_P21_ZCACHE_BENCH_01.asc](../tests/current/M19_P21_ZCACHE_BENCH_01.asc). L'ancien banc [M19_P2_BENCH_BOBS_01.asc](../tests/passed/M19_P2_BENCH_BOBS_01.asc) est **archivé avec son blob Git identique** (`4345d8728af1d6dba29a5936463219ac49b3b109`), et son [rapport 68020 PASS](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) reste la référence.

**P2.1 PRET, AUCUN LOG WinUAE ENCORE :** même source AGAPIC/FICON8 que P2 (4,8,16 objets) ; `BASE` trie à chaque frame, `CACHE` conserve l'ordre jusqu'à modification Z/visibilité/compte. Cinq contrôles d'invalidation avant mesure ; deux passages inversés BASE→CACHE puis CACHE→BASE. Chaque mode × N × passage : 120 demandes d'ordre, 60 compositions fond+Bobs (sans Swap) et 20 VBL+Swap. 120 Fill séparés ; résultat attendu `FRAME_OK 240`, `DRAW_OK 9088`, `SORT_CALLS_TOTAL 1225`, `CACHE_BUILDS_TOTAL 17`, `CACHE_HITS_TOTAL 1188`, `CACHE_INVALID_TESTS 5`, `BENCH_CASES 12`, `RESULT 1`, `ERR 0`. **Gate B de P2.1 à recevoir**, ne pas assimiler au précédent PASS.

**Journal attendu :** `RAM:M19_P21_ZCACHE_RUNTIME.TXT`, voir [instructions tests/current](../tests/current/README.md) et [protocole détaillé](../benchmarks/README_M19_P21_ZCACHE_68020_NOJIT.md). Échap signale `ERR 41`. `Timer` PAL nominal 20 ms/tick, aucune mesure de cycles CPU directe. Toute attente Safe en phase COMP invalide l'interprétation « temps CPU pur ». Pas d'AMOS Compiler ni de matériel physique testé pour P2.1.

**Aucun changement de bibliothèque :** R84 v0.13.29 `LAST_GOOD` protégée ; `main` uniquement, **aucune branche ni commande AP20 native nouvelle**. Le résultat du dernier A/B doit guider la décision sur le tri BASIC, pas déclencher automatiquement une nouvelle API.

---


## M19 P2 — benchmark MC68020/14 MHz/JIT OFF PASS ; analyse et prochaines optimisations (15/11/2026)

**Nouveau journal utilisateur :** `M19_P2_BENCH_BOBS_RUNTIME 68020 14Mhz noJIT.TXT`. `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68020`, `CPU_ATTNFLAGS 3`, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK 240`, `DRAW_OK 9088`, erreurs Sort/Fill/Draw/Swap `0/0/0/0`, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, Chip/Fast delta 0, `CLOSE_RETURNED 1`. **14 MHz et JIT OFF déclarés par l'auteur, non auto-journalisés.** Bibliothèque R84 `LAST_GOOD` et source benchmark intactes.

**Deux passages, ticks bruts** (800 tris / 120 fonds / 120 compositions / 40 présentations par charge) :
- **4 Bobs :** tri 162/163 ; fond 188/188 ; comp 360/361 ; disp 160/160.
- **8 Bobs :** tri 604/604 ; fond 188/188 ; comp 578/577 ; disp 202/201.
- **16 Bobs :** tri 2347/2347 ; fond 188/188 ; comp 1137/1137 ; disp 401/401.

**PAL nominal 20 ms/tick :** composition ~**60,08 / 96,25 / 189,50 ms/frame** ; présentation ~**80,00 / 100,75 / 200,50 ms/frame** ; tri BASIC ~**4,06 / 15,10 / 58,68 ms/appel** (4/8/16). Fond constant ~31,33 ms/frame ; reste de dessin estimé ~6,2 ms par Bob, selon soustraction de séries indépendantes. À 16 objets, le tri représente ~31 % du temps de composition, avec des Z pourtant fixes.

**Comparaison :** 68030 avec JIT activé (test précédent PASS) composait ~23,25 / 23,42 / 23,83 ms/frame, non extrapolable au 68020 sans JIT. [Rapport 68020 et analyse détaillée](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) · [Rapport 68030/JIT](../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md). Les deux benchmarks sont qualifiés **Runtime WinUAE**, pas Compiler ou matériel.

**Suite recommandée, non engagée :** benchmark A/B **cache d'ordre Z en BASIC** (trier uniquement si Z, création, suppression, visibilité changent), puis mesure isolée des formats AGAPIC opaque/masqué et FICON8 et de la stratégie de fond. **Ne pas créer d'API native sans preuve d'un gain ciblé.** Le test actif reste `tests/current/M19_P2_BENCH_BOBS_01.asc`, seul ASC. P2.0 fonctionnel archivé, R84 `LAST_GOOD` inchangée, `main` uniquement.

---


## M19 P2 — benchmark complet 68030/JIT PASS, 68020 sans JIT attendu (15/11/2026)

**Second journal utilisateur `M19_P2_BENCH_BOBS_RUNTIME(1).TXT` :** WinUAE Runtime, `CPU 68030`, **JIT activé selon l'auteur (non enregistré dans le log)**, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK 240`, `DRAW_OK 9088`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, `SAFE_RETRIES 1` global, `COMP_SAFE_RETRIES 0` sur les six séries, Chip/Fast delta 0, fermeture 1.

**Ticks P0/P1 (800 tris / 120 fonds / 120 compositions / 40 présentations) :** N4 tri 0/0, fond 139/140, comp 140/139, disp 80/80 ; N8 tri 1/1, fond 140/139, comp 140/141, disp 80/80 ; N16 tri 6/6, fond 139/139, comp 143/143, disp 80/80. `Timer` PAL 20 ms/tick nominal : composition ≈ 23,25 / 23,42 / 23,83 ms/frame. **Ne pas extrapoler cette exécution JIT au MC68020 physique.**

**Rapport de référence :** [68030 JIT PASS](../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md) ; [premier run interrompu](../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md) conservé. Source `tests/current/M19_P2_BENCH_BOBS_01.asc` inchangée, seul ASC actif, bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée.

**Suite annoncée :** nouvel essai du même ASC en **MC68020 à 14 MHz, JIT OFF, PAL** ; conserver le journal distinct. Aucune API native approuvée.

---


## M19 P2 — premier journal benchmark 4/8/16, arrêt Échap (15/11/2026)

**Source active inchangée :** [tests/current/M19_P2_BENCH_BOBS_01.asc](../tests/current/M19_P2_BENCH_BOBS_01.asc) (SHA blob `4345d8728af1d6dba29a5936463219ac49b3b109`). Bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée. CI [`6138657` Artifact integrity PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43691301111).

**Journal utilisateur `M19_P2_BENCH_BOBS_RUNTIME.TXT` :** `RUN_MODE RUNTIME`, CPU annoncé `68030`, `RESULT 0`, `VERDICT FAIL`, **`ERR 20` = `Aga Key` a retourné 69 (Échap)**, `FRAME_OK 41/240`, `DRAW_OK 1736` (arithmétique des phases cohérente), `DRAW_FAIL 0`, `SWAP_FAIL 0`, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, `CHIP_DELTA 0`, `FAST_DELTA 0`, `CLOSE_RETURNED 1`.

**Mesures partielles P0 :** 4 Bobs : tri `0` tick/800, fond `139` ticks/120, composition `140` ticks/120, présentation `80` ticks/40 ; 8 Bobs : tri `1`, fond `140`, composition `140`, présentation **non terminée**. **16 Bobs et second passage totalement non mesurés**, les cases zéro sont des valeurs par défaut. Timer PAL nominal 20 ms/tick ; 4/8 composition ≈ 23,33 ms/frame, surtout liée au fond, mais la précision du timer et le mode Runtime interdisent d'en déduire une accélération ou une conclusion native. [Rapport détaillé](../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md).

**Prochaine action :** refaire l'ASC **inchangé** sans presser Échap, laisser 240 frames, conserver le fichier RAM: avant tout nouvel essai. Si `ERR 20` survient sans appui Échap, instrumenter le clavier au lieu de présumer une erreur d'utilisateur. Pour l'analyse cible, exécuter ensuite 68020/14MHz, PAL/JIT OFF, séparément du 68030. **Gate B benchmark non acquise ; aucune API native décidée.**

---


## M19 P2 — benchmark 4, 8 et 16 Bobs PRÊT, WinUAE à exécuter (15/11/2026)

**Accord utilisateur « ok » pour le benchmark proposé après le PASS P2.0.** Bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée, `main` uniquement. Aucune nouvelle instruction native, API AP20, branche ou release.

**Seul ASC actif :** [tests/current/M19_P2_BENCH_BOBS_01.asc](../tests/current/M19_P2_BENCH_BOBS_01.asc). Le P2.0 validé Runtime est archivé **octet pour octet** dans [tests/passed/M19_P2_OBJECTS_01.asc](../tests/passed/M19_P2_OBJECTS_01.asc) ; son [rapport PASS](M19_P2_WINUAE_RUNTIME_2026-11-15.md) reste la preuve, **pas** le benchmark qui n'a pas encore été testé.

**Protocole :** [benchmarks/README_M19_P2_BOBS_4_8_16.md](../benchmarks/README_M19_P2_BOBS_4_8_16.md). 4/8/16 objets, sources partagées générées avant chrono (1/4 AGAPIC masqués, 1/4 AGAPIC opaques, 1/2 FICON8 masqués), deux passages `P0/P1`. `Timer` PAL : **800 tris BASIC**, **120 Fill seuls**, **120 compositions sans Swap**, **40 frames VBL+Swap** par charge et passage. `Safe` contrôlé avec retries bornés, `Aga Swap` explicite, zéro dessin en interruption. Le banc **n'inclut pas AMAL**, afin d'isoler tri + dessin.

**Attendu :** exécution AMOS Runtime sous WinUAE AGA PAL / 68020 14MHz / JIT OFF (68030 possible pour contrôle séparé), banques 11..23 libres, rapport `RAM:M19_P2_BENCH_BOBS_RUNTIME.TXT`. `RESULT 1`, `ERR 0`, 16 objets préparés, `FRAME_OK 240`, `DRAW_OK 9088`, aucun échec Draw/Swap. Les champs `N4/N8/N16_P0/P1_*_TICKS` contiennent les **mesures à recevoir**. Attention : `Timer` donne un temps écoulé, pas des cycles CPU ; retries Safe/Swap à conserver.

**Statut : source construite et contrôlée statiquement, mais Gate B benchmark / chiffres WinUAE NON VALIDÉS.** Compiler M19 et Amiga physique non testés. La décision d'implémenter un gestionnaire natif n'est pas prise.

---


## M19 P2.0 — Gate B Runtime WinUAE PASS (journal reçu le 15/11/2026)

**Source de référence :** `tests/current/M19_P2_OBJECTS_01.asc` (sous-routines à préfixe `_`), bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée. L'auteur a transmis `M19_P2_OBJECTS_RUNTIME.TXT`. **Gate B du prototype P2.0 PASS dans ce scénario** (`RUN_MODE RUNTIME`, `PRG_STATE 1`, CPU déclaré 68030, `RESULT 1`, `VERDICT PASS`, `ERR 0`).

**Mesures :** 240 frames, sources AGAPIC/FICON8 `6/4`, cinq objets créés et un supprimé, ID périmé/frame invalide/banque absente refusés `1/1/1`, masquage et réapparition `1/1`, priorité Z `2`, égalité stable `1`, sonde de superposition `PROBE_OK 1`/`PIXEL_DIFF 1`, 4 cas de clipping, 2 objets intégralement hors écran, 217 frames avec quatre objets dessinés, mouvements AMAL `239/239`, changements de frames `15/10`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, Chip/Fast delta `0/0`, `CLOSE_RETURNED 1`. [Rapport complet](M19_P2_WINUAE_RUNTIME_2026-11-15.md).

**Qualification limitée :** WinUAE Runtime 68030, 320×256, 256 couleurs/8 plans, banc P2.0 uniquement. **Ni AMOS Compiler M19 (Gate C), ni `PRG_STATE 0`, ni Amiga AGA physique (Gate D), ni cadence 50 FPS ne sont établis** par ce journal. La sonde RLE porte sur un seul pixel. Aucun développement d'API native approuvé.

**CI sur le commit préexistant `c65c820` :** [Artifact integrity PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337384) et [R84 Gate A ciblée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337256). La validation Runtime ci-dessus est **indépendante** de cette CI. Le journal utilisateur ne comprend pas les valeurs affichées `LOG OPEN ERR` / `LOG CLOSE ERR`.

**Suite conseillée :** mesurer d'abord le coût CPU/Chip du gestionnaire BASIC avec des charges croissantes, puis décider si des commandes AP20 natives sont réellement justifiées. L'étude des sprites matériels AGA reste le volet P3 distinct. Conserver la bibliothèque et le banc P2.0 validé sans modification.

---


## M19 P2.0 — correction du nom des sous-routines et préflight (15/11/2026)

**Retour WinUAE de l'auteur :** capture AMOS Professional avec `Syntax error` à `Gosub Sort _OBJECTS`. Cause vérifiée : `SORT` est un mot-clé AMOS et le nom source `SORT_OBJECTS` était séparé en deux tokens. Le commit source déjà présent sur `main`, [`18b01a6`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/18b01a6976b9ac61a2c2bf676e69da558f8571b2), préfixe les 7 sous-routines et tous leurs `Gosub` par `_` (dont `_SORT_OBJECTS`), sans changer leurs traitements ni la bibliothèque R84.

**Régression CI identifiée :** le test historique `tools/test_current_ram_log.py` imposait `End` comme dernière instruction physique. Le P2.0 utilise **`End` puis les sous-routines `Gosub` terminées par `Return`**, syntaxe normale. Le contrôle est adapté pour accepter ce cas **sans autoriser un programme sans End ni boucle infinie terminale**. `tools/test_current_amos_blocks.py` signale désormais les noms commençant par une commande réservée (`SORT_`, `MOVE_`, etc.) et inclut un test de régression pour `Gosub SORT_OBJECTS`.

**Statut :** correction structurelle / source uniquement ; **un nouvel essai AMOS/WinUAE reste nécessaire** avant de prétendre P2.0 Gate B PASS. P1 archived unchanged, `LAST_GOOD` inchangée, aucun nouveau token/AP20. [Test actif](../tests/current/M19_P2_OBJECTS_01.asc) · [Consignes](../tests/current/README.md).

---


## M19 P2.0 — prototype BASIC, un seul ASC actif (15/11/2026)

**Accord auteur : « ok go » pour commencer le prototype P2.0**, pas d'autorisation d'ajouter un token/une API native. R84 v0.13.29 `LAST_GOOD` protegee, 68020 minimum. L'experience AP20 V3 parallele du commit `a36c8ed` est hors du perimetre M19 ; aucun de ses fichiers n'est modifie.

**Unique test actif :** [tests/current/M19_P2_OBJECTS_01.asc](../tests/current/M19_P2_OBJECTS_01.asc). Le banc P1 WinUAE-PASS a ete **archive octet pour octet** dans [tests/passed/M19_P1_AGAPIC_BOBS_01.asc](../tests/passed/M19_P1_AGAPIC_BOBS_01.asc). Ne pas annoncer P2.0 PASS sans journal WinUAE.

**Contenu :** gestionnaire AMOS BASIC par `Dim` et `Gosub/Return` : 4 objets initiaux (2 AGAPIC AMAL manuel + 1 FICON8 BASIC + 1 AGAPIC opaque BASIC), masquage/retour, changements de frames cadences, tri stable Z/ID, sondes 1x1 de priorite, quatre clips et culling, suppression ID4 puis nouveau ID5, refus d'ID mort et de frame/banque invalides. Fond complet sur back buffer Safe, `Aga Swap` explicite, journal `RAM:M19_P2_OBJECTS_RUNTIME.TXT`. Dimension 320x256x256, sources generees par le test, banques 11..23 libres.

**Qualification :** controles structurels de source et simulation de compteurs de 240 frames, **pas une compilation ni une execution AMOS**. Gate B P2.0 Runtime WinUAE EN ATTENTE ; C Compiler, D materiel et mode interprete strict non testes. Voir [instructions](../tests/current/README.md) et [contrat P2](M19_P2_OBJECT_MANAGER_CONTRACT.md). Reprendre directement avec le log WinUAE, puis decider si la gestion native est vraiment necessaire.

---


## M19 P2 — contrat d'objets proposé, pas d'API nouvelle (15/11/2026)

**Nouvelle référence de conception :** [M19_P2_OBJECT_MANAGER_CONTRACT.md](M19_P2_OBJECT_MANAGER_CONTRACT.md). L'auteur a autorisé l'étude P2. Proposition de **prototype d'abord en AMOS BASIC**, réutilisant AGAPIC v1/v2 et FICON8, avec objets logiques (ID, source/frame, X/Y et hotspot, Z stable, visibilité), mouvement BASIC ou AMAL manuel, composition uniquement sur back buffer Safe, zéro rendu en interruption et Swap explicite.

**Historique avant feu vert P2.0 :** proposition de contrat ; la version actuelle de reprise est en tête du fichier. Aucune signature AP20 native approuvée ; le P1 WinUAE PASS est maintenant archivé. R84 v0.13.29 `LAST_GOOD` et archives intactes.

**CI du commit P1-documentation :** les marqueurs de version EN/FR sont désormais validés dans le contrôle README ; un ancien préflight `tools/test_opt020_p1e_benchmark_static.py` rejette encore `M19_P1_AGAPIC_BOBS_01.asc` parce que sa liste de noms possibles s'arrête à R84. Le garde est limité au **benchmark historique hors tests/current** + **unique ASC actif** dans cette mise à jour. Pas de modification des formules du benchmark ni du binaire. **CI complète à revérifier**.

**Suite :** validation du contrat P2, puis un ASC P2.0 BASIC en remplaçant/archivant proprement le P1 courant ; Gate B Runtime sur le nouveau scénario, avant toute décision d'API native. Aucun sprite matériel : sujet P3.

---


## M19 P1 — Gate B Runtime WinUAE PASS (journal reçu le 15/11/2026)

**Source testée :** `tests/current/M19_P1_AGAPIC_BOBS_01.asc`, R84 v0.13.29 `LAST_GOOD` intacte. Journal auteur `M19_P1_AGAPIC_BOBS_RUNTIME.TXT` et capture WinUAE.

**Résultats :** `PRG_STATE 1`, `CPU 68030`, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `CAP_OK 6`, `META_OK 6`, `PROBE_OK 1`, `PIXEL_DIFF 1`, `FRAME_OK 240`, déplacements 239/239, 15/10 changements d'image, 3 inversions de priorité, 46 frames avec chevauchement, 240 clips, 0 échecs de dessin/Swap, delta Chip/Fast 0, fermeture 1. **P1 Gate B PASS** sur le scénario Runtime 68030, 8 plans. [Rapport](M19_P1_WINUAE_RUNTIME_2026-11-15.md).

**Limites :** aucune validation M19 Compiler Gate C, interprété strict ni Amiga physique Gate D ; aucun nouvel objet matériel ni API.

**CI GitHub :** échec antérieur dans `tools/test_readme_api_coverage.py` en raison des marqueurs exacts de version absents des deux README, sans relation avec le rendu P1. Libellés ajustés dans ce commit documentaire, **nouvelle CI à vérifier**.

**Suite :** concevoir et faire valider le contrat d'objets P2 avant toute signature d'API ou implémentation native.

---


## M19 P1 EN COURS — multi-Bobs AGAPIC v1/v2 (14/11/2026)

**Unique ASC actif** : [tests/current/M19_P1_AGAPIC_BOBS_01.asc](../tests/current/M19_P1_AGAPIC_BOBS_01.asc). P0 archivé à [tests/passed/M19_P0_AMAL_BOBS_01.asc](../tests/passed/M19_P0_AMAL_BOBS_01.asc). Bibliothèque R84 v0.13.29 `LAST_GOOD` intacte ; `main` uniquement.

**Historique avant la validation Runtime P1 : prototype préparé** : six images AGAPIC 24×24, v1/v2, masquées et opaques, deux canaux AMAL en synchronisation manuelle, animation d'image contrôlée toutes les 16/24 frames, ordre de rendu alterné, comparaison de deux captures RLE 1×1 avec ordre de dessin inversé, quatre clips et redessin du fond dans le back buffer Safe avant Swap.

**Essai attendu :** AMOS Runtime, 320×256×256, banques 11..19 libres, puis journal `RAM:M19_P1_AGAPIC_BOBS_RUNTIME.TXT` et observation visuelle. `CAP_OK 6`, `META_OK 6`, `PIXEL_DIFF 1`, `FRAME_OK >= 180`, mouvements, frames, priorités, `DRAW_FAIL 0`, `SWAP_FAIL 0`, fermeture correcte. Gate B P1 maintenant attestée (voir première section) ; Gates C/D non testées. [Consignes](../tests/current/README.md) · [Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md).

---


## M19 P0 — résultat WinUAE et suppression du clignotement (14/11/2026)

**Validation reçue :** `M19_P0_AMAL_BOBS_RUNTIME.TXT` : `PRG_STATE 1` (Runtime), `CPU 68030`, `RESULT 1`, `ERR 0`, 211 frames, déplacements X/Y = 210/210, aucun refus Draw/Swap, mémoire Chip/Fast à delta 0, `CLOSE_RETURNED 1`. Le rendu des deux Bobs a été confirmé. **Gate B M19 P0 PASS dans ce scénario** ; aucune extrapolation au mode strictement interprété, Compiler ou matériel physique.

**Diagnostic visuel :** le clignotement était lié aux expressions AMAL `Let A=3-A` et `Let A=7-A` (alternance d'image à chaque frame), pas à une erreur observée de dessin/Swap. L'auteur confirme qu'il disparaît en retirant ces expressions. Source `tests/current/M19_P0_AMAL_BOBS_01.asc` mise à jour pour conserver les images fixes 1 et 3. **Nouveau journal de la version corrigée non reçu** ; le PASS chiffré correspond à la version initiale.

**Suite engagée :** P1 a désormais son banc actif ; voir la première section. Conserver R84 `LAST_GOOD` et ne pas ajouter d'API sans contrat approuvé. [Rapport](M19_P0_RUNTIME_DIAGNOSTIC_2026-11-14.md) · [Plan](M19_SPRITES_BOBS_AMAL_PLAN.md).

---


## Chantier M19 P0 ENGAGE — 14/11/2026 (apres R84 promue)

**Plan de référence approuvé :** [M19 sprites matériels, Bobs et AMAL](M19_SPRITES_BOBS_AMAL_PLAN.md). Première étape : AMAL manuel (`Synchro Off`, deux programmes `Amal ... To adresse`, `Synchro` dans la boucle BASIC), deux Bobs logiciels via `Aga F Icon` dans le back buffer AGA privé, sans dessin en interruption. **Aucune nouvelle commande native** ; R84 et `LAST_GOOD` restent identiques et protégées.

**Test AMOS courant unique :** `tests/current/M19_P0_AMAL_BOBS_01.asc` (remplace comme banc actif l'ancien R84 déjà figé dans `tests/passed/AGAPIC_R84_V1_V2_01.asc`). Ce P0 est un prototype source et doit être contrôlé sous AMOS/WinUAE ; **Gate B M19 P0 Runtime désormais attestée sur le scénario initial ; Gate C et mode strictement interprété non attestés**. Rapport attendu `RAM:M19_P0_AMAL_BOBS_<RUN_MODE>.TXT`. Suivre [tests/current/README.md](../tests/current/README.md). Un seul ASC courant et aucun binaire M19.

---


## R84 v0.13.29 — PROMUE `LAST_GOOD` le 14/11/2026 (autorisation explicite)

**Circuit unique sur `main` :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **76 commandes / 85 entrées AP20**, trois modules C2P/IFF/AGA (5 558 / 2 508 / 56 580 octets). **R83 historique** : SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, 64 188 octets, reconstruite par `tools/build_aga_r83_modular.py` et conservée dans Git.

**Validation :** Gate A CPU native/CI PASS (44 cas Info + 47 captures) ; **Gate C AMOS Compiler PASS** sur WinUAE 68030 avec une banque incluse lors de la compilation, 4/8 plans, `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 2`, Chip 0 et Fast **−11 920 octets**. **Gate B Runtime corrigée : NON attestée séparément**, ce que l’auteur accepte en autorisant la promotion, sans nouvel essai. Quatre fichiers ABK restent dans `RAM:` au moment de la mesure Fast ; aucune fuite native n'est établie par ce delta. `PRG_STATE 0` strict et Amiga physique Gate D non testés.

**Test actif unique :** `tests/current/AGAPIC_R84_V1_V2_01.asc`, copie identique figée dans `tests/passed/`. Pas de branche ni binaire parallèle, aucun tag, release GitHub ou publication Aminet. [Rapport de promotion](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Journal compilé](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md).

Les états R84 candidate, R83 et antérieurs ci-dessous sont **historiques**.

---

## HISTORIQUE — R84 v0.13.29 avant promotion (14/11/2026)

- **Unique binaire de travail :** `dist/AMOSPro_AGA.Lib`, R84 **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, 76 commandes / 85 entrées AP20 ; unités C2P 5 558, IFF 2 508, AGA/AGAPIC 56 580 (marge 8 954 octets).
- **`LAST_GOOD` R83 protégée :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, ses Gates A/B/C validées. **R84 candidate NON PROMUE.**
- Nouveaux points d’entrée : `Aga Bank Image Info(Bank,Champ)` (5 champs, v1 palette/ModeID absents=0, échec=-1) et `Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` (v1 ou v2). Ancienne `Aga Image Capture` préservée.
- **Gate A native CPU/CI R84 PASS** : 44 cas d'Info v1/v2, 47 captures v1/v2 sur vrai 68020 émulé, structure AP20/ABI, métadonnées/flux RLE, palette/ModeID, banque occupée, mémoire, dispatch.
- **Gates B Runtime WinUAE et C AMOS Compiler EN ATTENTE.** Test unique actif : `tests/current/AGAPIC_R84_V1_V2_01.asc`. Le test R83 est déjà dans `tests/passed`. Exécuter les 2 modes, collecter `RAM:AGAPIC_R84_RUNTIME.TXT` et `RAM:AGAPIC_R84_COMPILED.TXT`. Ne pas déduire une Gate D physique ni `PRG_STATE 0`.
- Pas de nouvelle branche, pas de tag/release/Aminet, pas de binaire parallèle. Ne promouvoir que sur nouvelle autorisation explicite.

[Roadmap](ROADMAP.md) · [Contrat](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Rapport Gate A](AGAPIC_R84_GATE_A_2026-11-14.md).

Les sections R83 et antérieures ci-dessous sont **historiques**.

---

## ÉTAT COURANT — R83 v0.13.28 PROMUE LAST_GOOD (14/11/2026)
