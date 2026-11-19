# M19 B8 — Aga Bob Clear / Update : modèle de référence (19 novembre 2026)

## État réel

**Développement en cours, SOURCE-ONLY.** Aucun token `Aga Bob Clear` ou `Aga Bob Update` n'est installé dans `dist/AMOSPro_AGA.Lib`. La bibliothèque active **B7-m2 reste 102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`. Son scénario Bob Lifecycle dispose de Gates A/B/C PASS ; aucun résultat n'est transféré aux nouvelles fonctions.

Le modèle exécutable `tools/m19_bob_clear_update_model.py` et son test `tools/test_m19_bob_clear_update_model.py` servent d'**oracle de comportement**, pas de code CPU 68020 ni de bibliothèque AP20.

## Contrat fonctionnel retenu pour le prototype

- **`Aga Bob Clear` (nom et fonction numérique 1/0 proposés, non exportés)** : restaurer le fond du **back buffer physique courant**, tel qu'il a été sauvegardé avant la dernière étape de dessin sur cette page. Le front affiché et l'autre page ne doivent pas changer. `Clear` ne fait pas de Swap et ne désactive pas les Bobs.
- **`Aga Bob Update` (fonction numérique 1/0 proposée, non exportée)** : prévalider toutes les images actives et leurs générations de banque, restaurer la page arrière si elle contient les Bobs d'une frame précédente, capturer son fond puis dessiner **1 à 64 Bobs** dans l'ordre des IDs. Un programme ayant déjà appelé `Clear` peut dessiner son nouveau décor avant `Update` ; cette mise à jour ne doit pas effacer ce nouveau décor.
- **Aucun `Aga Swap` implicite.** Un `Update` réussi place la frame en `READY` ; seul l'appel `Aga Swap` du programme la présente. Tout `Update` échoué place la frame en `DIRTY` et interdit le Swap.
- **Récupération après échec** : un `Clear` peut lever `DIRTY` seulement si une sauvegarde complète/valide de cette même page existe et a été restaurée. En l'absence de sauvegarde, la fermeture de l'écran est nécessaire. **C'est un changement proposé au garde B5**, non implémenté dans B7-m2.
- Les banques AGBO de B7-m2 et les masques transparents indépendants sont conservés. Les pixels index 0 restent opaques en l'absence de masque ; coordonnées négatives et clipping sont supportés. Les anciennes références de banque ne sont jamais dessinées après remplacement ou `Erase`.

## Algorithme de départ : fond sauvegardé indépendamment sur les deux pages

Chaque page physique dispose d'un snapshot propre. Pour la première implémentation de référence, on copie **tout le fond** avant de dessiner. Après un Swap, la page affichée devient frontale ; lorsqu'elle redevient inactive, `Clear` restaure son snapshot. Cette solution évite les Bobs fantômes et les erreurs de superposition (l'ordre de rendu des 64 Bobs est stable).

Coût théorique par page planaire non compressée : `2 × ceil(largeur / 16) × hauteur × profondeur` octets. À **320×256×8**, c'est **81 920 octets par page**, soit **163 840 octets pour les deux snapshots**, hors métadonnées, AGBO, buffers AGA et alignement. Le modèle compte ce coût, sans réaliser d'allocation Amiga. **Les performances CPU020 et les ressources Chip/Fast n'ont pas été mesurées.** Avant de connecter le code natif, vérifier si une restauration par rectangles sauvegardés, plus économe, doit remplacer le snapshot plein écran.

## Résultats du modèle

Exécuter `python -B tools/test_m19_bob_clear_update_model.py`. Les **14 tests fonctionnels** vérifient : double buffering sans Swap caché, `Clear` par page et idempotence, Off/réactivation et déplacements, fond dynamique entre Clear et Update, chevauchements, masques, index 0, clipping, 64 objets, **405 frames réparties en neuf étapes**, dimensionnement planar, perte/recréation de banque, faute en milieu de dessin, budget insuffisant avant premier pixel et Close → Open.

Ces tests sont réalisés sur **matrices de pixels Python** ; ils **ne valident pas** `graphics.library`, les signaux `Safe`/`Disp`, le vrai bitmap AGA, le DMA, le Blitter, l'ABI AMOS/AP20, le CPU MC68020, WinUAE ou AMOS Compiler.

## Conditions bloquantes pour l'implémentation native B8

1. Identifier dans les sources B7-m2 les **deux BitMap physiques** de l'écran privé, leurs plans réels, le propriétaire A5 et les transitions `Safe`/`Disp` ; refuser sans toucher à la mémoire toute page non-Safe.
2. Définir l'allocation, la durée de vie, le mapping et la libération des **snapshots par écran et par page**, avec vérification de la plage entière via l'API Exec. Ne jamais utiliser un pointeur Fast comme source DMA.
3. Prévalider les 64 images/masques et la génération des banques **avant** premier DMA. Conserver l'état `DIRTY` si la restauration échoue, refuser `Swap`, vérifier le callback `End` et Close sans double libération.
4. Étudier le budget et le coût mémoire, puis produire un émetteur **MC68020** append-only, builder AP20 source-pinné, tests CPU/ABI et préflight. Les noms et signatures de tokens doivent être réellement validés dans AMOS + Compiler.
5. **Gate A native, puis autorisation distincte de bascule de Lib**, puis Gates B Runtime et C Compiler sur l'ASC exact. Aucun changement de `LAST_GOOD` ni de l'ASC actuellement validé dans cette étape.

**Statut : modèle de référence implémenté et testé ; API native Clear/Update NON implémentée.**
