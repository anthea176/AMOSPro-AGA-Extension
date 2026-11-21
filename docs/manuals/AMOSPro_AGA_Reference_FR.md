---
title: "AMOSPro AGA Extension — Manuel des 100 instructions"
subtitle: "Référence AMOS Professional • M19 P2d • 68020+"
author: "AMOSPro-AGA-Extension — documentation API"
date: "21 novembre 2026"
lang: fr-FR
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc-title: "Sommaire"
---

> **Révision documentaire :** 2026-11-21 • **Bibliothèque :** `M19 P2d` • **API :** `100` instructions / `203` entrées AP20 • **CPU minimum :** `MC68020 / 68EC020` • **Chipset :** `AGA`.
> **Empreinte de la bibliothèque :**  
> `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`  
> **Révision du dépôt vérifiée :** [`a2b4a8a9a5a8`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/a2b4a8a9a5a86a789817bab92e49f1a480b1e816) (`main`).

Ce manuel décrit l’**API réellement exposée par la bibliothèque M19 P2d**, sans ajouter de commandes projetées. Il ne s’agit pas du manuel d’AMOS Professional lui-même : les appels `Aga` pilotent un écran Intuition privé et ne sont pas des synonymes des commandes AMOS natives.

## Comment utiliser ce manuel
Chaque fiche donne **le nom exact du token**, **la forme AMOS** (fonction ou instruction), **les paramètres**, **le comportement et les limites**, **un fragment d’appel** et **les prérequis**. Les fragments individuels supposent que l’écran, les banques et les ressources ont été préparés. Seuls les exemples complets de l’annexe sont des programmes autonomes.
Le code est en syntaxe **AMOS Professional**, pas en pseudo-BASIC : blocs `If … End If` sans `Then`, et `End Proc[...]` pour les résultats des procédures. Importer des sources `.asc` par `Project → Merge ASCII` dans un programme vierge.

### Portée de validation
La version P2d a été **promue LAST_GOOD** après tests du programme intégré Bob P2a–P2e sous WinUAE en **Runtime (Gate B)** et avec le **véritable AMOS Compiler (Gate C)**. Le banc a connu **121 refus initiaux de `Aga Swap`, tous récupérés après attente VBL**, dans les deux modes. Ces preuves concernent ce scénario ; elles ne constituent **pas** 100 tests individuels de toute l’API. L’interpréteur strict (Prg State 0) et un Amiga physique (Gate D) ne sont pas testés pour ce banc. Les fiches ci-dessous ne prétendent pas avoir été réexécutées pour cette édition.
[Rapport de promotion P2d](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md) · [Essai intégré Bob](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/bob_p2_all_in_one/README.md).

## Installation et environnement
1. Utiliser un **Amiga AGA A1200/A4000** ou WinUAE configuré avec chipset AGA et CPU **68020/68EC020 minimum**. AMOS Professional doit déjà être installé. Vérifier la RAM Chip disponible.
2. Installer la seule bibliothèque `dist/AMOSPro_AGA.Lib` dans `APSystem` sous le nom `AMOSPro_AGA.Lib` ; effectuer une sauvegarde préalable, puis déclarer la bibliothèque dans un slot AMOS libre (**14** est le slot des tests historiques, uniquement s’il est libre). Conserver ce slot entre les versions ; enregistrer la configuration et relancer AMOS.
3. Contrôler la version installée, la bibliothèque dans `About Loaded Extensions` et le SHA256. Ne pas installer `LAST_GOOD` comme seconde extension ni changer les numéros de slot sans maîtriser les fichiers AMOS déjà tokenisés.
4. **C2P uniquement :** copier séparément la bibliothèque AmigaOS `c2p.library` dans `LIBS:`. Elle ne s’enregistre **pas** comme extension AMOS. `Aga Iff To Chunky` employée seule n’en dépend pas. Une BankFont au format AMCAF est prise en charge par AGA sans imposer l’installation de toutes les commandes AMCAF.
[Installation détaillée](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.fr.md).

## Modèle d’exécution et pièges courants
| Sujet | Règle à respecter |
|---|---|
| **Écran privé** | `Aga Screen Open` crée un seul écran AGA Intuition, différent de `Screen Open` AMOS ; le fermer avant un nouveau mode. |
| **État du buffer** | Dessiner dans la page arrière Safe ; un retour `0` peut exiger une reprise bornée après `Aga Wait Vbl`, puis `Aga Swap`. Ne pas présenter une frame partielle. |
| **Synchronisation** | `Aga Swap` est une **fonction** avec statut, pas `Screen Swap`. `Aga Wait Vbl` est une **instruction** sans résultat. |
| **Rectangles** | Les commandes Blit, Hotspot et Capture prennent une largeur et une hauteur ; `Aga Box` et `Get AGA Bob` utilisent des coins inclusifs. |
| **Couleurs** | Pen/index palette 0 n’est pas forcément noir ni transparent. `Aga Copper Move` attend un RGB4, non un index couleur. |
| **Banques AMOS** | Vérifier l’existence avec `Length(n)` avant `Start(n)` ; ne jamais supposer que les numéros 10, 24, 27 ou 28 sont disponibles. |
| **Compiler** | Un PASS en Runtime ne prouve pas le Compiler. Conserver le même ASC et vérifier la bibliothèque chargée lors des deux essais. |
| **Sprites matériels** | Aucune commande `Aga Sprite` n’existe dans cette API P2d ; le chantier Sprite matériel S0 était en audit. |

## Formats de banque : aide-mémoire
| Format | Contenu et particularités |
|---|---|
| `AGAPAL v1` | Palettes RGB24 : en-tête 16 octets + 776 octets par slot ; emplacement à partir de 0. |
| `AGAPIC v1/v2` | Images compactées ; v1 sans palette embarquée, v2 peut embarquer RGB24 + ModeID. Les fonctions acceptées diffèrent. |
| `AGBO v1` | Banque DATA d’images pour Bobs logiciels, sélection par `Aga Bob Bank` ; masque et image sont deux notions distinctes. |
| `FICON8` | Icônes 16×16×8 planes en banque AMOS (Fast/Chip selon utilisation), identifiants à partir de 1. |
| `FICHIP8` | Cache d’icônes préparé physiquement en Chip RAM pour le Blitter. |
| `AGACBLK` | Capture planaire temporaire du décor en Chip RAM, avec coordonnées de restauration. |
| `C2P chunky` | Banque DATA/WORK de pixels 8 bits linéaires : 320×256 = 81 920 octets au minimum. |

## Index des 100 instructions
Les numéros ci-dessous sont des **numéros de fiche documentaire**, pas des numéros de token AP20.

### Écran, modes vidéo et fichiers IFF (001–007)
[001 Aga Detect](#cmd-001) · [002 Aga Screen Open](#cmd-002)
[003 Aga Screen Close](#cmd-003) · [004 Aga Double Buffer](#cmd-004)
[005 Aga Swap](#cmd-005) · [006 Aga Pic Info](#cmd-006)
[007 Aga Iff Load](#cmd-007)

### Palettes, transitions et banques de couleurs (008–018)
[008 Aga Palette Load](#cmd-008) · [009 Aga Palette Set](#cmd-009)
[010 Aga Palette Get](#cmd-010) · [011 Aga Palette Save](#cmd-011)
[012 Aga Bank Palette Init](#cmd-012) · [013 Aga Bank Palette Capture](#cmd-013)
[014 Aga Bank Palette Apply](#cmd-014) · [015 Aga Bank Palette Fade](#cmd-015)
[016 Aga Fade To Black](#cmd-016) · [017 Aga Fade To White](#cmd-017)
[018 Aga Palette Cycle](#cmd-018)

### Clavier et synchronisation (019–021)
[019 Aga Key](#cmd-019) · [020 Aga Wait Key](#cmd-020)
[021 Aga Wait Vbl](#cmd-021)

### Blitter et rectangles (022–024)
[022 Aga Blit Copy](#cmd-022) · [023 Aga Blit Fill](#cmd-023)
[024 Aga Blit Clear](#cmd-024)

### Copper raster (025–030)
[025 Aga Copper Clear](#cmd-025) · [026 Aga Copper Wait](#cmd-026)
[027 Aga Copper Move](#cmd-027) · [028 Aga Copper End](#cmd-028)
[029 Aga Copper On](#cmd-029) · [030 Aga Copper Off](#cmd-030)

### Souris, zones et collisions rectangulaires (031–037)
[031 Aga Mouse X](#cmd-031) · [032 Aga Mouse Y](#cmd-032)
[033 Aga Mouse Buttons](#cmd-033) · [034 Aga Mouse Pressed](#cmd-034)
[035 Aga Mouse Released](#cmd-035) · [036 Aga Hotspot Hit](#cmd-036)
[037 Aga Rect Overlap](#cmd-037)

### Texte, polices et primitives 2D (038–045)
[038 Aga Text](#cmd-038) · [039 Aga Font Select](#cmd-039)
[040 Aga Bank Font Select](#cmd-040) · [041 Aga Plot](#cmd-041)
[042 Aga Draw](#cmd-042) · [043 Aga Box](#cmd-043)
[044 Aga Circle](#cmd-044) · [045 Aga Mouse Cursor](#cmd-045)

### Images, icônes, captures et caches (046–061)
[046 Aga Bank Image Draw](#cmd-046) · [047 Aga Image Region](#cmd-047)
[048 Aga F Icon](#cmd-048) · [049 Aga F Blit](#cmd-049)
[050 Aga F Icon Bank Create](#cmd-050) · [051 Aga F Icon Bank Put](#cmd-051)
[052 Aga F Chip Bank Create](#cmd-052) · [053 Aga F Chip Stage](#cmd-053)
[054 Aga F Icon Capture](#cmd-054) · [055 Aga C Block Capture](#cmd-055)
[056 Aga C Block Draw](#cmd-056) · [057 Aga C Block Restore](#cmd-057)
[058 Aga Bank Image Info](#cmd-058) · [059 Aga Bank Image Capture](#cmd-059)
[060 Aga Bob Batch](#cmd-060) · [061 Aga Cache Blit](#cmd-061)

### Bobs logiciels AGA (062–083)
[062 Aga Bob Bank](#cmd-062) · [063 Aga Bob Bank Free](#cmd-063)
[064 Get AGA Bob](#cmd-064) · [065 Make AGA Bob Mask](#cmd-065)
[066 No AGA Bob Mask](#cmd-066) · [067 Aga Bob Blit](#cmd-067)
[068 Aga Bob](#cmd-068) · [069 Aga Bob Off](#cmd-069)
[070 Aga Bob Draw](#cmd-070) · [071 Aga Bob Clear](#cmd-071)
[072 Aga Bob Update](#cmd-072) · [073 Aga Bob Priority](#cmd-073)
[074 Aga Limit Bob](#cmd-074) · [075 Aga Del Bob](#cmd-075)
[076 Aga Ins Bob](#cmd-076) · [077 Aga Bob Col](#cmd-077)
[078 Aga Bob Flip](#cmd-078) · [079 Aga Bob Planes](#cmd-079)
[080 Aga Bob Auto Update](#cmd-080) · [081 Aga X Bob](#cmd-081)
[082 Aga Y Bob](#cmd-082) · [083 Aga I Bob](#cmd-083)

### Conversion chunky vers planar (C2P) (084–089)
[084 Aga Iff To Chunky](#cmd-084) · [085 Aga C2P Open](#cmd-085)
[086 Aga C2P Blit](#cmd-086) · [087 Aga C2P Zoom](#cmd-087)
[088 Aga C2P Convert](#cmd-088) · [089 Aga C2P Close](#cmd-089)

### Diagnostics et remplissage (090–093)
[090 Aga Probe](#cmd-090) · [091 Aga Demo](#cmd-091)
[092 Aga Screen Pattern](#cmd-092) · [093 Aga Back Fill](#cmd-093)

### Formes bas niveau à pointeurs (094–100)
[094 Aga Palette Bank Init](#cmd-094) · [095 Aga Palette Bank Capture](#cmd-095)
[096 Aga Palette Bank Apply](#cmd-096) · [097 Aga Fade To Bank](#cmd-097)
[098 Aga Image Draw](#cmd-098) · [099 Aga Image Capture](#cmd-099)
[100 Aga Font Bank Select](#cmd-100)

# Dictionnaire des commandes

## Écran, modes vidéo et fichiers IFF

L’écran Intuition AGA est privé à l’extension. Vérifier chaque ouverture et fermer avant de revenir à AMOS.

### 001. Aga Detect {#cmd-001}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_AGA=Aga Detect
```

**Rôle et comportement —** Détecte le chipset AGA. Un résultat non nul signifie disponible ; la valeur vraie n'est pas obligatoirement 1.

**Retour / effet —** valeur non nulle = AGA détecté ; 0 = absent.

**Exemple d’appel :**
```amos
_AGA=Aga Detect
```

### 002. Aga Screen Open {#cmd-002}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Screen Open(largeur,hauteur,nbCouleurs,modeID)
```

**Rôle et comportement —** Ouvre l'écran Intuition privé de l'extension, indépendant des écrans AMOS. Les couleurs sont un nombre d'entrées (2 à 256 en puissances de deux), non un nombre de plans. Un ModeID AmigaOS est requis ; retour 1/0.

**Paramètres :**
- `largeur` — largeur de l’écran en pixels.
- `hauteur` — hauteur de l’écran en pixels.
- `nbCouleurs` — nombre de couleurs indexées, non nombre de plans.
- `modeID` — identifiant de mode AmigaOS (`$00021000` = PAL LowRes).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** dimensions en pixels

**Exemple d’appel :**
```amos
_OK=Aga Screen Open(320,256,256,$00021000)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 003. Aga Screen Close {#cmd-003}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Screen Close
```

**Rôle et comportement —** Ferme l'écran AGA privé après gestion des messages Safe/Disp. Instruction sans retour ; ne pas la confondre avec Screen Close natif.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Screen Close
```

### 004. Aga Double Buffer {#cmd-004}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_DB=Aga Double Buffer
```

**Rôle et comportement —** Active le double buffering de l'écran privé ; retour 1 en cas de succès, 0 en cas d'échec.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_DB=Aga Double Buffer
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 005. Aga Swap {#cmd-005}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_SW=Aga Swap
```

**Rôle et comportement —** Présente la page arrière préparée. Retour 1 en cas de présentation, 0 si l'état des buffers ne l'autorise pas ; une page DIRTY non validée peut être refusée.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_SW=Aga Swap
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 006. Aga Pic Info {#cmd-006}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_V=Aga Pic Info(fichier$,champ)
```

**Rôle et comportement —** Lit un champ des métadonnées d'un IFF/ILBM par index 0 à 7 ; retourne la valeur ou -1 en cas d'erreur.

**Paramètres :**
- `fichier$` — chemin fichier AmigaDOS, chaîne AMOS.
- `champ` — index du champ : consulter le tableau des métadonnées.

**Retour / effet —** valeur du champ ; −1 en cas d’erreur.

**Exemple d’appel :**
```amos
_W=Aga Pic Info(_FILE$,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 007. Aga Iff Load {#cmd-007}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Iff Load(fichier$)
```

**Rôle et comportement —** Charge pixels et palette d'un IFF/ILBM compatible vers l'écran AGA actif. Retour 1/0 ; ouvrir l'écran avec les dimensions et le mode appropriés auparavant.

**Paramètres :**
- `fichier$` — chemin fichier AmigaDOS, chaîne AMOS.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Iff Load(_FILE$)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

## Palettes, transitions et banques de couleurs

Les entrées de palette sont des indices logiques. Les couleurs 24 bits et les valeurs RGB4 du Copper ne sont pas interchangeables.

### 008. Aga Palette Load {#cmd-008}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Load(_FILE$)
```

**Rôle et comportement —** Importe uniquement le CMAP d'un IFF FORM ILBM, y compris un fichier palette sans BODY ni BMHD. N'écrit aucun pixel. Retour 1/0.

**Paramètres :**
- `_FILE$` — chemin AmigaDOS, chaîne AMOS.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Palette Load(_FILE$)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 009. Aga Palette Set {#cmd-009}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Set(_PEN,_R,_G,_B)
```

**Rôle et comportement —** Modifie une entrée indexée de la ColorMap avec composantes RVB 8 bits (0 à 255), via LoadRGB32. Sans attente VBL. Refuse HAM, EHB et dual playfield ; retour 1/0.

**Paramètres :**
- `_PEN` — index de palette de l’écran privé.
- `_R` — composante rouge 8 bits (0..255).
- `_G` — composante verte 8 bits (0..255).
- `_B` — composante bleue 8 bits (0..255).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Palette Set(1,255,0,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 010. Aga Palette Get {#cmd-010}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_RGB=Aga Palette Get(_PEN)
```

**Rôle et comportement —** Lit une entrée de palette via GetRGB32. Renvoie $00RRGGBB, ou -1 en cas de refus ; la couleur noire vaut 0 et ne signifie pas une erreur.

**Paramètres :**
- `_PEN` — index de palette de l’écran privé.

**Retour / effet —** RGB24 `$00RRGGBB` ; −1 en cas d’erreur.

**Exemple d’appel :**
```amos
_RGB=Aga Palette Get(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 011. Aga Palette Save {#cmd-011}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Save(_FILE$)
```

**Rôle et comportement —** Écrit la ColorMap en IFF FORM ILBM contenant BMHD et CMAP, sans BODY. Le chemin AmigaDOS fait 1 à 255 octets. Écrase le fichier existant, même si une erreur survient ensuite ; retour 1/0.

**Paramètres :**
- `_FILE$` — chemin AmigaDOS, chaîne AMOS.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Attention : un fichier existant est écrasé.

**Exemple d’appel :**
```amos
_OK=Aga Palette Save("RAM:aga_palette.iff")
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 012. Aga Bank Palette Init {#cmd-012}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Palette Init(_B,_N)
```

**Rôle et comportement —** Initialise dans une banque DATA AMOS existante un conteneur AGAPAL v1 de N emplacements (1 à 256), taille exacte 16+776×N octets. Banque 5 à 65535 ; retour 1/0.

**Paramètres :**
- `_B` — numéro de banque DATA AMOS déjà existante.
- `_N` — nombre de slots de palette, de 1 à 256.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** La banque AGAPAL doit exister, de longueur exacte `16 + 776 × N` octets.

**Exemple d’appel :**
```amos
_OK=Aga Bank Palette Init(10,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 013. Aga Bank Palette Capture {#cmd-013}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Palette Capture(_B,_INDEX)
```

**Rôle et comportement —** Copie les couleurs actuelles de l'écran dans un slot AGAPAL v1 d'une banque DATA, indexé à partir de zéro. Ne modifie pas l'écran ; retour 1/0.

**Paramètres :**
- `_B` — numéro de banque DATA AMOS déjà existante.
- `_INDEX` — indice d’emplacement commençant à 0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bank Palette Capture(10,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 014. Aga Bank Palette Apply {#cmd-014}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Palette Apply(_B,_INDEX)
```

**Rôle et comportement —** Applique immédiatement un slot AGAPAL v1 non vide, ou la palette AGAPIC v2 à l'index 0. Le ModeID doit convenir à AGAPIC v2 ; pas de dessin ni attente VBL ; retour 1/0.

**Paramètres :**
- `_B` — numéro de banque DATA AMOS déjà existante.
- `_INDEX` — indice d’emplacement commençant à 0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bank Palette Apply(10,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 015. Aga Bank Palette Fade {#cmd-015}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Palette Fade(_B,_INDEX,_VBL)
```

**Rôle et comportement —** Fondu bloquant vers AGAPAL v1 ou AGAPIC v2 (index 0), de 1 à 255 VBL. La dernière étape garantit la palette cible exacte. Retour 1/0.

**Paramètres :**
- `_B` — numéro de banque DATA AMOS déjà existante.
- `_INDEX` — indice d’emplacement commençant à 0.
- `_VBL` — durée bloquante de 1 à 255 VBL.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bank Palette Fade(10,0,32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 016. Aga Fade To Black {#cmd-016}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Fade To Black(_VBL)
```

**Rôle et comportement —** Fondu bloquant de toutes les entrées logiques de la palette vers le noir exact, de 1 à 255 VBL. Pixels inchangés ; retour 1/0.

**Paramètres :**
- `_VBL` — durée bloquante de 1 à 255 VBL.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Fade To Black(32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 017. Aga Fade To White {#cmd-017}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Fade To White(_VBL)
```

**Rôle et comportement —** Fondu bloquant de toutes les entrées logiques de palette vers le blanc exact, de 1 à 255 VBL. Pixels inchangés ; retour 1/0.

**Paramètres :**
- `_VBL` — durée bloquante de 1 à 255 VBL.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Fade To White(32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 018. Aga Palette Cycle {#cmd-018}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Cycle(First,Last,Direction)
```

**Rôle et comportement —** Décale une seule fois une plage inclusive de couleurs : 0 ≤ First < Last < 256. Direction 1 décale la dernière vers First, -1 inverse. Conserve les composantes RGB32 ; aucun VBL automatique ; retour 1/0.

**Paramètres :**
- `First` — premier index de palette, inclus.
- `Last` — dernier index de palette, inclus.
- `Direction` — sens de rotation : 1 ou −1.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Une seule rotation par appel ; aucune attente VBL implicite.

**Exemple d’appel :**
```amos
_OK=Aga Palette Cycle(1,15,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

## Clavier et synchronisation

Les événements sont des RAWKEY, pas nécessairement des caractères ASCII. `Aga Wait Vbl` attend un rafraîchissement vertical.

### 019. Aga Key {#cmd-019}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_K=Aga Key
```

**Rôle et comportement —** Lecture clavier non bloquante depuis une FIFO RAWKEY de 16 éléments partagée avec le dispatcher d'événements souris. Le code n'est pas de l'ASCII.

**Retour / effet —** code clavier RAWKEY disponible / sentinelle selon état.

**Exemple d’appel :**
```amos
_K=Aga Key
```

### 020. Aga Wait Key {#cmd-020}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_K=Aga Wait Key
```

**Rôle et comportement —** Attend un événement clavier de la fenêtre Intuition AGA et rend le code RAWKEY ; ce n'est pas une valeur ASCII.

**Retour / effet —** code clavier RAWKEY, non ASCII garanti.

**Exemple d’appel :**
```amos
_K=Aga Wait Key
```

### 021. Aga Wait Vbl {#cmd-021}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Wait Vbl
```

**Rôle et comportement —** Attente d'un rafraîchissement vertical par WaitTOF ; ne fait rien en l'absence d'écran AGA ouvert.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Wait Vbl
```

## Blitter et rectangles

Le dernier couple d’arguments indique largeur et hauteur, pas les coordonnées du coin opposé. Dépend de l’état Safe de la page arrière.

### 022. Aga Blit Copy {#cmd-022}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Blit Copy(sourceX,sourceY,destX,destY,largeur,hauteur)
```

**Rôle et comportement —** Copie une zone rectangulaire à l'intérieur d'un même back buffer. Largeur et hauteur sont des dimensions, pas les coins de fin. Test Safe non bloquant avant DMA ; retour 1/0.

**Paramètres :**
- `sourceX` — coordonnée en pixels (rôle source/destination selon son nom).
- `sourceY` — coordonnée en pixels (rôle source/destination selon son nom).
- `destX` — coordonnée en pixels (rôle source/destination selon son nom).
- `destY` — coordonnée en pixels (rôle source/destination selon son nom).
- `largeur` — largeur de l’écran en pixels.
- `hauteur` — hauteur de l’écran en pixels.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Les deux rectangles appartiennent au même back buffer ; largeur et hauteur, pas coins finaux.

**Exemple d’appel :**
```amos
_OK=Aga Blit Copy(16,24,152,24,104,68)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 023. Aga Blit Fill {#cmd-023}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Blit Fill(x,y,largeur,hauteur,indexCouleur)
```

**Rôle et comportement —** Remplit un rectangle de la page arrière avec un index de couleur. Test Safe non bloquant avant DMA ; retour 1/0, sans dessin si le buffer n'est pas prêt.

**Paramètres :**
- `x` — paramètre entier ou adresse selon la description ci-dessous.
- `y` — paramètre entier ou adresse selon la description ci-dessous.
- `largeur` — largeur de l’écran en pixels.
- `hauteur` — hauteur de l’écran en pixels.
- `indexCouleur` — paramètre entier ou adresse selon la description ci-dessous.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** La dernière valeur est un index de couleur, non une couleur RGB24.

**Exemple d’appel :**
```amos
_OK=Aga Blit Fill(16,24,104,68,63)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 024. Aga Blit Clear {#cmd-024}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Blit Clear(x,y,largeur,hauteur)
```

**Rôle et comportement —** Remplit une zone rectangulaire du back buffer avec l'index 0 (qui n'est pas forcément noir). Test Safe, retour 1/0.

**Paramètres :**
- `x` — paramètre entier ou adresse selon la description ci-dessous.
- `y` — paramètre entier ou adresse selon la description ci-dessous.
- `largeur` — largeur de l’écran en pixels.
- `hauteur` — hauteur de l’écran en pixels.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** La mise à zéro concerne l’index de palette 0, pas forcément le noir.

**Exemple d’appel :**
```amos
_OK=Aga Blit Clear(32,40,72,36)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

## Copper raster

Les six appels Copper sont des fonctions qui exigent une affectation. Le Copper autorise uniquement les registres couleur contrôlés par l’API.

### 025. Aga Copper Clear {#cmd-025}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper Clear
```

**Rôle et comportement —** Crée une liste Copper vide pour l'écran privé. À appeler avant d'insérer WAIT ou MOVE. Retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Copper Clear
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 026. Aga Copper Wait {#cmd-026}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper Wait(v,h)
```

**Rôle et comportement —** Insère un WAIT aux coordonnées raster v (0–255) et h (0–222). Les positions WAIT successives doivent être strictement croissantes ; retour 1/0.

**Paramètres :**
- `v` — ligne verticale du raster 0..255.
- `h` — position horizontale 0..222.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Copper Wait(20,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 027. Aga Copper Move {#cmd-027}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper Move(registre,rgb4)
```

**Rôle et comportement —** Insère une écriture de registre couleur : offset pair $180 à $1BE pour COLOR00–COLOR31, et valeur RGB4 12 bits $000 à $FFF. Ce n'est pas un index de palette ; retour 1/0.

**Paramètres :**
- `registre` — registre couleur pair de `$180` à `$1BE`.
- `rgb4` — valeur RVB4 sur 12 bits, et non index palette.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** `$180` désigne COLOR00 ; `$F00` est RGB4 rouge.

**Exemple d’appel :**
```amos
_OK=Aga Copper Move($180,$F00)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 028. Aga Copper End {#cmd-028}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper End
```

**Rôle et comportement —** Finalise une liste Copper non vide. Un second End ou un ajout après End est refusé ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Copper End
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 029. Aga Copper On {#cmd-029}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper On
```

**Rôle et comportement —** Installe la liste Copper préparée et finalisée dans l'affichage Intuition du ViewPort privé ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Copper On
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 030. Aga Copper Off {#cmd-030}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Copper Off
```

**Rôle et comportement —** Retire la liste Copper et restaure l'affichage en libérant les ressources de l'extension. Appel répété autorisé ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Copper Off
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

## Souris, zones et collisions rectangulaires

Les lectures de boutons retournent des masques binaires ; les tests de rectangle travaillent avec des dimensions en pixels.

### 031. Aga Mouse X {#cmd-031}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_MX=Aga Mouse X
```

**Rôle et comportement —** Lit la position horizontale du pointeur en pixels logiques d'écran ; retourne -1 si hors écran ou écran fermé.

**Retour / effet —** position en pixels ; −1 si non disponible.

**Exemple d’appel :**
```amos
_MX=Aga Mouse X
```

### 032. Aga Mouse Y {#cmd-032}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_MY=Aga Mouse Y
```

**Rôle et comportement —** Lit la position verticale du pointeur en pixels logiques d'écran ; retourne -1 si hors écran ou écran fermé.

**Retour / effet —** position en pixels ; −1 si non disponible.

**Exemple d’appel :**
```amos
_MY=Aga Mouse Y
```

### 033. Aga Mouse Buttons {#cmd-033}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_B=Aga Mouse Buttons
```

**Rôle et comportement —** Renvoie l'état instantané des boutons : bit 1 gauche, bit 2 droit, bit 4 central (0–7 cumulable) ; -1 si dispositif/fenêtre indisponible.

**Retour / effet —** masque 0..7 ; −1 en cas d’indisponibilité.

**Exemple d’appel :**
```amos
_B=Aga Mouse Buttons
```

### 034. Aga Mouse Pressed {#cmd-034}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_P=Aga Mouse Pressed
```

**Rôle et comportement —** Retourne les fronts d'appui accumulés depuis le dernier relevé, masque 1/2/4. À distinguer de l'état maintenu Buttons.

**Retour / effet —** masque de fronts 0..7.

**Exemple d’appel :**
```amos
_P=Aga Mouse Pressed
```

### 035. Aga Mouse Released {#cmd-035}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_R=Aga Mouse Released
```

**Rôle et comportement —** Retourne les fronts de relâchement accumulés depuis le dernier relevé, masque 1/2/4, indépendamment de Pressed.

**Retour / effet —** masque de fronts 0..7.

**Exemple d’appel :**
```amos
_R=Aga Mouse Released
```

### 036. Aga Hotspot Hit {#cmd-036}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_HIT=Aga Hotspot Hit(_PX,_PY,_X,_Y,_W,_H)
```

**Rôle et comportement —** Teste l'appartenance d'un point au rectangle défini par origine X/Y et dimensions W/H. Retour entier 1 dedans, 0 dehors.

**Paramètres :**
- `_PX` — abscisse du point testé.
- `_PY` — ordonnée du point testé.
- `_X` — origine X de la zone.
- `_Y` — origine Y de la zone.
- `_W` — largeur de la zone, en pixels.
- `_H` — hauteur de la zone, en pixels.

**Retour / effet —** 1 = point dans le rectangle, 0 = hors rectangle.

**Exemple d’appel :**
```amos
_HIT=Aga Hotspot Hit(20,30,10,10,64,40)
```

### 037. Aga Rect Overlap {#cmd-037}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_C=Aga Rect Overlap(_AX,_AY,_AW,_AH,_BX,_BY,_BW,_BH)
```

**Rôle et comportement —** Teste le recouvrement de surfaces de deux rectangles (origine et dimensions de chacun). Retour 1 en cas de surface commune, 0 sinon.

**Paramètres :**
- `_AX` — origine X du rectangle A.
- `_AY` — origine Y du rectangle A.
- `_AW` — largeur du rectangle A.
- `_AH` — hauteur du rectangle A.
- `_BX` — origine X du rectangle B.
- `_BY` — origine Y du rectangle B.
- `_BW` — largeur du rectangle B.
- `_BH` — hauteur du rectangle B.

**Retour / effet —** 1 = intersections, 0 = aucune.

**Exemple d’appel :**
```amos
_C=Aga Rect Overlap(0,0,32,32,16,16,32,32)
```

## Texte, polices et primitives 2D

L’écriture se fait sur la page arrière. Les polices AmigaOS et les BankFonts AMCAF sont deux voies distinctes.

### 038. Aga Text {#cmd-038}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)
```

**Rôle et comportement —** Dessine une ligne de texte JAM1 transparente dans le back buffer : X, Y de ligne de base, index de couleur, chaîne AMOS. Retour 1/0.

**Paramètres :**
- `_X` — position horizontale en pixels.
- `_BASELINE_Y` — ordonnée de ligne de base du texte.
- `_PEN` — index de palette du texte.
- `_TEXT$` — texte AMOS à tracer.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Text(16,32,1,"AGA TEXT")
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 039. Aga Font Select {#cmd-039}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Font Select(_FONT$,_YSIZE)
```

**Rôle et comportement —** Charge une police AmigaOS .font par diskfont.library et sélectionne sa taille verticale (1 à 255). Retour 1/0.

**Paramètres :**
- `_FONT$` — nom de la police AmigaOS `.font`.
- `_YSIZE` — hauteur de police demandée, 1 à 255.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Font Select("topaz.font",8)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 040. Aga Bank Font Select {#cmd-040}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Font Select(Bank)
```

**Rôle et comportement —** Sélectionne une BankFont AMCAF à partir d'un numéro de banque DATA vivant ; adresse et longueur sont résolues automatiquement. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Utilise une BankFont au format AMCAF ; la présence de l’extension AMCAF n’est pas imposée par cet appel.

**Exemple d’appel :**
```amos
_OK=Aga Bank Font Select(10)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 041. Aga Plot {#cmd-041}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Plot(X,Y,Pen)
```

**Rôle et comportement —** Pose un pixel dans le back buffer aux coordonnées X/Y, avec index couleur valide pour la profondeur active. Retour 1/0.

**Paramètres :**
- `X` — coordonnée X du pixel.
- `Y` — coordonnée Y du pixel.
- `Pen` — index de couleur de la palette courante.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Plot(24,40,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 042. Aga Draw {#cmd-042}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Draw(X1,Y1,X2,Y2,Pen)
```

**Rôle et comportement —** Trace une ligne d'un pixel entre deux points (extrémités incluses), avec gestion des parties hors écran selon le contrat de clipping. Retour 1/0.

**Paramètres :**
- `X1` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y1` — coordonnée en pixels (rôle source/destination selon son nom).
- `X2` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y2` — coordonnée en pixels (rôle source/destination selon son nom).
- `Pen` — index de couleur de la palette courante.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Draw(10,20,80,100,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 043. Aga Box {#cmd-043}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Box(X1,Y1,X2,Y2,Pen)
```

**Rôle et comportement —** Trace le contour d'un rectangle à partir de deux coins inclusifs. Les quatre coordonnées ne sont pas des dimensions ; retour 1/0.

**Paramètres :**
- `X1` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y1` — coordonnée en pixels (rôle source/destination selon son nom).
- `X2` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y2` — coordonnée en pixels (rôle source/destination selon son nom).
- `Pen` — index de couleur de la palette courante.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Coordonnées des deux coins inclusifs ; ne pas confondre avec les dimensions du Blitter.

**Exemple d’appel :**
```amos
_OK=Aga Box(10,20,90,90,3)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 044. Aga Circle {#cmd-044}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Circle(CX,CY,Radius,Pen)
```

**Rôle et comportement —** Trace un cercle de contour centré sur CX/CY, rayon entier de 0 à 32767 et index de couleur. Rayon zéro : un pixel ; retour 1/0.

**Paramètres :**
- `CX` — abscisse du centre.
- `CY` — ordonnée du centre.
- `Radius` — rayon entier positif (0..32767).
- `Pen` — index de couleur de la palette courante.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Circle(80,80,24,4)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 045. Aga Mouse Cursor {#cmd-045}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Mouse Cursor(Visible)
```

**Rôle et comportement —** Affiche (1) ou masque (0) uniquement le curseur Intuition de la fenêtre AGA privée. Ne réserve pas un canal Sprite matériel ; retour 1/0.

**Paramètres :**
- `Visible` — 0 = masquer ; 1 = afficher.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Mouse Cursor(0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

## Images, icônes, captures et caches

AGAPIC, FICON8, FICHIP8 et AGACBLK ne sont pas des formats interchangeables. Respecter Chip/Fast et les banques actives.

### 046. Aga Bank Image Draw {#cmd-046}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Image Draw(Bank,X,Y,Mode)
```

**Rôle et comportement —** Dessine une image AGAPIC v1/RLE stockée dans une banque DATA vivante, résolue par numéro. Destination dans le back buffer ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Mode` — mode entier spécifique à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bank Image Draw(10,32,32,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 047. Aga Image Region {#cmd-047}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Image Region(Bank,SrcX,SrcY,Width,Height,X,Y,Mode)
```

**Rôle et comportement —** Dessine une région source de dimensions Width/Height dans une image AGAPIC d'une banque DATA. Source SrcX/SrcY et destination X/Y sont distinctes ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `SrcX` — coordonnée en pixels (rôle source/destination selon son nom).
- `SrcY` — coordonnée en pixels (rôle source/destination selon son nom).
- `Width` — largeur positive en pixels.
- `Height` — hauteur positive en pixels.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Mode` — mode entier spécifique à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Image Region(10,0,0,16,16,64,32,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 048. Aga F Icon {#cmd-048}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Icon(Bank,IconID,X,Y,Mode)
```

**Rôle et comportement —** Dessine au CPU une icône FICON8 de 16×16 pixels et 8 plans, identifiant à partir de 1, depuis la banque DATA vers le back buffer ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `IconID` — identifiant d’icône, à partir de 1.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Mode` — mode entier spécifique à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Icon(11,1,32,32,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 049. Aga F Blit {#cmd-049}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Blit(CacheBank,IconID,X,Y,Mode)
```

**Rôle et comportement —** Dessine au Blitter une icône 16×16×8 depuis un cache FICHIP8 physiquement en Chip RAM. Mode 0 opaque, mode 1 transparent ; retour 1/0.

**Paramètres :**
- `CacheBank` — numéro de banque AMOS selon le format attendu.
- `IconID` — identifiant d’icône, à partir de 1.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Mode` — mode entier spécifique à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Blit(12,1,32,32,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 050. Aga F Icon Bank Create {#cmd-050}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Icon Bank Create(Bank,Count)
```

**Rôle et comportement —** Crée une banque DATA FICON8 d'icônes 16×16×8 avec 4 à 4096 emplacements vides. Banque libre 5 à 65535 ; priorité Fast RAM ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `Count` — nombre d’éléments, borné par le format.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Icon Bank Create(11,16)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 051. Aga F Icon Bank Put {#cmd-051}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Icon Bank Put(DestBank,IconID,PixelBank,ByteOffset)
```

**Rôle et comportement —** Convertit 256 indices chunky 8 bits d'une banque DATA source à partir de ByteOffset dans un emplacement FICON8 existant. ID à partir de 1 ; retour 1/0.

**Paramètres :**
- `DestBank` — numéro de banque AMOS selon le format attendu.
- `IconID` — identifiant d’icône, à partir de 1.
- `PixelBank` — numéro de banque AMOS selon le format attendu.
- `ByteOffset` — paramètre entier ou adresse selon la description ci-dessous.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Icon Bank Put(11,1,13,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 052. Aga F Chip Bank Create {#cmd-052}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Chip Bank Create(CacheBank,Count)
```

**Rôle et comportement —** Crée une banque cache FICHIP8 de 4 à 4096 icônes 16×16×8 en vraie Chip RAM, destinée aux transferts Blitter. Retour 1/0.

**Paramètres :**
- `CacheBank` — numéro de banque AMOS selon le format attendu.
- `Count` — nombre d’éléments, borné par le format.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Chip Bank Create(12,16)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 053. Aga F Chip Stage {#cmd-053}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Chip Stage(SourceBank,CacheBank,IconID)
```

**Rôle et comportement —** Copie/prépare l'icône FICON8 désignée dans le cache FICHIP8 du même ID, avec réservation Chip déjà faite. Retour 1/0.

**Paramètres :**
- `SourceBank` — numéro de banque AMOS selon le format attendu.
- `CacheBank` — numéro de banque AMOS selon le format attendu.
- `IconID` — identifiant d’icône, à partir de 1.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Chip Stage(11,12,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 054. Aga F Icon Capture {#cmd-054}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga F Icon Capture(Bank,IconID,X,Y)
```

**Rôle et comportement —** Capture un carré 16×16 du back buffer à huit plans dans un emplacement FICON8 existant ; rectangle entièrement à l'écran. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `IconID` — ID de destination de l’icône existante, commençant à 1.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga F Icon Capture(11,1,32,32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 055. Aga C Block Capture {#cmd-055}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C Block Capture(Bank,X,Y,Width,Height,Method)
```

**Rôle et comportement —** Capture des données planaires non compressées dans une banque AGACBLK résidant physiquement en Chip RAM. Paramètre Method choisit CPU/Blitter suivant contrat ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Width` — largeur positive en pixels.
- `Height` — hauteur positive en pixels.
- `Method` — méthode de transfert : 0 CPU8, 1 CPU16, 2 Blitter pour CBlock.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** La banque de destination AGACBLK doit se trouver en vraie Chip RAM.

**Exemple d’appel :**
```amos
_OK=Aga C Block Capture(14,32,32,16,16,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 056. Aga C Block Draw {#cmd-056}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C Block Draw(Bank,X,Y,Method)
```

**Rôle et comportement —** Restaure à X/Y un CBlock AGACBLK opaque, y compris l'index zéro. Method 0 CPU8, 1 CPU16, 2 Blitter ; respecter l'alignement X 8/16 pixels ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Method` — méthode de transfert : 0 CPU8, 1 CPU16, 2 Blitter pour CBlock.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga C Block Draw(14,64,64,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 057. Aga C Block Restore {#cmd-057}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C Block Restore(Bank,Method)
```

**Rôle et comportement —** Restaure le CBlock Chip à sa position de capture mémorisée. Method 0 CPU8, 1 CPU16, 2 Blitter ; la banque est libérée par Erase Bank ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `Method` — méthode de transfert : 0 CPU8, 1 CPU16, 2 Blitter pour CBlock.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga C Block Restore(14,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 058. Aga Bank Image Info {#cmd-058}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_VALEUR=Aga Bank Image Info(Bank,Champ)
```

**Rôle et comportement —** Lit des métadonnées d'une banque DATA AGAPIC sans modifier pixels ni banque. Champs documentés : 1 largeur, 2 hauteur, 3 profondeur, 4 nombre de couleurs ; autres champs selon le format.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `Champ` — identifiant du champ de métadonnées.

**Retour / effet —** valeur du champ d’information ; consulter les champs du contrat AGAPIC.

**Exemple d’appel :**
```amos
_W=Aga Bank Image Info(10,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 059. Aga Bank Image Capture {#cmd-059}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)
```

**Rôle et comportement —** Capture un rectangle du back buffer dans une nouvelle banque AGAPIC libre. Version 1 ou 2 ; v2 embarque une palette RGB24 et le ModeID. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Width` — largeur positive en pixels.
- `Height` — hauteur positive en pixels.
- `TransparentIndex` — paramètre entier ou adresse selon la description ci-dessous.
- `Version` — paramètre entier ou adresse selon la description ci-dessous.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bank Image Capture(10,0,0,32,32,0,2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 060. Aga Bob Batch {#cmd-060}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Batch(DescriptorBank,Count)
```

**Rôle et comportement —** Dessine 1 à 256 descriptions BOB1 de banque DATA dans l'ordre, dans le back buffer inactif et Safe. Pas un gestionnaire de Bobs persistants ; retour 1/0.

**Paramètres :**
- `DescriptorBank` — banque DATA contenant des descripteurs BOB1.
- `Count` — nombre de Bobs dans le lot, au plus 256.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bob Batch(15,4)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 061. Aga Cache Blit {#cmd-061}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Cache Blit(CacheBank,X,Y,Mode)
```

**Rôle et comportement —** Dessine via Blitter un cache planaire AGPC 16×16×8 en vraie Chip RAM. Son masque de visibilité est distinct de la couleur zéro ; retour 1/0.

**Paramètres :**
- `CacheBank` — numéro de banque AMOS selon le format attendu.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Mode` — mode entier spécifique à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Cache Blit(16,32,32,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

## Bobs logiciels AGA

La banque AGBO, les objets persistants, leurs images et les pages physiques ont des cycles de vie différents. Ne pas présenter une page non prête.

### 062. Aga Bob Bank {#cmd-062}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Bob Bank _BANK
```

**Rôle et comportement —** Sélectionne ou prépare la banque AGBO v1 désignée par son numéro (5 à 65535). La banque peut être vide ; pas de retour fonction.

**Paramètres :**
- `_BANK` — numéro de banque AGBO DATA.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Bob Bank 24
```
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 063. Aga Bob Bank Free {#cmd-063}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Bob Bank Free _BANK
```

**Rôle et comportement —** Libère la mise en cache Chip liée à la banque AGBO et désactive les Bobs qui l'utilisent, sous condition de frame CLEAN. Ne détruit pas arbitrairement d'autres banques ; pas de retour.

**Paramètres :**
- `_BANK` — numéro de banque AGBO DATA.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Bob Bank Free 24
```

### 064. Get AGA Bob {#cmd-064}

**Forme AMOS :** Instruction (sans affectation)

```amos
Get AGA Bob _I,_X1,_Y1,_X2,_Y2
```

**Rôle et comportement —** Capture dans la banque AGBO sélectionnée une image ID 1 à 4096 depuis les coins inclusifs du back buffer. Exemple : de (0,0) à (31,31) produit 32×32. Instruction sans retour.

**Paramètres :**
- `_I` — ID d’image AGBO destination, 1..4096.
- `_X1` — coin gauche inclusif du rectangle.
- `_Y1` — coin haut inclusif du rectangle.
- `_X2` — coin droit inclusif du rectangle.
- `_Y2` — coin bas inclusif du rectangle.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Point de vigilance —** `X1,Y1,X2,Y2` sont inclusifs ; (0,0)–(31,31) donne 32×32.

**Exemple d’appel :**
```amos
Get AGA Bob 1,0,0,31,31
```
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 065. Make AGA Bob Mask {#cmd-065}

**Forme AMOS :** Instruction (sans affectation)

```amos
Make AGA Bob Mask _I,_C
```

**Rôle et comportement —** Construit ou remplace le masque de transparence d'une image AGBO existante : les pixels d'index C deviennent transparents. Instruction sans retour.

**Paramètres :**
- `_I` — ID d’image AGBO existante, 1..4096.
- `_C` — index de palette qui devient transparent.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Make AGA Bob Mask 1,0
```

### 066. No AGA Bob Mask {#cmd-066}

**Forme AMOS :** Instruction (sans affectation)

```amos
No AGA Bob Mask _I
```

**Rôle et comportement —** Retire le masque de transparence d'une image AGBO, rendant tous les pixels opaques (y compris index 0). Instruction sans retour.

**Paramètres :**
- `_I` — ID d’image AGBO dont retirer le masque.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Point de vigilance —** Sans masque : les pixels index 0 sont opaques.

**Exemple d’appel :**
```amos
No AGA Bob Mask 1
```

### 067. Aga Bob Blit {#cmd-067}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Blit(_I,_X,_Y)
```

**Rôle et comportement —** Dessine immédiatement l'image AGBO I sélectionnée aux coordonnées signées X/Y dans le back buffer, sans créer un Bob persistant. Retour 1/0.

**Paramètres :**
- `_I` — ID d’image AGBO à afficher.
- `_X` — position de dessin X, signée.
- `_Y` — position de dessin Y, signée.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bob Blit(1,32,32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 068. Aga Bob {#cmd-068}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Bob _N,_X,_Y,_I
```

**Rôle et comportement —** Déclare ou déplace un Bob persistant ID 1 à 64, avec image I d'une banque AGBO identifiée. Les coordonnées X/Y sont signées. Instruction sans retour.

**Paramètres :**
- `_N` — identifiant de Bob persistant, 1..64.
- `_X` — position du Bob X, signée.
- `_Y` — position du Bob Y, signée.
- `_I` — identifiant d’image AGBO, 1..4096.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Bob 1,32,32,1
```
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 069. Aga Bob Off {#cmd-069}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Bob Off _N
```

**Rôle et comportement —** Désactive le Bob persistant N (1 à 64), sans effacement immédiat, sans dessin ni Swap. Instruction sans retour.

**Paramètres :**
- `_N` — Bob persistant à désactiver, 1..64.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Bob Off 1
```

### 070. Aga Bob Draw {#cmd-070}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Draw
```

**Rôle et comportement —** Dessine les Bobs persistants actifs dans le back buffer Safe, dans l'ordre de priorité. N'effectue pas de présentation implicite ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bob Draw
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 071. Aga Bob Clear {#cmd-071}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Clear
```

**Rôle et comportement —** Restaure le décor mémorisé de la page arrière physique Safe. Ne suppose pas que les deux pages partagent le même fond ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bob Clear
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 072. Aga Bob Update {#cmd-072}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Update
```

**Rôle et comportement —** Prévalide les images, rétablit les fonds nécessaires et dessine les Bobs actifs sur la page arrière physique. Retour 1/0 ; aucune présentation implicite.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Bob Update
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 073. Aga Bob Priority {#cmd-073}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Priority(Mode)
```

**Rôle et comportement —** Configure l'ordre : 0 ID ascendant, 1 Y puis ID ascendants, 2 ID descendant, 3 Y puis ID descendants. Retour 1/0.

**Paramètres :**
- `Mode` — 0 ID ascendant ; 1 Y/ID ascendants ; 2 ID descendant ; 3 Y/ID descendants.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Priorités : 0 ID croissant ; 1 Y puis ID croissants ; 2 ID décroissant ; 3 Y puis ID décroissants.

**Exemple d’appel :**
```amos
_OK=Aga Bob Priority(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 074. Aga Limit Bob {#cmd-074}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Limit Bob(N,X,Y,W,H)
```

**Rôle et comportement —** Définit une limite globale (N=0) ou pour un Bob (N=1 à 64), avec origine signée et dimensions positives. Région demi-ouverte [X,X+W) × [Y,Y+H). Retour 1/0.

**Paramètres :**
- `N` — 0 limite globale ; 1..64 limite de Bob.
- `X` — origine X du rectangle limite.
- `Y` — origine Y du rectangle limite.
- `W` — largeur positive du rectangle limite.
- `H` — hauteur positive du rectangle limite.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Rectangle de limite : `[X,X+W) × [Y,Y+H)` ; N=0 global, N=1..64 individuel.

**Exemple d’appel :**
```amos
_OK=Aga Limit Bob(0,0,0,320,256)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 075. Aga Del Bob {#cmd-075}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Del Bob(Bank,First,Last)
```

**Rôle et comportement —** Supprime des images AGBO dont les identifiants vont de First à Last inclus. Les autres ID restent stables ; interdit les modifications pendant une frame engagée. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `First` — premier ID d’image à supprimer, inclus.
- `Last` — dernier ID d’image à supprimer, inclus.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Del Bob(24,2,4)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 076. Aga Ins Bob {#cmd-076}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Ins Bob(Bank,Image,W,H,Depth)
```

**Rôle et comportement —** Insère dans une banque AGBO un emplacement d'image transparent à identifiant libre, dimensions W/H et profondeur 1 à 8 plans. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `Image` — ID libre de l’image à créer.
- `W` — largeur de l’image en pixels.
- `H` — hauteur de l’image en pixels.
- `Depth` — nombre de plans de l’image, 1 à 8.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Ins Bob(24,2,16,16,8)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 077. Aga Bob Col {#cmd-077}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_C=Aga Bob Col(_A,_B,_MODE)
```

**Rôle et comportement —** Teste deux Bobs persistants actifs distincts : mode 0 rectangles visibles, mode 1 masques de pixels visibles. Retour 1 collision, 0 absence, -1 refus/paramètre invalide.

**Paramètres :**
- `_A` — ID du premier Bob persistant actif, 1..64.
- `_B` — ID distinct du second Bob persistant actif, 1..64.
- `_MODE` — 0 rectangle visible ; 1 masques visibles.

**Retour / effet —** 1 = collision ; 0 = aucune ; −1 = refus.

**Point de vigilance —** Mode 0 = boîtes visibles ; 1 = masques visibles ; distinct des tests `Aga Rect Overlap`.

**Exemple d’appel :**
```amos
_C=Aga Bob Col(1,2,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 078. Aga Bob Flip {#cmd-078}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Flip(_N,_MODE)
```

**Rôle et comportement —** Oriente le Bob N : 0 normal, 1 miroir horizontal, 2 miroir vertical, 3 deux axes. Garde le point X/Y ; retour 1/0.

**Paramètres :**
- `_N` — Bob persistant actif, 1..64.
- `_MODE` — 0 normal ; 1 horizontal ; 2 vertical ; 3 H+V.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Mode 0 normal, 1 horizontal, 2 vertical, 3 combiné ; attention au hotspot.

**Exemple d’appel :**
```amos
_OK=Aga Bob Flip(1,1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 079. Aga Bob Planes {#cmd-079}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Planes(_N,_MASK)
```

**Rôle et comportement —** Choisit les plans de destination écrits par le Bob N au moyen d'un masque de 8 bits (0 à 255). Le masque des plans est distinct du masque de transparence AGBO. Retour 1/0.

**Paramètres :**
- `_N` — Bob persistant actif, 1..64.
- `_MASK` — masque des 8 plans de destination, 0..255.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Les bits 0..7 sélectionnent les plans physiques ; 255 = tous les plans.

**Exemple d’appel :**
```amos
_OK=Aga Bob Planes(1,255)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 080. Aga Bob Auto Update {#cmd-080}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Bob Auto Update(_MODE)
```

**Rôle et comportement —** Mode 1 : effectue la préparation/mise à jour Bob à chaque Aga Swap ; mode 0 : rétablit le mode manuel. Exige une page propre lors du changement ; retour 1/0.

**Paramètres :**
- `_MODE` — 0 : manuel (défaut) ; 1 : automatique avant Swap.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Le mode automatique prépare les Bobs juste avant `Aga Swap` ; ne pas déclencher un Update manuel supplémentaire à l’aveugle.

**Exemple d’appel :**
```amos
_OK=Aga Bob Auto Update(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 081. Aga X Bob {#cmd-081}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_X=Aga X Bob(_N)
```

**Rôle et comportement —** Lit la position X signée d'un Bob persistant actif N. Retour -32769 si absent, désactivé ou inaccessible ; pas d'effet graphique.

**Paramètres :**
- `_N` — identifiant du Bob actif, 1..64.

**Retour / effet —** coordonnée X ; −32769 = Bob indisponible.

**Exemple d’appel :**
```amos
_X=Aga X Bob(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 082. Aga Y Bob {#cmd-082}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_Y=Aga Y Bob(_N)
```

**Rôle et comportement —** Lit la position Y signée d'un Bob persistant actif N. Retour -32769 si absent, désactivé ou inaccessible ; pas d'effet graphique.

**Paramètres :**
- `_N` — identifiant du Bob actif, 1..64.

**Retour / effet —** coordonnée Y ; −32769 = Bob indisponible.

**Exemple d’appel :**
```amos
_Y=Aga Y Bob(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 083. Aga I Bob {#cmd-083}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_I=Aga I Bob(_N)
```

**Rôle et comportement —** Lit le numéro d'image (1 à 4096) du Bob N actif. Retour -32769 en cas de Bob absent, OFF ou inaccessible ; pas d'effet graphique.

**Paramètres :**
- `_N` — identifiant du Bob actif, 1..64.

**Retour / effet —** ID d’image ; −32769 = Bob indisponible.

**Exemple d’appel :**
```amos
_I=Aga I Bob(1)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

## Conversion chunky vers planar (C2P)

Le groupe C2P nécessite `LIBS:c2p.library` en plus de l’extension, excepté le décodage IFF vers chunky utilisé seul.

### 084. Aga Iff To Chunky {#cmd-084}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Iff To Chunky(File$,Bank)
```

**Rôle et comportement —** Décode un IFF/ILBM indexé 320×256 à 4–8 plans, RAW ou ByteRun1, dans une banque DATA/WORK existante ≥81 920 octets. Refuse HAM/EHB, dual playfield et masque ; retour 1/0.

**Paramètres :**
- `File$` — chemin AmigaDOS de l’image ILBM.
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Décodage ILBM indexé 320×256 de 4 à 8 plans RAW/ByteRun1 ; ne requiert pas `c2p.library` utilisé seul.

**Exemple d’appel :**
```amos
_OK=Aga Iff To Chunky(_FILE$,10)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 085. Aga C2P Open {#cmd-085}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C2P Open(Bank)
```

**Rôle et comportement —** Associe une banque chunky DATA/WORK ≥81 920 octets et alloue le contexte C2P/bitmap Chip. Requiert c2p.library dans LIBS:, écran privé 320×256, double buffer. Un second Open échoue ; retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Nécessite `LIBS:c2p.library`, banque chunky DATA/WORK de 81 920 octets au moins, écran compatible et double buffer.

**Exemple d’appel :**
```amos
_OK=Aga C2P Open(10)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 086. Aga C2P Blit {#cmd-086}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C2P Blit(SrcBank,SrcPitch,SrcX,SrcY,W,H,DstX,DstY)
```

**Rôle et comportement —** Copie un rectangle chunky 8 bits opaque depuis une banque source vers la banque chunky du contexte C2P. SrcPitch est un pas en octets. Retour 1/0, sans présentation.

**Paramètres :**
- `SrcBank` — numéro de banque source.
- `SrcPitch` — pas source réel en octets entre deux lignes.
- `SrcX` — coordonnée en pixels (rôle source/destination selon son nom).
- `SrcY` — coordonnée en pixels (rôle source/destination selon son nom).
- `W` — taille en pixels selon le rôle du paramètre.
- `H` — taille en pixels selon le rôle du paramètre.
- `DstX` — coordonnée en pixels (rôle source/destination selon son nom).
- `DstY` — coordonnée en pixels (rôle source/destination selon son nom).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga C2P Blit(11,320,0,0,32,32,64,64)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 087. Aga C2P Zoom {#cmd-087}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C2P Zoom(SrcBank,SrcPitch,SrcX,SrcY,SrcW,SrcH,DstX,DstY,DstW,DstH)
```

**Rôle et comportement —** Redimensionne par plus proche voisin un rectangle chunky 8 bits vers le contexte C2P, avec dimensions source et destination explicites. Retour 1/0.

**Paramètres :**
- `SrcBank` — numéro de banque source.
- `SrcPitch` — pas source réel en octets entre deux lignes.
- `SrcX` — coordonnée en pixels (rôle source/destination selon son nom).
- `SrcY` — coordonnée en pixels (rôle source/destination selon son nom).
- `SrcW` — taille en pixels selon le rôle du paramètre.
- `SrcH` — taille en pixels selon le rôle du paramètre.
- `DstX` — coordonnée en pixels (rôle source/destination selon son nom).
- `DstY` — coordonnée en pixels (rôle source/destination selon son nom).
- `DstW` — taille en pixels selon le rôle du paramètre.
- `DstH` — taille en pixels selon le rôle du paramètre.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga C2P Zoom(11,320,0,0,32,32,64,64,64,64)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 088. Aga C2P Convert {#cmd-088}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C2P Convert
```

**Rôle et comportement —** Convertit la banque chunky liée en bitmap planaire avec c2p.library puis transfère sur la page arrière Safe. Ne change ni palette ni affichage ; Aga Swap explicite requis ; retour 1/0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** La conversion ne provoque pas `Aga Swap` ; la palette doit être gérée à part.

**Exemple d’appel :**
```amos
_OK=Aga C2P Convert
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 089. Aga C2P Close {#cmd-089}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga C2P Close
```

**Rôle et comportement —** Libère le contexte C2P et son bitmap Chip après synchronisation du Blitter. Retour 1 si un contexte est fermé, 0 s'il n'y en a pas (notamment second Close).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga C2P Close
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

## Diagnostics et remplissage

Certaines commandes sont réservées au diagnostic ; leur présence dans les 100 tokens ne leur donne pas un contrat de jeu stable.

### 090. Aga Probe {#cmd-090}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Probe
```

**Rôle et comportement —** Instruction de diagnostic interne sans paramètre, non conçue comme API de jeu. Ne pas fonder une logique applicative dessus.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Probe
```

### 091. Aga Demo {#cmd-091}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_D=Aga Demo
```

**Rôle et comportement —** Fonction de diagnostic interne sans contrat de retour stable pour un jeu. À réserver aux essais explicitement prévus.

**Retour / effet —** diagnostic : ne pas supposer de valeur contractuelle stable.

**Exemple d’appel :**
```amos
_D=Aga Demo
```

### 092. Aga Screen Pattern {#cmd-092}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Screen Pattern
```

**Rôle et comportement —** Trace un motif de diagnostic sur l'écran AGA ouvert. Instruction sans retour, utile pour contrôler la présentation visuelle.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Screen Pattern
```

### 093. Aga Back Fill {#cmd-093}

**Forme AMOS :** Instruction (sans affectation)

```amos
Aga Back Fill couleur
```

**Rôle et comportement —** Remplit toute la page arrière avec un index de couleur (par exemple 255 à huit plans). Instruction sans retour.

**Paramètres :**
- `couleur` — index couleur appliqué à toute la page arrière.

**Retour / effet —** Instruction sans valeur de retour ; ne pas écrire une affectation.

**Exemple d’appel :**
```amos
Aga Back Fill 0
```

## Formes bas niveau à pointeurs

Ces fonctions attendent une adresse de banque valide issue de `Start(bank)` ; vérifier la banque avec `Length(bank)` avant de lire `Start`.

### 094. Aga Palette Bank Init {#cmd-094}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Bank Init(Start(_B),_N)
```

**Rôle et comportement —** Variante bas niveau AGAPAL : adresse Start d'une banque DATA déjà réservée et taille exacte 16+776×N (N=1–256). Retour 1/0 ; vérifier la présence avant Start.

**Paramètres :**
- `Start(_B)` — adresse de banque DATA existante (`Start`), à ne pas demander à une banque absente.
- `_N` — ID ou nombre selon l’opération (voir règles de la section).

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Palette Bank Init(Start(10),2)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 095. Aga Palette Bank Capture {#cmd-095}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Bank Capture(Start(_B),_INDEX)
```

**Rôle et comportement —** Variante bas niveau à pointeur : capture la ColorMap dans un slot AGAPAL à index zéro-based d'une banque réservée. Retour 1/0.

**Paramètres :**
- `Start(_B)` — adresse de banque DATA existante (`Start`), à ne pas demander à une banque absente.
- `_INDEX` — indice d’emplacement commençant à 0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Palette Bank Capture(Start(10),0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 096. Aga Palette Bank Apply {#cmd-096}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Palette Bank Apply(Start(_B),_INDEX)
```

**Rôle et comportement —** Variante bas niveau à pointeur : applique un slot AGAPAL non vide à la palette privée. Aucune écriture de pixels ; retour 1/0.

**Paramètres :**
- `Start(_B)` — adresse de banque DATA existante (`Start`), à ne pas demander à une banque absente.
- `_INDEX` — indice d’emplacement commençant à 0.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Palette Bank Apply(Start(10),0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 097. Aga Fade To Bank {#cmd-097}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Fade To Bank(Start(_B),_INDEX,_VBL)
```

**Rôle et comportement —** Fondu bloquant vers un slot AGAPAL référencé par Start(_B), de 1 à 255 VBL, avec palette finale exacte. Retour 1/0.

**Paramètres :**
- `Start(_B)` — adresse de banque DATA existante (`Start`), à ne pas demander à une banque absente.
- `_INDEX` — indice d’emplacement commençant à 0.
- `_VBL` — durée bloquante de 1 à 255 VBL.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Fade To Bank(Start(10),0,32)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 098. Aga Image Draw {#cmd-098}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Image Draw(Start(_B),Length(_B),_X,_Y,_MODE)
```

**Rôle et comportement —** Variante bas niveau à pointeur et longueur d'une image AGAPIC v1/RLE dans une banque DATA vivante. Dessin dans la page arrière, retour 1/0.

**Paramètres :**
- `Start(_B)` — adresse de banque DATA existante (`Start`), à ne pas demander à une banque absente.
- `Length(_B)` — longueur de la banque existante en octets.
- `_X` — coordonnée en pixels (rôle source/destination selon son nom).
- `_Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `_MODE` — mode de fonctionnement propre à la commande.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Exemple d’appel :**
```amos
_OK=Aga Image Draw(Start(10),Length(10),32,32,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

### 099. Aga Image Capture {#cmd-099}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)
```

**Rôle et comportement —** Crée une banque AGAPIC v1 libre par capture d'un rectangle entièrement contenu dans le back buffer inactif, avec index de transparence. Retour 1/0.

**Paramètres :**
- `Bank` — numéro de banque AMOS vivante, sauf forme pointeur explicitée.
- `X` — coordonnée en pixels (rôle source/destination selon son nom).
- `Y` — coordonnée en pixels (rôle source/destination selon son nom).
- `Width` — largeur positive en pixels.
- `Height` — hauteur positive en pixels.
- `TransparentIndex` — paramètre entier ou adresse selon la description ci-dessous.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** L’image capturée est au format AGAPIC v1 ; utiliser la variante Bank pour demander la version 2.

**Exemple d’appel :**
```amos
_OK=Aga Image Capture(10,0,0,32,32,0)
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*

### 100. Aga Font Bank Select {#cmd-100}

**Forme AMOS :** Fonction numérique (résultat à affecter)

```amos
_OK=Aga Font Bank Select(_START,_LENGTH)
```

**Rôle et comportement —** Variante bas niveau de sélection de BankFont AMCAF par adresse et longueur de banque déjà réservée (Start/Length). Retour 1/0 ; ne requiert pas automatiquement une seconde extension AMCAF.

**Paramètres :**
- `_START` — pointeur de banque AMOS vivante.
- `_LENGTH` — taille de banque en octets.

**Retour / effet —** Fonction numérique. Pour les commandes de statut, `1` indique la réussite et `0` un refus/échec ; consulter la description pour les lectures de données et les cas particuliers.

**Point de vigilance —** Appeler `Length(_B)` sur la banque attendue avant `Start(_B)` pour éviter Bank not reserved.

**Exemple d’appel :**
```amos
_OK=Aga Font Bank Select(Start(10),Length(10))
```
*Fragment isolé : prévoir la création de l’écran/banque et contrôler le retour avant d’enchaîner.*
[Contrat public et autres détails](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md).

# Exemples commentés et schémas d’utilisation

## Exemple A — ouverture et fermeture sûres
Programme complet adapté de `examples/screen.asc`, sans les commentaires initiaux. Aucun fichier image requis. L’instruction de dessin `Aga Screen Pattern` est volontairement diagnostique.
```amos
Cls
Print "AGA SCREEN - 320 X 256"
If Aga Detect=0
   Print "AGA CHIPSET NOT DETECTED"
   End
End If
_OK=Aga Screen Open(320,256,256,$00021000)
If _OK<>1
   Print "SCREEN OPEN FAILED"
   End
End If
Aga Screen Pattern
Amos To Back
For _I=1 To 150
   Aga Wait Vbl
Next _I
Aga Screen Close
Amos To Front
Print "SCREEN CLOSED - BACK IN AMOS"
End
```
[Source originale](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/screen.asc).

## Exemple B — IFF, Blitter et contrôles de retours
Programme complet issu de `examples/blitter.asc`. Choisir un ILBM **320×256×8 plans** compatible, par exemple `examples/demo.iff` ; **dossier monté dans AmigaOS obligatoire**. Ce listing n’est pas un test nouvellement exécuté.
```amos
Cls
Print "AGA BLITTER - SELECT demo.iff"
_FILE$=Fsel$("**")
If _FILE$=""
   Print "CANCELLED"
   End
End If
_W=Aga Pic Info(_FILE$,0)
_H=Aga Pic Info(_FILE$,1)
_D=Aga Pic Info(_FILE$,2)
_C=Aga Pic Info(_FILE$,7)
_MODE=Aga Pic Info(_FILE$,6)
If _W<>320 or _H<>256 or _D<>8 or _C<>256
   Print "PLEASE SELECT A 320X256X8 IFF"
   End
End If
_OPEN=Aga Screen Open(_W,_H,_C,_MODE)
If _OPEN<>1
   Print "SCREEN OPEN FAILED"
   End
End If
_DB=Aga Double Buffer
If _DB<>1
   Aga Screen Close
   Amos To Front
   Print "DOUBLE BUFFER FAILED"
   End
End If
_LOAD=Aga Iff Load(_FILE$)
If _LOAD<>1
   Aga Screen Close
   Amos To Front
   Print "IFF LOAD FAILED"
   End
End If
_F=Aga Blit Fill(16,24,104,68,63)
_C=Aga Blit Clear(32,40,72,36)
_B=Aga Blit Copy(16,24,152,24,104,68)
If _F<>1 or _C<>1 or _B<>1
   Aga Screen Close
   Amos To Front
   Print "BLITTER ERROR ";_F;" ";_C;" ";_B
   End
End If
_SW=Aga Swap
If _SW<>1
   Aga Screen Close
   Amos To Front
   Print "SWAP FAILED"
   End
End If
Amos To Back
_K=Aga Wait Key
Aga Screen Close
Amos To Front
Print "FILL ";_F;" CLEAR ";_C;" COPY ";_B
Print "BLITTER CLOSED - KEY ";_K
End
```
[Source originale](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/blitter.asc).

## Exemple C — effet Copper (fragment)
Après une ouverture d’écran AGA et un double buffer réussis, ces appels forment la séquence de couleur. Ce **fragment n’est pas autonome** : les sorties d’échec et la fermeture doivent être traitées par le programme appelant.
```amos
_C=Aga Copper Clear
_W1=Aga Copper Wait(20,0)
_M1=Aga Copper Move($180,$F00)
_W2=Aga Copper Wait(80,0)
_M2=Aga Copper Move($180,$0F0)
_W3=Aga Copper Wait(140,0)
_M3=Aga Copper Move($180,$00F)
_W4=Aga Copper Wait(200,0)
_M4=Aga Copper Move($180,$000)
_E=Aga Copper End
_ON=Aga Copper On
_SW=Aga Swap
_K=Aga Wait Key
_OFF=Aga Copper Off
```

## Cycle de rendu conseillé
```text
Détection AGA -> Open -> Double Buffer
  -> créer/charger ressources -> attendre une page Safe
  -> dessiner toute la frame -> vérifier les retours
  -> Swap (reprise VBL bornée si refus)
  -> libérer les ressources -> Screen Close -> Amos To Front
```

## Bob manuel et Bob automatique : ne pas mélanger
**Mode manuel :** `Aga Bob Bank` choisit les images, `Get AGA Bob` capture, `Aga Bob` enregistre les objets. La boucle applique selon le scénario `Aga Bob Clear`, `Aga Bob Update`/`Aga Bob Draw`, puis `Aga Swap`, avec vérifications Safe. **Mode automatique P2d :** activer `Aga Bob Auto Update(1)` sur une page CLEAN ; l’étape de préparation se fait avant le Swap. Ne pas ajouter un second Update manuel dans la reprise d’un `Swap` refusé.
**Exemple de référence validé B/C :** utiliser sans modification `examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc` ; il mobilise les banques 24, 27 et 28 (à libérer avant import) et exploite des canaux AMAL natifs en complément des commandes AGA. Les journalisations d’origine sont conservées dans le dépôt.
[Exemple Bob intégral](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc).

# Annexes et vérifications

## Table des champs de Aga Pic Info
| Champ | Donnée renvoyée |
|---:|---|
| 0 | Largeur |
| 1 | Hauteur |
| 2 | Nombre de bitplanes |
| 3 | Nombre de couleurs CMAP |
| 4 | Compression (0 RAW ; 1 ByteRun1) |
| 5 | CAMG original |
| 6 | ModeID utilisable pour l’ouverture |
| 7 | Nombre de couleurs demandé pour l’écran |

## Valeurs et erreurs qui prêtent à confusion
| Cas | Convention |
|---|---|
| `Aga Detect` | non nul = présent ; `−1` peut correspondre à vrai sur WinUAE |
| `Aga Screen Open` / `Aga Double Buffer` | `1` = succès ; `0` = refus |
| `Aga Palette Get` | `$00RRGGBB` = valeur valide ; `−1` = erreur |
| `Aga Pic Info` | `−1` = erreur ; champs indexés `0..7` |
| `Aga Mouse Buttons` | `1/2/4` : gauche/droite/centre ; `−1` invalide |
| `Aga Bob Col` | `1` collision, `0` aucune, `−1` refus |
| `Aga X/Y/I Bob` | `−32769` = Bob invalide/indisponible |
| `Aga Swap` | retour `0` possible si non prêt ; reprise VBL bornée et vérifiée |

## Liste de contrôle avant de publier un programme
- Identifier le binaire exact installé, son slot AMOS et son SHA256 ; ne pas confondre le titre du programme avec la version chargée.
- Vérifier les dépendances : `LIBS:c2p.library`, banques libres et leur taille, IFF/ABK visibles par AmigaOS, RAM Chip suffisante.
- Vérifier les bornes des rectangles, le masque de transparence et l’index couleur ; tester les retours à chaque dessin et Swap.
- Capturer séparément les résultats WinUAE Runtime et ceux du véritable AMOS Compiler ; ne pas annoncer Gate C sur une simulation.
- Vérifier `Aga Screen Close`, le retour à `Amos To Front`, Ctrl+C, la seconde exécution sans fuite, et documenter ce qui reste non testé.

## Sources et références
- [README API FR](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.fr.md)
- [README API EN](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/README.md)
- [EXTENSION_SOURCE_RULES](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/EXTENSION_SOURCE_RULES.md)
- [INSTALL FR](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.fr.md)
- [INSTALL EN](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/INSTALL.md)
- [Bob P2d promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md)
- [Bob P2 integrated tests](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/docs/M19_P2_ALL_IN_ONE_2026-11-21.md)
- [AMOS examples](https://github.com/anthea176/AMOSPro-AGA-Extension/tree/a2b4a8a9a5a86a789817bab92e49f1a480b1e816/examples)
- [Original AMOS Pro manual](https://amospromanual.dev/)

---

**Note de méthode :** syntaxe et signatures recoupées avec les README bilingues du dépôt sur une révision précise. Les exemples courts sont des fragments d’appel illustratifs, **non validés un par un sous AMOS**. Aucune modification du code ou du dépôt par cette documentation.
