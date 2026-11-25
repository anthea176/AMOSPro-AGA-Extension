# S1-P2j — correctif diagnostique après rejet Runtime P2i

Autorisation auteur « ok go » après audit. Base exacte main f38dad5b0520e115efbc0fd8e03f1a83d56f4709 : P2i 149384 octets, SHA256 89b7a9ead30152d2088ca761e81f7016a47bab451024c637009426d7ba777b96, blob fde85e98c3209e8affc6044532d68bfa8bba4006, 105 commandes / 214 AP20. LAST_GOOD L2b blob 2809b4b409eea9e234df1b96bf2b08bd393d8c85 protégée. La Gate A P2i 45682158541 PASS n'est PAS une qualification réelle.

## Échec original et causes possibles

[Journal auteur original](evidence/M19_S1_PUBLIC_RUNTIME_2026-11-25.TXT), 351 octets CRLF, SHA256 f8f53e2bf7fb4921f99fa794f5a60a2a8334c17f4ecf63c81a1cc52efaa90be9, blob 5ce89d07acae4602aff5f962210e0afdc5db9cd3. PRG_STATE 1, ERR 10, 0 déplacement, RESULT 0, FAIL. Chip 1791560 -> 1620816 (-170744), Fast 138098032 -> 138088904 (-9128). Compatible avec une fermeture incomplète des deux buffers, pas preuve de fuite permanente. Le journal P2i masque CLEAN_ERR et tous les refus natifs. Le branchement précis du premier refus reste inconnu.

P2i vérifiait la table SimpleSprites avant le premier MoveSprite et supposait une publication immédiate de ses structures privées. P2b/P2d r2 ont observé ces références APRÈS déplacement et VBL. P2i vérifiait VideoControl/palette avant GetSprite, alors que P2b réservait les deux canaux puis vérifiait. Le mock P2i utilisait une banque synthétique image 1 et plaçait artificiellement le Screen sans DB ni fenêtre. L'ordre et le contexte ont donc divergé des preuves réelles. La CI post-livraison a aussi relevé 17 échecs sur 30 campagnes (12 succès, une en cours au relevé) dont formats de log et vérificateurs historiques de version. Ne pas appeler ces échecs des régressions natives sans diagnostic.

## P2j

- [Source publique](../src/native/m19_s1/M19_S1P2J_PUBLIC_MC68020.s), [retirement](../src/native/m19_s1/M19_S1P2J_RETIRE_MC68020.s), [reclaim](../src/native/m19_s1/M19_S1P2J_RECLAIM_MC68020.s), MC68020+, overlay source dérivé de P1i/P2i ; builder [P2j](../tools/build_m19_s1p2j_in_memory.py), aucun changement des sources P2i historiques.
- Deux acquisitions explicites 2/3, contrôle palette après acquisition, ChangeSprite puis contrôle du descripteur SimpleSprite documenté et MoveSprite, sans lecture de la table privée avant Move. Copie Chip indépendante de la banque. Un seul couple N/I, mêmes arguments et tokens, retour de Sprite=1 ou code négatif de diagnostic TEMPORAIRE. Tout programme doit tester =1, pas non-zéro. Off et Bank Free restent 1/0.
- Retrait sur reçus GetSprite exacts, ChangeSprite vers blank, trois WaitTOF, FreeSprite(3), FreeSprite(2), deux WaitTOF. Une observation blank échouée ne doit plus bloquer Close après libération des canaux possédés. Refus si identité/propriété incohérente ; jamais de libération d'un canal inconnu. Aucun accès à une ancienne VP après Close. CloseScreen FALSE ne doit jamais être pris pour un succès.
- **Verrou DMA rétabli : aucun FreeVec de Chip exposée.** Garder registre 112 + record 40 + Chip 192 pour la fixture, soit 344 octets utiles max pour cette image, hors overhead AllocVec. Un seul ensemble retenu ; nouvelle acquisition refusée tant que pending, réaffichage après Off refusé. Une exécution par snapshot/reset. Bank Free après fermeture exposée retourne 0 intentionnellement, sans prétendre être une lib finale. Aucun recyclage non prouvé, aucune progression vers S2.
- [Gate A P2j](../tools/test_m19_s1p2j_gate_a.py) : ABK réelle 532 octets SHA256 225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93, ID3 ; publication table différée jusqu'à Move, table Z3 $40004690, Close/End avec DB et fenêtre + messages Safe/Disp, échecs acquisition/alloc/palette, absence de FreeVec exposée, régressions 2D. OS toujours simulé ; les tests différés sont des contre-exemples au mock, pas une affirmation sur l'ordre interne réel de V40. [Autodoc GetSprite](https://d0.se/autodocs/graphics.library/GetSprite), [ChangeSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0427.html), [MoveSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0302.html).
- Préflight local du nouveau ASC PASS, 3930 octets, SHA256 7c6cd1fdca86323271810d37f484b2bad33b70fe02c968a4d7bb306511c56084, blob a23da76b8867e2b4caabb639ed71b1c9a615c5f1. Une séquence, 100 mouvements, erreur native et cleanup indépendants, Close retourné et état fermé distincts, modes séparés, mesure avant création du journal. Pas de test à lancer avec P2i.
- Gate A exacte à relever. B/C/D non testées. Aucune installation de P2j avant réussite. P2i rejetée, LAST_GOOD et banques inchangées.

### Codes Sprite P2j (diagnostic uniquement)

- -101 objet invalide ; -102 image/coordonnées.
- -110 State ; -111 cellule de liaison ; -112 Screen ; -113 GfxBase/version ; -114 dimensions ; -115 Modes/Copper utilisateur ; -116 ColorMap.
- -120 sélection/owner ; -121 banque live ; -123 pending ; -124 record ; -125 snapshot ; -126 préparation Chip ; -127 revalidation ; -128 géométrie.
- -131..-135 raison P2h (absent, occupé, incompatible, alloc, contexte Exec).
- -139 identité de ressource existante ; -140 réaffichage interdit ; -141 canal 2 indisponible ; -142 canal 3 indisponible ; -143 reçu incohérent.
- -150 VideoControl ; -151 bases/résolution/priorité ; -152 résolution par défaut ; -153 RGB ; -160 descripteur/publication.

## Qualification et activation

S1-P2j : 148296 octets, SHA256 `47d554866f1c04a63f9111dafd8bc64c9b937fc8e2ea9706ab6f20d12777b05a`, blob `29d9863a846179f43ac540d85afd7666f6405af0`, 105 commandes / 214 AP20, MC68020+. [Gate A exacte PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45690711843) sur 51bf3bdc176feb5eccdf4ec6b700e5533c20656e : 54 scénarios Sprite, 184 Pattern, 172 SafePort, 10 suites Bob et chaîne DB/IFF/Swap/capture dans les deux modèles AP20. UNIT142 64560 octets, groupe Sprite natif 10104 octets. B/C/D réelles NON TESTÉES. Un seul ensemble exposé conservé (192 octets Chip, 152 octets registre/record pour l'image 3, hors overhead). Aucune preuve DMA free ; aucun réaffichage après Off, reset avant nouvel essai. LAST_GOOD L2b inchangée, blob 2809b4b409eea9e234df1b96bf2b08bd393d8c85.

Premier assemblage P2j passé, test initial 45690266047 FAIL sur la tentative de réaffichage après Off (contrôle palette avant vérification flags4). Corrigé : état retrait vérifié avant palette. Gate A finale ci-dessus PASS. ASC préflight statique PASS. Blob extrait des 97 fragments base64 de la CI, identique au blob annoncé. Vérificateurs d'identité historiques et journal ASC corrigés ; CI post-activation à relever séparément. Aucun PASS WinUAE extrapolé.

## Retour auteur Runtime 25/11/2026

Premier essai sans redémarrage FAIL -132 (fermeture confirmée, CLEAN_ERR 0), puis après redémarrage PASS_DISPLAY_CLOSE_RETAINED_ONLY (100 mouvements, effacement banque, retrait/fermeture OK, RESULT 1 ERR 0, DMA_FREE_PROVEN 0). Chip -200, Fast -168. Gate B limitée de P2j acquise après reset ; C/D non testées. Cause exacte de -132 non instrumentée. [P2k](M19_S1_P2K_TRANSACTION_2026-11-25.md) traite la durée de vie du verrou, pas le DMA.
