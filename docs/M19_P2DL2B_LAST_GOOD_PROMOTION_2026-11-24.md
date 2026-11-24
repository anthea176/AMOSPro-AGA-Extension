# M19 P2d-L2b — promotion LAST_GOOD

**24 novembre 2026 — promotion L2b autorisée par l'auteur.** « attend avant ca il faudrait promoubvoir la courrante » : promotion interne de P2d-L2b, 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. Les deux Lib de dist/ sont identiques. P2d historique (136020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, blob `8a849b89aae57c2cda0b4db8771034a0978d3e78`) reste reconstructible depuis ses sources et conservée dans Git. Gate A et Runtime documentés sur L2b ; Compiler reporté, D physique non testée. Requalification CI après promotion et disposition des risques résiduels avant publication. Aucune publication, aucun tag ni reprise Sprite automatique.

## Autorité et provenance

- Commit avant promotion : [d710c2e](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/d710c2e9e064528d7c2443491250c1d3e99405ef).
- Binaire actif non modifié : `2809b4b409eea9e234df1b96bf2b08bd393d8c85`, 100 commandes / 203 AP20, MC68020 minimum, `$VER: AMOSPro_AGA M19 P2d-L2b`.
- Promotion de LAST_GOOD par réutilisation du **même blob Git**, pas de reconstruction ou patch du fichier.
- [Master ASM direct et Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45462745139) : comparaison exacte, 184 Pattern, 172 writers, 10 suites Bob.
- [Qualification détaillée](releases/0.14.1_QUALIFICATION.md) : T06 et cycles normaux de ressources Runtime PASS ; L4 Runtime transmis, journal identique au journal historique P2d, attribution contextuelle à L2b. Les preuves C P2d ne sont pas transférées.
- CI globale encore en cours lors de la préparation. Les risques résiduels sont conservés sans PASS inventé ni acceptation implicite.

## Transition des gardes

`LAST_GOOD_SHA` devient P2DL2B_SHA ; le contrôle de livraison autorise exclusivement les quatre blobs avant/après correspondant à cette promotion. La reconstruction historique P2d repose sur son builder exact et la vérification de l'ascendance L2b, non sur le slot LAST_GOOD mobile. Les builders L1/L2/L2b, la vérification des exports historiques et les CI identifiées sont adaptés ; les tests CPU/AP20 restent actifs. Les CI après promotion doivent être vérifiées : aucun PASS global présumé.

Aucun ASC, aucune source native ASM, aucun exemple public, archive, tag ou release modifié. La reprise Sprite est suspendue pendant cette opération. Le paquet 0.14.1 reste à produire et à valider séparément.