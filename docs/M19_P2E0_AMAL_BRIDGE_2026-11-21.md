# M19 P2e.0 — Passerelle AMAL mémoire vers Bob AGA (expérimental)

## Décision et portée

Après **P2d Runtime PASS 43/43** (journal utilisateur du 21/11/2026, `PRG_STATE 1`, `ERR 0`, `PROBE_PREALLOC 1`, `CLOSE_RETURNED 1`, `VERDICT PASS` ; SHA256 du journal original `28f7ebfff3d77e7cc65469df3c246f23487eb1696376d2e078be5543eb13ee7b`), l'auteur reporte le Compiler individuel. Un **exemple global P2a–P2e**, à faire plus tard, sera testé **en interprété et compilé**.

Cette étape P2e.0 utilise **AMAL original en mode mémoire**, sans hook AMOS privé, sans nouveau token, sans changement du moteur Bob ni de la bibliothèque installable. Le banc n'est **pas un test validé sous WinUAE** tant qu'un journal d'exécution exact n'a pas été reçu. L'ASC reste sous `tests/design/` et le seul ASC actif P2d dans `tests/current/` n'est ni déplacé ni modifié.

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

Fichier : [`tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.asc`](../tests/design/M19_P2E0_AMAL_BRIDGE_UNVALIDATED.asc).

- Cible : Lib P2d existante, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 AP20, CPU MC68020 minimum.
- Banc autonome, **sans IFF/ABK externe** : deux images AGBO opaques 1×1 aux couleurs 165 et 90 dans la banque 24 ; buffer de lecture 8 octets dans la banque 28 ; banque 27 préallouée pour le pixel oracle.
- Un seul canal AMAL 0, 240 appels `Synchro`, déplacement entre X=96..128, Y=100..116, alternance des images 1/2.
- Vérification des flags, valeurs X/Y/A, getters `Aga X/Y/I Bob`, `Aga Bob Auto Update(1)`, un seul `Aga Swap` explicite par cycle, capture de pixels aux abscisses alignées 8, puis `Amal Off 0` avant libération mémoire et fermeture AGA.
- Aucun `Aga Bob Update` additionnel ni `Channel To Bob`, donc aucun rendu ou swap OCS implicite.

## Exécution et verdict

1. Copier **uniquement** `dist/AMOSPro_AGA.Lib` P2d dans `APSystem`, redémarrer AMOS Pro dans WinUAE AGA.
2. Laisser libres les banques AMOS **24, 27, 28**. Dans un programme vierge, utiliser **Project → Merge ASCII** sur l'ASC expérimental précité.
3. **Test Runtime uniquement à ce stade**, pas de compilation individuelle. Sauvegarder `RAM:M19_P2E0_AMAL_BRIDGE.TXT` avant tout nouveau lancement.

Attendu : `ERR 0`, `MOVE_X 1`, `MOVE_Y 1`, `IMAGE1 1`, `IMAGE2 1`, `FLAG_X/Y/A > 0`, `VALID_SAMPLES >= 32`, `PIX_SAMPLES >= 2`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

La première erreur entraîne `ERR 1..21` et un journal diagnostique lorsqu'un retour normal est possible ; le pixel fautif expose `PIXEL_VALUE` et `PIXEL_EXPECTED`. Un problème de grammaire AMOS, de canal ou un Guru peut empêcher ce journal : dans ce cas noter le message exact et l'étape. Le test **n'a pas été exécuté par AMOS ou WinUAE**, la présence des appels dans le manuel n'en est pas une preuve.

## Validation et suites

- **Analyse statique locale : PASS** (218 lignes ASCII, max 79 caractères, blocs `If/For` équilibrés, Goto résolus, contrat mémoire présent). Ce n'est pas le préflight officiel tant que `tools/amos_preflight.py` n'est pas exécuté sur le fichier exact, et ce n'est **ni Gate B ni Gate C**.
- **P2e.1** : plusieurs canaux et plusieurs Bobs, après un premier résultat WinUAE.
- **P2e.2** : collisions/Flip/Planes/auto-update combinés et tests de limites.
- **P2e.3** : audit d'un raccordement AMAL natif plus transparent uniquement si la passerelle mémoire devient insuffisante.

`dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, `tests/current/`, `tests/passed/` et les ressources anciennes restent intacts.
