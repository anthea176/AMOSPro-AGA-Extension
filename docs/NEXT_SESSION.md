# Reprise actuelle — AMOSPro AGA Extension

## M19 P0j-b5 — verrou de Swap après échec d'une frame (source-only, Gate A à vérifier)

[Émetteur natif et protocole de tests](M19_P0J_SWAP_BARRIER_GATE_A_2026-11-17.md). Les trois points d'entrée **privés** sont `guarded_frame_draw_entry`, `guarded_swap_entry` et `guarded_close_entry`. La première routine active une barrière **DIRTY avant tout risque de DMA** et passe à READY seulement après le rendu complet P0j-b4 ; un refus laisse DIRTY persistant. La deuxième redirige **dans une candidate AP20 construite uniquement en mémoire** le token public existant `Aga Swap`, vérifie DIRTY/owner/State/DB/front et appelle seulement si autorisé la routine native AGA Swap originelle (signature figée, cible calculée à partir de A5+$1c8). La troisième raccorde la fermeture native P0c, sans réinitialiser DIRTY si l'écran reste ouvert. Deux stubs AP20 supplémentaires sont placés après BOBS pour respecter la portée PC16 ; **85 commandes inchangées, aucune `Aga Bob Draw` publique**.

**Politique conservatrice provisoire :** même un échec du préflight avant DMA exige Close/Reopen avant un nouveau Swap. Un Draw réussi ne peut pas lever un échec précédent. Pas de reconstruction partielle silencieuse, pas de Swap implicite. Le code n'est **ni distribué ni installé** ; Gate A native/CI **en attente**, B/C/D non exécutées. `dist/AMOSPro_AGA.Lib`, ASC actif, `LAST_GOOD` et archives inchangés. Le futur retour AMOS public proposé est `_OK=Aga Bob Draw` (1 après rendu complet, 0 après échec), **syntaxe/token non publiés et non encore validés par le véritable Compiler**.

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

**Protections :** `dist/AMOSPro_AGA.Lib` P0c **87 020 octets, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`**, `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 sont inchangés. Aucun nouveau `.asc` actif, aucune promotion, aucun dépôt/branche supplémentaire. La section P0d suivante documente le premier peintre **2082 octets avant correction du clipping** : elle est conservée comme checkpoint historique, pas comme état du noyau courant.

## M19 P0d — premier noyau Blitter Bob AGA privé : Gate A MC68020 PASS (16/11/2026)

**Source-only sur `main`** : [`tools/m19_p0d_private_blit_emit.py`](../tools/m19_p0d_private_blit_emit.py) construit un noyau privé de dessin **2 082 octets, MC68020 minimum**, sans token AP20, sans nouvelle `.Lib`, sans ASC supplémentaire. [Banc natif](../tools/test_m19_p0d_private_blit_native.py) : **720 scénarios pixel-exacts** (profondeurs 1/4/8, largeurs 1/17/31/32/37, masques transparence index 0/non nul ou opaque, clipping, deux placements du code) + **4 refus** (source Fast, profondeur incompatible, stride invalide, CPU sans AFF_68020). [CI ciblée complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43952569895), incluant le noyau sous Unicorn MC68020 et le garde ABI. Les services Exec/graphics et les transferts Blitter sont **simulés** : cette Gate A ne valide ni le DMA réel, ni WinUAE, ni le Compiler.

**Contrat privé du peintre :** source AGBO planaire *déjà préparée en vraie Chip par P0c*, masque 1 bit indépendant, BitMap back **déjà sécurisé par Safe**, `BltBitMapRastPort` opaque ou `BltMaskBitMapRastPort` masqué, `WaitBlit` avant retour, aucun `Aga Swap` automatique. Le noyau refuse les profondeurs source/écran différentes et ne gère pas le buffer, la sélection d'image, l'identité/génération de banque, les objets persistants ou la récupération des notifications Safe. **Un appelant natif vérifié doit encore le relier au registre P0c et au vrai back buffer AGA**, avec contrôle intégral des plages source/masque et de leur propriété avant DMA. Ne pas présenter ce noyau privé comme un Bob déjà affichable par une commande AMOS.

**Prochaine action :** auditer le chemin `Aga Bob Bank` existant et l'ABI AP20, puis intégrer une préparation Chip déclenchée en contexte public et un rendu Bob unique dans le back buffer sûr. Passer Gate A **sur le candidat complet** avant de demander une bascule explicitement autorisée de `dist/AMOSPro_AGA.Lib` et du seul ASC actif. Tests réels Gates B/C uniquement après cette bascule. **P0c 87 020 octets / SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`**, `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`, et R84 `LAST_GOOD` restent inchangés ; aucune promotion, pas d'archive, ni de nouveau binaire.

## M19 P0c — journaux Gates B et C PASS (16/11/2026)

Deux fichiers transmis par l'auteur : **`M19_P0C_RUNTIME.TXT`** (`PRG_STATE 1`) et **`M19_P0C_COMPILED.TXT`** (`PRG_STATE -1`). Dans **les deux** : `RESULT 1`, `ERR 0`, `VERDICT PASS` et `CLOSE_FIRST`, `CLOSE_WITH_DB`, `CLOSE_REOPEN` à **1**. **Gate A MC68020 PASS ; Gate B Runtime et Gate C Compiler PASS selon ces journaux** pour les trois séquences de fermeture. [Preuves, SHA256 des deux TXT et limites](M19_P0C_GATES_BC_2026-11-16.md).

Bibliothèque de travail **inchangée** : `dist/AMOSPro_AGA.Lib` P0c, **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; seul ASC `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` **inchangé**. Les TXT n'attestent ni l'empreinte de la copie installée dans WinUAE, ni les captures/CPU/JIT/ligne d'écran, ni le retour après dernier `End`. Callback End privé, interpréteur strict et Gate D **NON TESTÉS**. `LAST_GOOD` R84 intacte, aucune promotion. **Les sections antérieures ci-dessous sont des checkpoints historiques.**

## M19 P0c — CANDIDATE ACTIVE pour Gates B/C (autorisation du 16/11/2026)

**Bascule autorisée sur `main`** : binaire unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; **82 commandes / 92 entrées AP20**, source [builder P0c](../tools/build_m19_p0c_screen_close_in_memory.py) dérivée du P0b figé. **Seul ASC actif** : [`tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`](../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc) ; son design reste inchangé. Gate A native MC68020 PASS ; Gates B Runtime WinUAE et C vrai AMOS Compiler **NON TESTÉES**, Gate D NON TESTÉE. CPU 68030/JIT ON pour essais fonctionnels. **Aucune promotion `LAST_GOOD`** (R84 SHA inchangé), ni publication/ZIP/artefact CI. Le test actif P0b quitte `tests/current/` et reste accessible par Git, sans archivage forcé.

**Actions :** installer la Lib canonique dans le slot AGA d'AMOS, redémarrer, importer l'ASC par `Project → Merge ASCII`, exécuter Runtime puis Compiler et recueillir deux journaux distincts. [Protocole complet](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md). **Les sections P0c/P0b qui suivent sont des checkpoints historiques antérieurs à cette bascule**, et ne désignent plus la candidate ou l'ASC actif.



## M19 P0c — Screen Close public + callback End privé : Gate A MC68020 PASS (16/11/2026)

**CORRECTIF DE DISTRIBUTION (16/11/2026) :** ne plus distribuer P0c par l'artefact CI `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED`, ni l'exécuter directement depuis `tests/design/`. La règle est **une seule Lib dans `dist/AMOSPro_AGA.Lib` et un seul ASC dans `tests/current/` sur `main`**, uniquement après autorisation explicite du remplacement de P0b. Le workflow conserve les vérifications Gate A **en mémoire** sans exporter de `.Lib`. P0b, son test actif et `LAST_GOOD` restent inchangés ; **Gates B/C P0c en attente**. [Consignes à jour](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md).

**Nouveau candidat expérimental source-only (NON INSTALLÉ dans `dist/`)** : [builder AP20 V2](../tools/build_m19_p0c_screen_close_in_memory.py), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 82 commandes, 92 entrées AP20. Seuls le stub public `Aga Screen Close` (token 8) et le groupe BOBS 90 append-only changent ; groupe AGA 91 et API P0b restent intacts. Le vrai AGA Init, la vraie routine Screen Close et le vrai callback AMOS End sont exécutés sous Unicorn MC68020 avec services OS mockés. Pont `A5+0x1C8` → AGA State → ancienne routine Close (`+0x638`) sans BSR.W inter-unités ; libération Chip via `WaitBlit` **avant** l'ancienne fermeture. [Source Screen Close](../tools/m19_p0c_screen_close_bridge_emit.py) et [source End privé](../tools/m19_p0c_program_end_bridge_emit.py).

**[CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925480841) :** 38 scénarios réel Close, 54 scénarios End privé, 42 preclose, 64 registre, 120 AGBO/Chip, 64 Chip, 116 P0b ; [ASC de design préflight PASS](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc). [Rapport de Gate A](M19_P0C_SCREEN_CLOSE_BRIDGE_GATE_A_2026-11-16.md). L'artefact `M19_P0C_CLOSE_EXPERIMENT_GATE_A_UNINSTALLED` produit par cette **ancienne exécution** est une preuve historique ; il ne constitue pas un canal de distribution autorisé et les futurs runs n'en produisent plus.

**Verrou maintenu :** le callback `End` n'est armé que par l'entrée **privée** `program_end_arm_entry`, après staging Chip ; les commandes AMOS P0b ne préparent pas de Chip Bob et **ne l'appellent pas**. Il n'existe toujours pas de véritable rendu Bob ni de commande publique staging. **Gate B Runtime et Gate C Compiler P0c NON TESTÉES** ; aucune affirmation de fonctionnement de la Lib installée. Le test de design reste NON ACTIF ; ne lancer aucune Gate B/C P0c avant une bascule explicitement autorisée de la bibliothèque et de l'unique ASC courant. `dist/AMOSPro_AGA.Lib` P0b (82 376 octets) et R84 `LAST_GOOD` inchangées.

## M19 P0c — garde de pré-fermeture AGA natif, Gate A privée PASS (16/11/2026)

**Nouvelle source native MC68020 :** [`tools/m19_p0c_screen_preclose_emit.py`](../tools/m19_p0c_screen_preclose_emit.py), émetteur **source-only**, append-only sur le [registre P0c](../tools/m19_p0c_bank_registry_emit.py). Il ajoute `screen_preclose_entry` : vérification CPU/état, récupération de la base graphique **depuis `A5+0x1C8` → `State+8`** (et non le A4 du caller), contrôle de l'adresse de l'état, nettoyage des contextes Chip via `registry_close_entry`. Si le nettoyage échoue, il retourne **0 sans fermer l'écran** et sans écraser les allocations. Si le registre est vide, la fermeture répétée retourne **1**. **Le vrai `CloseWindow`/`CloseScreen` n'est jamais exécuté par cette entrée privée.**

**[CI Gate A privée PASS — 42 scénarios MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43920983278)** ([test](../tools/test_m19_p0c_screen_preclose_native.py)), unité BOBS privée **11 294 octets**, préfixes natifs P0b/P0c immuables. En régression dans la même CI : **64 PASS** registre, **120 PASS** AGBO/Chip, **116 PASS** API P0b, politique CPU/livraison séparée. Erreur initiale corrigée : une adresse temporaire `State+8` était prise à tort pour `GfxBase` en l'absence de celui-ci ; une variable de frame distincte évite tout appel `WaitBlit` sur ce faux pointeur.

**Point de liaison précisément identifié (non résolu)** : le token AP20 **`Aga Screen Close` est n°8, ciblant le groupe AGA V2 n°91, offset 2008**. Le registre BOBS est dans le groupe n°90. Le source `src/R88/*AGA_NATIVE.s` n'est qu'une **restauration mnémotechnique partielle d'audit** : interdit de l'utiliser pour patcher le vrai code de production. Le module AGA R88 comporte **56 580 octets de natif**, donc un simple `BSR.W` depuis BOBS n'est pas une solution à supposer. **Aucun hook automatique n'a été installé** sur la véritable commande de fermeture ni sur l'**End AMOS**. La fermeture du test est un modèle d'ordre d'appels et **non** l'exécution du Close historique réel.

**Suite bloquante :** retrouver/construire une liaison **source-auditée** entre le groupe AGA et l'entrée privée BOBS, avec contexte `GfxBase` vivant, et tester sur le *même candidat exact* l'entrée publique `Aga Screen Close`, le cleanup de sortie du programme et les relocations V2, avant toute nouvelle `.Lib` ou essai WinUAE/Compiler. Le binaire **P0b 82 376 octets** (SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`), R84 `LAST_GOOD` et l'unique ASC P0b validé restent **intacts**.

## M19 P0c — registre natif automatique de Chip par banque : Gate A privée 64 PASS (16/11/2026)

L'[émetteur du registre MC68020](../tools/m19_p0c_bank_registry_emit.py) ajoute **quatre points d'entrée privés** au préfixe P0b/P0c inchangé : préparation, lookup, libération d'une banque et fermeture globale. Un nœud **Exec AllocVec 32 octets, MEMF_PUBLIC|MEMF_CLEAR** par banque référence le contexte Chip 20 octets, sans banque AMOS supplémentaire ; l'état natif persistant mémorise **A5 propriétaire + tête de liste**. Une nouvelle entrée n'est chaînée **qu'après** réussite de la validation AGBO et de la préparation Chip. Les libérations attendent le Blitter via le helper P0c existant ; les boucles sont bornées à **256 contextes** et la fermeture est idempotente. Deux banques simultanées, états périmés, échecs d'allocation, ABI et nettoyage après effacement d'ABK sont couverts.

**[CI Gate A CPU MC68020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43917996936) : 64 scénarios registre, 120 validation AGBO, 64 helper Chip, 116 régression P0b, 11 094 octets de l'unité native privée ; [règles CPU/livraison PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43918000042).** Les services système **AMOS/Exec/graphics sont mockés**. Pas de nouvelle `.Lib`, aucun nouveau token AP20, aucune validation WinUAE/Compiler P0c.

**Limite bloquante :** l'entrée privée `registry_close_entry` est testée, mais **PAS raccordée à `Aga Screen Close`** du binaire installable. Un écran réellement fermé par la Lib actuelle n'appelle pas ce cleanup. Il reste à valider l'insertion de ce callback dans le cycle natif Open/Close (avec GfxBase toujours disponible), et l'invalidation robuste après `Erase`/`Load`/réutilisation d'adresse (ABA), avant le rendu Blitter. Le test actif P0b reste seul, bibliothèque P0b **82 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9` et R84 `LAST_GOOD` inchangées.

## M19 P0c — banque AGBO vérifiée + staging Chip privé : Gate A 120 PASS (16/11/2026)

Le nouvel [émetteur natif privé](../tools/m19_p0c_checked_bank_stage_emit.py) **MC68020 uniquement** ajoute au préfixe source P0b inchangé le contrôle de la banque AMOS réellement sélectionnée, la vérification de **toutes** les images/masques et des bits hors largeur, puis appelle le [noyau Chip privé](../tools/m19_p0c_chip_stage_emit.py). Trois chemins privés (staging, lookup d'identité/génération, release après `WaitBlit`) ont été éprouvés avec **deux contextes Chip indépendants sur deux banques**. [Banc CPU020](../tools/test_m19_p0c_checked_bank_stage_native.py) : **120 scénarios PASS**, 10 044 octets de code natif groupé, deux placements CPU 020 ; [CI ciblée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43916465599). Le noyau Chip précédent conserve **64 PASS**, P0b **116 PASS**. [Rapport](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md).

**Limites impératives :** Gate A **privée et simulée** (services Exec/AMOS/graphics mockés), aucun token AP20 ni `.Lib` P0c, pas de vraie allocation Chip WinUAE ni de dessin Blitter/objet Bob. Le **registre natif automatique des contextes par numéro de banque** et son cleanup à la fermeture restent à intégrer ; les deux contextes testés sont pour l'instant fournis explicitement au wrapper privé. Après `Erase`/`Load`, une **resélection de banque** reste obligatoire ; une réutilisation de l'adresse identique (« ABA ») ne peut pas être exclue par le seul couple pointeur/génération. Ne pas promettre la détection des `Poke` arbitraires. La bibliothèque P0b validée (82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) et la R84 `LAST_GOOD` sont inchangées.

## M19 P0c — staging Chip natif privé : Gate A MC68020 PASS (16/11/2026)

**Suite source-only de P0b** : [émetteur natif MC68020](../tools/m19_p0c_chip_stage_emit.py) (1 304 octets) et [banc Unicorn CPU020](../tools/test_m19_p0c_chip_stage_native.py) : **64 cas PASS** sur les allocations `AllocVec(MEMF_CHIP|MEMF_PUBLIC)`, `TypeOfMem`, `CopyMem`, remplacement atomique, `WaitBlit` avant `FreeVec`, garde CPU, registres/pile et identités périmées. [CI Gate A privée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021013) et [rapport de détail](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md). **Exec/graphics sont MOCKÉS : pas encore de véritable allocation Chip WinUAE ni de commande AP20 P0c.** Ne pas annoncer un Bob affichable. Le seul binaire installable reste P0b (82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) et les résultats Gate B Runtime / Gate C Compiler P0b demeurent valides. `LAST_GOOD` R84 n'a pas été promue.

**Prochaine intégration bloquante :** wrapper validant tout AGBO + banque AMOS, véritable table native des contextes Chip et invalidation, puis dessin Blitter des Bobs masqués à dimensions variables (sans `Swap` implicite). Le test unique `tests/current/M19_P0B_MC68020_MASK_BANK.asc` et les archives restent intacts.

## M19 P0b — Gates A, B Runtime et C validées (16/11/2026)

**État courant de main :** bibliothèque unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), 82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, 82 commandes / 92 entrées AP20. **Gate A MC68020 PASS** (116 scénarios commandes + 104 noyau), **Gate B Runtime WinUAE PASS** (`PRG_STATE 1`), **Gate C véritable AMOS Compiler PASS** (`PRG_STATE -1`), suivant les deux journaux fournis le 16/11. [Rapport et empreintes de l'ABK](M19_P0B_GATES_BC_2026-11-16.md). Interpréteur strict (`PRG_STATE 0`) et matériel physique NON TESTÉS. Ne pas confondre les anciennes mentions « NON TESTÉS » ci-dessous avec ce résultat plus récent.

**Suite du chantier :** préparer une représentation *privée* des images AGBO en vraie Chip RAM, vérifier les plages DMA entières et la durée de vie de l'allocation, puis seulement développer le dessin Blitter et les objets persistants. Le code natif actuel `Aga Bob Bank` gère sélection/métadonnées : il ne prépare pas encore de Chip DMA. Le format AGBO v1, les quatre commandes P0a/P0b validées et R84 `LAST_GOOD` sont conservés sans modification/promotion. Le test M19 P0b reste l'unique ASC actif.

## Historique M19 P0b — livraison initiale Gate A (avant Gates B/C)

**Livraison active sur `main` :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) (**82 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, 82 commandes / 92 entrées AP20) avec [ASC unique `tests/current/M19_P0B_MC68020_MASK_BANK.asc`](../tests/current/M19_P0B_MC68020_MASK_BANK.asc) et [notice](../tests/current/README.md). **Deux nouvelles instructions :** `Make AGA Bob Mask I,C` et `No AGA Bob Mask I` ; index transparent explicite (0 peut être opaque), masque 1 bit indépendant, préservation des autres images, transaction atomique. [CPU Gate A MC68020 PASS — 116 scénarios pour Make/No + 104 noyau](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43758224492), source candidate reconstruite/validée en CI [43758332071](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43758332071). **Runtime P0a : PASS sur journal utilisateur ; Runtime P0b et vrai AMOS Compiler P0b : NON TESTÉS.** WinUAE fonctionnel **68030/JIT ON** ; 68020/JIT OFF uniquement pour benchmark. Aucun IFF/ABK initial requis : génération par le test AMOS. `LAST_GOOD` R84 et archives inchangées, **aucune promotion**. Les sections P0a ci-dessous sont historiques.


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
