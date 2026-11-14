# Roadmap — AMOSPro AGA Extension

> **Suivi des travaux uniquement — état vérifié le 14 novembre 2026, branche `main`.**  
> Ce fichier sert à savoir **ce qui fonctionne, ce qui manque et ce qu'on envisage**. Il ne contient ni chronologie des versions, ni comptes rendus de tests, ni incidents clôturés. Les décisions nouvelles nécessitent l'accord de l'auteur.

## 1. État actuel

| Sujet | État |
|---|---|
| **Référence installable** | **R82 v0.13.27 — `LAST_GOOD`**, identique à `dist/AMOSPro_AGA.Lib` ; 64 112 octets, **74 commandes / 81 entrées AP20**. |
| **Validation R82** | **PASS** : Gate A native, WinUAE Runtime et AMOS Compiler sur le banc AGAPIC v1/v2 en CPU 68030. **Non vérifiés** : mode strictement interprété `PRG_STATE 0` et Amiga physique. |
| **Capacité Compiler V2** | Monolithe de **60 972 / 65 534 octets**, **4 562 octets disponibles**. Chaque nouvelle commande doit être mesurée avant intégration. |
| **Test AMOS actif** | `tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc` (unique ASC actif). |
| **Développement suivant** | **Aucun contrat de nouvelle commande approuvé à ce stade.** Premier besoin à trancher ci-dessous. |

Références : [binaire et API actuels](../README.fr.md) · [validation R82](AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md).

## 2. Fonctionnalités disponibles

- **Écran AGA privé** : ouverture, double buffering, dessin sur back buffer, Swap, palette et fermeture.
- **AGAPIC v1/v2** : images planaires compressées RLE en banque AMOS, masque facultatif, dessin complet et de régions. **v2** intègre une palette RGB24 et un DisplayModeID vérifié. **`Aga Image Capture` crée actuellement du v1 uniquement** ; le chargement et le dessin du v2 sont fonctionnels.
- **Palettes AGAPAL / AGAPIC v2** : commandes `Aga Bank Palette Init`, `Capture`, `Apply`, `Fade` par **numéro de banque**. La palette de l'image n'est **pas** appliquée automatiquement par le dessin.
- **C2P** : contexte, conversion chunky vers écran AGA, Blit, Zoom et chargement IFF vers chunky ; dépendance externe `LIBS:c2p.library`.
- **Fast Icons / CBlock** : fonctions existantes de capture, cache, transfert et dessin.

La présence d'une fonction dans R82 ne signifie **pas** que les 74 commandes ont chacune été testées dans toutes les configurations.

## 3. Prochaine décision — métadonnées d'une image AGAPIC

**Besoin identifié, fonction AMOS non disponible en R82.**

Pouvoir interroger une **banque AGAPIC v1 ou v2** sans décoder ni dessiner l'image :

| Information demandée | Disponibilité dans le format |
|---|---|
| Version, largeur, hauteur, profondeur, masque, codec | v1 et v2 |
| Nombre d'entrées de palette, format des pixels, DisplayModeID | v2 (absents de v1) |
| Couleurs RGB24 de la palette intégrée | v2 |

**À décider avant de coder :** signature AMOS unique, indices des champs, valeur renvoyée si champ absent ou banque invalide, vérifications des bornes et **coût réel dans les 4 562 octets restants**. Aucun nom de commande ni numéro de champ n'est encore validé. La R82 promue ne doit pas être modifiée.

## 4. Backlog — pistes non engagées

| Sujet | Périmètre à étudier |
|---|---|
| **M19 — Sprites / objets AGA et AMAL** | Interface, animation, synchronisation avec l'écran privé ; pas de dessin depuis une interruption. |
| **M20 — Tilemaps et scrolling** | Tuiles, carte, caméra, transparence, stratégie Fast/Chip et dirty rectangles. |
| **M21 — Dual Playfield** | Faisabilité et contrat AGA. |
| **M22 — Copper avancé** | Usages précis et limites d'accès aux registres. |
| **P2C et PNG natif AMOS** | Étudier séparément planar→chunky et éventuel chargement/sauvegarde PNG indexé. |
| **Optimisations graphiques supplémentaires** | Mesures comparables d'abord ; aucune nouvelle commande ou optimisation présumée. |

**Aucune de ces pistes n'est une tâche lancée ni une API approuvée.** L'ordre de réalisation reste à décider.

## 5. Règles de travail

- **`main` uniquement** : aucune nouvelle branche ni modification d'une autre branche sans demande explicite.
- **`LAST_GOOD` protégée** : pas de modification d'une version promue ; une évolution est une nouvelle candidate distincte, validée avant promotion.
- **CPU cible : 68020 minimum.** Contrat de chaque nouvelle fonction avant code, avec budget Compiler V2 contrôlé.
- **Validations séparées** : Gate A native, Gate B WinUAE Runtime/interprétation selon le mode réellement exécuté, Gate C Compiler, Gate D Amiga physique. Ne jamais généraliser un PASS.
- **Une seule source AMOS active** sous `tests/current/`. Aucun tag, release ou publication sans demande explicite.
