# Test actif M18/R61 — Fast Icon A/B/C PASS, candidate non promue

**Candidat R61 0.13.6** : Gate A CPU/Unicorn PASS 226 cas ; **B AMOS interprété WinUAE PASS et C compilé WinUAE PASS** sur les captures fournies le 13/11/2026. [Rapport détaillé](../../docs/M18_R61_FICON_WINUAE_GATES_BC.md). Gate D Amiga réel non testée, R60 LAST_GOOD conservée, aucune promotion R61.

Un seul fichier AMOS actif : [M18_R61_FICON_01.asc](M18_R61_FICON_01.asc). Banque nécessaire : [M18_FICON8_SAMPLE_BANK10.abk](M18_FICON8_SAMPLE_BANK10.abk), 1 184 octets AmBk, 1 164 octets DATA, 4 icônes AGA 16×16×8. La bibliothèque R61 candidate est exclusivement [dist/AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), 36 816 octets.

**Procédure :** session WinUAE jetable avec R61 installée, banque ABK dans le dossier AMOS, programme vide puis Project → Merge ASCII. Le chargement écrase la banque 10. Exécuter en interprété puis compiler un **nouvel exécutable avec cette R61**, sans réutiliser un ancien compilé R60.

**Observé interprété et compilé :** OPEN=1, DB=1, SW0=1, SAFE=1, quatre icônes=1, SHIFT=1, CLIP=1, OUT=1, invalides=0, R60 REJECT=0, NOS=0, CLOSE=-1, SWAP=1, CHIP avant/après identique, RESULT=1. Chip Free **interprété 1 797 840 / 1 797 840** et **compilé 1 861 944 / 1 861 944**. Dessin visuellement cohérent avec quatre icônes, SHIFT et clipping. Interruption de `Wait Vbl` ligne 141 en interprété **après** `CLOSE RETURNED` : fin de boucle de maintien, non crash. Cette capture ne vaut pas comparaison exhaustive pixel-à-pixel.

Nouvelle API Aga F Icon(Bank,IconID,X,Y,Mode), 8 plans, X/Y pixel-exacts, transparence par couleur zéro, CPU Fast/Chip vers Chip. **Ce n'est pas encore le backend Blitter masqué ni le cache Chip**, et la compatibilité binaire AMOS Unity/Turbo n'est pas revendiquée.
