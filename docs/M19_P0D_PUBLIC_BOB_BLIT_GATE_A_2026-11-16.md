# M19 P0d — Premier Bob AGA public `Aga Bob Blit(I,X,Y)` — Gate A MC68020

> **ACTUALISATION — BASCULE P0c → P0d AUTORISÉE (16/11/2026).** Ce rapport décrivait initialement la construction P0d **en mémoire uniquement**. La même candidate source-vérifiée (91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`) est maintenant la **bibliothèque active unique** `dist/AMOSPro_AGA.Lib` avec le seul [ASC actif](../tests/current/M19_P0D_BOB_BLIT_01.asc). **Gate A native MC68020 PASS** ; **Gates B WinUAE Runtime et C réel AMOS Compiler restent NON TESTÉES** sur cette candidate. Suivre le [protocole de campagne actuel](../tests/current/README.md). Le terme « non installée » dans les paragraphes historiques suivants se rapporte à l'étape **avant** cette autorisation, et non à la situation actuelle. `LAST_GOOD` R84 n'a pas été promue.


Date : 16/11/2026. Dépôt **`anthea176/AMOSPro-AGA-Extension`**, branche **`main` uniquement**.

## Résultat constaté

**GATE A native MC68020 : PASS.** Le premier chemin complet d'un appel AMOS à un Bob AGA immédiat existe en source et a passé des tests d'exécution CPU020 avec services AmigaOS **simulés**. Ce jalon est **SOURCE-ONLY / IN-MEMORY**, **NON INSTALLÉ** : pas de remplacement de `dist/AMOSPro_AGA.Lib`, pas de test AMOS activé et pas de conclusion Runtime/Compiler.

- [CI M19 Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43959009697) : reconstruire P0c/P0d en mémoire, vérifier AP20 HUNK/V2 et `GetP`, exécuter le wrapper public natif et la chaîne Chip/Blitter sous Unicorn MC68020, deux placements d'unités, préflight strict de l'ASC. **108 scénarios du chemin public PASS**.
- [CI politique CPU/chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43959010076) : **PASS**. Aucun changement dans les archives, la bibliothèque officielle ou le test actif.
- Gate A privée déjà validée : **720** cas pixel-exacts du peintre, **90** assertions du résolveur AGBO, **84** cas intégrés Safe/back buffer ; tous avec fonctions Exec/graphics simulées.
- Préflight [`tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc`](../tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc) : **PASS statique strict**, pas une compilation réelle et pas un programme de campagne actif.

## Identité du candidat AP20 (non distribué)

| Propriété | Valeur |
| --- | --- |
| Builder source | [`tools/build_m19_p0d_bob_blit_in_memory.py`](../tools/build_m19_p0d_bob_blit_in_memory.py) |
| Base immuable P0c | **87 020 octets** ; SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` |
| P0d construit en mémoire | **91 300 octets** |
| SHA256 P0d | `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` |
| Table | **83 commandes**, **93 entrées AP20** |
| Nouvelle fonction | `Aga Bob Blit(I,X,Y)` ; token/function index **88**, signature `00,0,0` |
| Nouvelle entrée native | Groupe BOBS **91**, offset **22 688** |
| Append natif total P0d | **4 256 octets**, dont wrapper public **390 octets** |
| Groupe AGA historique | Déplacé de l'index 91 à **92**, octets natifs préservés |
| RBSR interpréteur signé maximal | **32 196** ; marge de seulement **570** octets par rapport à la limite de contrôle 32 766 |
| CPU minimal | **MC68020/68EC020** |

**Important PC16 :** l'espace signé est presque épuisé. **Ne pas** ajouter en aveugle de nouvelles routines à ce même groupe BOBS après P0d ; une nouvelle structuration de groupes V2 avec vérification des appels croisés sera nécessaire pour les futures commandes d'objets animés.

## Contrat du premier appel public

La commande **fonction numérique** proposée est `_OK=Aga Bob Blit(_I,_X,_Y)`, où `_I` est un ID d'image **1-based** dans la banque AMOS active, et `_X,_Y` sont des coordonnées de destination signées. Renvoie **1** si accepté, y compris dessin totalement hors écran sans DMA, **0** en cas de refus. Les trois arguments suivent l'ABI AMOS numérique : `D3=Y`, `(A3)+=X,I`, `A3` avance de huit octets ; autres registres préservés. La syntaxe AP20 est contrôlée statiquement mais **ne peut être déclarée compilable sous AMOS** avant Gate C réelle.

1. `Aga Bob Bank N` continue de sélectionner ou créer la banque AGBO, **sans imposer une copie Chip sur une banque vide**. Capture par `Get AGA Bob` et masque indépendant par `Make/No AGA Bob Mask` restent inchangés.
2. À **la première invocation de `Aga Bob Blit`**, le wrapper vérifie état AGA et Double Buffer, la banque sélectionnée, l'identité du contenu et sa génération. Il appelle `registry_lookup_entry` ; si le staging manque ou est périmé, `registry_prepare_entry` copie **une seule fois la banque validée entière** en Chip. Puis `program_end_arm_entry` attache le nettoyage `End` ; en cas d'échec d'armement, le contexte de cette banque est libéré avant le retour 0.
3. Le moteur privé résout l'image et le masque dans **l'allocation Chip vérifiée**, choisit le **back buffer non affiché** à partir du vrai état AGA `A5+0x1C8`, vérifie `SafePort`, `BitMap`, profondeur et **dimensions logiques** de l'écran, puis invoque `BltBitMapRastPort` / `BltMaskBitMapRastPort` et `WaitBlit`.
4. **Aucun `Aga Swap` implicite** : le programme doit présenter volontairement le back buffer une fois tous les Bobs dessinés. En absence de notification `Safe`, le dessin refuse sans DMA ni Swap.
5. Aucun objet persistant n'est créé. **`Aga Bob N,X,Y,I`**, les numéros d'objets, `Aga Bob Bank Free`, `Aga Bob Off` et le moteur d'animation appartiennent au jalon suivant et **ne sont pas installés**.

**Écart explicite vis-à-vis du contrat cible :** la préparation Chip est **paresseuse au premier Blit**, pas automatique au moment exact de `Aga Bob Bank N` pour une banque chargée. C'est un choix expérimental du premier Bob affichable pour gérer les banques encore vides à la sélection. Il n'annule pas l'objectif d'une préparation anticipée **hors boucle de jeu**. `Erase`/`Load` ou réallocation exige de **resélectionner la banque** avant réutilisation. Les mutations `Poke` arbitraires ne sont pas garanties.

## Fichiers ajoutés et test de démonstration

- [`tools/m19_p0d_public_blit_emit.py`](../tools/m19_p0d_public_blit_emit.py) : wrapper AMOS 68020, préparation Chip / garde End / appel Safe-Blitter.
- [`tools/build_m19_p0d_bob_blit_in_memory.py`](../tools/build_m19_p0d_bob_blit_in_memory.py) : nouvelle entrée AP20, index/groupes V2, contrôles de provenance/offsets/roundtrip/déplacements. **Ne crée aucun binaire sur disque.**
- [`tools/test_m19_p0d_public_blit_gate_a.py`](../tools/test_m19_p0d_public_blit_gate_a.py) : CPU020 et registres, 1/4/8 plans, allocations par banque, callbacks, refus sans Double Buffer et sans 020, mémoire libérée à Close.
- [`tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc`](../tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc) : **source AMOS de conception NON ACTIVE**. Sans IFF/ABK externe, exige la banque 24 libre ; crée deux images, active masque sur la première, exécute quatre Blits (dont bords), un échec sur image absente, un seul Swap et écrit des journaux Runtime/Compiled séparés. Contrôle visuel humain indispensable.

## Commandes de vérification host / CI

```sh
python -B tools/native_cpu_policy.py --self-test
python -B tools/check_aga_delivery_paths.py --self-test
python -B tools/build_m19_p0d_bob_blit_in_memory.py
python -B tools/test_m19_p0d_public_blit_gate_a.py
python -B tools/amos_preflight.py --strict-target tests/design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc
```

Les trois dernières commandes exigent Python ; le banc MC68020 requiert `unicorn==2.1.4` et `capstone==5.0.9` comme la CI existante. Ces commandes **ne compilent pas** le programme AMOS.

## Gates B/C : NON TESTÉES — bascule explicite indispensable

Pour tenter WinUAE **Gate B Runtime** puis **Gate C AMOS Compiler**, il faudra **une autorisation explicite distincte** pour remplacer `dist/AMOSPro_AGA.Lib` P0c par la candidate P0d exacte issue du builder, et basculer **l'unique ASC `tests/current/*.asc`** vers le banc P0d. L'ancienne campagne P0c restera traçable dans Git mais ses fichiers actuels ne doivent pas être changés lors de cette Gate A.

Une fois cette bascule approuvée, vérifier taille/SHA256 du binaire réellement installé dans le slot AGA, CPU AGA 68030 JIT ON, lancer l'ASC actif via `Project → Merge ASCII`, observer les quatre Bobs et le retour AMOS, puis produire journaux `PRG_STATE 1` et `PRG_STATE -1` séparés. Ne pas considérer un simple `RESULT 1` comme validation visuelle du vrai DMA sans capture et observation.

**Protections inchangées :** `dist/AMOSPro_AGA.Lib` P0c, **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a` ; `tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc` seul ASC actif ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. Aucune promotion, publication, autre dépôt ou branche.
