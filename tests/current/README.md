# Tests AMOS actifs

**Test R38 en attente de Gate A CPU/CI puis Gate B sous AMOS interprété/WinUAE :** [`M14_R38_FONT_BANK_01.asc`](M14_R38_FONT_BANK_01.asc).

La commande proposée et approuvée est `_OK=Aga Font Bank Select(Start(10),Length(10))`. Le test charge dans la banque 10 le fichier **fourni par l'utilisateur** `AMCAF_FONT9.abk` depuis `RAM:`, sélectionne la fonte, efface la banque et vérifie `Aga Text`. **Le fichier réel n'est pas redistribué dans ce dépôt public.** Un modèle de BankFont à glyphes synthétiques originaux sert aux tests CPU.

Ne lancer ce test WinUAE **qu'après Gate A PASS et publication de la candidate R38** dans `dist/AMOSPro_AGA.Lib`. Le résultat attendu est `RESULT 1` et `CLOSE RETURNED`, à confirmer visuellement.

**Version de repli validée : R37 v0.10.9 `LAST_GOOD`**, 43 commandes AP20, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`. Son [test original](../passed/M14_R37_FONT_SELECT_01.asc) reste archivé. La Gate B R38, la Gate C Compiler et la Gate D Amiga réel ne sont pas testées.
