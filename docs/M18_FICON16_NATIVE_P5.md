# M18/P5 — Cache Chip et Blitter masqué (R62 / correctif R63)

**État 13/11/2026 :** R63 v0.13.8 est la [candidate active unique](../dist/AMOSPro_AGA.Lib), **38 736 octets**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`, [Gate A CPU 260 cas PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43429500351). **Gate B WinUAE interprétée en attente ; Gate C manuelle reportée à la fin de M18 ; D physique non faite.** R62 v0.13.7 avait Gate A PASS mais **Gate B interprétée ÉCHEC (BLIT=0, RESULT=0)**. R61 A/B/C PASS archivée ; R60 LAST_GOOD protégée. [Contrat complet du cache](M18_FAST_ICON_CACHE.md).

**Document technique de référence : [fonctionnement, cycle de vie, mémoire et limites du cache](M18_FAST_ICON_CACHE.md).**

## Principe et formats

La banque source `FICON8 ` conserve les icônes 16×16×8 plans ; le CPU peut la lire en Fast RAM. Le Blitter, qui ne peut pas lire cette mémoire, travaille sur une banque DATA distincte `FICHIP8 ` **réellement allouée en Chip RAM**. Le cache ne dépend pas des bitmaps écran et survit aux `Aga Swap`. Une banque de 4 icônes contient **1 168 octets** de payload (12 octets d'en-tête + 4 × [288 octets par icône + 1 octet de validité]) et un fichier ABK de **1 188 octets**.

Chaque slot cache est composé d'un masque de visibilité **32 octets** et de **8 plans contigus × 32 octets**. Les bits de couleur zéro deviennent invisibles si `Mode=1`; le mode 0 copie toutes les couleurs. Le bit de validité (stocké après tous les slots) doit être à 0 pendant la préparation et à 1 seulement après une copie complète.

**Actuellement, le staging se fait sur PC**, avec [`m18_ficon_chip_cache.py`](../tools/m18_ficon_chip_cache.py) et l'option `--prepared`. Le [noyau natif P2 expérimental](../tools/m18_ficon16_native_stage_emit.py) ne constitue pas une commande AMOS de staging à chaud ; allocation, éviction et re-préparation dynamique ne sont **pas intégrées**. La source peut être modifiée sans mettre le cache à jour : il faut alors recréer/recharger le cache.

## API et sécurité native

Le [wrapper AP20](../tools/m18_ficon_chip_ap20_emit.py) expose `_OK=Aga F Blit(CacheBank,IconID,X,Y,Mode)`. Il résout la banque par `Bnk.GetAdr`, contrôle enveloppe/nom/longueur/slots/masques/validité, cible uniquement le **back buffer privé inactif** et acquiert `Safe` de façon non bloquante. Un appel invalide renvoie 0 sans dessin ; un appel valide entièrement hors écran doit renvoyer 1 sans DMA.

Le [noyau Blitter M68000](../tools/m18_ficon16_chip_blit_emit.py) prépare un `BitMap` de source et un `RastPort` local (`InitRastPort`), appelle `BltBitMapRastPort` (opaque, minterm `$C0`) ou `BltMaskBitMapRastPort` (masqué, minterm `$E0`, masque en Chip), puis `WaitBlit` avant de rendre la main. Les LVO sont `-198`, `-606`, `-636` et `-228`. Il n'appelle aucun `Swap` ou `Wait Vbl`. Référence des minterms : [AmigaOS Graphics Minterms](https://wiki.amigaos.net/wiki/Graphics_Minterms).

**La préférence mémoire ABK ne suffit pas : `TypeOfMem(MEMF_CHIP)` doit confirmer l'accessibilité DMA réelle de la banque.** Le wrapper ne doit pas confondre ce résultat avec le champ `Flags` de l'en-tête DATA native d'AMOS, situé à `Start(bank)-12`.

## Test utilisateur R62 interprété : échec ciblé

Capture du 13/11/2026 : `OPEN/DB/SW0/SAFE=1`, `ICON=1/1/1/1`, `SHIFT=1`, **`BLIT=0/0/0/0`, `BCLP=0/0/0/0`, `BOUT=0`, `RESULT=0`**, `CLOSE=-1`, `NOS=0`, **`CHIP BEFORE/END=1 796 480/1 796 480`**. Le rejet du cas Blitter entièrement hors écran se produit probablement avant les appels graphics.library, lors du contrôle banque ou écran.

La R62 exigeait `Flags=3` sur l'en-tête DATA natif. Un problème équivalent avait déjà été diagnostiqué et corrigé pour AGAPIC : après `Load`, WinUAE a été observé avec **`Flags=0`** (voir [`m16_image_draw_r45_emit.py`](../tools/m16_image_draw_r45_emit.py)). Le correctif R63 autorise les classes DATA `0/1/3` **uniquement quand la zone est réellement en Chip**, et refuse toujours les autres types. **Cette cause reste à confirmer par un essai WinUAE interprété** ; ne pas enregistrer Gate B PASS avant un `RESULT 1`.

## Validation et planning

- [Cache hôte](../tools/test_m18_ficon_chip_cache.py) : validation structure/validité, 4 slots et équivalence CPU.
- [Noyau M68000 et ABI OS simulée](../tools/test_m18_ficon16_chip_blit.py) : masqué/opaque, clipping, `WaitBlit`, source non-Chip refusée.
- [Wrapper AP20 R62](../tools/test_m18_r62_chip_blit_gate_a.py) : 160 cas interpréteur/Compiler V2 **simulés**, sans preuve WinUAE.
- [Correctif R63](../tools/test_m18_r63_chip_blit_gate_a.py) : tests natifs des flags rechargés `0/1/3`, protections Chip toujours actives.
- **Pas de benchmark Fast Icon masqué réel pour cette version**, et surtout pas de comparaison CPU/Blitter avant de mesurer séparément le coût de préparation Fast→Chip.

**Règle auteur : durant le chantier M18, essais manuels WinUAE en interprété ; une unique Gate C Compiler manuelle sera réalisée à la fin du chantier**, une fois le moteur et l'ASC finalisés. Les simulations Compiler en CI ne remplacent pas cette Gate C.

Les binaires et tests actifs suivent uniquement [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md) : une seule candidate dans `dist/AMOSPro_AGA.Lib`, un seul ASC dans `tests/current`, et la R60 `LAST_GOOD` conservée.
