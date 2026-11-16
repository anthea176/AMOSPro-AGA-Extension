# Test actif — M19 P0d / premier Bob AGA au Blitter

**Bascule P0c → P0d explicitement autorisée le 16/11/2026.**

**Bibliothèque installable unique :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **91 300 octets**, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` ; **83 commandes / 93 entrées AP20**, MC68020/68EC020 minimum.

**Seul programme ASC actif :** [`M19_P0D_BOB_BLIT_01.asc`](M19_P0D_BOB_BLIT_01.asc), dérivé du [brouillon P0d](../design/M19_P0D_BOB_BLIT_01_UNVALIDATED.asc) avec **commentaires d'en-tête seuls changés**.

**Validation :** Gate A native Unicorn MC68020 **PASS** (108 scénarios publics, AP20/ABI et pixels contrôlés avec services Exec/Intuition/graphics simulés) ; préflight statique ASC **PASS** ; **Gate B Runtime WinUAE NON TESTÉE ; Gate C vrai AMOS Compiler NON TESTÉE ; Gate D physique NON TESTÉE.** [Rapport P0d](../../docs/M19_P0D_PUBLIC_BOB_BLIT_GATE_A_2026-11-16.md). Les Gates B/C P0c historiques restent valides **pour leur ancien binaire et ancien test uniquement**.

## Préparation WinUAE

1. Synchroniser le clone Windows sur `main`. Sauvegarder **hors dépôt** l'ancienne `AMOSPro_AGA.Lib` réellement installée dans `APSystem` ; ne pas remplacer `dist/AMOSPro_AGA_LAST_GOOD.Lib`.
2. Installer **exactement** `dist/AMOSPro_AGA.Lib` P0d dans le slot AGA existant d'AMOS Professional. Vérifier la **taille (91 300)** et le **SHA256 du fichier réellement installé**, par exemple avec PowerShell : `Get-FileHash "CHEMIN_APSystem/AMOSPro_AGA.Lib" -Algorithm SHA256`. Redémarrer AMOS.
3. Démarrer WinUAE AGA PAL avec CPU **68030/JIT ON**, RAM Chip/Fast suffisante ; relever la version d'AMOS Professional, du véritable AMOS Compiler V2, les paramètres CPU/JIT et l'empreinte de la bibliothèque installée.
4. Vérifier que la banque AMOS **24 est libre**, sinon le banc refuse volontairement sans effacer les données.
5. Dans un programme **vide**, faire **Project → Merge ASCII** sur le seul ASC actif `tests/current/M19_P0D_BOB_BLIT_01.asc`. **Ne pas utiliser `Load`** pour importer le source texte.

## Gate B — Runtime (Prg State=1)

Exécuter en **Runtime**. Le programme ouvre un écran AGA 320×256×256, active le double buffering, crée dans la banque 24 deux images planaires (17×15 et 37×8), rend l'index 0 transparent uniquement pour la première, prépare automatiquement la Chip au premier `Aga Bob Blit`, dessine quatre Bobs avec clipping, tente un ID d'image absent (retour 0) et fait **un seul `Aga Swap` explicite**.

**Contrôle visuel indispensable :** sur fond bleu foncé (index 1), vérifier un petit Bob rouge/orange avec transparence interne à (103,72), un Bob jaune opaque à (180,110), un Bob rouge partiellement rogné à gauche (X=-5,Y=170) et un Bob jaune tronqué au bord droit (X=315,Y=200). Pas d'écran vide/noir, de pixel parasite, de Guru, de freeze ni de Swap implicite. Le programme doit fermer l'écran, revenir à AMOS et effacer seulement sa propre banque 24.

Journal attendu `RAM:M19_P0D_RUNTIME.TXT` : `TEST M19_P0D_BOB_BLIT_01`, `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `IMAGE_COUNT 2`, `BANK_LENGTH 1036`, `MASK_FLAG 1`, `BLIT1 1`, `BLIT2 1`, `CLIP_LEFT 1`, `CLIP_RIGHT 1`, `MISSING_IMAGE 0`, `SWAP 1`, `CLOSE 1`. Vérifier aussi sur l'écran `LOG ... OPEN 0 CLOSE 0`. **Un PASS dans le TXT ne suffit pas à valider le rendu visible.**

## Gate C — réel AMOS Compiler (Prg State=-1)

Depuis **le même ASC actif et la même bibliothèque P0d réellement installée**, compiler un **nouvel exécutable** avec le vrai AMOS Compiler V2. L'exécuter sous WinUAE, constater les mêmes quatre Bobs, les mêmes couleurs/masques/clipping, fermeture correcte et aucun Guru/freeze. Conserver **séparément** `RAM:M19_P0D_COMPILED.TXT`, les captures, les options Compiler, la version et le retour effectif à AMOS. Journal attendu identique, sauf `RUN_MODE COMPILED` et `PRG_STATE -1`.

Si `Prg State` vaut 0, il s'agit du mode interprété strict et **pas** de la Gate B. Ne jamais déclarer B/C PASS sans les exécutables/journaux et l'observation.

## Protections

- `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 **inchangée** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. **Aucune promotion ni publication**.
- L'ancien ASC P0c est conservé via l'historique Git du commit précédent et son design `tests/design/` demeure intact ; il n'y a **qu'un seul ASC actif**.
- La candidate P0d contient uniquement le **dessin immédiat** `Aga Bob Blit(I,X,Y)` : le futur objet persistant `Aga Bob N,X,Y,I` n'est pas encore implémenté. Aucune validation physique Gate D.
