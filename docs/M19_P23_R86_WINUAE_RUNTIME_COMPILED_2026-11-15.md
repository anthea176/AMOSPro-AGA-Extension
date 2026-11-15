# M19 P2.3 — R86 v0.13.31 : WinUAE Runtime et Compiled PASS (15/11/2026)

**Gates B (Runtime) et C (AMOS Compiler) du test actif `Aga Bob Batch` : PASS**, sur les deux journaux transmis par l'auteur. Ces preuves s'appliquent au scénario `tests/current/M19_P23_BOBS_BATCH_01.asc`, et **ne constituent ni une promotion de R86, ni une démonstration de gain de vitesse, ni une validation exhaustive de tous les pixels WinUAE**.

## Version, test et intégrité

- Dépôt : `anthea176/AMOSPro-AGA-Extension` ; branche **`main`** uniquement.
- Candidat installé attendu : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **R86 v0.13.31** : 73 232 octets ; SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`. 78 commandes, 88 entrées AP20 ; blocs C2P 5 558 / IFF 2 508 / BOBS 5 226 / AGA 56 580 octets.
- Source du test AMOS : [`tests/current/M19_P23_BOBS_BATCH_01.asc`](../tests/current/M19_P23_BOBS_BATCH_01.asc), blob Git `19ad2044252783454f4082c118e53b34a6b83478`.
- R84 [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) **intouchable**, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.
- Gate A réelle MC68020 : **8 tests PASS** dans la [CI dédiée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700178749), dont pixels AGAPIC v1/v2 et FICON8, ModelID v2, ABI, rejets, clipping, modes et protection du front.
- **Limite d'attribution binaire** : les deux logs contiennent `LIBRARY R86_V0.13.31`, chaîne écrite dans le programme ASC ; ils **ne mesurent pas le SHA256** du binaire effectivement chargé dans WinUAE. La SHA indiquée ci-dessus est celle du candidat construit et conservé dans Git.

Empreintes des **fichiers TXT originaux transmis**, encodés avec 22 fins de lignes CRLF :
- Runtime : 339 octets, SHA256 `f443b08b1ea1065beb9d2fc991cfa90bc9eea653a9be8bbd5767aefbdb9dc255`.
- Compiled : 340 octets, SHA256 `ed81f6bcb557bac6dc342ae0e66322eb1c4de48664cfb49416bd2c7b9ffaf203`.

## Résultats croisés

| Champ | WinUAE Runtime | WinUAE Compiled |
|---|---:|---:|
| `RUN_MODE` | RUNTIME | COMPILED |
| `PRG_STATE` | 1 | -1 |
| `RESULT`, `ERR`, `VERDICT` | 1 / 0 / PASS | 1 / 0 / PASS |
| `CAPTURE` | 2 | 2 |
| `DRAW` | 3 | 3 |
| `CLIP` / `MASK` / `ORDER` | 1 / 1 / 1 | 1 / 1 / 1 |
| `REJECT` | 3 | 3 |
| `FRAMES` | 4 | 4 |
| `SWAPS` | 1 | 1 |
| `BASIC_TICKS` | 13 | 13 |
| `BATCH_TICKS` | 13 | 13 |
| `CHIP_BEFORE` → `CHIP_AFTER` | 1 798 712 → 1 798 712 | 1 860 472 → 1 860 472 |
| `FAST_BEFORE` → `FAST_AFTER` | 138 216 408 → 138 216 408 | 140 617 256 → 140 617 256 |
| `CLOSE_RETURNED` | 1 | 1 |

Les deux modes obtiennent un retour normal et sans erreur ; **delta Chip/Fast nul dans chaque exécution**. Le programme a capturé des banques AGAPIC v1/v2 et créé son FICON8 sans ressources externes, exercé trois appels Batch positifs et trois rejets, puis fermé l'écran.

## Interprétation et limites indispensables

1. **Gate B Runtime = PASS, Gate C Compiled = PASS pour le test soumis**. Il s'agit bien d'appels du nouveau moteur et pas seulement d'un témoin d'accès AP20.
2. **Pas de gain démontré** : quatre itérations seulement, fond complet `Aga Blit Fill` compris dans les deux chronométrages. `BASIC_TICKS=BATCH_TICKS=13` dans les deux modes. Résolution et durée insuffisantes pour attribuer un avantage (ou désavantage) au regroupement.
3. Dans l'ASC testé, `_ORDER=1` est posé après une capture 1×1 réussie **sans décoder ni confronter son pixel à une couleur attendue** ; `_CLIP=1` et `_MASK=1` suivent également des appels réussis **sans oracle de pixels WinUAE**. Ces compteurs prouvent le passage des chemins et le succès des commandes, non une vérification visuelle indépendante. Les contrôles **pixel exact** de la Gate A native restent distincts.
4. Le journal `SWAPS=1` correspond au **Swap explicite du programme BASIC**, pas à un Swap interne de Batch. La protection du front est exercée par la Gate A ; les logs WinUAE ne capturent pas directement les bitplanes du front.
5. Le delta mémoire nul atteste le retour des compteurs `Chip Free`/`Fast Free` mesurés, pas l'absence de toute fuite dans un scénario plus long.
6. Aucun essai **Gate D sur Amiga physique** ; pas de promotion `LAST_GOOD`, de branche, de tag ou de release.

## Journaux transmis — transcription fidèle des champs

**`M19_P23_RUNTIME.TXT`** :

```text
TEST M19_P23_BOBS_BATCH_01
LIBRARY R86_V0.13.31
RUN_MODE RUNTIME
PRG_STATE  1
RESULT  1
ERR  0
VERDICT PASS
CAPTURE  2
DRAW  3
CLIP  1
MASK  1
ORDER  1
REJECT  3
FRAMES  4
SWAPS  1
BASIC_TICKS  13
BATCH_TICKS  13
CHIP_BEFORE  1798712
CHIP_AFTER  1798712
FAST_BEFORE  138216408
FAST_AFTER  138216408
CLOSE_RETURNED  1
```

**`M19_P23_COMPILED.TXT`** :

```text
TEST M19_P23_BOBS_BATCH_01
LIBRARY R86_V0.13.31
RUN_MODE COMPILED
PRG_STATE -1
RESULT  1
ERR  0
VERDICT PASS
CAPTURE  2
DRAW  3
CLIP  1
MASK  1
ORDER  1
REJECT  3
FRAMES  4
SWAPS  1
BASIC_TICKS  13
BATCH_TICKS  13
CHIP_BEFORE  1860472
CHIP_AFTER  1860472
FAST_BEFORE  140617256
FAST_AFTER  140617256
CLOSE_RETURNED  1
```

## Suite

Ne pas modifier le test déjà qualifié afin de conserver la correspondance avec les journaux. Un **nouveau test à venir**, à installer seul dans `tests/current/` en archivant celui-ci octet pour octet dans `tests/passed/`, pourra vérifier un oracle de pixel WinUAE sur chevauchement, transparence et clipping, puis effectuer une mesure plus longue et ciblée du coût de dessin. Ne pas annoncer de gain avant cette mesure.

[Contrat R86](M19_P23_BOBS_BATCH_CONTRACT.md) · [Test actif](../tests/current/M19_P23_BOBS_BATCH_01.asc) · [Roadmap](ROADMAP.md)
