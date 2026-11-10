# Spécification de planification — souris, zones cliquables, collisions

**État au 10/11/2026 : M10 R25 validée sur scénario WinUAE.** La souris R23 (dispatcher IDCMP et FIFO), les hotspots R24 et la collision AABB R25 ont passé leurs tests AMOS/WinUAE documentés. R25 : `STATIC 1 PURE 1`, `SEEN FREE 1 HIT 1`, `FRAMES 409 DRAWERR 0`, `RESULT 1` et fermeture correcte ; [test archivé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc). Focus réel, stress et AMOS Compiler restent ouverts ; les anciens paragraphes R19-R22 ci-dessous sont historiques.

**R22 0.8.6, Gate A + B PASS sur son scénario :** `Aga Mouse Pressed/Released` fournissent des masques d'impulsions observées avec `PeekQualifier`. Premier appel = baseline, perte de focus = `-1` et remise à zéro, nouvelle ouverture = remise à zéro ; les deux masques de fronts sont indépendants. **Les appuis/relâchements totalement entre deux lectures restent indétectables.** Les files `IDCMP_MOUSEBUTTONS` et `RAWKEY` demandent une architecture de dispatcher commun dans un futur incrément. [Contrat R22](M8_MOUSE_EDGES_R22.md).

**R23 0.8.7 — Gate A + B PASS sur les scénarios testés :** dispatcher commun `IDCMP_MOUSEBUTTONS/RAWKEY`, FIFO de 16 touches, capture des clics complets entre deux lectures, `ReplyMsg` unique et traitement borné à 64 messages. WinUAE : `PRESSED=RELEASED=3`, `KEYS=64/64/-1`, `RESULT=1` ; Ctrl+C interrompt à `_WAITK=Aga Wait Key` avec fermeture correcte de l'écran Intuition. Tests de focus réel/stress et double-clic (plusieurs clics fusionnés en un bit) à poursuivre. [Rapport R23](M8_IDCMP_R23.md).

## Périmètre et séparation des responsabilités

- **Entrées souris** : événements matériels/Intuition, coordonnées converties dans le repère de l'écran AGA, boutons et transitions.
- **Zones cliquables** : logique d'interface pour transformer un clic dans une zone en un identifiant d'action.
- **Collisions** : logique géométrique entre éléments de jeu ; distincte du clic souris et indépendante des registres Copper.
- **Gameplay** : réaction à une action, cheminement, combat, mouvement autorisé, gravité ou résolution de pénétration. Ces décisions restent **dans le programme AMOS du jeu**.

## M8 — souris / actions

| Fonction requise | Contrat souhaité | Cas à tester |
|---|---|---|
| Position | `mouseX` et `mouseY` en pixels **logiques de l'écran AGA** ; origine en haut à gauche | Décalage fenêtre, 320/640/1280, écran fermé |
| Boutons | État gauche/droit et central s'il est disponible ; préciser masque et signification des bits | Appuis simultanés, pression maintenue, focus |
| Transitions | `pressed` (0→1), `released` (1→0), maintien ; clic simple, clic droit, éventuellement double-clic avec temporisation définie | Aucun double déclenchement en boucle ; seuil double-clic vérifiable |
| Mouvement | Lecture non bloquante, survol (hover), déplacement, drag avec capture si retenu | Absence d'événements, déplacement hors fenêtre, relâchement hors zone |
| Molette | Événements molette verticale/horizontale si exposés par la couche Intuition cible ; disponibilité à vérifier | Pas de défilement fantôme ; aucun événement si non pris en charge |
| Focus / sécurité | Définir comportement hors écran, perte de focus, fermeture et Ctrl+C | Pas de boucle infinie, pas de ressources orphelines |

**API R19 validée :** `_X=Aga Mouse X` et `_Y=Aga Mouse Y`, fonctions entières sans paramètres, `-1` si invalide. **API boutons validée en R21 :** `Aga Mouse Buttons` (instantané global ; masque gauche/droit/central), les fronts étant calculés côté AMOS entre deux lectures. **R22 PASS WinUAE sur son scénario :** fonctions natives `Aga Mouse Pressed/Released`, sans dispatcher IDCMP. **Non implémentées :** capture d'événements asynchrones de clics rapides, drag, molette. L'intégration des prochains événements `IDCMP_MOUSEBUTTONS` devra préserver le clavier Intuition existant.

Points techniques : `IDCMP_MOUSEMOVE` / `IDCMP_MOUSEBUTTONS`, localisation relative à la `Window` Intuition de l'extension, transformation vers l'écran (sans confondre coordonnées fenêtre, coordonnées physiques du mode vidéo et coordonnées du monde). Préserver le clavier Intuition actuel : `Aga Key`, `Aga Wait Key`, comportement Break Ctrl+C.

## M9 — zones cliquables / hotspots

**R24 0.9.0 — Gate A CPU/CI PASS (402 cas), Gate B WinUAE PASS sur son scénario :** `Aga Hotspot Hit(px,py,x,y,w,h)` retourne 1/0, bords fin exclusive, origine négative autorisée, aucun registre de zones. Capture utilisateur : `STATIC=1`, `OVERLAP=20`, `PURE=1`, `LEFT ID=20`, `RIGHT OUT=1`, `RESULT=1`, retour AMOS normal ligne 183. [Test archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc). Compteurs 13/3 correspondant à des clics répétés volontairement (confirmation utilisateur) ; aucune répétition parasite constatée sur ce scénario, test d'unicité sur un clic isolé non réalisé ; focus et stress non testés.


Exemple de **contrat fonctionnel proposé** : une zone `(id,x,y,largeur,hauteur)` est active dans le repère logique de l'écran, avec l'intérieur défini par `x <= px < x+largeur` et `y <= py < y+hauteur`. Les coordonnées négatives, dimensions nulles et dépassements sont traités explicitement ; aucun masquage implicite.

Fonctions à concevoir :

1. Déclarer ou mettre à jour une zone, supprimer, activer et désactiver.
2. Tester un point `(px,py)` et renvoyer un ID ou une valeur « aucune zone ».
3. Associer un événement `pressed` à la zone présente **au moment du clic** ; gérer `released` et éventuellement `drag` séparément.
4. Définir l'ordre de priorité de zones superposées (ex. dernière zone déclarée ou priorité explicite).
5. Réinitialiser les zones liées à l'écran lors de sa fermeture. Éviter des pointeurs/IDs persistants vers un écran détruit.

**Premier test de validation :** interface de trois rectangles affichés, dont deux superposés ; tester survol (hover), clic gauche et droit, centre, bord, zone superposée, hors zone, perte de focus, relâchement en dehors de la zone et éventuellement drag. Une pression prolongée n'active l'action qu'une seule fois.

Pour un jeu, la gestion de zones peut aussi rester en AMOS au-dessus d'une simple fonction `pointInRect`. La nécessité d'un registre interne des zones dans l'extension devra être justifiée avant d'augmenter son état partagé.

## M10 — collisions 2D

**R25 0.9.1 — Gate A CPU/CI + Gate B WinUAE PASS sur le scénario testé :** `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)` renvoie 1 pour une aire de chevauchement positive, 0 pour séparation, simple contact ou taille invalide. Entiers signés 32 bits, origines négatives admises ; aucune gestion d'objets/physique. **704 cas CPU/CI PASS** ([CI R25](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42916575209)), et **WinUAE PASS** : rectangle bleu fixe, rectangle mobile vert/rouge, `FRAMES 409`, `DRAWERR 0`, `RESULT 1`, retour correct à AMOS. [Test R25 archivé](../tests/passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) · [contrat M10](M10_RECT_OVERLAP_R25.md). L'IFF fournit uniquement palette/mode vidéo ; il ne sert pas au calcul AABB. Les 50 FPS ne sont pas mesurés.


**Noyau minimal, réutilisable et déterministe :**

- Point / rectangle : même convention de bords **fin exclusive** que pour les hotspots.
- Rectangle / rectangle **AABB** : chevauchement positif uniquement. Le contact des bords seuls est documenté comme « pas de recouvrement » pour ce premier contrat.
- Position locale versus position monde : conversions laissées explicites, sans mélange avec les coordonnées de la fenêtre Intuition.
- Objets de jeu et tuiles : boite englobante, plusieurs hitboxes, couches ou groupes de collision si un besoin réel apparaît.
- Collisions pixel parfait / masque / Bob : **option ultérieure**, après étude des banques et des masques effectivement utilisés.
- Résolution de collision, vitesse et réponse physique : **hors extension bas niveau** par défaut, sauf besoin transversal démontré.

Cas limites de recette : une dimension nulle, coordonnées négatives, rectangles identiques, inclusion totale, contact bord à bord, chevauchement d'un pixel, valeurs limites d'entier, éléments masqués et off-screen.

**Décision R25 :** première étape M10 sous forme de fonction géométrique pure, sans état ni registre d'objets. Un moteur de collision avec objets reste une possibilité future à justifier.

## Gates et dépendances

Le **Copper n'est pas une dépendance fonctionnelle** de la souris ou des collisions. Les chantiers pourront être indépendants à partir de la couche écran + Intuition. Pour chaque API : contrat AMOS/ABI et non-régression des commandes existantes ; test interprété WinUAE ; AMOS Compiler ; matériel lorsque pertinent.

**État des validations :** R19-R23 souris et clavier, R24 hotspots, R25 AABB : Gate A CPU/CI et Gate B AMOS/WinUAE PASS **sur leurs scénarios archivés respectifs**. Les limites focus/stress, AMOS Compiler, matériel physique et mesure FPS restent ouvertes ; ne pas réattribuer les réserves historiques R20 à R25.
