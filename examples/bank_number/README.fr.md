# Fonctions par numéro de banque — AMOSPro AGA

[English](README.md) · [Tous les exemples](../README.fr.md) · [Installation](../../INSTALL.fr.md)

Cet exemple compare `Aga Bank Image Draw(Bank,X,Y,Mode)` et `Aga Bank Font Select(Bank)` aux anciennes fonctions graphiques prenant une adresse et une longueur. Ces commandes ont été introduites avec **R54** et figurent dans la [R68 actuellement promue `LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).

## Contenu du dossier

- [`BANK_NUMBER_HELPERS.asc`](BANK_NUMBER_HELPERS.asc) — source AMOS ASCII.
- [`AGAPIC_SAMPLE_BANK10.abk`](AGAPIC_SAMPLE_BANK10.abk) — image AGAPIC chargée en banque **10**.
- [`Hwarf1252S.abk`](Hwarf1252S.abk) et [licence de la fonte](Hwarf-12xxS.licence) — police bitmap chargée en banque **25**.

Copier **tout le dossier** sur un volume visible depuis AmigaDOS et **l'exécuter avec ce dossier comme répertoire courant**. Dans un programme AMOS vierge, utiliser **Project → Merge ASCII** pour importer `BANK_NUMBER_HELPERS.asc`. Lancer en interprété ; pour compiler, produire un **nouvel exécutable** avec la bibliothèque installée.

**Attention :** le programme utilise `Load ...,10` et `Load ...,25` et écrase les banques existantes 10 et 25. Tester dans une session jetable ou sauvegarder les banques.

## Résultats attendus et validation

Le programme vérifie `DRAW NEW O/M OLD 1 1 1`, `FONT NEW/OLD/TEXT 1 1 1 1 1`, `INVALID IMG/FONT 0 0 NOS 0`, `RESULT 1`, `CLOSE RETURNED` ainsi que le rendu des images et des textes.

**Preuve historique :** le [programme R54 original](../../tests/passed/M16_R54_BANK_NUMBER_01.asc) a passé les essais WinUAE interprété et compilé avec un nouvel exécutable. La copie publique présente ne diffère que par la référence à la ressource renommée `AGAPIC_SAMPLE_BANK10.abk` ; elle n'est donc **plus strictement identique aux octets du test archivé** et **n'a pas été réexécutée séparément** depuis ce renommage. Gate D sur Amiga physique non testée.

Code sous [MIT](../../LICENSE), fonte Hwarf sous [licence distincte](Hwarf-12xxS.licence), illustrations soumises à des [conditions séparées](../../ASSETS_LICENSE.md).
