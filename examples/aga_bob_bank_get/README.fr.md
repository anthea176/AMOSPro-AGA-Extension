# Aga Bob Bank / Get Aga Bob — ancien essai M19 P0a (MC68020)

**Exemple historique uniquement : ce fichier n'est pas le banc actif P0c.**
La bibliothèque canonique actuelle reste [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **M19 P0c**, 87 020 octets, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`. Le [seul ASC actif](../../tests/current/M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc) a ses propres Gates A/B/C ; **cet ancien exemple P0a n'a pas été réexécuté sur P0c**.

- Ancien candidat P0a : 79 660 octets, SHA256 `e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0`, Gate A historique PASS seulement pour cette version.
- [Source ASC historique inchangé](BANK_GET_MULTI.asc) : génère les pixels avec `Aga Blit Fill` et un ABK dans `RAM:`, **sans IFF/ABK externe**.
- Banque **24** : utiliser un programme vierge ; le test vérifie qu'elle est libre. Les tests de `Save/Load` détruisent uniquement la banque 24 créée par ce test.
- CPU minimum **MC68020/68EC020**, WinUAE AGA 68030/JIT ON conseillé pour un éventuel nouvel essai.

**Attention :** le champ `CANDIDATE SHA256` présent dans l'ASC est la chaîne de l'ancien test P0a ; il ne mesure pas le binaire actuellement installé. Aucun PASS P0c ne doit être inféré de cette chaîne.

## Utilisation

1. Pour un nouvel essai, utiliser seulement la bibliothèque **P0c canonique** dans `dist/AMOSPro_AGA.Lib`, après sauvegarde hors dépôt de celle installée ; redémarrer AMOS Professional (AGA 68030/JIT ON). **Ne pas modifier `LAST_GOOD` R84.** Ce scénario P0a n'est pas validé sur P0c.
2. Dans un programme vide, faire **Project -> Merge ASCII** avec [l'ASC historique `BANK_GET_MULTI.asc`](BANK_GET_MULTI.asc), sans utiliser `Load` pour un source non tokenisé.
3. Executer d'abord en interprete/Runtime. Trois rectangles sont dessines sur le *back buffer AGA*, et `Get AGA Bob` construit trois images ID 1,3,2 puis remplace l'image 2. Les tailles de banque attendues sont **552, 976, 1528, 1032 octets**. L'image est affichee 100 VBL si `Aga Swap` reussit.
4. Apres fermeture de l'ecran, le programme effectue `Save "RAM:M19_P0A_68020_BOBS.ABK",24`, `Erase 24`, `Load` puis `Aga Bob Bank 24`, et verifie la taille `1032`, la signature `AGBO` et le compte `3`. Le fichier ABK est **une sortie**, pas un prerequis.
5. Relever dans la console **`PASS ERR 0`**, **`ABK RELOADED 1`** et **`CLOSE RETURNED 1`**, puis ouvrir le journal `RAM:M19_P0A_INTERPRETED.TXT` ou `RAM:M19_P0A_RUNTIME.TXT` selon `Prg State`. Envoyer le journal et la capture si erreur.
6. Compiler **ce meme ASC** sous AMOS Compiler, lancer l'executable produit et lire `RAM:M19_P0A_COMPILED.TXT`. Un gel ou un Guru, meme avec image visible, est un **FAIL**.

## Perimetre / risques

- `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2` sont **des instructions**, pas des fonctions. Les bornes `X2,Y2` sont **inclusives**. Le test les controle via `Length`, `Peek$`, `Deek`, `Leek` et la sauvegarde/relecture AMOS.
- **Il n'existe pas encore de commande d'affichage** `Aga Bob N,X,Y,I` ni de commande native `Make AGA Bob Mask`. Ce test capture et sauvegarde les images, il **ne dessine pas de Bob**. Le dessin visible vient uniquement de `Aga Blit Fill`.
- Aucun mode `Save/Load`, tokenisation AMOS reelle ni execution WinUAE/Compiler n'a encore ete valide pour cette candidate. **GATE A MC68020 PASS (74 cas CPU sous services simules + 44 tests hote)** : [preuve GitHub Actions](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43754375272). **Gates B/C/D NON TESTEES.**
- **Ne pas promouvoir** dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`. Ce document est un **point historique P0a** ; P0c est désormais la seule bibliothèque active, sans promotion de R84.
- Cet ASC n'a passe que le **preflight statique** (`scripts/amos_preflight.py`), pas la compilation AMOS. Les fichiers `RAM:` sont temporaires (RAM Disk) et peuvent deja exister apres un essai precedent ; les supprimer avant de refaire un essai si `Save` se plaint.
