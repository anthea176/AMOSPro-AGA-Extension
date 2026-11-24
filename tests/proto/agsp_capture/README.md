# S1-P1g — Prototype Runtime Get AGA Sprite (non distribué)

Ces fichiers sont des **tests en développement**, exclusivement sous `tests/proto/`. Ne jamais les copier dans `examples/` tant qu'ils ne sont pas approuvés comme exemples de release.

## Préparer le test

**S1-P1g livrée dans [dist/AMOSPro_AGA.Lib](../../../dist/AMOSPro_AGA.Lib)** : 142684 octets, SHA256 `29788993d299c47d923ddce45ae2c9ae2cc3c98e510989a6975db3a3d10c6f66`, [Gate A AP20 ciblée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45470002173). LAST_GOOD L2b intacte. L'ASC P1e est repris octet pour octet, sans transfert de preuve Runtime. Ne pas installer P1e ni P1f (erreur de syntaxe). Réimporter l'ASC depuis un programme vierge après redémarrage d'AMOS.

1. Sur Windows, à la racine du dépôt, générer l'IFF déterministe :
   `python tools/m19_s1p1e_make_fixture.py`
   Le fichier `tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff` (5 428 octets, SHA256 `b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9`) est produit localement, volontairement sans binaire versionné inutile.
2. Récupérer la Lib S1-P1g dans dist/ et vérifier son SHA256 ci-dessus et installer uniquement dans WinUAE de test, après sauvegarde de la Lib et configuration AMOS. Copier l'IFF et [`GET_AGA_SPRITE.asc`](GET_AGA_SPRITE.asc) ensemble. Banque 29 libre. Conserver la LAST_GOOD L2b pour retour arrière.
3. Dans AMOS Professional, `Project → Merge ASCII` sur une source vierge et exécuter en **Runtime**. Le Compiler de la sonde AGSP précédente a été volontairement sauté, et n'est pas requis pour ce test.

La zone valide A (x13–28, y5–20) a 3 couleurs opaques + transparent ; B (x80–95) a également 3 couleurs ; la zone C (x48–63) comporte **4 couleurs opaques et doit être refusée** en S1. Le prototype sélectionne la banque 29, capture A et B, refuse C, remplace l'image 1, sauvegarde, efface, recharge, resélectionne la banque et y ajoute une troisième image.

Supprimer ou archiver les anciens journaux et ABK RAM: de cette sonde avant le test ; les noms conservent P1E car l'ASC n'a pas changé. Confirmer le SHA de la Lib S1-P1g installée avec les nouveaux journaux.

**Journal visé** : `RAM:M19_S1P1E_AGSP_RUNTIME.TXT`. Un succès doit donner `RESULT 1`, `ERR 0`, `CAPTURED 3`, `REFUSED 1`, `SAVED 1`, `RELOADED 1`, `RECAPTURED 1`. Deux banques sauvegardées pour analyse : `RAM:AGSP_S1P1E_SAVED.ABK` et `RAM:AGSP_S1P1E_FINAL.ABK`.

**Statut :** préflight et générateur IFF PASS dans la CI Sprite ; S1-P1g livrée, Gate A AP20 ciblée PASS. Aucune exécution Runtime de la commande encore attestée. Aucun Sprite DMA ne s'affiche : seule la banque DATA AGSP est créée.
