# M19 S2a-P1 — intégration publique du changement d'image

26/11/2026 — auteur « ok go ». Cible MC68020+, source-only sur main. Parent exact P2m 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`. [P2m Runtime/Compiler](M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md) · [staging 148 cas PASS](M19_S2A_FRAME_STAGE_2026-11-26.md). Aucun changement du binaire actif, de LAST_GOOD, de l'ASC, de l'ABK ou des tokens.

## Intégration

[Module natif](../src/native/m19_s2/M19_S2A_FRAME_CHANGE_MC68020.s) et [builder](../tools/build_m19_s2a_in_memory.py). Le builder réassemble UNIT207 P2m intégralement et exige l'identité octet pour octet du parent ; réassemble ensuite la variante à partir des mêmes sources, avec les points de raccordement explicites et les deux modules S2a. Seule UNIT207 est modifiée ; UNIT142 (65424 octets), stubs AP20 et tokens restent exacts. Les 105 commandes et 214 entrées sont inchangées. Réserve PC16 16384 exigée. Reproduction binaire testée en mémoire deux fois. Aucun fichier installable généré.

- Même objet N et même image I : déplacement existant, sans WaitTOF additionnel.
- Même objet, nouvelle image : banque sélectionnée live et identique, génération identique, préparation P2a détachée, hauteur/palette RGB24/hotspot identiques ; largeur 16, 2 plans. Le premier objet continue à utiliser les canaux 2/3 et le même bloc Chip de deux slots. Pas de Sprite Off, GetSprite ou FreeSprite lors d'un changement réussi.
- Avant écriture du slot inactif : snapshot GfxBase, ViewPort privé en tête du View actif, absence de Gels Sprite Copper / user Copper sur ce ViewPort, références exactes descripteur et copinit, paire 2/3 réservée, deux WaitTOF avec relectures. Pas de lecture non bornée de LOF/SHF ni d'écriture directe des pointeurs Copper. Les deux adresses doivent partager le mot haut (refus de traversée 64 Kio). Scratch libéré tant que jamais publié. Relecture du contexte avant ChangeSprite et vérification après ChangeSprite et MoveSprite ; métadonnées mises à jour seulement après confirmation. V40 ChangeSprite n'est pas un BOOL. Le chemin Close/End P2m reste exact.
- Pré-publication : refus, image active et allocation conservées ; slot inactif éventuellement préparé. Post-publication incertaine : ID du record invalidé, retrait P2m tenté, sinon quarantaine sans libération prématurée. Off/Close restent accessibles.

| Retour | Motif S2a |
| --- | --- |
| -200 | descripteur actif non reconnu |
| -201 | banque/sélection/génération invalide ou modifiée |
| -202 | préparation ou compatibilité frame refusée |
| -203 | contexte ou références OS non concordants |
| -204 | changement traversant une frontière 64 Kio |
| -205 | publication/déplacement non confirmés ; retrait tenté |

Les validations P2m de coordonnées, palette, propriétaire et retraite restent applicables. Les contrôles OS supposent le propriétaire exclusif des canaux et aucun Poke/Copper concurrent. Les deux WaitTOF bornent la première politique de réutilisation ; coût à mesurer (environ deux trames PAL avant changement, pas de promesse 50 Hz). Les preuves WinUAE et Amiga réel restent distinctes.

## Tests

[Gate A publique](../tools/test_m19_s2a_public_gate_a.py) : 100 alternances par mode DB simple/double et par modèle AP20, déplacement sans changement supplémentaire, invariants d'allocation et d'écriture du slot inactif, contenu exact de la frame, refus de banque/palette/hauteur/hotspot, OOM, changement de référence tardif, frontière 64 Kio, échec ChangeSprite/MoveSprite, quarantaine, Off/Bank Free/Close/End depuis les deux slots. Rejouer la suite P2m inchangée, la chaîne DB/IFF/Swap/capture et les régressions Pattern/SafePort/Bob. [CI dédiée](../.github/workflows/m19-s2a-public-gate-a.yml).

**Statut au commit : sources et tests intégrés, Gate A à relever.** Les modèles CPU ne prouvent pas l'instant réel des lectures DMA. P2m reste le seul binaire actif ; aucun test WinUAE S2a à lancer avant qualification et livraison de la paire exacte.

## Revue source après intégration

Le snapshot doit refuser également un pointeur LOF/SHF déjà invalide et stable. Vérification TypeOfMem des deux débuts de listes (2 octets, sans parcours ni modification), test négatif sur les deux champs. Cette corroboration ne démontre pas l'absence de références dans les listes dynamiques. La Gate A du commit précédent ne peut pas qualifier les octets corrigés.

## Reprise 26/11 au soir — qualification parallèle

Auteur : « ol continu jusqua la lib », autorisation de bascule sur main après Gate A et préflight exacts, sans LAST_GOOD. [CI 45897664765](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45897664765) annulée à 30 minutes après PASS des deux campagnes publiques (200 changements + négatifs par modèle, soit 400 au total). Binaire 151164 octets, SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2`, blob `190504fd46494224c6c32e20f17dcc3d6a027684`, UNIT207 12142, marge PC16 20592, UNIT142 inchangée 65424. Pas de PASS complet anticipé. La même suite est maintenant répartie sur neuf jobs indépendants, chacun reconstruisant exactement le même binaire, avec délai 60 min. Les callbacks Python sur les instructions natives ordinaires sont évités (CPU et hook des écritures inchangés, toutes les interceptions OS et pseudo-appels restent actives). Aucune réduction des tests. Préparation indépendante du seul futur ASC et de sa banque de deux frames, issue du modèle exact des tests publics. L'ancien ABK reste inchangé pour la provenance P2m. Le futur verdict exige la mémoire nette avant/après et après fermeture, sans confondre un écart transitoire d'allocateur avec une fuite ; les écarts intra-écran restent journalisés. Aucune distribution alternative ni écriture CI.

## Qualification et activation 27/11/2026

**27/11/2026 — S2a-P1 active sur main, autorisation auteur « ol continu jusqua la lib ».** [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45907171922), commit source `91a4acf89f511420ba0a87515ec2a85b6d124277` : 10 jobs réussis, 400 changements d'image et négatifs, 200 cycles/20 fermetures P2m hérités, DB/IFF/Swap/capture, 184 Pattern, 172 SafePort, 10 suites Bob, reconstruction exacte et préflight strict PASS. Lib 151164 octets SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2` blob `190504fd46494224c6c32e20f17dcc3d6a027684`; ASC 7265 octets SHA256 `d191282714b43d38b07585fa1054895885f8b2d1be403abcfd9f5f76d993ebdb` blob `ac74e8773a86914a00f3a153487afe61a9803efc`; nouvelle banque de campagne AGSP_S2A_ANIMATION.ABK 372 octets SHA256 `4b13eb9ac278ad56a73c043327a11d48a3d79d65807563409d94e64aa16d50aa` blob `210179c9328e1ff032070b2dd40ffa8849e8294a`. 105 commandes / 214 AP20, MC68020+, UNIT142 65424 (110 libres) inchangée, UNIT207 12142, PC16 max 12172, marge 20592. Uniquement UNIT207 et titre changés depuis P2m. Aucun changement LAST_GOOD L2b, ancien ABK ou archive, aucun autre dépôt, branche, promotion ou release. B/C/D S2a non testées. L'ancien P2m reste dans Git.

Les deux échecs de relance intermédiaires étaient des erreurs de quoting shell, corrigées par le runner Python à arguments explicites. Aucun changement natif. Tous les shards ont retrouvé la même empreinte et réussi. Le préflight et le binaire exact proviennent de la même CI. Les consommateurs de provenance sont adaptés à S2a, les builders historiques retrouvent leurs parents épinglés par SHA dans Git. Les contrôles post-livraison restent distincts.
