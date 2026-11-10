# Audit Alice68 / AGA-PiStorm pour AMOSPro-AGA-Extension

Date de l'audit : 2026-11-08

Source principale étudiée : `farsonic/Alice68`, branche `main`, commit observé `c09bc449df386158a52e7544fa5f539e6d46e7c9` du 7 novembre 2026.

## Objet

Alice68 est une machine AGA autonome sur Raspberry Pi 4 construite autour de :

- Emu68 pour l'exécution 68k ;
- AGA-PiStorm pour le chipset virtuel Alice/Lisa/Paula, Copper et Blitter ;
- EMU68AGA Bare Metal pour la couche machine ;
- des ajouts Alice68 pour l'USB, le réseau, les HDF et les volumes SD.

Pour AMOSPro-AGA-Extension, l'intérêt principal n'est pas d'intégrer Alice68, mais d'utiliser son coeur AGA comme **référence technique et comportementale** afin de fiabiliser nos propres commandes AMOS AGA.

L'extension doit continuer à viser le vrai chipset AGA et WinUAE, avec AMOS Professional 365 comme environnement principal.

## Zones du dépôt réellement utiles

Les fichiers prioritaires sont :

- `core/src/playfield.c`
- `core/src/copper.c`
- `core/src/blitter.c`
- `core/src/sprites.c`
- `core/src/custom.c`

Le répertoire `arm/` est surtout utile pour comprendre l'intégration Emu68/HDMI et les contraintes de synchronisation, mais ses couches HVS, HDMI, V3D, RGB-out, USB et réseau ne sont pas des cibles à reprendre dans l'extension AMOS.

## Matrice d'intérêt

| Fonction | Alice68 / AGA-PiStorm | Intérêt pour AMOSPro-AGA |
| --- | --- | --- |
| Bitplanes 1 à 8 | Oui | Très élevé |
| Palette AGA 256 couleurs / RGB24 | Oui | Très élevé |
| BPLCON0/1/2/3/4 | Oui | Très élevé |
| FMODE / largeur de fetch | Oui | Très élevé |
| DDF / DIW / DIWHIGH | Oui | Très élevé |
| Scrolling BPLCON1 | Oui | Très élevé |
| Copper MOVE / WAIT / SKIP | Oui | Très élevé |
| Sprites 16 / 32 / 64 px | Oui | Très élevé |
| Sprites attachés | Oui | Élevé |
| Dual Playfield | Oui | Élevé |
| EHB | Oui | Élevé |
| HAM6 / HAM8 | Oui | Élevé |
| Blitter logique / registres | Oui | Très élevé |
| Timing exact du Blitter | Non : mode volontairement simplifié | À ne pas utiliser comme référence de performance |
| HDMI / HVS / V3D | Oui | Hors périmètre |
| USB / WiFi / Ethernet / HDF | Oui | Hors périmètre |

## 1. Playfield AGA

`core/src/playfield.c` est la source la plus utile pour notre projet.

Le code gère notamment :

- 1 à 8 bitplanes ;
- LowRes, HiRes et SuperHiRes ;
- `FMODE` ;
- `BPLCON0` à `BPLCON4` ;
- `DIWSTRT`, `DIWSTOP`, `DIWHIGH` ;
- `DDFSTRT`, `DDFSTOP` ;
- scroll `BPLCON1` ;
- palette AGA ;
- HAM6 / HAM8 ;
- EHB ;
- Dual Playfield ;
- priorité entre playfields et sprites ;
- collisions ;
- conversion planar vers rendu.

### Conséquence pour notre API AMOS

Les futures commandes de haut niveau doivent masquer cette plomberie matérielle.

Exemple de cible :

```amos
_OK=Aga Screen Open(320,256,256,$00021000)
```

L'utilisateur AMOS ne doit pas être obligé de régler manuellement `FMODE`, `BPLCONx`, DDF, DIW, modulos et pointeurs de bitplanes pour obtenir un écran AGA normal.

## 2. Palette AGA 256 couleurs / RGB24

Alice68 maintient 256 entrées de palette et modélise le fonctionnement AGA de `BPLCON3` avec :

- sélection de banque de 32 couleurs ;
- bit `LOCT` ;
- écriture séparée des nibbles hauts et bas RGB.

Une couleur AGA 24 bits est donc construite par deux écritures de 12 bits :

1. `LOCT=0` : nibbles hauts RGB ;
2. `LOCT=1` : nibbles bas RGB.

### Conséquence

Notre future commande :

```amos
Aga Set Colour index,r,g,b
```

doit cacher complètement la gestion banque + LOCT et accepter des composants 0..255.

La M3b peut continuer à utiliser `graphics.library` pour la gestion normale des écrans Intuition. Le comportement matériel observé ici reste une référence pour contrôler les résultats et préparer les fonctions plus proches du hardware.

## 3. FMODE et bande passante

Alice68 utilise des tables de fetch qui changent selon :

- la résolution ;
- la valeur de `FMODE` ;
- le nombre de plans ;
- la largeur de fetch.

Ce point confirme qu'un écran AGA à 8 bitplanes ne se résume pas à régler `BPLCON0`.

### Décision de conception

- garder une API AMOS de haut niveau ;
- ne pas exposer `FMODE` comme paramètre obligatoire pour les usages courants ;
- réserver les réglages directs éventuels à une future couche "expert" ;
- valider les combinaisons résolution/profondeur contre les vraies capacités du mode AmigaOS et du chipset.

## 4. Copper

`core/src/copper.c` implémente :

- MOVE ;
- WAIT ;
- SKIP ;
- COP1LC / COP2LC ;
- COPJMP1 / COPJMP2 ;
- attente du Blitter ;
- concurrence avec les slots DMA bitplanes ;
- redémarrage vertical ;
- comparaisons beam et masques.

Le code est documenté avec de nombreuses validations par traces DMA WinUAE.

### API future possible

```text
Aga Copper Clear
Aga Copper Move
Aga Copper Wait
Aga Copper End
Aga Copper On
Aga Copper Off
```

Une telle couche permettrait des effets raster, split-screen, changements de palette, scrolling et modifications de bitplanes sans charger inutilement le 68k.

Ce bloc est particulièrement intéressant après stabilisation des écrans persistants M3b.

## 5. Sprites AGA

`core/src/sprites.c` confirme et modélise :

- 8 sprites matériels ;
- largeur 16 / 32 / 64 pixels selon `FMODE` ;
- résolution LowRes / HiRes / SuperHiRes ;
- sprites attachés ;
- bases de couleurs AGA via `BPLCON4` ;
- priorités avec les playfields ;
- changements de position et de données en cours de ligne.

### API future possible

```text
Aga Sprite Width
Aga Sprite
Aga Sprite Off
Aga Sprite Attach
```

Pour des jeux AMOS, cela peut fournir une voie matérielle très légère en CPU par rapport à des Bobs pour certains objets répétitifs ou éléments de HUD.

## 6. Dual Playfield

Alice68 sépare correctement les plans des deux playfields et gère :

- `PF2PRI` ;
- `PF2OF` ;
- priorités ;
- palettes ;
- interaction avec les sprites.

Une future fonction Dual Playfield est donc réaliste, mais elle vient après la stabilisation des écrans, palette, buffering et fonctions de base.

## 7. HAM6 / HAM8 / EHB

Le code prend explicitement en charge :

- HAM6 sur 6 plans ;
- HAM8 sur 8 plans ;
- EHB sur 6 plans ;
- règles spécifiques de rendu.

Ces modes ne doivent pas être traités comme de simples variantes "nombre de couleurs".

Cette règle est déjà cohérente avec `docs/M3B_PLAN.md` : la sélection doit passer par le ModeID / mode spécial, avec routines de palette et d'écriture adaptées.

## 8. Blitter

`core/src/blitter.c` est une bonne référence pour comprendre :

- `BLTCON0`, `BLTCON1` ;
- canaux A/B/C/D ;
- minterms ;
- shifts ;
- masks ;
- modulos ;
- fill ;
- descending ;
- line mode ;
- `BLTSIZE`, `BLTSIZH`, `BLTSIZV`.

### Limite majeure

Alice68 exécute les données du blit pratiquement immédiatement puis retarde volontairement la signalisation de fin.

Le code précise que cette temporisation n'est **pas** une simulation fidèle du temps réel d'un Blitter physique.

### Règle pour notre projet

Alice68 peut servir de référence pour :

- la logique ;
- les registres ;
- les opérations ;
- les cas limites.

Alice68 **ne doit pas servir à mesurer ou promettre les performances du Blitter sur A1200**.

Les performances réelles devront être validées sur :

1. WinUAE configuré de façon pertinente/cycle-exact lorsque nécessaire ;
2. vrai matériel AGA lorsque disponible.

## 9. Méthode de validation à reprendre

AGA-PiStorm utilise une méthode très intéressante :

- capture WinUAE ;
- registres ;
- palette ;
- Chip RAM ;
- traces DMA ;
- capture d'écran ;
- comparaison avec le coeur AGA.

Le point important est que les bugs de timing ne sont pas recherchés uniquement par comparaison visuelle : les slots DMA sont également comparés.

### Adaptation proposée pour AMOSPro-AGA

Pour les futures fonctions matérielles sensibles :

1. programme de test AMOS minimal ;
2. exécution WinUAE interprétée ;
3. exécution WinUAE compilée ;
4. capture des résultats visibles et registres pertinents ;
5. validation sur vrai AGA quand nécessaire ;
6. Alice68 utilisé comme référence supplémentaire de comportement, jamais comme preuve unique.

## 10. Ce qui reste hors périmètre

Ne pas importer dans AMOSPro-AGA :

- `arm/aga_hdmi.c` ;
- `arm/aga_hvs.c` ;
- `arm/aga_v3d.c` ;
- `arm/aga_rgbout.c` ;
- USB ;
- réseau ;
- WiFi ;
- Ethernet ;
- HDF ;
- cartes Zorro virtuelles.

Ces éléments servent Alice68 comme machine Raspberry Pi autonome, pas l'objectif de notre extension AMOS.

## 11. Licence et provenance

Le coeur AGA-PiStorm étudié est sous GPL-2.0-only et contient des éléments dérivés/traduits de UAE/WinUAE.

Le dépôt AMOSPro-AGA-Extension est actuellement sous licence MIT.

### Règle impérative

Ne pas copier directement du code GPL-2.0-only d'Alice68/AGA-PiStorm dans le code MIT de notre extension.

Utiliser Alice68 comme :

- référence de comportement ;
- référence de registres ;
- source d'idées de tests ;
- guide pour identifier les points délicats.

L'implémentation AMOSPro-AGA doit rester propre et basée sur la documentation matérielle, les interfaces AmigaOS et nos propres routines, avec validation croisée WinUAE / vrai AGA / références externes.

## 12. Impact sur la roadmap

Ordre technique recommandé après stabilisation de M3b :

| Priorité | Fonction |
| --- | --- |
| 1 | Écrans AGA persistants 1-8 bitplanes |
| 1 | Palette 256 couleurs RGB24 |
| 1 | validation correcte des modes / FMODE implicite via AmigaOS |
| 1 | cycle Open / Draw / Close robuste |
| 2 | Double buffering / VBL |
| 2 | fonctions Blitter Copy / Fill |
| 2 | couche Copper |
| 2 | sprites AGA 16 / 32 / 64 px |
| 3 | scrolling matériel |
| 3 | Dual Playfield |
| 4 | sprites attachés |
| 4 | EHB / HAM8 / SuperHiRes avancé |

Le principe reste : **AMOS AGA, pas un nouveau moteur de jeu**.

Une commande AMOS simple peut cacher une mécanique AGA complexe ; l'utilisateur doit bénéficier du chipset sans devoir programmer chaque registre à la main.

## 13. Usage d'Alice68 comme cible de test

Alice68 peut aussi devenir une cible pratique de compatibilité :

```text
AMOS Professional 365
        |
AMOSPro-AGA-Extension
        |
programme AMOS compilé/interprété
        |
   +----+-------------------+
   |                        |
WinUAE / vrai AGA        Alice68
                            |
                       AGA virtuel
```

Cela permettrait de tester une même API AMOS sur plusieurs implémentations du chipset.

Alice68 reste toutefois expérimental et ne remplace jamais la validation sur vrai Amiga AGA pour les sujets de timing et de performances.

## Conclusion

Alice68/AGA-PiStorm est une référence très utile pour AMOSPro-AGA-Extension, surtout pour :

- palette 24 bits ;
- FMODE ;
- bitplanes ;
- Copper ;
- sprites AGA ;
- Dual Playfield ;
- HAM/EHB ;
- logique Blitter ;
- stratégie de validation avec WinUAE et traces DMA.

La priorité immédiate du dépôt ne change pas : **terminer et valider M3b R1 sous WinUAE interprété et compilé avant d'élargir le périmètre**.

Ensuite, les enseignements de cet audit doivent guider la conception des couches Blitter, Copper et sprites sans casser l'API simple ni les jalons déjà validés.
