# M19 — suite du moteur Bob après la démonstration publique (18/11/2026)

## Décision de travail

Le développement ne doit **plus être piloté par des benchmarks A/B/C**. Le dernier test à décor texturé est **Gate B Runtime PASS** : 720/720 frames, `ERR 0`, sans défaut graphique signalé par l'auteur. Le gain mesuré de restauration locale a été documenté dans [le rapport](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md) ; il ne faut plus rallonger la campagne de mesures.

L'exemple public [BOB_LOCAL_RESTORE.asc](../examples/bob_local_restore/BOB_LOCAL_RESTORE.asc) démontre le **parcours déjà fonctionnel** : titre AGA, 4 Bobs multi-banques, deux back buffers, restauration des anciennes zones et sortie propre. C'est un **nouveau source adapté**, seulement PREFLIGHT PASS tant que son propre test WinUAE n'a pas été exécuté ; les résultats de son prédécesseur ne sont pas transférés automatiquement.

**Référence figée pour la suite :** `dist/AMOSPro_AGA.Lib`, **M19 P0j-b7-m1**, 102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, 86 commandes / 181 entrées AP20, quatre unités natives, cible **MC68020+** ; R84 `LAST_GOOD` protégée. B7-m1 possède déjà `Aga Bob Bank`, `Aga Bob _N,_X,_Y,_I`, `Aga Bob Off _N`, `_OK=Aga Bob Draw` et `_OK=Aga Swap`. [Contrats d'API](../README.fr.md) · [source des 64 Bobs](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md).

## Gate A de reprise : PASS sur B7-m1

**CI [44404123651](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44404123651) PASS** : le [nouveau banc MC68020](../tools/test_m19_b7m1_bob_lifecycle_gate_a.py) reconstruit les **102 360 octets exacts de la Lib B7-m1**, puis exécute **194 contrôles comptabilisés** sur deux implantations native AP20. Vérifications : Off puis Draw (1 Bob, puis zéro Bob), réactivation des IDs avec source banque et masque conservés, progression **1/4/8/16/64 Bobs** sur banques 10/11, réduction 64 → 16 par Off, identité périmée ignorée pour un Bob inactif mais refusée avant DMA pour un actif, Swap DIRTY verrouillé, Close/End sans double free dans le mock. [Compte rendu et limites](M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md).

**Ce résultat valide le source natif en émulation MC68020, pas le comportement WinUAE des nouveaux cas Off/On ni un vrai Compiler.** Le jalon **Gate B fonctionnel** dispose maintenant d'un ASC Off/On dédié (préflight PASS, WinUAE en attente). La démo publique reste inchangée ; l'ancien ASC est conservé dans l'historique Git. Aucun nouvel émetteur ni changement de Lib n'a été nécessaire.

## Test fonctionnel Gate B prêt — Runtime WinUAE encore nécessaire

L'autorisation « ok go » du 18/11/2026 lance la campagne **Off/On fonctionnelle**. L'ASC actif unique est [`tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc`](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10 866 octets**, SHA256 `faed496a977a151850255f39f0ac134bd80014975b6dcd7942b27b351c05645d`. Il a PASS le préflight AMOS strict et **405 scènes pixel simulées sur deux back buffers**, mais **sa Gate B WinUAE n'est pas encore exécutée**. [Notice et verdicts attendus](../tests/current/README.md).

Neuf étapes de **45 frames** : **2→1→0→2→4→8→16→64→16**, retour propre à AMOS et journal `RAM:M19_B7M1_BOB_LIFECYCLE.TXT`. Réactivation des mêmes IDs, masques + opaques de banques 24/25, retrait de 48 IDs par Off et restauration des anciens rectangles sur la page arrière utilisée. Zéro `Timer`, zéro FPS, pas de Compiler. Les **50 commandes Off** sont comptées comme **commandes émises**, pas comme une preuve du nombre de Bobs visibles. Le dernier benchmark exact [reste accessible dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) ; la démo publique n'a pas été modifiée.

## Prochain jalon : cycle de vie des Bobs persistants

L'objectif est de **qualifier les fonctions existantes**, sans créer prématurément une nouvelle commande ou modifier le format AGBO :

1. **Activation/Off/réactivation : Gate A native PASS ; Gate B à faire.** Bob 1 actif → `Aga Bob Off 1` → Draw/Swap sans Bob 1 → réactivation sous le même ID, banque d'origine vérifiée ; pas de Bob fantôme sur la page visible.
2. **Banques mixtes : Gate A native PASS pour 1/4/8/16/64 ; Gate B à faire.** 1, 4, 8, 16 puis 64 Bobs issus de plusieurs banques, avec IDs stables, ordre croissant de rendu, masques et transparence cohérents. Les **scénarios 8/16/64** restent à tester sur cette Lib (les anciens modèles sources ne valent pas preuve B7-m1 en Runtime).
3. **Échecs sûrs : source active périmée et DIRTY Gate A PASS ; autres défauts et Gate B à faire.** image absente, masque invalide, remplacement de banque, mutation tardive, Safe/Disp en attente : pas de Swap après Draw refusé, pas de présentation d'un back buffer partiel. Reconstruction du fond et récupération sûres avant nouvelle présentation.
4. **Fermeture/End : Gate A PASS dans le mock ; relance WinUAE à faire.** Close/End, libérations au plus une fois, changement d'écran et second lancement sans `Erase All`. Vérifier séparément les paths Runtime, puis seulement après autorisation le vrai Compiler.

## Exécution proposée

- **Étape source-only d'abord :** auditer les émetteurs `tools/m19_p0j_*.py` et étendre les tests MC68020 sur les comportements Off/relance, identités AGBO et gardes Swap/End. Aucun changement de Lib sans un nouveau Gate A exact et autorisation de bascule.
- **Ensuite un seul test fonctionnel** sous `tests/current/`, avec journaux d'état et de fermeture, **sans mesures FPS**. Remplacer le dernier benchmark actif seulement lorsque le nouveau test est effectivement préparé et statiquement vérifié.
- **Gates distinctes :** A native / simulation ; B Runtime WinUAE (nouveau test) ; C vrai AMOS Compiler uniquement après décision spécifique ; D matériel physique. Aucune promotion de `LAST_GOOD` implicite.

**Statut au 18/11/2026 :** premier jalon fonctionnel **Gate A PASS**, nouvelle **Gate B Off/On non effectuée**, pas de nouvelle Lib ni Compiler. Branche `main` exclusivement.
