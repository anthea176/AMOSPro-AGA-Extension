# Démonstration de référence C2P — image AGA 320×256 × 256 couleurs

**Statut : programme de référence prêt pour essai sous WinUAE.** Le code est vérifié statiquement, mais son exécution AMOS/WinUAE **n'est pas encore validée**. Ne pas confondre avec le test courant `tests/current/C2P_R79_ZOOM_01.asc` dont la Gate B a été transmise.

## Fichiers utilisés

| Fichier | Rôle |
|---|---|
| [C2P_IFF_SHOWCASE.asc](C2P_IFF_SHOWCASE.asc) | Programme AMOS à importer par **Merge ASCII**, exemple intégré de C2P Open / Convert / Blit / Zoom / Close / ReOpen |
| [AGA_DEMO_320x256_256c.iff](../../iff-TEST/AGA_DEMO_320x256_256c.iff) | **Image source authentique**, 320×256, 8 bitplanes, palette RGB de 256 couleurs, ByteRun1, `CAMG=$00021000` |
| [AGA_DEMO_320x256_256c.chk](../../iff-TEST/AGA_DEMO_320x256_256c.chk) | Banque chunky **81 920 octets** décodée hors ligne depuis le BODY du même IFF |
| [EXPECTED_C2P_SHOWCASE.png](EXPECTED_C2P_SHOWCASE.png) | **Image finale attendue** (320×256×256 couleurs), créée hors ligne depuis le même IFF et les **mêmes** coordonnées Blit/Zoom ; **référence visuelle**, pas preuve WinUAE |
| [test_c2p_iff_showcase.py](../../tools/test_c2p_iff_showcase.py) | Reproduction déterministe de la conversion et de la composition, vérification des hashes, 14 pixels et paramètres AMOS |

**Ces deux fichiers image doivent être dans le même répertoire AmigaDOS :**
`AGA_DEMO_320x256_256c.iff` et `AGA_DEMO_320x256_256c.chk`. Le programme demande **une seule fois l'IFF** avec `Fsel$("**")`, puis déduit automatiquement le nom du compagnon `.chk`. Il vérifie sa taille exacte avant `Bload`. Pas de chemin Windows ou WinUAE codé en dur.

**ATTENTION :** l'exemple réalloue les **banques DATA 12 et 13** et efface leur contenu au terme du test. Le lancer dans un programme AMOS vide, sans données importantes dans ces banques.

## Installation / exécution

1. Installer `dist/AMOSPro_AGA.Lib` **R79 v0.13.24** et conserver `LIBS:c2p.library` **1.9**. WinUAE : chipset AGA, CPU **68020+**, mémoire disponible pour deux banques 80 Kio, bitmap SDK C2P et double buffering.
2. Mettre les fichiers `.iff` et `.chk` **ensemble** sur un disque/volume AmigaDOS accessible depuis WinUAE. Le contenu original IFF du dépôt est **inchangé**.
3. Importer [C2P_IFF_SHOWCASE.asc](C2P_IFF_SHOWCASE.asc) par **Merge ASCII**, dans un programme vide. Pour cette validation de référence, **lancer en interprété** (ne pas utiliser AMOS Compiler).
4. Dans la sélection de fichier, choisir précisément **AGA_DEMO_320x256_256c.iff**. L'exemple dérive automatiquement le chemin `.chk` et contrôle les premiers indices.
5. Observer trois étapes : **(1)** image IFF d'origine + sa palette, **(2)** même image produite par `Aga C2P Convert` et `Aga Swap`, **(3)** montage graphique tiré **de cette vraie image** : trois Blit, sept Zoom, agrandissements/réductions, non-entier et clipping sur les quatre bords.
6. Le programme vérifie les **14 pixels de référence**, deux appels invalides refusés, `Aga C2P Close`, double Close, refus après Close, réouverture, copie et Zoom après ReOpen, puis Convert/Swap final. **Échap** sur l'image finale déclenche la fermeture normale. `Amos To Back` est exécuté avant l'attente clavier, `Amos To Front` après la fermeture de l'écran.
7. Récupérer le journal `RAM:C2P_IFF_SHOWCASE.TXT` **avant tout reset**. Vérifier `RESULT 1`, `VERDICT PASS`, `PIXEL_CHECK_COUNT 14`, toutes les lignes `*_OK 1`, `ERR 0`, `SCREEN_CLOSE_COUNT 1`, et analyser les valeurs Chip/Fast avant/après.

## Empreintes figées pour les futurs milestones

| Référence | SHA256 |
|---|---|
| IFF d'origine (80 776 octets) | `1820df9bcd77ae111b55927981482ce90c67da06d74646f6b6d92082f00db2db` |
| Indices chunky (81 920 octets) | `3f4df7bc229d36ab5a2711913fa8798d1d11bfe82a6792a98e5be67ad470b694` |
| Composition chunky finale attendue (81 920 octets) | `57604d9abf991cc5fe17425e4247431048d4cdc3276083302bbf1359b484cd09` |

**Image de comparaison :** [EXPECTED_C2P_SHOWCASE.png](EXPECTED_C2P_SHOWCASE.png), PNG indexé **83 029 octets**, SHA256 `919b166c1c815df2fe08bb0d0d8c3fdbb6224bdd8b9c0bcb08e40ae3b8cedadb`. Les pixels et la palette RGB de cette image sont vérifiés par le test Python standard-library (aucune dépendance à Pillow dans la CI).

Le SHA de la composition est un **oracle de référence calculé sur PC**, pas une mesure de l'écran AGA réalisée sous WinUAE. Le programme AMOS vérifie **14 indices précis** sur le chunky et le retour des commandes ; l'inspection visuelle par l'auteur reste nécessaire. Le test 320×256×256 couleurs **ne remplace pas** la matrice autonome 16/32/64/128/256 couleurs de `tests/current/`.

La commande d'audit hors ligne (aucune modification des binaires AGA) est :

```sh
python -B tools/test_c2p_iff_showcase.py
```

Pour **régénérer explicitement** le compagnon chunky depuis le BODY IFF, après sauvegarde de la version de référence :

```sh
python -B tools/test_c2p_iff_showcase.py --write
```

La source IFF fait partie des ressources graphiques du projet : [ASSETS_LICENSE.md](../../ASSETS_LICENSE.md). **Le fichier chunky dérivé reste soumis aux mêmes droits que l'image d'origine ; il n'est pas placé sous licence MIT.**

## Principe

```text
IFF PAL 320×256 × 8 plans ──> Aga Iff Load / Palette Load ──> Aga Swap
              |
              +── conversion hors ligne ByteRun1/planar → .chk (81 920 indices)
                        |
                        +── Bload → banque DATA 12 (destination C2P)
                        +── Bload → banque DATA 13 (source non modifiée)
                        |
                        +── Aga C2P Open(12)
                              ├── Convert → Swap (image originale)
                              ├── Blit (3 rectangles, banque 13 → 12)
                              ├── Zoom (7 rectangles, banque 13 → 12)
                              ├── 14 pixels vérifiés + refus
                              ├── Convert → Swap (composition)
                              ├── Close → ReOpen
                              ├── Convert → Swap (composition intacte)
                              └── Close → Screen Close → Erase 13/12 → RAM log
```

**Critère de validation du milestone intégré :** preuve visuelle de l'image composée **et** journal `RAM:C2P_IFF_SHOWCASE.TXT` PASS sans Guru, avec bilan mémoire analysé. **Aucune clôture de C2P ou promotion de LAST_GOOD n'est automatique.**
