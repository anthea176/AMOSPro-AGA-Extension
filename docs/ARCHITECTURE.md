# Architecture technique — extension AMOS Professional 365 AGA

**Ce document décrit l'architecture actuelle et ses limites, pas la chronologie des prototypes.** La précédente compilation historique de notes R10/R12 reste intacte dans [`history/ARCHITECTURE_LEGACY_20261110.md`](history/ARCHITECTURE_LEGACY_20261110.md). Vérifier le code, les builders et le binaire avant tout changement.

## 1. Vue d'ensemble

`AMOS Professional 365` → appels extension `AP20 / HUNK` → état partagé extension → `Intuition` / `graphics.library` → écran AGA, bitplanes et buffers. La couche AGA est indépendante des écrans historiques gérés par AMOS ; **ne pas supposer** que les commandes natives AMOS dessinent automatiquement sur l'écran Intuition de l'extension.

L'objectif est une API de haut niveau sûre et réutilisable, pas la réécriture d'AMOS ni d'un moteur RPG.

## 2. Socle AMOS/AGA et extension M8

| Domaine | Principales commandes | Périmètre réellement connu |
|---|---|---|
| Chipset / écran | `Aga Detect`, `Aga Screen Open`, `Aga Screen Close`, `Aga Screen Pattern` | Gestion d'écran Intuition AGA ; modes selon capacité AmigaOS |
| Présentation | `Aga Double Buffer`, `Aga Swap`, `Aga Back Fill`, `Aga Wait Vbl` | Double buffering et attente TOF |
| IFF/ILBM | `Aga Pic Info`, `Aga Iff Load` | Métadonnées, chargement image/palette ; M5 clos sur modes testés |
| Clavier | `Aga Key`, `Aga Wait Key` | Input Intuition, attention au focus et Ctrl+C |
| Blitter M6 | `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` | Back buffer ; R13/R14/R15 PASS AMOS interprété/WinUAE. |
| Souris M8/R23 (PASS WinUAE scénario) | `Aga Mouse Pressed/Released`, `Aga Key/Wait Key` | Dispatcher central IDCMP, FIFO RAWKEY 16, Gate A CPU/CI PASS 15 cas ; Gate B WinUAE PASS sur clics rapides, FIFO clavier et Ctrl+C. |
| Hotspots M9/R24 (PASS WinUAE sur scénario) | `Aga Hotspot Hit(px,py,x,y,w,h)` | Sans état, bornes finales exclusives ; CPU/CI 402 cas PASS et WinUAE PASS (ID 20 recouvrement, hors zone, retour AMOS) ; aucun registre de zones. |
| Collisions M10/R25 (candidate) | `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)` | AABB sans état, contact bord exclu ; 704 cas 68000 CPU/CI PASS. WinUAE à tester avec double buffering et VBL. |
| Souris M8/R22 (PASS WinUAE sur scénario) | `Aga Mouse Pressed`, `Aga Mouse Released` | Masques 1/2/4, focus contrôlé, historique privé ; CPU/CI PASS (25 cas) et WinUAE PASS sur le test R22 archivé. |
| Souris M8/R21 (PASS WinUAE) | `Aga Mouse X/Y`, `Aga Mouse Buttons` | R21 0.8.5 : RMBTRAP supprimant la barre Intuition au clic droit ; **CPU/CI 11 cas et WinUAE PASS utilisateur** sur le test archivé. |
| Souris M8/R20 (historique) | `Aga Mouse Buttons` | 21 cas CPU PASS ; sous WinUAE boutons reconnus, mais barre Intuition persistante sur clic droit. |
| Souris M8/R19 | `Aga Mouse X`, `Aga Mouse Y` | **PASS CPU 76 cas et AMOS interprété/WinUAE** pour le test R19 archivé. |

Sur le nouveau `main`, **R25 0.9.1 est la bibliothèque candidate : Gate A CPU/CI PASS 704 cas, Gate B WinUAE NON TESTÉE**. [Test graphique animé R25](../tests/current/M10_R25_RECT_OVERLAP_VISUAL_01.asc) : couleur indexée bleu/vert/rouge, double-buffer `Aga Swap` et `Aga Wait Vbl` à chaque image. [Contrat M10](M10_RECT_OVERLAP_R25.md). R24 0.9.0 reste la dernière archive validée sous WinUAE ; `LAST_GOOD` R10 et archives M8/M9 intactes. Compiler, hardware, focus, stress non testés.

## 3. ABI, état et ressources

- Extension AP20 : table des tokens/signatures et paramètres, retour entier en D3 (D2=0), dépilement correct des paramètres sur A3. **La source d'autorité technique demeure [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md).**
- L'écran/Window Intuition, le ViewPort, les BitMaps, les ScreenBuffers et les bibliothèques OS sont possédés par l'extension selon leur cycle de vie ; libérer dans l'ordre approprié, avec chemins d'échec sûrs.
- Pas de blocage `WaitPort` / `Exec Wait` infini ; les événements input sont traités de manière coopérative et les tests AMOS doivent pouvoir terminer.
- Les builders reproductibles et la validation CPU vérifient structure et ABI ; **ils ne remplacent pas un test runtime AMOS**.

## 4. Copper — M7 RGB4 validé pour le scénario WinUAE

Se référer **directement** à [M7_COPPER_DESIGN](M7_COPPER_DESIGN.md) et [M7_STATUS](M7_STATUS.md). R16 ajoute `Aga Copper Clear`, initialisation de la liste vide `CEND` sur le ViewPort du Screen Intuition (**PASS WinUAE**). R17 ajoute **`Aga Copper On` / `Off`**, activation via `MakeScreen/RethinkDisplay` puis détachement et libération des allocations de l'extension. **R17 PASS WinUAE (3 exécutions) sur la liste vide. R18 ajoute `Aga Copper Wait`, `Move`, `End` : raster RGB4 visible et Gate B WinUAE PASS pour le scénario testé.** Voir [M7 R18](M7_COPPER_R18.md). Pas de manipulation libre des registres de Copper via AMOS.

## 5. Interaction 2D et compatibilité jeux

[Plan souris / zones / collisions](INTERACTIONS_COLLISIONS.md) : R19 fournit les coordonnées X/Y validées sous WinUAE (voir [R19](M8_MOUSE_R19.md)). La lecture instantanée des boutons est disponible et validée en R21 ; les transitions Pressed/Released de R22 sont validées sur le scénario d'échantillonnage, et le dispatcher événementiel R23 existe en candidate préflight pour les clics très courts. La lecture réelle sous WinUAE, Ctrl+C et le focus doivent encore être validés. M9 zones et M10 collisions pourront utiliser des calculs logiciels sans dépendance au Copper.

**Compatibilité graphique AMOS/AMCAF à évaluer :** `Change Bank Font`, `Scrn Rastport`, `Text`, `Text Length`, ainsi que `ScOnAd` et `Ec_RastPort`, utilisent des structures d'écran/RastPort AMOS qui ne sont pas garanties par notre écran Intuition AGA indépendant. Tester les interfaces existantes avant d'ajouter de nouvelles routines. `Aga Blit Copy` ne remplace pas toutes les variantes de `Screen Copy`.

## 6. Modes et validations

AGA : palette indexée selon profondeur (1–8 plans), modes EHB/HAM avec sémantique particulière, HAM6/HAM8/SuperHiRes testés en M5 sous WinUAE pour les cas documentés ; cela ne valide pas toutes les combinaisons de ModeID. Les modes DblPAL/DblNTSC, les programmes compilés du candidat R15 et le matériel réel gardent leurs réserves.

**Gates :** A statique/AP20/CPU ; B interprété WinUAE ; C Compiler ; D vrai AGA. Suivre les résultats par jalon dans ses fichiers de STATUS et ne jamais extrapoler un PASS.

**Voir aussi :** [Roadmap](ROADMAP.md), [Index des docs](README.md), [Tests archivés](../tests/passed/), [Builders](../tools/README.md).
