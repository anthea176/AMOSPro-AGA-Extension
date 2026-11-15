# M19 P0a — Test AMOS Professional AGA Bobs multi-images (MC68020)

**Statut : bibliothèque active M19 P0a GATE A PASS uniquement.** Installer **[`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib)**, 79 660 octets, dans le slot d'extension habituel de `APSystem`. **L'ASC de campagne unique** est [`tests/current/M19_P0A_MC68020_BANK_GET.asc`](../../tests/current/M19_P0A_MC68020_BANK_GET.asc). La R88 historique est archivée sous `dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib`. Gates B/C non testées.

- Code natif **MC68020 ou 68EC020 minimum** ; tests fonctionnels en WinUAE 68030, JIT ON, PAL, chipset AGA). Aucun fallback 68000.
- SHA256 du candidat : `e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0` ; taille **79 660 octets** ; **80 commandes / 90 entrees AP20**.
- [Programme ASCII](M19_P0A_MC68020_BANK_GET.asc) ; **aucune ressource externe** `.iff`, `.abk` ou police necessaire. Le test dessine ses images par `Aga Blit Fill` et genere un ABK dans `RAM:`.
- Banque **24 exclusivement** : utiliser un programme AMOS vierge et verifier qu'elle est libre. Le programme refuse de l'ecraser si elle est deja occupee. Les essais peuvent effacer **uniquement la banque 24 creee par ce test** pour valider `Save` / `Load`.

## Utilisation

1. Sauvegarder localement le fichier `AMOSPro_AGA.Lib` du slot AMOS actuel. Copier la candidate liee ci-dessus dans le bon slot sous son nom **`AMOSPro_AGA.Lib`**, puis **redemarrer** AMOS Professional dans WinUAE (CPU 68030 / JIT ON / AGA). **Ne pas modifier `dist/AMOSPro_AGA_LAST_GOOD.Lib`.**
2. Dans un nouveau programme vide, faire **Project -> Merge ASCII** avec [le test actif `M19_P0A_MC68020_BANK_GET.asc`](../../tests/current/M19_P0A_MC68020_BANK_GET.asc), surtout pas `Load` du `.asc` comme programme tokenise.
3. Executer d'abord en interprete/Runtime. Trois rectangles sont dessines sur le *back buffer AGA*, et `Get AGA Bob` construit trois images ID 1,3,2 puis remplace l'image 2. Les tailles de banque attendues sont **552, 976, 1528, 1032 octets**. L'image est affichee 100 VBL si `Aga Swap` reussit.
4. Apres fermeture de l'ecran, le programme effectue `Save "RAM:M19_P0A_68020_BOBS.ABK",24`, `Erase 24`, `Load` puis `Aga Bob Bank 24`, et verifie la taille `1032`, la signature `AGBO` et le compte `3`. Le fichier ABK est **une sortie**, pas un prerequis.
5. Relever dans la console **`PASS ERR 0`**, **`ABK RELOADED 1`** et **`CLOSE RETURNED 1`**, puis ouvrir le journal `RAM:M19_P0A_INTERPRETED.TXT` ou `RAM:M19_P0A_RUNTIME.TXT` selon `Prg State`. Envoyer le journal et la capture si erreur.
6. Compiler **ce meme ASC** sous AMOS Compiler, lancer l'executable produit et lire `RAM:M19_P0A_COMPILED.TXT`. Un gel ou un Guru, meme avec image visible, est un **FAIL**.

## Perimetre / risques

- `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2` sont **des instructions**, pas des fonctions. Les bornes `X2,Y2` sont **inclusives**. Le test les controle via `Length`, `Peek$`, `Deek`, `Leek` et la sauvegarde/relecture AMOS.
- **Il n'existe pas encore de commande d'affichage** `Aga Bob N,X,Y,I` ni de commande native `Make AGA Bob Mask`. Ce test capture et sauvegarde les images, il **ne dessine pas de Bob**. Le dessin visible vient uniquement de `Aga Blit Fill`.
- Aucun mode `Save/Load`, tokenisation AMOS reelle ni execution WinUAE/Compiler n'a encore ete valide pour cette candidate. **GATE A MC68020 PASS (74 cas CPU sous services simules + 44 tests hote)** : [preuve GitHub Actions](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43754375272). **Gates B/C/D NON TESTEES.**
- **Ne pas promouvoir** dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`. La R88 historique demeure dans `dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib` ; cette candidate est la candidate active `dist/AMOSPro_AGA.Lib` (R88 archivée), en attente des Gates B/C.
- Cet ASC n'a passe que le **preflight statique** (`scripts/amos_preflight.py`), pas la compilation AMOS. Les fichiers `RAM:` sont temporaires (RAM Disk) et peuvent deja exister apres un essai precedent ; les supprimer avant de refaire un essai si `Save` se plaint.
