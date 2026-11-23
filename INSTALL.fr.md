# Installation d'AMOSPro AGA Extension

**Candidate de test active S1-P1e Get AGA Sprite (MC68020+) :** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib), 142 000 octets, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`, 102 commandes / 208 entrées AP20. Gate A PASS avec services Amiga simulés ; nouvelles commandes Sprite **non testées sous WinUAE Runtime ni AMOS Compiler**. **LAST_GOOD protégée M19 P2d inchangée :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](dist/AMOSPro_AGA_LAST_GOOD.Lib), 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 entrées AP20, avec ses validations B/C propres. **Aucune publication de release/tag 0.14.0.**

[English](INSTALL.md) | **Français** · [Exemples](examples/README.fr.md)

Extension **non officielle** d'AMOS Professional pour les Amiga AGA (A1200/A4000 ou WinUAE correctement configuré). AMOS Professional doit déjà être installé.

## 1. Installer l'extension

1. **Sauvegarder** ta configuration AMOS et toute ancienne bibliothèque, notamment le fichier de configuration de l'interpréteur (généralement `S:AMOSPro_Interpreter_Config`).
2. Pour les essais S1-P1e seulement, copier la **candidate non validée** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) dans **APSystem** sous le nom `AMOSPro_AGA.Lib`, **sur un WinUAE isolé**, après sauvegarde de la bibliothèque installée et de la configuration de l'interpréteur. Vérifier son SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`. La `LAST_GOOD` reste P2d et **n'est pas identique** à cette candidate. Garder le slot existant et redémarrer AMOS.
3. Démarrer **AMOS Professional**. Dans **Config → Set Interpreter**, charger la configuration actuelle, puis ouvrir **Set Loaded Extensions**.
4. Enregistrer `AMOSPro_AGA.Lib` dans le **slot d'extension 14 s'il est libre** (c'est le slot utilisé par les tests historiques du projet). Si le 14 est déjà pris, ne pas remplacer l'autre extension : choisir un slot libre en sachant que les anciens fichiers AMOS tokenisés dépendent du slot utilisé. Saisir le nom exact ou le chemin AmigaDOS complet, selon la configuration.
5. **Sauvegarder la configuration de l'interpréteur**, quitter AMOS puis le relancer. Vérifier dans **AMOS → About Loaded Extensions** que l'extension AGA apparaît.

**Mise à jour :** pour remplacer une ancienne version de `AMOSPro_AGA.Lib`, conserver le même numéro de slot et redémarrer AMOS. Sauvegarder au préalable l'ancien fichier et la configuration.

## 2. Prérequis et dépendance C2P

**Prérequis de la candidate de test S1-P1e (même CPU minimal que P2d) :** Amiga à chipset **AGA** (A1200/A4000 ou WinUAE configuré en AGA), processeur **Motorola 68020/68EC020 minimum** (pas de 68000 seul), AMOS Professional installé et suffisamment de **Chip RAM** pour l'écran AGA privé et ses buffers.

**Bibliothèque supplémentaire pour le C2P :** [**c2p.library v1.9 d'Alimede Informatica sur Aminet**](https://aminet.net/package/dev/misc/c2plib) ([sources officielles](https://github.com/alimede/c2p.library)). C'est une bibliothèque partagée AmigaOS, **pas** une extension AMOS et elle n'est **pas** intégrée à `AMOSPro_AGA.Lib`.

1. Télécharger **`c2plib.lha`** sur Aminet, puis décompresser l'archive avec un outil compatible LhA.
2. Repérer le fichier **`c2p.library`** (normalement dans le répertoire **`libs/`** du paquet). Copier **ce fichier** dans **`LIBS:c2p.library`** sur l'Amiga (habituellement **`SYS:Libs/c2p.library`**). Sous WinUAE, le fichier doit être sur un volume **visible depuis AmigaOS**, pas seulement dans Windows.
3. Conserver **`AMOSPro_AGA.Lib` dans `APSystem`** et **`c2p.library` dans `LIBS:`**. **Ne pas enregistrer** `c2p.library` dans *Set Loaded Extensions*. Relancer AMOS si la dépendance était auparavant absente.

**Périmètre :** les cinq commandes `Aga C2P` (`Open`, `Convert`, `Close`, `Blit`, `Zoom`) utilisent un contexte dépendant de cette bibliothèque. Les autres fonctions de l'extension, **dont `Aga Iff To Chunky` employée seule**, fonctionnent sans elle. En son absence, `Aga C2P Open` retourne **0**, sans empêcher le chargement de l'extension AGA.

**Conditions C2P :** écran AGA privé **320×256** en **16/32/64/128/256 couleurs indexées (4–8 plans)**, **`Aga Double Buffer`** actif et banque chunky AMOS **DATA/WORK existante** (n° **5..65535**, au moins **81 920 octets**). La banque peut être remplie depuis un ILBM compatible par `Aga Iff To Chunky(File$,Bank)`. Ordre : **Open → Blit/Zoom facultatif → Convert → `Aga Swap` explicite → Close**. Palette à charger séparément ; pas de Swap ou de modification automatique des couleurs.

## 3. Lancer les exemples

1. Copier les exemples `.asc` choisis ainsi que `demo.iff` depuis [`examples/`](examples/) dans un répertoire accessible depuis l'Amiga ou WinUAE (disque dur Amiga, dossier Windows monté, image disque).
2. Dans l'éditeur AMOS, créer un **programme vide** (**New**), puis **Project → Merge ASCII** (raccourci **Amiga + Maj + M**). Importer `examples/screen.asc`.
3. Exécuter en **mode interprété** : un motif AGA apparaît quelques secondes puis l'écran se referme et AMOS revient.
4. Pour `picture.asc`, repartir d'un programme vide puis faire **Merge ASCII**. Au sélecteur de fichiers (`Fsel$("**")`), choisir `examples/demo.iff` ; appuyer sur une touche pour fermer l'affichage.
5. Essayer ensuite `blitter.asc`, `copper.asc` et `mouse.asc`. Chaque exemple est expliqué dans [`examples/README.fr.md`](examples/README.fr.md).

**Attention :** `Merge ASCII` **ajoute** le source dans le programme actuel. Repartir d'un programme vide pour chaque exemple, sinon les codes vont se mélanger. Après import, on peut enregistrer le source dans le format AMOS natif `.AMOS`.

## 4. Dépannage

| Problème | Vérification |
|---|---|
| Commandes `Aga ...` inconnues | La bonne `.Lib` doit être dans `APSystem`, déclarée dans les extensions chargées, puis AMOS redémarré. Vérifier le slot et le nom. |
| `demo.iff` introuvable | Le chemin doit être visible **depuis AmigaOS**. Parcourir les volumes accessibles au sélecteur, pas le chemin Windows directement. |
| Ouverture de l'écran impossible | Vérifier le chipset **AGA** et la disponibilité du mode PAL 320×256 en 256 couleurs. |
| Un `.asc` ne se charge pas | Utiliser **Project → Merge ASCII**, pas `Load` qui attend un programme AMOS tokenisé. |
| `Aga C2P Open(Bank)` retourne 0 | Vérifier `LIBS:c2p.library`, CPU 68020+, écran AGA privé 320×256 à 4–8 plans, `Aga Double Buffer` réussi et banque chunky DATA/WORK d'au moins 81 920 octets. Un deuxième Open renvoie aussi 0. |
| `Aga C2P Convert` échoue ou aucune image n'apparaît | Vérifier qu'Open a réussi, que la banque existe toujours et que le back buffer est `Safe`. Après Convert, appeler explicitement `Aga Swap` et charger la palette si nécessaire. |
| `Aga Iff To Chunky` refuse l'image | Seuls les ILBM indexés 320×256, 4–8 plans, RAW/ByteRun1, sans HAM/EHB, masque ni dual playfield sont acceptés. |
| Erreur dans un exemple | Consulter le résultat. Le [tout-en-un compilé R46 C1](examples/compiler_all_in_one/) est validé sous WinUAE ; les autres exemples disposent de tests distincts. |

## Statut et droits

**Statut actuel :** S1-P1e est une **candidate de test** dans `dist/`, sans release publique. Gate A CPU/CI simulée PASS ; B Runtime WinUAE, C vrai Compiler et D matériel physique non testées. `LAST_GOOD` M19 P2d reste protégée avec ses preuves B/C propres. Aucune release GitHub, aucun tag ni publication Aminet autorisés.

**Code et exemples en ASCII :** [MIT](LICENSE). **`demo.iff` et autres graphismes :** [licence distincte](ASSETS_LICENSE.md), **pas sous MIT**. Aucun fan art tiers n'est nécessaire aux exemples.

Documentation AMOS : [Set Loaded Extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
