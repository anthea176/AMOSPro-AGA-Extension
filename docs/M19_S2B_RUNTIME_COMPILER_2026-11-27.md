# M19 S2b-P1 — résultats Runtime et Compiler du 27/11/2026

**27/11/2026 — S2b-P1 : Gates A/B/C PASS pour le banc multi-Sprites.** B Runtime (`PRG_STATE=1`) 1/1 et C vrai Compiler (`-1`) 1/1, 300 changements et 300 déplacements chacun, 2/2 ouvertures/fermetures, 6 retraits automatiques, saturation -206 conforme, ERR/CLEAN_ERR=0, pertes Chip/Fast par cycle et écran nulles. CI post-activation `502739d` : 42 succès, 1 skipped, 0 échec. D physique non testée ; observation visuelle, relance Runtime indépendante sans reset et SHA installé non attestés par les logs. Lib/ASC/ABK et LAST_GOOD L2b inchangées. Auteur « ok allons y » : consigner preuves puis audit/répartition source-only sans nouvelle API, préserver ABI et requalifier avant S2c ; aucune promotion ni bascule de nouvelle Lib autorisée par ce relevé.

## Identité de référence
- Livraison [502739d](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/502739db328178d7abd47e8bc247a7c54d453139), builder [build_m19_s2b_in_memory.py](../tools/build_m19_s2b_in_memory.py) et [rapport Gate A](M19_S2B_MULTI_SPRITE_2026-11-27.md).
- Lib 152876 octets, SHA256 `b44edbbcf4b3c02cb6527ea0f002bee863c992dd4b670636e7431a1b69e1a2fa`, blob `6a9493b69c5fa64a0cb167722423cfee7f18bbb3` ; ASC 8954 octets, SHA256 `2cda351432ba495589c4848ef8c2d640426e18c6e71287d643a506e2e21acde0` ; ABK 1012 octets, SHA256 `eb0060bce79d15785d5d6f6caf31f8819adfd518b0e179dca5feb025b80b2c78`. Identités Git vérifiées ; SHA installé dans WinUAE non mesuré dans les deux logs.
- LAST_GOOD L2b 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`, protégée.

## Journaux auteur préservés à l'octet (CRLF)
| Mesure | Runtime | Compiler |
| --- | ---: | ---: |
| PRG_STATE | 1 | -1 |
| CPU_ATTNFLAGS | 32823 | 32823 |
| OPENED / CLOSED | 2 / 2 | 2 / 2 |
| SATURATION / FULL_RC | 2 / -206 | 2 / -206 |
| CHANGED / MOVED | 300 / 300 | 300 / 300 |
| SHOWN / OFF_COUNT / AUTO_CLOSE | 8 / 2 / 6 | 8 / 2 / 6 |
| SPRITE_RC / CHANGE_RC / MOVE_RC / OFF_RC / FREE_RC | 1 / 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 / 1 |
| Chip avant = après | 1791320 | 1757416 |
| Fast avant = après | 138092136 | 137821312 |
| Chip/Fast cycle loss | 0 / 0 | 0 / 0 |
| Chip/Fast screen loss | 0 / 0 | 0 / 0 |
| RESULT / ERR / CLEAN_ERR | 1 / 0 / 0 | 1 / 0 / 0 |
| VERDICT | PASS_S2B_MULTI_SPRITE | PASS_S2B_MULTI_SPRITE |

- [Runtime](evidence/M19_S2B_RUNTIME.TXT), 572 octets, SHA256 `c75fadab104d2d8c034289a3ca675eb4e5d8cbe302bc29a0fed6b7d4a9a12e39`.
- [Compiler](evidence/M19_S2B_COMPILED.TXT), 573 octets, SHA256 `eee5492df444804f36e524508ec9e86a5a7601debcea71c87a1b3af507d0d0d5`.

Les compteurs correspondent à la campagne. L'écart Fast temporaire mesuré dans les deux écrans par rapport au départ est de 1016 octets dans chacun des modes, récupérés en fin de campagne ; aucune différence entre les deux cycles écran d'un même lancement. Les différences de mémoire initiale entre Runtime et Compiler ne sont pas des fuites mesurées. Les logs ne fournissent ni validation visuelle explicite, ni preuve de seconde relance Runtime sans reset, ni configuration CPU/JIT effectivement relevée au-delà de CPU_ATTNFLAGS. Pas de Gate B interpréteur strict (PRG_STATE=0), pas de Gate D ni preuve DMA matérielle universelle. Aucun transfert des Gates vers une future candidate.

## CI et suite
Gate A [46041721740](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46041721740) 7/7 jobs ; reconstruction/préflight [46042040810](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46042040810) PASS. Sur 502739d, 42 workflows success, 1 skipped, aucun échec, notamment [Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46042661214). La marge d'UNIT142 (10 octets) impose un audit de répartition avant S2c. UNIT207 : 13756 octets, PC16 max 13786, marge 18978 ; réserve de conception 16384. Cible MC68020 minimum. Ne pas remplacer les 4 chemins Close/End ni changer les offsets sans vérification source, ABI et requalification intégrée des graphismes. Aucun nouveau token, binaire, ASC, archive de tests, tag ou promotion.
