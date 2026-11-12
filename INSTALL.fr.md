# Installation d'AMOSPro AGA Extension

**Version candidate R40 0.11.1 : Gate A CPU/CI 68000 PASS (221 cas), Gate B WinUAE à tester.** Nouveau `Aga Plot(X,Y,Pen)`, **45 commandes AP20**. [Bibliothèque R40](dist/AMOSPro_AGA.Lib) (23 840 octets ; SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`). La [R38 validée sous WinUAE](dist/AMOSPro_AGA_LAST_GOOD.Lib) (23 380 octets ; SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`) reste dans `LAST_GOOD`. Tests R39 non engagés ; Gates C Compiler et D Amiga physique non testées.


[English](INSTALL.md) | **Français** · [Exemples](examples/README.fr.md)

Extension **non officielle** d'AMOS Professional pour les Amiga AGA (A1200/A4000 ou WinUAE correctement configuré). AMOS Professional doit déjà être installé.

## 1. Installer l'extension

1. **Sauvegarder** ta configuration AMOS et toute ancienne bibliothèque, notamment le fichier de configuration de l'interpréteur (généralement `S:AMOSPro_Interpreter_Config`).
2. Copier la [candidate R40 v0.11.1](dist/AMOSPro_AGA.Lib) (**45 commandes, Gate A CPU/CI PASS, Gate B WinUAE à tester**) dans **`APSystem`**, sous le nom exact `AMOSPro_AGA.Lib`. Conserver le même slot d'extension que la R38 et **redémarrer AMOS**. Sauvegarder l'ancienne Lib avant de la remplacer ; la [R38 `LAST_GOOD`](dist/AMOSPro_AGA_LAST_GOOD.Lib) demeure disponible pour revenir en arrière. Le nouveau [test R40](tests/current/M15_R40_PLOT_01.asc) ne nécessite aucun fichier externe.
3. Démarrer **AMOS Professional**. Dans **Config → Set Interpreter**, charger la configuration actuelle, puis ouvrir **Set Loaded Extensions**.
4. Enregistrer `AMOSPro_AGA.Lib` dans le **slot d'extension 14 s'il est libre** (c'est le slot utilisé par les tests historiques du projet). Si le 14 est déjà pris, ne pas remplacer l'autre extension : choisir un slot libre en sachant que les anciens fichiers AMOS tokenisés dépendent du slot utilisé. Saisir le nom exact ou le chemin AmigaDOS complet, selon la configuration.
5. **Sauvegarder la configuration de l'interpréteur**, quitter AMOS puis le relancer. Vérifier dans **AMOS → About Loaded Extensions** que l'extension AGA apparaît.

**Mise à jour :** pour remplacer une ancienne version de `AMOSPro_AGA.Lib`, conserver le même numéro de slot et redémarrer AMOS. Sauvegarder au préalable l'ancien fichier et la configuration.

## 2. Lancer les exemples

1. Copier les sept fichiers `.asc` ainsi que `demo.iff` depuis [`examples/`](examples/) dans un répertoire accessible depuis l'Amiga ou WinUAE (disque dur Amiga, dossier Windows monté, image disque).
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
| Erreur dans un exemple | Revenir à AMOS et consulter le message. **Ces nouveaux exemples sont contrôlés statiquement, mais n'ont pas encore été essayés sous WinUAE.** |

## Statut et droits

**Candidat R40 — Gate A PASS, Gate B non testée :** [`dist/AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) et [archive R40](dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib) strictement identiques, **23 840 octets**, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`. [Test WinUAE actif](tests/current/M15_R40_PLOT_01.asc). **Dernier `LAST_GOOD` : R38 v0.11.0**, [fichier](dist/AMOSPro_AGA_LAST_GOOD.Lib) et [archive](dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib), SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`, inchangés.

**Code et exemples en ASCII :** [MIT](LICENSE). **`demo.iff` et autres graphismes :** [licence distincte](ASSETS_LICENSE.md), **pas sous MIT**. Aucun fan art tiers n'est nécessaire aux exemples.

Documentation AMOS : [Set Loaded Extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
