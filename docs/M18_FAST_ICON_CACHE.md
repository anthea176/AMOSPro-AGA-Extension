# M18 — Cache des Fast Icons AGA 256 couleurs

## Objet et état d'implémentation

Le cache accélère l'affichage répété d'icônes **16×16 pixels / 8 bitplanes / 256 couleurs** en séparant la **source en Fast RAM**, la **préparation en Chip RAM** et les **copies par Blitter**. Il ne remplace pas les banques Icon classiques d'AMOS, ni les banques AGAPIC RLE.

- **R61 :** `Aga F Icon(Bank,IconID,X,Y,Mode)`, chemin CPU direct depuis `FICON8 ` vers le back buffer AGA, validé WinUAE en interprété et compilé. La banque source peut être en Fast ou en Chip.
- **R62 :** `Aga F Blit(CacheBank,IconID,X,Y,Mode)`, chemin Blitter depuis un cache `FICHIP8 ` pré-stagé en Chip. Gate A CPU/OS simulé PASS ; **essai WinUAE interprété du 13/11/2026 : RESULT 0**, tous les BLIT=0. Pas de Gate B validée, Gate C différée.
- **R63 v0.13.8 :** [candidate de travail active](../dist/AMOSPro_AGA.Lib), **38 736 octets**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`, correction des flags natifs DATA rechargés 0/1/3 avec contrôle `TypeOfMem(MEMF_CHIP)`. [Gate A native 260 cas PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43429500351). **Gate B WinUAE interprétée à faire ; Gate C manuelle en fin de M18.** Le test courant lit `Deek(Start(11)-12)` pour confirmer la cause. Aucun test de performance ou de staging AMOS réel pour ce backend.
- **Pas encore implémentés :** création/re-staging **dynamique** d'un cache depuis AMOS, cache à la demande, éviction automatique, benchmark CPU/Blitter avec coût de staging réel.

## Pipeline et responsabilité mémoire

```text
Banque source AMOS FICON8 (préférence Fast RAM)
        │ lecture CPU uniquement
        ▼
Préparation 16×16 : transposition du masque et des 8 plans
        │ une fois par icône chargée/actualisée
        ▼
Banque DATA AMOS FICHIP8 en Chip RAM
  ├─ masque de visibilité (32 octets)
  ├─ 8 plans bitplanes (8 × 32 octets)
  └─ validité de chaque icône, à la fin de la banque
        │ Aga F Blit (répétable, source déjà en Chip)
        ▼
Blitter → BitMap du back buffer AGA inactif
        │ Aga Swap contrôlé par le programme
        ▼
Écran AGA visible
```

Le **Blitter ne peut pas lire la Fast RAM** sur l'Amiga classique. Il lit donc exclusivement la copie en Chip ; la source originale peut rester en Fast sans être effacée. Les deux ScreenBuffers restent indépendants de la banque cache, qui appartient à AMOS. `Aga Swap` et `Aga Screen Close` ne l'effacent pas ; `Erase <numéro>` libère la banque. `Aga F Blit` attend la fin du transfert par `WaitBlit` avant de rendre la main.

### Deux formats distincts

| Point | Source `FICON8 ` | Cache `FICHIP8 ` |
|---|---|---|
| Emplacement visé | Fast RAM (préférence, non garantie) | **Chip RAM obligatoire** |
| Banque AMOS | DATA 5…65535 | DATA 5…65535 |
| Taille entête de données | 12 octets | 12 octets |
| Taille par icône | 288 octets | 288 octets + **1 octet de validité** |
| Organisation | 16 lignes de (masque de préservation 2 octets + 8 mots de plans) | 32 octets masque de visibilité, puis 8 plans contigus de 32 octets |
| Masque | Bit 1 = préserver le pixel de destination | Bit 1 = **dessiner** le pixel source |
| Accès | `Aga F Icon` CPU | `Aga F Blit` via DMA Blitter |

Le cache stocke tous les slots à la suite, puis **tous les octets de validité à la fin**. Chaque index d'icône est **basé sur 1**. Le champ validité doit être à 0 pendant le staging, puis passer à 1 seulement après l'écriture complète et la validation des 288 octets.

### Consommation de Chip RAM

Données utiles de cache : **`12 + N × 289` octets**, N étant le nombre d'icônes. Il faut ajouter l'enveloppe `AmBk` de 20 octets pour la taille du fichier ABK, ainsi que les métadonnées internes/alignements d'AMOS à l'exécution.

| Icônes | Payload cache Chip | Fichier ABK |
|---:|---:|---:|
| 4 | 1 168 octets | 1 188 octets |
| 32 | 9 260 octets | 9 280 octets |
| 100 | 28 912 octets | 28 932 octets |
| 256 | 73 996 octets | 74 016 octets |

Le format permet théoriquement 4 à 4 096 icônes, **pas** la garantie qu'une telle banque tiendra dans la Chip disponible. Ces tailles ne sont pas les valeurs exactes de `Chip Free` après allocation : AMOS ajoute ses propres frais de gestion.

## Cycle de vie : actuel et futur

1. **Charger** la source `FICON8` (banque 10) et un cache `FICHIP8` préparé (banque 11), puis **forcer le cache en Chip : `Bank Permanent 11` et `Bank To Chip 11` avec AMCAF, après le `Load`**. La préparation des pixels se fait toujours sur PC avec [`tools/m18_ficon_chip_cache.py`](../tools/m18_ficon_chip_cache.py) : `--prepared --write M18_FICHIP8_SAMPLE_BANK11.abk`. Le déplacement en Chip n'est pas le staging des icônes.
2. **Valider** le nom, la longueur, la profondeur 8, l'ID, la canonicité masque/plans et le marqueur prêt. La valeur des flags natifs après `Load` peut différer de la préférence mémoire inscrite dans l'ABK.
3. **Vérifier la Chip réelle**, par `TypeOfMem(MEMF_CHIP)` sur la zone utilisée par le DMA ; ne jamais se fier au seul drapeau `AmBk`. Une banque en Fast ne doit pas être transmise au Blitter.
4. **Dessiner** autant de fois que nécessaire : `Mode=0` opaque (la couleur 0 est copiée) ou `Mode=1` transparente (les pixels d'index 0 laissent le fond intact). X/Y libre au pixel, clipping 4 bords ; `Safe` non bloquant sur le back buffer inactif ; aucun Swap/VBL implicite.
5. **Réutiliser** le cache entre les dessins et les échanges de buffers. Modifier/recharger la banque source ne met **pas** automatiquement le cache à jour.
6. **Invalider/repréparer** les slots concernés quand les images changent. Aujourd'hui il faut régénérer/recharger la banque Chip ; une future commande AMOS de staging devra assurer `ready=0 → copie → ready=1` de manière sûre.
7. **Libérer** la banque cache avec `Erase 11` lorsque le lot d'icônes n'est plus utile. La banque source peut suivre son propre cycle de vie.

**Ce n'est actuellement ni un cache LRU, ni un cache automatique, ni une compression.** La structure est prête pour une future préparation sélective, mais le moteur n'alloue pas et n'évince pas tout seul. Une banque cache ne doit jamais être détruite pendant qu'un transfert DMA l'utilise ; l'API attend `WaitBlit`.

### Exemple R62/R63 (une fois la Gate B validée)

```amos
Load "M18_FICON8_SAMPLE_BANK10.abk",10
Load "M18_FICHIP8_SAMPLE_BANK11.abk",11
Bank Permanent 11 : Rem AMCAF - conserver banque de donnees
Bank To Chip 11 : Rem AMCAF - deplacement reel en Chip RAM

_OK=Aga F Blit(11,2,100,60,0) : Rem opaque
_OK=Aga F Blit(11,3,120,80,1) : Rem couleur 0 transparente
...
Erase 11
Erase 10
```

Ce code suppose que l'écran AGA et le double buffer sont déjà ouverts et que la banque 11 a réellement été allouée en Chip RAM. Le `Load` **écrase les banques 10 et 11** : utiliser des numéros libres et conserver les ressources importantes.

## Performances : mesures à faire

Ne pas comparer un dessin CPU qui lit directement la Fast RAM à un blit depuis des icônes pré-stagées **sans compter la préparation**. Mesurer distinctement :

- `T_stage` : transfert CPU Fast→Chip, préparation du masque et des plans, acquisition/création du cache (à implémenter dans le moteur).
- `T_cpu` : un appel direct `Aga F Icon`.
- `T_blit` : un appel `Aga F Blit` sur cache déjà valide.
- `N` : nombre de redessins d'une icône entre deux invalidations.

Le chemin cache devient favorable si **`T_stage + N × T_blit < N × T_cpu`**, sans oublier la contrainte de Chip RAM. Mesurer opaque/transparent, aligné/décalé, avec et sans clipping, sur 68020/68030 sans JIT ; consigner tailles et résolution de `Timer`.

## Régression WinUAE R62 (13 novembre 2026)

La capture fournie par l'auteur en **AMOS interprété** affiche `OPEN/DB/SW0/SAFE=1`, `ICON=1/1/1/1`, **`BLIT=0/0/0/0`, `BCLP=0/0/0/0`, `OUT=0`, `RESULT=0`**, `CHIP BEFORE/END=1 796 480/1 796 480`, `CLOSE=-1`. Le rejet d'une icône entièrement hors écran indique que le blocage est situé **avant** le DMA ou dans une validation du contexte ; la capture ne mesure pas directement `TypeOfMem` ni les flags du cache.

Le wrapper [R62](../tools/m18_ficon_chip_ap20_emit.py) exigeait `Flags=3` dans la **structure native** de la banque à `Start(11)-12`. Or le projet avait déjà constaté `Flags=0` après rechargement d'une banque AMOS DATA sous WinUAE (voir [`m16_image_draw_r45_emit.py`](../tools/m16_image_draw_r45_emit.py), correctif R46). C'est une **cause probable**, à confirmer par la Gate B d'une version corrigée et, si besoin, la lecture `Deek(Start(11)-12)`. Il faut conserver la vérification physique `TypeOfMem(MEMF_CHIP)` pour ne pas masquer un vrai défaut d'allocation.

## Échecs interprétés R62/R63 et correction du placement de banque (13/11/2026)

La capture R63 confirme que le correctif de la structure native de banque ne suffit pas : `FICHIP 11 FLAGS 0`, **`BLIT 0 0 0 0`, `BCLP 0 0 0 0`, `RESULT 0`** ; source CPU et clipping OK, `CLOSE -1`, Chip Free 1 796 472 avant/après. La Gate A native 260 cas reste PASS, mais **la Gate B réelle de R63 est ÉCHEC**.

La documentation AMOS place les flags à `Start(Bank)-12` ; valeur **0 = Work/Fast**, 3 = Data/Chip. Le code natif R63 accepte déjà ces flags **mais exige une source physiquement DMA-accessible par `TypeOfMem(MEMF_CHIP)`** ; aucune preuve disponible que `Load` a effectivement placé le cache en Chip RAM. Le test hôte précédent simule une banque 11 Chip indépendamment de la valeur des flags : il ne reproduit donc pas une éventuelle allocation réelle en Fast.

**Correction du protocole :** la banque pré-stagée n'était **pas forcée en Chip** après `Load`. La forme ABK seule ne garantit pas son placement effectif. Le [même ASC actif R63](../tests/current/M18_R63_CHIP_BLIT_01.asc) utilise maintenant **`Bank Permanent 11` puis `Bank To Chip 11`** (AMCAF 1.40), après `Load "M18_FICHIP8_SAMPLE_BANK11.abk",11`. Ces commandes convertissent le type en banque permanente et déplacent son allocation en Chip ; **`Start(11)` peut changer**. Il affiche les flags natifs **avant/après**, `BANK 11 START` et les deltas de mémoire **Load + déplacement**, désormais nommés `BANK11 CHIP DELTA` et `BANK11 FAST DELTA`. Ne pas reproduire les essais R62/R63 sans forcer la Chip. Si BLIT reste à 0 après cela, examiner les contrôles natifs au lieu de désactiver la protection DMA. La Gate B de l'essai corrigé reste à faire en interprété.

Ce diagnostic ne constitue pas une modification native, ne prouve pas `TypeOfMem` et n'exige **aucune nouvelle compilation**. R63 .Lib inchangée ; R60 LAST_GOOD intacte.

## Troisième essai interprété R63 : BLIT OK, erreur du harnais Chip Free

**Essai interprété R63 du 13/11/2026, cache forcé en Chip :** `BLIT 1/1/1/1 S1`, `BCLP 1/1/1/1 OUT 1`, `BCBAD 0/0/0`, `ICON 1/1/1/1`, `CLOSE -1`, `FLAGS OLD 0 NEW 3`, `BANK11 CHIP DELTA 1192`, `FAST DELTA 0`. **`RESULT 0` est un faux négatif du programme de test**, et non un retour d'échec Blitter : `_CF0` est relevé avec la banque 11 encore allouée (**1 795 248 octets libres**), `_CF1` après `Erase 11` (**1 796 440 octets**), différence exactement **1 192 octets**. L'ASC actif compare désormais `_CF_BASE` (avant chargement des banques 10 et 11) à `_CF1` (après leur effacement), et affiche séparément `_CF0` (`CHIP CACHE ACTIVE`). **R63 .Lib inchangée, Gate B finale à confirmer avec l'ASC corrigé et un contrôle visuel, Compiler manuel reporté à la fin de M18.**

Les captures démontrent les retours des commandes mais pas l'exactitude pixel par pixel du rendu graphique. Aucune régression native ni modification de la bibliothèque n'est requise pour ce faux échec ; le test corrigé reste à exécuter.

## Politique de validation M18

**L'auteur ne souhaite pas recompiler sous AMOS à chaque fonction ou correctif.** Développement : tests natifs automatisés + **tests manuels WinUAE en interprété**. **Une seule Gate C manuelle avec un nouvel exécutable AMOS Compiler sera faite à la fin du chantier M18**, sur la candidate finalisée. Ne jamais déclarer Gate C PASS sur la seule base des simulations Compiler V2 en CI.

Références internes : [contrat P5](M18_FICON16_NATIVE_P5.md), [émission AP20](../tools/m18_ficon_chip_ap20_emit.py), [noyau Blitter](../tools/m18_ficon16_chip_blit_emit.py), [tests natifs](../tools/test_m18_r62_chip_blit_gate_a.py), [règles de source](../EXTENSION_SOURCE_RULES.md).
