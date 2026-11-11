# Architecture technique — extension AMOS Professional 365 AGA

**Ce document décrit l'architecture actuelle et ses limites, pas la chronologie des prototypes.** La précédente compilation historique de notes R10/R12 reste intacte dans [`history/ARCHITECTURE_LEGACY_20261110.md`](history/ARCHITECTURE_LEGACY_20261110.md). Vérifier le code, les builders et le binaire avant tout changement.

## 1. Vue d'ensemble

`AMOS Professional 365` → appels extension `AP20 / HUNK` → état partagé extension → `Intuition` / `graphics.library` → écran AGA, bitplanes et buffers. La couche AGA est indépendante des écrans historiques gérés par AMOS ; **ne pas supposer** que les commandes natives AMOS dessinent automatiquement sur l'écran Intuition de l'extension.

L'objectif est une API de haut niveau sûre et réutilisable, pas la réécriture d'AMOS ni d'un moteur RPG.

## 2. Socle AMOS/AGA et extension M10

| Domaine | Principales commandes | Périmètre réellement connu |
|---|---|---|
| Chipset / écran | `Aga Detect`, `Aga Screen Open`, `Aga Screen Close`, `Aga Screen Pattern` | Gestion d'écran Intuition AGA ; modes selon capacité AmigaOS |
| Présentation | `Aga Double Buffer`, `Aga Swap`, `Aga Back Fill`, `Aga Wait Vbl` | Double buffering et attente TOF |
| IFF/ILBM | `Aga Pic Info`, `Aga Iff Load` | Métadonnées, chargement image/palette ; M5 clos sur modes testés |
| Palettes M13 | `Aga Palette Load/Set/Get/Save`, `Aga Palette Bank Init/Capture/Apply`, `Aga Fade To Bank` | RGB24 IFF et banques AGAPAL DATA/ABK ; R31 Capture et R32 Apply validées sous AMOS interprété/WinUAE sur leurs scénarios ; R33 Fade To Bank Gate A CPU/CI PASS et WinUAE en attente ; autres fades/cycling non implémentés |
| Clavier | `Aga Key`, `Aga Wait Key` | Input Intuition, attention au focus et Ctrl+C |
| Blitter M6 | `Aga Blit Copy`, `Aga Blit Fill`, `Aga Blit Clear` | Back buffer ; R13/R14/R15 PASS AMOS interprété/WinUAE. |
| Souris M8/R23 (PASS WinUAE scénario) | `Aga Mouse Pressed/Released`, `Aga Key/Wait Key` | Dispatcher central IDCMP, FIFO RAWKEY 16, Gate A CPU/CI PASS 15 cas ; Gate B WinUAE PASS sur clics rapides, FIFO clavier et Ctrl+C. |
| Hotspots M9/R24 (PASS WinUAE sur scénario) | `Aga Hotspot Hit(px,py,x,y,w,h)` | Sans état, bornes finales exclusives ; CPU/CI 402 cas PASS et WinUAE PASS (ID 20 recouvrement, hors zone, retour AMOS) ; aucun registre de zones. |
| Collisions M10/R25 (PASS sur scénario WinUAE) | `Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh)` | AABB sans état, contact bord exclu ; **704 cas CPU/CI PASS, Gate B AMOS/WinUAE PASS** sur 409 images, `DRAWERR 0`, `RESULT 1` et retour AMOS correct. |
| Souris M8/R22 (PASS WinUAE sur scénario) | `Aga Mouse Pressed`, `Aga Mouse Released` | Masques 1/2/4, focus contrôlé, historique privé ; CPU/CI PASS (25 cas) et WinUAE PASS sur le test R22 archivé. |
| Souris M8/R21 (PASS WinUAE) | `Aga Mouse X/Y`, `Aga Mouse Buttons` | R21 0.8.5 : RMBTRAP supprimant la barre Intuition au clic droit ; **CPU/CI 11 cas et WinUAE PASS utilisateur** sur le test archivé. |
| Souris M8/R20 (historique) | `Aga Mouse Buttons` | 21 cas CPU PASS ; sous WinUAE boutons reconnus, mais barre Intuition persistante sur clic droit. |
| Souris M8/R19 | `Aga Mouse X`, `Aga Mouse Y` | **PASS CPU 76 cas et AMOS interprété/WinUAE** pour le test R19 archivé. |

Sur `main`, **R33 0.10.5 est validée Gates A CPU/CI et B fonctionnelle AMOS interprété/WinUAE** : `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R33 (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`, 39 commandes AP20). R33 Fade est bloquante sur 1..255 VBL et termine sur le RGB24 exact ; preuve fonctionnelle [test archivé](../tests/passed/M13_R33_AGAPAL_FADE_01.asc) (`RESULT 1`, `CLOSE RETURNED`, fin ligne 141). **Fluidité visuelle non validée** : le test faisait `Aga Swap` puis `Amos To Back` après les transitions très brèves. [Démo visuelle complémentaire](../examples/fade_to_bank_r33.asc) (150 VBL et dessin visible avant le fade), non encore testée sous WinUAE. Gates C Compiler/D matériel non testées.

**Historique R32 0.10.4 :** Gates A CPU/CI (136 scénarios) et B fonctionnelle AMOS interprété/WinUAE PASS, test [R32 archivé](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc), archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib` préservée (19 244 octets, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894`). R32 n'est plus `LAST_GOOD`, remplacée par R33 validée fonctionnellement. Gates Compiler et Amiga réel non testées.

## 3. ABI, état et ressources

- Extension AP20 : table des tokens/signatures et paramètres, retour entier en D3 (D2=0), dépilement correct des paramètres sur A3. **La source d'autorité technique demeure [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md).**
- L'écran/Window Intuition, le ViewPort, les BitMaps, les ScreenBuffers et les bibliothèques OS sont possédés par l'extension selon leur cycle de vie ; libérer dans l'ordre approprié, avec chemins d'échec sûrs.
- Pas de blocage `WaitPort` / `Exec Wait` infini ; les événements input sont traités de manière coopérative et les tests AMOS doivent pouvoir terminer.
- Les builders reproductibles et la validation CPU vérifient structure et ABI ; **ils ne remplacent pas un test runtime AMOS**.

## 4. Copper — M7 RGB4 validé pour le scénario WinUAE

Se référer **directement** à [M7_COPPER_DESIGN](M7_COPPER_DESIGN.md) et [M7_STATUS](M7_STATUS.md). R16 ajoute `Aga Copper Clear`, initialisation de la liste vide `CEND` sur le ViewPort du Screen Intuition (**PASS WinUAE**). R17 ajoute **`Aga Copper On` / `Off`**, activation via `MakeScreen/RethinkDisplay` puis détachement et libération des allocations de l'extension. **R17 PASS WinUAE (3 exécutions) sur la liste vide. R18 ajoute `Aga Copper Wait`, `Move`, `End` : raster RGB4 visible et Gate B WinUAE PASS pour le scénario testé.** Voir [M7 R18](M7_COPPER_R18.md). Pas de manipulation libre des registres de Copper via AMOS.

## 5. Interaction 2D et compatibilité jeux

[Plan souris / zones / collisions](INTERACTIONS_COLLISIONS.md) : R19/R21/R22 ont fourni les positions, boutons et fronts ; **le dispatcher R23 a passé un test WinUAE de clics rapides, FIFO clavier et Ctrl+C**. **M9/R24 hotspots et M10/R25 AABB sont validés sur leurs scénarios respectifs**. La résolution physique et les tests pixel-perfect sont hors du noyau R25 ; les fonctions géométriques ne dépendent pas du Copper.

**M11 — audit source R25 effectué :** [étude back buffer/RastPort](M11_BACKBUFFER_R25.md) : chaîne `A5+$1C8 → State+32 → DBState+8 → SB0/SB1 → sb_BitMap`, identique octet pour octet entre R23 et R25 sur les segments graphiques. `Aga Back Fill` utilise déjà `InitRastPort` puis `RastPort.BitMap=back`. **Évolution réalisée depuis cette étude :** `Aga Text` R26 utilise `graphics.library/Text` sur le back buffer AGA avec protection Safe, validée sous WinUAE sur les scénarios M11. R27 ajoute le contrôle Safe indépendant aux trois Blitters et réussit les 40 swaps M12. L'audit de départ M11 reste [archivé ici](M11_BACKBUFFER_R25.md). La reprise des fontes avancées est le jalon M14 (pas encore implémenté).

**Compatibilité graphique AMOS/AMCAF à évaluer :** les commandes AMOS et AMCAF telles que `Change Bank Font`, `Scrn Rastport`, `Text`, `Text Length` utilisent l'état graphique AMOS. Notre écran Intuition et son double buffering sont indépendants : **ne pas faire d'essai qui suppose que `Text` AMOS y dessine directement**. Les fonctions AmigaOS `Text` et `SetFont` peuvent viser un `RastPort` propre au back buffer, sous réserve de confirmer le code R25 et le cycle de vie des buffers. `Aga Blit Copy` ne remplace pas toutes les variantes de `Screen Copy`.

## 6. Modes et validations

AGA : palette indexée selon profondeur (1–8 plans), modes EHB/HAM avec sémantique particulière, HAM6/HAM8/SuperHiRes testés en M5 sous WinUAE pour les cas documentés ; cela ne valide pas toutes les combinaisons de ModeID. Les modes DblPAL/DblNTSC, les programmes compilés du candidat R15 et le matériel réel gardent leurs réserves.

**Gates :** A statique/AP20/CPU ; B interprété WinUAE ; C Compiler ; D vrai AGA. Suivre les résultats par jalon dans ses fichiers de STATUS et ne jamais extrapoler un PASS.

**Voir aussi :** [Roadmap](ROADMAP.md), [Index des docs](README.md), [Tests archivés](../tests/passed/), [Builders](../tools/README.md).
