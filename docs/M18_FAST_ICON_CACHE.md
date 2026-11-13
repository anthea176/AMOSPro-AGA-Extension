# M18 — Cache des Fast Icons AGA 256 couleurs

## Objet et état d'implémentation

Le cache accélère l'affichage répété d'icônes **16×16 pixels / 8 bitplanes / 256 couleurs** en séparant la **source en Fast RAM**, la **préparation en Chip RAM** et les **copies par Blitter**. Il ne remplace pas les banques Icon classiques d'AMOS, ni les banques AGAPIC RLE.

- **R61 :** `Aga F Icon(Bank,IconID,X,Y,Mode)`, chemin CPU direct depuis `FICON8 ` vers le back buffer AGA, validé WinUAE en interprété et compilé. La banque source peut être en Fast ou en Chip.
- **R62 :** `Aga F Blit(CacheBank,IconID,X,Y,Mode)`, chemin Blitter depuis un cache `FICHIP8 ` pré-stagé en Chip. Gate A CPU/OS simulé PASS ; **essai WinUAE interprété du 13/11/2026 : RESULT 0**, tous les BLIT=0. Pas de Gate B validée, Gate C différée.
- **R63 :** correctif de compatibilité des flags natifs des banques AMOS rechargées (valeur 0 déjà constatée pour AGAPIC), à qualifier séparément. L'absence de plantage n'est pas une preuve de rendu ou de vitesse.
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

1. **Charger** la source `FICON8` (par exemple banque 10) et un cache `FICHIP8` préparé (par exemple banque 11). **Actuellement**, la préparation se fait sur PC avant le `Load`, à l'aide de [`tools/m18_ficon_chip_cache.py`](../tools/m18_ficon_chip_cache.py) : `--prepared --write M18_FICHIP8_SAMPLE_BANK11.abk`.
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

## Politique de validation M18

**L'auteur ne souhaite pas recompiler sous AMOS à chaque fonction ou correctif.** Développement : tests natifs automatisés + **tests manuels WinUAE en interprété**. **Une seule Gate C manuelle avec un nouvel exécutable AMOS Compiler sera faite à la fin du chantier M18**, sur la candidate finalisée. Ne jamais déclarer Gate C PASS sur la seule base des simulations Compiler V2 en CI.

Références internes : [contrat P5](M18_FICON16_NATIVE_P5.md), [émission AP20](../tools/m18_ficon_chip_ap20_emit.py), [noyau Blitter](../tools/m18_ficon16_chip_blit_emit.py), [tests natifs](../tools/test_m18_r62_chip_blit_gate_a.py), [règles de source](../EXTENSION_SOURCE_RULES.md).
