# Test AMOS actif — M16/R53 : AGAPIC Image Capture

**Seul test actif :** [`M16_R53_IMAGE_CAPTURE_01.asc`](M16_R53_IMAGE_CAPTURE_01.asc), correspondant exactement à la candidate **R53 v0.12.8** dans [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), également archivée sous [R53 link fix](../../dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib).

**Gate A : en revalidation CI. Gate B interprété : non testé. Gate C Compiler : non testé.** Il s'agit d'une vraie capture en banque DATA native AMOS, pas d'une sonde factice. Le correctif remplace les mauvais indices `Rjsr` par ceux des vrais services de banques AMOS : 797/800/816/819. Consulter [la preuve de liaison](../../docs/M16_MAIN_LINKAGE_FIX.md).

Dans une configuration WinUAE **de test**, installer `dist/AMOSPro_AGA.Lib` sous son nom exact dans le slot APSystem habituel, puis **redémarrer complètement AMOS**. Vérifier avec `List Bank` que les banques **11 et 12 sont libres**. Importer le programme par **Project → Merge ASCII** dans un programme vide, lancer **en interprété d'abord**. Le test initialise un écran AGA, capture avec et sans transparence, vérifie refus/absence de destruction, sauvegarde et recharge une banque, dessine les images, et ferme l'écran.

**Résultat attendu :** `CAP 11 12 1 1`, `NOSCREEN 0`, `FLAGS 0 1`, `COLL 0 PRES 1`, `INVALID` tous à 0, `DRAW O/M/RELOAD 1 1 1 RL 1`, `RESULT 1`, `CLOSE RETURNED` et un rendu visuellement correct. En cas de plantage, relever le dernier message affiché ; ne pas compiler. Après Gate B PASS confirmé par l'utilisateur, compiler **un nouvel exécutable** et effectuer Gate C séparément.

**Ne pas promouvoir R53 automatiquement.** [R46 C1 `LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) reste la bibliothèque de référence validée ; les candidats précédents restent archivés.
