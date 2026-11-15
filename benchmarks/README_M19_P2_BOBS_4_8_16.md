# M19 / P2 — Benchmark comparatif de 4, 8 et 16 Bobs (R84)

> **État au 15/11/2026 : second passage complet WinUAE Runtime 68030 avec JIT activé selon l'auteur : PASS, 240/240 frames, 9 088 dessins, zéro échec Draw/Swap.** [Résultats complets 68030/JIT](RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md). [Premier essai interrompu](RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md) conservé séparément. **Comparatif 68020/14 MHz/JIT OFF attendu.** `main` uniquement, R84 `LAST_GOOD` protégée, aucune API native.

**Unique ASC actif :** [`tests/current/M19_P2_BENCH_BOBS_01.asc`](../tests/current/M19_P2_BENCH_BOBS_01.asc). Le [prototype P2.0 fonctionnel validé](../tests/passed/M19_P2_OBJECTS_01.asc) est archivé octet pour octet ; [rapport Runtime P2.0](../docs/M19_P2_WINUAE_RUNTIME_2026-11-15.md).

## Objectif et comparaison équitable

Mesurer le **coût de tri du gestionnaire BASIC**, le coût d'effacement 320×256, le **temps de composition complète dans le back buffer AGA**, et la cadence observée d'une séquence **VBL + dessin + Swap**. Les quatre mesures sont **distinctes**. Aucune de ces valeurs ne mesure directement les cycles CPU du noyau 68020 ; `Timer` mesure le temps écoulé.

- **AGA privé :** 320×256, **8 plans / 256 couleurs**, palette commune, double buffer de l'extension R84.
- **Sources :** six banques AGAPIC 24×24 v1/v2 (banques 12..17) et quatre FICON8 16×16 (banque 20) fabriquées une fois avant le chronométrage. Les images sont **partagées** ; pas de capture ni allocation durant les boucles chronométrées.
- **Répartition constante dans chaque lot de quatre :** un AGAPIC masqué, un FICON8 masqué, un AGAPIC opaque et un second FICON8 masqué. Résultat : **4 = 1/2/1**, **8 = 2/4/2**, **16 = 4/8/4** (AGAPIC masqué / FICON8 / AGAPIC opaque). Les positions restent à l'intérieur de l'écran. Les objets sont triés selon **(Z croissant, ID stable)** avec des Z inversés pour exercer le tri.
- **Mouvement :** léger décalage X/Y calculé en BASIC à partir du numéro de frame, sans allocation ni mise à jour AMAL. **Ce banc isole le tri et le rendu ; il ne mesure pas la charge d'AMAL**, validé séparément en P0/P1/P2.0.
- **Séries :** deux passages successifs `P0/P1`, pour chaque charge **4, 8, 16** ; les temps sont consignés sans consolidation prématurée.

## Opérations chronométrées

| Champ du journal | Boucle par charge et par passage | Interprétation correcte |
|---|---:|---|
| `SORT_TICKS` | **800 appels** au tri BASIC | Gestionnaire seul ; comprend les boucles BASIC, pas de dessin |
| `FILL_TICKS` | **120 appels** `Aga Blit Fill(0,0,320,256,1)` | Fond seul, y compris attente de disponibilité si elle se produit |
| `COMP_TICKS` | **120 compositions** : fond + tri + N dessins | Temps écoulé de composition dans le back buffer, **sans Swap/VBL de cadence** sauf retries Safe |
| `DISP_TICKS` | **40 frames** : `Aga Wait Vbl`, composition, `Aga Swap` | Temps de présentation complet, **incluant VBL/Swap** ; ne pas comparer directement à `COMP_TICKS` |

`Timer` = **environ 20 ms/tick en PAL** (précision de 1 tick) selon les benchmarks existants du dépôt. On peut estimer `COMP_TICKS × 20 / 120` en **ms/frame** et `DISP_TICKS × 20 / 40` en ms/frame **à titre indicatif** ; ne pas arrondir ces valeurs en FPS sans tenir compte des attentes `Safe`, de l'émulation et du quantifiage. `SORT_TICKS × 20/800` représente le temps moyen écoulé par tri, mais peut être imprécis lorsque le total est très faible.

**Important :** `Aga Blit Fill` est une opération potentiellement accélérée par le Blitter ; `COMP_TICKS` n'est **pas** une mesure de cycles CPU purs. Le benchmark n'utilise aucune boucle de dessin en interruption. Le fond et les Bobs sont toujours redessinés **dans le back buffer contrôlé Safe** ; Swap est déclenché explicitement. `Aga Wait Vbl` ne vaut jamais acquittement Safe.

## Exécution reproductible

1. Démarrer WinUAE en AGA, PAL, **JIT OFF**. Pour l'étude 68020, choisir **MC68020 à 14 MHz, vitesse CPU fixe**. Noter également la fréquence chipset/réglage WinUAE, Chip RAM et Fast RAM. Pour une vérification rapide, commencer éventuellement en 68030 mais **ne pas comparer** ces nombres avec ceux du 68020.
2. Installer la bibliothèque R84 `LAST_GOOD` ; s'assurer que les banques **11 à 23 sont libres** et lancer depuis un programme vide **Project → Merge ASCII** avec le seul ASC actif.
3. L'écran AGA est initialement peu animé pendant les phases chronométrées sans Swap ; c'est **normal**. Les séquences visibles avec 4, puis 8, puis 16 Bobs sont courtes. Ne pas cliquer sur l'écran ni modifier les préférences WinUAE pendant l'essai. **Échap interrompt immédiatement avec `ERR 20`** ; le premier journal reçu s'est interrompu après la première frame présentée à 8 Bobs. Éviter tout appui sur Échap pendant les mesures ; si le code revient sans appui, le signaler.
4. Laisser finir les **2 passages × 3 charges**, jusqu'au retour AMOS. Récupérer **`RAM:M19_P2_BENCH_BOBS_RUNTIME.TXT`** (ou suffixe selon `Prg State`). **Copier le journal hors de RAM: avant de relancer**, car il sera écrasé.
5. Répéter idéalement deux à trois fois à configuration strictement identique. Chaque fichier est analysé séparément ; utiliser le **médian** des passages ou relances et garder les mesures brutes.

## Contrôles et qualité du benchmark

- `RESULT 1`, `VERDICT PASS`, `ERR 0`, `CAP_OK 6`, `ICON_OK 4`, `OBJECTS_PREPARED 16`, `FRAME_OK 240`, `SORT_FAIL/FILL_FAIL/DRAW_FAIL/SWAP_FAIL 0`, `CLOSE_RETURNED 1`.
- Chaque passage : `N4_*_COMP_DRAWS 480`, `N8_*_COMP_DRAWS 960`, `N16_*_COMP_DRAWS 1920`. Total de dessins attendus, **échauffement inclus** : `DRAW_OK 9088`.
- Relever `N{4,8,16}_P{0,1}_COMP_SAFE_RETRIES` ; **si non nul**, la mesure de composition inclut des attentes VBL et n'isole plus la composition non bloquante. `SAFE_RETRIES` et `SWAP_RETRIES` sont également consignés. Le compteur global de retries englobe les phases visualisées et les mesures Fill.
- `RESULT PASS` valide les **retours d'appel et les compteurs du banc**, **pas** un objectif de FPS, pas une absence de tearing prouvée, ni une mesure de cycles exacts. `Chip/Fast delta 0` éventuel est un constat net entre deux prises mémoire, pas le pic ni une preuve universelle d'absence de fuite.

## Réaliser l'analyse

Après réception du journal, calculer pour chaque N et chaque passage :

```text
sort_ms_par_appel       = SORT_TICKS * 20 / 800
fill_ms_par_appel       = FILL_TICKS * 20 / 120
composition_ms_par_frame= COMP_TICKS * 20 / 120
presentation_ms_par_frame=DISP_TICKS * 20 / 40
```

Les **différences 4→8→16** seront analysées séparément pour le tri, le fond et la composition. Si des retries Safe surviennent dans une série, signaler que la mesure est contaminée, et ne pas attribuer l'écart à des calculs CPU. Le débit de présentation est limité/synchronisé par VBL/Swap : on ne peut pas le transformer en performance du renderer seul.

**Décision future :** mesurer avant d'investir dans un gestionnaire AP20 natif. Une extension native ne sera proposée que si le tri ou la composition constitue un goulot d'étranglement démontré ; son contrat, son coût binaire et ses gates doivent être approuvés indépendamment. Les sprites matériels AGA restent l'étude P3.

[Contrat du gestionnaire](../docs/M19_P2_OBJECT_MANAGER_CONTRACT.md) · [Plan M19](../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Rapport P2.0 PASS](../docs/M19_P2_WINUAE_RUNTIME_2026-11-15.md)
