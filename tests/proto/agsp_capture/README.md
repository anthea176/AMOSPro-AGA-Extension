# S1-P1e — Prototype Runtime Get AGA Sprite (non distribué)

Ces fichiers sont des **tests en développement**, exclusivement sous `tests/proto/`. Ne jamais les copier dans `examples/` tant qu'ils ne sont pas approuvés comme exemples de release.

## Préparer le test

**État au 24/11/2026 :** les deux Lib du dépôt sont P2d-L2b, **sans les deux commandes Sprite**. S1-P1e historique (142000 octets, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`) est conservée dans Git ; ne pas l'installer sur le socle corrigé. Le [jalon S1-P1f](../../../docs/M19_S1_P1F_L2B_REBASE_2026-11-24.md) réintègre cette capture sur L2b. Attendre Gate A et livraison explicite de la Lib S1-P1f avant le test Runtime.

1. Sur Windows, à la racine du dépôt, générer l'IFF déterministe :
   `python tools/m19_s1p1e_make_fixture.py`
   Le fichier `tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff` (5 428 octets, SHA256 `b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9`) est produit localement, volontairement sans binaire versionné inutile.
2. Une fois S1-P1f livrée dans dist/, vérifier son SHA256 annoncé dans le rapport de Gate A et installer uniquement dans WinUAE de test, après sauvegarde de la Lib et configuration AMOS. Copier l'IFF et [`GET_AGA_SPRITE.asc`](GET_AGA_SPRITE.asc) ensemble. Banque 29 libre. Conserver la LAST_GOOD L2b pour retour arrière.
3. Dans AMOS Professional, `Project → Merge ASCII` sur une source vierge et exécuter en **Runtime**. Le Compiler de la sonde AGSP précédente a été volontairement sauté, et n'est pas requis pour ce test.

La zone valide A (x13–28, y5–20) a 3 couleurs opaques + transparent ; B (x80–95) a également 3 couleurs ; la zone C (x48–63) comporte **4 couleurs opaques et doit être refusée** en S1. Le prototype sélectionne la banque 29, capture A et B, refuse C, remplace l'image 1, sauvegarde, efface, recharge, resélectionne la banque et y ajoute une troisième image.

**Journal visé** : `RAM:M19_S1P1E_AGSP_RUNTIME.TXT`. Un succès doit donner `RESULT 1`, `ERR 0`, `CAPTURED 3`, `REFUSED 1`, `SAVED 1`, `RELOADED 1`, `RECAPTURED 1`. Deux banques sauvegardées pour analyse : `RAM:AGSP_S1P1E_SAVED.ABK` et `RAM:AGSP_S1P1E_FINAL.ABK`.

**Statut :** préflight et générateur IFF PASS historiques ; S1-P1f en qualification, non livrée. Aucune exécution Runtime de la commande encore attestée. Aucun Sprite DMA ne s'affiche : seule la banque DATA AGSP est créée.
