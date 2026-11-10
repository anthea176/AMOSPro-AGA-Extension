# M3b — Écrans AGA persistants, résolutions et profondeurs paramétrables

**État 31/10/2026 :** M3b-1 v0.0.4 initiale a **échoué sous WinUAE interprété** (`M3B OPEN=0`) à cause de l'ordre des paramètres. La **R1 corrigée** est publiée, 13 tests statiques réussis, **sans validation WinUAE R1 à ce stade**. Voir [le correctif R1](M3B_V004_R1_FIX.md). La v0.0.3 M3a est la base expérimentale confirmée sous WinUAE, en interprété et en compilé, pour un écran PAL 320×256×8 et la séquence `Amos To Back` → `Aga Demo` → `Amos To Front`.

## Exigence de conception

**Ne pas limiter l'extension définitive à 320×256 / 256 couleurs.** L'AGA permet différentes résolutions et profondeurs ; M3a ne démontrait qu'une seule combinaison. L'interface M3b doit accepter les paramètres d'écran dès sa conception, sans imposer un nouveau nom de commande par résolution.

AGA : 1 à 8 bitplanes en mode indexé (2, 4, 8, 16, 32, 64, 128 ou 256 couleurs simultanées), avec palette RGB24 (16 777 216 couleurs de référence). Ce n'est PAS un framebuffer RVB direct 24 bits. Les modes spéciaux EHB (6 plans, 32 couleurs + 32 demi-intensité), HAM6 (6 plans) et HAM8 (8 plans, jusqu'à 262 144 combinaisons de couleurs à l'écran, contraintes de voisinage) demandent un traitement séparé.

## Familles de modes à couvrir progressivement

| Famille | Dimensions PAL standard | Autres variantes | Profondeurs indexées |
| --- | --- | --- | --- |
| LowRes | 320×256 | 320×200 NTSC ; entrelacé 320×512 PAL / 320×400 NTSC | 1–8 plans |
| HiRes | 640×256 | 640×200 NTSC ; entrelacé 640×512 PAL / 640×400 NTSC | 1–8 plans selon mode disponible |
| SuperHiRes | 1280×256 | 1280×200 NTSC ; modes entrelacés | Jusqu'à 8 plans si réellement disponible et supporté |
| Moniteurs 31 kHz | Modes DBLPAL / DBLNTSC et variantes de moniteurs | Selon pilote et machine | À interroger auprès d'AmigaOS |
| EHB | Suivant le ModeID EHB | LowRes, HiRes, etc. selon disponibilité | 6 plans, 64 couleurs liées |
| HAM6 / HAM8 | Suivant le ModeID HAM | Résolutions supportées par AGA et l'OS | 6 / 8 plans, encodage non indexé ordinaire |

**Ce tableau donne des familles matérielles, pas une garantie** : tout couple largeur/hauteur/profondeur/ModeID devra être validé via la display database, les limitations de chipset et la mémoire disponible. Les modes SuperHiRes à huit plans peuvent être particulièrement coûteux en bande passante.

## API AMOS proposée — à valider côté tokens/compilateur

Pour éviter une API bloquée sur 320×256, exposer une ouverture paramétrée par **largeur, hauteur, nombre de couleurs et ModeID** :

```amos
If Aga Detect<>0
   _OK=Aga Screen Open(320,256,256,$00021000)
   If _OK<>0
      Amos To Back
      Aga Screen Pattern
      Wait 150
      Amos To Front
      Aga Screen Close
   End If
End If
```

**Ceci est une proposition de syntaxe, pas encore une commande disponible.** Le ModeID `$00021000` désigne PAL LowRes. Les modes PAL HiRes `$00029000` et HiRes interlacé `$00029004` seront parmi les premières variantes à essayer. Un complément futur pourra choisir automatiquement le meilleur ModeID via les propriétés souhaitées.

- `Aga Screen Open(width,height,colours,modeId)` : fonction numérique. Convertir `colours` (puissance de deux de 2 à 256) en 1–8 plans ; refuser paramètres incohérents ou mode indisponible. Ne pas ouvrir deux écrans pour un seul contexte.
- `Aga Screen Pattern` : instruction sans argument qui dessine dans l'écran ouvert ; doit respecter sa largeur, hauteur et profondeur effectives, pas des constantes 320/256/8.
- `Aga Screen Close` : instruction idempotente, sans double libération.
- `Aga Set Colour(index,r,g,b)` : fonction future de palette, indices 0..(colours−1), composants RGB 0..255, via graphics.library. Sémantique HAM/EHB distincte et explicitement documentée.
- `Aga Screen Info` / `Aga Screen Ready` : diagnostics éventuels, seulement après validation des premières commandes.

**Le mode spécial (HAM8 / EHB) ne doit pas être représenté comme un simple nombre de couleurs** : il faut une sélection par ModeID ou par un paramètre `mode` explicite. Dessiner un indice de palette en HAM8 ne donne pas le même comportement qu'en mode indexé.

## Contrôle des ModeID

- Utiliser `SA_DisplayID` pour `OpenScreenTagList`, ne pas bricoler directement BPLCON0/BPLCON3 ou le Copper AMOS.
- Valider d'abord le mode avec `ModeNotAvailable`, puis consulter `FindDisplayInfo` / `GetDisplayInfoData` (`DTAG_DISP` et `DTAG_DIMS`) pour connaître les dimensions et le nombre maximal de plans ; `BestModeIDA` pourrait ultérieurement proposer un mode compatible automatiquement.
- Refuser proprement un ModeID invalide, une profondeur supérieure au maximum, une demande impossible en Chip RAM ou l'absence de chipset AGA/Kickstart 3.x.
- Préserver la bascule d'affichage explicite `Amos To Back` / `Amos To Front`, validée sous M3a.

## Consommation minimale de la mémoire image (hors OS / Copper)

Calcul théorique pour une seule image plane : `width × height × bitplanes / 8`, sans les contraintes d'alignement ni les autres allocations.

| Écran | Plans | Bitmap seul |
| --- | --- | --- |
| 320×256, 32 couleurs | 5 | 50 Kio |
| 320×256, 256 couleurs | 8 | 80 Kio |
| 640×256, 256 couleurs | 8 | 160 Kio |
| 640×512, 256 couleurs | 8 | 320 Kio |
| 1280×256, 256 couleurs | 8 | 320 Kio |

En double buffering futur, compter au minimum deux bitmaps, sans oublier les contraintes DMA/Chip RAM.

## État persistant entre appels — condition préalable

1. Résoudre et valider l'ABI de la zone de données de l'extension AMOS 365 ; stocker écran, IntuitionBase, GfxBase, `modeId`, dimensions, profondeur, état, erreurs et ressources de palette. Ne jamais retenir un pointeur de pile.
2. Contrôler les chemins d'ouverture partielle, de double ouverture, de fermeture répétée, d'arrêt AMOS et de sortie d'exécutable compilé.
3. Ne pas toucher aux écrans AMOS ni à son Copper ECS ; la bibliothèque gère uniquement ses propres écrans Intuition.
4. Préserver la version M3a validée octet pour octet dans `archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib`.

## Ordre de réalisation / tests

**M3b-1 est désormais implémenté dans un binaire expérimental** : [instructions de test de la v0.0.4](M3B_V004_TEST.md). L'API est paramétrée dès l'ouverture. Le mécanisme de persistance utilise une zone d'extension et les hooks RESET/END documentés dans les sources AMOS 365. Ces hooks restent à éprouver sous WinUAE, en particulier après interruption.

- **M3b-1** : tester et valider sous WinUAE le cycle persistant actuellement implémenté `Open / Pattern / Close` pour le mode déjà éprouvé PAL 320×256×256, avec paramètres visibles dès l'API ; valider interpréteur et compilateur.
- **M3b-2** : tester profondeurs 16 / 32 / 64 / 128 / 256 couleurs sur 320×256, puis 640×256 et 640×512 ; surveiller mémoire Chip.
- **M3b-3** : NTSC, SuperHiRes et autres ModeID proposés par la display database, selon capacité/bande passante, avec rejet sûr des combinaisons indisponibles.
- **M3b-4** : EHB et HAM8, avec palettes et routines d'écriture adaptées (pas une simple variation de profondeur indexée).
- **M3b-5** : test de répétition (10 cycles), manque de mémoire, mode invalide, arrêt AMOS en cours d'écran, ECS, fermeture double et régression `Aga Detect`.
- **M4 ensuite** : double buffering, VBL, image-bank transfer, Bobs.

**Aucun jalon M3b ne devient « validé » sans retour WinUAE interprété ET compilé.** Les autres installations et projets restent inchangés.

## Références AmigaOS / AGA

- [ModeIDs officiels graphics/modeid.i](https://d0.se/include/graphics/modeid.i)
- [AmigaOS Display Database et ModeNotAvailable](https://wiki.amigaos.net/wiki/Display_Database)
- [AmigaOS Intuition Screens : SA_DisplayID et SA_Depth](https://wiki.amigaos.net/wiki/Intuition_Screens)
- [Guide matériel AGA historique](https://github.com/rkrajnc/minimig-mist/blob/master/doc/amiga/aga/AGA.guide)
- [HAM/EHB](https://arisamiga.github.io/amiga-bootcamp/08_graphics/ham_ehb_modes/)


## Retour d'essai et correction R1

Le développeur a exécuté `tests/M3B_320.asc` avec la première v0.0.4 : détection AGA vraie mais ouverture refusée. Le décodage des arguments était inversé : AMOS Pro v2+/365 passe `modeID` dans `D3`, puis `colors`, `height`, `width` dans `(A3)+`. La révision R1 corrige **quatre octets** dans la routine `Open` ; son binaire reste expérimental tant que l'interpréteur et le compilateur WinUAE ne l'ont pas validé. Ne pas confondre avec la M3a déjà validée.
