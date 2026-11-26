# Sprites matériels AGA — feuille de route S0 à S3

**26/11/2026 — S2a engagé, premier composant source seul.** [S2a — staging et contrat](M19_S2A_FRAME_STAGE_2026-11-26.md). P2m reste active ; pas de nouveau token, Lib, ASC ou promotion. CI composant à relever ; intégration/publication DMA et Gates B/C/D S2a non acquises.

> **Contrat auteur AGSP v1 (22/11/2026) :** banque AMOS DATA multi-images `AGSP` distincte de `AGBO` et des Sprite OCS, images capturées depuis IFF indexé à palette CMAP RGB24. 3 couleurs opaques par canal S1 (2bpp), 4..15 en S2 attaché (4bpp), >15 refus ; palette locale et hotspot par image. [Spécification testable](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) et [contrat API S1 actualisé](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md). Modèle hôte + tests seulement, pas de DMA/WinUAE S1 validé.


> **Décision S1 22/11/2026 :** capturer directement les Sprites depuis une **planche IFF/ILBM indexée à palette CMAP RGB24 chargée sur l'écran AGA**. Plus de banque Sprite `.abk` ni de Work 64 octets pour l'utilisateur. S1 16px/3 couleurs opaques ; S2 32/64px et 15 couleurs avec deux canaux attachés. [Contrat S1 révisé](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md). Pas encore de nouvelles commandes ni validation du détachement DMA.

> **Etat courant au 22/11/2026 :** S0a/b/c ont des preuves Runtime, **S0d est valide Gates B (Runtime) et C (vrai AMOS Compiler)**, animations F et raster confirmes visuellement en deux modes. [Journal Runtime](evidence/M19_S0D_ROB_RUNTIME_2026-11-22.TXT) et [journal Compiler](evidence/M19_S0D_ROB_COMPILED_2026-11-22.TXT). **Aucune validation de surete DMA materielle generale, pas de Gate D.** [Premier contrat de commandes S1 : PROPOSITION A APPROUVER](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md) ; noms, signature, format banque, palette et cleanup sont encore soumis a validation. Aucun token, code natif ou binaire S1 livre.


> **Etape S0d (22/11/2026)** : [premier Sprite 16x16 S0c Runtime et visuel PASS](evidence/M19_S0C_VIS_RUNTIME_2026-11-22.TXT), 100 mouvements, retour AMOS et banque Chip liberee selon log ; absence d'artefacts confirmee par auteur. [Banc unique S0d](../tests/design/sprites_aga/SPRITE_PROBE.asc) en cours de qualification pour 3 cycles Open/Close et interactions curseur/Copper. Aucune validation Compiler ou hardware et aucune preuve formelle de DMA-detach.


> **Actualisation S0 (21/11/2026)** : [audit d'intégration détaillé](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md), **12 tests hôtes PASS** pour le modèle de propriété des canaux ; ni code natif ni fonctionnement DMA démontré. P2d `LAST_GOOD` inchangée, S1 non commencée.


> **Priorité actuelle après clôture P2d Bob (21/11/2026) : REPRENDRE S0.** Moteur Bob P0–P2 clos et P2d promue `LAST_GOOD` après Gates B/C WinUAE sur le banc intégré. Les mentions historiques « R84 LAST_GOOD » ci-dessous reflètent le contexte de conception du 15/11, **pas** la bibliothèque actuelle. Audit S0 NDK/ABI/Intuition/Copper à terminer avant tout prototype S1 (Sprite 16 pixels), et sans modification de P2d promue.


**Décision auteur du 15 novembre 2026 : prévoir le chantier Sprites matériels AGA, séparément du moteur Bob AGA.**  
**Statut : contrat d'intention et plan d'étude seulement ; aucune nouvelle API `Aga Sprite` implémentée, aucun nouveau test matériel ou Compiler exécuté.**  
Dépôt : `anthea176/AMOSPro-AGA-Extension`, **branche `main` exclusivement**. Pas de modification de R84 `LAST_GOOD`, de la candidate R88, ni de promotion automatique.

## 1. Deux moteurs distincts et complémentaires

- **Bobs AGA (M19)** : objets **logiciels** affichés dans les bitplanes de l'écran AGA privé par le Blitter, jusqu'à 8 plans / 256 couleurs, dimensions variables, masques et banques ABK multi-images. Contrat approuvé : [M19 Bobs multi-images](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md), phases **P0/P1/P2**.
- **Sprites matériels AGA (ce document)** : objets **affichés par les canaux DMA Sprite du chipset**, superposés à l'écran, sans recopie ni restauration de décor par le Blitter. Contraintes spécifiques de largeur, palette, canaux, Copper, priorité et Chip RAM. Phases **S0/S1/S2/S3**.
- **À mutualiser après preuve** : éventuellement des métadonnées logiques (ID, X/Y, frame, visibilité, hotspot), outils de capture/indexation et cycle de vie des allocations. **Ne pas supposer des formats binaires Sprite et Bob interchangeables**, ni imposer une banque ABK commune sans essai documenté.
- **AMAL facultatif et ultérieur** : il peut fournir des coordonnées/frames à un objet, mais ne doit pas devenir le moteur de dessin ou accéder aux ressources DMA/bitplanes depuis une interruption. Voir [plan historique M19 / AMAL](M19_SPRITES_BOBS_AMAL_PLAN.md).

**Ordre recommandé :** préserver la priorité du **socle Bob M19 P0** déjà décidé ; préparer l'audit S0 en parallèle documentaire, puis coder les Sprites sur une candidate expérimentale distincte et contrôlée. Les jalons S0–S3 **ne sont pas une promesse de livraison** ni une autorisation de changement du binaire.

## 2. Capacités de référence : matériel AGA vs AMOS natif

| Point | Matériel AGA / AMOS | Conséquence pour l'extension |
| --- | --- | --- |
| Canaux matériels | **8 canaux Sprite** matériels (0..7) | Les objets logiciels AMOS « computed Sprites » ne créent **pas** de canaux matériels supplémentaires. |
| Couleurs d'un canal indépendant | **3 couleurs visibles + transparent** (2 bits/pixel) | Ne pas promettre 256 couleurs simultanées sur un Sprite. |
| Paire de canaux attachés | **15 couleurs visibles + transparent** (4 bits/pixel, deux canaux mobilisés) | Au plus quatre paires matérielles attachées simultanément, hors multiplexage. |
| Largeur AGA | **16, 32 ou 64 pixels**, selon le mode Sprite `FMODE` ; largeur du fetch réglée au niveau du display | **`FMODE` n'est pas une largeur libre indépendante par canal** ; vérifier effets DMA, alignement et compatibilité avec le mode vidéo de l'écran privé. |
| Palette AGA | Sélection de **tranches de 16 entrées** dans la palette AGA de 256 couleurs, via la configuration Sprite (`BPLCON4` notamment) | Les choix de tranches sont **partagés/contraints par la configuration matérielle** ; une palette 256 couleurs disponible ne signifie pas une couleur libre par pixel Sprite. Vérifier les interactions avec les bitplanes, le curseur et l'affichage. |
| Mémoire et affichage | Données DMA Sprite en **véritable Chip RAM**, accès synchronisé avec le balayage | Allocation, taille, alignement et durée de vie à valider avant tout affichage ; copie depuis Fast si nécessaire. |
| Positionnement | Sprites en **coordonnées matérielles** ; AMOS natif expose `X Hard`, `Y Hard`, `X Screen`, `Y Screen` | Définir une API AGA ergonomique en coordonnées logiques/écran et vérifier offsets d'affichage, overscan, haute résolution et hotspot. |
| Ressources système | Intuition/graphics.library/Copper peuvent réserver des canaux, notamment celui du pointeur | Ne jamais réécrire des pointeurs Sprite ou registres DMA que le système possède ; définir la stratégie de possession/cleanup avant programmation. |
| Multiplexage | Un canal peut servir à plusieurs Sprites sur **différentes plages verticales** sous contraintes de timing | Nombre d'objets supérieur à huit **possible sous conditions**, non garanti ; allocation temporelle et limites DMA à mesurer. |

**Attention au vocabulaire AMOS :** le [manuel, chapitre 7.01](https://amospromanual.dev/07-01-hardware-sprites.html) décrit jusqu'à **56 « computed Sprites »**, produits par regroupement/réutilisation de canaux OCS. Ce n'est **ni** une promesse de 56 canaux AGA **ni** une fonction disponible automatiquement sur l'écran AGA privé. Le chapitre décrit aussi les commandes `Sprite` (0..63, dont 8..63 « computed »), `Get Sprite`, `Del Sprite`, `Ins Sprite`, `Get Sprite Palette`, `Sprite Update` (On/Off), `Sprite Off`, `X Sprite`, `Y Sprite`, `I Sprite`, les conversions de coordonnées et `Hot Spot`. Ces **commandes AMOS natives ne sont pas équivalentes à des commandes AGA de l'extension**.

**Validation préalable des registres :** les documents publics consultés ne doivent pas suffire pour figer les **valeurs de bits de `FMODE`, `BPLCON3`, `BPLCON4`**. Au moment d'implémenter, confronter les tables aux includes NDK et au code chipset existant, puis réaliser un test WinUAE discriminant. Aucun `move.w` « magique » ajouté d'après une seule source externe.

## 3. Feuille de route technique

### S0 — Audit matériel et intégration Intuition (bloquant)

1. Examiner **le code exact de l'écran privé** (`Aga Screen Open`, gestion ViewPort/Copper, `Safe`/`Disp`, `Aga Swap`, `Aga Screen Close`), propriétaires des canaux Sprite, curseur souris et allocations système.
2. Vérifier possibilités et limites de `graphics.library` / API système pour **16/32/64 pixels AGA**. Choisir la stratégie d'allocation Sprite/Copper sans écraser une ressource Intuition ; aucun accès DMA « brut » non maîtrisé.
3. Relever la configuration réelle des registres de display/`FMODE`/palettes et les contraintes d'alignement, de taille Chip, de priorité Sprite/bitplanes et de timing DMA.
4. Définir le contrat de coordonnées : origine de l'écran privé, offsets hardware, profondeur/format des palettes, hotspot, haute résolution et modes d'affichage.
5. Vérifier la présence de **huit canaux physiques** tout en identifiant **ceux effectivement disponibles** dans les scénarios testés. Documenter le fonctionnement du pointeur (souvent canal 0) sans supposer sa disponibilité.
6. Produire un **schéma mémoire + protocole test S1** avant d'ajouter des tokens AP20. **Statut : modèle de propriété S0 testé sur hôte, matériel/ABI S0 non clôturés.**

### S1 — Premier Sprite matériel autonome (16 pixels)

- Prototype d'un Sprite **16 px de large**, 3 couleurs + transparent, sur l'écran AGA privé ; affichage, changement de position/frame et désactivation ; test avec Bob(s) AGA en arrière-plan.
- Étudier la création/capture d'images Sprite depuis l'écran AGA **sans convertisseur PC obligatoire** ; réserver une vraie allocation Chip et garantir sa durée de vie pendant le DMA. **Format, banque et syntaxe publique à définir après S0**.
- Séparer la mise à jour des Sprites d'`Aga Swap` : **pas de changement de page AGA implicite**. Vérifier le moment de changement de pointeurs Sprite/affichage par rapport au balayage et à `Disp` ; ni `Wait Vbl` ni `Safe` ne sont à eux seuls des garanties universelles.
- Vérifier coexistence avec le pointeur souris, le Copper/OS, la fermeture, les erreurs, l'absence d'artefacts/ Guru. **Aucune allocation/libération dans une interruption.**
- Tests : **Gate A** source/CPU, **Gate B** AMOS Runtime WinUAE, **Gate C** vrai AMOS Compiler pour le même scénario, séparées ; **Gate D** machine physique ultérieure. Aucun PASS ne peut être anticipé.

### S2 — Modes AGA avancés et ergonomie

- **Sprites attachés** (15 couleurs + transparent), coût de deux canaux et règles de paires ; index de palette et sélection des tranches `BPLCON4`.
- **Largeurs 32 / 64 pixels AGA** ; changements `FMODE` compatibles avec le display, formats DMA, alignement et consommation de bande passante. Tester un mode de largeur par contexte avant d'envisager des changements mid-frame.
- Fonctionnalités AMOS pertinentes à étudier : **banques Sprite**, `Get Sprite`, `Sprite Off`, `Sprite Update`, lecture X/Y/image, hotspot, palettes, animation de frame. Les **nouveaux noms d'API AGA ne sont pas décidés**.
- Contrôler transparence, affichage hors écran, coordonnées, hi-res, priorité relative aux bitplanes et écrans multiples éventuels.
- Benchmarks reproductibles : CPU 68020/14 MHz JIT OFF et configurations plus rapides, charge DMA et temps de frame ; *draw-only* séparé du coût de scène et d'animation.

### S3 — Multiplexage, animation et interactions

- Réutilisation **verticale** des canaux Sprite : ordonnancement des objets, conflits de plages, limite de largeur/quantité et charge Copper. Une solution « computed Sprites » AGA demande son propre contrat ; ne pas recopier la limite « 56 » du système AMOS OCS.
- Animation multi-objets et, éventuellement, **AMAL manuel**, uniquement dans le thread principal et après preuve de compatibilité.
- Collisions : rectangle puis masque si utile ; préciser la différence avec les collisions hardware et les commandes AMOS natives `Sprite Col`/`Col`. Ne pas promettre l'automatisme du gestionnaire OCS.
- Tests de robustesse : saturation canaux, conflits d'allocations, mélange Bobs/Sprites, Copper, souris, `Aga Screen Close` et re-open, retour AMOS, Compiler et matériel réel.

## 4. Gestion des ressources / erreurs — contrat transversal

- **Séparation Bob / Sprite** : les images Bob 1..8 bitplanes restent gérées par le Blitter ; la Sprite DMA exige une **représentation matérielle distincte**, compatible avec 2 ou 4 bits/pixel. Une capture 256 couleurs n'est pas affichable telle quelle comme Sprite : validation/re-mappage contrôlé des indices requis, sinon refus explicite.
- **Gestion des banques** : la numérotation des banques AMOS et l'éventuel format `ABK` multi-images Sprite **sont à définir** ; ne pas réserver arbitrairement banque n°1 ni réutiliser de force le numéro d'une banque Bob. La sauvegarde `Save`/`Load` native est une cible d'ergonomie, pas une compatibilité prouvée pour ce format encore inexistant.
- **Chip RAM** : pas de commande AMCAF obligatoire ni de copie manuelle par l'utilisateur ; la prise en charge automatique est **un objectif à qualifier en S0/S1**, sans supposer `Load`→Chip automatiquement.
- **Propriété hardware** : aucun canal Sprite, pointeur OS ou entrée Copper modifié sans possession vérifiée ; libération seulement quand le hardware ne l'utilise plus. Nettoyage complet sur erreur, fermeture et redémarrage d'écran.
- **Concurrence** : aucune opération d'allocation/libération ou de dessin dans les interruptions ; état d'objets mis à jour depuis la boucle principale. `Aga Swap` reste explicite pour les bitplanes ; les Sprites ne doivent pas déclencher un swap à l'insu du programmeur.
- **Statuts** : documenter séparément faits matériels vérifiés, hypothèses d'implémentation, code écrit, tests statiques, Runtime/Compiler WinUAE et Amiga réel. Aucun gain/performance/nombre d'objets simultanés inventé.

## 5. Décision de priorité et état du chantier

| Chantier | État | Prochain travail autorisé par cette note |
| --- | --- | --- |
| **M19 — Bobs AGA** | Contrat fonctionnel et feuille P0/P1/P2 approuvés ; nouveau moteur multi-images **non implémenté** dans ce contrat | P0a : vérification de la syntaxe AP20/Compiler, banque multi-images et capture sous AMOS |
| **Sprites AGA S0** | **À étudier ; aucune commande nouvelle validée** | Audit lecture seule écran/Intuition/Copper/sprites et protocole d'essai |
| **Sprites AGA S1/S2/S3** | **Non implémentés / non testés** | Développement par étapes après S0 et décision explicite sur API et ressources |

**Ne pas confondre** les anciens prototypes M19 `Aga Bob Batch`/AGPC ou les exemples AMAL avec la future API Bob multi-images ni le moteur Sprite matériel. Aucune compilation ou validation WinUAE ne découle de cette feuille de route.

## 6. Références

- [AMOS Professional, chapitre 7.01 — Hardware Sprites](https://amospromanual.dev/07-01-hardware-sprites.html) : matériel OCS, « computed Sprites », commande Sprite/Off/Update et banque images.
- [AMOS Professional, chapitre 7.02 — Blitter Objects](https://amospromanual.dev/07-02-blitter-objects.html) : distinction Bob et Sprite.
- [AmigaOS Documentation — Hardware Sprites](https://wiki.amigaos.net/wiki/Hardware_Sprites) : canaux, ownership système, Chip RAM.
- [AGA Sprite Enhancements — arisamiga](https://arisamiga.github.io/amiga-bootcamp/01_hardware/aga_a1200_a4000/aga_sprites/) : largeur AGA, FMODE, palette BPLCON4, DMA (à recouper pour les valeurs de registres).
- [Plan M19 historique Sprites/Bobs/AMAL](M19_SPRITES_BOBS_AMAL_PLAN.md) : prototypes et Gates antérieurs ; ne pas effacer les résultats validés.
- [M19 Bobs — contrat multi-images](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) : interface Bob approuvée, distincte du futur contrat Sprite.

**Documentation uniquement. Aucune API Sprite nouvelle, aucun binaire, test actif ou release modifiés.**
