# Roadmap — AMOSPro AGA Extension

> **Suivi des travaux uniquement — état vérifié le 14 novembre 2026, branche `main`.**  
> Ce fichier sert à savoir **ce qui fonctionne, ce qui manque et ce qu'on envisage**. Il ne contient ni chronologie des versions, ni comptes rendus de tests, ni incidents clôturés. Les décisions nouvelles nécessitent l'accord de l'auteur.

## 1. État actuel

| Sujet | État |
|---|---|
| **Bibliothèque active** | **R84 v0.13.29 PROMUE `LAST_GOOD`** : `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` identiques (67 904 octets, **76 commandes / 85 entrées AP20**). R83 v0.13.28 reste historique, reproductible par son builder (64 188 octets, 74 commandes). |
| **Validation R84 / R83** | **R84 : Gate A native/CI PASS**, **Gate C AMOS Compiler PASS** (programme avec banque, 4/8 plans, `ERR 0`, Chip 0, Fast −11 920). **Gate B Runtime corrigée NON attestée séparément** ; promotion explicitement autorisée avec cette limite. R83 A/B/C historiques PASS ; `PRG_STATE 0` strict et Gate D physique non testés. |
| **Capacité Compiler V2** | **R84 : trois unités** : C2P 5 558, IFF 2 508, AGA/AGAPIC **56 580 octets**, toutes sous 65 534 octets, et `BSR.W` vérifié (écart maximal 9 000). **Marge AGA R84 : 8 954 octets.** |
| **Test AMOS actif** | `tests/current/AGAPIC_R84_V1_V2_01.asc` — Info, captures native v1/v2 4/8 plans, opaque/masquée, comparaison RLE, sauvegarde ABK, dessin et fermeture ; unique ASC. |
| **Priorités avant M19** | **1. R83 modulaire** : terminée et promue, Gates A/B/C PASS sur `main`. **2. AGAPIC v1/v2 complet** : R84 implémentée et promue avec Gates A/C PASS, Gate B corrigée non attestée séparément ; pas de nouvel essai imposé à l’auteur. |

Références : [binaire et API actuels](../README.fr.md) · [promotion R84](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Gate C compilée](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md).

## 2. Fonctionnalités disponibles

- **Écran AGA privé** : ouverture, double buffering, dessin sur back buffer, Swap, palette et fermeture.
- **AGAPIC v1/v2** : images planaires compressées RLE en banque AMOS, masque facultatif, dessin complet et de régions. **v2** intègre une palette RGB24 et un DisplayModeID vérifié. **`Aga Image Capture` historique crée du v1** ; la nouvelle `Aga Bank Image Capture(...,Version)` crée explicitement v1 ou v2 ; chargement/dessin des deux formats et lecture des métadonnées disponibles.
- **Palettes AGAPAL / AGAPIC v2** : commandes `Aga Bank Palette Init`, `Capture`, `Apply`, `Fade` par **numéro de banque**. La palette de l'image n'est **pas** appliquée automatiquement par le dessin.
- **C2P** : contexte, conversion chunky vers écran AGA, Blit, Zoom et chargement IFF vers chunky ; dépendance externe `LIBS:c2p.library`.
- **Fast Icons / CBlock** : fonctions existantes de capture, cache, transfert et dessin.

La présence d'une fonction dans R82 ne signifie **pas** que les 74 commandes ont chacune été testées dans toutes les configurations.

## 3. Chantiers prioritaires avant M19 — ordre retenu le 14/11/2026

Ces **deux chantiers ont été réalisés** avant M19. R83 a validé l'architecture modulaire ; R84 a ajouté les fonctions natives AGAPIC et a été promue sur accord explicite avec Gates A/C PASS et Gate B corrigée non documentée séparément. La preuve P5 expérimentale reste historique.

### Chantier 1 — R83 modulaire : trois unités AP20

**Sur `main`, R83 v0.13.28 PROMUE `LAST_GOOD` avec autorisation explicite du 14/11/2026.**

- **Binaire actif :** `dist/AMOSPro_AGA.Lib` = R83 **64 188 octets**, 74 commandes R82 inchangées, 83 entrées AP20, trois vraies unités natives : C2P 5 558 octets, IFF→chunky 2 508 octets et AGA/AGAPIC/palettes 52 974 octets. **Aucun remplissage de stress-test**, aucun titre `TEST ONLY`.
- **Source :** `tools/build_aga_r83_modular.py` reconstruit depuis le builder historique R82 SHA-épinglé (SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`) et contrôle le format AP20, les 78 `RBSR`, les quatre liens palettes et la portée du chargeur `BSR.W`. **Gates A CPU/CI MC68020, B Runtime WinUAE et C AMOS Compiler R83 PASS (68030)**.
- **Preuve d'architecture historique :** P5 a passé WinUAE Runtime et Compiler avec ses trois unités natives, AGAPIC v1/v2, C2P Blit/Zoom et 14/14 pixels. Elle contenait 12 Ko de NOP de stress-test, désormais supprimés. Ses résultats ne prouvent pas automatiquement le comportement du binaire R83 raccourci.
- **Test R83 actif :** `tests/current/C2P_R83_MODULAR_01.asc` reprend le banc IFF positif R80/R81 : décodage `Aga Iff To Chunky` sur une entrée ILBM réelle 320×256 (4–8 plans), C2P, Blit, Zoom et fermeture. Les banques 12/13 sont effacées au lancement. Un seul ASC est actif.
- **Promotion R83 réalisée :** Gates B/C confirmées par les journaux utilisateur, accord explicite, binaire actif et `LAST_GOOD` identiques. R82 reste reconstructible dans Git. Aucun tag ni release.
- **Après R83 :** chantier 2 AGAPIC (métadonnées et capture au choix v1/v2). Le module AGA dispose actuellement de **12 560 octets de marge théorique** ; toute augmentation doit contrôler la taille et les branchements `BSR.W`.

Références : [constructeur R83](../tools/build_aga_r83_modular.py) · [test actif](../tests/current/C2P_R83_MODULAR_01.asc) · [preuves P5 historiques](experiments/AP20_V3_MULTIUNIT_64K_P5.md).


### Chantier 2 — AGAPIC v1/v2 : compléter les fonctions natives AMOS

**R84 v0.13.29 sur `main` : PROMUE `LAST_GOOD`, Gate A native/CI PASS et Gate C AMOS Compiler PASS (banque intégrée), Gate B Runtime corrigée non documentée séparément.** La candidate active R84 propose les deux fonctions suivantes : `_VALEUR=Aga Bank Image Info(Bank,Champ)` (champs 1..5 ; v1 sans palette/ModeID = 0, erreur = -1), et `_OK=Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` (Version=1 ou 2). L’ancienne `Aga Image Capture` reste inchangée (v1). Captures opaque/masquées en 4/8 plans, RGB24 complet/ModeID et nettoyage ont passé les tests CPU. Les décisions AGAPIC v1/v2 ci-dessous demeurent le contrat à respecter ; la Gate B vérifiera les vrais ABK Save/Load, Draw/Region, palette, régression et mémoire sur WinUAE. **La R83 historique reste reconstructible octet pour octet ; `LAST_GOOD` désigne désormais R84.** [Contrat R84](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Gate A](AGAPIC_R84_GATE_A_2026-11-14.md).

**Constat R82 :** lecture, dessin v1/v2 et application explicite de la palette v2 fonctionnels sur le périmètre testé ; `Aga Image Capture` ne crée **que du v1**. L'API de métadonnées demandée n'existe pas dans R82. La capture native devra permettre de créer **au choix une banque AGAPIC v1 ou v2**, sauvegardable et rechargeable par AMOS, sans convertisseur PC obligatoire. **La création v1 reste une fonction à part entière**, et non une compatibilité limitée à la lecture.

**2A — Lecture des informations d'une banque image**

Signature demandée : `_VALEUR=Aga Bank Image Info(Bank,Champ)`, avec `Bank` = **numéro de banque AMOS DATA vivante** (pas `Start(Bank)`).

| Champ | Exemple AMOS | Résultat attendu |
|---:|---|---|
| **1** | `_W=Aga Bank Image Info(10,1)` | Largeur en pixels |
| **2** | `_H=Aga Bank Image Info(10,2)` | Hauteur en pixels |
| **3** | `_DEPTH=Aga Bank Image Info(10,3)` | Profondeur (1..8 plans) |
| **4** | `_COLORS=Aga Bank Image Info(10,4)` | Nombre de couleurs de la palette embarquée (v2 : `2^Depth`) |
| **5** | `_MODEID=Aga Bank Image Info(10,5)` | DisplayModeID enregistré (v2) |

Le lecteur doit reconnaître **v1 et v2**, ne pas dessiner, ne pas décoder les pixels et ne modifier ni la banque ni la palette écran. Pour **v1**, largeur/hauteur/profondeur sont disponibles mais **palette et ModeID sont absents du format** : valeurs de retour à formaliser, sans en inventer. À fixer dans le contrat avant codage : cas banque absente/invalide, mauvais champ, version/offsets corrompus, distinction d'erreur et valeurs valides (en particulier ModeID U32).

**2B — Capture native AGAPIC v1 ET v2 dans AMOS**

- **Choix explicite du format à créer : v1 ou v2.** Prévoir un paramètre `Version` (valeurs 1 ou 2) ou une interface équivalente dans la **nouvelle API de capture**, à valider lors du contrat technique. Ne pas imposer v2 à toutes les nouvelles captures.
- **Compatibilité de la commande existante :** `Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)` continue de créer du **v1 à l'identique**, sans changement de syntaxe ou de comportement. La future interface doit aussi pouvoir demander explicitement une création **v1**.
- **Commun aux deux versions :** capturer un rectangle valide depuis le **back buffer AGA privé `Safe`** : pixels planaires RLE, masque indépendant éventuel, dimensions et profondeur, en respectant l'encodage de chaque version.
- **Sortie v1 :** conserver strictement l'en-tête, les offsets et le flux RLE v1, **sans** palette intégrée ni DisplayModeID, afin de produire des banques lisibles par les anciennes versions de l'extension.
- **Sortie v2 :** capturer en plus la **palette RGB24 complète de `2^Depth` couleurs** à partir du `ColorMap` AGA et le **DisplayModeID réellement utilisé** par l'écran privé. Enregistrer `PaletteCount`, `PixelFormat=1`, offsets, alignements et longueur totale conformes au format v2.
- **Dans les deux cas :** créer une banque DATA AMOS AGAPIC cohérente, de longueur calculée et vérifiée, réutilisable via `Aga Bank Image Draw` / `Aga Image Region`, puis sauvegardable/rechargeable avec les mécanismes AMOS. `Aga Bank Palette Apply(Bank,0)` reste réservé à la v2. Aucun Swap, VBL ou changement de palette écran implicite.
- Gérer les refus sans laisser de banque partiellement créée ou de données existantes détruites ; contrôler géométrie, bornes, taille, allocation, RAM, masques et nettoyage.

**Compatibilité impérative :** `Aga Image Capture` v1, AGAPIC v1, AGAPAL v1 et les commandes de dessin/palette R82 doivent continuer à fonctionner. Le ModeID strict et la palette v2 restent indépendants du dessin ; les palettes ne sont pas appliquées automatiquement.

**Validation avant acceptation :** contrôles du format/ABK v1/v2 (dont corruption et aller-retour Save/Load), **capture native de la même image en v1 puis en v2**, compatibilité des banques v1 avec les anciens lecteurs, captures opaques et masquées, 4/8 plans au minimum, pixels comparés dans les deux versions, palette v2 comparée, ModeID v2 exact/refus d'incompatibilité, banques invalides, limites mémoire, fermeture et régressions R82 ; Gates A native, B WinUAE Runtime et C Compiler séparées. Gate D matériel et `PRG_STATE 0` non présumés. **R83 `LAST_GOOD` reste protégée** ; pas de promotion future sans validation et accord.

Référence de format : [contrat AGAPIC v2](M16_AGAPIC_V2_CONTRACT_2026-11-14.md) ; ce document est historique sur le plan du statut des tests, mais ses dispositions binaires v1/v2 sont la base à préserver.

## 4. Backlog — pistes non engagées

| Sujet | Périmètre à étudier |
|---|---|
| **M19 — Sprites / objets AGA et AMAL** | **Après les deux chantiers de §3** : interface, animation, synchronisation avec l'écran privé ; pas de dessin depuis une interruption. |
| **M20 — Tilemaps et scrolling** | Tuiles, carte, caméra, transparence, stratégie Fast/Chip et dirty rectangles. |
| **M21 — Dual Playfield** | Faisabilité et contrat AGA. |
| **M22 — Copper avancé** | Usages précis et limites d'accès aux registres. |
| **P2C et PNG natif AMOS** | Étudier séparément planar→chunky et éventuel chargement/sauvegarde PNG indexé. |
| **Optimisations graphiques supplémentaires** | Mesures comparables d'abord ; aucune nouvelle commande ou optimisation présumée. |

**Aucune de ces pistes n'est une tâche lancée ni une API approuvée.** L'ordre de réalisation reste à décider.

## 5. Règles de travail

- **GitHub : branche `main` uniquement.** Un seul binaire actif `dist/AMOSPro_AGA.Lib`, un seul ASC actif `tests/current/*.asc`, et R84 `LAST_GOOD` protégée. Les preuves P5 historiques ne sont pas un second circuit de travail. Aucune nouvelle branche, promotion, tag ni release sans accord explicite.
- **`LAST_GOOD` protégée** : R84 désormais promue octet pour octet ; prochaine évolution dans une nouvelle candidate puis promotion uniquement sur accord explicite.
- **CPU cible : 68020 minimum.** Contrat de chaque nouvelle fonction avant code, avec budget Compiler V2 contrôlé.
- **Validations séparées** : Gate A native, Gate B WinUAE Runtime/interprétation selon le mode réellement exécuté, Gate C Compiler, Gate D Amiga physique. Ne jamais généraliser un PASS.
- **Une seule source AMOS active** sous `tests/current/`. Aucun tag, release ou publication sans demande explicite.
