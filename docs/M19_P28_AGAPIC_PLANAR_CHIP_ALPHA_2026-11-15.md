# M19 P2.8 — prototype de cache AGAPIC planaire a alpha independant

**15 novembre 2026.** Developpement **sur `main` uniquement**, sans modifier le binaire actif R87 v0.13.32 (`dist/AMOSPro_AGA.Lib`, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`), ni la R84 `LAST_GOOD` (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). **Pas de promotion automatique.**

## Objet, limites et sources reelles

Les mesures WinUAE P2.7 [archivees](../benchmarks/RESULTATS_M19_P27_R87_CPU_RLE_FICON_BLITTER_2026-11-15.md) demontrent, sur un meme motif 16x16 : **-59,31 % Runtime / -62,07 % Compiled** en passant du dessin AGAPIC RLE au dessin FICON8 planaire deja decode ; le Blitter opaque avec source pre-stagee reduit ensuite les ticks de **41,67 % / 45,90 %**. Ces valeurs sont des **temps de dessin uniquement** : ni alpha general, ni copies reelles depuis un cache Chip, ni FPS complets n'ont ete qualifies par P2.7.

P2.8 poursuit **une etape discriminante** sans gonfler le binaire actif :

- `tools/m19_p28_agapic_planar_cache.py` : convertit les **vrais formats AGAPIC v1/v2** par les parseurs du depot (`m16_agapic`, `m16_agapic_v2`), en un **snapshot planaire** immutable. Tous les groupes RLE sont valides **avant** de produire une banque. Conserve explicitement le masque 1 bit **independant de la couleur** : pixel 0 opaque ou pixel colore invisible restent possibles.
- **Format AGPC v1 interne, 72 octets d'en-tete** : dimensions, profondeur, stride planaire, ModeID v2, offsets mask/planes, longueur totale, generation explicite, marqueur ready et SHA256 des octets source. Les images non multiples de 16 sont completees par des **bits zero** a droite. Chaque plan a un stride word-aligne de `2 * ceil(w / 16)` octets.
- **Source AGAPIC et cache sont des banques distinctes** ; `make_cache_abk()` produit un vrai conteneur AMOS DATA (`AGPCACHE`) a ownership explicite. Un `Erase/Load` ou changement de donnees source exige **une remise en banque explicite** pour obtenir la nouvelle image. La presence du cache n'implique **aucun pointeur vivant** vers la source ; l'empreinte source est verifiable a l'etape de staging.
- **Chip RAM = validation runtime obligatoire** : la demande de banque `flags=3` est une preference, **pas une preuve `TypeOfMem(... ) & MEMF_CHIP`**. Tant que l'allocation Chip/validite des pointeurs n'est pas verifiee par le futur AP20, le resultat de `native_chip_slot_16x16x8` est **un bloc de donnees**, jamais un pointeur DMA utilisable directement.
- Le bloc 16x16/8 plans (`32 octets de masque + 8*32 de plans`, total **288 octets**) peut alimenter sans changement le **vrai coeur 68000 M18/P5** `tools/m18_ficon16_chip_blit_emit.py`. Celui-ci choisit `BltMaskBitMapRastPort`, verifie les pointeurs Chip en `TypeOfMem`, l'image inactive, le clipping, `WaitBlit`, les registres et le retour sans toucher au buffer avant. Les **tests sont effectues dans Unicorn avec services OS/DMA simules**, pas sur le Blitter reel. Le coeur M18 **n'est pas une commande accessible dans R87**. **ATTENTION : le wrapper M18 `m18_ficon_chip_ap20_emit.py` n'est PAS reutilisable a l'identique** : sa validation `masque == OR des huit plans de couleur` est fausse pour un masque alpha AGAPIC independant (par exemple couleur 0 visible, couleur 6 invisible). Il faudra un nouveau wrapper AGPC avec validation d'ownership, limites et alpha sans cette contrainte.

## Ce qui est effectivement implemente en P2.8 P0

- **Snapshot de largeur/hauteur/depth variables, de 1 a 8 plans** : decodage du RLE AGAPIC v1/v2 et preparation planaire au chargement (hors frame), alpha binaire preserve.
- Lecteur strict AGPC, validation de version, marqueur ready, offsets, total, zero-padding, generation, hash de source et ModeID v2. Le `mode 1` est interdit si l'AGAPIC source ne contenait pas de masque.
- Dessin CPU de reference, clipping, coordonnees signees 16 bits, transparence independante.
- Tests multi-tailles (dont largeur 17/31/37), profondeur 1/4/8, positions arbitraires, 0 opaque, couleur non-nulle transparente, refus de corruption/banque absente, snapshots v1/v2.
- **Gate A native reutilisee** : execution du coeur M18/P5 sur des slots AGPC 16x16x8 par Unicorn, tests de pixels reels en memoire 68k avec hook de DMA independent, protections front/guard/memoire Chip ; **pas de production de R88 ni d'appel AMOS nouveau**.

### Phase suivante, non encore validee

1. **Pont AP20 R88 candidat NON publie** : creation/remplissage d'une banque AGPC **reellement Chip**, validation de son en-tete et marqueur ready, controle `GetAdr`, flags historiques/chargement, `TypeOfMem` des deux bouts du bloc, `Safe` du back buffer ; appel au coeur M18 apres verification complete. Conserver ABI, taille maximale 65 534 octets par unite et la portee BSR.W/relocation du Compiler V2.
2. **Extension pour largeur quelconque** du moteur Blitter (16x16 seul dans M18/P5), source planaire contigue, mask aligne, `BltMaskBitMapRastPort`, clipping et capture identique au rendu CPU ; ne pas assimiler une copie opaque BlitCopy a un rendu masque.
3. **Benchmark reel complet** : sources identiques, cache construit une fois et cout de staging distinct, 4/8/16/32 Bobs, frame fond+dessin+`Aga Swap` et `Aga Wait Vbl` (separes dans les journaux), tests des deux back buffers, erreurs et Guru, medianes et FPS reels. **WinUAE Gates B/C de P2.8 non executees.**

## Etats de validation

| Controle | Statut |
|---|---|
| P2.7 R87 Runtime et Compiled | **PASS**, journaux archivés, scope draw-only |
| P2.8 P0 modèle/cache v1-v2 | **PREPARE**, en attente CI verifiee |
| P2.8 coeur M18/P5 réutilisé sous Unicorn | **PREPARE**, en attente CI verifiee |
| P2.8 AP20/ABI candidate R88 | **NON IMPLEMENTE** |
| P2.8 WinUAE Runtime / Compiled | **NON TESTE** |
| P2.8 FPS effectifs, DAC/Amiga physique | **NON TESTE** |

Le verdict Gate A doit porter uniquement sur le **modele et coeur deja present**, pas sur un backend AP20 qui n'existe pas encore. Conserver les resultats et sources exacts ; les banques natives R84 et la candidate R87 **ne changent pas**.

## Avancement P2.8 P1 — R88 expérimentale (15/11/2026)

Le prototype AP20 `tools/m19_p28_agpc_ap20_emit.py` et le constructeur **sans option d'écriture dist** `tools/build_m19_p28_r88_in_memory.py` produisent R88 v0.13.33 (75 040 octets, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`), API tentative `Aga Cache Blit(CacheBank,X,Y,Mode)`. Le cœur de Blitter masqué M18/P5 est réutilisé après validation de la banque AGPC, vraie Chip RAM, des adresses du back buffer, du Safe et de la compatibilité v2 ModeID. **Le contrôle obsolète `masque == OR des plans couleur` a été supprimé.**

[Gate A MC68020 sous Unicorn](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43730486672) : **130 scénarios réels 68k interprété/relocations Compiler V2 PASS**, 288 comparaisons de format AGPC P0 PASS, 48 scénarios du cœur M18 PASS. Correctif d'un faux négatif du modèle : utiliser le **stride physique réel** (18 octets en mémoire de test, contre 10 octets utiles) lors des comparaisons d'oracle pixel.

Le [banc P2.8](../tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc) a passé le préflight AMOS strict (ce n'est pas un essai WinUAE) et vise 8 parités avec masque indépendant, 12 séries de dessin seul et 12 séries de **frames complètes avec décor, VBL et Swap**, 24 frames par série. Le bundle créé après Gate A contient R88 temporaire, ASC et quatre banques v1/v2 AGAPIC+AGPC. **Gates B/C R88 NON TESTÉES et FPS non mesurés.** Aucune bibliothèque R87/R84 modifiée ni promue.
