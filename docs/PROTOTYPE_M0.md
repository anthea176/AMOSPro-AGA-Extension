> **Archive M0.** L'utilisateur a confirme le bon fonctionnement dans WinUAE. Le test de compilation propre a M0 n'a pas ete confirme explicitement. La version courante M1 se trouve dans docs/PROTOTYPE_M1.md.

# Prototype M0 : AMOSPro_AGA.Lib 0.0.1

## Ce que cette version permet

Une commande de test **Aga Probe**, sans paramètre et sans effet. Objectif : vérifier la chaîne d'appel des extensions AMOS Professional 365, interpréteur puis compilateur.

**Ce n'est pas encore une extension graphique AGA.** Pas de détection AGA, pas de palette 256 couleurs, pas d'écran AGA, et pas de contrôle CPU 68020 dans ce premier binaire.

## Installation — uniquement sur une copie

1. Créer une copie d'une installation AMOS 365 fonctionnelle, sans modifier l'installation de référence.
2. Télécharger [AMOSPro_AGA.Lib](../archive/AMOSPro_AGA_M0.Lib) et la placer dans `APSystem/` de cette copie.
3. Dans WinUAE A1200 / 68020 / AGA / Kickstart 3.x, démarrer la copie d'AMOS.
4. Menu **Config → Set Interpreter → Load configuration → Set Loaded Extensions**.
5. Sur le **slot 14**, s'il est libre, saisir exactement `AMOSPro_AGA.Lib`.
6. Sauvegarder la configuration, quitter et relancer AMOS.
7. Vérifier dans **About Loaded Extensions** que l'extension est chargée.
8. Importer [AGA_PROBE.asc](../tests/AGA_PROBE.asc), lancer en interprété, puis compiler et lancer l'exécutable obtenu.

Le programme doit afficher `AGA extension : appel OK` et attendre une touche. En cas de plantage ou de refus, noter le message exact, puis retirer l'extension de la configuration de test.

**Avant toute installation**, sauvegarder les fichiers de configuration actifs (notamment celui utilisé dans `S:`). Éviter que l'AMOS de test n'écrase le fichier de configuration de l'installation principale.

Documentation configuration d'AMOS : https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/13/1302.html

## Construction / traçabilité

Le binaire expérimental est une adaptation binaire du `AMOSPro_Request.Lib` inclus dans https://github.com/marc365/AMOS-Professional-365 (source `+Request.s` explicitement *public domain*). Il reprend le même en-tête HUNK, la table d'entrée, l'initialisation APex et les préambules de routines, en remplaçant les trois fonctions Requester par des retours immédiats. Le pointeur de reset, le numéro de slot et la table de tokens ont été adaptés au slot 14 et à `Aga Probe`.

- SHA256 du prototype : `5cbb8937b377d39314fafae98eb1030b0ada4bd1b05b828eb0e87ee6cffc28c5`
- Longueur : 232 octets.
- Contrôles statiques du format HUNK, de la table des tokens et des signatures : réussis.
- Test sous WinUAE / AMOS 365 : **à faire**.

Le fichier `src/AMOSPro_AGA.s` est une base de travail séparée, **pas encore une source validée produisant ce binaire**.

## Risque connu

AMOS Professional charge la configuration depuis divers emplacements dont `S:`. Une copie du dossier AMOS n'isole pas automatiquement la configuration si WinUAE partage le même volume Workbench : utiliser un environnement WinUAE de test séparé pour éviter de modifier l'installation de production.
