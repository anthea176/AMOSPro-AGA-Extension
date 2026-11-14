# Test actif M19 P0 : AMAL manuel + deux Bobs logiciels

**Unique ASC actif :** [M19_P0_AMAL_BOBS_01.asc](M19_P0_AMAL_BOBS_01.asc). L'ancien R84 est deja fige sans changement dans [tests/passed/AGAPIC_R84_V1_V2_01.asc](../passed/AGAPIC_R84_V1_V2_01.asc).

**Bibliotheque :** utiliser [R84 v0.13.29 LAST_GOOD](../../dist/AMOSPro_AGA.Lib) (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucune nouvelle API M19, aucun nouveau binaire, `c2p.library` non requise.

**Etat :** source P0 preparee pour essai. La syntaxe est fondee sur le [manuel AMAL](https://amospromanual.dev/07-06-amal.html) ; **ni test reel WinUAE, ni compilation AMOS, ni PASS M19 ne sont attestes**. Le preflight hors AMOS ne prouve pas un comportement runtime.

## Executer sous AMOS / WinUAE

1. Verifier que les banques **11, 12, 13 sont libres**. Le test les refuse si elles sont occupees ; il n'efface jamais une banque initiale. Installer la R84 validee.
2. Importer `M19_P0_AMAL_BOBS_01.asc` avec **Project -> Merge ASCII**. Lancer sous AMOS. L'ecran prive AGA est en **320x256x256 couleurs**.
3. Observer deux motifs 16x16 colores et animes : premier horizontal, second vertical ; chaque Bob change d'image alternativement. Le prototype dure au maximum **240 frames de logique**, Echap permet une sortie anticipee apres la mise au premier plan de la fenetre AGA par `Amos To Back`.
4. Le programme ferme l'ecran, arrete AMAL avant liberation de ses tampons, restitue AMOS, affiche RESULT/ERR et cree `RAM:M19_P0_AMAL_BOBS_INTERPRETED.TXT`, `_RUNTIME.TXT` ou `_COMPILED.TXT` suivant `Prg State`.
5. Transmettre le **journal RAM**, la confirmation du mouvement des deux Bobs et l'eventuel message d'erreur avec sa ligne. Ne **pas** compiler pour le premier passage : Gate C sera envisagee en fin de chantier.

**Criteres P0 :** `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK>=25`, `MOVE_X0>0`, `MOVE_Y1>0`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, `CLOSE_RETURNED 1`, un journal cree sans erreur et observation visuelle. Les deltas Chip/Fast sont mesures avant ecriture dans RAM: ; interpreter avec les autres lignes du rapport.

Le premier rendu reconstruit volontairement **tout le fond** avec `Aga Blit Fill` ; les deux Bobs utilisent `Aga F Icon` en mode transparence. `Synchro` est appele une seule fois par frame dans la boucle AMOS, et aucune commande de dessin n'est appelee par interruption. Les retries des commandes graphiques et du Swap sont **bornes**.

[Plan M19](../../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Roadmap](../../docs/ROADMAP.md) · [Regles source](../../EXTENSION_SOURCE_RULES.md).
