# M19 — Sprites matériels AGA S1 : contrat d'API proposé

**Date :** 22 novembre 2026  
**Décision auteur du 22/11/2026 : S1 crée les images par capture d'IFF indexé avec CMAP RGB24 sur l'écran AGA, sans `.abk` ni banque Work brute ; signatures publiques et code natif encore à approuver.**  
**Dépôt / branche :** `anthea176/AMOSPro-AGA-Extension`, `main` seulement.  
**CPU cible du futur code natif :** MC68020 / 68EC020 minimum.  
**Référence protégée :** P2d, `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 136 020 octets chacun, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. **Aucune modification binaire autorisée par cette proposition.**

## 1. Origine et preuves réellement obtenues

Ce projet poursuit le [plan S0–S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md) après les sondes `S0a`, `S0b`, `S0c` et `S0d`. Les tests publics/expérimentaux ne sont **pas** des tokens `Aga Sprite`.

- **S0a (Runtime)** : `ViewPort.Modes=$5000`, drapeau `SPRITES=$4000` présent, [journal](evidence/M19_S0_VIEWPORT_RUNTIME_2026-11-21.TXT).
- **S0b (Runtime)** : `GetSprite(-1)` acquiert le canal 1, `FreeSprite` le restitue deux fois, [journal](evidence/M19_S0B_SPR_RUNTIME_2026-11-22.TXT).
- **S0c (Runtime)** : Sprite 16x16 réellement vu en mouvement par l'auteur, 100 mouvements, banque Chip libérée selon les compteurs, [journal](evidence/M19_S0C_VIS_RUNTIME_2026-11-22.TXT).
- **S0d (Runtime ET véritable AMOS Compiler)** : [source exacte](../tests/design/sprites_aga/SPRITE_PROBE.asc), Git blob `eb4e9d0275edbe3266724705910fa66747c743ea`, `SOURCE_TAG M19_S0D_ROB_V1`. [Runtime](evidence/M19_S0D_ROB_RUNTIME_2026-11-22.TXT) et [Compiler](evidence/M19_S0D_ROB_COMPILED_2026-11-22.TXT) ont `RESULT 1`, `ERR 0`, `CYCLES_OK 3`, `OPENS 3`, `CLOSES 3`, `GETS/FREES 3`, `MOVES 108`, `COPPER_ON/OFF 1`, `BANK_FREES 3`, `BANK_HELD_ANY 0`. Le vrai journal compilé porte `PRG_STATE -1` et `RUN_MODE COMPILED`. L'auteur confirme le Sprite et le raster **visibles dans les deux modes**, sans artefact signalé.

**Portée exacte : S0d Gate B et Gate C PASS pour ce scénario.** Ces preuves ne qualifient ni un moteur natif intégré, ni plusieurs canaux simultanés, ni l'absence de fuite Chip mesurée indépendamment, ni la sécurité DMA formelle, ni la Gate D sur Amiga physique. La version précise du Compiler et l'empreinte de la Lib effectivement installée dans WinUAE ne sont pas consignées dans ces journaux.

## 2. Décision : images Sprite par capture d'IFF indexé RGB24

Le Sprite est capturé depuis un **écran AGA privé où une planche IFF/ILBM indexée a été chargée** avec `Aga Iff Load(File$)`. Exemple d'entrée S1 : ILBM 320x256, **8 bitplanes / 256 indices** et palette `CMAP` RGB sur 8 bits par composante (**24 bits de précision des couleurs**). **Aucune banque Sprite `.abk` et aucune banque Work brute de 64 octets ne sont imposées à l'utilisateur**.

Attention : **IFF indexé avec CMAP RGB24 != IFF truecolor à 24 plans**. Le second est hors du MVP S1. Le CMAP contient des triplets RGB8, selon la [spécification AmigaOS ILBM](https://wiki.amigaos.net/wiki/ILBM_IFF_Interleaved_Bitmap). HAM/EHB et conversion automatique truecolor vers Sprite restent hors périmètre.

Chaîne de production retenue :

1. Dessiner les images dans un IFF ILBM indexé et charger via `Aga Iff Load` sur l'écran AGA privé.
2. Capturer une zone rectangulaire du buffer **où l'IFF est effectivement chargé** ; définir explicitement l'indice transparent (même si ce n'est pas 0).
3. Lire les indices pixel et les valeurs RGB24 de leur palette. **S1 = au plus 3 indices opaques distincts + transparent** ; si davantage, **refus sans quantification silencieuse**.
4. Remapper les pixels de la capture vers le format matériel 2 bitplanes (0 transparent, 1..3 couleurs), puis copier et conserver l'image DMA dans la **Chip RAM possédée par l'extension**.
5. Acquérir un canal libre uniquement par `graphics.library/GetSprite(-1)`, présenter, déplacer et détacher le Sprite en respectant le cycle de vie OS/Copper.

Le logiciel dispose déjà de `Aga Iff Load`, `Aga Palette Get/Set` et `Aga Bank Image Capture(...,Version=2)` ; cette dernière fournit un précédent de **capture de région avec palette RGB24 dans AGAPIC v2**. S1 peut réutiliser le code natif de capture, **sans forcer une banque AGAPIC utilisateur**. La représentation DMA Sprite reste distincte du format AGAPIC et des Bobs.

**Palette RGB24 != 24 bits par pixel Sprite :** un canal matériel 16 pixels conserve **3 couleurs visibles + transparent**. Les deux canaux attachés de S2 permettront **15 visibles + transparent**. L'AGA dispose de 256 entrées RGB24, mais elles sont partagées avec les bitplanes et contrôlées pour les Sprites par les sélections de tranches et `BPLCON4`. **Ne jamais remplacer des couleurs du fond IFF ou du curseur à l'aveugle** : stratégie palette à qualifier puis refus si conflit non résolu.

### Signatures candidates : fonctions non disponibles

| Fonction future proposée | Effet attendu | Retour |
| --- | --- | --- |
| `Aga Sprite Capture(Id,SX,SY,W,H,TransparentPen)` | Capture depuis l'écran AGA, S1 W=16, H bornée, vérification des indices et RGB24 ; conservation interne indépendante de l'IFF | 1 succès, 0 refus |
| `Aga Sprite On(Id,X,Y)` | Affiche une image capturée ; attribue un canal OS libre | 1 succès, 0 refus |
| `Aga Sprite Move(X,Y)` | Déplace l'unique Sprite actif, sans Swap AGA implicite | 1 succès, 0 refus |
| `Aga Sprite Off` | Détache les références DMA puis libère seulement les ressources devenues sûres | 1 fin, 0 refus/pending |

Ces signatures **ne sont pas implémentées** et nécessitent approbation distincte. `Capture` à 6 paramètres doit être vérifié avec l'ABI AP20/`GetP`/Compiler avant code. L'extension n'expose pas directement le numéro de canal pour piloter la palette.

### Échelonnement

- **S1** : un Sprite matériel 16 pixels, 2 bitplanes, 3 couleurs RGB24 opaques + transparence, image capturée depuis IFF indexé.
- **S2** : Sprite 32 et 64 pixels AGA (largeur `FMODE` du contexte, pas libre par canal), deux canaux attachés 15 couleurs + transparence, palette/animation multi-images, après qualification OS.
- **S3** : multiplexage, animations multi-objets, collisions et éventuellement AMAL ; hors S1.

**Points à vérifier avant développement :** source du buffer en double buffering, prise en charge exacte des indices/palette RGB24, sélection des pens Sprite sans altérer le décor, protocole OS de détachement du DMA, paramètres AMOS/Compiler.
## 3. Propriété, refus, fermeture : invariants bloquants

1. **Acquisition :** `GetSprite(-1)` seulement, numéro 0..7 fourni par l'OS ; si `-1`, pas de Sprite et retour contrôlé. Ne jamais forcer le canal 0 ni désactiver le pointeur Intuition globalement.
2. **Transaction :** la validation de la zone capturée, du nombre de couleurs, de la palette, des coordonnées, du Screen et du ViewPort précèdent les effets. Échec d'allocation ou de token : pas de canal orphelin et pas de mémoire utilisateur détruite. `On` quand un Sprite S1 existe déjà **refuse sans modifier l'objet existant**.
3. **Mémoire :** copie dans un tampon propriétaire Chip, durée de vie prolongée pendant **toute** référence du DMA ; source utilisateur non accrochée au Sprite. Aucune allocation/libération depuis un callback ou une interruption.
4. **Retrait :** `ChangeSprite` vers l'image vide, puis **démontrer une méthode OS sûre** de déconnexion du display/Copper avant libération Chip ; `FreeSprite` seul n'est **pas** une preuve DMA. Les 2 VBL + 3 WaitTOF de S0d sont des observations de test, **pas un contrat matériel suffisant**. Si l'arrêt n'est pas garanti, **ne pas libérer** la mémoire encore potentiellement lue. Prévoir une résolution bornée d'un état pending, sans attente infinie.
5. **Écran :** `Aga Screen Close` doit faire le cleanup du Sprite **avant** destruction des `Screen*/ViewPort*`, préserver le cleanup Bob/Copper et ne pas avoir de chemin de double-free. Définir explicitement le comportement lorsque l'arrêt du DMA est encore pending avant d'intégrer la première API ; ne pas contourner cet échec.
6. **Palette/Copper :** aucun emprunt des deux bits d'état de `Screen.UserData` utilisés par le Copper ; ni écriture du Copper d'autrui, ni modification de ses listes sans API existante. `Aga Swap` explicite uniquement pour les bitplanes.
7. **Isolations :** pas de régression des fonctions Bobs, souris, écran, Copper, banques. Aucun appel sur un écran fermé ne doit déréférencer son ancien `ViewPort*`.

**VERROU OUVERT AVANT CODE NATIF :** analyser et justifier le vrai mécanisme de déconnexion DMA/Copper en s'appuyant sur les sources Intuition/graphics.library et sur les chemins P2d de fermeture, puis définir le cleanup d'échec. La visibilité de S0d ne lève pas ce verrou.

## 4. Critères d'acceptation et Gates futures

| Gate / étape | Conditions prévues (non acquises pour S1) |
| --- | --- |
| **Contrat** | Approbation auteur des signatures, de la sémantique de `canal+1`, du capture IFF RGB24, de l'indice transparent, de la palette et de la politique de fermeture |
| **Source / Gate A** | Builder/émetteurs natifs basés sur sources P2d, marqueur `AGA_NATIVE_MIN_CPU: MC68020`, ABI/AP20, `GetP`, D3/D2, registres et relocation vérifiés ; tests propriété OS/Chip, refus de canaux, erreurs, compile source / CI, régressions Bob/Copper |
| **Gate B Runtime WinUAE** | Un seul ASC expérimental réutilisé sous `tests/design/sprites_aga/`, 1 Sprite 16x16 visible, coordonnées/animation, IFF 8 plans indexé avec CMAP RGB24 et région à 3 couleurs opaques maximum, canal indisponible, arrêt, Close/reopen, souris, Copper et Bob en arrière-plan ; rendu et logs |
| **Gate C vrai AMOS Compiler** | Même source et même Lib candidate *exactes*, binaire produit et lancé par le Compiler AMOS, log `PRG_STATE -1`, parité fonctionnelle/visuelle, aucun freeze à Open/Close |
| **Gate D** | Amiga AGA physique lorsque disponible ; ne jamais revendiquer cette Gate depuis WinUAE |

En plus des compteurs `GET/FREE`, mesurer la **Chip RAM libre avant/après** sans ouvrir le journal RAM avant la mesure ; vérifier les références réellement désarmées, les relances répétées, le chemin `Off` idempotent et l'absence de corruption avec Copper et curseur. Les exécutions S0d sont des **preuves préparatoires**, non des Gates S1 transférables.

## 5. Ce qui reste à trancher avant toute implémentation

1. **Valider ou modifier le MVP : un seul Sprite 16x16 actif**, puis plusieurs Sprites en phase ultérieure.
2. **Valider ou modifier les trois noms/signatures** `On(bank,x,y)`, `Move(x,y)`, `Off`, et le retour de `On` : `canal+1` contre `1` booléen + autre accès au canal.
3. **Valider ou modifier le format de source Work 64 octets** et l'exposition de la palette : affectation RGB24 aux pens réellement accessibles sans toucher au fond IFF.
4. **Clore techniquement la sûreté de retrait DMA** et la transaction de `Aga Screen Close`. Si ce point demeure indémontrable, **S1 reste bloqué**.

**Aucun builder, source AMOS, extension AP20, binaire ni `LAST_GOOD` modifié par cette étude.** Aucune promotion automatique après un éventuel test. Les archives S0 restent des preuves historiques.
