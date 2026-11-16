# M19 P0e — Registre privé des Bobs persistants (MC68020) : Gate A

> **ACTUALISATION — pont validé en Gate A le 16/11/2026.** Le blocage « pont entre groupes manquant » documenté dans la section historique ci-dessous est **résolu pour le registre privé** : [pont source natif BOBS → AGA](../tools/m19_p0e_v2_object_bridge_emit.py), **60 tests MC68020 PASS**, [rapport détaillé](M19_P0E_V2_CROSS_UNIT_BRIDGE_GATE_A_2026-11-16.md). Il manque encore les commandes publiques, le moteur Draw et le reset automatique Close/End. La bibliothèque P0d active n'est pas remplacée.


Date : 16 novembre 2026. Dépôt **`anthea176/AMOSPro-AGA-Extension`**, **`main` exclusivement**.

## Statut précis

Le premier registre natif d'objets Bob persistants est **créé, audité et exécuté sous MC68020**. Il ne contient **aucun token public AMOS** et **aucun Blitter / rendu** : ne pas présenter `Aga Bob N,X,Y,I`, `Aga Bob Off N` ou `Aga Bob Draw` comme disponibles dans la bibliothèque courante P0d.

- **Code source** : [`tools/m19_p0e_object_table_emit.py`](../tools/m19_p0e_object_table_emit.py), **2 332 octets natifs**, `# AGA_NATIVE_MIN_CPU: MC68020`. Table statique privée de **64 objets**, cases de 24 octets (banque, image, X, Y, activité, réserve), propriétaire AMOS `A5` ; sans banque AMOS, sans allocation Chip ni duplication d'image.
- **Entrées privées** : `object_put` (créer/mettre à jour), `object_off` (désactiver), `object_read` (lecture d'un objet actif vers une sortie fournie par appelant fiable), `object_reset` (vider la table). Objet indexé de **1 à 64**, banque AMOS **5..65535**, image **1..4096**, X/Y signés 16 bits ; un objet conserve sa banque d'origine après changement de banque sélectionnée. Ordre de traitement déterministe par numéro croissant.
- **[Gate A MC68020 CPU020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43964286301)** : **316 scénarios** sur deux implantations, ABI/restauration des registres, 64 slots, création/mise à jour, Off et réactivation, bornes, propriétaire A5 différent, erreur CPU sans `AFF_68020`, aucun accès hors table. [Test natif](../tools/test_m19_p0e_object_table_native.py). Services OS et AMOS **non testés en réel** pour P0e.
- **[Builder AP20 V2 privé PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43964566218)** : [`tools/build_m19_p0e_object_table_in_memory.py`](../tools/build_m19_p0e_object_table_in_memory.py). Construit **en mémoire uniquement** une bibliothèque P0d + suffixe privé (même table de **83 commandes / 93 entrées AP20**, sans nouveau token). **93 632 octets**, SHA256 **`588345837105bdade12f8ab289b8a46f22cd1be5f9a14c8f88ca9f2220e28790`**. Suffixe natif **2 332 octets**, ajouté au **groupe AGA V2 92** à l'offset natif **56 546** ; taille groupe **58 912**, inférieure à 65 534. L'ancien groupe AGA (56 580 octets) est préservé octet pour octet en préfixe ; groupes BOBS/C2P/IFF, stubs et jetons de P0d **inchangés**. Interpréteur : **distance RBSR maximale inchangée à 32 196**, sans nouvelle rupture PC16.
- **[Politique CPU et chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43964286344)** : PASS ; pas de modification des livrables P0d ni de `LAST_GOOD`.

## Contrat fonctionnel de la phase suivante

Le futur moteur doit conserver le contrat approuvé du [design multi-image AGBO](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) :

1. `Aga Bob N,X,Y,I` crée/met à jour l'objet **N** avec la **banque sélectionnée au moment de l'appel**. Changer la banque active ensuite n'affecte pas les objets existants. Plusieurs objets peuvent partager une seule image et sa copie Chip.
2. `Aga Bob Off N` désactive l'objet, sans supprimer l'AGBO source ni provoquer de Swap. Une redéfinition avec `Aga Bob` le réactive. Prévoir un chemin de réinitialisation des objets lors du Close/End et une gestion sûre des banques effacées/rechargées.
3. `Aga Bob Draw` parcourt les objets actifs par numéro croissant et dessine via la **chaîne P0d réellement validée** : sélection de banque vérifiée, source/mask en Chip, back buffer Safe, Blitter/WaitBlit, aucune présentation implicite.
4. **Fond et double buffer** : dans la première version, le programme reconstruit le fond du back buffer **avant** de dessiner les objets puis appelle `Aga Swap` **une seule fois**. `Aga Bob Clear / Update` avec sauvegarde/restauration du fond n'est **pas encore implémenté** : ne pas promettre la disparition des anciennes empreintes sans redraw.
5. **Gates distinctes** : Gate A native et ABI sur la **candidate AP20 complète avec tokens**, puis Runtime WinUAE Gate B et Compiler réel Gate C après autorisation de bascule. Gate D physique reste indépendante.

## Blocage d'intégration à résoudre avant exposition publique

Le **registre de banque sélectionnée `bank_active_state`** et le staging Chip P0d résident dans **l'unité native BOBS**. Le registre d'objets privé P0e est ajouté à la **fin de l'unité native AGA** pour préserver les branchements interpréteur signés. **Il n'existe pas encore de pont vérifié entre ces unités** : le code P0e ne connaît pas encore, depuis le groupe AGA, la banque sélectionnée par `Aga Bob Bank N` dans BOBS, ni un pointeur de dessin P0d utilisable après relocation Compiler.

**Ne pas** : ajouter les 2 332 octets à BOBS (RBSR à seulement 570 octets de la borne de contrôle), inventer un emplacement A5/State partagé, désassembler le .Lib officiel comme source, introduire une seconde banque AMOS Chip, copier les images à chaque frame, ou appeler directement une adresse entre deux groupes V2 sans preuve de relocation.

**Voie à auditer :** le P0c source vérifié sait reconstruire l'adresse de l'original callback AGA End à partir de `A5+0x1c8` et d'un delta validé, après contrôle d'une signature d'instructions. Étudier son usage comme **ancre de relocation vérifiable** pour accéder au code privé P0e depuis BOBS, et la manière inverse de rejoindre la fonction P0d sans pointer périmé. Prévoir tests des deux chemins interprété/compilé, de Close/End, des deux banques et de l'absence de DMA après Erase/Load. Ne pas considérer cette piste comme démontrée avant essai CPU/Compiler.

## Protections

- **Bibliothèque active P0d inchangée** : `dist/AMOSPro_AGA.Lib`, **91 300 octets**, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` ; premier `Aga Bob Blit(I,X,Y)` validé en [Gates B/C WinUAE](M19_P0D_GATES_BC_2026-11-16.md).
- **ASC actif unique inchangé** : `tests/current/M19_P0D_BOB_BLIT_01.asc`. Aucun nouveau banc P0e actif, aucune tentative de Compiler/WinUAE sur le registre privé P0e.
- **`LAST_GOOD` R84 intacte** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. Pas de promotion, publication, archive ni changement de branche.

**Statut final :** P0d public Gates A/B/C PASS (preuve utilisateur Runtime/Compiler + visuel) ; P0e table privée Gate A CPU et preuve AP20 source PASS ; **P0e public B/C/D NON TESTÉS**, aucun token P0e livré.
