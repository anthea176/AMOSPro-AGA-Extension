# M18 — CBlock AGA : capture/restauration rapide en Chip RAM

**Décision auteur du 13/11/2026 : priorité absolue à la VITESSE ; banque temporaire en CHIP RAM ; alignement horizontal de 8 PIXELS si profitable.** Il s'agit bien de **8 pixels, pas de 8 octets**. Le précédent contrat « Fast RAM + RLE + pixel exact » est **abandonné**. Ce contrat est **implémenté dans R68**, Gates **A native et B WinUAE interprétée PASS** ([rapport R68](M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md)). Sur le 68020 à 14 MHz **sans JIT**, CPU8/CPU16/Blitter donnent capture **34/28/30** et Draw **35/29/29** ticks ; sur le 68030 **avec JIT**, les mesures sont **0/0/6** dans les deux sens, les zéros CPU étant sous la résolution de Timer. Ne pas mélanger ces profils.

**État R68 v0.13.13 : unique candidate `dist/AMOSPro_AGA.Lib`, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, 64 commandes / 71 AP20. Gate A M68000 48 cas PASS, Gate B WinUAE interprétée PASS sur les captures auteur du 13/11/2026 ; [ASC R68 exact archivé](../tests/passed/M18_R68_CBLOCK_CHIP_01.asc). ASC intégré [toujours actif dans tests/current](../tests/current/M18_R68_COMPILER_FINAL_01.asc) : **Gate B interprétée WinUAE 68030 JIT ON PASS** (`RESULT 1`, [rapport](M18_R68_INTEGRATED_GATE_B_68030_JIT_2026-11-13.md)) ; **Gate C Compiler réelle PASS** ([rapport de l'ASC compilé](M18_R68_INTEGRATED_GATE_C_COMPILER_2026-11-13.md)). R68 `LAST_GOOD` PROMUE après Gates A/B/C ; R63 préservée dans l'historique Git. D physique non testée.**

## 1. Usage prioritaire et origine

**Scénario** : sauvegarder très vite un morceau de fond avant l'affichage d'un panneau / dialogue, puis restaurer ce fond aussi vite que possible. Un même bloc doit pouvoir être **recapturé et restitué de nombreuses fois** sans réallocation ni compression. Les performances de `Capture` **et** `Draw/Restore` comptent.

AMOS Professional possède `Get Cblock` / `Put Cblock` / `Del Cblock` avec un RLE sur octets de bitplanes et un alignement historique sur 8 pixels. L'objectif AGA reprend l'usage **bloc de fond temporaire**, **pas** le format compressé, la compatibilité binaire ou l'allocateur privé d'AMOS :

- [Commandes CBlock dans le code AMOS Professional](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BLib.s#L706-L716)
- [Routines historiques de capture et de restitution](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BW.s#L12013-L12213)
- [Gestion historique des blocs](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BW.s#L12229-L12313)

**Leçon de l'audit** : l'alignement sur 8 pixels permet des transferts d'octets planaires, mais **n'établit pas** que 8 pixels est optimal pour le Blitter (qui travaille en mots de 16 bits). Il faut comparer **8 et 16 pixels**, ainsi que le CPU sur de petits rectangles, avant de choisir un chemin rapide.

## 2. Choix techniques actés et propositions

| Sujet | Contrat corrigé |
|---|---|
| Priorité | **Temps d'exécution minimal**, sans décodage RLE, conversion chunky/planar ou réorganisation coûteuse à chaque dessin |
| Mémoire | **Banque DATA AMOS temporaire allouée en Chip RAM physique** ; refus si elle ne réside pas réellement en Chip |
| Cycle de vie | Banque créée à la première capture, **réutilisée sur les captures suivantes** à dimensions/profondeur identiques ; libération via `Erase Bank` ou `Erase` |
| Format | **RAW planar, sans compression**, directement exploitable par CPU/Blitter |
| Blitter | **Chemin privilégié pour les rectangles où il est plus rapide** ; opérations DMA **Chip→Chip**, pas de staging Fast→Chip |
| Petits rectangles | Prévoir un **chemin CPU si le benchmark le justifie** ; ne pas imposer le Blitter si son initialisation coûte davantage |
| Granularité horizontale | **8 pixels proposés** pour X source, largeur et X destination ; aucune ambiguïté avec 8 octets |
| Implémentation de cette granularité | Les paramètres **doivent être multiples de 8** ; retour `0` sinon, sans arrondi silencieux ni modification des voisins |
| Détail DMA | Les bitplanes du bloc sont stockés sur **mots alignés (16 bits)** ; les derniers pixels de remplissage restent hors du rectangle logique |
| Géométrie | Y/hauteur en pixels ; capture et restauration entièrement dans l'écran pour le chemin rapide v1, sans clipping lent |
| Profondeur | 1 à 8 plans réellement ouverts par l'extension, avec correspondance stricte à la restitution |
| Opaque | Index couleur 0 **restitué** ; pas de masque de transparence |
| Source/destination | **Back buffer du seul écran AGA privé** ; pas l'écran AMOS ni Workbench, pas de `Swap` automatique |
| Palette | Seuls les indices de pixels sont copiés, jamais les valeurs RGB |
| Persistant | **Non prioritaire** : ce n'est ni AGAPIC, ni une banque à archiver ; `Save/Load` ne fait pas partie de la qualification v1 |

**Important** : réserver une banque Chip ne garantit pas automatiquement que sa base DMA, la longueur et chaque plan sont utilisables par le Blitter. Vérifier le placement réel et l'alignement mémoire avant de dessiner.

## 3. API AMOS implémentée en R68 (Gate B PASS)

```amos
_OK=Aga C Block Capture(Bank,X,Y,Width,Height,Method)
_OK=Aga C Block Draw(Bank,X,Y,Method)
_OK=Aga C Block Restore(Bank,Method)
```

**Argument `Method` :** `0` = CPU 8 pixels (octet), `1` = CPU 16 pixels (mot), `2` = Blitter Chip→Chip 8 pixels. Alignement horizontal des X et de la largeur : 8 pixels pour 0/2, 16 pixels pour 1. Ces modes sont explicites pour mesurer le chemin réellement le plus rapide ; pas de choix automatique avant benchmark.

### Capture / recapture

- Si `Bank` (5..65535) est libre : allouer une **banque DATA `AGACBLK ` en Chip RAM**, la vérifier, puis remplir le bloc.
- Si elle existe déjà et est **notre banque CBlock Chip valide** avec **mêmes Width, Height et Depth** : **recapturer directement dedans** sans supprimer / recréer le bloc ; la position d'origine sauvegardée devient le nouveau X/Y.
- Si le numéro est occupé par une banque étrangère, mal formée, non-Chip ou de dimensions différentes : **retour `0` sans écraser la banque existante**.
- X et Width doivent être positifs/nuls selon leur rôle et **multiples de 8 pixels** ; largeur/hauteur strictement positives. Zone entièrement à l'écran et paramètres sans overflow ; pas de clipping implicite.
- Retour `1` après transfert complet et synchronisation requise ; `0` en cas de refus, sans écriture partielle détectable ni fuite de Chip.

### Draw et Restore

- `Draw(Bank,X,Y,Method)` restitue la banque temporaire en **opaque**, avec X destination **multiple de 8 pixels** ; `Restore(Bank,Method)` utilise le dernier X/Y enregistrés par Capture.
- Première version **pleinement à l'écran seulement**, sans clipping et sans arrondi. Hors écran ou mauvais alignement = `0`, back buffer intact. Une voie de clipping rapide pourra être étudiée séparément après mesure.
- Banque et profondeur invalides, `TypeOfMem` non Chip, taille incohérente, back buffer fermé ou non prêt : retour `0`.
- `Erase Bank` ou `Erase` libère la mémoire de la banque après synchronisation des DMA. **Pas de commande CBlock Delete nécessaire**.

Exemple de cycle R68 (**Gate B WinUAE interprétée validée**) :

```amos
_OK=Aga C Block Capture(20,32,48,80,48,2)
' ...dessin d'un panneau...
_OK=Aga C Block Restore(20,2)
' Même banque, nouveau fond, PAS de nouvelle allocation :
_OK=Aga C Block Capture(20,40,48,80,48,0)
_OK=Aga C Block Draw(20,88,96,2)
Erase 20
```

## 4. Format `AGACBLK` temporaire v1 — RAW/DMA, sans RLE

Une banque AMOS DATA, nom natif sur 8 caractères `AGACBLK `. En-tête fixe de **40 octets**, big-endian ; un seul rectangle ; aucun pointeur persistant. Son contenu doit être utilisable directement depuis la Chip RAM, sans compaction/décompaction.

| Offset | Octets | Champ | Valeur |
|---:|---:|---|---|
| 0 | 8 | Magic | `AGACBLK1` |
| 8 | 2 | HeaderSize | `40` |
| 10 | 2 | Version | `1` |
| 12 | 2 | Depth | `1..8` |
| 14 | 2 | Flags | `0` (RAW uniquement) |
| 16 | 4 | OriginalX | dernier X capturé |
| 20 | 4 | OriginalY | dernier Y capturé |
| 24 | 4 | Width | multiple de 8 pixels, >0 |
| 28 | 4 | Height | >0 |
| 32 | 4 | RowStride | `2 * ceil(Width / 16)` octets par ligne et plan |
| 36 | 4 | PlaneBytes | `RowStride * Height` |
| 40 | variable | Pixel data | `Depth` plans consécutifs, `PlaneBytes` octets/plan |

**Longueur exacte** : `40 + Depth × RowStride × Height`, avec calcul 32 bits vérifié et comparaison à `Length(Bank)`. `RowStride` est **pair** pour la DMA 16 bits. Les pixels sont en **planar, bit 15 en premier**, dans chaque mot. Les bits supplémentaires (si Width est multiple de 8 mais pas de 16) sont nuls à la capture, et **ne sont jamais écrits hors du rectangle logique** lors du dessin (masque de dernier mot au Blitter ou chemin CPU de bord). L'adresse de début `Start(Bank)+40` doit être paire et physiquement Chip.

Pour rappel :
- 16×16×8 plans : **256 octets de pixels + 40** octets d'en-tête.
- 24×16×8 plans : **512 + 40** octets (stride word de 4 octets pour 24 pixels, padding DMA inclus).
- 320×256×8 plans : **81 920 + 40** octets.
- Hors surcoût AMOS. **La mémoire Chip est limitée** : refuser proprement les allocations impossibles et récupérer toute allocation partielle.

Le format privilégie les copies **par mots et longs quand l'alignement le permet**. La mise en page ne doit pas imposer un transcodage de bitplanes à chaque `Draw`. Un copier-coller CPU ou une opération Blitter doivent produire les **mêmes pixels**.

## 5. Synchronisation et sécurité

1. **Prévalidation** des numéros, types/noms/entêtes de banque, dimensions, largeur/positions multiples de 8, taille totale/overflow, éventuel réemploi, plage mémoire, plans, pitch, profondeur et écran.
2. **Allocation Chip réelle** : mécanisme AMOS déjà utilisé par R66 (`Bnk.Reserve` avec demande Chip), puis contrôle du **premier et du dernier octet** par `TypeOfMem & MEMF_CHIP`. Si échec sur création, effacer uniquement la banque nouvellement créée, jamais une banque étrangère. Les références AMOS fournissent les bons flags ; ne pas supposer que `Bank To Chip` suffit.
3. **Back buffer AGA privé** : appliquer `Safe` et `WaitBlit` suivant le contrat de l'extension avant de lire ou écrire des bitplanes, sans `Wait Vbl` ni `Swap` implicites.
4. **Blitter DMA** : gérer correctement ses masques gauche/droite, décalages éventuels de 8 bits, strides/modulos, bornes, `WaitBlit` et l'usage sûr via les appels système existants. Même avec X multiple de 8, **une origine X=8 n'est pas alignée sur un mot 16 bits**. Aucun octet externe au rectangle ne doit changer.
5. **Recapture** : le bloc reste Chip et de même taille. Les paramètres invalides doivent échouer avant la première écriture. Ne jamais réallouer silencieusement un bloc de dimensions différentes.
6. **Pas de pointeur privé conservé** après appel, afin de ne pas devenir invalide après déplacement / suppression d'une banque AMOS.
7. **Compiler/AP20** : préserver A3/D2/D3/pile, relogeabilité et règles de `EXTENSION_SOURCE_RULES.md` ; une simulation CPU ne vaut pas validation Compiler WinUAE.

### Coût critique à mesurer

Le choix d'un stockage Chip et sans compression est **un choix d'architecture demandé** ; sa vitesse réelle doit être **mesurée**, pas proclamée. Les comparaisons doivent inclure `Safe` / `WaitBlit`, la préparation du Blitter et la fin DMA, pas seulement le lancement.

| Scénario | Comparaison |
|---|---|
| Taille | 8×8, 16×16, 24×16, 64×48, 128×96, 320×64 |
| Origine X | 0 et 8, 16 et 24 ; comparer granularité 8 vs alignement 16 pixels |
| Contenu | Uniforme, motifs et bruit (RAW, coût de copie inchangé) |
| Exécution | CPU Chip→Chip vs Blitter Chip→Chip, **Capture** et **Draw** séparés |
| Réemploi | Première Capture (allocation comprise) vs 100/1000 recaptures sans allocation |
| Matériel simulé | WinUAE 68020 et 68030 sans JIT, configurations identifiées |
| Intégrité | Pixels du rectangle identiques, pixels voisins inchangés, Chip Free restaurée après `Erase` |

**Optimiser les appels répétés**, pas uniquement les allocations ; un chemin CPU pour petits blocs et un chemin Blitter pour grands blocs peuvent coexister sans deuxième banque.

## 6. Gates et suite de M18

- **Gate A : PASS** — 48 cas natifs M68000, modèle planaire CPU8/CPU16/Blitter, mémoire Chip, réemploi, erreurs, ABI et CI.
- **Gate B : PASS** — scénarios R68 et PERF-02 sur WinUAE interprété 68020/68030 **sans JIT**, visuel, copies, reprise de banque, comparaisons planaires, mémoire, fermeture et `RESULT 1`. [Rapport PERF-02](M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md).
- **Gate C : PASS** — essai unique AMOS Compiler réel sous WinUAE, [rapport](M18_R68_INTEGRATED_GATE_C_COMPILER_2026-11-13.md). **Gate D** : AGA physique distincte, non testée.
- **R68 v0.13.13 PROMUE `LAST_GOOD`** : Gates **A/B/C PASS** sur les scénarios validés, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Après M18 : 68020+ puis `c2p.library`, sans mélange de chantiers.

**Le sens du correctif est fixé par l'auteur : performances, banque temporaire en Chip, alignement en pixels.** **Signatures R68 validées ; décision du 13/11/2026 : choix CPU8/CPU16/Blitter laissé au programmeur par `Method`, aucune sélection automatique selon CPU, dimensions ou benchmark.** La bibliothèque R68 a passé les Gates A/B/C et est promue ; Gate D physique reste non testée.

## 7. Décision finale M18 — méthode explicite, sans automatisme (13/11/2026)

**Décision de l'auteur : laisser le choix au programmeur AMOS.** `Method` est un argument **obligatoire** de `Aga C Block Capture`, `Aga C Block Draw` et `Aga C Block Restore`. Aucun `Method=3` ou mode `Auto` : l'extension n'effectue **aucune détection CPU**, aucun calcul de seuil, aucune substitution silencieuse de méthode.

| `Method` | Voie native | X et largeur (pixels) | Usage |
|---:|---|---|---|
| `0` | CPU8 / octets planaires | Multiples de **8** | Accès à des coordonnées X de 8 pixels non alignées sur 16 |
| `1` | CPU16 / mots planaires | Multiples de **16** | Voie CPU alignée, parfois plus rapide sur certaines tailles/CPU |
| `2` | Blitter Chip→Chip | Multiples de **8** | Bonne option pour la majorité des rectangles mesurés, sans être imposée |

**Motif :** [PERF-02 sans JIT](M18_R68_CBLOCK_PERF_02_WINUAE_2026-11-13.md) confirme que le Blitter est souvent plus rapide mais **pas toujours**, et que des écarts de 1 à 3 ticks ne justifient pas une politique automatique dépendante de WinUAE. Le code appelant choisit explicitement une méthode valide pour ses contraintes. Les refus d'alignement ou de zone restent `0`, sans clipping ni réinterprétation automatique.

**Aucune modification du binaire R68** n'est nécessaire pour cette décision. [Exemple autonome R68](../examples/cblock_chip_r68/README.fr.md) : source prête à être essayée en AMOS interprété, **pas encore validée indépendamment sous WinUAE**. Les exemples validés et l'ASC PERF-02 restent archivés sans modification. **Gate C réelle PASS** ([rapport](M18_R68_INTEGRATED_GATE_C_COMPILER_2026-11-13.md)), Gate D matérielle non testée ; R68 promue `LAST_GOOD`, R63 historique préservée.
