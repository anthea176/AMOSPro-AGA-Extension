# S1-P1e — Prototype Runtime Get AGA Sprite (non distribué)

Ces fichiers sont des **tests en développement**, exclusivement sous `tests/proto/`. Ne jamais les copier dans `examples/` tant qu'ils ne sont pas approuvés comme exemples de release.

## Préparer le test

**Attention : la Lib installée M19 P2d ne reconnaît pas `Aga Sprite Bank` ni `Get AGA Sprite`.** Le programme ci-dessous ne peut être fusionné sous AMOS qu'avec une **candidate de test S1-P1e** incorporant ces deux tokens. La CI native ne remplace ni une candidate installable ni un essai WinUAE.

1. Sur Windows, à la racine du dépôt, générer l'IFF déterministe :
   `python tools/m19_s1p1e_make_fixture.py`
   Le fichier `tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff` (5 428 octets, SHA256 `b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9`) est produit localement, volontairement sans binaire versionné inutile.
2. Depuis l'[exécution CI S1-P1e](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s1-p1c-amos-bank-commit.yml), récupérer l'artefact **`AGSP-S1-P1e-UNTESTED-WinUAE-Candidate`** (bouton *Artifacts*). Il contient la candidate `AMOSPro_AGA.Lib`, l'IFF et ce programme ASC. Cette Lib est **non testée sous WinUAE** : l'installer **uniquement dans un environnement WinUAE isolé**, après sauvegarde de la Lib actuelle. Elle n'est pas une release et n'a jamais été placée dans `dist/`. Copier `AGSP_CAPTURE_320X256.iff` et [`GET_AGA_SPRITE.asc`](GET_AGA_SPRITE.asc) dans le même répertoire AMOS. Vérifier que la **banque 29 est libre** ; le test l'effacera uniquement s'il l'a créée.
3. Dans AMOS Professional, `Project → Merge ASCII` sur une source vierge et exécuter en **Runtime**. Le Compiler de la sonde AGSP précédente a été volontairement sauté, et n'est pas requis pour ce test.

La zone valide A (x13–28, y5–20) a 3 couleurs opaques + transparent ; B (x80–95) a également 3 couleurs ; la zone C (x48–63) comporte **4 couleurs opaques et doit être refusée** en S1. Le prototype sélectionne la banque 29, capture A et B, refuse C, remplace l'image 1, sauvegarde, efface, recharge, resélectionne la banque et y ajoute une troisième image.

**Journal visé** : `RAM:M19_S1P1E_AGSP_RUNTIME.TXT`. Un succès doit donner `RESULT 1`, `ERR 0`, `CAPTURED 3`, `REFUSED 1`, `SAVED 1`, `RELOADED 1`, `RECAPTURED 1`. Deux banques sauvegardées pour analyse : `RAM:AGSP_S1P1E_SAVED.ABK` et `RAM:AGSP_S1P1E_FINAL.ABK`.

**Statut actuel : préflight et générateur IFF PASS en CI, candidate Lib de test livrée uniquement en artefact GH Actions**, pas encore d'exécution AMOS Runtime de la commande. Aucun Sprite DMA ne s'affiche : seule la banque DATA AGSP est créée.
