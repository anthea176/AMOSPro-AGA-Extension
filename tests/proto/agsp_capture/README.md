# S1-P1h — Prototype Runtime Get AGA Sprite (non distribué)

> **Runtime FAIL (ERR 9) le 24/11/2026. Ne pas relancer P1h.** Banque 29 AGASPRT créée (32 octets), première capture refusée. Révision P1i source-only en qualification ; voir [audit](../../../docs/M19_S1_P1I_CONTRACT_AUDIT_2026-11-24.md). Le protocole ci-dessous est conservé comme historique et futur test inchangé, pas une instruction d'installation actuelle.

> **P1g rejetée en Runtime (ERR 7).** P1h corrige le publisher et le mock Cur_Banks. Ne pas relancer P1g ; utiliser uniquement P1h livrée après Gate A native PASS. L'IFF est présente dans ce dossier.

Ces fichiers sont des **tests en développement**, exclusivement sous `tests/proto/`. Ne jamais les copier dans `examples/` tant qu'ils ne sont pas approuvés comme exemples de release.

## Préparer le test

**S1-P1h livrée dans [dist/AMOSPro_AGA.Lib](../../../dist/AMOSPro_AGA.Lib)** : 142720 octets, SHA256 `900646cc208cc99095c81c209276579a28dbcbbcbd43dd10c4e93be35d2e05eb`, [Gate A native PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45481353847). LAST_GOOD L2b intacte. L'ASC P1e est repris octet pour octet, sans transfert de preuve Runtime. Ne pas installer P1e, P1f (erreur de syntaxe), ni P1g (ERR 7). Réimporter l'ASC depuis un programme vierge après redémarrage d'AMOS.

1. L'IFF étant déjà versionnée, aucune génération nécessaire. Pour vérifier sa provenance depuis la racine du dépôt :
   `python tools/m19_s1p1e_make_fixture.py`
   Le fichier `tests/proto/agsp_capture/AGSP_CAPTURE_320X256.iff` (5 428 octets, SHA256 `b39aa201dddd878405c828687973b3b874ae5d0f8cc1f09d1617dda7ff0628b9`) est désormais versionné ; le générateur permet de contrôler sa provenance.
2. Récupérer la Lib S1-P1h dans dist/ et vérifier son SHA256 ci-dessus et installer uniquement dans WinUAE de test, après sauvegarde de la Lib et configuration AMOS. Copier l'IFF et [`GET_AGA_SPRITE.asc`](GET_AGA_SPRITE.asc) ensemble. Banque 29 libre. Conserver la LAST_GOOD L2b pour retour arrière.
3. Dans AMOS Professional, `Project → Merge ASCII` sur une source vierge et exécuter en **Runtime**. Le Compiler de la sonde AGSP précédente a été volontairement sauté, et n'est pas requis pour ce test.

La zone valide A (x13–28, y5–20) a 3 couleurs opaques + transparent ; B (x80–95) a également 3 couleurs ; la zone C (x48–63) comporte **4 couleurs opaques et doit être refusée** en S1. Le prototype sélectionne la banque 29, capture A et B, refuse C, remplace l'image 1, sauvegarde, efface, recharge, resélectionne la banque et y ajoute une troisième image.

Supprimer ou archiver les anciens journaux et ABK RAM: de cette sonde avant le test ; les noms conservent P1E car l'ASC n'a pas changé. Confirmer le SHA de la Lib S1-P1h installée avec les nouveaux journaux.

**Journal visé** : `RAM:M19_S1P1E_AGSP_RUNTIME.TXT`. Un succès doit donner `RESULT 1`, `ERR 0`, `CAPTURED 3`, `REFUSED 1`, `SAVED 1`, `RELOADED 1`, `RECAPTURED 1`. Deux banques sauvegardées pour analyse : `RAM:AGSP_S1P1E_SAVED.ABK` et `RAM:AGSP_S1P1E_FINAL.ABK`.

**Statut :** préflight et générateur IFF PASS dans la CI Sprite ; S1-P1h livrée, Gate A native PASS. Aucune exécution Runtime de la commande encore attestée. Aucun Sprite DMA ne s'affiche : seule la banque DATA AGSP est créée.
