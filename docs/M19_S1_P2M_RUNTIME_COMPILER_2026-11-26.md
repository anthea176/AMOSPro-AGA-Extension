# S1-P2m — Résultats WinUAE Runtime et Compiler

26/11/2026 — Base exacte livrée par [57a1a9d](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/57a1a9d2085e5d887a1fccc5300a0de5eaeef709), Lib 149400 octets SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, ASC 6700 octets SHA256 `84d2dfddc753e2c05d8a05ff991fe8b4f3e6d36daa20110cc447add547aaa684`, ABK inchangée. Attribution par contexte des essais et SOURCE_TAG, pas d'empreinte de la Lib installée mesurée dans WinUAE.

## Journaux originaux

| Fichier | Mode | Fast intra-écran max | RESULT / ERR / CLEAN_ERR | Verdict original |
| --- | --- | ---: | --- | --- |
| [M19_P2M_RUNTIME.TXT](evidence/M19_P2M_RUNTIME.TXT) | Runtime 1 | 64 | 0 / 14 / 0 | FAIL |
| [M19_P2M_RUNTIME(1).TXT](evidence/M19_P2M_RUNTIME%281%29.TXT) | Runtime 1 | 64 | 0 / 14 / 0 | FAIL |
| [M19_P2M_RUNTIME3.TXT](evidence/M19_P2M_RUNTIME3.TXT) | Runtime 1 | 0 | 1 / 0 / 0 | PASS_FUNCTIONAL_LIFECYCLE |
| [M19_P2M_RUNTIME4.TXT](evidence/M19_P2M_RUNTIME4.TXT) | Runtime 1 | 0 | 1 / 0 / 0 | PASS_FUNCTIONAL_LIFECYCLE |
| [M19_P2M_RUNTIME5.TXT](evidence/M19_P2M_RUNTIME5.TXT) | Runtime 1 | 0 | 1 / 0 / 0 | PASS_FUNCTIONAL_LIFECYCLE |
| [M19_P2M_COMPILED1.TXT](evidence/M19_P2M_COMPILED1.TXT) | Compiler -1 | 0 | 1 / 0 / 0 | PASS_FUNCTIONAL_LIFECYCLE |
| [M19_P2M_COMPILED2.TXT](evidence/M19_P2M_COMPILED2.TXT) | Compiler -1 | 128 | 0 / 14 / 0 | FAIL |

Tous les journaux : CPU_ATTNFLAGS 32823 ; 100 affichages, 100 déplacements, 100 Off, 10 fermetures avec Sprite actif, 10 ouvertures/fermetures ; tous les retours API à 1. Chip intra-écran 0, pertes après fermeture 0, Chip/Fast avant=après sur chaque exécution. Les deux premiers Runtime sont **octet-identiques**, ne constituent pas deux preuves indépendantes. Les trois derniers Runtime sont distincts et strictement PASS ; les deux Compiler sont distincts et fonctionnels mais seulement un strictement PASS. ERR14 provient de la règle exigeant Fast_Cycle_Loss=0 ; les écarts transitoires 64/128 octets ont été récupérés au plus tard en fin de campagne ; cause exacte non établie. Les fichiers de journal conservés dans RAM: expliquent selon l'auteur les variations inter-lancements ; leur coût exact n'a pas été isolé. Le bilan avant/après est mesuré avant écriture du log. Ne pas changer les verdicts ni augmenter artificiellement une tolérance.

SHA256 des fichiers originaux :
- `M19_P2M_RUNTIME.TXT` : `5f44970ae60cd5e1541f5d0cc14fddbeb1a028ce7685befc97feb674e92b6ee1`
- `M19_P2M_RUNTIME(1).TXT` : `5f44970ae60cd5e1541f5d0cc14fddbeb1a028ce7685befc97feb674e92b6ee1`
- `M19_P2M_RUNTIME3.TXT` : `f763b89018d4b489e24be6c8fc3111223e969345ce5a64edd7fa7996c7aebe91`
- `M19_P2M_RUNTIME4.TXT` : `018b93bb0658a8c519fc504e39c95fb79acc7e6b897af8db772861560a9f54ed`
- `M19_P2M_RUNTIME5.TXT` : `c913a484d15053093c74c12bd5a88f36278be3c2f2e19a8cf09ba27b568b484a`
- `M19_P2M_COMPILED1.TXT` : `d9f002f06b30793703f2b206f361e2e04580a80d09b47cb375ad8bfdf86b0800`
- `M19_P2M_COMPILED2.TXT` : `244333f0e255f7545fb8179839eb18e774d78623841f11a9f740a2b8cf477552`

## Qualification

- A : Gate A intégrée [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891037257), reconstruction et préflight strict PASS.
- B : fonctionnelle validée sur trois relances successives strictes, pas de nouvel essai identique demandé.
- C : vrai Compiler PRG_STATE=-1, fonctionnel 2/2, strict 1/2 ; réserve Fast transitoire documentée et acceptée pour poursuivre le chantier. Ne pas afficher C strict PASS 2/2.
- D : NON TESTÉE.
- CI après livraison 57a1a9d : 13 workflows ont échoué sur le même contrôle statique `test_current_ram_log.py`, champ close, car le nouveau journal imprime OPENED/CLOSED. Les 13 traces ont été vérifiées. Le contrôle accepte désormais les deux compteurs exacts et exige la fermeture et l'incrément correspondants ; trois mutations négatives prévues. Requalification CI à relever, ne pas la déclarer PASS par anticipation.

Décision auteur : « oui passons a la suite du chantier sprite » puis « ok go ». Conserver P2m et l'ASC exacts, engager S2a. Aucune promotion LAST_GOOD, nouvelle Lib, nouveau test actif, archive installable, release ou autre branche.
