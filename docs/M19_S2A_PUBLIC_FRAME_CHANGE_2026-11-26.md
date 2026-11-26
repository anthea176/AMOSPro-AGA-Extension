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
