# Installation d'AMOSPro AGA Extension

**Candidate R63 v0.13.8 (Gate A PASS, Gate B WinUAE en attente, C Compiler manuelle à la fin de M18) :** [seule AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib), 38 736 octets, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. **R60 LAST_GOOD** reste [distincte et protégée](dist/AMOSPro_AGA_LAST_GOOD.Lib). Charger l'[ASC R63 actif](tests/current/M18_R63_CHIP_BLIT_01.asc), [FICON8 banque 10](tests/current/M18_FICON8_SAMPLE_BANK10.abk) et [FICHIP8 banque 11](tests/current/M18_FICHIP8_SAMPLE_BANK11.abk). **Load écrase les deux banques.** Après chargement de la banque 11, exécuter **`Bank Permanent 11` puis `Bank To Chip 11` (AMCAF)** avant tout `Aga F Blit` : une préférence Chip du fichier ABK ne prouve pas l'emplacement effectif. Les commandes sont intégrées à l'ASC actif. Tests de développement en interprété ; un seul nouvel exécutable compilé à la clôture de M18.


[English](INSTALL.md) | **Français** · [Exemples](examples/README.fr.md)

Extension **non officielle** d'AMOS Professional pour les Amiga AGA (A1200/A4000 ou WinUAE correctement configuré). AMOS Professional doit déjà être installé.

## 1. Installer l'extension

1. **Sauvegarder** ta configuration AMOS et toute ancienne bibliothèque, notamment le fichier de configuration de l'interpréteur (généralement `S:AMOSPro_Interpreter_Config`).
2. Copier la [bibliothèque R54 validée](dist/AMOSPro_AGA.Lib) dans **APSystem** sous le nom `AMOSPro_AGA.Lib`, dans le même slot, puis **redémarrer AMOS et Compiler**. Conserver l'ancienne bibliothèque/configuration. Pour reproduire la validation, exécuter le [test archivé](tests/passed/M16_R54_BANK_NUMBER_01.asc) en interprété ; après succès, compiler un **nouvel exécutable** et le tester séparément.
3. Démarrer **AMOS Professional**. Dans **Config → Set Interpreter**, charger la configuration actuelle, puis ouvrir **Set Loaded Extensions**.
4. Enregistrer `AMOSPro_AGA.Lib` dans le **slot d'extension 14 s'il est libre** (c'est le slot utilisé par les tests historiques du projet). Si le 14 est déjà pris, ne pas remplacer l'autre extension : choisir un slot libre en sachant que les anciens fichiers AMOS tokenisés dépendent du slot utilisé. Saisir le nom exact ou le chemin AmigaDOS complet, selon la configuration.
5. **Sauvegarder la configuration de l'interpréteur**, quitter AMOS puis le relancer. Vérifier dans **AMOS → About Loaded Extensions** que l'extension AGA apparaît.

**Mise à jour :** pour remplacer une ancienne version de `AMOSPro_AGA.Lib`, conserver le même numéro de slot et redémarrer AMOS. Sauvegarder au préalable l'ancien fichier et la configuration.

## 2. Lancer les exemples

1. Copier les exemples `.asc` choisis ainsi que `demo.iff` depuis [`examples/`](examples/) dans un répertoire accessible depuis l'Amiga ou WinUAE (disque dur Amiga, dossier Windows monté, image disque).
2. Dans l'éditeur AMOS, créer un **programme vide** (**New**), puis **Project → Merge ASCII** (raccourci **Amiga + Maj + M**). Importer `examples/screen.asc`.
3. Exécuter en **mode interprété** : un motif AGA apparaît quelques secondes puis l'écran se referme et AMOS revient.
4. Pour `picture.asc`, repartir d'un programme vide puis faire **Merge ASCII**. Au sélecteur de fichiers (`Fsel$("**")`), choisir `examples/demo.iff` ; appuyer sur une touche pour fermer l'affichage.
5. Essayer ensuite `blitter.asc`, `copper.asc` et `mouse.asc`. Chaque exemple est expliqué dans [`examples/README.fr.md`](examples/README.fr.md).

**Attention :** `Merge ASCII` **ajoute** le source dans le programme actuel. Repartir d'un programme vide pour chaque exemple, sinon les codes vont se mélanger. Après import, on peut enregistrer le source dans le format AMOS natif `.AMOS`.

## 3. Dépannage

| Problème | Vérification |
|---|---|
| Commandes `Aga ...` inconnues | La bonne `.Lib` doit être dans `APSystem`, déclarée dans les extensions chargées, puis AMOS redémarré. Vérifier le slot et le nom. |
| `demo.iff` introuvable | Le chemin doit être visible **depuis AmigaOS**. Parcourir les volumes accessibles au sélecteur, pas le chemin Windows directement. |
| Ouverture de l'écran impossible | Vérifier le chipset **AGA** et la disponibilité du mode PAL 320×256 en 256 couleurs. |
| Un `.asc` ne se charge pas | Utiliser **Project → Merge ASCII**, pas `Load` qui attend un programme AMOS tokenisé. |
| Erreur dans un exemple | Consulter le résultat. Le [tout-en-un compilé R46 C1](examples/compiler_r46_all_in_one/) est validé sous WinUAE ; les autres exemples disposent de tests distincts. |

## Statut et droits

**R54 v0.12.9 — bibliothèque officielle promue, Compiler-safe (12/11/2026) :** [installable](dist/AMOSPro_AGA.Lib) = [LAST_GOOD](dist/AMOSPro_AGA_LAST_GOOD.Lib) = [archive R54 figée](dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib), SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, **32 364 octets / 53 commandes / 60 entrées AP20**. Gates A/B/C PASS sur le scénario utilisateur ; Gate D Amiga physique non testée. L'ancienne [archive Compiler-safe R46 C1](dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) reste figée pour la traçabilité et les régressions.

**Code et exemples en ASCII :** [MIT](LICENSE). **`demo.iff` et autres graphismes :** [licence distincte](ASSETS_LICENSE.md), **pas sous MIT**. Aucun fan art tiers n'est nécessaire aux exemples.

Documentation AMOS : [Set Loaded Extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
