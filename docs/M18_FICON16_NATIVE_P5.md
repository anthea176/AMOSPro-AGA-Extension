# M18/P5 — Cache Chip persistant et Blitter masqué, Gate A expérimentale

**État : Gate A CPU/ABI du cache Chip et Blitter PASS sur [CI 43426447385](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43426447385).** R62 v0.13.7 candidate de travail [dist/AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib), **38 732 octets**, SHA256 `9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6`, **Gates B/C WinUAE et D physique non encore testées**. R60 LAST_GOOD protégée, R61 A/B/C PASS archivée. R61 v0.13.6 validée B/C reste candidate active ; R60 `LAST_GOOD` reste figée. **Aucune nouvelle commande AP20 ni ASC actif.**

## Cache Chip géré par AMOS

Le [format hôte FICHIP8](../tools/m18_ficon_chip_cache.py) réserve explicitement une banque DATA AMOS `FICHIP8 ` (**flags=3, demande mémoire Chip**) qui appartient à AMOS et non aux ScreenBuffers. Elle persiste donc entre Swap, Screen Close et Screen Open ; l'application libère la banque par `Erase Bank`. Elle contient un en-tête 12 octets (taille, compte, 16×16, profondeur 8), `count × 288` octets de slots planaires et `count` octets de validité (un marqueur par icône).

Chaque slot : **32 octets de masque de visibilité (bit 1 = copier) + huit plans contigus de 32 octets**. Le [staging natif P2](../tools/m18_ficon16_native_stage_emit.py) transforme la source Unity `FICON8 ` de Fast/Chip vers ce slot ; les métadonnées de validité doivent être mises à 1 seulement après copie complète. Recharger une banque source implique un nouveau staging, indépendamment de la durée de vie de la banque Chip.

**Protection DMA :** un drapeau ABK Chip n'est jamais suffisant ; l'adresse effective de toute la source cache doit être de type `MEMF_CHIP` (Exec `TypeOfMem`), avant tout accès DMA. Les slots restent indépendants du front/back buffer.

## Noyau Blitter

Le [noyau M68000](../tools/m18_ficon16_chip_blit_emit.py) reçoit un slot Chip valide, le `BitMap` privé inactif, X/Y et mode. Il prépare un `BitMap` temporaire **2 octets/ligne × 16, huit plans**, un `RastPort` local initialisé avec `InitRastPort`, puis appelle `BltBitMapRastPort` (opaque, minterm `$C0`) ou `BltMaskBitMapRastPort` (transparence couleur zéro, minterm `$E0`, masque 1 bit en Chip). Il applique le clipping aux quatre bords avant DMA ; **`WaitBlit` est systématique après un blit**. Aucune attente VBL, Swap, allocation native ou changement de front.

L'API AmigaOS donne les LVO `InitRastPort=-198`, `BltBitMapRastPort=-606`, `BltMaskBitMapRastPort=-636`, `WaitBlit=-228`. Le noyau ne remplace pas le wrapper AP20 de R61 : **il reste à raccorder les validations des deux banques, du marqueur de staging, du back buffer et de Safe avant publication d'une nouvelle candidate**.

## Validation et suite

- [Test hôte cache](../tools/test_m18_ficon_chip_cache.py) : format ABK, masque, validité, réutilisation de slots, équivalence au rendu CPU P1 sur clipping X/Y.
- [Test noyau M68000](../tools/test_m18_ficon16_chip_blit.py) : instructions natives exécutées sous Unicorn, interception stricte des appels Exec/graphics, vérification des registres LVO, des huit plans contre l'oracle pixel, de WaitBlit et du refus de source Fast. **Pas de DMA physique émulée** : la copie est simulée côté test.

**Gates B/C WinUAE, Gate D matériel et benchmarks 8 plans non réalisés pour P5.** Il faudra un nouveau candidat unique après Gate A native, puis un seul ASC actif ; les fichiers R61 et `LAST_GOOD` ne sont pas modifiés par cette phase.

## Prototype AP20 R62

Le [wrapper natif](../tools/m18_ficon_chip_ap20_emit.py) expose **la future commande `Aga F Blit(CacheBank,IconID,X,Y,Mode)`**, ajoute l'accès live `Bnk.GetAdr`, vérifie l'en-tête `FICHIP8 `, le marqueur de disponibilité et la canonicité des huit plans, puis les pointeurs du back buffer et Safe avant le DMA. Le [builder in-memory R62](../tools/build_m18_r62_chip_blit.py) ajoute un seul token à R61 ; la Gate A couvre les dispositions AP20 interprétée et Compiler V2 simulées, mais **pas WinUAE**.

La [banque prête à charger](../tools/m18_ficon_chip_cache.py) se génère par `python -B tools/m18_ficon_chip_cache.py --prepared --write M18_FICHIP8_SAMPLE_BANK11.abk` ; elle reprend exactement les quatre icônes de la banque Fast R61, puis les prépare en Chip au format 32 octets masque + huit plans contigus. Ce staging est **hors du chrono Blitter** et n'est **pas une nouvelle commande AMOS de staging dynamique** ; aucun gain CPU/Blitter effectif n'est encore revendiqué.

## R62 utilisable sous WinUAE (candidate non promue)

[ASC de test actif unique](../tests/current/M18_R62_CHIP_BLIT_01.asc), [ABK source FICON8](../tests/current/M18_FICON8_SAMPLE_BANK10.abk) et [ABK FICHIP8 Chip pré-stagée](../tests/current/M18_FICHIP8_SAMPLE_BANK11.abk). Le second ABK a 1 188 octets ; son bit DATA/Chip ne dispense pas de la vérification de mémoire physique. La bibliothèque R62 est la **seule candidate** dans `dist/AMOSPro_AGA.Lib`. **Aucune mesure de vitesse Blitter ni comparaison du staging Fast→Chip sous WinUAE n'est encore disponible.**
