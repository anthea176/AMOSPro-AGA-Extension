# Installation d'AMOSPro AGA Extension

**Candidate actuelle R61 v0.13.6 :** [AMOSPro_AGA.Lib](dist/AMOSPro_AGA.Lib), 36 816 octets (Gate A PASS ; Gates B/C WinUAE interprété/compilé NON TESTÉES). **LAST_GOOD protégée : R60 v0.13.5**, [AMOSPro_AGA_LAST_GOOD.Lib](dist/AMOSPro_AGA_LAST_GOOD.Lib), 35 056 octets, Gates A/B/C R60 PASS. Pour R61, utiliser [l'unique ASC actif](tests/current/M18_R61_FICON_01.asc) et [sa banque FICON8](tests/current/M18_FICON8_SAMPLE_BANK10.abk), puis créer un nouvel exécutable compilé : ne pas réutiliser un ancien programme R60.


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
