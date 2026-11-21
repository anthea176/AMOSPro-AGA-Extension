# M19 P2e.0 — Passerelle AMAL mémoire vers Bob AGA (expérimental)

## Décision et portée

Après **P2d Runtime PASS 43/43** (journal utilisateur du 21/11/2026, `PRG_STATE 1`, `ERR 0`, `PROBE_PREALLOC 1`, `CLOSE_RETURNED 1`, `VERDICT PASS` ; SHA256 du journal original `28f7ebfff3d77e7cc65469df3c246f23487eb1696376d2e078be5543eb13ee7b`), l'auteur reporte le Compiler individuel. Un **exemple global P2a–P2e**, à faire plus tard, sera testé **en interprété et compilé**.

Cette étape P2e.0 utilise **AMAL original en mode mémoire**, sans hook AMOS privé, sans nouveau token, sans changement du moteur Bob ni de la bibliothèque installable. Le banc **est activé comme unique ASC dans `tests/current/`** après préflight statique, mais **aucun lancement WinUAE ni Compiler n'a été effectué** sur P2e.0. Le test P2d validé a quitté la campagne active, sans archivage et sans modification de son contenu historique (réf. Git `7f78e93b`).

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

**Banc actif :** [`tests/current/M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc), 5 632 octets, SHA256 `bf1d53b54736e990f30ca3a5e79605f2cc88a7a4d0d9886ab166b9a48fe09fa4`. **Origine de conception :** [`tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt`](../tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.txt), non exécutable et inchangée. Le banc actif corrige l'oracle pixel : après un Swap, la capture lit l'ancienne page visible devenue arrière ; elle doit comparer le pixel et la couleur de la **frame précédente**, et non ceux du Bob courant.

- Cible : Lib P2d existante, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 AP20, CPU MC68020 minimum.
- Banc autonome, **sans IFF/ABK externe** : deux images AGBO opaques 1×1 aux couleurs 165 et 90 dans la banque 24 ; buffer de lecture 8 octets dans la banque 28 ; banque 27 préallouée pour le pixel oracle.
- Un seul canal AMAL 0, 240 appels `Synchro`, déplacement entre X=96..128, Y=100..116, alternance des images 1/2.
- Vérification des flags, valeurs X/Y/A, getters `Aga X/Y/I Bob`, `Aga Bob Auto Update(1)`, un seul `Aga Swap` explicite par cycle, capture de pixels aux abscisses alignées 8, puis `Amal Off 0` avant libération mémoire et fermeture AGA.
- Aucun `Aga Bob Update` additionnel ni `Channel To Bob`, donc aucun rendu ou swap OCS implicite.

## Exécution et verdict

1. Copier **uniquement** `dist/AMOSPro_AGA.Lib` P2d dans `APSystem`, redémarrer AMOS Pro dans WinUAE AGA.
2. Laisser libres les banques **24, 27, 28**. Dans un programme vierge, importer l'ASC actif [`tests/current/M19_P2E0_AMAL_BRIDGE.asc`](../tests/current/M19_P2E0_AMAL_BRIDGE.asc) via **Project → Merge ASCII**.
3. **Lancer en Runtime uniquement**, sans compilation individuelle. Contrôler l'animation, puis sauvegarder `RAM:M19_P2E0_AMAL_BRIDGE.TXT` avant un autre lancement. Relever toute erreur AMOS, affichage incorrect, Guru ou freeze et le point atteint.

Attendu : `ERR 0`, `MOVE_X 1`, `MOVE_Y 1`, `IMAGE1 1`, `IMAGE2 1`, `FLAG_X/Y/A > 0`, `VALID_SAMPLES >= 32`, `PIX_SAMPLES >= 2`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

La première erreur entraîne `ERR 1..21` et un journal diagnostique lorsqu'un retour normal est possible ; le pixel fautif expose `PIXEL_VALUE` et `PIXEL_EXPECTED`. Un problème de grammaire AMOS, de canal ou un Guru peut empêcher ce journal : dans ce cas noter le message exact et l'étape. Le test **n'a pas été exécuté par AMOS ou WinUAE**, la présence des appels dans le manuel n'en est pas une preuve.

## Validation et suites

- **Préflight officiel : PASS sur l'ASC actif exact**, script octet-identique à `tools/amos_preflight.py` (Git blob `9f45b4088bb95a5d604b0548ba79a85a1da6a72e`), avec `--strict-target` ; 21 auto-tests du preflight PASS et garde-fous complémentaires locaux PASS (225 lignes ASCII, maximum 75 caractères, blocs et Goto cohérents). Le préflight **ne compile pas AMOS**. Les CI du commit seront qualifiées séparément.
- **Gates B Runtime / interprété strict / C Compiler / D physique : NON TESTÉES sur P2e.0.** Le Compiler individuel reste reporté à l'exemple global P2.
- **P2e.1** : plusieurs canaux et plusieurs Bobs, après un premier résultat WinUAE.
- **P2e.2** : collisions/Flip/Planes/auto-update combinés et tests de limites.
- **P2e.3** : audit d'un raccordement AMAL natif plus transparent uniquement si la passerelle mémoire devient insuffisante.

`dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, `tests/passed/` et les ressources anciennes restent intacts. Seul l'ASC actif `tests/current/` est remplacé selon l'autorisation explicite de la campagne ; aucune promotion.
