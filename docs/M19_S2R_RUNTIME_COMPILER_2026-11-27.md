# M19 S2r-P1 — résultats Runtime et Compiler du 27/11/2026

**27/11/2026 — S2r-P1 A/B/C fonctionnelles PASS dans le périmètre du banc.** B Runtime 1/1 (`PRG_STATE=1`, Fast transitoire 128 octets récupérés), C vrai Compiler 1/1 (`-1`, aucun écart cycle), 4/4 Capture/Meta/Negative/Draw, 300 changements/déplacements, 2/2 Open/Close, ERR=CLEAN_ERR=0, pertes nettes Chip/Fast nulles. Capture WinUAE fournie : trois rectangles rouges et trois Sprites distincts simultanés. Pas de preuve de seconde relance indépendante, de SHA installé ou Gate D physique. CI post-activation en échec sur l'accès Git superficiel au prédécesseur S2b ; [correction 21 workflows fetch-depth: 0](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5c20ee6fca24b5248a7510c29d6586dfac3bfc0f) livrée, résultat final à relever. S2r active inchangée ; LAST_GOOD L2b protégée. Autorisation auteur « oui va y » pour corriger CI et consigner les preuves ; S2c après requalification CI, pas de promotion ni nouvelle Lib.

## Identité et provenance
- [Activation](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31735f84f0da50ea4ba324f9bc63bec9313cd47a) ; Lib 154352 octets, SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a`, blob `61d8211e449ffd9cb41e3fb2b6ec9efdf352c88c`.
- ASC 11806 octets SHA256 `d06f3c296d45a8766acdf678b03675c99ee702baf776a2f2f50e2da5aa8939e3`, blob `f1985251d4d37e978c4ec61b5e06f81fb3559ee4` ; ABK 1012 octets SHA256 `eb0060bce79d15785d5d6f6caf31f8819adfd518b0e179dca5feb025b80b2c78`.
- Gate A [8 jobs PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059388877), [préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46059623366). Les identités Git sont établies ; l'empreinte du fichier effectivement installé dans WinUAE n'est pas dans les journaux.
- UNIT142 63350 octets, marge 2184, gain 2174 ; UNIT207 13756, PC16 max 13786, marge 18978 ; unité AGAPIC 214=3640. 105 commandes / 219 AP20. LAST_GOOD L2b 136708 octets SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`.

## Journaux auteur, CRLF préservés
- [Runtime](evidence/M19_S2R_RUNTIME.TXT), 726 octets, SHA256 `c33077be0494f5ca25e677a178bc274d1785547656f2a4936c3292c98b90e7f8`, blob `be86caabebb2c098d3331f280d6eca44f7029735`.
- [Compiler](evidence/M19_S2R_COMPILED.TXT), 725 octets, SHA256 `b3fd7cfee759cfcc63ac16f6cc96d54192f45d3ec3f0848ebbbf4c7cd6e254b2`, blob `276abdaa9e5c41a43de614b991119c136c88b6f5`.

| Mesure | Runtime | Compiler |
| --- | ---: | ---: |
| PRG_STATE | 1 | -1 |
| CPU_ATTNFLAGS | 32823 | 32823 |
| OPENED / CLOSED | 2 / 2 | 2 / 2 |
| SATURATION / FULL_RC | 2 / -206 | 2 / -206 |
| CHANGED / MOVED | 300 / 300 | 300 / 300 |
| SHOWN / OFF_COUNT / AUTO_CLOSE | 8 / 2 / 6 | 8 / 2 / 6 |
| SPRITE_RC / CHANGE_RC / MOVE_RC / OFF_RC / FREE_RC | 1 / 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 / 1 |
| AGAPIC_CAPTURE / META / NEGATIVE / DRAW | 4 / 4 / 4 / 4 | 4 / 4 / 4 / 4 |
| AGAPIC W/H/DEPTH/COLORS/MODE | 19/9/8/256/135168 | 19/9/8/256/135168 |
| AGAPIC_RC / INFO_BAD / DUP_RC / DRAW_RC / OWN | 1/-1/0/1/0 | 1/-1/0/1/0 |
| CHIP_BEFORE = CHIP_AFTER | 1793432 | 1758984 |
| FAST_BEFORE = FAST_AFTER | 138100504 | 137824264 |
| CHIP_CYCLE_LOSS / FAST_CYCLE_LOSS | 0 / 128 | 0 / 0 |
| CHIP_SCREEN_LOSS / FAST_SCREEN_LOSS | 0 / 0 | 0 / 0 |
| RESULT / ERR / CLEAN_ERR | 1 / 0 / 0 | 1 / 0 / 0 |
| VERDICT | PASS_S2R_REPARTITION | PASS_S2R_REPARTITION |

Les deux lignes SCREEN d'un lancement ont exactement les mêmes valeurs. Le Fast mesuré après fermeture avant la libération finale est inférieur de 1016 octets au départ dans les deux modes (Runtime 138099488 ; Compiler 137823248) ; récupéré en fin de campagne. FAST_CYCLE_LOSS est le maximum des différences relevées pendant la boucle, pas une mesure nette. Le banc impose zéro perte finale et écran ; 128 octets temporaires Runtime sont récupérés, cause non isolée. B fonctionnelle PASS avec réserve, C fonctionnelle PASS, aucune prétention de test exhaustif ni de Gate D. Relance indépendante sans reset non fournie ; image statique ne prouve pas l'animation ni le comportement Off/reuse par elle seule.

Capture fournie par l'auteur `image(20261127-195929).png`, SHA256 `926a21a305b7c0e2851974b0a9d285a7632514880fe63965732b326d6fccc924` (jointe à la conversation, non déposée dans Git) : trois rectangles rouges en haut et trois Sprites aux motifs/couleurs distincts. Mode de cette capture non attesté séparément.

## Correction CI post-livraison
Les échecs de [Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46060169308) et du [contrôle canonique](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46060169275) sur 31735f8 sont liés à `git show 502739d...:dist/AMOSPro_AGA.Lib` dans un clone superficiel. Même traceback confirmé dans P2b et P2d. [Correction](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5c20ee6fca24b5248a7510c29d6586dfac3bfc0f) : 21 YAML, 22 checkouts passés à fetch-depth: 0 ; mêmes validations, aucun changement de Lib, ASC, ABK, LAST_GOOD ou sources natives. Relever les nouveaux jobs avant de déclarer la CI post-activation verte et avant S2c. Pas de transfert automatique de B/C à une future Lib. Aucun changement de branche ou publication.
