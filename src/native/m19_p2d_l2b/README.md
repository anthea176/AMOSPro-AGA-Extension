# M19 P2d-L2b — source ASM liee (MC68020)

**Promotion 24/11/2026 :** L2b est la LAST_GOOD protegee, identique a la Lib active. P2d reste la base historique reconstructible ; aucune source ASM modifiee par la promotion. [Rapport](../../../docs/M19_P2DL2B_LAST_GOOD_PROMOTION_2026-11-24.md).

**Reference de travail au 24/11/2026 :** P2d-L2b, 136 708 octets, 100 commandes / 203 AP20, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. Cible 0.14.1 non publiee. LAST_GOOD P2d protegee : 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.

## Master direct

[`M19_P2D_L2B_LINKED_EDITABLE.s`](M19_P2D_L2B_LINKED_EDITABLE.s) rassemble les sources existantes sans regeneration Python, sans desassemblage ni duplication des 268 modules de base. Les quatre ancres modifiees et l'ordre des tails sont ceux des builders source verifies.

| Correction | Bloc lie |
| --- | --- |
| L1 IFF Load | [IFF](M19_L2B_UNIT142_IFF_LOAD_BODY_MC68020.s) |
| L1 Back Fill | [Back Fill](M19_L2B_UNIT142_BACK_FILL_BODY_MC68020.s) |
| L2 premier Bind B8 | [BOBS](M19_L2B_BOBS_SUPPORT_BODY_MC68020.s) |
| L2b Screen Pattern | [Pattern](M19_L2B_UNIT142_PATTERN_BODY_MC68020.s) |

UNIT142 : 62 740 -> 62 960 (L1) -> 63 334 octets (L2b) ; BOBS : 60 928 -> 61 008 (L2). Les autres groupes, les 203 entrees AP20 et les liens PC16 restent inchanges. Les parties historiques et donnees deja classees sont conservees, pas reconverties en source metier.

## Assemblage direct

Depuis `src/native/m19_p2d_l2b/`, avec vasmm68k_mot du commit `8b85ef6eb7d257bf29a56ddc63cf2be20a317256` :

```sh
vasmm68k_mot -Fbin -m68020 -no-opt -quiet -I../m19_p2d -o /tmp/p2d_l2b_source_check.bin M19_P2D_L2B_LINKED_EDITABLE.s
sha256sum /tmp/p2d_l2b_source_check.bin
cmp /tmp/p2d_l2b_source_check.bin ../../../dist/AMOSPro_AGA.Lib
```

SHA attendu : `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`. Ne jamais ecrire directement dans dist/. Le [test Gate A](../../../tools/test_m19_p2d_l2b_pattern_gate_a.py) controle aussi ce master contre le builder et le binaire exact. La Gate A historique [45449139352](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449139352) (184 Pattern, 172 writers, 10 suites Bob) porte sur le builder L2b. La comparaison directe doit passer sa propre CI ; elle ne valide pas WinUAE/Compiler.

**Autorite des changements :** [builder L2b](../../../tools/build_m19_p2d_l2b_pattern_in_memory.py) et overlays existants. Conserver P2d/L1/L2 intacts ; synchroniser le master lie et le builder pour toute evolution. Ne pas utiliser les exports d'audit comme source de production. Sprite reste gele.

## Resultat du master direct

[CI 45462745139](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45462745139) PASS sur e74ee34 : `P2D L2B LINKED ASM BYTE-EXACT PASS 136708 a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, puis 184 Pattern, 172 writers et 10 suites Bob PASS. Aucun changement d'octet de la Lib. Gate C L2b reportee ; physique non testee. Voir [qualification](../../../docs/releases/0.14.1_QUALIFICATION.md).
