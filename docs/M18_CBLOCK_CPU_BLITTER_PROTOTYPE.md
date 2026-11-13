# M18/P0 — Prototype CBlock : CPU8 / CPU16 / BLIT8

**13 novembre 2026 — stade P0 autonome, NON installé**. R67 v0.13.12 demeure l'unique candidate ; R63 LAST_GOOD protégée. Les sources de ce prototype ne changent aucun token AP20, aucune bibliothèque ni aucun ASC actif.

## Périmètre

Objectif confirmé par l'auteur : **capture/restauration de fonds AGA aussi rapide que possible, banque temporaire Chip, format planaire RAW, alignement horizontal sur 8 PIXELS** (pas 8 octets). Tester si 16 pixels apporte un gain supplémentaire ; aucune conclusion de vitesse sans mesures réelles WinUAE.

Trois méthodes internes, pour les **deux sens** back buffer → banque Chip et banque Chip → back buffer :

| Méthode | Alignement X source, X destination et largeur | Chemin |
|---|---|---|
| **CPU8** | multiples de 8 pixels | `MOVE.B (A0)+,(A1)+` par octet planaire |
| **CPU16** | multiples de 16 pixels | `MOVE.W (A0)+,(A1)+` par mot planaire |
| **BLIT8** | multiples de 8 pixels | `InitRastPort` + `BltBitMapRastPort` minterm `$C0` + `WaitBlit` |

Pas d'arrondi silencieux, pas de RLE, pas de staging Fast→Chip, pas de `Swap` ni VBL implicites. Une largeur de 24 pixels ou une origine X=8 est admissible en CPU8/BLIT8, mais **pas** en CPU16. Pour le Blitter, le décalage sur 8 pixels n'est pas un alignement mot de 16 bits : graphics.library doit assurer les masques et décalages corrects.

## Code produit

- [Modèle CPU/Blitter et oracle pixels](../tools/m18_cblock_copy_model.py) : trois implémentations indépendantes du rendu ; vérification des données Chip simulées et des frontières du rectangle.
- [Test du modèle](../tools/test_m18_cblock_copy_model.py) : **1 250 équivalences de pixels PASS en local**, 23 refus, profondeurs 1/2/4/5/8, capture/restauration, X=0/8/16/24/32.
- [Émetteur M68000](../tools/m18_cblock_copy_emit.py) : **872 octets générés localement** pour les trois chemins ; noyau indépendant du format de banque, aucun wrapper AP20.
- [Test natif Unicorn/Capstone](../tools/test_m18_cblock_copy_native.py) : évalue la véritable exécution 68000, l'ABI, les refus, les pixels et les appels graphics.library **simulés**, pas la DMA sur un Amiga.

Les deux tests sont ajoutés à la CI rapide (le test natif après installation des dépendances). Le résultat CI devra être consulté sur le **commit exact** ; les **1 250 équivalences ci-dessus sont des contrôles hôte**, pas une mesure de vitesse.

## Limites et prochaine étape

Le noyau suppose une source et une destination `BitMap` déjà **validées en Chip réelle**, de même profondeur, avec des pointeurs et plages sûrs. Il vérifie son alignement, ses rectangles, strides, nombre de plans et présence des pointeurs, mais ne valide pas à lui seul les allocations AMOS ni `TypeOfMem`, `Safe`, le double buffering ou les dimensions logiques de l'écran. C'est le rôle du **futur wrapper AP20**.

Avant tout benchmark WinUAE, il faudra créer/réutiliser une banque DATA temporaire `AGACBLK ` en Chip réelle **sans écraser les autres banques**, valider tous les plans et leur dernier octet, gérer `Safe/WaitBlit` et le retour d'erreur, puis installer une **seule candidate** accompagnée d'**un seul ASC actif dans `tests/current/`**.

### Matrice de benchmark interprété prévue

| Tailles | Géométrie | Mesures |
|---|---|---|
| 8×8, 16×16, 24×16 | X=8,16 | CPU8 vs CPU16 (si compatible) vs Blitter |
| 64×48, 128×96, 320×64 | X=0,8,16,24 | Capture et Restore séparées |
| 100 et 1000 reprises | banque déjà créée | Temps d'appel incluant Safe/WaitBlit, sans coût de création |
| première capture | allocation Chip incluse | Coût de création séparé, mémoire Chip avant/après Erase |

Effectuer les mesures sous **WinUAE 68020 et 68030 sans JIT**, en notant le mode **AMOS interprété**, les réglages et les ticks. **Ne pas proclamer un mode plus rapide sur la base de Python, Unicorn ou d'estimations**. Gate C Compiler manuelle **une seule fois à la clôture M18** ; Gate D physique non testée.