# M19 P2e.0 — Passerelle AMAL mémoire vers Bob AGA (expérimental)

## Décision et portée

Après **P2d Runtime PASS 43/43** (journal utilisateur du 21/11/2026, `PRG_STATE 1`, `ERR 0`, `PROBE_PREALLOC 1`, `CLOSE_RETURNED 1`, `VERDICT PASS` ; SHA256 du journal original `28f7ebfff3d77e7cc65469df3c246f23487eb1696376d2e078be5543eb13ee7b`), l'auteur reporte le Compiler individuel. Un **exemple global P2a–P2e**, à faire plus tard, sera testé **en interprété et compilé**.

Cette étape P2e.0 utilise **AMAL original en mode mémoire**, sans hook AMOS privé, sans nouveau token, sans changement du moteur Bob ni de la bibliothèque installable. Le banc **est activé comme unique ASC dans `tests/current/`** après préflight statique, et un **premier lancement WinUAE Runtime a échoué à la première présentation d'un Bob**. La correction de diagnostic n'a pas encore été testée sous WinUAE et aucun Compiler n'a été lancé. Le test P2d validé a quitté la campagne active, sans archivage et sans modification de son contenu historique (réf. Git `7f78e93b`).

## Premier essai Runtime : FAIL, correction limitée au banc

Journal utilisateur `M19_P2E0_AMAL_BRIDGE.TXT` de **300 octets**, SHA256 `f2f6914bd719c0409346c0bebdba451775b1d9491c293f442e8a8334a8c5b650`, correspondant au banc initial 5 632 octets SHA256 `bf1d53b54736e990f30ca3a5e79605f2cc88a7a4d0d9886ab166b9a48fe09fa4` :

- `PRG_STATE 1`, `RESULT 0`, `ERR 15`, `FRAME 1`, `SWAPS 1`, `VALID_SAMPLES 0`, `PIX_SAMPLES 0` et `VERDICT FAIL`.
- `LAST_X 97`, `LAST_Y 101`, `LAST_IMAGE 1`, `IMAGE1 1` : le canal AMAL fournit une première position/image et les getters Bob correspondent ; le rendu n'est pas encore validé.
- `CLOSE_RETURNED 1` : nettoyage AGA sans plantage observé sur ce scénario.

Les sources natives `tools/m19_b8_back_selector_emit.py` établissent que le sélecteur de back buffer refusera une page où le bit `Safe pending` reste actif. L'ancien banc P2e.0 ne reproduisait pas l'initialisation **de la seconde page** effectuée dans le banc P2d validé. **Le journal ne mesure pas directement le bit Safe** : il serait abusif d'affirmer que cette condition a déclenché l'erreur 15.

Le banc est corrigé en initialisant la zone 96,100,48×32 des deux pages physiques avec `Aga Blit Fill`, sans changer la Lib, AMAL ou l'API. Nouvelles sorties `BG0` / `BG1` / `SWAP_RESULT` et nouveaux codes `ERR 22` / `ERR 23` si les fills sont refusés. **Nouveau Runtime en attente**.

## Deuxième essai Runtime : rendu et mouvement corrects, flags à zéro

Journal exact `M19_P2E0_AMAL_BRIDGE(1).TXT` de 342 octets, SHA256 `918f262be52ba0f12bc1435c8c129be9afc4f972997f4eb238822107c8f6be1d`, correspondant à l'ASC P2e.0 de 6 089 octets (`27e8a132...`).

- **VALIDATION FONCTIONNELLE PARTIELLE :** `PRG_STATE 1`, `FRAME 241`, `VALID_SAMPLES 240`, `SWAPS 241`, `BG0 1`, `BG1 1`, `SWAP_RESULT 1`, `PIX_SAMPLES 29`, `MOVE_X/Y 1`, `IMAGE1/2 1`, `PIXEL_VALUE 90`, `PIXEL_EXPECTED 90`, `CLOSE_RETURNED 1`. Plus aucun `ERR 15`.
- **Verdict de l'ancien test : FAIL `ERR 21`** : `FLAG_X 0`, `FLAG_Y 0`, `FLAG_A 0`. Le manuel AMOS Professional décrit pourtant ces bits dans le mot à l'offset 0 de la zone `AMAL ... To address`. Les valeurs X/Y/A progressent normalement dans ce mode `Synchro Off` + `Synchro` ; la raison de l'absence des flags **n'a pas été établie**.
- **Nouveau banc de 6 795 octets :** bits de changement conservés en diagnostic brut (`FLAG_X/Y/A`, `FLAG_WORD_LAST`), mais verdict `ERR 21` fondé sur **`CHG_X`, `CHG_Y`, `CHG_A`** calculés depuis les transitions effectives de X/Y/A sur les trames consécutives. Les autres exigences (pixels, Swap, pages physiques, propreté de la sortie) sont inchangées.
- **Statut :** nouveau banc seulement livré et contrôlé statiquement ; **Runtime WinUAE de ce troisième ASC NON TESTÉ**, Compiler individuel reporté.

## Contrat AMAL d'origine vérifié dans le manuel

Voir [AMOS Pro, chapitre 7.6 « AMAL »](https://amospromanual.dev/07-06-amal.html), sections « Calling an AMAL program » et « SYNCHRO ».

L'instruction `Amal 0,_AMAL$ To _ADDR` publie dans **8 octets à une adresse paire** :

| Offset | Type | Signification |
| --- | --- | --- |
| `+0` | Word | flags, bit 0 : X changé, bit 1 : Y changé, bit 2 : image A changée |
| `+2` | Word | X |
| `+4` | Word | Y |
| `+6` | Word | image A |

On réserve `Reserve As Data 28,8`, on vérifie `Length(28)` et l'alignement de `Start(28)`, puis on lit par `Deek`. X/Y sont convertis en entiers signés 16 bits. `Synchro Off` intervient **avant** l'affectation AMAL ; `Synchro` est exécuté dans la tâche AMOS, puis les valeurs sont contrôlées avant `Aga Bob` et `Aga Swap`. `Channel To Bob` n'est jamais utilisé : il agirait sur les Bobs OCS, pas sur les Bobs privés AGA.

## Banc P2e.0

**Banc actif :** [`tests/current/M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc), 6 795 octets, SHA256 `62c94e9560134c0602b6e79b8cb2c78bf5adf207364d85d5a8953201ba61125f`. **Origine de conception :** [`tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt`](../tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt), non exécutable et inchangée. Le banc actif corrige l'oracle pixel : après un Swap, la capture lit l'ancienne page visible devenue arrière ; elle doit comparer le pixel et la couleur de la **frame précédente**, et non ceux du Bob courant.

- Cible : Lib P2d existante, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 AP20, CPU MC68020 minimum.
- Banc autonome, **sans IFF/ABK externe** : deux images AGBO opaques 1×1 aux couleurs 165 et 90 dans la banque 24 ; buffer de lecture 8 octets dans la banque 28 ; banque 27 préallouée pour le pixel oracle.
- Un seul canal AMAL 0, 240 appels `Synchro`, déplacement entre X=96..128, Y=100..116, alternance des images 1/2.
- Vérification des flags, valeurs X/Y/A, getters `Aga X/Y/I Bob`, `Aga Bob Auto Update(1)`, un seul `Aga Swap` explicite par cycle, capture de pixels aux abscisses alignées 8, puis `Amal Off 0` avant libération mémoire et fermeture AGA.
- Aucun `Aga Bob Update` additionnel ni `Channel To Bob`, donc aucun rendu ou swap OCS implicite.

## Exécution et verdict

1. Copier **uniquement** `dist/AMOSPro_AGA.Lib` P2d dans `APSystem`, redémarrer AMOS Pro dans WinUAE AGA.
2. Laisser libres les banques **24, 27, 28**. Dans un programme vierge, importer l'ASC actif [`tests/current/M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc) via **Project → Merge ASCII**.
3. **Lancer en Runtime uniquement**, sans compilation individuelle. Contrôler l'animation, puis sauvegarder `RAM:M19_P2E0_AMAL_BRIDGE.TXT` avant un autre lancement. Relever toute erreur AMOS, affichage incorrect, Guru ou freeze et le point atteint.

Attendu : `ERR 0`, `CHG_X/Y/A > 0`, `MOVE_X 1`, `MOVE_Y 1`, `IMAGE1 1`, `IMAGE2 1`, `FLAG_X/Y/A > 0`, `VALID_SAMPLES >= 32`, `PIX_SAMPLES >= 2`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

La première erreur entraîne `ERR 1..23` et un journal diagnostique lorsqu'un retour normal est possible ; le pixel fautif expose `PIXEL_VALUE` et `PIXEL_EXPECTED`. Un problème de grammaire AMOS, de canal ou un Guru peut empêcher ce journal : dans ce cas noter le message exact et l'étape. Le **premier test** a été exécuté en Runtime WinUAE et a échoué (`ERR 15`). La **révision ci-dessus** n'a pas encore de nouveau résultat WinUAE ; la présence des appels dans le manuel ne les valide pas.

## Validation et suites

- **Ancien ASC** : préflight officiel strict et contrat de journal PASS en CI avant la première Gate B FAIL. **ASC corrigé** : structure AMOS statique contrôlée (41+4 blocs If et End If équilibrés, lignes ≤220) ; préflight GitHub CI à vérifier sur le commit corrigé. Le préflight **ne compile pas AMOS**.
- **Gate B Runtime WinUAE P2e.0** : premier banc **FAIL (`ERR 15`)**, second banc **FAIL (`ERR 21`) mais rendu/mouvements/pixels confirmés**, troisième ASC avec deltas observés **NON TESTÉ**. Interprété strict / Gate C Compiler / Gate D physique **NON TESTÉS** sur P2e.0. Le Compiler individuel reste reporté à l'exemple global P2.
- **P2e.1** : plusieurs canaux et plusieurs Bobs, après un premier résultat WinUAE.
- **P2e.2** : collisions/Flip/Planes/auto-update combinés et tests de limites.
- **P2e.3** : audit d'un raccordement AMAL natif plus transparent uniquement si la passerelle mémoire devient insuffisante.

`dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, `tests/passed/` et les ressources anciennes restent intacts. Seul l'ASC actif `tests/current/` est remplacé selon l'autorisation explicite de la campagne ; aucune promotion.
