# M19 — P0 banque Bob AGA multi-images : assets de test

Ce répertoire contient **le véritable fichier ABK de test**, versionné dans GitHub (et non seulement généré par la CI).

| Fichier | Utilité |
| --- | --- |
| [M19_BOBS_HERO_BANK10.abk](M19_BOBS_HERO_BANK10.abk) | Banque AMOS DATA n°10, 3 images planaires non compressées avec 2 masques indépendants |

**Taille :** 131092 octets. **SHA-256 :** `b98aff949c0d2d28797c1a72dca66b466ffdbc2fffeb851669971b430e8a1ca6`.

**Programme associé :** [M19_BOBS_ABK_P0_LOAD_SAVE_01.asc](../../design/M19_BOBS_ABK_P0_LOAD_SAVE_01.asc).

## Installation et test dans WinUAE / AMOS

1. Copier **l'ABK de ce dossier et l'ASC de tests/design** dans le **même répertoire de travail AMOS** (WinUAE). Ne pas exécuter l'ASC sans la banque.
2. Vérifier que la banque AMOS **10 est libre** ou peut être remplacée : l'ASC utilise volontairement la banque 10.
3. Ouvrir un programme vierge dans AMOS Professional, puis **Project -> Merge ASCII** et sélectionner `M19_BOBS_ABK_P0_LOAD_SAVE_01.asc`.
4. Exécuter en interprété. Le programme vérifie l'enveloppe, le répertoire et les dimensions puis appelle `Save "RAM:M19_BOBS_P0_COPY.ABK",10`, `Erase 10`, `Load "RAM:M19_BOBS_P0_COPY.ABK",10`.
5. Relever la sortie `ABK ROUNDTRIP RESULT 1` (attendue, **pas encore observée en WinUAE**) ou l'erreur. Le banc n'emploie **aucune** des nouvelles commandes natives Bob, encore non implémentées.

Reconstruction reproductible, sans asset extérieur : depuis la racine du dépôt, `python -B tools/m19_agabob_fixture.py` génère une copie locale de l'ABK. Comparer son SHA-256 à celui indiqué ci-dessus.

**État :** 8 tests du modèle hôte exécutés localement (PASS) ; AP20 natif, Gate A, WinUAE Runtime et Compiler **non validés pour ces nouvelles commandes**. R84 LAST_GOOD et R88 active inchangées.
