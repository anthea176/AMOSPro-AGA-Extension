# R54 v0.12.9 — fonctions graphiques par numéro de banque

Dossier de l'**essai R54 exact validé par l'utilisateur** en AMOS interprété puis dans un nouvel exécutable compilé sous WinUAE. [Programme original archivé](../../tests/passed/M16_R54_BANK_NUMBER_01.asc). Compare les nouvelles commandes `Aga Bank Image Draw(10,X,Y,Mode)` et `Aga Bank Font Select(25)` aux anciennes versions par adresse/longueur, dont les signatures restent inchangées.

Copier **le dossier complet** dans un volume visible depuis AmigaDOS : programme `M16_R54_BANK_NUMBER_01.asc`, ressources `M16_AGAPIC_SAMPLE_BANK10.abk`, `Hwarf1252S.abk` et licence Hwarf. Installer la [bibliothèque R54 validée](../../dist/AMOSPro_AGA.Lib) en tant que `APSystem/AMOSPro_AGA.Lib`, conserver le slot et redémarrer AMOS. Importer avec **Project → Merge ASCII** dans un programme vierge, lancer en interprété et, éventuellement, compiler un **nouvel exécutable**.

**Attention :** les commandes `Load ... ,10` et `Load ... ,25` écrasent les banques 10 et 25 déjà présentes. Tester dans une configuration WinUAE jetable ou sauvegarder ces banques.

Attendu : `DRAW NEW O/M OLD 1 1 1`, `FONT NEW/OLD/TEXT 1 1 1 1 1`, `INVALID IMG/FONT 0 0 NOS 0`, `RESULT 1`, `CLOSE RETURNED`, ainsi qu'un rendu correct des images et textes. **Gates A/B/C PASS sur ce scénario ; Gate D Amiga AGA physique non testée.** Ceci est un exemple avancé versionné, pas un tutoriel débutant.

Code sous [MIT](../../LICENSE), fonte sous [licence Hwarf distincte](Hwarf-12xxS.licence), autres illustrations sous [licence séparée](../../ASSETS_LICENSE.md).
