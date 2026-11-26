# S1-P2l-a — capacité AP20 et observation DMA (26/11/2026)

Autorisation auteur « ok allons y » après validation B/C P2k. Première étape source-only ; pas de bascule, pas d'ASC alternatif, pas de libération DMA, pas de promotion. Base main dc73ab6a055e6e02d991568b134ee5975b1c0a11 : P2k r4 149080 octets SHA256 ecfee351e9afbff95dfbfd16ab805b896e8c4889147f70136dd5b1c8dcbdee41, blob 0841bdc692006e7eb18ae5cc2b1df4a9fc4135f8. [Gate A r4](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45705955562) et [Gates B/C réelles](M19_S1_P2K_TRANSACTION_2026-11-25.md). LAST_GOOD L2b SHA256 a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc, ASC courant et ABK inchangés. Cible MC68020.

## Capacité : ne pas déstabiliser UNIT142

UNIT142 = 65276/65534, marge 258. UNIT207 = 10208 octets (10174 natifs + dispatcher 34), marge au compteur WORD 55326. Les trois stubs Sprite après UNIT207 ont un déplacement maximum de 10238, limite paire autorisée 32764 par pc16_displacements : marge calculée 22526 octets avant ajout de l'observateur. Cette estimation est vérifiée par recherche de frontière et refus du prochain mot ; le banc ajoute aussi 16384 octets de réserve uniquement dans un objet en mémoire et exécute des appels Sprite/Close réels sous CPU simulé dans les deux modèles. **Ne pas déplacer UNIT142 :** tous ses octets, y compris ancre locale, Close/End et reçus, restent strictement identiques. L'extension de récupération future doit rester dans UNIT207, à partir du point d'entrée Bank Free et de l'ancre persistante existants. Pas de nouveau pointeur de code dans la RAM persistante, pas de saut relatif entre unités indépendantes. Si une évolution nécessite de modifier Close/End au-delà de 258 octets, prévoir une restructuration séparée avec Gate A/B/C ; ne pas contourner le plafond.

## Observateur privé P2l-a

[Source](../src/native/m19_s1/M19_S1P2L_DMA_OBSERVE_MC68020.s), [builder](../tools/build_m19_s1p2l_a_in_memory.py), [banc](../tools/test_m19_s1p2l_a_gate_a.py). Reconstitution préalable P2k exacte depuis ses builders ; assemblage du même groupe207 plus un append source VASM -m68020, préfixe vérifié byte-exact. Tokens et 214 entrées inchangés, seules les distances des trois stubs après 207 changent. Aucune commande publique ni appel automatique du probe ; le banc le lance par son entrée native privée dans chaque modèle, les commandes existantes sont testées par leurs vrais stubs.

Le probe acquiert réellement le registre P2k avec p2h_enter (lookup seulement), exige reçu Close (root+12=0, lifetime+48=0), record épinglé flags=4, géométrie/longueur/absence de chevauchement, TypeOfMem Chip aux extrémités. Ouvre graphics.library V39+ indépendamment ; observe exclusivement V39/V40 avec structures mappées, ActiView=0, LOF/SHF=wait_forever, WAIT terminal, SPR2/3 neutres, slots 2/3 non réservés et descripteurs nuls ; contrôle les huit paires MOVE de copinit et les huit pointeurs SimpleSprites contre les plages privées Chip et record. Deux observations séparées par deux WaitTOF, stabilité des bases entre observations ; restitution de l'emprunt même sur refus, fermeture de sa référence graphics. Aucun ancien ViewPort déréférencé, aucune écriture dans Chip/Copper/record, aucun FreeSprite/FreeVec exposé. Le mapping TypeOfMem des extrémités ne prouve pas la taille d'allocation ni l'atomicité des structures OS ; les allocations privées sont épinglées par le protocole. Un résultat 1 signifie **observations compatibles seulement, DMA_FREE_PROVEN reste 0**. Il ne constitue ni une autorisation de réemploi ni un certificat de détachement du DMA physique. Les autres listes inactives et le pointeur interne du chipset ne sont pas prouvés par ces lectures.

| Retour privé | Signification |
| --- | --- |
| 1 | Deux observations idle compatibles, aucune libération |
| -131..-136 | Refus du registre P2k |
| -180 | Pas de reçu de fermeture / record absent |
| -181 | Record non mappé |
| -182 | Flags autres que 4 |
| -183 | Géométrie/allocation invalide |
| -184 | Gfx absent/incompatible |
| -185 | View/LOF/SHF/WAIT non idle |
| -186 | Layout Copper/table invalide |
| -187 | Référence privée ou canal occupé |
| -188 | Bases changées entre observations |
| -189 | Restitution du verrou refusée |

## Qualification et CI

Banc : tests CPU réels des instructions avec OS simulé ; garde read-only (pas d'alloc/free ni de nouvel appel Sprite), refus et retry, mutation pendant WaitTOF, ancien emprunt, 16 KiB de croissance testée, suite complète P2k + Pattern/SafePort/Bob et chaîne DB/IFF/Swap/capture. CI à relever ; aucun PASS P2l-a annoncé avant exécution. Deux défauts CI historiques P2k : exporteur strict utilisait la branche author-promoted pour P2i/j/k pourtant distincts de LAST_GOOD ; raccord aux vérificateurs exacts existants. Workflow Bob Auto Update attendait T06 au lieu de SPRITE_PUBLIC pour P2j/k ; correspondance ASC et SHA strictes rétablies. Aucun assouplissement ni changement natif associé ; requalification CI requise.

Suite après Gate A : définir un moyen de relever les observations sur la machine réelle sans inventer d'API publique ou livrer une autre Lib, vérifier les conditions de détachement effectif du DMA, puis seulement proposer une politique de réemploi/récupération. Réaffichage après Off et 100 cycles ne sont pas implémentés ici. Aucun changement de P2k validée, ni de LAST_GOOD.

## Suivi CI 26/11 — contrôles historiques

Sur d467a131d7628842d14c1368995db725f615a195 : Bob Auto Update [PASS 45865653766](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45865653766) ; export strict P2k/L2b et refus de monolithisation PASS dans Artifact integrity 45865653804. Ce dernier a ensuite échoué dans `test_current_input_state_offsets.py:77` : ancien test S1-P1f..i attendait 208 entrées et UNIT142 identique, alors que P2i/j/k ont 214 entrées et quatre spans Close/End autorisés. Le contrôle corrigé exige l'identité exacte de chaque variante, la comparaison de toutes les entrées héritées sauf UNIT142, la restauration des seuls quatre spans source-proven, les BRA.L et cibles dans le tail, puis l'égalité stricte du préfixe L2b et les sept LEA/huit cas négatifs historiques. Aucun assouplissement d'offset. Nouvelle CI à relever. P2l-a initiale 45865653811 encore en cours lors du relevé.
