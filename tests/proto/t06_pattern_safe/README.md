# T06B — Pattern immédiatement après Swap

Préparé le 24/11/2026 dans la campagne L2b/0.14.1, à la suite du [T06A PASS](../../../docs/evidence/T06_PATTERN_RUNTIME_PASS_L2B_2026-11-24.TXT). [ASC](T06_PATTERN_SAFE.asc) 5 198 octets ASCII LF, SHA256 `a425acd7df5928fe8e88aac7cb97afba4607375d6e1a7ca6cdf5926c503e961a`, Git blob `4f6379af79bcc285f8924985a47d0d9ce136a914`. Préflight local du skill AMOS PASS sur ces octets exacts. **Gate B NON TESTÉE**, pas de Compiler demandé.

Bibliothèque unique attendue : P2d-L2b, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc` ([livraison](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/a336339c0e37613ff1ac40b8f7467d35ebba84db)). Même configuration WinUAE 68030 / JIT ON / PAL AGA, banque 27 libre. Aucun fichier IFF/ABK. Projet vierge, Merge ASCII, Runtime. La sonde T06A reste l'ASC courant unique inchangé.

## Protocole

12 cycles de trois Swaps réussis, donc six appels Pattern sur chacune des deux pages physiques si tous les cycles réussissent. Chaque cycle remplit et contrôle le back à 17, Swap, remplit et contrôle l'autre page à 239, Swap. **Pattern est la première commande AGA après ce deuxième Swap réussi** (aucun Wait Vbl, aucune capture ni writer intercalés). Le test ne lit pas le drapeau interne Safe : il sollicite la fenêtre post-Swap sans prouver que le message n'était pas déjà arrivé avant l'appel. Capture CBlock ensuite (CPU 0, x160, 8x1, trois lignes), attente/reprises éventuelles uniquement après Pattern. Vérifie 64/128/192 ; si ces pixels sont valides, Swap diagnostique puis capture de l'ancien front 239/239/239. Aucun Swap après erreur de dessin. Chaque reprise de Fill, Capture ou Swap est bornée à quatre VBL, au besoin ; pas de VBL imposée après Swap réussi. Pas de mesure FPS. Fermeture et journal en cas de FAIL normal. Le refus forcé Safe absent et l'échec d'allocation restent couverts par la Gate A simulée, pas injectés sur WinUAE.

## Journal attendu

RAM:T06B_SAFE_RUNTIME.TXT : PRG_STATE 1, RESULT 1, ERR 0, VALID_ROUNDS 12, PATTERN_CALLS 12, PRE_PATTERN_VBLS 0 (compteur de protocole, pas nombre de VBL internes), BACK_OK 12, FRONT_OK 12, SWAPS 36, SWAP_REFUSALS=SWAP_RECOVERED, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1, VERDICT PASS. Les compteurs de retries ne sont pas obligatoirement nuls.

ERR10/11 et 13/14 = Fill ou capture du marqueur ; ERR12/15 = Swap de préparation ; ERR30/31 = capture ou indices arrière après Pattern ; ERR40 = Swap diagnostic ; ERR41/42 = capture ou indices de l'ancien front ; ERR60 = fermeture. Les indices finaux et ROUND_LAST localisent un éventuel échec. Un PASS qualifie le scénario post-Swap réel, pas une preuve exhaustive des timings ni des ressources L3.

## Résultat T06B PASS (L2b)

T06B Runtime PASS sur L2b : 12/12 cycles, 12 Pattern immédiatement après Swap réussi sans VBL préalable, BACK_OK=FRONT_OK=12, 36 swaps, 0 refus Swap, 12 reprises Fill et 12 Capture abouties, ERR 0, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. T06A et T06B qualifiés en Runtime ; fenêtre post-Swap exercée sans observation directe du drapeau interne Safe. Refus Safe absent/allocateur injectés couverts par Gate A, pas par WinUAE. Compiler reporté, D non testée. [Journal original](../../../docs/evidence/T06B_SAFE_RUNTIME_PASS_L2B_2026-11-24.TXT). Journal original 488 octets CRLF, SHA256 `1f07abe44b08ae13b294ddec5e80f507642920deba9a8e64f750e36ab26d1263`, blob `030887327d580e83520df62ae99270e31423b85b`. [Suite L3/T14A](../l3_resources/README.md).
