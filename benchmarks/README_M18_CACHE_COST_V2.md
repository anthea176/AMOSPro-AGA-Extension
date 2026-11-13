# M18 — R60 cache Chip benchmark v2

**Statut : ASC préparé, WinUAE non encore testé.** [Télécharger le programme ASCII](m18_r60_cache_cost_v2.asc). Ce programme utilise la bibliothèque **R60 v0.13.5 LAST_GOOD** inchangée. Il n'implémente pas de nouveau Fast Icon.

## Exécution WinUAE

Dans une session jetable, placer `m18_r60_cache_cost_v2.asc` et [`M16_AGAPIC_SAMPLE_BANK10.abk`](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire courant d'AMOS. **Attention : le Load écrase la banque 10.** Dans un programme vide : **Project → Merge ASCII** et exécuter. Préférence pour **68020 sans JIT, PAL, cycle-exact si disponible, compilé** ; garder le même exécutable pour un passage 68030 50 MHz sans JIT, en notant les réglages réels WinUAE. La boucle `Do / Wait Vbl / Loop` finale garde les résultats visibles.

Afficher et relever les **8 trios de ticks** ainsi que `ERR`, `CLOSE`, `CHIP`. Chaque tick `Timer` PAL vaut **20 ms**. Le test utilise un écran **320×256×16 (4 bitplanes)**, 3 essais par cas, un staging initial (16,24) dans le back buffer Chip et une copie vers (160,40) sans recouvrement. Aucun Swap/VBL/Print ne se trouve dans les boucles mesurées.

| Ligne | Nombre d'appels par essai | Ce qui est chronométré |
|---|---:|---|
| `OFF` | 240 CPU | `Aga Image Region` 16×16 hors écran (X=320) : **une validation RLE** et contrôles, zéro dessin |
| `1PIX` | 240 CPU | `Aga Image Region` visible 1×1 : **deux passes RLE**, un pixel dessiné |
| `CPU16` | 240 CPU | `Aga Image Region` visible 16×16 opaque |
| `MASK16` | 240 CPU | `Aga Image Region` visible 16×16 avec masque indépendant AGAPIC |
| `BLIT` | 2 400 copies | `Aga Blit Copy` 16×16 **opaque depuis Chip déjà préparée** |
| `CACHE1` | 240 stages + 240 copies | un stage AGAPIC avant chaque copie |
| `CACHE4` | 60 stages + 240 copies | un stage AGAPIC pour 4 copies |
| `CACHE16` | 15 stages + 240 copies | un stage AGAPIC pour 16 copies |

**Normalisation :** pour comparer le CPU (N=240) au Blitter (N=2 400), calculer `médiane ticks × 20 ms / N`. Les trois séries `CACHE*` comprennent **240 copies identiques**, mais une fréquence de staging différente.

## Interprétation et limites

- `OFF` n'isole pas le RLE seul : il inclut aussi les vérifications de banque, d'écran et de structure. Les différences `OFF / 1PIX / CPU16` donnent des indications sur le coût de la deuxième passe et de l'écriture CPU, sans profiler chaque instruction.
- `CACHE1/4/16` chronomètre **la préparation par décodage AGAPIC R60**, pas le staging d'un Fast Icon planaire 8 plans pré-décodé. **Aucun seuil de rentabilité général des Fast Icons natifs ne peut encore être déduit.**
- `Aga Blit Copy` est une **copie opaque**. `MASK16` est une mesure CPU seulement ; le moteur Blitter masqué reste à créer. La source est dans **le back buffer** : sans Swap pendant les séries, la persistance d'un cache dans les deux buffers n'est **pas** démontrée.
- Le benchmark ne vérifie que le **dernier résultat d'appel de chaque série** et la valeur Chip Free avant/après, pas tous les retours ni le rendu pixel par pixel. `ERR 0`, `CLOSE -1`, mémoire Chip identique et fin normale restent **à vérifier réellement sous WinUAE**.
- La comparaison décisive devra tester le vrai moteur **Fast 8 plans → CPU Chip** contre **Fast → staging Chip → Blitter**, masquage et alignements compris, avec coûts complets. **Aucune nouvelle commande R61 ni promotion n'est autorisée par ce bench.**

**Dépôt :** benchmark exploratoire dans `benchmarks/`, distinct d'un ASC de validation d'une nouvelle bibliothèque dans `tests/current/`. Ancien [benchmark R60](m18_r60_cpu_vs_blit_16x16.asc), R60 `LAST_GOOD` et archives intactes.
