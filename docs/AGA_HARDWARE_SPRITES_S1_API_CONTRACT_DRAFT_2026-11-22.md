# M19 — Sprites matériels AGA S1 : contrat d'API proposé

**Date :** 22 novembre 2026  
**Statut : PROPOSITION POUR VALIDATION PAR L'AUTEUR — aucune API nouvelle approuvée, codée, exportée ou testée.**  
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

## 2. Périmètre minimal S1 proposé (à décider)

Un **seul Sprite matériel 16x16 à la fois**, indépendant des Bobs. L'écran privé AGA existant est déjà ouvert : pour le premier jalon, retenir **320x256, 256 couleurs**, mode identique à S0d. Un canal matériel simple OS, **non attaché**, **2 bits/pixel** (couleur 0 transparente, 1–3 visibles). Aucun multiplexage, aucun mode AGA 32/64 px, pas d'AMAL, pas de banque Sprite ABK multi-images à ce stade.

L'extension doit posséder son état Sprite, sa structure `SimpleSprite`, ses données **en vraie Chip RAM** et le canal attribué par `graphics.library/GetSprite(-1)`. Le curseur Intuition, le Copper existant et les Bobs conservent leurs ressources et leur propriétaire. **Pas de manipulation directe de `SPRnPT`, `DMACON`, `COP1LC`, `FMODE`, `BPLCON3` ou `BPLCON4`.** Aucun `Aga Swap` implicite, aucune opération depuis une interruption.

### Signatures proposées (PAS des commandes disponibles)

| Fonction entière cible | Arguments / effet | Retour proposé |
| --- | --- | --- |
| `Aga Sprite On(bank,x,y)` | Charge une image 16x16 depuis une banque AMOS `Work`, copie dans une allocation Chip propriétaire, acquiert le **premier canal OS libre** et présente le Sprite aux coordonnées de l'écran privé | `0` = refus sans acquisition résiduelle ; `1..8` = **canal physique obtenu +1** (à approuver, car différent du booléen habituel des commandes AGA) |
| `Aga Sprite Move(x,y)` | Déplace le Sprite S1 actif, sans changer de banque, de Copper ni de page bitplane | `1` = accepté ; `0` = aucun Sprite ou coordonnées invalides |
| `Aga Sprite Off` | Retire l'image, détache de façon prouvée les références DMA, libère le canal OS et sa Chip RAM | `1` = entièrement arrêté/nettoyé (ou déjà inactif sur écran ouvert) ; `0` = détachement non confirmé, ressource conservée et erreur signalable |

Ces signatures, le choix du retour `canal+1` et les détails de format ci-dessous **doivent recevoir une approbation explicite avant toute création de token AP20 ou code natif**. Ne pas considérer cette table comme une commande AMOS syntaxiquement ou fonctionnellement vérifiée.

### Format image proposé pour S1, sans ABK Sprite

- `bank` : banque AMOS `Work` présente et **exactement 64 octets** de pixels de source, non compressés et indépendants de l'emplacement Chip/Fast du côté utilisateur ; lire et valider type/taille avant accès.
- **16 lignes × 4 octets** : par ligne, un WORD big-endian du plan 0 suivi d'un WORD big-endian du plan 1. Le bit 15 représente le pixel le plus à gauche. Indices visibles 1/2/3 ; 0 transparent.
- L'extension construit la représentation DMA **72 octets** (4 de contrôle, 64 de pixels, 4 de fin) et sa structure OS dans **sa propre** mémoire Chip. Elle ne conserve aucun pointeur vers la banque source ; celle-ci peut être libérée par l'utilisateur après un `On` réussi.
- Le numéro logique de banque est fourni par l'appelant, sans supposer `100` libre, ni écraser une banque Bob/AGAPIC. La numérotation, le type `Work`, la taille stricte et la lecture en mémoire doivent être validés dans les sources AMOS P2d avant code.
- Origine `x,y` : coin supérieur gauche logique de l'écran privé 320x256, **Sprite entièrement visible** pour le premier jalon : `0<=x<=304`, `0<=y<=240`. Aucune conversion implicite du hotspot. Tests de correspondance coordonnées à prévoir.
- Palette : pour un canal physique `c` attribué par l'OS, le banc S0 utilise les entrées `16+((c AND 6)*2)+1..3`. Le retour `canal+1` proposé permet au programme appelant de calculer ces indices et d'employer l'API existante `Aga Palette Set`. **La compatibilité précise avec `BPLCON4`, les autres canaux, le Copper et les palettes utilisateur reste à qualifier ; ne pas imposer silencieusement un changement global de palette.**

## 3. Propriété, refus, fermeture : invariants bloquants

1. **Acquisition :** `GetSprite(-1)` seulement, numéro 0..7 fourni par l'OS ; si `-1`, pas de Sprite et retour contrôlé. Ne jamais forcer le canal 0 ni désactiver le pointeur Intuition globalement.
2. **Transaction :** les validations de banque, taille, coordonnées, Screen et ViewPort précèdent les effets. Échec d'allocation ou de token : pas de canal orphelin et pas de mémoire utilisateur détruite. `On` quand un Sprite S1 existe déjà **refuse sans modifier l'objet existant**.
3. **Mémoire :** copie dans un tampon propriétaire Chip, durée de vie prolongée pendant **toute** référence du DMA ; source utilisateur non accrochée au Sprite. Aucune allocation/libération depuis un callback ou une interruption.
4. **Retrait :** `ChangeSprite` vers l'image vide, puis **démontrer une méthode OS sûre** de déconnexion du display/Copper avant libération Chip ; `FreeSprite` seul n'est **pas** une preuve DMA. Les 2 VBL + 3 WaitTOF de S0d sont des observations de test, **pas un contrat matériel suffisant**. Si l'arrêt n'est pas garanti, **ne pas libérer** la mémoire encore potentiellement lue. Prévoir une résolution bornée d'un état pending, sans attente infinie.
5. **Écran :** `Aga Screen Close` doit faire le cleanup du Sprite **avant** destruction des `Screen*/ViewPort*`, préserver le cleanup Bob/Copper et ne pas avoir de chemin de double-free. Définir explicitement le comportement lorsque l'arrêt du DMA est encore pending avant d'intégrer la première API ; ne pas contourner cet échec.
6. **Palette/Copper :** aucun emprunt des deux bits d'état de `Screen.UserData` utilisés par le Copper ; ni écriture du Copper d'autrui, ni modification de ses listes sans API existante. `Aga Swap` explicite uniquement pour les bitplanes.
7. **Isolations :** pas de régression des fonctions Bobs, souris, écran, Copper, banques. Aucun appel sur un écran fermé ne doit déréférencer son ancien `ViewPort*`.

**VERROU OUVERT AVANT CODE NATIF :** analyser et justifier le vrai mécanisme de déconnexion DMA/Copper en s'appuyant sur les sources Intuition/graphics.library et sur les chemins P2d de fermeture, puis définir le cleanup d'échec. La visibilité de S0d ne lève pas ce verrou.

## 4. Critères d'acceptation et Gates futures

| Gate / étape | Conditions prévues (non acquises pour S1) |
| --- | --- |
| **Contrat** | Approbation auteur des signatures, de la sémantique de `canal+1`, du format Work 64 octets, de la palette et de la politique de fermeture |
| **Source / Gate A** | Builder/émetteurs natifs basés sur sources P2d, marqueur `AGA_NATIVE_MIN_CPU: MC68020`, ABI/AP20, `GetP`, D3/D2, registres et relocation vérifiés ; tests propriété OS/Chip, refus de canaux, erreurs, compile source / CI, régressions Bob/Copper |
| **Gate B Runtime WinUAE** | Un seul ASC expérimental réutilisé sous `tests/design/sprites_aga/`, 1 Sprite 16x16 visible, coordonnées/animation, bank Fast/Work, canal indisponible, arrêt, Close/reopen, souris, Copper et Bob en arrière-plan ; rendu et logs |
| **Gate C vrai AMOS Compiler** | Même source et même Lib candidate *exactes*, binaire produit et lancé par le Compiler AMOS, log `PRG_STATE -1`, parité fonctionnelle/visuelle, aucun freeze à Open/Close |
| **Gate D** | Amiga AGA physique lorsque disponible ; ne jamais revendiquer cette Gate depuis WinUAE |

En plus des compteurs `GET/FREE`, mesurer la **Chip RAM libre avant/après** sans ouvrir le journal RAM avant la mesure ; vérifier les références réellement désarmées, les relances répétées, le chemin `Off` idempotent et l'absence de corruption avec Copper et curseur. Les exécutions S0d sont des **preuves préparatoires**, non des Gates S1 transférables.

## 5. Ce qui reste à trancher avant toute implémentation

1. **Valider ou modifier le MVP : un seul Sprite 16x16 actif**, puis plusieurs Sprites en phase ultérieure.
2. **Valider ou modifier les trois noms/signatures** `On(bank,x,y)`, `Move(x,y)`, `Off`, et le retour de `On` : `canal+1` contre `1` booléen + autre accès au canal.
3. **Valider ou modifier le format de source Work 64 octets** et l'exposition de la palette : indices via canal physique pour le MVP ou une commande palette dédiée.
4. **Clore techniquement la sûreté de retrait DMA** et la transaction de `Aga Screen Close`. Si ce point demeure indémontrable, **S1 reste bloqué**.

**Aucun builder, source AMOS, extension AP20, binaire ni `LAST_GOOD` modifié par cette étude.** Aucune promotion automatique après un éventuel test. Les archives S0 restent des preuves historiques.
