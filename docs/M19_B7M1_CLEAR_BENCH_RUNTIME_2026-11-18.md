# M19 B7-m1 — benchmark Fill plein écran / dirty rectangles (18/11/2026)

## Point de départ et provenance

Le [banc B7-m1 précédent (120 frames)](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/75caa3c8198aad612e434e1ae3d54ceb2249ca45/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) a fourni le journal utilisateur du 18/11/2026 : `RESULT 1`, `ERR 0`, `FRAMES_OK 120`, `DRAW_FAILS 0`, `SWAP_FAILS 0`. L'auteur rapporte quatre lancements réussis sans `Erase All`, sans traînée, avec une animation ressentie comme lente. La capture montre deux Bobs mobiles et deux Bobs fixes au bord ; cette dernière propriété était **volontaire** dans le vieux code. Aucune mesure de fréquence n'existait.

La Lib de travail reste **M19 P0j-b7-m1, 102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, reconstruite par `tools/build_m19_p0j_end_lifecycle_in_memory.py::build_multiframe()`. Cible **MC68020+** ; essai prévu WinUAE AGA PAL **68030/JIT ON**, uniquement en Runtime. R84 `LAST_GOOD`, les archives et la Lib installable restent intacts.

## Hypothèse à départager

En 320×256 à huit bitplanes, un Fill plein écran correspond à 81 920 octets de données planaires logiques à réinitialiser, sans compter la contention Chip, les registres DMA, les appels BASIC et la synchronisation Safe/Disp. Il est **plausible**, mais **non démontré**, que cet effacement soit responsable de la lenteur observée.

Le nouveau test remplace **l'unique ASC actif**, sans nouveau binaire, et préserve son chemin pour les workflows : [`tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) **7 555 octets**, SHA256 `0f18cb608f75cda0390f86d25169bd4312561efd4d2051435a6803ceff42f689`.

## Protocole comparatif

| Passage | Cas | Frames | Composition |
|---|---|---:|---|
| 1 | A | 120 | Fill 320×256 + quatre Bobs mobiles + Swap |
| 2 | B | 120 | Fill 320×256 + Swap **sans Draw** |
| 3 | C | 120 | Effacement local des anciennes positions + quatre Bobs mobiles + Swap |
| 4 | C | 120 | Même C, nouvelle initialisation des deux pages |
| 5 | B | 120 | Même B |
| 6 | A | 120 | Même A |

Quatre trajectoires distinctes, deux banques **24/25**, Bobs rouges masqués de **17×15** et jaunes opaques de **37×8**, clipping aux bords. A et C ont **exactement les mêmes positions** à frame identique. B n'appelle pas `Aga Bob Draw`, même si le registre Bob a déjà été initialisé par A.

**C et double buffering :** deux premières frames de chaque série = réinitialisation plein écran de chacune des deux pages. Ensuite, huit tableaux conservent X/Y des quatre Bobs pour **chaque** page (indices 0 et 1), et l'on efface **seulement** leurs anciennes emprises avant le nouveau Draw. Les rectangles sont clipés à [0,320[×[0,256[. Le suivi de page bascule **après Swap réussi**, jamais avant. Les quatre Bobs sont repeints après tous les effacements ; aucun Bob fixe n'est conservé. Les retries Fill et Swap utilisent `Repeat/Until` avec 40 tentatives maximum, attente VBL **seulement en cas de refus**, échec bloquant. Aucun `Wait Vbl` artificiel dans une frame réussie.

**Mesure :** `Timer` AMOS = 50 ticks par seconde ; chaque fenêtre couvre 120 frames de Fill/Draw/Swap sans bank capture, I/O, fermeture ni attente finale. Compteurs par série : `RUN_FRAMES`, `RUN_TICKS`, `RUN_FPS_X10` (FPS multipliés par 10). Compteur global `RETRY_VBL` pour repérer les attentes forcées. Deux répétitions inversées limitent le biais d'ordre, sans fournir une véritable dispersion statistique.

**Chemin de sortie :** retour `Amos To Front`, `Aga Screen Close`, effacement banques 24/25 et écriture du log `RAM:M19_B7M1_CLEAR_BENCH.TXT`. Exécution Runtime uniquement ; `PRG_STATE -1` refusé, aucun appel Compiler.

## Validation et limitations

- **PREFLIGHT PASS** : `amos_preflight.py --strict-target --fail-on-warnings`, source ASCII, max 95 caractères par ligne.
- **STATIC PASS** : `tools/test_m19_p0j_b7_anim_asc_static.py` contrôle le SHA exact, l'ordre Fill/Draw/Swap, les quatre coordonnées, deux pages, les attentes bornées, la fermeture et le journal.
- **240 états de frame géométriques (2×120) PASS** sur une simulation Python d'occupation de pixels (empreintes pleines conservatrices ; ce n'est ni le masque réel ni le DMA). Vérification du clipping gauche/droite et des anciennes positions page par page.
- **Gate B nouveau benchmark : NON TESTÉE. Gate C : NON TESTÉE. Gate D : NON TESTÉE.** Ne pas recycler la validation de l'ancien ASC ni annoncer un gain en pourcentage sans les six séries de `RUN_TICKS`.

### Interprétation attendue

Comparer les ticks **A/C** par paire (1 contre 3, 6 contre 4) : une baisse montre que, pour ce programme, des effacements partiels sont plus rapides. La série B mesure le coût « Fill plein écran + Swap » sans Draw, mais n'isole ni le temps DMA pur du Fill ni les synchronisations Safe/Disp. Un `RETRY_VBL` élevé ou une forte asymétrie entre répétitions rend la comparaison moins fiable. Toute traînée dans C impose de considérer C comme **FAIL visuel**, même si `VERDICT PATH_OK`.

[Mode d'emploi](../tests/current/README.md). L'ASC historique reste accessible dans Git, sans second ASC actif ni modification de `tests/passed/`.
