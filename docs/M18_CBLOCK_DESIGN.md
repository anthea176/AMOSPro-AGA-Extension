# M18 — CBlock AGA : capture/restauration rapide en Chip RAM

**Décision auteur du 13/11/2026 : priorité absolue à la VITESSE ; banque temporaire en CHIP RAM ; alignement horizontal de 8 PIXELS si profitable.** Il s'agit bien de **8 pixels, pas de 8 octets**. Le précédent contrat « Fast RAM + RLE + pixel exact » est **abandonné**. Ce document décrit le contrat désormais **implémenté dans R68** et encore en attente de validation WinUAE (Gate B).

**État R68 v0.13.13 : unique candidate `dist/AMOSPro_AGA.Lib`, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`, 64 commandes / 71 entrées AP20 ; Gate A native M68000 48 cas PASS ; Gate B WinUAE interprétée À FAIRE sur [l'ASC unique](../tests/current/M18_R68_CBLOCK_CHIP_01.asc). R63 `LAST_GOOD` protégée ; une seule Gate C manuelle à la fin de M18, D matérielle non testée.**

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

## 3. API AMOS implémentée en R68 (Gate B à valider)

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

Exemple de cycle R68 (**non validé sous WinUAE à ce stade**) :

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

- **Gate A** (après validation des signatures) : modèle des copies planaires 8/16, masques de dernier mot, absence de corruption des voisins, vrais chemins natifs 68000, allocations Chip, réemplois, invalides, ABI/AP20 + CI ; tous les cas doivent vérifier **premier/dernier octet**.
- **Gate B** : un seul nouveau test dans `tests/current/`, sous WinUAE **en interprété** ; allocation/reprise de banque, capture et restauration, trois profondeurs si supportées, comparaisons CPU/Blitter et mesure de temps, fermeture propre, `RESULT 1` et `CLOSE RETURNED` ; pas de nouvelle compilation AMOS.
- **Gate C** : **un seul test Compiler manuel à la toute fin de M18**, sur binaire alors finalisé ; **Gate D** : AGA physique distincte.
- **R67** reste la bibliothèque candidate non promue ; **R63 LAST_GOOD** inchangée. Après M18 : 68020+ puis `c2p.library`, sans mélange de chantiers.

**Le sens du correctif est fixé par l'auteur : performances, banque temporaire en Chip, alignement en pixels.** Les **signatures** et les **choix du chemin CPU/Blitter selon taille** restent à confirmer par tests. Ne pas annoncer une R68 créée par ce seul document.
