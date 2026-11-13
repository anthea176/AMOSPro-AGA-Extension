# AMOSPro AGA — exemples et démonstrations

[English](README.md) · [Installation](../INSTALL.fr.md) · [Bibliothèque R68 promue](../dist/AMOSPro_AGA_LAST_GOOD.Lib)

**Bibliothèque installable de référence : R68 v0.13.13, promue `LAST_GOOD`.** Le fichier de travail `dist/AMOSPro_AGA.Lib` peut être une candidate de développement non validée (actuellement R69) ; pour les exemples publics, copier `dist/AMOSPro_AGA_LAST_GOOD.Lib` dans `APSystem` sous le nom `AMOSPro_AGA.Lib`. L'extension a passé les scénarios CPU/CI, WinUAE interprété et Compiler intégré (Gates A/B/C). La Gate D sur Amiga physique reste à effectuer. Le résultat de chaque **exemple individuel** est précisé séparément : une Gate validée pour l'API ne valide pas automatiquement toutes les démonstrations.

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
