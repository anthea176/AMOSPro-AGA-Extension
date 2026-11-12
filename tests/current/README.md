# Tests AMOS — aucun ASC actif après promotion R54

**R54 v0.12.9 est maintenant `LAST_GOOD`** : Gates A CPU/CI, B WinUAE interprété et C WinUAE compilé **PASS sur le scénario testé** ; Gate D machine AGA réelle NON TESTÉE. [Bibliothèque installable](../../dist/AMOSPro_AGA.Lib) et [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) sont identiques à l'[archive R54](../../dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib).

Le programme exact confirmé par l'utilisateur est archivé sans modification dans [`tests/passed/M16_R54_BANK_NUMBER_01.asc`](../passed/M16_R54_BANK_NUMBER_01.asc) ; il a donné `RESULT 1` et `CLOSE RETURNED` en interprété, avec rendu conforme, puis PASS compilé. [R53 Image Capture](../passed/M16_R53_IMAGE_CAPTURE_01.asc) et les autres preuves historiques sont préservées.

Les ressources `M16_AGAPIC_SAMPLE_BANK10.abk`, `Hwarf1252S.abk` et la licence Hwarf sont encore ici pour rejouer le scénario archivé. Attention : le test utilise `Load` sur les banques 10 et 25 dans une configuration WinUAE jetable.

Aucun nouveau test actif. Le prochain développement n'est pas encore engagé.
