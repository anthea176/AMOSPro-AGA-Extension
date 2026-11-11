# Tests AMOS actifs

**Test R38 : Gate A CPU/CI PASS, Gate B sous AMOS interprété/WinUAE en attente :** [`M14_R38_FONT_BANK_01.asc`](M14_R38_FONT_BANK_01.asc).

La commande approuvée est `_OK=Aga Font Bank Select(Start(10),Length(10))`. Le test charge dans la banque 10 le fichier **fourni par l'utilisateur** `AMCAF_FONT9.abk` depuis `RAM:`, sélectionne la fonte, efface la banque et vérifie `Aga Text`. **Le fichier réel n'est pas redistribué dans ce dépôt public.** Un modèle de BankFont à glyphes synthétiques originaux sert aux tests CPU.

**Gate A R38 PASS (60 groupes CPU 68000 + régressions R37/R26/R36)**. La candidate R38 v0.11.0 est maintenant dans `dist/AMOSPro_AGA.Lib`, **23 380 octets**, SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`. Exécuter ce test WinUAE et vérifier visuellement le texte issu de la banque AMCAF **après `Erase 10`**. Résultats attendus : `RESULT 1`, `CLOSE RETURNED`, retour AMOS normal. Gate B toujours non testée.

**Version de repli validée : R37 v0.10.9 `LAST_GOOD`**, 43 commandes AP20, SHA256 `bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a`. Son [test original](../passed/M14_R37_FONT_SELECT_01.asc) reste archivé. La Gate B R38, la Gate C Compiler et la Gate D Amiga réel ne sont pas testées.

**Correctif du refus `BANK 0` / `BANK2 0` :** accepte maintenant les banques DATA/WORK et les fontes proportionnelles Hwarf/Pix3M ; la copie privée pour `Aga Text` est toujours allouée en **Chip RAM** (`MEMF_CHIP`). La banque source peut se trouver en Fast, car elle est seulement lue puis copiée. En cas de nouveau refus, le test affiche les valeurs du header AMOS (`LEN`, `RAWLEN`, `FLAGS`).
