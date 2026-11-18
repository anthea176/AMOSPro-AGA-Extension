# M19 — suite du moteur Bob après la démonstration publique (18/11/2026)

## Décision de travail

Le développement ne doit **plus être piloté par des benchmarks A/B/C**. Le dernier test à décor texturé est **Gate B Runtime PASS** : 720/720 frames, `ERR 0`, sans défaut graphique signalé par l'auteur. Le gain mesuré de restauration locale a été documenté dans [le rapport](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md) ; il ne faut plus rallonger la campagne de mesures.

L'exemple public [BOB_LOCAL_RESTORE.asc](../examples/bob_local_restore/BOB_LOCAL_RESTORE.asc) démontre le **parcours déjà fonctionnel** : titre AGA, 4 Bobs multi-banques, deux back buffers, restauration des anciennes zones et sortie propre. C'est un **nouveau source adapté**, seulement PREFLIGHT PASS tant que son propre test WinUAE n'a pas été exécuté ; les résultats de son prédécesseur ne sont pas transférés automatiquement.

**Référence figée pour la suite :** `dist/AMOSPro_AGA.Lib`, **M19 P0j-b7-m1**, 102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, 86 commandes / 181 entrées AP20, quatre unités natives, cible **MC68020+** ; R84 `LAST_GOOD` protégée. B7-m1 possède déjà `Aga Bob Bank`, `Aga Bob _N,_X,_Y,_I`, `Aga Bob Off _N`, `_OK=Aga Bob Draw` et `_OK=Aga Swap`. [Contrats d'API](../README.fr.md) · [source des 64 Bobs](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md).

## Prochain jalon : cycle de vie des Bobs persistants

L'objectif est de **qualifier les fonctions existantes**, sans créer prématurément une nouvelle commande ou modifier le format AGBO :

1. **Activation/Off/réactivation :** Bob 1 actif → `Aga Bob Off 1` → Draw/Swap sans Bob 1 → réactivation sous le même ID, banque d'origine vérifiée ; pas de Bob fantôme sur la page visible.
2. **Banques mixtes :** 1, 4, 8, 16 puis 64 Bobs issus de plusieurs banques, avec IDs stables, ordre croissant de rendu, masques et transparence cohérents. Les **scénarios 8/16/64** restent à tester sur cette Lib (les anciens modèles sources ne valent pas preuve B7-m1 en Runtime).
3. **Échecs sûrs :** image absente, masque invalide, remplacement de banque, mutation tardive, Safe/Disp en attente : pas de Swap après Draw refusé, pas de présentation d'un back buffer partiel. Reconstruction du fond et récupération sûres avant nouvelle présentation.
4. **Fermeture/relance :** Close/End, libérations au plus une fois, changement d'écran et second lancement sans `Erase All`. Vérifier séparément les paths Runtime, puis seulement après autorisation le vrai Compiler.

## Exécution proposée

- **Étape source-only d'abord :** auditer les émetteurs `tools/m19_p0j_*.py` et étendre les tests MC68020 sur les comportements Off/relance, identités AGBO et gardes Swap/End. Aucun changement de Lib sans un nouveau Gate A exact et autorisation de bascule.
- **Ensuite un seul test fonctionnel** sous `tests/current/`, avec journaux d'état et de fermeture, **sans mesures FPS**. Remplacer le dernier benchmark actif seulement lorsque le nouveau test est effectivement préparé et statiquement vérifié.
- **Gates distinctes :** A native / simulation ; B Runtime WinUAE (nouveau test) ; C vrai AMOS Compiler uniquement après décision spécifique ; D matériel physique. Aucune promotion de `LAST_GOOD` implicite.

**Statut au 18/11/2026 :** plan technique préparé et ancré dans les contrats vérifiés. **Pas de correction native supplémentaire, pas de nouvelle Lib, pas de nouvelle Gate A/B/C pour ce prochain jalon.** Branche `main` exclusivement.
