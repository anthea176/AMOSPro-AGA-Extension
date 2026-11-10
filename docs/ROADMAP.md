# Roadmap — AMOS Professional 365 / Extension AGA

**Objectif :** construire des primitives AGA réutilisables dans les programmes AMOS 365, sans imposer de réécriture du moteur des jeux. La roadmap décrit **l'ordre du travail à venir**, pas les anciens essais R1 à R15.

**R24 M9 Hotspot Hit (10/11/2026) : Gate A CPU/CI PASS (402 cas), Gate B AMOS/WinUAE PASS** sur le scénario utilisateur : `STATIC=1`, `OVERLAP=20`, `LEFT ID=20`, `RIGHT OUT=1`, `RESULT=1` et fermeture AMOS correcte ligne 183. [Test corrigé exact archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc). Compteurs LEFT 13 / RIGHT 3 observés, sans conclusion sur le nombre de clics physiques. Focus et stress non vérifiés.

**R23 IDCMP 0.8.7 (10/11/2026) : Gate A CPU/CI PASS 15 cas (CI (archive CI privée, run #42899343161)), Gate B AMOS interprété/WinUAE PASS** sur clics rapides (`PRESSED=RELEASED=3`), FIFO clavier (`KEYS=64/64/-1`, `WAIT=16`, `RESULT=1`), et Ctrl+C : interruption à `_WAITK=Aga Wait Key` avec fermeture correcte de l'écran Intuition. [Test R23 archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc) sans modification. Prochains contrôles éventuels : focus réel, stress et saturation. [Contrat R23](M8_IDCMP_R23.md).

**R22 (10/11/2026) :** `Aga Mouse Pressed/Released` **Gate A CPU/CI PASS (25 cas)** et **Gate B WinUAE PASS** sur le scénario utilisateur (fronts gauche/droit uniques, clavier, fermeture/réouverture, fin normale). [Test R22 archivé](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Clics très brefs et focus réel restent à valider ; [dossier R22](M8_MOUSE_EDGES_R22.md). R21 et `LAST_GOOD` protégées.

**Checkpoint R21 validé (10/11/2026) :** Gate A **PASS 11 cas CPU 68000 et CI verte**, Gate B **PASS utilisateur AMOS interprété/WinUAE** : le clic droit ne provoque plus de barre Intuition. Le test R21 a été archivé sans changement dans [`tests/passed/`](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc). R20 conserve son défaut de menu dans les archives, R19 X/Y et R18 Copper restent acquis ; `LAST_GOOD` R10 inchangée. **M8 reste en cours** pour les transitions natives, clics très brefs et gestion du focus. [Statut](M8_STATUS.md) · [R21](M8_RMBTRAP_R21.md).

**État au 10 novembre 2026 : M8 souris en cours.** R19 0.8.3 `Aga Mouse X/Y` : **Gate A CPU PASS 76 cas, CI générale PASS et Gate B AMOS/WinUAE PASS** sur les positions `(0,0)` et `(319,255)`. Test archivé. Boutons, clics, transitions M8 puis M9 zones et M10 collisions à faire. M7 R16/R17/R18 PASS WinUAE ; LAST_GOOD R10 inchangée. Voir [M8_STATUS](M8_STATUS.md).

## 1. Vue d'ensemble — ordre des chantiers

| Jalon | Fonctionnalités | Situation | Prochaine décision / résultat attendu |
|---|---|---|---|
| M0–M4 | ABI AP20/AMOS, détection AGA, écran Intuition, présentation double buffer et VBL | Socle existant ; validations historiques selon leurs tests | Ne pas retoucher sans régression démontrée |
| M5 | Inspection et chargement IFF/ILBM, palettes et modes vidéo (dont HAM6/HAM8 et SuperHiRes) | **Clôturé par l'utilisateur** pour le périmètre testé sous WinUAE | Conserver les réserves Compiler, matériel, DblPAL/NTSC |
| M6 | `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` | **PASS AMOS interprété/WinUAE** sur tests archivés ; Compiler / Amiga réel non testés | Base R15 protégée |
| **M7 — VALIDÉ (RGB4 WinUAE)** | **Copper `Clear/Wait/Move/End/On/Off`** | **R16/R17/R18 PASS sous AMOS interprété/WinUAE**, raster visible | Réserves Compiler/Amiga réel, stress/fuites et couleurs AGA avancées |
| **M8 — VALIDÉ sur périmètre R23** | **Souris : positions, boutons, clics, dispatcher IDCMP** | R19–R23 CPU/WinUAE PASS sur scénarios archivés, Ctrl+C et retour Intuition inclus | Conserver R23 comme archive ; focus réel, stress, matériel/Compiler non testés |
| **M9 — R24 VALIDÉ (scénario WinUAE)** | **Hotspots : première primitive `Aga Hotspot Hit`** | Gate A CPU/CI PASS 402 cas ; Gate B WinUAE PASS sur bords, recouvrement ID 20, clic hors zone, fermeture/réouverture ; [test exact archivé](../tests/passed/M9_R24_HOTSPOT_HIT_01.asc) | Évaluer si un registre de zones / l'horodatage du clic ou le drag sont nécessaires ; focus, stress et compilateur non testés |
| **M10 — À FAIRE** | **Collisions 2D : points, rectangles, objets, masques selon besoin** | Non implémenté | API géométrique déterministe, puis collisions graphiques seulement si utiles |
| **M11 — À ÉTUDIER** | Compatibilité graphique AMOS : `Screen Copy` étendu, Bob/Icon, Turbo `F Draw` / `F Plot`, palette et fontes | Compatibilité AMOS/AMCAF avec l'écran Intuition AGA **non démontrée** | Évaluer les primitives existantes et valider les besoins par des tests indépendants |
| M12+ — EXTENSIONS | Palette AGA 24 bits complète, sprites matériels, scrolling, dual playfield, Copper avancé, optimisations | Planifié ou optionnel selon besoins | Étapes indépendantes, sans retarder les fondamentaux |

**Les numéros M8–M12 sont des jalons de planification, pas des builds existants.** La priorité concrète pourra changer après validation de M7 ; aucun jalon futur ne vaut accord d'implémentation détaillé.

## 2. M7 — Copper RGB4, bilan du scénario validé

Dossier technique faisant foi : [`M7_COPPER_DESIGN.md`](M7_COPPER_DESIGN.md). Avancement effectif : [`M7_STATUS.md`](M7_STATUS.md).

1. **M7.0 — sécurité (validée sur les scénarios R16–R18, sans stress test) :** confirmer le cycle de vie de `ViewPort.UCopIns` / `UCopList`, la propriété mémoire, l'attachement et le retrait avec l'écran Intuition. Ne jamais détourner `COP1LC/COP2LC`. `FreeVPortCopLists` ne doit pas être utilisé comme simple nettoyage de notre seule liste.
2. **M7.1 — R16/R17 PASS sous WinUAE sur leurs scénarios :** `Aga Copper Clear` crée une liste vide terminée sur l'écran privé ; `Aga Copper On` l'applique avec `MakeScreen/RethinkDisplay` ; `Aga Copper Off` la détache et libère les allocations possédées par l'extension après synchronisation. **R17 validée sur 3 exécutions** avec Off répétés et fermetures d'écran, fin AMOS normale ligne 83. Les 23 segments R16 restent inchangés (hors `GetP`). Les listes raster actives, les fuites mémoire éventuelles et le matériel réel restent hors de ce PASS. **R18 `Wait/Move/End` : PASS WinUAE sur le test raster du 10/11/2026.**
3. **M7.2 — effet raster minimal : PASS WinUAE.** liste contrôlée, WAITs croissants et MOVE limités à `COLOR00..COLOR31`, RGB4 12 bits dans cette première étape. Pas d'accès générique aux registres AGA ni de BPLCON3.
4. **M7.3 — recette : PASS AMOS interprété/WinUAE.** un seul programme AMOS de validation, raster visible, `Off` propre, `Aga Swap`, fermeture/réouverture, interruption clavier. Vérifier séparément CPU/CI, interprété WinUAE, Compiler et Amiga réel.
5. **Après preuve du noyau :** palette AGA 24 bits, banques de couleurs, effets plus sophistiqués ; pas d'anticipation avant le premier PASS.

**R16 WinUAE (10/11/2026) :** `C1/C2/C3=1`, `OPEN/REOPEN=1`, `SWAP=1`, `KEY 67`, `CLOSE X2 RETURNED`, fin ligne 74. **R17 WinUAE (10/11/2026) : PASS 3/3**, `C1/ON1/SWAP/OFF1/OFF2/C2/ON2/OFF3/REOPEN/C3/ON3/OFF4=1`, `KEY 67`, `CLOSE X2 RETURNED`, fin ligne 83. Tests archivés. **R18 WinUAE (10/11/2026) : PASS**, raster rouge/vert/bleu/noir visible ; `W1..W4=M1..M4=1`, rejets `BADREG/RGB/WAIT/END2/AFTER=0`, `END/ON/SWAP/OFF/OFF2/REOPEN/CLEAR2/ON2/OFF3=1`, `KEY 68`, `CLOSE X2 RETURNED`, fin ligne 95. Test corrigé archivé. **Non testés :** stress/fuites, Compiler et matériel réel. Voir [R16](M7_COPPER_R16.md), [R17](M7_COPPER_R17.md) et [R18](M7_COPPER_R18.md).

## 3. M8–M10 — interaction, clics et collisions

Spécification fonctionnelle de référence : [`INTERACTIONS_COLLISIONS.md`](INTERACTIONS_COLLISIONS.md).

- **M8, souris :** R19 X/Y non bloquantes **PASS CPU (76 cas) et WinUAE** le 10/11/2026, `P1=(0,0)` et `P2=(319,255)`. [Test archivé](../tests/passed/M8_R19_MOUSE_POSITION_01.asc). À développer : boutons, transitions, clic unique, focus/drag éventuel. Compiler et Amiga réel non testés.
- **M9, zones cliquables :** rectangles `(x,y,largeur,hauteur)`, identification par ID, activable/désactivable, règle de bord explicite, priorité si deux zones se recouvrent, clic déclenché une seule fois et état lié à l'écran.
- **M10, collisions :** point/rectangle, rectangle/rectangle (AABB), puis Bob/sprite/tuile et masque pixel éventuel. Séparer **détection de collision** et **résolution du déplacement / physique / gameplay**, qui appartient au jeu sauf besoin commun démontré.

Les hit-tests peuvent être de simples fonctions AMOS/extension sans matériel AGA. **Ne pas lier artificiellement les collisions au Copper** : ce sont des fonctions de logique 2D différentes.

## 4. Compatibilité graphique AMOS/AMCAF — axe transversal

Les fonctionnalités de l'extension doivent rester **génériques**, indépendantes d'un programme particulier. Toute compatibilité avec les primitives graphiques AMOS et AMCAF est à démontrer dans des scénarios reproductibles, pas à déduire de l'existence d'une commande.

1. **Écran/RastPort AMOS et AMCAF :** vérifier `Change Bank Font`, `Scrn Rastport`, `Text` et `Text Length`. Notre écran Intuition AGA indépendant **n'est pas automatiquement l'écran courant AMOS** ; vérifier les pointeurs `ScOnAd` et `Ec_RastPort` avant toute intégration. Ne pas recréer un moteur de fontes sans preuve d'incompatibilité.
2. **Blitter/copie :** `Aga Blit Copy` couvre les copies dans un **même back buffer** ; ce n'est pas un remplacement universel de `Screen Copy` (copies inter-écrans, caches ou autres formats). Définir les besoins par des tests.
3. **Bob/Icon, transparence/masques :** étudier `Paste Bob`, `Paste Icon`, `F 16 Icon` et `Bob Update`, les contraintes Chip RAM et les conversions éventuelles de banques.
4. **Primitives Turbo :** auditer les sources AMOS/Unity/Turbo de `F Draw` et `F Plot` avant de proposer des équivalents AGA, avec contrats de coordonnées, clipping et bitplanes.
5. **Présentation et palette :** tester `Autoback`, `Screen Swap`, `Colour`, `Palette` et les modes EHB/HAM sans assimiler ces modes à des palettes 256 couleurs indexées.

Les priorités de compatibilité applicative sont **distinctes** de la roadmap générale de l'extension ; les capacités Copper et souris suivent leurs propres validations.

## 5. Règles de décision, livraison et suivi

- **Une seule source d'état immédiat :** [`NEXT_SESSION.md`](NEXT_SESSION.md) et le STATUS du jalon ; la roadmap ne reçoit plus les journaux R1→R15 en tête.
- **Chaque API future reste « proposée »** tant qu'elle ne figure pas dans un binaire et un scénario de validation identifié. Ne pas présenter les commandes de M7–M12 comme disponibles.
- **Gates distinctes** : A = structure HUNK/AP20 + CPU/CI ; B = AMOS interprété/WinUAE ; C = AMOS Compiler ; D = Amiga AGA physique. Ne jamais transformer un préflight Python en PASS matériel.
- **Protection** : `dist/AMOSPro_AGA.Lib` est le candidat de test ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` n'est changé qu'avec validation explicite ; archives et tests passés restent intacts.
- **Au prochain chantier** : lire [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md), le HEAD réel de `main` et les documents/status du jalon, avant de créer un builder ou un test.

**Navigation :** [index documentaire](README.md) · [architecture actuelle](ARCHITECTURE.md) · [Copper M7](M7_COPPER_DESIGN.md) · [souris / zones / collisions](INTERACTIONS_COLLISIONS.md).
