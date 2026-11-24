# AMOSPro AGA Extension — sources natives MC68020

**Candidate active S1-P1f** : source native Sprite [M19_S1P1D_BANK_PUBLIC_MC68020.s](m19_s1/M19_S1P1D_BANK_PUBLIC_MC68020.s), Get [M19_S1P1E_GET_PUBLIC_MC68020.s](m19_s1/M19_S1P1E_GET_PUBLIC_MC68020.s), base L2b ci-dessous, [builder combiné](../../tools/build_m19_s1p1f_l2b_get_sprite_ap20.py). 142684 octets, SHA256 `dffe70c5550a4387b99901a2431892a2a7d6fe67328ab7cff8f69afd7ad91931`, 102 commandes / 208 AP20 ; [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45466155974), B/C/D non testées. Les sources ASM restent strictement inchangées, le builder ajoute le groupe Sprite au socle lié.

**P2d-L2b promue LAST_GOOD le 24/11/2026 (cible 0.14.1, non publiee)** : [master ASM direct](m19_p2d_l2b/M19_P2D_L2B_LINKED_EDITABLE.s) et [guide](m19_p2d_l2b/README.md). 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, 100 commandes / 203 AP20. Comparaison exacte du master direct [PASS en CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45462745139), memes 136708 octets que LAST_GOOD et le builder.

| Dossier | Role |
| --- | --- |
| [m19_p2d](m19_p2d/README.md) | Base ASM historique P2d, ancienne LAST_GOOD figee |
| [m19_p2d_l1](m19_p2d_l1/) | Overlays SafePort IFF Load et Back Fill |
| [m19_p2d_l2](m19_p2d_l2/) | Overlay premier Bind B8 |
| [m19_p2d_l2b](m19_p2d_l2b/README.md) | Overlay Screen Pattern et master lie actif |
| [m19_s1](m19_s1/) | Sprite actif S1-P1f, hors LAST_GOOD L2b |

[Builder source L2b](../../tools/build_m19_p2d_l2b_pattern_in_memory.py) : contrat de reconstruction. [Reprise et validation](../../docs/NEXT_SESSION.md). MC68020/68EC020 minimum. Pas de desassemblage de production ni de promotion automatique.
