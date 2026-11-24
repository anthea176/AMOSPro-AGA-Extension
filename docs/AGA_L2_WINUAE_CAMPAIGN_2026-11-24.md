# P2d-L2 — préparation de la campagne WinUAE B/C

**Résultats du 24/11/2026 :** SafePort IFF / Back Fill / premier Bind B8 B/C PASS rapportés, P2 ALL IN ONE Runtime PASS rapporté (240/240, 252 swaps, 120 refus récupérés), EDGE SAFE 20x18 Runtime PASS (240/240, 0 refus), RPG V9 Runtime PASS (250 frames, 2 retries). Identité L2 confirmée par l'auteur. Les autres Gates C sont reportées par choix auteur ; D non testée. EDGE sans pré-VBL Runtime PASS (240/240, 241 swaps, 120 refus tous récupérés, 128 pixels de bord valides, ERR 0). T06 et L3 restent ouverts. LAST_GOOD intacte. Sprite gelé. [Rapport et logs](AGA_L2_WINUAE_RESULTS_2026-11-24.md). Les paragraphes suivants décrivent la préparation de la campagne ; ne pas réexécuter les tests déjà validés ni demander une nouvelle compilation.


**24 novembre 2026 · main uniquement. Candidate active autorisée / PREFLIGHT PASS ; B/C/D NON TESTÉES.**

Candidate L1+L2 : **136 332 octets**, SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1`, 100 commandes / 203 AP20 ; [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45402935866), [commit source a6065ac](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/a6065ac83fd648934b98598aae86b8fa5d31b437). 172 cas writers + 10 suites Bob, deux modèles AP20. Bascule autorisée par « allons y » : [Lib active](../dist/AMOSPro_AGA.Lib), blob d9bc3d015c4f396b2f2d674315fff4918fa0610e. LAST_GOOD P2d reste protégée. Aucun changement Sprite.

## 1. Essai discriminant T02/T04/T19/T17 partiel

ASC actif [M19_P2D_L2_SAFEPORT_BC.asc](../tests/current/M19_P2D_L2_SAFEPORT_BC.asc), copie exacte de la sonde préparée dans tests/proto, 6 703 octets ASCII LF, SHA256 `720348897fd0f939dc413687ccc69ed524fd7edff863dcc89f320a1f68e0f974`, blob attendu `024a69d90ac09af71c8fd55c306fefe2d99a9c84`. Préflight statique AMOS local PASS sur ces octets ; pas une compilation. Seul ASC actif ; ancienne référence P2 ALL IN ONE conservée dans tests/passed et examples.

Ressource : [AGA_DEMO_320x256_256c.iff](../tests/current/AGA_DEMO_320x256_256c.iff) (80 776 octets, blob baf5d4c9e2a0a95f37762d7a2d84c63a093ddb92). Copier sans modification dans RAM: avant essai. Inventaire ILBM : 320x256, 8 plans, 256 couleurs, CAMG 00021000, ByteRun1. Taille et blob Git vérifiés ; octets du BODY non redécodés indépendamment ici (connecteur binaire limité). Le programme vérifie Pic Info et compare deux pixels à son premier chargement de référence, ce n'est pas un oracle de décodage indépendant.

Banques 24 (AGBO) et 27 (C Block) libres au départ, créées sur place ; pas de banque externe ni AMAL dans cette sonde. Fermer l'écran et restaurer AMOS sur erreur ; si Mouse X ne confirme pas l'absence d'écran, conserver les banques plutôt que risquer une libération pendant une fermeture incomplète.

| Phase | Séquence et attendu |
|---|---|
| 1 | Open/DB, IFF témoin, 2 pixels, remplir les deux pages d'un marqueur différent du premier pixel IFF. |
| 2 | IFF immédiatement après Swap, avant tout autre writer. Premier retour et 0..4 VBL de retry journalisés. Comparer 2 pixels au témoin. Préparer sous le futur Bob un rectangle distinct de pen 165, puis Swap. |
| 3 | Back Fill immédiatement après Swap ; une VBL après l'instruction, jamais avant. Vérifier deux pixels éloignés du back, distincts du marqueur précédent. L'instruction n'a pas de résultat numérique ; un timeout sans écriture reste un refus légitime de sécurité mais fait échouer le test fonctionnel. |
| 4 | Bob 20x18 pen 165, banque/mask, nettoyer les pixels sources, Auto Update 1, dernier Swap sans Bob. |
| 5 | Bob 1, puis Swap, sans Fill/IFF/capture/VBL intermédiaire. 0..4 retries uniquement après refus, donc pas de contournement du premier Bind. |
| 6 | Présentation suivante, vérifier top-left et bottom-right du Bob sur l'ancienne page affichée (capture alignée x112, masque 16). Close, Mouse X -1, compteurs mémoire avant/après. |

PASS attendu : RESULT 1, ERR 0, PHASE_LAST 6, IFF_OK 1, BACK_FILL_OK 1, FIRST_BIND_OK 1, PIXEL_CHECKS 6, PIXEL_LAST 165, SWAPS 6, SWAP_REFUSALS=SWAP_RECOVERED, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. Pas d'exigence de zéro refus ; les premiers retours restent visibles. ERR20 IFF non récupéré, 21/22 pixel IFF, 30/31 Back Fill, 50 premier Bind non récupéré, 60 seconde présentation, 61/62 pixel Bob, 70 fermeture suspecte. Les autres codes couvrent préparation et capture.

Limites : l'ASC ne lit pas DB+20 ni GetMsg ; il ne prouve pas chaque timing réel de Safe, l'absence de toute corruption front ou le CRC de toute la page. Les deux références IFF sont locales. La palette est commune ; aucun test ColorMap exhaustif. La preuve Gate A instrumentée complète ces observations. CLOSE_RETURNED et Mouse X restent des indices fonctionnels, pas une mesure exhaustive des frees. Les deltas Chip/Fast sont diagnostiques, à comparer sur répétitions. T06 Screen Pattern reste VM : ne pas provoquer une écriture potentiellement non-Safe dans cette sonde.

## 2. Campagne active

1. Vérifier le SHA du fichier **installé** dans APSystem, redémarrer AMOS. Configuration fonctionnelle WinUAE 68030 / JIT ON / AGA PAL ; noter RAM Chip/Fast, versions AMOS et Compiler. Pas de mesure de performance dans ce test. Ne pas changer de réglage entre B et C.
2. Utiliser le seul ASC actif sous tests/current. Un seul ASC de campagne active à la fois. Projet vierge, Project -> Merge ASCII. Runtime `Prg State=1`, journal `RAM:P2D_L2_RUNTIME.TXT` ; nouvel exécutable produit avec le vrai AMOS Compiler, `Prg State=-1`, journal `RAM:P2D_L2_COMPILED.TXT`. Copier chaque log avant de relancer (le programme utilise Open Out). Mode 0 séparé. En cas de freeze, relever le dernier affichage, Guru et configuration, ne pas inventer un log.
3. Ensuite, requalifier **à l'identique** [M19_P2_ALL_IN_ONE.asc](../tests/passed/M19_P2_ALL_IN_ONE.asc) (25 056 octets, blob c48d334fd4508d402d28399bffdfec08d4cb4acb), 240 frames, collisions, Flip, Planes. RESULT 1, ERR 0, 240 VALID_SAMPLES, 252 SWAPS, refus tous récupérés. Garder les logs anciens intacts.
4. Rejouer le différentiel [P2_EDGE_20X18.asc](../tests/proto/rpg_bob_dim/P2_EDGE_20X18.asc) sans VBL supplémentaire, puis la variante EDGE_SWAPVBL en comparaison seulement si nécessaire. EDGE historique : FAIL ERR15 frame221 ; 123 contrôles edge réussis ne prouvaient pas le test entier. Cette sonde cible l'amorçage B8, pas une attribution automatique d'ERR15 en régime établi. Le vrai scénario RPG décor/objets, T14 ressources, T06 Pattern et Gate D restent ouverts.

## 3. Livraison autorisée

Lib exacte reconstruite par [CI 45428031730](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45428031730), 172 cas writers et 10 suites Bob repassés. Réassemblage de la candidate à partir de P2d protégée vérifiée par SHA256 et des seules plages assemblées par vasm dans ce job ; SHA256 final identique à la Gate A. Blob Git `d9bc3d015c4f396b2f2d674315fff4918fa0610e`. Builder et contrôles actifs reconnaissent exclusivement les identités épinglées, et la CI L2 compare le binaire livré à la reconstruction source complète. Aucun changement ASM depuis la Gate A. L'ASC exact est activé sans modification et l'ancienne copie active de P2 ALL IN ONE retirée ; sa copie passée et publique restent intactes. Aucun nouveau PASS WinUAE. Les nouvelles CI de distribution doivent être lues indépendamment. S1-P1e reste historique, aucune promotion LAST_GOOD.
