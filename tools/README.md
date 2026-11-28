# Outils Python — builder actif et historique versionne

**28/11/2026 — P3c premier link FAIL, P3d requalification intégrée.** [CI initiale 46130520637](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46130520637) : UNIT142 franchit les assertions de placement, puis label hérité p2i_leave_only manquant dans UNIT213. Correction label, garde compte attaché >=4, contrôle ViewPort head/tail borné et pré-Get des allocations/slots/références, garde drop stage. Nouveau banc AP20 public (Runtime/Compiler modèles) : 3 largeurs, 2 versions OS modélisées, 8 mélanges simple/attaché, 3 paires, transitions, troisième frame, refus de largeur/genre/géométrie, OOM, acquisition partielle, échec Change, CloseScreen false/retry. Capture et chaîne P1 rejouées sur P3 exact. CI en attente de preuves ; aucune Lib active ni LAST_GOOD modifiée.

**28/11/2026 — P3b PASS, P3c intégration source-only.** [P3b CI 46129459290](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46129459290) PASS 505 scénarios sur chacun des trois chemins, slice compact 1732o SHA256 `19bdc48e0a8a6572813e80be4fb4a32b9b4194d662d42421e9f02d5df9c117f7`, gain 522o, marge brute UNIT142 472o. P3c assemble la future candidate depuis P1 exact et S2c-E1 exact via observers facultatifs. Nouveau registre v6 même nom, 612o, 3 slots 168o (reçu P2d 96o + métadonnées RGB et IDs). Préclose retire ET reclaim avant CloseScreen, refuse toute ambiguïté, garde header de lifetime jusqu'au BOOL de fermeture. Aucun code persistant ni nouveau token. Routes publiques Show/Move/Exchange/Off/Bank Free, stage retenu pour alternance, drop gardé pour troisième frame ; width commune, génération/hauteur/kind/palette identiques, hotspot zéro, 3 paires. UNIT142 réutilise fenêtre historique et slice compact append après root fixe; UNIT213 remplace routes v5, préfixe capture P1 strictement inchangé. CI de link/reconstruction à relever, tests publics CPU à compléter : aucune revendication de Gate A intégrée ni installable. Aucun changement Lib/ASC/ABK/LAST_GOOD. Auteur « aller avance arrete de tarreter puatin ».

**28/11/2026 — P3a PASS, P3b compactage source-only.** [CI P3a 46129309895](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46129309895) PASS 325 scénarios sur le slice à adresse indépendante, code complet 4882o, slice 2254o dont shim 20o, SHA256 `a7e9e26b038694d4bff727985fc3a21b6c7cd6a85e0df7c9db91688848376d29`. Retire/Reclaim net 2234o excède de 50o la marge brute UNIT142 (2184o), avant raccord registre. P3b ajoute variante `--compact` : remplacer uniquement les trois blocs exacts d'alloc/alias, références et FreeSpriteData déroulés par boucles bornées sur offsets 4/8/52/56/72/76, même ordre, même hauteur blank/frame, 15 comparaisons d'alias, consommation des pointeurs avant OS. Source P2d intacte, slice exact maintenu, 180 nouveaux scénarios d'alias descripteur/stream à hauteur1, avant retraite ou reclaim privé, sur toutes largeurs. Rejouer les trois variantes ; taille et résultat à relever. Même si la taille brute passe, placement effectif Close/End/AP20 et registre restent à qualifier. Aucun changement livré dans la Lib/ASC/ABK/LAST_GOOD.

**28/11/2026 — P2d PASS, P3a étude de placement source-only.** [CI P2d 46129155350](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46129155350) PASS préparation 165, acquisition 341, affichage 298, Move/Change 684 chacun, 272 négatifs, retraite 325. SHA256 retraite P2d `48e52ed1c95b58dd2df7cf68204a986751394241c5ca9c9c111f643a8e2416a2`. [Policy 46129155352](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46129155352) PASS. P3a : `emit_m19_s2d_ext_close_slice.py` extrait les fonctions exactes Retire/Reclaim et leurs trois dépendances (span, no, unreferenced), sans code d'affichage et sans nouveau code de libération. Le modèle prépare avec le composant complet puis appelle le slice à une adresse indépendante ; répète tous les scénarios de retraite/reclaim. Taille assemblée et CI à relever. UNIT142 actif 63350/65534 octets : 2184 octets bruts libres, mais aucune insertion supposée possible sans contrôle de la fenêtre Close/End, du registre et des relocations. Garder un seul registre versionné et aucun pointeur de code persistant ; si duplication source limitée ne tient pas, qualifier séparément une solution AP20 interne. P3 registre et API non encore intégrés. Aucun binaire/ASC/ABK/LAST_GOOD touché.

**28/11/2026 — P2c3 PASS, P2d V39 attaché source-only.** [CI P2c3 46128783824](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46128783824) PASS 316 scénarios, SHA256 `346099f46594adcac2fe3d6d2f02254838df2954859b588d2dd170d7ff53defc`. P2d applique le correctif documenté AllocSpriteDataA V39 sur l'odd strictement détaché : bit7 octet3 et, pour 32/64, octet5/9. Garde taille/alignement/hauteur/TypeOfMem endpoints, aucun champ OS ou DMA écrit ; en cas de refus rollback des deux allocations encore privées. V40+ sans retouche. Acquisition séparée R1, Show/Move/Exchange/Retire modèles étendus V39/40 ; pas de preuve réelle du ROM V39 ni du DMA. CI P2d à relever. P3 : intégration publique/registre durable/Close/End reste à faire. Lib/ASC/ABK/LAST_GOOD inchangés.

**28/11/2026 — P2c2 PASS, P2c3 retrait/reclaim source-only.** [CI P2c2 46128561794](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46128561794) PASS 648 Move, 648 Change, 272 négatifs, SHA256 `c192adfe84ce0611db62022977567547aa246cd37be263f4c30ef1b0fdb9706a`. P1 : capture/chain/mixed-runtime PASS [run initial](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127045983) ; mixed-compiled initial annulé par timeout, [seconde exécution exacte PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127317655/job/140924680792), même SHA256 P1 `7741b1945206bf2176ccf1dfed4f8ec8d65c5e64eccd09ae50e5804c53d6da76`. Les quatre suites P1 sont donc PASS par preuves combinées sur le même binaire, pas un run initial intégralement vert. P2c3 inclut P2c2 et ajoute +12 Retire, +16 Reclaim. Reçu 96o ; +84 journal sticky bit31 et masque initial confirmé. État4/5/7/15/31, restitution odd/even uniquement sur reçus certains ; consommer chaque reçu avant appel FreeSprite, corroborer réservations/slots/neutralité, garder toutes allocations si ambiguïté. Vérification huit slots et étendues Chip, deux WaitTOF et snapshots LOF/SHF stables ; peut observer le View courant distinct de l'ancien VP, caller doit garantir chaîne OS sûre. Reclaim état0 privé ou20 retiré, revérification des références, appel FreeSpriteData sur chaque allocation unique avec effacement du pointeur, état32 terminal. Quarantaine sans déduction d'ownership. Source-only ; les preuves sont celles du modèle OS, pas DMA réel, Close/End public ni WinUAE. [CI composants](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever. Aucune Lib/ASC/ABK/LAST_GOOD modifiée.

**28/11/2026 — P2c1 PASS, P2c2 déplacement et échange de frame source-only.** [CI P2c1 46128012202](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46128012202) PASS 244 cas SHA256 `41803e181c660a423ca34f372079d45ee7f1c3b87a221be3b6708b7b21ebd2fb`, P2a 150 et P2b-R1 307 reconfirmés ; P1 mixed-runtime 288 changements PASS. P2c2 inclut le source exact P2c1 sans le modifier. Entrées privées +0 Show, +4 Move, +8 Exchange ; record 96o (72o précédents, +72/+76 stage, +80 phase 0 absent/1 privé/2 potentiellement exposé/3 ancienne frame sans références échantillonnées après fences, +84 zéro, +88/+92 LOF/SHF). Même largeur/profondeur/hauteur/palette et provenance à charge du caller. Move valide les deux refs, coordonnées, contexte, listes. Exchange valide les nouvelles allocations disjointes, masque la paire, vérifie deux WaitTOF cachés, remplace odd/even cachés, révèle, contrôle les huit slots Copper/table sans suivre les listes dynamiques, échange les pointeurs. État15 sticky en cas d'incertitude, garde les deux ensembles. Phase3 permet échange inverse ; ne prouve pas libération DMA universelle. Aucun FreeSpriteData ou écriture OS directe. [CI composants](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever. Retraite/Close/End et intégration publique restent à établir. Lib, ASC, ABK et LAST_GOOD protégés. Autorisation auteur « continu contonu ».

**28/11/2026 — P2b-R1 PASS, P2c1 première publication source-only.** [CI 46127825060](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127825060), 150 préparations et 307 reçus avec garde largeur, SHA256 P2b-R1 `e638265435685a5d7295c74c4a17a6403351aaaa8e6e41e287c5b6053dc5bc63`, [policy PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127825059). P2c1 ajoute `M19_S2D_EXT_HIDDEN_SHOW_MC68020.s` et `test_m19_s2d_ext_hidden_show_cpu.py`. Reçu privé étendu 72o, source V40 archivée (cf. audit R1), géométrie 320x256, caller garantit palette et allocations épinglées. Vérifications de hauteur/alignement/CHIP/ATTACH, mode, VP, table et CopInit. Move odd puis even à x0/y257 (initialisation coordonnées des blanks), ChangeExtSpriteA odd puis even cachés pour attaché, even seul pour simple ; corroboration des slots et positions à chaque appel, Move even final (propagation odd selon source V40), état31 seulement sur succès, état15 sticky après tentative incertaine, aucun Free ni modification directe des structures OS. Ne constitue pas preuve d'atomicité réelle, ne couvre pas encore Move répété, Change Frame ou retraite/Close/End. [CI composants](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever. Aucun changement Lib/ASC/ABK/LAST_GOOD.

**28/11/2026 — Correction P2b-R1 issue de l'audit du source OS V40.** Le fichier [simplesprites.asm, révision 39.41](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/a/simplesprites.asm), blob `9795ab23dfb810f04511002fc05d20df48203027`, est contradictoire avec l'Autodoc : ce snapshot rejette encore GSTAG_ATTACHED. Toujours deux GetExtSpriteA explicites, y compris V40 attaché, sans supposer que la ROM correspond exactement au snapshot. Le source confirme aussi que Get réserve et renseigne ss_num mais ne publie pas SimpleSprites ; MoveSprite installe le descripteur, et ChangeExtSpriteA reprend ss_x/y de l'ancien descripteur. AllocSpriteDataA n'initialise pas ces coordonnées dans ce snapshot : future publication doit d'abord positionner les blanks via MoveSprite hors VP, puis vérifier table et neutralité. Le [gfxbase.i 39.33](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/gfxbase.i), blob `d1ed75e43322452282589b884a4a2c83fd3e63c1`, donne offsets 166 SpriteReserved, 237 MemType, 444 SpriteWidth (mots), 448 SoftSprites (LIB_SIZE=34, IS_SIZE=22, LH_SIZE=14). Lecture seule V39/V40 avec lib_PosSize>=450 ; refus autres versions dans cette voie privée jusqu'à validation de leur layout (pas décision d'abandon OS ultérieur). Préflight matériel : 32px si MemType!=0, 64px si MemType=3 ; largeur existante ou négociation seulement si réservations soft uniquement et aucun objet de largeur différente. Contrôle paire libre avant Get, reçu even/odd + largeur réelle + bit de réservation après Get, conflit odd apparu entre appels => état5, incohérence => quarantaine. Le code OS de négociation peut masquer temporairement les soft sprites ; restauration réelle du curseur à vérifier. Aucun Move/Change/Free/écriture FMODE. Requalification source-only à relever.

**Gates composants précédents :** [P2a/P2b CI 46127548256](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127548256) PASS 150/187 cas (ancienne version P2b à tag, pas preuve R1) ; P2a SHA256 `ad36c7013356151c8561891ca339fc430ba527f07d904960d1f2496cdef3f95f`, P2b `be0e018f2aa8f2b7dfd14e137570cd531b1acb4ced0534f231851c1d0ac17019` ; [CPU et delivery](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127548274) PASS. [P1 capture](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127045983/job/140923838488) PASS 57 régressions 16px + 116 cas larges pour chacun des deux modèles AP20 ; chain PASS ; mixed à relever. P1 in-memory SHA inchangé. S2c-E1 reste active, LAST_GOOD/ASC/ABK intacts.

**28/11/2026 — S2d-P2b, source-only : préparation de deux blanks ExtSprite et reçus d'acquisition.** Deux descripteurs transparents de même largeur, hauteur 1, 2 plans pour simple (odd garde transparent) ou 4 plans pour attaché V40+. GetExtSpriteA par canal explicite 2/4/6 et odd ; tag GSTAG_ATTACHED pour V40+ attaché. État sticky avant le premier Get ; retour exact et ss_num public corroborés, échec second Get conserve reçu even, retour incohérent => quarantaine. Aucun FreeSprite/FreeSpriteData de mémoire potentiellement exposée, aucun Move/Change, aucun accès FMODE. Reçu privé 36 octets, largeur de contexte déclarée par caller sous emprunt registre (pas lecture du mode matériel). [CI P2a/P2b](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever ; aucune revendication de validation réelle, de paire atomique ou de détachement DMA. Le prochain composant devra établir neutralité et retraite, puis intégrer publication/changement, contexte et Close/End. P1 chain PASS, autres shards à relever. Aucune modification Lib/ASC/ABK/LAST_GOOD.

**28/11/2026 — P2a premier run FAIL dans le dernier groupe négatif, correction du seul oracle de test.** [CI 46127317618](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127317618) : assemblage MC68020, contrôles CPU/chemins et identité canonique PASS ; le banc arrive aux corruptions AGSP finales après les cas d'allocation. Le test inversait un bit du compteur de génération, produisant une génération non nulle toujours valide. Désormais cas positif génération non nulle modifiée, cas négatif génération nulle explicite, vérification de chaque mutation via le parseur indépendant avant refus attendu. Aucune modification native ; requalification complète à relever. Le premier run reste FAIL.

**28/11/2026 — S2d-P2a : préparation ExtSprite détachée source-only engagée en parallèle de la qualification P1, autorisation auteur « continu ne tarrete pas ».** [CI P1 46127045983](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127045983) : shard chain PASS sur les deux modèles AP20, build P1 observé 161096 octets SHA256 `7741b1945206bf2176ccf1dfed4f8ec8d65c5e64eccd09ae50e5804c53d6da76`, blob `3c6faa1ef3b4d833cf357146d05743d3647510c5`, 105 commandes/219 AP20, UNIT213 20498, marge WORD 45036, PC16 max 3658 avec réserve 16384. Autres shards P1 à relever. P2a : validation AGSP v1 complète, InitBitMap, AllocSpriteDataA (A2=bitmap, A1=tags), FreeSpriteData (A2) sur échec seconde allocation. Sprite simple V39+, attaché V40+ seulement pour ce composant : V39 a deux défauts documentés (ATTACH dans les données et GSTAG_ATTACHED), aucun contournement non qualifié ni décision d'abandon de V39. [CI P2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever. Aucune acquisition de canal ni publication DMA, aucune écriture ExtSprite/FMODE, aucune activation. S2c-E1/ASC/ABK/LAST_GOOD inchangés.

**28/11/2026 — S2d-P1 intégration capture source-only engagée, autorisation auteur « ok on continu ».** [P0 CI 46125716891](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46125716891) PASS : six groupes CPU, fixture 24 images 6836 octets SHA256 `f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64`, régressions S1/S2c et contrôle du couple actif PASS. [Requalification intégrale S2c-E1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826) PASS. P1 relie le Get AGA Sprite existant aux kernels larges via le pont ScreenBuffer Safe/WaitBlit et la transaction AGSP inchangée : largeur inclusive 16/32/64, workspace 4120+128*W (6168/8216/12312), staging oldlen+96+(W/2)*H, largeur explicite dans les requêtes privées. Builder en mémoire depuis le source exact S2c-E1, vérification du parent SHA et AP20, ancien mode sans option inchangé. [CI P1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-public-capture-gate-a.yml) à relever : aucune validation intégrée revendiquée avant les résultats. Aucune modification DMA, token, bibliothèque, ASC, ABK, LAST_GOOD ni archive. Prochaine étape après qualification P1 : ExtSprite V39+ (P2).

Builder P1 source-only : `python -B tools/build_m19_s2d_capture_in_memory.py --vasm <vasmm68k_mot>` ; aucun résultat écrit dans dist/. Le builder actif S2c-E1 reste celui documenté ci-dessous.

**28/11/2026 — S2d-P0, sources de capture/repack 16/32/64 engagées pour 0.15.0-alpha.1 (pas de Lib intégrée).** Deux kernels MC68020 isolés, dérivés de S2c sans modification de ses sources : descripteur capture +62.W largeur explicite, repack +36.W largeur et +38.W réservé zéro ; stride=W/8, 4*stride*H maximal 8192 octets. AGSP v1 sur disque inchangé ; aucune modification DMA/OS/AP20. Générateur de 24 images contrastées (3 largeurs × 4 familles × 2 frames, sous-palettes RGB24 cohérentes) et banc CPU avec oracle AGSP indépendant, canaris, conservation des entrées, tous les comptes de couleurs, hauteur 1/256, bords, transparence, 16 opaques et refus, remplacements entre largeurs/profondeurs. [CI P0](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-wide-capture-gate-a.yml) à relever ; aucun PASS CPU revendiqué avant résultat. La suite intégrera la capture dans les commandes existantes, puis la voie ExtSprite V39 qualifiée séparément. S2c-E1 reste active, B/C fonctionnelles PASS. Aucun changement du couple actif, archives ni LAST_GOOD.

**28/11/2026 — S2c-P1e Gates B Runtime et C Compiler fonctionnelles PASS** (PRG_STATE=1/-1, RESULT=1 ERR=0 CLEAN_ERR=0, PASS_S2C_MIXED). Chaque mode : 3 Open/Close, 12 Show, 450 Change, 450 Move, 3 Off, 9 retraits auto, 3 saturations -206, AGAPIC 6/6, AGSP 4 plans 6/6 et 3 refus. Chip/Fast sans perte nette ; Fast temporaire 1464 octets récupérée. Attribution à la Lib active par contexte, SHA installé, visuel complet, relance indépendante et D non attestés. L'auteur demande de renforcer le contraste des prochaines campagnes. S2c-E1 reste active (160896 octets, SHA256 `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310`), aucune promotion de LAST_GOOD. [Preuves](../docs/M19_S2C_P1E_RUNTIME_COMPILER_2026-11-28.md).

**Chantier suivant : 0.15.0-alpha.1 (M19 S2d)** : capture/repack puis affichage Sprite 16/32/64px ; largeur commune par contexte, API existante, couleur franche et motifs asymétriques. Source-only jusqu'à preuve Gate A et bascule explicitement autorisée. Cible publique 0.15.0 ; objectif final 1.0.0. Ne pas renommer les binaires historiques. [Plan](../docs/M19_S2D_WIDE_SPRITES_0_15_0.md).

Les états précédents ci-dessous sont historiques.

**28/11/2026 — S2c-P1e (titre interne S2c-E1) active sur main, autorisation auteur « ben go... ».** Gate A complète par preuves combinées sur le même binaire exact : [premier run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46123061368), 8 suites historiques PASS, 288 changements + 11 injections P1d + 15 scénarios ViewPort réussis dans chaque layout avant assertion erronée du dernier scénario ; [requalification](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826), jobs ciblés [fences-compiled](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826/job/140915600110) et [fences-runtime](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826/job/140915600178) PASS avec retour -104595462, aucune staging/publication et retraite des deux canaux, peer intact. Correction du seul test `817f26311e231730768f2711cd5dbb37320939d5`, aucune modification native depuis `25cf6e9d7d625b60599eef1749814f1aed472da8`. La CI initiale reste FAIL et le second passage intégral est en cours à ce relevé ; ne pas les annoncer comme runs intégralement verts. CPU/chemins et documentation PASS. Double reconstruction et préflight ASC strict PASS. Lib 160896 octets SHA256 `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310`, blob `9110fe94f0d937207038d77d6df250b99392c54c`. MC68020+, 105 commandes/219 AP20 ; UNIT213 seule modifiée par rapport à P1d (20298 octets, marge 45236), PC16 max 3658 avec réserve 16384. ASC 15459 octets et ABK 1460 octets byte-exacts. P1d historique B FAIL check 5 (`8e17d6f524f320832f7c7489cf27fe4f92b084df`). P1e B/C/D réelles NON TESTÉES ; CI post-activation à relever. LAST_GOOD L2b protégée ; aucune promotion, branche, archive ni release. [Rapport](../docs/M19_S2C_P1E_VIEWPORT_CHAIN_2026-11-28.md).

Builder actif : `python -B tools/build_m19_s2c_in_memory.py --vasm <vasmm68k_mot> --viewport-chain`. Les modes sans option et --diagnostic reconstruisent P1c/P1d byte-exacts. Le vérificateur authentifie la filiation P1e→P1d→P1c→S2r.

**28/11/2026 — P1d Gate B Runtime FAIL, diagnostic discriminant réussi :** `SPRITE_RC=-17104896` = `-$01050000`, stage 1/check 5/detail 0 : `ViewPort.Next` non nul avant acquisition. `ERR=10`, `CLEAN_ERR=0`, mêmes compteurs que P1c ; Chip 1791328 et Fast 138086880 identiques avant/après. P1d active (S2c-D1, 160812 octets, SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`), B FAIL, C/D non testées. Auteur « pook go » : correction P1e source-only engagée avec diagnostic conservé, parcours borné et read-only des successeurs ; pas de bascule avant Gate A PASS. ASC/ABK/LAST_GOOD inchangés. [Rapport](../docs/M19_S2C_P1E_VIEWPORT_CHAIN_2026-11-28.md).

Les statuts précédents ci-dessous sont historiques.

**28/11/2026 — S2c-P1d (titre interne S2c-D1) active sur main, autorisation auteur « go ».** [Gate A intégrée PASS 11/11](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896471), source `adcfa65d0f2e8ca402263eb3f0daee90d3471265` : 288 changements + 11 injections de défauts par modèle Runtime/Compiler, capture et régressions historiques PASS ; double reconstruction et préflight ASC strict PASS. Lib 160812 octets SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`, blob `551674f3598c8b0c10a581d9ac7a1f7cf1155659`. MC68020+, 105 commandes/219 AP20 ; UNIT213 seule modifiée (20216 octets, marge 45318), PC16 max 3658 avec réserve 16384. ASC 15459 octets et ABK 1460 octets strictement inchangés. P1c Runtime FAIL -153 conservée dans Git `8f490c4ee9f3609abd763e8ba2f03e4d97de49de`. P1d est un diagnostic, pas un correctif fonctionnel ; B/C/D P1d NON TESTÉES, CI post-activation à relever. LAST_GOOD L2b protégée, aucune promotion, nouvelle branche, archive ni release. [Rapport](../docs/M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md).

Builder actif : `python -B tools/build_m19_s2c_in_memory.py --vasm <vasmm68k_mot> --diagnostic`. La variante sans option reconstruit P1c byte-exacte. Le vérificateur canonique authentifie la filiation P1d→P1c→S2r.

**28/11/2026 — S2c-P1c Gate B Runtime FAIL** (`PRG_STATE=1`, ERR10, SPRITE_RC=-153, CLEAN_ERR=0). Écran 1 simple complet ; 150 Change/Move ; écran 2 premier attaché ID42/image9 refusé après le premier simple ; écran 3 non atteint. AGAPIC 4/4, capture AGSP 4 plans 4/4, refus 2/2, 2 Close, mémoire finale identique. S2c-P1c reste active (SHA256 `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb`), C/D non testées, LAST_GOOD protégée. Auteur « vaa y fait moi tous le diag » : P1d instrumentée source-only, Gate A et reconstruction à relever avant activation. Ne pas lancer le Compiler P1c. [Diagnostic et journal](../docs/M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md).

**28/11/2026 — S2c-P1c, candidate de test active sur main, autorisation auteur « va y », puis « ok continu des que c bon ».** [Gate A intégrée PASS 11/11](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072322336), source `5efc907baadd7c736345a97464023e2695e15c6b` : deux modèles mixtes 288 changements chacun, 392 contrôles AGAPIC et régressions capture, Pattern, SafePort, Bob, DB/IFF/Swap PASS. [Campagne exacte et préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072461473). Lib 159844 octets SHA256 `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb` blob `7e8b5320c4098db053afb2bf8ce9f16bf611ff39` ; ASC 15459 octets SHA256 `48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec` ; nouvelle ABK AGSP_S2C_MIXED.ABK 1460 octets SHA256 `6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246`. 105 commandes / 219 AP20, MC68020+, UNIT142 63350, îlot Sprite 213 19246 octets, marge WORD 46288, réserve 16384 vérifiée. Titre binaire exact S2c-P2 (aucune retouche cosmétique). S2r préservée dans Git `31735f84f0da50ea4ba324f9bc63bec9313cd47a`. Gates B/C/D réelles S2c NON TESTÉES. CI post-activation à relever. LAST_GOOD L2b et anciennes ABK inchangées ; aucune promotion, branche, archive ni release. [Rapport](../docs/M19_S2C_P1C_PUBLIC_MIXED_2026-11-27.md).

Builder actif : `build_m19_s2c_in_memory.py` ; `verify_m19_s2c_delivery.py` vérifie le SHA et la structure AP20 exacte, puis la filiation S2r ; `prepare_m19_s2c_campaign.py` régénère en RUNNER_TEMP depuis l'ASC historique, sans écriture dans dist.

**27/11/2026 — S2r-P1 A/B/C fonctionnelles PASS dans le périmètre du banc.** B Runtime 1/1 (`PRG_STATE=1`, Fast transitoire 128 octets récupérés), C vrai Compiler 1/1 (`-1`, aucun écart cycle), 4/4 Capture/Meta/Negative/Draw, 300 changements/déplacements, 2/2 Open/Close, ERR=CLEAN_ERR=0, pertes nettes Chip/Fast nulles. Capture WinUAE fournie : trois rectangles rouges et trois Sprites distincts simultanés. Pas de preuve de seconde relance indépendante, de SHA installé ou Gate D physique. CI post-activation en échec sur l'accès Git superficiel au prédécesseur S2b ; [correction 21 workflows fetch-depth: 0](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5c20ee6fca24b5248a7510c29d6586dfac3bfc0f) livrée, résultat final à relever. S2r active inchangée ; LAST_GOOD L2b protégée. Autorisation auteur « oui va y » pour corriger CI et consigner les preuves ; S2c après requalification CI, pas de promotion ni nouvelle Lib. [Résultats et journaux](../docs/M19_S2R_RUNTIME_COMPILER_2026-11-27.md).

**27/11/2026 — S2r-P1 candidate active sur main, autorisation auteur « ok va y ».** [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059388877) : 8 jobs, 1200 changements Sprite, 600 cycles Show/Off, 20 fermetures et négatifs, 392 contrôles AGAPIC déplacés, DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob. [Double construction et préflight ASC strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059623366). Lib 154352 octets SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a` blob `61d8211e449ffd9cb41e3fb2b6ec9efdf352c88c` ; ASC 11806 octets SHA256 `d06f3c296d45a8766acdf678b03675c99ee702baf776a2f2f50e2da5aa8939e3` blob `f1985251d4d37e978c4ec61b5e06f81fb3559ee4` ; même AGSP_S2B_MULTI.ABK 1012 octets blob `c122c79976bce5afad051f487d77af8cc296f2cc`. UNIT142 63350 (2184 libres), UNIT207 13756 (18978 libres PC16), nouvel îlot 214=3640, PC16 max 13786, 105 commandes / 219 AP20, MC68020+. Gates B/C/D réelles de S2r NON TESTÉES. S2b A/B/C historique dans Git ; LAST_GOOD L2b et toutes ABK protégées. Aucune promotion, autre branche, archive ou release. [Rapport](../docs/M19_S2R_REPARTITION_2026-11-27.md).

**27/11/2026 — S2b-P1 candidate active, autorisation auteur « ok go ».** [Gate A intégrée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46041721740), source `f49a027ce466b4968c60db0dab901b53751aecd2` : 1200 changements d'image, 600 cycles Show/Off, 20 fermetures collectives et négatifs dans deux modèles AP20 ; chain DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob ; 7 jobs PASS. [Reconstruction et préflight ASC strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46042040810). Lib 152876 octets SHA256 `b44edbbcf4b3c02cb6527ea0f002bee863c992dd4b670636e7431a1b69e1a2fa` blob `6a9493b69c5fa64a0cb167722423cfee7f18bbb3` ; ASC 8954 octets SHA256 `2cda351432ba495589c4848ef8c2d640426e18c6e71287d643a506e2e21acde0` blob `2d1737f64cff84a24ff7551386abd672dc59b738` ; nouvelle ABK 1012 octets SHA256 `eb0060bce79d15785d5d6f6caf31f8819adfd518b0e179dca5feb025b80b2c78` blob `c122c79976bce5afad051f487d77af8cc296f2cc`. UNIT142 65524 (10 libres), UNIT207 13756 (18978 libres PC16), PC16 max 13786, 105 commandes/214 AP20, MC68020+. B/C/D réelles non testées. Anciennes ABK et LAST_GOOD L2b inchangées. S2a A/B/C validée dans Git ; aucun changement de release ou branche. [Rapport](../docs/M19_S2B_MULTI_SPRITE_2026-11-27.md).

**27/11/2026 — S2b-P0 retrait par paire : [114 cas MC68020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46037779887).** Source `b7e7b2e71c3393cfd81cad080f3ecc25422f7b3e`, politique CPU/delivery et paire active S2a vérifiées avant/après. Retrait indépendant des paires 2/3, 4/5, 6/7, six ordres de retrait des trois paires actives, reçus partiels, références tardives et retry. Seulement composant CPU + OS modélisé ; intégration registry/Close/End, Gate A intégrée et B/C/D S2b encore à faire. S2a validée A/B/C reste active, LAST_GOOD inchangée.

**27/11/2026 — S2a-P1 active sur main, autorisation auteur « ol continu jusqua la lib ».** [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45907171922), commit source `91a4acf89f511420ba0a87515ec2a85b6d124277` : 10 jobs réussis, 400 changements d'image et négatifs, 200 cycles/20 fermetures P2m hérités, DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob, reconstruction exacte et préflight strict PASS. Lib 151164 octets SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2` blob `190504fd46494224c6c32e20f17dcc3d6a027684`; ASC 7265 octets SHA256 `d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb` blob `ac74e8773a86914a00f3a153487afe61a9803efc`; nouvelle banque de campagne AGSP_S2A_ANIMATION.ABK 372 octets SHA256 `4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa` blob `210179c9328e1ff032070b2dd40ffa8849e8294a`. 105 commandes / 214 AP20, MC68020+, UNIT142 65424 (110 libres) inchangée, UNIT207 12142, PC16 max 12172, marge 20592. Uniquement UNIT207 et titre changés depuis P2m. Aucun changement LAST_GOOD L2b, ancien ABK ou archive, aucun autre dépôt, branche, promotion ou release. B/C/D S2a non testées. L'ancien P2m reste dans Git. [Rapport](../docs/M19_S2A_PUBLIC_FRAME_CHANGE_2026-11-26.md).

**26/11/2026 — S2a engagé, premier composant source seul.** [Staging et contrat](../docs/M19_S2A_FRAME_STAGE_2026-11-26.md). P2m reste active ; pas de nouveau token, Lib, ASC ou promotion. CI composant [PASS 148 cas MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45896382931) ; intégration/publication DMA et Gates B/C/D S2a non acquises.

**26/11/2026 — clôture fonctionnelle P2m, accord auteur « oui passons a la suite du chantier sprite » puis « ok go ».** Gate B Runtime fonctionnelle validée (trois derniers PASS stricts), Gate C Compiler fonctionnelle 2/2 (PASS strict 1/2 ; ERR14 sur écart Fast temporaire 128 octets). Aucun écart net de Chip/Fast par exécution. D physique non testée. Auteur accepte la clôture fonctionnelle avec réserve ; aucune promotion LAST_GOOD. Les fichiers RAM conservés expliquent les différences entre lancements selon l'auteur ; leur coût exact n'a pas été isolé. La Lib et l'ASC exacts restent actifs, LAST_GOOD L2b protégée. Prochaine étape S2a : changement d'image à chaud, source-only avant Gate A, sans nouveau token. [Résultats et journaux originaux](../docs/M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md).

**26/11/2026 — S1-P2m active sur main, Gate A complète PASS.** Lib 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, blob `a29e86a6414021e19b87615681dcc08fe406518c`, 105 commandes / 214 AP20, MC68020+. [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891037257) (source ee70cdf84e4ec1896eb657b07e2a2876d2244932) : 100 cycles et 10 fermetures par modèle AP20, cas négatifs, 184 Pattern, 172 SafePort, 10 suites Bob, DB/IFF/Swap/capture ; reconstruction identique et préflight strict PASS. [Reconstruction indépendante](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891360197). UNIT142 65424 (110 libres), UNIT207 10380 (22354 libres PC16), PC16 max 10410. ASC 6700 octets SHA256 `84d2dfddc753e2c05d8a05ff991fe8b4f3e6d36daa20110cc447add547aaa684`, blob `ddd9b676b9a3d4c0f4cccf08ca058cade61df9aa`. À la livraison : B/C/D non testées (voir actualisation ci-dessus). LAST_GOOD L2b et ABK inchangées. Autorisation auteur « continu livre moi cette lib ». P2l-c historique rejetée en relance fonctionnelle.

[Rapport et protocole fonctionnel](../docs/M19_S1_P2M_FUNCTIONAL_LIFECYCLE_2026-11-26.md).

> S1-P1i : Gate B Runtime capture AGSP PASS (journal auteur du 24/11/2026, PRG_STATE 1, RESULT 1, ERR 0) ; attribution à P1i par contexte, empreinte de la Lib installée non consignée. C reportée, D non testée ; aucune DMA.

## Candidate active S1-P2m (26/11/2026)

Builder `build_m19_s1p2m_in_memory.py`, vérificateur `verify_m19_s1p2m_delivery.py`, ASC `prepare_m19_s1p2m_campaign.py`. Les anciens builders reconstruisent les parents vérifiés depuis l'historique Git (clone complet), en mémoire, sans écrire dans dist/. Gate B fonctionnelle à effectuer.

## Historique S1-P2l-c (26/11/2026)

Builder `build_m19_s1p2l_c_in_memory.py`, Gate A 532 PASS, reconstruction exacte PASS ; `verify_m19_s1p2l_c_delivery.py` et `active_library.py` contrôlent la paire exacte et la récupération du parent P2l-b. ASC via `prepare_m19_s1p2l_c_campaign.py` depuis P2l-b historique (préflight strict PASS). B à effectuer, C reportée, D non testée. [Rapport](../docs/M19_S1_P2L_C_IDLE_DETAIL_2026-11-26.md). Aucun changement de LAST_GOOD.

## Historique S1-P2l-b (26/11/2026)

Builder `build_m19_s1p2l_b_in_memory.py`, Gate A 496 PASS, B Runtime 2/2 quarantaine, C reportée, D non testée. [Rapport](../docs/M19_S1_P2L_B_DIAG_ROUTE_2026-11-26.md).

## Historique S1-P1i (24/11/2026)

`dist/AMOSPro_AGA.Lib` : 142968 octets, SHA256 `2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3`, 102 commandes / 208 AP20, [Gate A native PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492646401). Builder source `build_m19_s1p1i_l2b_contract_in_memory.py` (VASM MC68020), vérification exacte avec `test_m19_s1p1i_l2b_integration_gate_a.py`. Base protégée L2b SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`. Runtime B / vrai Compiler C / matériel D non testés. Les anciens builders restent reproductibles et les sections ci-dessous sont historiques.

## Historique P2d-L2 (24/11/2026)

`dist/AMOSPro_AGA.Lib` : 136 332 octets, SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1`, 100 commandes / 203 AP20, Gate A 172 cas writers + 10 suites Bob PASS. Builder source `build_m19_p2d_l2_first_bind_in_memory.py` (vasm MC68020), reconstruit L1 puis L2 et compare à la Lib active exacte. `active_library.py` vérifie les deux SHA et les plages natives append-only. LAST_GOOD P2d protégée. B/C/D NON TESTÉES. [Protocole](../docs/AGA_L2_WINUAE_CAMPAIGN_2026-11-24.md). S1-P1e gelée et reconstructible depuis son builder historique ; aucune commande Sprite active.

## Migration ASM P2d — source entierement classifiee (22/11/2026)

Les quatre unites natives P2d sont couvertes par **268 modules ASM
MC68020** et un inventaire **sans octet non classifie**.
**122 602 octets de mnemoniques sur 131 734 octets de groupes AP20
(93,07 %)** ; 9 132 octets restants prouvables par les sources,
dont **98 octets de suffixe d'ancienne boucle R80 (IFF/UNIT156)**
qu'il ne faut pas reutiliser librement.

Reproduire la source via `tools/build_m19_p2d_editable_asm.py`,
ou directement par vasm sur
`src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s`.
Controles utiles : `m19_p2d_unit142_raw_probe.py --check`,
`m19_p2d_unit153_source.py --check`,
`m19_p2d_unit156_nibble.py --check`.
[Rapport](../docs/M19_P2D_NATIVE_SOURCE_CLASSIFICATION_2026-11-22.md).
Aucune modification de `dist/`, de LAST_GOOD ou des tests AMOS.


## Statut courant — P2d / UNIT142 MC68020 (22/11/2026)

Lib officielle inchangée : `dist/AMOSPro_AGA.Lib` et
`dist/AMOSPro_AGA_LAST_GOOD.Lib`, 136 020 octets,
SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.
100 commandes et 203 entrées AP20. Builder original
`tools/build_m19_p2d_in_memory.py::build_p2d`.
Builder ASM source `tools/build_m19_p2d_editable_asm.py`.

**266 modules ASM au total, dont 166 UNIT142** :
**58 166 octets d'instructions UNIT142 (92,71 %)** et
**4 574 octets non-code source-prouvés** ; **0 non classifié**.
[Gate A source PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45061168489) : P2d réassemblée
octet-identique, **166 mutations confinées**.
Les 21 NOP R83 demeurent des instructions, sans qualification
de padding libre. WinUAE B, Compiler C, matériel D non requalifiés.
[Reprise](../docs/NEXT_SESSION.md) ·
[Audit UNIT142](../docs/M19_P2D_UNIT142_RAW_REMAINDER_AUDIT_2026-11-22.md).


## Historique — M19 B7-m1, Runtime uniquement (18/11/2026)

**Bancs de vitesse arrêtés après Gate B PASS** du décor texturé. Le [programme d'exemple public](../examples/bob_local_restore/README.fr.md) utilise uniquement la restauration locale + quatre Bobs, avec titre et sortie interactive (nouvelle variante, PREFLIGHT PASS ; WinUAE à confirmer). Prochaine étape de développement : [cycle de vie Bob Off, multi-banques et IDs 1..64](../docs/M19_NEXT_BOB_LIFECYCLE_2026-11-18.md), sans modification automatique de la Lib ni Compiler.

La **seule** bibliothèque destinée aux tests est `dist/AMOSPro_AGA.Lib`, construite par `build_multiframe()` dans [build_m19_p0j_end_lifecycle_in_memory.py](build_m19_p0j_end_lifecycle_in_memory.py) : **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, quatre îlots MC68020, 86 commandes / 181 entrées AP20. La source B7 d'origine est figée ; son builder `build()` reste reproductible et ne doit pas remplacer cette candidate. La [Gate A multiframe](../docs/M19_P0J_B7_MULTIFRAME_GATE_A_2026-11-18.md) a PASS 793 contrôles et deux implantations, avec Safe/Disp simulés. Le [banc précédent de 120 frames](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/75caa3c8198aad612e434e1ae3d54ceb2249ca45/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) a passé la Gate B Runtime (journal 120/120, quatre lancements sans traînées). Le [banc A/B/C Fill historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/2d019a555447ab3cd294d1c4b4e69928d7afd9db/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) a **PASS Gate B** : 720/720 frames et réduction de 48,85 % du temps mesuré en effacement local (719 retries VBL inclus). [Résultats](../docs/M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md). Le [banc actif A/B/C à décor non uniforme](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), **9 624 octets**, SHA256 `8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904`, conserve l'unique ASC de campagne. Préflight strict et oracle pixel simulé de 720 frames PASS ; **Gate B Runtime WinUAE PASS** (720/720, ERR 0, visuel confirmé, A/B 25,05 FPS, C 48,98 FPS, 719 VBL de retry) ; **Gate C Compiler NON TESTÉE**. [Nouveau protocole](../docs/M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md). **Aucun essai Compiler**, R84 LAST_GOOD et archives intacts. Les chapitres P0c et antérieurs ci-dessous sont historiques.

## État actif — M19 P0c distribué pour Gates WinUAE B/C (16/11/2026)

Avec autorisation explicite, le candidat reconstruit par [`build_m19_p0c_screen_close_in_memory.py`](build_m19_p0c_screen_close_in_memory.py) est maintenant installé **uniquement** sous [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, **82 commandes / 92 entrées AP20**. Le [seul ASC actif](../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc) passe le preflight statique de la Gate A ; Gates B Runtime WinUAE et C vrai Compiler encore NON TESTÉES. Le bloc ci-dessous décrit l'état **historique avant cette autorisation**. La Lib P0b est reproductible via son builder figé ; `LAST_GOOD` R84 et archives intacts. Aucun artefact CI alternatif.

## M19 P0c — pont source-only Screen Close et End, Gate A CPU020 (16/11/2026)

Le builder [`build_m19_p0c_screen_close_in_memory.py`](build_m19_p0c_screen_close_in_memory.py) utilise **exclusivement** le constructeur P0b exact, contrôle les signatures du code AGA **historique et inchangé** (groupe 91), redirige le seul token `Aga Screen Close` (index 8) vers le [pont MC68020](m19_p0c_screen_close_bridge_emit.py) ajouté à BOBS (groupe 90) et ajoute [l'armement/callback End privé](m19_p0c_program_end_bridge_emit.py). Aucune modification de la Lib P0b ni de `LAST_GOOD`.

La candidate AP20 expérimentale est produite **en mémoire** : **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`, 82 commandes et 92 entrées. Les tests [`test_m19_p0c_screen_close_real_gate_a.py`](test_m19_p0c_screen_close_real_gate_a.py) et [`test_m19_p0c_program_end_real_gate_a.py`](test_m19_p0c_program_end_real_gate_a.py) exécutent les **vrais octets Init, Close et End natifs AGA** avec des services OS simulés. [CI Gate A et artefact non installé](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43925480841) PASS (38 scénarios Close, 54 End, 116 P0b). Le test [ASC séparé, préflight statique PASS](../tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc) attend les Gates B/C WinUAE. Documentation : [rapport et protocole](../docs/M19_P0C_SCREEN_CLOSE_BRIDGE_GATE_A_2026-11-16.md).

**Ne pas présenter comme livré en production :** `End` est armé uniquement depuis une entrée Chip **privée**, aucune instruction AMOS ne prépare encore les Bobs en Chip ni ne déclenche ce callback ; pas de rendu, pas de test WinUAE/Compiler P0c.

## M19 P0c — pré-fermeture AGA privée MC68020 (16/11/2026)

- [`m19_p0c_screen_preclose_emit.py`](m19_p0c_screen_preclose_emit.py) : entrée native privée après registre P0c, obtient `GfxBase` par `A5+0x1C8` / `State+8` et refuse un cleanup non sûr ; aucun appel `CloseWindow`/`CloseScreen`, aucun hook AP20.
- [`test_m19_p0c_screen_preclose_native.py`](test_m19_p0c_screen_preclose_native.py) : **42 tests MC68020 PASS**, deux placements, type mémoire/CPU/ABI, absence de GfxBase, double fermeture, deux banques, conservation des ressources en échec et contrôle du dispatch P0b réel (`Aga Screen Close` token 8, groupe 91, BOBS 90). [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43920983278).
- **Pas de `.Lib` P0c**, pas de test de la vraie fermeture publique ni de WinUAE/Compiler. Le module AGA R88 assembleur n'est conservé qu'en restitution partielle d'audit, **non appropriée pour patcher le code de production**. [Rapport P0c](../docs/M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md).

## M19 P0c — registre automatique Chip par banque (Gate A privée, 16/11/2026)

- [`m19_p0c_bank_registry_emit.py`](m19_p0c_bank_registry_emit.py) : source native MC68020 privée, liste de contextes par banque, `registry_prepare`/`lookup`/`free`/`close`, allocation/rollback et libération après `WaitBlit`. Préfixe P0b/P0c immuable.
- [`test_m19_p0c_bank_registry_native.py`](test_m19_p0c_bank_registry_native.py) : **64 scénarios CPU020 PASS**, y compris deux banques, remplacement, erreur d'allocation, propriétaire A5, fermeture idempotente et libération après `Erase` ; [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43917996936).
- La fermeture est **privée, non branchée à la commande publique `Aga Screen Close`**. Aucun binaire `.Lib` P0c ni token AP20 nouveau, aucune preuve Runtime/Compiler P0c ; [rapport](../docs/M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md).

## M19 P0c — wrapper privé AGBO et Chip (16/11/2026)

- [`m19_p0c_checked_bank_stage_emit.py`](m19_p0c_checked_bank_stage_emit.py) : ajout **source-only** à la fin du groupe natif P0b figé. Vérification stricte de la banque AGBO et de ses masques avant staging dans la zone Chip.
- [`test_m19_p0c_checked_bank_stage_native.py`](test_m19_p0c_checked_bank_stage_native.py) : **120 scénarios CPU020 PASS**, deux placements, tests de corruption, lookup/release et **deux contextes Chip** indépendants. [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43916465599).
- Le [helper `m19_p0c_chip_stage_emit.py`](m19_p0c_chip_stage_emit.py) conserve **64 tests privés PASS** ; le modèle AGBO hôte conserve ses **9 tests**. Pas de token AP20 nouveau, pas de sortie `.Lib`, pas de rendu. Le builder installable demeure `build_m19_p0b_masks_in_memory.py` pour la candidate P0b.

## M19 P0c privé — staging Chip MC68020 (16/11/2026)

Les scripts [`m19_p0c_chip_stage_emit.py`](m19_p0c_chip_stage_emit.py) et [`test_m19_p0c_chip_stage_native.py`](test_m19_p0c_chip_stage_native.py) préparent le **noyau natif privé** (allocations Chip/TypeOfMem/CopyMem/WaitBlit/FreeVec). **64 cas Gate A CPU020 PASS**, système Amiga simulé. **Ce ne sont pas les builders de la bibliothèque P0b**, et ils ne produisent ni nouvelle Lib ni token AP20. Voir [le rapport technique](../docs/M19_P0C_CHIP_DMA_PRIVATE_GATE_A_2026-11-16.md). Builder installable P0b vérifié : `build_m19_p0b_masks_in_memory.py`; source de base R88 figée, R84 `LAST_GOOD` protégée.

## Point d'entrée actif (audit du 15/11/2026)

Le builder à examiner pour la bibliothèque installable de travail est `tools/build_aga_current.py`, à confronter à `dist/AMOSPro_AGA.Lib`, à ses SHA et au HEAD réel de `main`. Au checkpoint R88 v0.13.33, le builder source `tools/build_m19_p28_r88_in_memory.py` reconstruit la candidate à partir de l'archive R87 figée ; cela ne rend pas R87 installable à la place de `dist/AMOSPro_AGA.Lib`. Les builders et tests plus anciens restent conservés pour la reproductibilité et peuvent être appelés par la CI ou par des scripts actuels. **Aucun déplacement automatique dans `tools/obsolete/`, aucune suppression ni nouvelle arborescence.**

**Binaire installable unique :** `dist/AMOSPro_AGA.Lib` ; **R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` protégée**, sans promotion automatique. Un fichier sous `dist/experimental/` est une archive existante, **pas** une seconde candidate à installer. Vérifier le HEAD et la liste des outils réellement importés avant de désigner le builder courant : un ancien état R68/R87/R88 peut devenir historique. Les Gates CPU/CI, WinUAE Runtime/interprété et Compiler réel restent distinctes. [Règles permanentes](../EXTENSION_SOURCE_RULES.md) · [état courant](../docs/NEXT_SESSION.md).

## Historique — R68 v0.13.13 PROMUE `LAST_GOOD`, M18 Gates A/B/C PASS

**À la date du checkpoint R68, bibliothèque active : R68 v0.13.13**, `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` (51 064 octets ; SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`). [Compiler Gate C PASS](../docs/M18_R68_INTEGRATED_GATE_C_COMPILER_2026-11-13.md), Gates A/B/C PASS, Gate D physique non testée. [ASC archivé](../tests/passed/M18_R68_COMPILER_FINAL_01.asc). Méthodes CBlock 0 CPU8 / 1 CPU16 / 2 Blitter obligatoires ; aucune sélection automatique.

**Historique R67 v0.13.12 (ancien candidat) :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **43 180 octets**, SHA256 `ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5`, 61 commandes/68 AP20. `Aga F Icon Capture(Bank,IconID,X,Y)` capture 16×16 indices directement du back buffer AGA, X non aligné, couleur zéro masquée. [Émetteur](m18_ficon_capture_emit.py), [builder](build_m18_r67_ficon_capture.py), [240 cas Gate A natifs](test_m18_r67_ficon_capture_gate_a.py), [CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43456641279). [ASC unique actif R67](../tests/current/M18_R67_FICON8_CAPTURE_01.asc), Gate B interprétée en attente, Compiler C en fin M18. **R63 LAST_GOOD protégée**.


**Candidate R66 précédente Gates A/B PASS :** [binaire historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e8b9e2ef85f2c3f4a3a13fbedd715e18d9808664/dist/AMOSPro_AGA.Lib), **41 804 octets**, SHA256 `e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca`, 60 commandes / 67 AP20. `Aga F Chip Bank Create` et `Aga F Chip Stage`, [émetteur](m18_fichip_dynamic_emit.py), [builder déterministe](build_m18_r66_fichip_dynamic.py), [122 tests Gate A réels 68000 PASS](test_m18_r66_fichip_dynamic_gate_a.py), [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43453950765). [ASC R66 archivé](../tests/passed/M18_R66_FICHIP_DYNAMIC_01.asc), WinUAE interprété B **PASS** (deux captures auteur, `RESULT 1`, visuel CPU/Blitter confirmé, [rapport](../docs/M18_R66_FICHIP_DYNAMIC_WINUAE_GATE_B_2026-11-13.md)) ; Compiler C en fin M18, D physique non fait. **R63 `LAST_GOOD` protégée.**
**Ancienne candidate R65 v0.13.10 :** [binaire Git figé](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/1ba3a72d7bdbdbaafdd371767475453b5efd81ed/dist/AMOSPro_AGA.Lib) 40 116 octets, SHA256 `6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2`, 58 commandes / 65 AP20. Nouvelle `Aga F Icon Bank Put`, import de 256 indices couleur depuis une banque DATA AMOS vers un slot FICON8. [Gate A 98 cas natifs PASS, modèle hôte 44 cas, CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43444242260). [ASC R65 validé archivé](../tests/passed/M18_R65_FICON8_PUT_01.asc), WinUAE Gate B interprétée **PASS** (visuel transparent/opaque et `RESULT 1`, [rapport](../docs/M18_R65_FICON8_PUT_WINUAE_GATE_B_2026-11-13.md)) ; Compiler C une seule fois en fin M18. [R64 binaire historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e42d73d99d342baa2bac9ead456e45d4cea7e011/dist/AMOSPro_AGA.Lib) Gates A/B PASS ; **R63 LAST_GOOD protégée**.

**Ancienne candidate R64 v0.13.9 (historique)** : [binaire Git figé](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e42d73d99d342baa2bac9ead456e45d4cea7e011/dist/AMOSPro_AGA.Lib) 39 100 octets, SHA256 `4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c`, 57 commandes / 64 entrées AP20. Création native de banques `FICON8` : [émetteur](m18_ficon_bank_create_emit.py), [builder déterministe](build_m18_r64_ficon_bank_create.py), [42 tests Gate A PASS](test_m18_r64_ficon_bank_create_gate_a.py) ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43440810232)). [ASC R64 validé archivé](../tests/passed/M18_R64_FICON8_CREATE_01.asc), Gate B WinUAE interprétée **PASS**, avec `RESULT 1` et visuel transparent/opaque confirmé ([rapport](../docs/M18_R64_FICON8_WINUAE_GATE_B_2026-11-13.md)) ; Compiler C à la fin M18. **R63 v0.13.8 `LAST_GOOD` reste protégée**.


**Ancienne `LAST_GOOD` : R60 v0.13.5 (historique, non installable actuelle)**, 35 056 octets, SHA256 `00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8`, 54 commandes / 61 entrées AP20, unité V2 32 798 octets. Gates A/B/C WinUAE et [régression complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43382293638), promotion explicitement autorisée. [Test R60 archivé](../tests/passed/M18_R60_IMAGE_REGION_01.asc). R59 0.13.4 reste disponible depuis `build_m17_r59_compact_v2.py` et l'ancien commit Git. L'unique ASC actif actuel est le test R67.

**Suite M18, P0/P1 hôte uniquement :** [audit `F 16 Icon` / `F Paste Icon`](../docs/M18_F16_ICON_AUDIT.md), [modèle d'icônes indexées](m18_icon_atlas_model.py), [tests hôte](test_m18_icon_atlas_model.py). La suite exige une vérification de la commande historique avant une signature native. CBlock pixel-exact reste prévu dans M18, **avant** l'optimisation 68020+ et `c2p.library`. Aucune nouvelle bibliothèque créée. **Pont AGAPIC vers Fast Icon :** [convertisseur hôte](m18_ficon16_convert.py), [tests d'intégrité et alpha](test_m18_ficon16_convert.py). Source indexée réordonnée en slots 1..N sans destruction de la couleur ni du masque compatible. **P1 source originale :** [audit des Fast Icons Unity](../docs/M18_FICON16_SOURCE_P1.md), [moteur de référence CPU / mots Blitter](m18_ficon16_model.py) et [tests hôte](test_m18_ficon16_model.py). Le nom exact Unity est `Paste F Icon`, avec 16×16, 8 plans et masque couleur zéro, différent du nom Turbo `F Paste Icon` ; aucune vitesse Amiga mesurée.

## M18 / R60 — rendu natif AGAPIC par sous-rectangle, Gates A/B/C PASS

**À l'époque, bibliothèque officielle `dist/AMOSPro_AGA.Lib` : R60 v0.13.5 (historique)**, 35 056 octets, SHA256 `00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8`, 54 commandes / 61 entrées AP20, V2 32 798 octets. Nouveau `Aga Image Region` (8 arguments). [`m18_image_region_emit.py`](m18_image_region_emit.py) (2 012 octets 68000), [builder](build_m18_r60_image_region.py), [test M68000](test_m18_r60_image_region.py) : **86 cas CPU Gate A PASS** ([run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43318155860)) et reconstruction déterministe. **Gates B/C WinUAE PASS sur l'ASC R60** (captures auteur du 13/11/2026, `RESULT 1`, `CLOSE RETURNED` ; [régression complète de pré-release PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43382293638) sur commit exact `a8b14bc`) ; [ASC R60 archivé](../tests/passed/M18_R60_IMAGE_REGION_01.asc), `LAST_GOOD` R60 identique au binaire installable. [Rapport](../docs/M18_R60_IMAGE_REGION.md).

## M18 / P0 — atlas AGAPIC v1, modèle hôte (pas de bibliothèque)

[`m18_agapic_atlas_model.py`](m18_agapic_atlas_model.py) propose le rendu partiel par ligne d'une seule banque AGAPIC v1, avec sélection de frames de grille sans allouer une image intermédiaire. [`test_m18_agapic_atlas_model.py`](test_m18_agapic_atlas_model.py) vérifie pixels, masques, clipping, profondeur et erreurs sans écriture. **Ce modèle P0 Python n'est pas une Gate A native ni une Gate B/C WinUAE.** Il n'a pas ajouté de bibliothèque ; R60 est désormais la `LAST_GOOD` officielle. [Contrat](../docs/M18_AGAPIC_ATLAS_P0.md).

## Historique R57 — code RastPort (ancien test archivé)

**R57 à son checkpoint historique :** [ancienne référence figée dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/5f29d78e65b666f7260f5a32e28bd4e8bcf59a4a/dist/AMOSPro_AGA_LAST_GOOD.Lib), 32 980 octets, SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`, monolithe 30 780 octets. [`tests/passed/M17_R57_RAST_FILL_01.asc`](../tests/passed/M17_R57_RAST_FILL_01.asc) conserve l'ancien test, alors actif, fin `Do / Wait Vbl / Loop`. **Gates A CPU/CI PASS** ([run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43286230339)), **B AMOS interprété/WinUAE PASS** et **C AMOS Compiler/WinUAE PASS** (captures utilisateur : `RESULT 1`, erreurs 0, `CLOSE RETURNED`, pas de Guru). L'arrêt interprété à la ligne 169 dans `Wait Vbl` est volontaire, sur la boucle d'attente. **D physique non testée**.

Générateur `tools/build_m17_r57_rastport.py` : remplacera en mémoire le helper R55 de 620 octets par RastPort R56 de 580 octets + 40 NOP ; aucun autre binaire écrit. Test natif `tools/test_m17_r57_rastport.py` ; binaire courant vérifié par `python -B tools/build_aga_current.py --verify`. Le binaire R56 a subi le Guru compilé `8000000B` ; cette architecture de placement a désormais **PASS en compilé sur le test courant R57** et sur le **benchmark V2 compilé** (Fill médiane 41 ticks, Clear médiane 58 ; R55 : 54/115, gains en temps **24,1 % / 49,6 %**). [Mesures](../benchmarks/RESULTATS_32C_R57_COMPILER_2026-11-12.md). Le mécanisme exact du Guru R56 n'est pas prouvé.

**R54, ancienne `LAST_GOOD` à l'époque, archivée**, SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`. Seule branche `main`, aucun autre livrable actif.

## Historique — R53 capture et sondes R47–R52

Lors de la préparation de R53 0.12.8, `python -B tools/build_m16_capture.py` reconstruisait la candidate en mémoire ; l'option `--publish` concernait cette version, **pas la R54 actuelle**. À cette époque, `LAST_GOOD` était encore R46 C1. Sources de cette étape : `amos_main_abi.py`, `m16_capture_emit.py`, `m16_capture_r47_core_emit.py`, `compiler_relocation.py`, fixture `tests/fixtures/amos_main_declarations.json`. [Preuves historiques](../docs/M16_MAIN_LINKAGE_FIX.md).

Les builders et sondes R47–R52 sont conservés pour la reproductibilité, sans servir de base courante. Les paragraphes suivants décrivent des états **historiques**, non des candidates à installer aujourd'hui.

**Diagnostic temporaire R48 (`Aga Image Capture`) :** `python -B tools/test_m16_r48_token_probe.py` et `python -B tools/build_m16_r48_token_probe.py`. Reproduction contrôlée de la signature R47 à 6 paramètres et de sa taille 32 012 octets, mais routine sans effet de bord. [Binaire expérimental](../dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib) · [procédure](../docs/M16_R48_TOKEN_ABI_PROBE.md). **CI/CPU Gate A PASS, WinUAE Gate B non testée, aucune capture réellement implémentée par R48.** R46 C1 était encore officielle et `LAST_GOOD` à cette date (état historique).

**M16 Capture (modèle hôte historique, avant la R53 validée) :** `python -B tools/test_m16_agapic_capture_model.py` valide l'extraction planaire, le masque, la compression AGAPIC v1, le refus des captures hors écran et des numéros de banque déjà occupés et le repli mémoire simulé. **Ce test ne valide ni le code 68000, ni AMOS interprété, ni le Compiler ; R46 C1 était `LAST_GOOD` lors de cette étude.** Voir [contrat](../docs/M16_AGAPIC_CAPTURE_DESIGN.md).

## CI : vérification quotidienne rapide / régression complète manuelle

- **Sur chaque push/PR concerné :** [Artifact integrity](../.github/workflows/artifact-integrity.yml) vérifie les SHA256 et HUNK de **toutes les archives** sans exécuter leurs anciens builders, l'AP20 Compiler-safe courant, le build courant, les régressions de relocation, API/exemples et les tests de développement M16/R47. Lanceur léger : `python -B tools/verify_fast.py`.
- **Sur demande, avant promotion ou livraison Aminet :** [Full artifact regression](../.github/workflows/artifact-regression-full.yml), à lancer manuellement dans **GitHub Actions** sur le commit à publier. Ce workflow conserve **la totalité des anciens tests et reconstructions historiques**, l'export strict du code natif et les vérifications exhaustives, sans tourner à chaque push.
- Les workflows R33–R38 restent archivés et déclenchés seulement par modification de leurs fichiers respectifs ou manuellement. **La rapidité de la CI ne réduit pas le contrat de validation des nouvelles commandes ni les Gates B/C/D.**
- **Ne pas confondre :** cette séparation diminue le temps des workflows GitHub, pas le temps d'exécution des programmes sur Amiga. Aucun binaire ni archive historique modifiés par cette optimisation.

## Construction Compiler-safe — R60 promue, R46 C1 figée

**Officielle : R60 v0.13.5**, [bibliothèque installable](../dist/AMOSPro_AGA.Lib) et [`LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) identiques à l'octet près, **35 056 octets**, SHA256 `00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8`, Gates A/B/C et [régression complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43382293638), promotion autorisée. **R59 v0.13.4** est l'ancienne référence, reproductible avec [`build_m17_r59_compact_v2.py`](build_m17_r59_compact_v2.py) et conservée au [commit historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/3f7957632781e06816a1019fae24a4cd7eb58aac/dist/AMOSPro_AGA_LAST_GOOD.Lib). R57 et R46 C1 restent des checkpoints historiques.

**Vérifier l'officielle et son pont :**

```sh
python -B tools/build_aga_current.py --verify
python -B tools/test_aga_compiler_bridge_r46.py
python -B tools/test_compiler_relocation.py
python -B tools/verify_artifacts.py
```

`build_aga_current.py` vérifie la reproductibilité de R59 **et** celle de R46 C1 depuis son archive. Il ne réécrit aucun binaire. Les anciens scripts R40–R46 restent dédiés aux références historiques.

**Pour toute candidate postérieure à R60**, partir du `LAST_GOOD` V2 en vigueur : déballer les parties natives avec `compiler_bridge_v2_probe.unwrap_native_parts_v2()`, modifier uniquement des fonctions auditées dans un builder reproductible, puis terminer avec `wrap_native_ap20_v2()`. Vérifier AP20, ABI, offsets non signés, source strict, Gate A CPU et Gate B/C WinUAE avant toute promotion. Ne jamais appliquer automatiquement l'enveloppe V1 à un binaire V2.

**Limite de taille du V2 :** bloc Compiler R59 de **30 782 octets** ; borne théorique de l'unité **65 534 octets** (compteur WORD AMOS Compiler). La routine témoin R58 à 40 000 a été validée en compilé ; la borne supérieure de 65 534 octets reste une hypothèse de format, pas une validation WinUAE. Ne pas extrapoler les performances ni le comportement mémoire sans tests.

[Instructions impératives](../EXTENSION_SOURCE_RULES.md) · [diagnostic M17](../docs/M17_BLITTER_DIAGNOSTIC.md) · [relocalisation C1 historique](../docs/GATE_C_R46_MONOLITH_CANDIDATE.md). Travail exclusivement sur `main`, archives et `tests/passed/` immuables.

## Historique : M16/R46 native avant promotion C1

**R46 native validée Gates A/B le 12/11/2026 puis remplacée comme binaire officiel par C1** : [archive R46 native figée](../dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib), 29 288 octets, SHA256 `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580`. [ASC WinUAE exact](../tests/passed/M16_R46_IMAGE_DRAW_01.asc) (4 240 octets, blob `83eff57323b1cacd0ea58a131ef1ebcec079eceb`) archivé ; aucun ASC courant. Pour préserver les builds reproductibles, les builders historiques R40–R45 et le prototype expérimental Compiler restent ancrés sur l'archive R44 figée. Gates C/D non validées.

### Historique de la candidate R46 avant validation WinUAE

**R46 v0.12.1 :** [émetteur 68000 R45/R46](m16_image_draw_r45_emit.py), [builder R46](build_m16_image_draw_r46.py), [tests CPU R46](test_m16_image_draw_r46.py) (**258 scénarios natifs PASS**), [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43221899949), [rapport](../docs/M16_R46_FLAGS0_FIX.md). Le correctif accepte les flags natifs **0/1/3** observés après `Load` d'une banque DATA ABK. [Binaire courant R46](../dist/AMOSPro_AGA.Lib), 29 288 octets, SHA256 `5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580`. [Test courant R46](../tests/current/M16_R46_IMAGE_DRAW_01.asc), **Gate B NON TESTÉE**. R45 défaillante, 29 280 octets, reste [en archive](../dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib), [ASC R45 original en échec](../tests/failed/M16_R45_IMAGE_DRAW_01.asc) gelé. **R44 `LAST_GOOD` intacte.**

### Historique M16/R45 — Gate B WinUAE FAIL, archive figée

- Codec [m16_agapic.py](m16_agapic.py) : RLE planaire par ligne en groupes de 16 pixels ; DATA AmBk, profondeur 1..8, masquage 1 bit indépendant et modèle de dessin CPU word-wise.
- Conversion hors Amiga [m16_agapic_convert.py](m16_agapic_convert.py) : PNG palette vers ABK ; masque PNG optionnel, import PNG via Pillow.
- [m16_agapic_sample.py](m16_agapic_sample.py) : banque DATA ABK exemple 64×40×4, numéro 10, masque indépendant et index 0 visible.
- [test_m16_agapic.py](test_m16_agapic.py) : roundtrips, clipping quatre bords, 1/2/4/8 plans, opaque et transparent, tests de données corrompues et garde mémoire.
- **P0 PASS** : 432 roundtrips ABK, 1 344 rendus planaires, 31 rejets invalides, [CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43213818778). [Banque ABK témoin 1 856 octets](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk), [notice](../tests/design/M16_AGAPIC_PREVIEW_README.md), SHA256 56443d5ed29527a21d043b845e70c545402648ef35fa590943cd62818499edaf.
- [Test d'aperçu ABK AMOS](../tests/design/M16_AGAPIC_ABK_PREVIEW_01.asc), **PASS confirmé par capture utilisateur** : banque DATA 10, 1 836 octets, 64×40×4, masque et codec RLE, `ABK FORMAT RESULT 1`. [Rapport détaillé](../docs/M16_AGAPIC_WINUAE_P0_PASS.md). `List Bank` affiche `S: $40413010`, sans marqueur F/C : Fast RAM à confirmer séparément. **P0 ABK WinUAE PASS ; le vrai code CPU R45 est maintenant implémenté, mais son premier rendu WinUAE a échoué (aucune image) et aucune performance 68000 n'est mesurée.** [Contrat proposé R45](../docs/M16_R45_IMAGE_DRAW_CONTRACT.md).

**R45 v0.12.0 archivée, Gate B FAIL :** [émetteur](m16_image_draw_r45_emit.py), [builder historique](build_m16_image_draw_r45.py), [tests natifs R45](test_m16_image_draw_r45.py) (127 scénarios CPU PASS). Sous WinUAE, flags natifs 0 de banque DATA chargée rejetés : tous les `Aga Image Draw` retournent 0. [Archive R45 figée](../dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib), SHA256 `0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7`. Ne pas assimiler Gate A à Gate B.

## M15bis/R44 — Aga Mouse Cursor, Gates A CPU/CI et B WinUAE PASS

**Outils :** `m15bis_cursor_r44_emit.py`, `build_m15bis_cursor_r44.py`, `test_m15bis_cursor_r44.py`. **516 cas CPU 68000 PASS**, dont 500 bascules de curseur, allocation unique 72 octets Chip, ABI, protections des quatre fermetures et nettoyage ordonné `ClearPointer` → `CloseWindow` → `FreeMem`, export 68000 strict et [CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43209272738). Test curseur WinUAE `RESULT 1`, `CLOSE RETURNED`, Chip DROP 0, et [exemple interactif M15/M15bis](../examples/m15_2d_cursor.asc) confirmés par utilisateur. **R44 `AMOSPro_AGA.Lib` = `LAST_GOOD` = archive versionnée**, 27 460 octets, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`, **49 commandes AP20 / 55 segments**. [Test d'origine archivé](../tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc) sans retouche, `tests/current/` sans ASC actif. **R43 est figée dans son archive**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`. Gates C/D non testées. [Clôture](../docs/M15_M15BIS_R44_CLOSURE.md).

## M15/R43 — Aga Circle (archive historique)

La bibliothèque R43 v0.11.4 et ses 436 tests CPU/CI + validation WinUAE restent conservés dans `dist/experimental/`. Le test R43 original reste dans `tests/passed/`. Les sections R36 et antérieures ci-dessous sont historiques.

## R36 0.10.8 — Aga Palette Cycle : Gates A CPU/CI et B AMOS/WinUAE PASS (11/11/2026)

**Une seule commande approuvée :** `_OK=Aga Palette Cycle(First,Last,Direction)`, une rotation RGB32 complète par appel (+1 : dernière couleur vers premier index, -1 : inverse), indices inclus `0<=First<Last<256` dans les pens logiques/ColorMap de l'écran AGA Intuition privé indexé. Un `GetRGB32`, permutation exacte des triplets 32 bits, un `LoadRGB32` sur la plage seulement, **aucun `WaitTOF` implicite** ; aucun pixel, banque, fichier ou couleur hors plage touché. Scratch Exec public `8+12*N` (max 3 080 octets) libéré. Succès 1, invalides/refus atomiques 0 ; AMOS pilote la cadence. [Contrat technique R36](../docs/M13_PALETTE_CYCLE_R36.md).

**Gate A CPU/CI PASS :** **106 scénarios natifs CPU 68000 PASS**, export source 68000 strict PASS, [CI candidate complète 38/38 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064975345), **42 commandes AP20**.

**Gate B interprété AMOS/WinUAE PASS — capture utilisateur :** quatre bandes affichées avant 20 rotations à huit VBL d'intervalle. `OPEN 1 DB 1 DRAW 1 1 1 1`, `CYC20 1 RESTORED 16711680 16776960`, `FWD 1 COLOR 16776960 16711680 65280 255`, `REV 1 RESTORE 16711680 16776960`, `NEG 1 COLOR 65280 16711680 POS 1`, `RESET 16711680 16776960`, `BADFIRST 0 BADEQ 0 BADORDER 0`, `BADLAST 0 DIR0 0 DIR2 0 DIRN 0`, `AFTERBAD 16711680 NOSCREEN 0`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin AMOS normale **ligne 138**. Confirmation utilisateur « fct nickel ! », sans mesure FPS ni durée réelle.

**R36 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`. Archive **R35 0.10.7 préservée intacte**, 21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. [Test R36 original archivé](../tests/passed/M13_R36_PALETTE_CYCLE_01.asc), Git blob `4644236576033f755ac0dc274f6f22f92a2d9201` conservé **sans modification**. **Aucun ASC actif dans `tests/current/`.** Gates C Compiler et D Amiga AGA réel **NON TESTÉES**.

**Suite :** R36 clôturée côté AMOS interprété/WinUAE. Aucun R37 ou autre fonction sans discussion et accord explicite de l'utilisateur. Travailler uniquement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, sans autre branche ni dépôt.

---

## R35 0.10.7 — Aga Fade To White : Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Contrat approuvé — seule fonction ajoutée :** `_OK=Aga Fade To White(vbl)`, durée entière 1..255 VBL (0/négatifs/>255 refusés sans modification), fondu RGB24 bloquant de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **blanc exact**. Une capture source `GetRGB32` si vbl>1, interpolation signée 8.8 et un `graphics.library/WaitTOF` suivi de `LoadRGB32` par VBL, dernière image RGB32 `0xFFFFFFFF` exacte. Pas de banque AGAPAL, pixel ou fichier touché ; HAM/EHB/dual playfield rejetés, ColorMap contrôlée, tampon Exec `8+42*N` octets (max 10 760) libéré. Pas de mesure FPS ni de garantie de temps écoulé en cadence réelle. [Contrat technique R35](../docs/M13_FADE_WHITE_R35.md).

**Gate A CPU/CI PASS :** 50 scénarios natifs 68000 et export source strict PASS, [CI candidate complète 37/37 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057572164), 41 commandes AP20.

**Gate B PASS — capture utilisateur AMOS interprété/WinUAE :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. L'utilisateur a confirmé « c nickel » après le fondu visible de 150 VBL, sans mesure de cadence/FPS.

**R35 promue `LAST_GOOD` à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`. **R34 0.10.6 est préservée dans son archive** (20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`). [Test R35 exact archivé](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc), Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2` inchangé. **`tests/current/` sans aucun ASC actif.** Gates C Compiler/D Amiga AGA réel NON TESTÉES.

**Suite :** R35 clôturée côté WinUAE. Ne pas implémenter d'autre commande (R36 ou autre) sans discussion et accord explicite. Rester strictement sur `main` du dépôt `anthea176/AMOSPro-AGA-Extension`, aucune autre branche ni dépôt.

---

## R34 0.10.6 — Aga Fade To Black : Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Contrat approuvé et unique fonction ajoutée :** `_OK=Aga Fade To Black(vbl)`, durée entière 1..255 VBL (0, négatifs et >255 refusés). Fondu RGB24 **bloquant** de tous les pens logiques de l'écran AGA Intuition privé indexé vers le **noir exact**, un `graphics.library/WaitTOF` et `LoadRGB32` par étape, interpolation signée 8.8 depuis la capture `GetRGB32` ; dernière étape RGB32 nulle sans erreur d'arrondi. Aucune banque AGAPAL nécessaire, aucune écriture pixels, banques ou fichiers. Scratch Exec `8+42*N` octets (max 10 760) libéré. Refus sans effet ; retour 1 succès, 0 échec. Pas de mesure FPS ni garantie de durée réelle exacte sur 68000. [Contrat technique R34](../docs/M13_FADE_BLACK_R34.md).

**Gate A PASS :** 48 scénarios CPU natifs 68000 et export source strict PASS, [CI de publication complète 36/36 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053552010), 40 commandes AP20.

**Gate B PASS — capture utilisateur WinUAE/AMOS interprété :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `SAME 1 SAME28 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 113**. L'utilisateur confirme « nickel » sur la démonstration visuelle du fondu 150 VBL ; cadence/FPS non mesurés.

**Promotion R34 à l'octet près :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib`, **20 752 octets**, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`. R33 0.10.5 reste figée dans son archive (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`). Le [test exact R34 archivé](../tests/passed/M13_R34_FADE_TO_BLACK_01.asc) est conservé **sans modification** (blob Git `5fe2f819048cd3706eedaf363f3415a00270406a`). **Aucun ASC actif dans `tests/current/`**. Gates C Compiler/D Amiga AGA réel **NON TESTÉES**.

**Suite :** aucune nouvelle fonction implémentée ; discuter et approuver un nouveau contrat (par exemple Fade To White) **avant** tout codage. Rester exclusivement sur `main`, pas d'autre branche ni de dépôt sans demande explicite.

---
## R33 0.10.5 VALIDÉE — Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Nouvelle fonction :** `_OK=Aga Fade To Bank(Start(bank),index,vbl)`. Fondu RGB24 **bloquant** sur 1..255 VBL ; `WaitTOF` puis `LoadRGB32` par image, interpolation 8.8 signée, **dernière image RGB24 exacte**. Uniquement les pens 0..compte-1 sont modifiés ; banques/pixels et pens supérieurs restent inchangés. `vbl=0` refusé ; pour une application immédiate utiliser `Aga Palette Bank Apply`. Requiert une banque DATA AGAPAL **vivante** (`Start(bank)` réel), une palette non vide et un écran AGA indexé privé. Scratch Exec temporaire `8+42*N` (10 760 octets max), libéré. Les VBL ne garantissent pas une durée réelle stricte si le calcul dépasse une trame.

**Gate A :** 51 scénarios CPU natifs 68000 PASS, export source 68000 strict PASS, **[CI de publication 35/35 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43045308067)**, 39 commandes AP20.

**Gate B fonctionnelle PASS — capture utilisateur WinUAE/AMOS interprété :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `FADE0 1 GREEN 65280`, `FADE1 1 BLUE 255 SAME 1 255`, `PART 1 PEN3 660510 PEN28 16711680`, `BAD0 0 BAD256 0 BADNEG 0`, `BADINDEX 0 EMPTY 0 BADSIZE 0`, `AFTERBAD 16711680 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 BLUE 255`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 141**. Le test confirmait les couleurs finales et les rejets, **pas la qualité visuelle ni la fluidité du fondu** : son `Aga Swap` et `Amos To Back` étaient exécutés APRÈS les transitions, et celles-ci duraient surtout 12/1/2 VBL. **Démo distincte** [`examples/fade_to_bank_r33.asc`](../examples/fade_to_bank_r33.asc) : affiche d'abord trois grandes bandes, puis rouge → vert → bleu → rouge en 150 VBL avec des pauses. Démo **validée visuellement sous WinUAE par l'utilisateur le 11/11/2026 : fondu visible et fonctionnel**, sans mesure de cadence, FPS ou durée réelle.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33 `dist/experimental/AMOSPro_AGA_M13_v0.10.5_AGAPAL_FADE_TO_BANK_R33.Lib`, **20 208 octets**, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, strictement identiques. R32 préservée intacte en archive (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). ASC fonctionnel archivé à l'octet près : [`tests/passed/M13_R33_AGAPAL_FADE_01.asc`](../tests/passed/M13_R33_AGAPAL_FADE_01.asc). Aucun ASC actif dans `tests/current/`. Gates C (Compiler) et D (Amiga AGA physique) **NON TESTÉES**.

**Suite :** observation visuelle positive enregistrée ; ne pas prétendre à une mesure de fluidité, FPS ou cadence sans instrumentation. Toute prochaine fonction doit être discutée et approuvée avant le codage ; mettre à jour les deux README et rester strictement sur `main`, sans autre branche/dépôt.

---
## R32 0.10.4 VALIDÉE — Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Fonction ajoutée seule :** `_OK=Aga Palette Bank Apply(Start(bank),index)` applique une palette RGB24 AGAPAL non vide (1..256 couleurs) à l'écran AGA privé par `graphics.library/LoadRGB32`, immédiatement sans VBL implicite. Retour entier 1/0, aucun changement des banques/pixels, seuls les pens 0..compte-1 remplacés. Exiger un vrai `Start(bank)` d'une banque DATA vivante, jamais un numéro brut ou une adresse périmée.

**Gate A :** 136 scénarios CPU 68000 PASS, export source 68000 strict PASS, [CI candidate 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960).

**Gate B PASS — capture utilisateur de `M13_R32_AGAPAL_APPLY_01.asc` :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, et fin propre `End of program at line 161`. PASS limité à ce scénario AMOS interprété/WinUAE ; Compiler et vrai Amiga AGA non testés.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib`, **19 244 octets**, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894` (octet pour octet). R31 0.10.3 est préservée en archive versionnée (18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`). ASC validé archivé **sans modification** dans [`tests/passed/M13_R32_AGAPAL_APPLY_01.asc`](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc). **Aucun ASC actif** dans `tests/current/`. Gates C Compiler/D matériel réel **NON TESTÉES**.

**Suite :** aucune fonction Import/Fade/Cycling sans échange et accord explicite sur son contrat ; travailler seulement sur `main`, aucun autre dépôt ni branche.

---



**Outils R32 :** `m13_agapal_apply_r32_emit.py`, `build_m13_agapal_apply_r32.py` (base archive R31), `test_m13_agapal_apply_r32.py` (136 scénarios CPU PASS). Gate B AMOS interprété/WinUAE PASS, test ASC archivé ; R32 est `LAST_GOOD`.

**CI candidate R32 :** [34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960). La promotion actualise les assertions sur `LAST_GOOD` sans modifier les archives ni le code 68000.

## R31 0.10.3 VALIDÉE — AGAPAL Capture WinUAE PASS (11/11/2026)

**Gate A :** 107 scénarios CPU 68000 PASS, export 68000 strict PASS, [CI candidate 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027906298). **Gate B AMOS interprété/WinUAE : PASS** sur `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED` et fin propre. **Gates C Compiler / D matériel réel NON TESTÉES**.

**ABK utilisateur inspecté :** `R31_AGAPAL_CAPTURE.ABK` (6 244 octets) = `AmBk` + `AGAPAL` v1 6 224 octets, 8 emplacements, 0/1 contenant 256 couleurs RGB24 (pen 28 bleu/rouge), 2 à 7 vides, pens 3/224 préservés. SHA256 du fichier fourni : `7a3162969b0d700287ae0852872811dae072c19720a794beb8818d01b93f6cd9`.

**R31 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive versionnée R31, 18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`. Archive R30 conservée, inchangée. ASC de test **archivé octet pour octet** (Git blob `0196fc1ba730345a926f444691be80c16a7fb89c`) dans `tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`. [CI de promotion 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43029502969). Pas d'autre commande avant discussion et accord utilisateur.

---


## R30 0.10.2 — AGAPAL Bank Init validée Gate B AMOS/WinUAE

**Gate B PASS confirmé par capture utilisateur le 11/11/2026 :** `INIT 1 REINIT 1`, `HEADER AGAPAL V 1 COUNT 8`, `OFFSET0 80 OFFSET7 5456`, `BAD0 0 BAD257 0 BADSIZE 0`, `SENTINEL 99 ZERO 0`, `ABK RESTORED AGAPAL SIZE 6224`, `REST0 80 REST7 5456 INDEX 1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Fonction `_OK=Aga Palette Bank Init(Start(bank),N)` validée sur le scénario : banque DATA AMOS et rechargement ABK natif, aucun changement d'écran. **Gates C Compiler et D Amiga physique : non testées**.

**R30 promue :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.2_AGAPAL_BANK_INIT_R30.Lib`, **17 824 octets**, SHA256 `446f00cb6d8d09ce3085a51f8d182be55ae97a2c1eb43f10996009a7c8a4af2e`. Archive R29 conservée sans changement. Test corrigé archivé **sans modification**, blob Git `646aa30fb61dfb2ff6b9f5bc5dfe47d8365b2964` : [`tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc`](../tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc). `tests/current/` ne contient plus de test actif. Gate A 39 cas 68000 et [CI 32/32 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43024446890). CI de promotion **32/32 PASS**.

**Rappel :** l'erreur `Type mismatch` du premier essai était dans l'ASC de test ; elle a été corrigée en remplaçant `_STILL` par `_STILL$`. La R30 binaire n'a pas changé. Capture/import de palettes, fades et cycling sont encore **à discuter individuellement avant programmation**.

---




## R29 0.10.1 VALIDÉE — Gate A + Gate B AMOS/WinUAE PASS, 11/11/2026

**Preuves utilisateur :** test `M13_R29_PALETTE_SAVE_01.asc` exécuté sous AMOS interprété/WinUAE : `OPEN 1 DB 1`, `DRAW 1 1 1 1`, `SAVE1 1 SAVE2 1 LOAD 1`, `BEFORE 65280 BLACK 0 AFTER 16711680`, `OTHER 795192 BLUE 128 SWAP 1`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. L'utilisateur confirme également l'ouverture de la palette IFF produite avec ses **256 couleurs dans Cloanto Personal Paint (PPaint)** ; le fichier ne contient pas de pixels `BODY`. Cela établit l'interopérabilité **pour ce fichier et cet essai**, pas tous les éditeurs IFF.

**Promotion obligatoire :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.1_PALETTE_SAVE_R29.Lib`, **R29 0.10.1**, 17 472 octets, SHA256 `fa00e153a12b32f1f1ee22435e46acc4cf42dd61bdf540de121071b040cd99c1`, octet pour octet. L'archive R28 est figée et conservée. Le fichier de test original (Git blob `b80baabe5533288cac3285a78c232827cce94085`) est déplacé **sans modification** dans `tests/passed/M13_R29_PALETTE_SAVE_01.asc` ; **aucun `.asc` actif** dans `tests/current/`.

**Validation :** Gate A CPU 68000 **49 scénarios PASS**, [CI R29 avant promotion **30/30 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43016176793) ; Gate B interprété/WinUAE **PASS** sur le test et PPaint précités. **Gates C (Compiler) et D (matériel réel) NON TESTÉES**. La validation sous PPaint ne démontre pas l'affichage des pixels puisque le format est volontairement sans `BODY`.

**Suite M13 :** fonctions de banques de palettes (Fast RAM privilégiée) et fades natifs `Aga Fade To Bank/Black/White`, puis cycling. **Avant chaque nouvelle fonction, discuter et valider son contrat avec l'utilisateur ; aucune implémentation anticipée.**

---

**Outils R31 :** `m13_agapal_capture_r31_emit.py` (68000), `build_m13_agapal_capture_r31.py` (candidate reproductible depuis R30), `test_m13_agapal_capture_r31.py` (107 scénarios CPU). R31 en Gate A PASS ; test WinUAE actif, R30 toujours `LAST_GOOD`.

**Outils R30 :** `m13_agapal_r30_emit.py` (68000), `build_m13_agapal_r30.py` (reproductible depuis R29), `test_m13_agapal_r30.py` (39 scénarios CPU). La candidate R30 est à tester sous WinUAE ; R29 reste `LAST_GOOD`.

**Outils R29 :** [`m13_palette_save_r29_emit.py`](m13_palette_save_r29_emit.py) (routines 68000 `Aga Palette Save`), [`build_m13_palette_save_r29.py`](build_m13_palette_save_r29.py) (builder reproductible mémoire depuis R28), [`test_m13_palette_save_r29.py`](test_m13_palette_save_r29.py) (49 scénarios CPU natifs et roundtrip R28). La CI couvre R29 et les régressions R28–R10.


## R28 validée — 11/11/2026

M13/R28 0.10.0 : Gate A 159 cas 68000 PASS, CI précédente 29/29 PASS ; Gate B AMOS interprété/WinUAE PASS sur la capture M13-R28-PALETTE-01 du 11/11/2026. Résultats : OPEN/DB/IFF CMAP/SET/DRAW/SWAP = 1 ; BAD 0 BADG -1 ; PEAK 16254720 ($F80700), FINAL 65280 ($00FF00), FADEERR 0, CLOSED -1, RESULT 1, CLOSE RETURNED. Le test AMOS sélectionne un IFF sans que son chemin soit connu depuis la capture ; la compatibilité d'un export palette seule PPaint/DPaint réel n'est donc pas établie. Le résultat numérique n'atteste pas à lui seul l'observation visuelle complète des 64 transitions. Gate C Compiler et Gate D Amiga réel non testées.

**Bibliothèques :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` sont des copies binaires identiques de l'archive `dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib` : 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c`. R27 reste figée dans `dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib` (SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`). Test original déplacé octet pour octet : `tests/passed/M13_R28_PALETTE_01.asc`; aucun test ASC actif.

**Suite autorisée M13 :** palette sauvegardable au format standard IFF FORM ILBM/CMAP, sauvegarde/restauration, fade natif, puis cycling ; incréments séparés et Gate A avant toute nouvelle candidate. M14 fontes et M15 dessin 2D restent ultérieurs.

---

**Descriptions de prévalidation R28 et antérieures conservées ci-dessous pour historique ; elles ne reflètent pas la bibliothèque actuelle.**

## M13 — R28 0.10.0 standard IFF palette (Gate A CPU 159 PASS ; Gate B non testée)

- [`m13_palette_r28_emit.py`](m13_palette_r28_emit.py) : charge CMAP sans modifier BODY, `Palette Set` par `LoadRGB32`, `Palette Get` par `GetRGB32` ; contrôles ColorMap/count/bitplanes, RGB8 et modes HAM/EHB.
- [`build_m13_palette_r28.py`](build_m13_palette_r28.py) : builder **en mémoire** depuis l'archive R27 WinUAE-PASS, 3 fonctions AP20 ajoutées en fin de HUNK, ancien code conservé ; `--emit-base64` pour audit après PASS.
- [`test_m13_palette_r28.py`](test_m13_palette_r28.py) : **159 cas CPU 68000 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43004699618)) ; IFF palettes seules `FORM ILBM/CMAP` avec ou sans BMHD/CRNG, IFF images ordinaires sans écriture BODY, ABI, RGB32, HUNK AP20 et nettoyage des ressources.
- [Contrat M13/R28](../docs/M13_PALETTE_R28.md) · [candidate prête à l'emploi : `dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) · [archive versionnée](../dist/experimental/AMOSPro_AGA_M13_v0.10.0_PALETTE_BASE_R28.Lib), 16 208 octets, SHA256 `ddda516ba6e155e07381318ba2147320c06f8bbb5256b4a20fe3d6873be2891c` · [test WinUAE actif](../tests/current/M13_R28_PALETTE_01.asc). **R28 Gate B non testée ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R27 0.9.3 validée WinUAE.** Une version validée est immédiatement promue en `LAST_GOOD` après confirmation utilisateur. Sauvegarde IFF standard, fades et cycling restent à réaliser.

## M12 — R27 Safe Blitters (Gate A CPU/CI 403 cas PASS et Gate B AMOS/WinUAE 40 swaps PASS)

- [`m12_blit_safe_r27_emit.py`](m12_blit_safe_r27_emit.py) : même garde `GetMsg(SafePort)` non bloquante avant DMA dans Copy/Fill, préserve `D6`/ABI et le bit Disp.
- [`build_m12_blit_safe_r27.py`](build_m12_blit_safe_r27.py) : builder en mémoire depuis R26 archivée ; **R27 0.9.3 est maintenant `dist/AMOSPro_AGA_LAST_GOOD.Lib`**, octet-identique à [son archive versionnée](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), 14 252 octets, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe` ; 31 commandes, neuf segments modifiés. **`dist/AMOSPro_AGA.Lib` = R28 candidate**, sans sous-répertoire.
- [`test_m12_blit_safe_r27.py`](test_m12_blit_safe_r27.py) : **403 scénarios CPU 68000 PASS** dont Copy/Fill/Clear Safe/Disp, aucun DMA après rejet, ABI, BSR Clear et relocations clavier/souris R23 ; [CI finale 28/28 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997575220). **Gate B AMOS/WinUAE PASS** sur [40 swaps originaux archivés](../tests/passed/M12_R27_SAFE_BLIT_01.asc).
- [Rapport M12, captures et réserves](../docs/M12_SAFE_BLITTER_R27.md) · [test WinUAE archivé sans modification](../tests/passed/M12_R27_SAFE_BLIT_01.asc) : `DONE 40 C 14 F 13 P 13`, `RESULT 1`, clignotement des rectangles. **C'est la dernière version Gate B PASS, donc `LAST_GOOD` R27.** Le test M13 R28 est maintenant le seul actif et attend Gate B ; Compiler et Amiga réel non testés.


## M11 — R26 `Aga Text` 0.9.2 : validation WinUAE initiale et multi-swap 40 images PASS

- [`build_m11_text_r26.py`](build_m11_text_r26.py) : builder **en mémoire** reproductible depuis R25 figée ; **à la clôture de R26**, la candidate `dist/AMOSPro_AGA.Lib` était égale à [l'archive R26](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. Il ne modifie aucun binaire en étant exécuté.
- [`m11_text_r26_emit.py`](m11_text_r26_emit.py) : nouvelle routine 68000 `TextExtent` + `InitRastPort` + `Text`, sécurité Safe/Disp non bloquante sans `WaitPort` ni `ReplyMsg`.
- [`test_m11_text_r26.py`](test_m11_text_r26.py) : **64 cas CPU 68000 PASS** (ABI, back buffer, Safe/Disp, clipping) lors de la [CI R26 complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42922291061). **Gate B AMOS/WinUAE PASS** sur le [test R26 original archivé](../tests/passed/M11_R26_AGA_TEXT_01.asc), texte vert visible sur fond bleu, `RESULT 1`, fermeture propre.
- [Contrat et résultats R26](../docs/M11_TEXT_R26.md) · [test texte initial PASS](../tests/passed/M11_R26_AGA_TEXT_01.asc) · [test multi-swap PASS archivé](../tests/passed/M11_R26_SAFE_SWAP_02.asc). **40 alternances A/B confirmées**, `PROBE0 39 SWAP0 0`, toutes erreurs nulles, `RESULT 1`. `tests/current/` ne contient aucun `.asc` après archivage du test R27. La R26 et les archives R25/R24/`LAST_GOOD` R10 restent inchangées ; Compiler, matériel réel et longue durée non testés.

### Historique de conception M11 (avant l'implémentation R26 ; non applicable à l'état courant)


- Le diagnostic [`M11_R25_AMOS_TEXT_01.asc`](../tests/historical/M11_R25_AMOS_TEXT_01.asc), qui supposait que `Text` AMOS viserait notre écran Intuition AGA, a été **écarté avant exécution WinUAE** et classé historique sans modification des octets.
- **Aucun test actif** dans `tests/current/`. La prochaine étape est une inspection en lecture seule de la source R25 : `BitMap` du back buffer, `RastPort`, `Aga Swap` et cycle de vie. Envisager `graphics.library/Text` seulement avec une cible graphique explicitement liée à ce back buffer. [Étude](../docs/M11_TEXT_COMPAT.md).
- Aucun builder R26 créé. Binaires R25/R24, `LAST_GOOD` R10 et archives `tests/passed/` intacts.


## M10 — R25 0.9.1 : collisions AABB (Gate A CPU/CI + Gate B WinUAE PASS sur scénario)

- [Émetteur natif 68000](m10_rect_overlap_r25_emit.py) : huit entiers, `D3=bh` et `A3+28`, aucun état/OS, arithmétique signée 32 bits sans `x+w` dangereux.
- [Builder reproductible, sans écriture](build_m10_rect_overlap_r25.py) depuis l'archive validée R24 et [préflight CPU](test_m10_rect_overlap_r25.py) : cas de bords, un pixel, inclusions, tailles invalides, extrêmes, symétrie et non-régression R24.
- [Test AMOS visuel R25 archivé et validé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) · [contrat R25](../docs/M10_RECT_OVERLAP_R25.md). Rectangle bleu fixe, mobile vert/rouge ; `FRAMES 409`, `DRAWERR 0`, `RESULT 1`, fermeture correcte. **Gate A CPU/CI PASS 704 cas** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209)), **Gate B AMOS/WinUAE PASS** sur le scénario utilisateur. Aucun `.asc` actif dans `tests/current/`. CI et contrôle statique ne valent pas validation du Compiler ou du matériel.

## M9 — R24 0.9.0 : Hotspot Hit (Gate A CPU/CI + Gate B WinUAE PASS)

- [Émetteur pur 68000](m9_hotspot_r24_emit.py) : six paramètres, bords fin exclusive, arithmétique 32 bits sans débordement, aucun état ni appel OS.
- [Builder pur R24](build_m9_hotspot_hit_r24.py) : depuis R23 **archivée et validée**, ajout d'une seule entrée AP20 + séparateur `GetP`. `dist/AMOSPro_AGA.Lib` candidate R24 et son archive sont comparées en CI.
- [Test CPU préflight](test_m9_hotspot_hit_r24.py) : contrôles 68000 ABI/A3, frontières, zones superposées, int32, R23 inchangée. **Gate A CPU/CI PASS 402 cas (CI (archive CI privée, run #42908096685)), Gate B WinUAE PASS sur le test R24 archivé.** [Contrat](../docs/M9_HOTSPOT_R24.md) · [test WinUAE exact](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc).

## M8 — R23 0.8.7 : IDCMP clavier/souris (Gate A + B PASS sur scénarios testés)

- [`m8_idcmp_r23_emit.py`](m8_idcmp_r23_emit.py) : dispatcher 68000 non bloquant des messages `IDCMP_MOUSEBUTTONS` et `RAWKEY`, FIFO clavier 16 places.
- [`build_m8_idcmp_r23.py`](build_m8_idcmp_r23.py) : builder **pur**, depuis l'archive R22 PASS, reconstruit la candidate R23 sans écrire les archives. Mode `--emit-base64` réservé à la vérification de l'artifact.
- [`test_m8_idcmp_r23_preflight.py`](test_m8_idcmp_r23_preflight.py) : couverture CPU/emulateur native de la capture des clics courts et de la préservation des touches, sans preuve WinUAE.
- [Contrat R23](../docs/M8_IDCMP_R23.md) · [test WinUAE exact archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc). **Gate A CPU/CI PASS (15 cas, CI (archive CI privée, run #42899343161)), Gate B WinUAE PASS** sur clics rapides, FIFO clavier et Ctrl+C à `_WAITK=Aga Wait Key` avec fermeture Intuition. Archive R22 et `LAST_GOOD` R10 inchangées ; Compiler/hardware/stress non testés.

## M8 — R22 0.8.6 : transitions souris natives (CPU + WinUAE PASS sur scénario)

- `m8_mouse_edges_emit.py` : génération déterministe des routines 68000 `Aga Mouse Pressed/Released`, fronts indépendants et contrôle du focus sans toucher à la file clavier.
- `build_m8_mouse_edges_r22.py` : construction reproductible depuis l'archive R21, deux entrées AP20 nouvelles, petite réinitialisation sur ouverture d'écran ; archives et LAST_GOOD inchangées.
- `test_m8_mouse_edges_r22.py` : tests CPU 68000, ABI, états sticky, clavier intact, focus, refus et réouverture.
- [Contrat R22](../docs/M8_MOUSE_EDGES_R22.md) · [test AMOS validé et archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Gate A/CI PASS (25 scénarios, CI (archive CI privée, run #42893816454)) ; Gate B WinUAE PASS sur capture utilisateur.

## M8 — R21 0.8.5 RMBTRAP (CPU/CI PASS 11 cas ; WinUAE PASS utilisateur)

- `build_m8_rmbtrap_r21.py` : builder depuis R20 archivée, change **un seul octet** de code dans `NewWindow.Flags` de `Aga Screen Open` ; R21 archivée, R22 courante sur `main`.
- `test_m8_rmbtrap_r21.py` : simule CPU 68000 et intercepte les flags transmis à `OpenWindow()`; contrôle régressions des boutons R20 et autres segments immuables.
- [Dossier technique R21](../docs/M8_RMBTRAP_R21.md) · [test AMOS archivé](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc).

## M8 — R20 0.8.4 Mouse Buttons (CPU/CI PASS 21 cas ; WinUAE boutons OK mais menu Intuition défectueux)

- `build_m8_mouse_buttons_r20.py` : nouveau builder depuis l'archive R19 figée, ne modifie que l'entrée 29 (`GetP`) et ajoute l'entrée 30 `Aga Mouse Buttons` ; `dist/AMOSPro_AGA.Lib` R20 figée (builder historique ne réécrit pas la candidate R21).
- `test_m8_mouse_buttons_r20.py` : tests CPU 68000 sous Unicorn (appels input.device simulés, masques, ABI/SP, erreurs, R19 inchangé).
- [R20 boutons](../docs/M8_MOUSE_BUTTONS_R20.md), [test AMOS historique](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc).
- **R19 reste archivée :** ne plus exécuter son builder historique en écriture de `dist/` R20 ; la fonction pure `build()` est conservée pour les tests.

## M8 — R19 0.8.3 Mouse X/Y, PASS CPU/CI et AMOS interprété/WinUAE

- `build_m8_mouse_position_r19.py` — builder historique R19 (archive figée) depuis l'archive R18 figée ; reproduit R19 sans écraser la bibliothèque R21 de `main`.
- `test_m8_mouse_position_r19.py` — 76 cas CPU 68000 **PASS et CI générale PASS** (CI générale #42878271256 (archive CI privée)) : coordonnées signées, 320/640/1280, fenêtres déplacées, écran fermé, écran étranger, ABI D3/D2/A3/SP.
- `test_amos_copper_syntax.py` — contrôle statique étendu aux appels nus des fonctions `Aga Mouse X/Y` ; elles doivent être utilisées dans une expression.
- [`M8_MOUSE_R19.md`](../docs/M8_MOUSE_R19.md), [`M8_STATUS.md`](../docs/M8_STATUS.md) — spécification de l'API et procédure WinUAE.

## M7 — R18 0.8.2 Copper Wait/Move/End, PASS CPU/CI et WinUAE (archivé)

- `m7_copper_contract.py` — API de validation Python pour une liste utilisateur de 64 instructions au maximum : `Clear/Wait/Move/End/On/Off` ; autorise seulement COLOR00..COLOR31, RGB4 et les WAIT bornés. **Aucun code Amiga n'est exécuté.**
- `test_m7_copper_contract.py` — tests de grammaire, limites et erreurs ; **pas une preuve 68000/WinUAE**.
- `test_amos_copper_syntax.py` — vérification automatisée : les fonctions Copper AP20 doivent apparaître dans une expression et non comme instructions isolées.
- `build_m7_copper_raster_r18.py` — builder **historique R18**, régénère uniquement son archive validée ; l'appel direct n'écrase plus la Lib R19 courante.
- `test_m7_copper_raster_r18.py` — 26 scénarios CPU 68000 Gate A PASS (ABI/A3, WAIT croissants, COLOR00..31, CEND, refus de liste active). **Gate B WinUAE PASS** sur le test raster corrigé.
- `build_m7_copper_on_off_r17.py` — builder **historique R17**, ne doit plus écraser le candidat R18 ; conserve sa propre archive.
- `test_m7_copper_on_off_r17.py` — tests CPU Intuition MakeScreen/RethinkDisplay, propriétaires, retour ABI, cas d'erreur, retrait et libération.
- `build_m7_copper_clear_r16.py` — builder **historique R16** depuis R15, désormais limité à la régénération de son archive ; ne doit pas écraser l'actif R18.
- `test_m7_copper_clear_r16.py` — test CPU/ABI 68000, simulation OS, pointeurs Screen, allocation et chemins d'échec ; **ne prouve pas WinUAE**.
- Références : [`M7_COPPER_R18.md`](../docs/M7_COPPER_R18.md), [`M7_COPPER_R17.md`](../docs/M7_COPPER_R17.md), [`M7_STATUS.md`](../docs/M7_STATUS.md), [`M7_COPPER_R16.md`](../docs/M7_COPPER_R16.md) et [`M7_COPPER_DESIGN.md`](../docs/M7_COPPER_DESIGN.md).

## Rappel — M6 R15 validé

La racine de `tools/` conserve les builders, tests CPU et outils génériques utilisés ; les anciennes versions restent dans `obsolete/`.

## M6 — R15 Clear validé sous AMOS interprété/WinUAE

- `build_m6_blit_clear_r15.py` — génère le candidat R15 `dist/AMOSPro_AGA.Lib` et son archive R15 depuis **l'archive R14 figée**, sans modifier les versions validées.
- `test_m6_blit_clear_r15.py` — CPU 68000, wrapper A3+12, BSR vers Fill, contenu pixel par pixel, rejets, non-régression R14 Fill et R13 Copy.
- `build_m6_blit_fill_r14.py` — builder **historique R14**, toujours reproductible depuis R13 archivée ; son exécution en ligne de commande ne doit plus écraser le candidat R15.
- `test_m6_blit_fill_r14.py` — contrôles CPU 68000, bitplanes, couleur, bounds, masques, minterms, ABI et sauvegarde de Copy.
- `build_m6_blit_copy_r13.py` — ancien builder R13, conservé pour reproduire la version **déjà validée** de Copy depuis R12 archivée ; ne pas l'exécuter directement comme livraison active R14.
- `test_m6_blit_copy_r13.py` — CPU 68000 (Unicorn), ABI A3/GetP, géométrie, sélection back buffer, appel BltBitMap et WaitBlit. Ce n'est pas une validation graphique sous WinUAE.
- `.github/workflows/artifact-integrity.yml` — vérifie R15, reconstruit le candidat actif, rejoue les tests CPU R14/R13 et contrôle la protection des archives / `LAST_GOOD`.

## M5 — R12 stable et références

- `build_newscreen_a0_r12.py`, `build_ntsc_pal_r10.py`, `ap20_utils.py`, `audit_ap20.py` : construction et vérification R12/R10.
- `test_newscreen_a0_r12.py`, `test_ntsc_pal_r10.py`, `verify_artifacts.py`, `check_no_blocking_waits.py` : contrôles d'intégrité.
- `validate_ilbm.py`, `build_m5_generic.py`, `build_m5_generic_r2.py`, `m68k_emit.py`, `test_m5_generic.py`, `test_m5_generic_r2.py` : composants génériques IFF/CPU.
- `inspect_winuae_dump.py` : diagnostic WinUAE.

`tools/obsolete/` conserve les anciennes générations. Ne pas promouvoir ni écraser la R10 `LAST_GOOD`. Consulter [les détails du R15 Clear](../docs/M6_BLITTER_R15.md), avec R14 Fill et R13 Copy déjà validés sous WinUAE.
