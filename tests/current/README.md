# Seul test actif — R54 v0.12.9 : fonctions par numero de banque

**Bibliotheque correspondante** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), candidate R54 0.12.9. **Gate A CPU/CI PASS ; Gates B AMOS interprete et C Compiler R54 NON TESTEES.** R53 Image Capture, elle, a passe Gates A/B/C et son test exact est [archive dans `tests/passed/`](../passed/M16_R53_IMAGE_CAPTURE_01.asc). R46 C1 reste [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).

**Un seul ASC actif :** [`M16_R54_BANK_NUMBER_01.asc`](M16_R54_BANK_NUMBER_01.asc). Les deux ABK necessaires sont fournis ici avec la licence Hwarf : `M16_AGAPIC_SAMPLE_BANK10.abk` et `Hwarf1252S.abk`.

Sous une configuration **WinUAE jetable**, placer **les deux ABK dans le meme repertoire AmigaDOS que le test**. ATTENTION : les commandes `Load` ecrasent les banques **10 et 25**. Installer la R54 au chemin habituel `APSystem/AMOSPro_AGA.Lib` dans le slot existant, **quitter et redemarrer AMOS**, puis `Project -> Merge ASCII` depuis un programme vierge. Lancer **en interprete d'abord** ; si PASS reel et aspect visuel confirme, compiler un **nouvel executable** pour Gate C.

Le test compare `Aga Bank Image Draw(10,X,Y,Mode)` a `Aga Image Draw(Start(10),Length(10),X,Y,Mode)`, et `Aga Bank Font Select(25)` a `Aga Font Bank Select(Start(25),Length(25))`. Il teste le refus des banques invalides, la police apres `Erase 25`, la fermeture et Chip Free. Attendu : **`DRAW NEW O/M OLD 1 1 1`**, **`FONT NEW/OLD/TEXT 1 1 1 1 1`**, **`INVALID IMG/FONT 0 0 NOS 0`**, **`RESULT 1`**, **`CLOSE RETURNED`**, et un rendu correct des trois images et des textes. La variation Chip Free est une indication, pas un verdict unique.

**Ne pas promouvoir R54 / LAST_GOOD avant la confirmation WinUAE et la regression complete de publication.**
