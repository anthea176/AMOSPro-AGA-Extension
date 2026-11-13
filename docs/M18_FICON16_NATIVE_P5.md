# M18/P5 — Cache Chip persistant et Blitter masqué, Gate A expérimentale

**État : code en phase Gate A uniquement, non installé dans R61.** R61 v0.13.6 validée B/C reste candidate active ; R60 `LAST_GOOD` reste figée. **Aucune nouvelle commande AP20 ni ASC actif.**

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
