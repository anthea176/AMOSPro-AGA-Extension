# Installation d'AMOSPro AGA Extension

**R42 v0.11.3 — candidate AMOS/WinUAE, Gate A CPU/CI PASS (360 cas), Gate B non testée :** [`AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) = [archive R42](dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib), **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`, **47 commandes AP20**. Nouvelle fonction `Aga Box(X1,Y1,X2,Y2,Pen)` : contour de rectangle, coins inversables, clipping sécurisé. [Test actif R42](tests/current/M15_R42_BOX_01.asc) sans IFF/ABK supplémentaire. **Dernier `LAST_GOOD` : R41 v0.11.2** (24 816 octets), [archive R41](dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib) inchangée. Gates C Compiler/D Amiga réel non testées.


[English](INSTALL.md) | **Français** · [Exemples](examples/README.fr.md)

Extension **non officielle** d'AMOS Professional pour les Amiga AGA (A1200/A4000 ou WinUAE correctement configuré). AMOS Professional doit déjà être installé.

## 1. Installer l'extension

1. **Sauvegarder** ta configuration AMOS et toute ancienne bibliothèque, notamment le fichier de configuration de l'interpréteur (généralement `S:AMOSPro_Interpreter_Config`).
2. Copier la [candidate R42 v0.11.3](dist/AMOSPro_AGA.Lib) dans **`APSystem`** sous le nom exact `AMOSPro_AGA.Lib`, **sans changer de slot**, puis **redémarrer AMOS**. Sauvegarder l'ancienne bibliothèque ; [`LAST_GOOD` R41](dist/AMOSPro_AGA_LAST_GOOD.Lib) reste disponible pour revenir en arrière. Importer le [test R42](tests/current/M15_R42_BOX_01.asc) via **Project → Merge ASCII** depuis un programme vide.
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

**R42 v0.11.3 — candidate AMOS/WinUAE, Gate A CPU/CI PASS (360 cas), Gate B non testée :** [`AMOSPro_AGA.Lib`](dist/AMOSPro_AGA.Lib) = [archive R42](dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib), **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`, **47 commandes AP20**. Nouvelle fonction `Aga Box(X1,Y1,X2,Y2,Pen)` : contour de rectangle, coins inversables, clipping sécurisé. [Test actif R42](tests/current/M15_R42_BOX_01.asc) sans IFF/ABK supplémentaire. **Dernier `LAST_GOOD` : R41 v0.11.2** (24 816 octets), [archive R41](dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib) inchangée. Gates C Compiler/D Amiga réel non testées.

**Code et exemples en ASCII :** [MIT](LICENSE). **`demo.iff` et autres graphismes :** [licence distincte](ASSETS_LICENSE.md), **pas sous MIT**. Aucun fan art tiers n'est nécessaire aux exemples.

Documentation AMOS : [Set Loaded Extensions](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1305.html) · [Merge ASCII](https://amospromanual.dev/04-01-the-editor.html).
