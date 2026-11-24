# AMOSPro AGA Extension — sources natives MC68020

**Version de travail P2d-L2b (cible 0.14.1, non publiee)** : [master ASM direct](m19_p2d_l2b/M19_P2D_L2B_LINKED_EDITABLE.s) et [guide](m19_p2d_l2b/README.md). 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, 100 commandes / 203 AP20. Comparaison exacte exigee en CI avant de declarer le master direct valide.

| Dossier | Role |
| --- | --- |
| [m19_p2d](m19_p2d/README.md) | Base ASM historique P2d / LAST_GOOD figee |
| [m19_p2d_l1](m19_p2d_l1/) | Overlays SafePort IFF Load et Back Fill |
| [m19_p2d_l2](m19_p2d_l2/) | Overlay premier Bind B8 |
| [m19_p2d_l2b](m19_p2d_l2b/README.md) | Overlay Screen Pattern et master lie actif |
| [m19_s1](m19_s1/) | Sprite gele, hors L2b |

[Builder source L2b](../../tools/build_m19_p2d_l2b_pattern_in_memory.py) : contrat de reconstruction. [Reprise et validation](../../docs/NEXT_SESSION.md). MC68020/68EC020 minimum. Pas de desassemblage de production ni de promotion automatique.
