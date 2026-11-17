# Architecture technique — extension AMOS Professional 365 AGA

## M19 P0j-b3 — résolveur Chip indépendant de la sélection

L'entrée privée `explicit_image_resolve_entry` reçoit banque D3, image D0, sortie 36 octets A1, A5 propriétaire. La vérification du contexte Chip de P0j-b1 précède un branchement vers le **validateur de répertoire/masques/offsets P0d original** à une étiquette zéro octet. Le source P0d historique n'a pas changé de bytes, et aucune lecture ni écriture du shadow sélectionné n'intervient dans ce nouveau parcours.

**Gate A MC68020 PASS — 52 contrôles**, [CI 44174319362](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44174319362), deux implantations AP20 V2, masques d'une banque 10 préparés en Chip tandis que 11 reste sélectionnée, descripteurs pixel et masque vérifiés en mémoire et refus des sources périmées. Source BOBS **19 338 octets** SHA256 `ac4252e15ec04467d6789869f0f247c49249c5799276bfc07099811529d51437`, AP20 en mémoire **99 832 octets** SHA256 `90b5d69743bb93c5de9f97039e802e9bedd6866302e7b655efdde4c4a2f5e585`, 85 commandes / 178 entrées / 4 groupes, PC16 max 854.

**Reste P0j-b4** : mettre le peintre P0d Safe/WaitBlit sur cette nouvelle voie et parcourir les 64 objets sans shadow temporaire. Aucun changement Lib/ASC/R84 ni Gate B/C/D pour b3. [Rapport](M19_P0J_EXPLICIT_IMAGE_RESOLVE_GATE_A_2026-11-17.md).


## M19 P0j-b2 — staging Chip explicitement indexé par banque (17/11/2026)

Les entrées privées `explicit_checked_stage_entry` et `explicit_registry_prepare_entry` prennent D3 = banque AGBO, A5 = propriétaire et A4 = GfxBase, réutilisent **les octets historiques du validateur P0c et la publication atomique du registre**, sans consulter `bank_active_state`. Deux labels de raccord zéro octet ont été insérés dans les emitters P0c sans modifier leur binaire. Le fast-path s'appuie sur P0j-b1 pour **réutiliser un contexte Chip valide sans CopyMem ni AllocVec**.

**Gate A MC68020 PASS (46 vérifications)**, [CI 44172967134](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44172967134), deux implantations AP20 V2, banques 10/11 avec 11 toujours sélectionnée, intégrité des pixels Chip et aucune écriture du shadow. BOBS source **19 208 octets** SHA256 `1e2f5102e384e717326b3038ee3efda0ed331c2cd644e1e4d7a643e280db26ff`, candidate source-only AP20 **99 672 octets** SHA256 `8e1ef5daccde882aa78adb93c13108ee0d085063540920cbecfa80b4dddaad8d`, 85 commandes / 178 entrées / 4 îlots, PC16 max 854.

**P0d résolveur d'image/peintre toujours lié au shadow** : P0j-b2 ne rend pas encore le `Draw` complet réentrant, n'est pas installé et ne vaut pas Gates B/C/D. `dist/AMOSPro_AGA.Lib`, ASC actif, archives et R84 protégés. [Rapport P0j-b2](M19_P0J_EXPLICIT_BANK_STAGE_GATE_A_2026-11-17.md).


## M19 P0j-b1 — lookup Chip source-only explicitement indexé par banque

L'entrée privée `explicit_bank_lookup_entry` accepte D3 = banque AGBO, A1 = sortie 28 octets, A5 = owner AMOS. Elle retrouve le P0c registry node de **cette banque**, compare le pointeur `Bnk.GetAdr` et la génération de l'AGBO avec le contexte Chip, et contrôle MEMF_CHIP avant de publier la sortie. Aucune lecture/écriture de `bank_active_state` dans cette entrée, et hook de test de non-écriture. **Gate A MC68020 PASS (68 contrôles)**, [CI M19 44170930154](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44170930154), avec services système simulés et deux implantations AP20 V2. Code BOBS source-only **18 802 octets**, SHA256 `6f8d3d3edc887e707288d49981019c58b640b7a1f20b2b235bf73fafaebca7cf` ; image AP20 en mémoire **99 280 octets**, SHA256 `757025bbcf846694d8ecc0377a28fa08344d9b82964501dfdc4a7f0c4b6c171e`, 85 commandes / 178 entrées / 4 îlots. Gates B/C/D P0j-b1 non exécutées.

**Le staging P0c et le résolveur P0d utilisent encore le shadow sélectionné** : b1 ne résout que la lecture du contexte déjà préparé. Aucun Draw public ni changement de Lib, ASC ou `LAST_GOOD`. [Rapport](M19_P0J_EXPLICIT_BANK_LOOKUP_GATE_A_2026-11-17.md).


## M19 P0j-a — prévalidation native de toute la frame avant Blitter (17/11/2026)

La source-only candidate P0j-a ajoute un passage pré-DMA sur les **64 Bobs** après P0h et avant le P0i. Chaque objet actif utilise l'identité P0g et le `Bnk.GetAdr` de sa propre banque, recherche son image dans le répertoire AGBO et valide profondeur, géométrie, stride, longueurs et masques utilisés. **Gate A MC68020 PASS (68 vérifications)**, [CI M19 44167065047](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44167065047), avec services graphiques simulés. Les corruptions de l'image du 64e Bob refusent la frame avant le premier Blit. Candidate source-only **98 652 octets** SHA256 `4d43956a5dfbc1ae9cb1baf7058f48e6748f8bf80ef948fcc6b0a1872960a4ab`, BOBS source natif **18 176 octets** SHA256 `a91a0b99a05811a7f333738e1327b90a90dfe1aa947ec712d4290f568b88f618`. API 85 commandes / 178 AP20 / quatre îlots inchangés.

**Limites** : le routage P0i effectue toujours une projection temporaire non réentrante de `bank_active_state`. Le staging Chip P0c vérifie intégralement les banques lors de la préparation après le précontrôle, et les échecs asynchrones ou la mutation d'une banque entre les passes ne sont pas atomiques. Aucun `Aga Bob Draw` public ; la Lib `dist/AMOSPro_AGA.Lib`, le seul ASC et `LAST_GOOD` restent identiques. [Rapport P0j-a](M19_P0J_IMAGE_PREFLIGHT_GATE_A_2026-11-17.md).


## M19 P0i — chaîne native multi-banques vers le Blitter (17/11/2026)

**Gate A MC68020 PASS** — [CI M19 44163799991](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44163799991), **76 contrôles**, deux placements natifs AP20 V2 simulés, jusqu'à **64 Bobs réellement peints** depuis deux banques d'origine. L'entrée privée `routed_paint_all_entry` effectue un précontrôle P0h des 64 slots puis utilise la lecture P0g, le cache Chip P0c, la fonction Safe/WaitBlit P0d et l'identité P0f ; ordre 1..64, pas de Swap. Le front reste intact, le rendu Blitter est pixel-exact. Chaque banque reste indépendante dans le registre des allocations Chip.

La bibliothèque expérimentale **en mémoire seulement** : **97 820 octets**, SHA256 `004a04f9819fc2df9498ec8887e3de8a6533a7f620f04743c1fa1ae6ee872fa4`, 85 commandes, 178 sections AP20, quatre îlots ; nouveau source BOBS 17 330 octets SHA256 `e9d3d37401237574fa7b8e9a55817ae6d62673db68bb6207dc8a423a5a4364ea`. Bibliothèque installable inchangée, 96 908 octets ; `LAST_GOOD` R84 protégée.

**Limites avant exposition publique :** l'implémentation projette temporairement l'identité de la banque source dans `bank_active_state`, avant restauration systématique ; **non réentrante**. Un Bob manquant découvert après des peintures précédentes peut modifier partiellement le back buffer, même si aucun Swap n'est fait et si la fonction retourne 0. Éliminer la projection et valider l'intégralité des images en amont du DMA. Gates B/C/D non réalisées pour P0i. [Rapport détaillé](M19_P0I_MULTIBANK_DRAW_GATE_A_2026-11-17.md).


## AP20 V2 — retour à l'API fonctionnelle après preuve de cinq groupes (17/11/2026)

La bibliothèque installable unique est **l'image quatre unités source-reproductible** (96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`), avec 85 commandes et 178 sections AP20. Le banc à cinq unités, avec deux commandes temporaires et une table de 40 Kio, a **PASS Gate A/B/C** (Runtime et vrai Compiler) ; voir [le rapport de preuve](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md). Sa cinquième unité ne contenait aucun code de production : elle a donc été retirée du binaire actif plutôt que laissée comme unité inerte.

La capacité de croissance du dispatch V2 est **démontrée dans l'historique**, pas perdue : l'émetteur et le builder déterministes restent conservés dans les sources pour audit. Le prochain cinquième groupe **utile** exigera de nouveaux tests Gate A/B/C. `LAST_GOOD` et archives protégés.


## AP20 V2 — croissance append-only à cinq unités, Gate A (17/11/2026)

La [cinquième unité de diagnostic](M19_AP20_V2_FIFTH_UNIT_GATE_A_2026-11-17.md) **ajoute trois sections AP20 à la fin** de la candidate quatre îlots : deux stubs `Rbsr` (indices **178, 179**) et une unité V2 à l'indice **180**. Les sections **0…177** (dont les unités natives **142, 153, 156, 177**) demeurent **strictement identiques**, aux mêmes décalages dans le code AP20 concaténé ; les anciennes entrées publiques conservent leurs indices et tokens. Le bloc 180 fait **41 060 octets**, comprend un véritable tableau privé de 40 Kio et deux fonctions `D3/D2` ; la seconde est à l'offset natif non signé **41 012 (`$A034`)**, tout en gardant un `Rbsr` local de **6 octets**. Portée PC16 max de l'ensemble : **854 octets**, identique à quatre unités.

La candidate source-only **138 044 octets** / SHA256 `967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1` passe **Gate A réelle MC68020**, avec relocation interpréteur et Compiler **modélisées** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44135445819)). **Les vraies Gates B/C de cette cinquième unité et la Gate D sont NON TESTÉES.** Les Gates B/C précédentes concernent **quatre unités seulement**. Le binaire installé `dist/AMOSPro_AGA.Lib` (96 908 octets) et le test actif restent inchangés ; `LAST_GOOD` R84 protégée. Ne pas interpréter « offsets du code conservés » comme adresses absolues de relocation identiques : l'extension de la table de tokens déplace les offsets dans le HUNK.

## M19 — AP20 V2 par îlots : preuve Compiler réel (17/11/2026)

**Gates A/B/C PASS pour le banc `M19_AP20_ISLANDS_01.asc`.** La **Gate C** est documentée par `PRG_STATE -1`, `RESULT 1` / `ERR 0` **et une capture d'écran provenant explicitement de l'exécutable compilé**, selon l'auteur ; Gate B par `PRG_STATE 1` et son journal. [Preuves et limites](M19_AP20_V2_GATES_BC_2026-11-17.md). Le Compiler V2 accepte et exécute ainsi le chemin de dispatch AP20 entrelacé emprunté par ce banc, sans prouver l'ensemble des exports ni une cinquième unité native.

Le binaire et le test demeurent inchangés : `dist/AMOSPro_AGA.Lib`, 96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56` ; `tests/current/M19_AP20_ISLANDS_01.asc` seul actif. **Gate D, objets persistants et callbacks `End` non testés ; R84 `LAST_GOOD` protégée.** Le checkpoint « Gates B/C NON TESTÉES » plus bas est historique.

## M19 AP20 V2 — îlots de dispatch installés pour Gates B/C (17/11/2026)

**Candidate de test autorisée** dans la seule `dist/AMOSPro_AGA.Lib` : **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`. [Remappeur](../tools/ap20_v2_island_dispatch.py) + [builder P0f](../tools/build_m19_ap20_islands_in_memory.py). Chaque unité native V2 est inchangée en octets, les stubs AP20 sont regroupés à proximité et le tableau des tokens est remappé ; les marqueurs `GetP` précèdent les nouveaux stubs. **PC16 maximal : 854 octets** (P0f originel 32 576). 85 commandes, 178 entrées AP20, quatre groupes natifs. Gate A CPU020 et CI PASS (lien dans [rapport](M19_AP20_V2_DISPATCH_ISLANDS_2026-11-16.md)). **L'entrelacement stubs/groupes doit encore être validé par l'AMOS Compiler V2 réel (Gate C NON TESTÉE), comme la Gate B Runtime.** Test actif unique `tests/current/M19_AP20_ISLANDS_01.asc`. P0d reste reproductible à partir de son builder et de l'historique ; R84 `LAST_GOOD` protégée. Les sections P0d suivantes sont des checkpoints historiques, pas l'état actif.

## M19 P0d — bibliothèque de test active : Bob Blit AP20/Compiler V2 (16/11/2026)

La bascule canonique autorisée P0c → P0d fournit **`dist/AMOSPro_AGA.Lib` (91 300 octets ; SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`)**, 83 commandes/93 entrées V2. Le constructeur [`build_m19_p0d_bob_blit_in_memory.py`](../tools/build_m19_p0d_bob_blit_in_memory.py) repart **uniquement des sources figées et vérifiées P0b/P0c** ; il conserve octet pour octet les unités natives AGA/C2P/IFF, ajoute le stub `Aga Bob Blit(I,X,Y)` et les sources MC68020 du pont AGBO/Chip/Safe/Blitter au groupe BOBS V2. Le décalage RBSR maximal **32 196** exige une future organisation en groupes : ne plus agrandir le bloc sans preuve de portée PC16.

**Gate A CPU020 PASS**, OS/graphics/DMA simulés ; **Gates B Runtime et C Compiler réels en attente**, Gate D physique non testée. Programme actif `tests/current/M19_P0D_BOB_BLIT_01.asc`; [protocole](../tests/current/README.md). `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 protégée. Les sections antérieures mentionnant P0c comme candidate active restent des historiques techniques.


## M19 P0c — CANDIDATE ACTIVE pour Gates B/C (autorisation du 16/11/2026)

**Bascule autorisée sur `main`** : binaire unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; **82 commandes / 92 entrées AP20**, source [builder P0c](../tools/build_m19_p0c_screen_close_in_memory.py) dérivée du P0b figé. **Seul ASC actif** : [`tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`](../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc) ; son design reste inchangé. Gate A native MC68020 PASS ; Gates B Runtime WinUAE et C vrai AMOS Compiler **NON TESTÉES**, Gate D NON TESTÉE. CPU 68030/JIT ON pour essais fonctionnels. **Aucune promotion `LAST_GOOD`** (R84 SHA inchangé), ni publication/ZIP/artefact CI. Le test actif P0b quitte `tests/current/` et reste accessible par Git, sans archivage forcé.

**Actions :** installer la Lib canonique dans le slot AGA d'AMOS, redémarrer, importer l'ASC par `Project → Merge ASCII`, exécuter Runtime puis Compiler et recueillir deux journaux distincts. [Protocole complet](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md). **Les sections P0c/P0b qui suivent sont des checkpoints historiques antérieurs à cette bascule**, et ne désignent plus la candidate ou l'ASC actif.


## M19 P0c — liaison AP20 V2 BOBS → AGA Close et End privé (16/11/2026)

**Distribution (correctif du 16/11/2026) :** les exécutables expérimentaux restent reconstruits **en mémoire** pour la Gate A, sans publier de `.Lib` ou ZIP en artefact CI. Les Gates B/C P0c ne peuvent utiliser que le binaire canonique `dist/AMOSPro_AGA.Lib` et l'unique `tests/current/*.asc` après bascule autorisée ; P0b et `LAST_GOOD` sont actuellement préservés. [Préparation](M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md).

Le [builder in-memory P0c](../tools/build_m19_p0c_screen_close_in_memory.py) reconstitue la candidate depuis la base source P0b SHA `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, contrôle tout le layout AP20 V2, puis **ne modifie que** le stub public n°8 `Aga Screen Close` et ajoute le code MC68020 du groupe BOBS n°90. Le groupe AGA n°91 est préservé **octet pour octet**, sans patch du désassemblage audit-only. L'ancienne routine Close est localisée par `A5+0x1C8` → AGA State (native offset `0x1C2`) + `0x638` = `0x7FA`. Le constructeur vérifie signatures et offsets avant d'émettre ; l'appel dynamique `JSR` reste valide entre deux unités AP20 copiées séparément. Le registre Chip se vide et attend le Blitter **avant** l'ancien Close. Le prototype `End` privé préserve les deux callbacks AMOS `A5+0x1CC`/`A5+0x1D0` : armement explicite, nettoyage puis rétablissement du callback AGA original à `State-0x168`.

**Gate A CPU020 PASS :** [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925480841), 38 vrais chemins Close, 54 callback End privés, 116 tests P0b et tests privés P0c inchangés. **AP20 expérimental : 87 020 octets, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 82 commandes, 92 entrées** ; l'artefact CI est **hors `dist/`** et n'est pas la Lib installable officielle. Le code réel Init/Close/End est exercé avec **services simulés**, pas WinUAE ni AMOS Compiler. **Gates B/C en attente**, tout comme l'exposition publique de staging/armement End et le dessin des Bobs. [Contrat de test détaillé](M19_P0C_SCREEN_CLOSE_BRIDGE_GATE_A_2026-11-16.md).

## M19 P0c — point de pré-fermeture AGA, sans hook public (16/11/2026)

L'entrée native privée [`screen_preclose_entry`](../tools/m19_p0c_screen_preclose_emit.py), MC68020, lit l'état AGA via `A5+0x1C8`, contrôle `State+8` (GfxBase), puis appelle le cleanup du registre BOBS **tant que GfxBase n'a pas été fermé**. Elle retourne un statut **1/0** ; l'échec doit faire interrompre le futur appel public de fermeture. Le nouveau garde préserve intégralement les préfixes P0b/P0c et a passé **42 scénarios Gate A CPU020 simulés** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43920983278)) ; l'ensemble du code source natif BOBS privé fait **11 294 octets**.

L'audit du vrai AP20 P0b identifie `Aga Screen Close` **token 8 → groupe natif AGA 91, offset 2008** ; BOBS est le groupe 90. L'ancien groupe AGA est conservé tel quel. La seule `src/R88/...AGA_NATIVE.s` disponible est une **restitution partielle pour audit**, pas une source vérifiée de production. **Le trampoline inter-groupe n'est pas construit, le hook `Screen Close`/AMOS End n'est pas installé**, et les tests modélisent l'ordre destructif sans exécuter l'ancienne commande. Un `BSR.W` direct depuis BOBS n'est pas une liaison V2 démontrée (AGA R88 = 56 580 octets). Ne pas traiter Gate A privée comme Gate B/C ou valider la fermeture utilisateur à ce stade.

## M19 P0c — registre propriétaire de contexts Chip (16/11/2026)

Le [registre natif privé](../tools/m19_p0c_bank_registry_emit.py) prolonge le groupe BOBS source sans modifier le préfixe P0b/P0c existant. Un état PC relatif de **8 octets** contient l'identité de programme AMOS (A5) et la tête d'une liste de nœuds alloués par Exec (**32 octets chacun**, numéro de banque + contexte Chip de 20 octets). L'entrée `registry_prepare_entry` ajoute un nœud seulement après validation complète de la banque AGBO et allocation Chip réussie ; `registry_lookup_entry` refuse les références obsolètes ; `registry_free_entry` libère une banque ; `registry_close_entry` vide toute la liste avec synchronisation Blitter, y compris si les banques AMOS ont été supprimées. Parcours bornés à **256 entrées**, pas de banque AMOS auxiliaire.

**Gate A privée : 64 scénarios MC68020 PASS**, unité groupée 11 094 octets, CI [43917996936](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43917996936). Le cleanup est **une entrée privée testée, pas un hook réel dans `Aga Screen Close`** ; les allocations système sont simulées. L'étape suivante consiste à prouver le raccordement Open/Close et le cycle de vie, puis les objets Bob et le rendu masqué. Aucune modification de `dist/AMOSPro_AGA.Lib` ni de `LAST_GOOD`.

## M19 P0c — validation native du conteneur AGBO (16/11/2026)

Le [wrapper privé](../tools/m19_p0c_checked_bank_stage_emit.py) assemble le **préfixe natif P0b strictement identique** avec un validateur AGBO complet et le [helper Chip privé](../tools/m19_p0c_chip_stage_emit.py). Il recontrôle banque sélectionnée, `Bnk.GetAdr`, tête de liste AMOS, taille et nom du DATA bank, répertoire strict de toutes les images, géométries, offsets, masques séparés et padding planaire avant `AllocVec(MEMF_CHIP)`. **120 scénarios Gate A CPU020 simulés PASS**, incluant deux allocations propres à deux banques et invalidation sur changement d'adresse/génération, source native totale 10 044 octets (y compris P0b). [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43916465599) et [rapport](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md).

Le contexte de 20 octets est **encore fourni par le caller privé** : pas de table par banque dans l'état global de l'extension, pas de token public, pas de rendu Blitter. La détection de réutilisation « ABA » d'une même adresse/génération après Erase/Load nécessite une discipline explicite de resélection et un futur état propriétaire. **Aucune modification du binaire P0b ni de LAST_GOOD.**

## M19 P0c — futur staging Chip (source-only, 16/11/2026)

Un noyau [MC68020 privé](../tools/m19_p0c_chip_stage_emit.py) de **1 304 octets** a passé **64 tests Gate A CPU020 sous Unicorn** ([résultats](M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md)). Il alloue une zone propriétaire `MEMF_CHIP|MEMF_PUBLIC`, vérifie les bornes via `TypeOfMem`, copie les plans et masques et attend `WaitBlit` avant `FreeVec`. Les appels Exec/graphics sont **mockés** : il n'est pas lié à AP20 ni à une table de contextes persistants dans la bibliothèque active. La vérification complète du conteneur AGBO et les appels Blitter de dessin restent à intégrer et tester. **Les octets P0b installables, les résultats Gates B/C et R84 `LAST_GOOD` ne changent pas.**

## État M19 P0b vérifié le 16/11/2026

Le binaire installable actif est **M19 P0b**, 82 376 octets (SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`), 82 commandes / 92 entrées AP20. Gates A, B Runtime et C Compiler **PASS** pour le scénario de capture/masques multi-images; voir [les preuves](M19_P0B_GATES_BC_2026-11-16.md). **La préparation en vraie Chip RAM pour dessin DMA n'est toujours pas intégrée.** Le repère R88 ci-dessous est historique, non le binaire courant. R84 `LAST_GOOD` reste distinct et non promu.


## Repère actif de l'architecture (audit du 15/11/2026)

Le suivi de version de ce document contient plusieurs états historiques R46, R59 et R84. **Ne pas les considérer comme la version actuellement installable.** Au checkpoint documentaire R88, la candidate non promue était `dist/AMOSPro_AGA.Lib` **R88 v0.13.33** (75 040 octets, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`, **78 commandes / 88 entrées AP20, quatre unités natives V2**). **R84 v0.13.29 reste `LAST_GOOD`** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Depuis ce checkpoint, des commits plus récents peuvent avoir été ajoutés : vérifier `main` HEAD, `dist/AMOSPro_AGA.Lib` et son builder avant tout nouveau code. Gate A R88 : 130 cas PASS ; le premier essai WinUAE P2.8 a échoué `ERR 12` avec ABK Fast ; la révision Chip restait à retester ; Gate C R88 non démontrée à cette date. Les nouvelles commandes Bob multi-images restent des **contrats de conception**, pas des capacités automatiquement présentes dans R88.

**Structures partagées : provenance historique, pas d'offsets garantis sur toute version.** Les anciennes règles (sections 6–7 de l'[archive intégrale](EXTENSION_SOURCE_RULES_HISTORIQUE_2026-11-15.md), blob `d450f41475d32f838186c23f5e7e6eb13a8458ce`) décrivent les positions suivantes, à **recontrôler dans le code natif et le builder cible avant réutilisation** :

| Ancienne structure | Offsets documentés (octets) | Contrat |
|---|---|---|
| `State` | `+0 Screen*`, `+4 IntuitionBase`, `+8 GfxBase`, `+12 width`, `+16 height`, `+20 colors`, `+24 ModeID`, `+28 depth`, `+32 DBState*`, `+36 Window*` | Chaque accès doit correspondre au layout du binaire exact |
| `DBState` | `+0 ScreenBuffer original`, `+4 alternatif`, `+8 front`, `+12 SafePort`, `+16 DispPort`, `+20 réservé` | Notifications en vol et cycle de vie Safe/Disp à conserver |

Les offsets système AmigaOS/NDK (`BitMap`, `ScreenBuffer`, `ViewPort`, `RasInfo`) doivent également être vérifiés sur leurs définitions officielles et sur le mode de compilation choisi. Ne pas créer un état parallèle pour les Bobs AGA. Le [contrat permanent](../EXTENSION_SOURCE_RULES.md) est désormais la référence opérationnelle.

---

## Historique — R84 v0.13.29 `LAST_GOOD` PROMUE (14/11/2026)

**À ce checkpoint R84, le binaire actif et `LAST_GOOD` étaient identiques** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, 76 commandes, 85 entrées AP20, 3 groupes natifs (C2P 5 558, IFF 2 508, AGA/AGAPIC 56 580). Le builder `tools/build_aga_r84_agapic.py` reconstruit R84 depuis un builder R83 historique indépendant du chemin mobile `LAST_GOOD`. La R83 (SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, 64 188 octets) reste reconstructible et visible dans l'historique Git.

**Gates A CPU/CI et C AMOS Compiler PASS** ; compilation WinUAE 68030 avec une banque, 4/8 plans, tous indicateurs fonctionnels à 1, `ERR 0`, Chip 0, Fast −11 920 octets (4 ABK conservés dans RAM:). **Gate B Runtime corrigée non attestée séparément** ; Gate D physique et `PRG_STATE 0` strict non testés. Promotion explicitement autorisée sans imposer un nouveau test. Aucun tag ou publication.

[Promotion](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Compiler](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md) · [Roadmap](ROADMAP.md).

---

## Historique — R84 v0.13.29 candidate avant promotion (14/11/2026)

**R84 active sur `main` :** `dist/AMOSPro_AGA.Lib`, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **76 commandes, 85 entrées AP20** ; 3 unités natives C2P **5 558**, IFF **2 508**, AGA/AGAPIC **56 580** octets. Nouveau code natif : Info **1 088** et capture v1/v2 **2 510** octets, sans padding ; dispatcher 68020 et toutes les signatures héritées de R83 validés. **Marge AGA 8 954 octets** jusqu'à 65 534. Plus grand écart du chargeur BSR.W : **9 000 octets**.

**Gate A CPU/CI R84 PASS** : [CI dédiée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43644680232) : 44 tests Info et 47 tests de capture sous émulation MC68020, v1/v2, profondeurs 1/4/8, opaque/masqué, RGB24, ModeID, flux RLE, allocations et conservation des banques existantes. **Gates B Runtime WinUAE et C Compiler NON TESTÉES** sur le binaire R84 ; `tests/current/AGAPIC_R84_V1_V2_01.asc` est le seul test AMOS actif. La **R83 `LAST_GOOD` SHA256 01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb est protégée, inchangée et A/B/C PASS**. Pas de promotion R84, pas de tag ni publication.

[Contrat R84](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Gate A](AGAPIC_R84_GATE_A_2026-11-14.md) · [Roadmap](ROADMAP.md).

---

## Historique — M17/R59 compacte `LAST_GOOD` PROMUE, Gates A/B/C PASS (12/11/2026)

**Bibliothèque officielle et `LAST_GOOD` identiques :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), R59 0.13.4, 32 984 octets, SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`. **53 commandes, 60 entrées AP20, 59 routines natives R57 strictement identiques**. Le dispatcher V2 de 34 octets traite des offsets non signés avec `MOVEQ #0,D0` et `ADDA.L`. Monolithe **30 782 octets** (34 dispatcher + 30 748 natifs). Les stubs AP20 et le code natif de R57 sont identiques ; seule l'enveloppe de 32 à 34 octets et le titre changent. `Aga Probe` utilise son chemin d'origine, **sans routine témoin à 40 Ko**.

**Gate A R59 CPU/CI, B interprétée et C nouvel exécutable compilé sous WinUAE PASS**, deux captures utilisateur distinctes du 12/11/2026 (`RESULT 1`, `CLOSE RETURNED`, aucun Guru visible) ; **régression complète [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43312486348)** sur `5f29d78`, accord explicite de promotion, et **Gate D physique non testée**. Les deux fichiers `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` ont le même SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`. R58 a validé séparément le témoin **à l'offset 40 000** (padding 9 252 octets désormais retiré) ; son [test reste archivé](../tests/passed/M17_R58_COMPILER_BRIDGE_01.asc). **[Test R59 archivé](../tests/passed/M17_R59_COMPACT_V2_01.asc)** ; aucun ASC actif. Ancienne `LAST_GOOD` R57 v0.13.2 : [commit historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/5f29d78e65b666f7260f5a32e28bd4e8bcf59a4a/dist/AMOSPro_AGA_LAST_GOOD.Lib), SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`. [Rapport R59](M17_R59_COMPACT_V2.md).

## Historique — M16/R46 v0.12.1, ancien checkpoint Gates A/B (12/11/2026)

**AMOS interprété / WinUAE : PASS sur captures utilisateur** du test `M16-R46-IMAGE-DRAW-01`. Images opaque, masquée et décalée visibles, quatre côtés clippés : `OPAQUE 1 MASK 1 SHIFT 1`, `CLIP 1 1 1 1`, `BAD 0 0 0 OUT 1`, `SWAP 1 BACKSAFE 1`, `CHIP BEFORE/END 1801928 1801928`, `NATIVE LEN 1852 WANT 1852`, `NATIVE NO 10 FLAGS 0`, `NATIVE NAME AGAPIC`, `HEAD AGAPIC V 1`, `STREAM 196 TOTAL 1836`, **`ERRORS 0 RESULT 1`**, **`CLOSE RETURNED`** (ligne 148). La chaîne graphique `R45 - CPU AGAPIC IMAGE` est un ancien libellé dans le test R46, conservé sans retouche.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib`, **29 288 octets**, SHA256 `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580`, même blob Git ; **50 commandes AP20 / 56 segments** ; 258 scénarios natifs CPU 68000 et source strict Gate A PASS ([CI R46](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43221899949)). Test WinUAE exact archivé en `tests/passed/M16_R46_IMAGE_DRAW_01.asc` (**4 240 octets**, Git blob `83eff57323b1cacd0ea58a131ef1ebcec079eceb`) ; aucun ASC actif dans `tests/current/`. Archive R44 validée et archive R45 échouée immuables. **Gate C Compiler non validée** (CI expérimentale distincte en échec), **Gate D Amiga AGA physique non testée**. Emplacement Fast RAM réel et performances 68000 matériel non mesurés. **Branche `main` uniquement.**


## M15 + M15bis — R44 v0.11.5 : CLÔTURE Gates A/B et LAST_GOOD (12/11/2026)

**M15 Plot/Draw/Box/Circle et M15bis Aga Mouse Cursor sont clôturés** après la CI Gate A (516 scénarios CPU 68000 R44) et les validations WinUAE utilisateur : test R44 (500 bascules, 0 erreur, CHIP DROP 0, RESULT 1, CLOSE RETURNED) puis démonstration globale `examples/m15_2d_cursor.asc` (« ça marche super »). Le retour global confirme le fonctionnement visuel, sans capture chiffrée fournie pour cette démo. **49 commandes AP20, 55 segments.**

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive versionnée R44, **27 460 octets**, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. Original `M15BIS_R44_MOUSE_CURSOR_01.asc` archivé octet pour octet en `tests/passed/` (blob Git `099f7125260c340dfbb4819f5770d1dbafd6789d`), `tests/current/` sans ASC actif. **R43** et les versions antérieures demeurent archivées et non modifiées. **Gates C Compiler / D AGA physique NON TESTÉES.**

**Rapport de clôture :** [M15_M15BIS_R44_CLOSURE.md](M15_M15BIS_R44_CLOSURE.md). **Étape suivante éventuelle : M16**, format d'images compressées en Fast RAM avec dessin CPU ; aucun code M16 engagé. **Uniquement `main`**, aucune branche créée. Les sections R43 et antérieures ci-dessous sont des archives historiques de leur époque.

## M15/R43 v0.11.4 — Aga Circle : Gates A CPU/CI et B AMOS/WinUAE PASS, LAST_GOOD (12/11/2026)

**R43 VALIDÉE par l'utilisateur (capture « parfait !!! ») :** `_OK=Aga Circle(CX,CY,Radius,Pen)` — cercle de contour d'un pixel par Bresenham midpoint 68000 en arithmétique 32 bits avec clipping sécurisé des huit octants, sans dessin hors écran ni bord inventé. Écran AGA privé, uniquement sur le back buffer après `Safe` non bloquant ; aucune allocation persistante, aucun swap/VBL implicite. **48 commandes AP20, 54 segments ; 436 scénarios CPU 68000 Gate A PASS et CI complète PASS** ([CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43204551950)).

**Gate B AMOS interprété/WinUAE PASS :** l'utilisateur confirme le rendu et la capture affiche `OPEN 1 DB 1 CLEAR 1`, `CIRCLES 1 1 1 1 DOT 1`, `CORNERS 1 1 1 1`, `CLIPPED 1 1 1 1`, `PEN0 1 OUTSIDE 0 0 0 0`, `WRAP 0 BADR 0 0`, `BADXY 0 0 BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`** et **`CLOSE RETURNED`**. [Test d'origine archivé sans modification](../tests/passed/M15_R43_CIRCLE_01.asc), Git blob `088158365a64accf0417fdda3fbba74e2e58ebf7` (**3 466 octets**) ; aucun fichier ASC dans `tests/current/`.

**Promotion obligatoire réalisée :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib`, **27 092 octets**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, à l'octet près. **R42** reste dans son archive versionnée intacte (25 896 octets, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`) ; toutes les versions précédentes conservées. **Gates C Compiler et D AGA physique NON TESTÉES.** M15 primitives de base (Plot/Draw/Box/Circle) terminé sur les Gates A/B. **Suite à discuter : M15bis, visibilité locale du pointeur souris AGA, avant M16 (images compressées Fast RAM)**. R39 fontes bitmap toujours reportée ; aucun nouveau contrat de commande validé pour M15bis/M16. Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## M15/R42 v0.11.3 — Aga Box : Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R42 VALIDÉE :** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**, **360 tests CPU 68000 + export source natif strict + CI PASS**, Gate B AMOS interprété/WinUAE **PASS confirmé par l'utilisateur** (« ça marche ! bravo »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BOXES 1 1 1 REV 1`, `CLIPPED 1 1 1 1`, `LINES 1 1 DOT 1`, `OUTSIDE 0 0 0 0`, `WRAP 0 BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **119** ; rendu validé. [Test original archivé sans retouche](../tests/passed/M15_R42_BOX_01.asc), Git blob `dbf5cefb215cc0ae1359d648ea34c855a92b2012` (**3 264 octets**). **`tests/current/` ne contient aucun ASC actif.**

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` **octet pour octet**, **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. L'archive R41 v0.11.2 (SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`), R40, R38 et les précédentes sont inchangées. Contour d'un pixel, coins inclusifs et inversables, clipping des **quatre côtés originaux** sans fausse bordure, sécurité du back buffer `Safe` et refus des paramètres invalides. **Gates C Compiler et D Amiga AGA physique NON TESTÉES.** Prochain chantier éventuel : M15/R43 `Aga Circle` (NON implémenté). R39 fontes bitmap reste reportée. **La proposition M16 de banque d'images compressées en Fast RAM reste une idée de roadmap, pas une fonction livrée.** Dépôt `anthea176/AMOSPro-AGA-Extension`, **`main` uniquement**.

## Historique de préparation avant validation R42

**M15/R42 v0.11.3 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (360 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**. Coins inclusifs normalisés, 1 px d'épaisseur, clipping indépendant des quatre côtés d'origine (jamais de bordure inventée), refus sécurisé des rectangles hors écran, validation des coordonnées signed16 et index `Pen`, BitMap physique et signal `Safe` non bloquant. [Test unique WinUAE](../tests/current/M15_R42_BOX_01.asc) à importer via **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` identiques (**25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R41 v0.11.2 validée** (24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`) ; archives R41 et antérieures inchangées. [CI CPU + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Gates C Compiler/D AGA physique non testées. Aucun test R42 archivé ou `LAST_GOOD` promu sans validation utilisateur. Travail uniquement sur `main` de `anthea176/AMOSPro-AGA-Extension`.

## M15/R41 v0.11.2 — Gates A CPU/CI et B WinUAE PASS, LAST_GOOD (12/11/2026)

**R41 `Aga Draw(X1,Y1,X2,Y2,Pen)` VALIDÉE** : 46 commandes AP20, **325 tests CPU 68000 + export assembleur strict + CI PASS**, puis test AMOS interprété/WinUAE confirmé par l'utilisateur (« rendu ok ! »). Capture : `OPEN 1 DB 1 CLEAR 1`, `BORDER 1 1 1 1`, `CLIPPED 1 1 1 1`, `STAR 8 ERR 0 CENTER 1`, `OUTSIDE 0 0 0 0`, `BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne **131**. [Test exact archivé](../tests/passed/M15_R41_DRAW_01.asc) (Git blob `aa7de64b37a2842db21bc7452c2fab4570413e9f`, 3 553 octets). `tests/current/` ne contient aucun ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` **octet pour octet**, **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. Archive R40 v0.11.1 préservée (SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), ainsi que R38 et les archives antérieures. Dessin strictement sur le back buffer AGA : tracé rapide `Move/Draw` uniquement si extrémités valides ; clipping logiciel avec contrôle **avant chaque pixel** hors limites. **Gates C AMOS Compiler et D Amiga AGA réel NON TESTÉES.** R39 fontes bitmap reportée ; R42 `Aga Box` et R43 `Aga Circle` non implémentées. Dépôt `anthea176/AMOSPro-AGA-Extension`, branche **`main` uniquement**.

## Historique (avant promotion R41)

**M15/R41 v0.11.2 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (325 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)`, **46 commandes AP20** ; tracé rapide pour lignes intégralement à l'écran et Bresenham avec vérification de chaque pixel avant `WritePixel` pour les segments qui dépassent. [Test unique WinUAE](../tests/current/M15_R41_DRAW_01.asc), import par **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib` à l'octet près (**24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R40 v0.11.1 validée** (23 840 octets, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`), archives R40/R38 et plus anciennes inchangées. [CI CPU 68000 + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457). Gates C Compiler/D Amiga réel non testées. Ne promouvoir R41 et n'archiver le test qu'après validation explicite de l'utilisateur. **Uniquement `main` du dépôt `anthea176/AMOSPro-AGA-Extension`.**

## M15/R40 v0.11.1 — Aga Plot : Gates A CPU/CI + B WinUAE PASS, LAST_GOOD (12/11/2026)

**R40 VALIDÉE sous AMOS interprété / WinUAE :** `_OK=Aga Plot(X,Y,Pen)`, **45 commandes AP20**. 221 scénarios CPU 68000 + export strict et [CI candidate](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43129055588) PASS. Confirmation utilisateur le 12/11/2026 (« ça marche nickel ») avec capture `OPEN 1 DB 1 CLEAR 1`, `PALETTE 1 1 1 1`, `CORNERS 1 1 1 1`, `CENTER 1 PEN0 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin ligne 99. [Test original archivé octet pour octet](../tests/passed/M15_R40_PLOT_01.asc) (Git blob `6ab9cf4a91cca9f8097ffba40a32e2b85b049c38`). `tests/current/` sans ASC actif.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib` à l'octet près (**23 840 octets**, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`). L'archive R38 v0.11.0 et toutes les versions antérieures restent inchangées. **Gate A CPU/CI PASS, Gate B WinUAE PASS, Gates C Compiler/D Amiga physique NON TESTÉES.** Protection intégrée : refus des coordonnées X/Y hors de `[0,Width-1]`/`[0,Height-1]` et des pen hors de `0..2^Depth-1` avant tout dessin, vérification des bitplanes et du back buffer `Safe`. `Aga Draw`, `Aga Box`, `Aga Circle` non implémentées ; les protections de `Plot` ne constituent pas un clipping général. R39 fontes bitmap 8x8 est reportée. Dépôt unique `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**.

**État actuel au 12/11/2026 :** R40 v0.11.1 `Aga Plot`, **45 commandes AP20**, Gates A CPU/CI et B WinUAE PASS ; `LAST_GOOD` = R40, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`. Gates C/D non testées. Voir [contrat R40](M15_PLOT_R40.md).

**Ce document décrit l'architecture actuelle et ses limites, pas la chronologie des prototypes.** La précédente compilation historique de notes R10/R12 reste intacte dans [`history/ARCHITECTURE_LEGACY_20261110.md`](history/ARCHITECTURE_LEGACY_20261110.md). Vérifier le code, les builders et le binaire avant tout changement.

**Historique M14/R37 :** `Aga Font Select(FontName$,YSize)` utilise `OpenDiskFont` et `SetFont`. R37 a passé Gates A/B et sa bibliothèque est figée dans `dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib` (22 328 octets) ; R38 est désormais une archive historique ; R40 est `LAST_GOOD`. [Contrat](M14_FONT_SELECT_R37.md).

**Version validée M14/R38 :** `Aga Font Bank Select(Start(bank),Length(bank))` (44e commande AP20) utilise une copie privée Chip RAM. Nettoyage par `StripFont`/`FreeVec` aux changements/reset/fermeture. **Gates A et B PASS**, R38 archivée 23 380 octets ; `LAST_GOOD` actuel = R40. **Stress WinUAE validé : 500 changements (Topaz AMCAF / Hwarf / Pix3M / Topaz AmigaOS), 500 `Aga Text`, 0 erreur, aucune baisse du total Chip libre (1 582 088 octets) ni du plus grand bloc (1 320 664 octets), `RESULT 1` et retour AMOS normal.** [Test archivé](../tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc). Ce protocole ne couvre pas tous les scénarios. [Contrat](M14_FONT_BANK_R38.md).

**Correction R38 après retour utilisateur (`BANK 0`, `BANK2 0`) :** accepteur DATA/WORK corrigé et prise en charge des tables supplémentaires des fontes proportionnelles Hwarf/Pix3M. **Allocation du rendu en Chip RAM obligatoire**, vérifiée par `AllocVec(MEMF_PUBLIC|MEMF_CHIP|MEMF_CLEAR)` : une banque source en Fast est copiée, jamais utilisée directement par `SetFont`. Gate A [60 groupes natifs et régressions PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43123200900), Gate B R38 confirmée par l'utilisateur le 12/11/2026 ; R38 est maintenant archivée ; R40 est `LAST_GOOD`.

## 1. Vue d'ensemble

`AMOS Professional 365` → appels extension `AP20 / HUNK` → état partagé extension → `Intuition` / `graphics.library` → écran AGA, bitplanes et buffers. La couche AGA est indépendante des écrans historiques gérés par AMOS ; **ne pas supposer** que les commandes natives AMOS dessinent automatiquement sur l'écran Intuition de l'extension.

L'objectif est une API de haut niveau sûre et réutilisable, pas la réécriture d'AMOS ni d'un moteur RPG.

## 2. Socle AMOS/AGA et extension M10

| Domaine | Principales commandes | Périmètre réellement connu |
|---|---|---|
| Chipset / écran | `Aga Detect`, `Aga Screen Open`, `Aga Screen Close`, `Aga Screen Pattern` | Gestion d'écran Intuition AGA ; modes selon capacité AmigaOS |
| Présentation | `Aga Double Buffer`, `Aga Swap`, `Aga Back Fill`, `Aga Wait Vbl` | Double buffering et attente TOF |
| IFF/ILBM | `Aga Pic Info`, `Aga Iff Load` | Métadonnées, chargement image/palette ; M5 clos sur modes testés |
| Palettes M13 | `Aga Palette Load/Set/Get/Save`, `Aga Palette Bank Init/Capture/Apply`, `Aga Fade To Bank`, `Aga Fade To Black` (R34 WinUAE-PASS), `Aga Fade To White` (R35 WinUAE-PASS), `Aga Palette Cycle` (R36 WinUAE-PASS) | RGB24 IFF et banques AGAPAL DATA/ABK ; R31 Capture et R32 Apply validées sous AMOS interprété/WinUAE sur leurs scénarios ; R33 Fade To Bank Gates A/B PASS et démo visuelle confirmée sous WinUAE ; R34 Fade To Black Gates A CPU (48 scénarios) et B AMOS/WinUAE PASS utilisateur, fondu visuel confirmé ; R35 Fade To White Gates A CPU/CI (50 scénarios) et B AMOS/WinUAE PASS utilisateur, fondu blanc visible confirmé ; R36 Color Cycling Gates A CPU/CI 106 scénarios et B AMOS/WinUAE PASS, effet visible confirmé ; autres fonctions non implémentées |
| Fontes M14/R37 (WinUAE-PASS) | `Aga Font Select(FontName$,YSize)`, `Aga Text` | Sélection et libération de fontes AmigaOS via diskfont/graphics.library sur le back buffer Intuition AGA ; Gates A/B PASS, banque AMCAF pas encore prise en charge. |
| Clavier | `Aga Key`, `Aga Wait Key` | Input Intuition, attention au focus et Ctrl+C |
| Blitter M6 | `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` | Back buffer ; R13/R14/R15 PASS AMOS interprété/WinUAE. |
| Souris M8/R23 (PASS WinUAE scénario) | `Aga Mouse Pressed/Released`, `Aga Key/Wait Key` | Dispatcher central IDCMP, FIFO RAWKEY 16, Gate A CPU/CI PASS 15 cas ; Gate B WinUAE PASS sur clics rapides, FIFO clavier et Ctrl+C. |
| Hotspots M9/R24 (PASS WinUAE sur scénario) | `Aga Hotspot Hit(px,py,x,y,w,h)` | Sans état, bornes finales exclusives ; CPU/CI 402 cas PASS et WinUAE PASS (ID 20 recouvrement, hors zone, retour AMOS) ; aucun registre de zones. |
| Collisions M10/R25 (PASS sur scénario WinUAE) | `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)` | AABB sans état, contact bord exclu ; **704 cas CPU/CI PASS, Gate B AMOS/WinUAE PASS** sur 409 images, `DRAWERR 0`, `RESULT 1` et retour AMOS correct. |
| Souris M8/R22 (PASS WinUAE sur scénario) | `Aga Mouse Pressed`, `Aga Mouse Released` | Masques 1/2/4, focus contrôlé, historique privé ; CPU/CI PASS (25 cas) et WinUAE PASS sur le test R22 archivé. |
| Souris M8/R21 (PASS WinUAE) | `Aga Mouse X/Y`, `Aga Mouse Buttons` | R21 0.8.5 : RMBTRAP supprimant la barre Intuition au clic droit ; **CPU/CI 11 cas et WinUAE PASS utilisateur** sur le test archivé. |
| Souris M8/R20 (historique) | `Aga Mouse Buttons` | 21 cas CPU PASS ; sous WinUAE boutons reconnus, mais barre Intuition persistante sur clic droit. |
| Souris M8/R19 | `Aga Mouse X`, `Aga Mouse Y` | **PASS CPU 76 cas et AMOS interprété/WinUAE** pour le test R19 archivé. |

**Historique R36 0.10.8 — dernière version validée WinUAE, désormais `LAST_GOOD` :** archive R36 et `dist/AMOSPro_AGA_LAST_GOOD.Lib` identiques à l'octet près, 21 836 octets, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`, 42 commandes AP20. `Aga Palette Cycle` a passé Gate A (106 scénarios CPU) et Gate B interprétée WinUAE (`RESULT 1`, `CLOSE RETURNED`). Les Gates C/D restent non testées. [Contrat R36](M13_PALETTE_CYCLE_R36.md).

**Historique R35 0.10.7 :** Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS ; archive R35 figée sous `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`, 41 commandes AP20. `Aga Fade To White(vbl)` effectue un fondu bloquant sur 1..255 VBL vers le blanc RGB24 exact (`0xFFFFFFFF` par composante RGB32) sur tous les pens logiques sans banque AGAPAL. Test [R35 archivé](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc) : `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `RESULT 1`, `CLOSE RETURNED`. Fondu visible confirmé par l'utilisateur le 11/11/2026 ; cadence/FPS non mesurés. [Contrat](M13_FADE_WHITE_R35.md). Gates C Compiler/D Amiga réel non testées.

**Historique R34 0.10.6 :** Gates A CPU/CI et B AMOS interprété/WinUAE PASS, archive R34 figée sous `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib` (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`, 40 commandes AP20). `Aga Fade To Black(vbl)` ramène tous les pens logiques RGB24 au noir exact en 1..255 VBL bloquantes, sans banque. Test [R34 archivé](../tests/passed/M13_R34_FADE_TO_BLACK_01.asc) (`FADE150 1 BLACK 0 0 0 0`, `RESULT 1`, `CLOSE RETURNED`, fin ligne 113) ; démonstration visuelle validée par l'utilisateur le 11/11/2026. Cadence/FPS non mesurés. [Contrat](M13_FADE_BLACK_R34.md). Gates C Compiler/D matériel réel non testées.

**Historique R33 0.10.5 :** Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS ; archive R33 figée (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, 39 commandes AP20). R33 Fade est bloquante sur 1..255 VBL et termine sur le RGB24 exact ; preuve fonctionnelle [test archivé](../tests/passed/M13_R33_AGAPAL_FADE_01.asc) (`RESULT 1`, `CLOSE RETURNED`, fin ligne 141). **Test fonctionnel archivé :** `Aga Swap` puis `Amos To Back` étaient appelés après les transitions trop brèves pour être bien vues. [Démo visuelle complémentaire](../examples/fade_to_bank_r33.asc) (150 VBL et dessin visible avant le fade), **confirmée fonctionnelle et visible par l'utilisateur sous WinUAE le 11/11/2026** ; cadence/FPS et durée réelle non mesurées. Gates C Compiler/D matériel non testées.

**Historique R32 0.10.4 :** Gates A CPU/CI (136 scénarios) et B fonctionnelle AMOS interprété/WinUAE PASS, test [R32 archivé](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc), archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib` préservée (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). R32 est conservée en archive historique et n'est plus `LAST_GOOD`. Gates Compiler et Amiga réel non testées.

## 3. ABI, état et ressources

- Extension AP20 : table des tokens/signatures et paramètres, retour entier en D3 (D2=0), dépilement correct des paramètres sur A3. **La source d'autorité technique demeure [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md).**
- L'écran/Window Intuition, le ViewPort, les BitMaps, les ScreenBuffers et les bibliothèques OS sont possédés par l'extension selon leur cycle de vie ; libérer dans l'ordre approprié, avec chemins d'échec sûrs.
- Pas de blocage `WaitPort` / `Exec Wait` infini ; les événements input sont traités de manière coopérative et les tests AMOS doivent pouvoir terminer.
- Les builders reproductibles et la validation CPU vérifient structure et ABI ; **ils ne remplacent pas un test runtime AMOS**.

## 4. Copper — M7 RGB4 validé pour le scénario WinUAE

Se référer **directement** à [M7_COPPER_DESIGN](M7_COPPER_DESIGN.md) et [M7_STATUS](M7_STATUS.md). R16 ajoute `Aga Copper Clear`, initialisation de la liste vide `CEND` sur le ViewPort du Screen Intuition (**PASS WinUAE**). R17 ajoute **`Aga Copper On` / `Off`**, activation via `MakeScreen/RethinkDisplay` puis détachement et libération des allocations de l'extension. **R17 PASS WinUAE (3 exécutions) sur la liste vide. R18 ajoute `Aga Copper Wait`, `Move`, `End` : raster RGB4 visible et Gate B WinUAE PASS pour le scénario testé.** Voir [M7 R18](M7_COPPER_R18.md). Pas de manipulation libre des registres de Copper via AMOS.

## 5. Interaction 2D et compatibilité jeux

[Plan souris / zones / collisions](INTERACTIONS_COLLISIONS.md) : R19/R21/R22 ont fourni les positions, boutons et fronts ; **le dispatcher R23 a passé un test WinUAE de clics rapides, FIFO clavier et Ctrl+C**. **M9/R24 hotspots et M10/R25 AABB sont validés sur leurs scénarios respectifs**. La résolution physique et les tests pixel-perfect sont hors du noyau R25 ; les fonctions géométriques ne dépendent pas du Copper.

**M11 — audit source R25 effectué :** [étude back buffer/RastPort](M11_BACKBUFFER_R25.md) : chaîne `A5+$1C8 → State+32 → DBState+8 → SB0/SB1 → sb_BitMap`, identique octet pour octet entre R23 et R25 sur les segments graphiques. `Aga Back Fill` utilise déjà `InitRastPort` puis `RastPort.BitMap=back`. **Évolution réalisée depuis cette étude :** `Aga Text` R26 utilise `graphics.library/Text` sur le back buffer AGA avec protection Safe, validée sous WinUAE sur les scénarios M11. R27 ajoute le contrôle Safe indépendant aux trois Blitters et réussit les 40 swaps M12. L'audit de départ M11 reste [archivé ici](M11_BACKBUFFER_R25.md). La reprise des fontes avancées est le jalon M14 (pas encore implémenté).

**Compatibilité graphique AMOS/AMCAF à évaluer :** les commandes AMOS et AMCAF telles que `Change Bank Font`, `Scrn Rastport`, `Text`, `Text Length` utilisent l'état graphique AMOS. Notre écran Intuition et son double buffering sont indépendants : **ne pas faire d'essai qui suppose que `Text` AMOS y dessine directement**. Les fonctions AmigaOS `Text` et `SetFont` peuvent viser un `RastPort` propre au back buffer, sous réserve de confirmer le code R25 et le cycle de vie des buffers. `Aga Blit Copy` ne remplace pas toutes les variantes de `Screen Copy`.

## 6. Modes et validations

AGA : palette indexée selon profondeur (1–8 plans), modes EHB/HAM avec sémantique particulière, HAM6/HAM8/SuperHiRes testés en M5 sous WinUAE pour les cas documentés ; cela ne valide pas toutes les combinaisons de ModeID. Les modes DblPAL/DblNTSC, les programmes compilés du candidat R15 et le matériel réel gardent leurs réserves.

**Gates :** A statique/AP20/CPU ; B interprété WinUAE ; C Compiler ; D vrai AGA. Suivre les résultats par jalon dans ses fichiers de STATUS et ne jamais extrapoler un PASS.

**Voir aussi :** [Roadmap](ROADMAP.md), [Index des docs](README.md), [Tests archivés](../tests/passed/), [Builders](../tools/README.md).
