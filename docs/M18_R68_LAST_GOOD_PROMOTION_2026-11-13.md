# Promotion LAST_GOOD — R68 v0.13.13 (13/11/2026)

## Autorisation, tests et portée

L'auteur a explicitement autorisé la promotion de R68 après le scénario final compilé sous WinUAE : **RESULT 1** et **CLOSE RETURNED**, avec Fast Icon R64–R67 et CBlock R68 CPU8/CPU16/Blitter validés. [Rapport réel Gate C](M18_R68_INTEGRATED_GATE_C_COMPILER_2026-11-13.md) · [test source immuable](../tests/passed/M18_R68_COMPILER_FINAL_01.asc).

**Gates A/B/C : PASS** sur les scénarios de qualification documentés ; **Gate D physique : NON TESTÉE**. Il n'y a pas eu de seconde exécution du Compiler, de sélection automatique des méthodes, ni de publication Aminet.

## Régression complète obligatoire avant copie binaire

- HEAD main contrôlé : [564eb80cfcb599dd93a1d111eee26c5d67338827](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/564eb80cfcb599dd93a1d111eee26c5d67338827).
- [Artifact integrity + pre_release_full : SUCCESS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43486655608) sur ce SHA exact, vérifié avant promotion (48 étapes du contrôle rapide et 54 étapes du job complet).
- Tous les tests historiques, audits HUNK/AP20, reconstructions CPU et vérifications des exemples concernés ont terminé sans erreur. Ces contrôles CI ne remplacent pas les Gates B/C WinUAE réelles, fournies séparément.

## Identité du LAST_GOOD

- Source des octets : dist/AMOSPro_AGA.Lib, **R68 v0.13.13**, 51 064 octets, 64 commandes / 71 AP20.
- SHA256 attendu (installable et LAST_GOOD) : **ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed**.
- Copie Git exacte : blob SHA **1582afef850e67efd3bdfb335ff5417a69770904** pour les deux fichiers, sans construction, transformation ni modification de la candidate.
- Le SHA attendu est maintenant figé dans tools/active_library.py et tools/verify_artifacts.py ; tools/build_aga_current.py impose également l'égalité octet pour octet.
- L'ancienne R63 LAST_GOOD (38 736 octets, SHA256 fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba) est préservée dans [l'historique Git avant promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/564eb80cfcb599dd93a1d111eee26c5d67338827/dist/AMOSPro_AGA_LAST_GOOD.Lib), sans nouveau binaire expérimental.

## Vérification après commit

Le push de promotion sur main utilise le préfixe release: R68 pour relancer automatiquement les contrôles rapides et la régression complète sur le SHA de promotion exact. Conserver Gate D non testée et ne pas rouvrir Gate C sans changement fonctionnel approuvé.
