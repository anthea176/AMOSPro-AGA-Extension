# AMOSPro AGA — exemples et démonstrations

[English](README.md) · [Installation](../INSTALL.fr.md) · [Bibliothèque R73 promue](../dist/AMOSPro_AGA_LAST_GOOD.Lib)

**Référence promue : R73 v0.13.18 `LAST_GOOD`** (Gates A/B/C). **Candidate courante R80 v0.13.25** : chargeur natif IFF -> chunky directement dans une banque DATA, Gate A CPU PASS, **Gate B WinUAE R80 et Gate C Compiler non testées**. L'ancien exemple IFF R79 reste compatible avec R80 mais utilise encore un compagnon `.chk` ; **le nouvel ASC R80 n'en utilise pas**. Pour l'affichage C2P : CPU 68020+ et `LIBS:c2p.library`. Gate D Amiga physique non testée.

## Lancer un exemple

1. Installer `AMOSPro_AGA.Lib` dans le bon slot d'extension du répertoire `APSystem`, puis redémarrer AMOS Professional.
2. Dans un **programme vierge**, choisir **Project → Merge ASCII** pour importer un fichier `.asc`. Ce sont des sources ASCII et non des programmes AMOS tokenisés.
3. Conserver les éventuels fichiers `.abk` et `.iff` au bon endroit et vérifier la disponibilité des banques AMOS nécessaires.
4. Pour les exemples utilisant une image, choisir [`demo.iff`](demo.iff) dans le sélecteur AmigaOS. Fermer proprement l'écran AGA avant de passer à l'exemple suivant.

## Démonstrations graphiques

| Source | Fonctionnalité | Ressources et validation |
|---|---|---|
| [`screen.asc`](screen.asc) | Ouverture/fermeture d'un écran AGA 320×256×256 | Aucune ressource |
| [`picture.asc`](picture.asc) | Informations IFF, chargement et double buffering | Choisir `demo.iff` |
| [`blitter.asc`](blitter.asc) | Blitter Fill, Clear et Copy | Choisir `demo.iff` |
| [`copper.asc`](copper.asc) | Bandes de couleurs Copper RGB4 | Aucune ressource |
| [`mouse.asc`](mouse.asc) | Position, boutons et clavier | Clic / touche |
| [`collide.asc`](collide.asc) | Collision AABB, souris et double buffer animé | `demo.iff` fournit le mode/la palette ; clic gauche pour quitter |
| [`show.asc`](show.asc) | HUD animé, texte, dessin, collision et swaps sécurisés | `demo.iff` fournit le mode/la palette ; clic/touche pour quitter |
| [`fade_to_bank.asc`](fade_to_bank.asc) | Trois bandes colorées et fondus de palette RGB24 | Écrase la banque **12** ; **fondu visible confirmé par l'utilisateur sous WinUAE interprété** |
| [`font_bank.asc`](font_bank.asc) | BankFonts AMCAF Hwarf et Pix3M | Lancer depuis `examples/` avec [`Amcaf Fonts/`](Amcaf%20Fonts/) ; écrase la banque **25** ; exemple confirmé sous WinUAE interprété |
| [`2d_cursor.asc`](2d_cursor.asc) | Plot, Draw, Box, Circle, viseur mobile et visibilité du pointeur | Aucun fichier externe ; clic droit pour afficher/masquer, clic gauche/touche pour quitter ; **confirmé sous WinUAE** |

Les démonstrations simples sont contrôlées statiquement. Seuls les scénarios expressément confirmés ci-dessus ont une preuve d'exécution WinUAE ; tous les programmes autonomes n'ont pas été validés de bout en bout.

## Exemples avancés

| Exemple | Fonctionnalités | Banques et validation |
|---|---|---|
| [**C2P — IFF direct en chunky (R80)**](../tests/current/README.md) · [ASC](../tests/current/C2P_R80_IFF_CHUNKY_01.asc) | Charge le vrai IFF dans deux banques DATA, puis C2P, trois Blit, sept Zoom, 14 pixels de référence et journal RAM, **sans fichier chunky annexe**. | **R80 Gate A CPU PASS, Gate B WinUAE à effectuer.** |
| [**C2P — IFF de référence**](c2p_iff_showcase/README.fr.md) · [ASC](c2p_iff_showcase/C2P_IFF_SHOWCASE.asc) · [PNG attendu](c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png) | Démo intégrée sur **la vraie image AGA fantasy 320×256×256c** : IFF/Palette → C2P Convert/Swap → 3 Blit et 7 Zoom (agrandissements, réductions, clipping) → Close/ReOpen ; 14 pixels et bilan RAM | **R79 ou ultérieure, dont R80** + `LIBS:c2p.library` ; image IFF et compagnon `.chk` dans `iff-TEST/` côte à côte ; **écrase banques 12 et 13** ; oracle statique PASS, **démonstration WinUAE PASS (14/14 pixels, ERR 0, deltas mémoire 0/0)** |
| [**Convertisseur IFF → ABK**](iff_to_abk/README.fr.md) · [ASC](iff_to_abk/IFF_TO_ABK.asc) | Sélection IFF avec `Fsel$`, capture AGAPIC, sauvegarde **ABK + IFF de palette**, effacement, rechargement, message **CHARGEMENT ABK**, reconstruction et `Aga Wait Key` | **Erase 11** au démarrage : écrase la banque 11 existante ; sorties `RAM:IFF_TO_ABK.abk` + `.iff`. Exemple à valider sous WinUAE |
| [**Visionneuse ABK**](iff_to_abk/README.fr.md) · [ASC](iff_to_abk/ABK_VIEWER.asc) | Sélection de l'ABK, lecture automatique de la palette `.iff` du même dossier, affichage sous écran PAL 320×256 jusqu'à `Aga Wait Key` | **Erase 11** destructif ; banque AGAPIC v1 et palette IFF compagnon obligatoires ; exemple à valider sous WinUAE |
| [**CBlock Chip Lab**](cblock_chip/README.fr.md) · [ASC](cblock_chip/CBLOCK_CHIP_LAB.asc) | Capture, dessin et restauration d'un fond planaire temporaire en Chip. **`Method` obligatoire :** `0` CPU8, `1` CPU16, `2` Blitter ; **pas d'AUTO** | Banque **11** libre, bibliothèque R68 ou ultérieure compatible ; **démo contrôlée statiquement seulement**. API R68 validée séparément sous WinUAE et Compiler |
| [**Fast Icon Lab**](fast_icons/README.fr.md) · [ASC](fast_icons/FAST_ICON_LAB.asc) | Banques `FICON8`/`FICHIP8`, staging, capture non alignée, dessin CPU/Blitter opaque et masqué | Banques **11, 12, 13** libres ; commandes disponibles depuis R67 et dans R68 ; **démo confirmée sous WinUAE interprété**, pas recompilée séparément |
| [**Fonctions par numéro de banque**](bank_number/README.fr.md) · [ASC](bank_number/BANK_NUMBER_HELPERS.asc) | Dessin AGAPIC et sélection de police par numéro de banque, comparaison avec les fonctions adresse/longueur | Écrase **10/25**, fichiers ABK inclus. Scénario original R54 passé en interprété et compilé ; copie publique adaptée au nouveau nom de ressource, non réexécutée séparément |
| [**Compiler tout-en-un**](compiler_all_in_one/README.md) · [ASC](compiler_all_in_one/COMPILER_ALL_IN_ONE.asc) | Démonstration historique R46 C1 : images, 2D, polices, curseur et nettoyage | Écrase **10/25**. Original compilé validé sous WinUAE ; ASC public renommé avec référence de ressource adaptée, **non recompilé depuis le renommage** |

**ZIP historique :** [`COMPILER_ALL_IN_ONE.zip`](COMPILER_ALL_IN_ONE.zip) reste **strictement identique en octets à l'archive validée R46 C1**, y compris les **anciens noms internes versionnés**. Seul le nom extérieur est simplifié. Pour reproduire la validation Compiler originale, extraire ce ZIP en conservant ses noms. Pour des noms publics propres, utiliser le [dossier `compiler_all_in_one/`](compiler_all_in_one/) ; sa copie adaptée nécessite un nouvel essai Compiler avant de revendiquer une validation indépendante.

## Ressources et précautions

- [`demo.iff`](demo.iff) : carte de test PAL 320×256×256 couleurs. Pour `collide.asc` et `show.asc`, elle sert surtout à établir le mode vidéo et la palette ; les formes sont dessinées par les commandes AGA.
- **Attention aux banques :** `Reserve As Data` et `Load` peuvent écraser une banque existante. Utiliser un programme vierge ou sauvegarder les banques.
- Pour `font_bank.asc`, conserver les chemins relatifs `Amcaf Fonts/Hwarf1252S.abk` et `Amcaf Fonts/Pix3M-1252L.abk`. **Aucune extension AMCAF distincte n'est nécessaire** pour afficher ces BankFonts via l'extension AGA.
- Importer les fichiers `.asc` par **Merge ASCII**, pas par le `Load` classique d'AMOS.
- Les sources originales numérotées des tests restent dans [`tests/passed/`](../tests/passed/). Changer le nom d'un fichier ABK dans un ASC public **ne constitue pas une nouvelle validation runtime**.

**Licences :** code des exemples sous [MIT](../LICENSE) ; polices sous licences [Hwarf](Amcaf%20Fonts/Hwarf-12xxS.licence) et [Pix3M](Amcaf%20Fonts/Pix3M-12xxL.licence) ; IFF et autres illustrations soumis à des [conditions distinctes](../ASSETS_LICENSE.md).
