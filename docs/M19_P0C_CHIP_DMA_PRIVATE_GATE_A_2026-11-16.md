# M19 P0c — staging Chip privé MC68020 : Gate A CPU (16/11/2026)

## Portée réelle

**SOURCE NATIVE PRIVÉE ET TESTÉE SUR CPU020 (Exec/graphics simulés)** ; aucun nouveau token AP20, aucune modification de la bibliothèque installable, aucun résultat WinUAE ou AMOS Compiler pour ce code P0c. Le moteur d'affichage Bob n'est pas encore livré.

- Dépôt autorisé : `anthea176/AMOSPro-AGA-Extension` sur `main`.
- Bibliothèque P0b toujours active : `dist/AMOSPro_AGA.Lib` **82 376 octets**, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`, 82 commandes et 92 entrées AP20.
- Source : [`tools/m19_p0c_chip_stage_emit.py`](../tools/m19_p0c_chip_stage_emit.py), **1 304 octets de code natif déterministe** ciblant **MC68020/68EC020 minimum**.
- Banc CPU : [`tools/test_m19_p0c_chip_stage_native.py`](../tools/test_m19_p0c_chip_stage_native.py) ; **64 scénarios MC68020 sous Unicorn** avec deux placements de code. [CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021013).
- Modèle de géométrie ABK/planar antérieur : [`tools/m19_p0b_chip_dma_model.py`](../tools/m19_p0b_chip_dma_model.py), **9 scénarios HOST PASS**.
- [CI politique CPU et destinations PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43914021170) ; CI de reconstitution P0b et tests 116 scénarios également PASS sur le même HEAD.

## Contrat interne de trois points d'entrée, pas une API AMOS

| Entrée privée | Paramètres natifs | Résultat |
|---|---|---|
| `stage_entry` | A0 = début des seuls pixels/masques planaires AGBO contigus **déjà vérifiés** ; D0 = taille exacte en octets ; A1 = contexte interne privé zéro-initialisé ; D1 = identité du payload AMOS (paire) ; D4 = génération AGBO ; A4 = `GfxBase` pour tout remplacement | D3 = 1 succès / 0 refus ; D2 = 0 |
| `release_entry` | A1 = contexte propriétaire ; A4 = `GfxBase` valide si allocation active | D3/D2 identiques |
| `lookup_entry` | A1 = contexte ; D0 = identité actuelle contrôlée par l'appelant ; D1 = génération actuelle contrôlée | 1 uniquement si la représentation préparée appartient à cette identité/génération |

Contexte **20 octets**, à allouer dans l'état natif privé : pointeur Chip (+0), taille (+4), identité payload (+8), génération (+12), cookie propriétaire `CHIP` (+16). Aucune banque AMOS numérotée auxiliaire.

**Préparation :** avant modification du contexte, le noyau vérifie CPU, paramètres et alignement, plage source déclarée, cohérence de l'ancien contexte, éventuelle allocation Chip précédente ; demande ensuite un **`AllocVec(size, MEMF_PUBLIC|MEMF_CHIP)`**. Il vérifie `TypeOfMem` au premier et au dernier octet du bloc alloué, puis appelle `CopyMem` sur la taille exacte. Si une étape échoue, il appelle `FreeVec` pour libérer la nouvelle allocation, **sans écraser l'ancien contexte**. Une fois les données copiées, le remplacement passe par **`graphics.library/WaitBlit` avant la libération de l'ancienne source**. `release_entry` attend également la fin du Blitter avant `FreeVec`. Aucun `Aga Swap` ni attente Exec non bornée.

Le critère de plage complète repose sur la **garantie `AllocVec(MEMF_CHIP)` pour tout le bloc contigu**, plus la vérification `TypeOfMem` aux deux extrémités ; `TypeOfMem` sur deux adresses arbitraires ne prouverait pas à lui seul la continuité d'une banque inconnue. Il est interdit d'exposer au DMA une source non allouée ainsi. `AllocVec`/**`FreeVec`** évite les erreurs d'association de taille de `AllocMem`/`FreeMem`.

**Références vérifiées :**
- [AmigaOS 3.x NDK — AllocMem, MEMF_CHIP](https://developer.amigaos3.net/autodocs/exec.library/AllocMem.html).
- [Table des LVO Exec](https://arisamiga.github.io/amiga-bootcamp/14_references/exec_lvo_table/) : `TypeOfMem=-534`, `CopyMem=-624`, `AllocVec=-684`, `FreeVec=-690`.
- [Graphics — WaitBlit obligatoire avant de libérer une ressource Blitter](https://wiki.amigaos.net/wiki/Graphics_Primitives).

## Tests MC68020 de la Gate A privée

Sous Unicorn CPU modèle `UC_CPU_M68K_M68020`, les services système sont simulés avec destruction volontaire des registres volatils D0/D1/A0/A1 pour détecter les violations ABI. Le test couvre :

- allocation de données alignées, parité exacte des pixels/masques et canaries hors plage ;
- deux emplacements du même code natif pour vérifier les liens PC relatifs ;
- allocation impossible, refus de la mémoire non Chip sur début ou fin, restitution de toute allocation transitoire ;
- remplacement d'une allocation existante, attente Blitter et libération **après** attente ;
- refus lors de remplacement si `GfxBase` est absent ; état original conservé ;
- taille nulle, impaire, excessive ; pointeurs/identités nuls ou impairs ; génération nulle ; contexte corrompu ;
- `lookup` sur identité/génération périmées, `release` sûr/idempotent ; garde CPU si `AFF_68020` absent ;
- conservation des registres préservés et de A7, ABI D3/D2, décodage MC68020 Capstone.

**Résultat effectif : 64 scénarios PASS, code natif 1 304 octets**, logs GitHub Actions du 16/11/2026. **Ceci est une Gate A de noyau privé, non une Gate A d'instruction AMOS complète.**

## Verrous restants avant la nouvelle .Lib ou l'affichage Bob

1. Le **wrapper AMOS/public** doit valider l'intégralité de `AGBO` v1 (métadonnées, offsets, limites et masques), ainsi que la véritable identité de banque AMOS ; il transmettra ensuite uniquement les pixels/masques contigus au helper. Le helper n'accepte pas lui-même une banque ABK brute non validée.
2. Définir l'emplacement, le cycle d'initialisation et le cleanup de la table des **contextes par banque** dans le groupe natif BOBS. Le contexte ponctuel du test n'est pas encore intégré à l'état de la Lib.
3. Chaque dessin devra revalider l'identité et la génération de la banque sélectionnée ; après `Erase`/`Load` ou recapture, ne jamais réutiliser les anciens pointeurs. `Poke` direct dans AGBO non supporté.
4. Revoir la forme exacte de la commande publique `Aga Bob Bank Free N` et des commandes objet/rendu avant l'ajout de tokens ; pas de nouveau token dans ce jalon.
5. Gate A CPU/AP20 de la **candidate complète** puis Gates B WinUAE et C AMOS Compiler réelles sur le nouveau test exact. Le test P0b (Runtime/Compiled PASS) ne valide pas automatiquement ce code P0c.

**Protections :** `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84, `tests/current/M19_P0B_MC68020_MASK_BANK.asc` et tous les tests/archives existants restent inchangés. Aucune promotion, aucun exécutable AMOS P0c.


## Étape suivante : wrapper complet banque AGBO → staging Chip (16/11/2026)

La source [`tools/m19_p0c_checked_bank_stage_emit.py`](../tools/m19_p0c_checked_bank_stage_emit.py) **n'altère aucun octet du préfixe P0b**. Elle ajoute en interne les entrées privées `checked_stage_entry`, `checked_lookup_entry` et `checked_release_entry` ; celles-ci appellent le helper `emit_chip_stage` existant, sans ajouter de token AP20 ni changer la bibliothèque.

**Entrées et garanties testées :** `checked_stage_entry` reçoit `A5=AMOS`, `D3=numéro de banque sélectionnée`, `A1=contexte privé 20 octets`, `A4=GfxBase`. Il interroge `Bnk.GetAdr`, vérifie la tête de liste et le pointeur de sélection, les métadonnées DATA/AGBO et **toutes** les entrées : ID stricts, largeurs et profondeurs 1..8, stride planaire, taille de pixel, masque 1 bit indépendant, offsets contigus et padding. **Une banque vide est valide pour la création, mais ne peut pas être préparée pour du dessin** (aucune source plane à allouer).

Après validation exhaustive, le wrapper transmet la plage contiguë des **pixels/masques seulement** au helper `AllocVec(MEMF_CHIP|MEMF_PUBLIC)`, `TypeOfMem`, `CopyMem` et `WaitBlit` avant libération. `checked_lookup_entry` vérifie que la banque est toujours sélectionnée et que l'adresse/génération du payload correspond au contexte. `checked_release_entry` libère un contexte même si la banque AMOS a été effacée, après attente de fin du Blitter, sans effacer le DATA bank AMOS.

**Gate A privée nouvelle :** [CI 43916465599](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43916465599) : **120 scénarios CPU020 PASS** avec appels AMOS/Exec/graphics simulés et deux déplacements du code (interprété/compilé-like) ; l'unité source reconstruite fait **10 044 octets** et contient le préfixe P0b à l'identique. Dans cette même CI, **64 scénarios** du noyau Chip privé et **116 scénarios** des commandes P0b restent PASS. [Code du banc](../tools/test_m19_p0c_checked_bank_stage_native.py).

**Deux contextes sont réellement testés en parallèle dans le banc**, associés respectivement aux banques AMOS 10 et 11, sans duplication de la source par Bob. Mais ils sont **fournis par le banc** : la table interne allouant/trouvant le contexte d'une banque et son nettoyage global au `Aga Screen Close` ne sont pas encore codés. L'état persistant et le dessin de Bob restent absents.

**Limite d'identité** : le seul couple pointeur AGBO / génération n'élimine pas une réutilisation de même adresse et génération (« ABA ») après `Erase`/`Load`. Le contrat exige une resélection de banque, la gestion propriétaire d'identité sera renforcée dans la future intégration. Modification arbitraire in-place par `Poke` non garantie.

**Statuts** : Gate A CPU d'un **wrapper privé** PASS ; Gate B/C pour ce wrapper **NON TESTÉES**. Pas d'API publique, pas de modification de `dist/AMOSPro_AGA.Lib`, pas de promotion de R84 `LAST_GOOD`, pas de modification de l'ASC validé P0b. La partie `TypeOfMem` et `WaitBlit` est encore exercée sur des services simulés, pas sur les bibliothèques natives WinUAE.

## M19 P0c — registre par banque et nettoyage privé, 16/11/2026

**Source native :** [`tools/m19_p0c_bank_registry_emit.py`](../tools/m19_p0c_bank_registry_emit.py) ; unité déterministe **11 094 octets**, contenant intégralement les préfixes natifs existants P0b et P0c **inchangés octet pour octet**. Nouveau registre strictement **privé** : aucun token AP20, aucune modification de `dist/`, `tests/current/`, `tests/passed/` ou `LAST_GOOD`.

Structure : racine statique PC-relative 8 octets (`A5` propriétaire, `head`), nœuds **32 octets** alloués avec `Exec AllocVec(MEMF_PUBLIC|MEMF_CLEAR)` (next+0, numéro banque+4, contexte Chip 20 octets +8..+27, réservés +28..+31). Les nœuds ne sont **pas** des banques AMOS ; chacun contient le pointeur et le contrat de propriété de la copie Chip allouée séparément. Recherche bornée à **256** nœuds ; accès refusé si une autre identité A5 tente d'utiliser une liste non vide.

**Quatre entrées privées :** `registry_prepare_entry` publie un nœud seulement après validation AGBO + stage Chip ; échec de validation/alloc laisse une entrée précédente intacte et libère un nœud détaché. `registry_lookup_entry` confronte la banque actuellement sélectionnée à l'identité/génération stockée. `registry_free_entry` appelle le helper de libération, qui attend `WaitBlit`, avant de détacher et libérer le nœud Exec. `registry_close_entry` parcourt toutes les banques, libérant même après effacement des banques AMOS, et remet la racine à zéro ; l'appel répété est sans effet. Un échec `WaitBlit`/ownership simulable laisse la ressource encore liée pour permettre un nouvel essai ; cela ne signifie pas un hook de fermeture installé.

**Gate A CPU :** [`tools/test_m19_p0c_bank_registry_native.py`](../tools/test_m19_p0c_bank_registry_native.py), [workflow](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43917996936) : **64 scénarios PASS** dans les deux positions d'exécution en MC68020 Unicorn. Le même workflow donne **120 scénarios PASS** pour le validateur AGBO/Chip, **64 pour le helper Chip** et **116 pour la candidate P0b**. Vérifications des registres A0..A6/D0..D7 sauvegardés (hors D2/D3), A7, canaries, contenu binaire de la copie Chip, deux banques et deux allocations, rollback sur échecs, refresh, propriétaires distincts, libération totale et partielle. Les services Exec/graphics/AMOS restent **simulés**, aucun test sous WinUAE pour ce registre. [CPU/delivery policy PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43918000042).

**À ne pas prétendre livré :** `registry_close_entry` constitue une entrée **à raccorder** depuis le futur code de fermeture de l'écran AGA. La commande **actuelle** `Aga Screen Close` ne l'appelle pas ; aucune fuite n'est donc corrigée dans la Lib P0b par ce seul code. Avant intégration : source officielle du cycle Open/Close, contexte `GfxBase` valide durant cleanup, traitement de l'ABA pointeur/génération après `Erase`/`Load`, contrats de rendu Bob, Gate A AP20 puis Gate B/C réelles. L'ancien workflow indépendant « Artifact integrity » échoue historiquement sur son contrôle du wrapper Compiler et n'est pas une preuve de régression du registre. Il reste à traiter séparément.


## M19 P0c — garde source-native de pré-fermeture, 16/11/2026

[`tools/m19_p0c_screen_preclose_emit.py`](../tools/m19_p0c_screen_preclose_emit.py) ajoute une **entrée privée MC68020**, `screen_preclose_entry`, à l'unité BOBS native P0c après le registre existant, sans modifier un octet de son préfixe. **11 294 octets** au total pour cette unité source-only. Sa signature interne est `A5 = AMOS programme`, retour `D2=0, D3=1/0` ; elle ne fait confiance ni à A4 en entrée ni à un faux GraphicsBase. Le pointeur d'état écran vient de `A5+0x1C8`, et `GfxBase` de `State+8`, après validation du garde CPU et du pointeur d'état via Exec `TypeOfMem` aux deux adresses nécessaires. Si l'état manque avec un registre vide, l'appel est idempotent ; avec un registre actif et GfxBase absent, l'appel refuse et **laisse toutes les allocations en place**. Aucun `WaitPort`, `Aga Swap`, `CloseWindow` ni `CloseScreen` n'est introduit.

**Incident détecté par Gate A puis corrigé** : le premier essai utilisait le même slot de frame pour l'adresse de la fin du contrôle `TypeOfMem(State+8)` et pour `GfxBase`. Lorsque le champ `State+8` valait zéro, ce pointeur temporaire pouvait être transmis comme base graphics.library et entraîner une exception CPU à `0x52004`. Le correctif isole `state_end` du champ `gfx`. Le test garde un cas négatif explicite garantissant le refus **sans appel à `WaitBlit` ni double libération**, avant de rétablir GfxBase et réussir.

**Gate A privée :** [GitHub Actions 43920983278](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43920983278) **PASS**, **42 scénarios CPU MC68020**, modèle Unicorn avec services AMOS/Exec/graphics simulés et deux placements interprété-like/compilé-like. Régressions : 64 scénarios du registre, 120 du validateur AGBO, 64 du helper Chip et 116 P0b PASS. [Banc exact](../tools/test_m19_p0c_screen_preclose_native.py). Les appels destructifs de fermeture AGA sont **simulés**, non issus du code historique réel.

**Audit des entrées AP20 et blocage d'intégration :** le binaire P0b reconstruisible SHA `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9` expose `Aga Screen Close` au **token public n°8**, dont le RBSR V2 cible le **groupe 91** à l'offset **2008**. BOBS est le **groupe 90**. Ces informations sont contrôlées par le banc à partir des tokens/segments de la candidate réelle, sans utiliser d'index de groupe présumé. Le source `src/R88/AMOSPro_AGA_R88_AGA_NATIVE.s` précise lui-même « PARTIAL MC68020 MNEMONIC RESTORATION », « not an installable .Lib », donc **non autorisé comme source de production pour l'injection d'un appel**. Le binaire natif AGA source-audité R88 de la tree a **56 580 octets** : pas de BSR.W inter-groupe à improviser. Un correctif réel devra traiter le dispatch Compiler V2 **et** l'ancienne fermeture/cleanup End, non simplement le helper.

**Bilan sans ambiguïté :** point de pré-fermeture privé **PASS Gate A** ; **raccordement automatique à `Aga Screen Close` = NON RÉALISÉ**, AMOS End = NON RÉALISÉ, Gate B/C **NON TESTÉES** pour P0c ; `dist/AMOSPro_AGA.Lib` et `LAST_GOOD` inchangées. Pas d'ASC supplémentaire ni de nouvelle bibliothèque installable.
