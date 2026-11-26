# M19 S2a — changement d'image à chaud (premier composant source)

26/11/2026 — auteur « ok go » après clôture P2m et proposition S2a. Base protégée **P2m**, 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, [résultats Runtime/Compiler](M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md). Pas de nouvelle Lib installable, pas de changement ASC, token, AGSP v1, LAST_GOOD ou branche.

## Objectif S2a

Réutiliser l'appel existant `Aga Sprite(N,X,Y,I)` : déplacer si I est l'image courante, sinon demander le remplacement de l'image du même objet N, sans Off ni restitution des canaux. Pour la première tranche : écran P2m LowRes PAL 320x256x256, un seul objet actif, 16 pixels, 2 plans, hauteur identique, palette locale RGB24 identique, hotspot nul ; même banque sélectionnée et même génération. Les changements de géométrie, palette et multi-objets relèvent des jalons suivants. Refuser explicitement toute incompatibilité sans effacer l'image active. La sélection de cette première tranche est une proposition technique conservatrice, pas une nouvelle restriction permanente de l'API.

## Audit source

- [P2m public](../src/native/m19_s1/M19_S1P2M_PUBLIC_MC68020.s) refuse aujourd'hui un I différent au début du chemin actif. `p2i_active` impose posctldata=base+48. Le registre Exec, les canaux 2/3, le record de 40 octets et le descripteur SimpleSprite sont liés à la durée de vie P2m.
- [P2a préparation](../src/native/m19_s1/M19_S1P2A_CHIP_PREPARE_MC68020.s) alloue 48 octets d'en-tête puis deux zones de même taille `F=8+4*H`. La seconde est historiquement le blank. Le [retrait P2m](../src/native/m19_s1/M19_S1P2M_RETIRE_MC68020.s) n'en republie plus le pointeur : FreeSprite OS, neutralité des slots et copinit puis deux WaitTOF. Le [reclaim](../src/native/m19_s1/M19_S1P2M_RECLAIM_MC68020.s) libère l'unique base Chip et le record. Les deux zones peuvent devenir slots A/B sans agrandir la structure ni déplacer les chemins Close/End, **à condition de prouver la sécurité de la réécriture du slot inactif**.
- Source AmigaOS V40 [simplesprites.asm, ChangeSprite/MoveSprite](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/a/simplesprites.asm#L1048) blob `9795ab23dfb810f04511002fc05d20df48203027` : ChangeSprite remplace ss_posctldata puis tombe dans MoveSprite (coordonnées actuelles, pas de résultat booléen). DefaultMoveSprite écrit le descripteur SimpleSprite, les mots de contrôle et les deux mots du pointeur copinit de démarrage ; les écritures haut/bas ne constituent pas une publication atomique générale. Le test du pointeur seul ne prouve pas le retrait de toute référence DMA. Ne pas remplacer cette API OS par des écritures directes dans le Copper.
- UNIT142 n'a que 110 octets libres. Développement des chemins de publication et de validation exclusivement dans UNIT207 tant que possible. Exiger la conservation byte-exacte de UNIT142, des tokens et des stubs au prochain builder.

## Composant livré, non intégré

[AGSP_S2A_STAGE](../src/native/m19_s2/M19_S2A_FRAME_STAGE_MC68020.s) copie uniquement un bloc d'image P2a détaché et validé dans le slot opposé à ss_posctldata du bloc P2m. Le caller doit fournir les deux étendues exactes et épinglées, le verrou propriétaire, une allocation Chip réelle, et **un reçu indépendant de disponibilité du slot**. Le helper vérifie dimensions, longueurs/offsets exacts, pointeurs, non-chevauchement, état détaché, génération, palette et hotspot, contrôle/terminateur ; refuse toute mutation avant validation. D0/D1 = pointeur et taille ou zéro. Registres non volatils préservés ; aucun accès OS/DMA, aucun FreeVec, aucune modification de métadonnées. Aucun accroissement permanent de Chip RAM par rapport à P2m. Un scratch temporaire P2a est acceptable pour la première intégration ; son coût devra être mesuré et un cache de frames étudié ensuite.

[Tests MC68020](../tools/test_m19_s2a_frame_stage_cpu.py) : 1/16/255/256 lignes, les deux slots, 100 alternances avec reçus *simulés*, intégrité du slot actif, de l'en-tête, du bloc source et gardes, écritures exactes bornées, ABI, refus de pointeurs/longueurs/overlap, de palette/hauteur/génération/hotspot incompatibles et de contrôles/terminateurs non nuls. [CI source seule](../.github/workflows/m19-s2a-frame-stage.yml). Aucun PASS natif revendiqué avant résultat CI ; ce composant ne teste ni la publication ni la sûreté DMA réelle.

## Étape suivante : intégration S2a

1. Authentifier l'objet actif, contexte/owner, sélection et génération. Préparer le nouveau frame via P2a sur une banque encore stable (vérification AGSP_I_EXPECT avant et après). Refuser avant publication si le contrat n'est pas satisfait.
2. Prouver l'absence de référence au slot de staging : premier slot jamais publié, puis receipt de transition du slot précédent. Appuyer le protocole sur des références OS stables, ViewPort/ActiView appropriés, table SimpleSprites et pointeurs startup exacts avant/après une ou plusieurs frontières de frame à qualifier. Le fence P2m de neutralité après FreeSprite ne peut pas être transposé mécaniquement à une republication active. Pas de libération ni de réécriture d'un slot incertain ; garder possibilité de Off/Close P2m et refuser un nouveau changement si le reçu manque. Ne pas introduire un état que la retraite UNIT142 ne saurait traiter.
3. Après staging, publier par ChangeSprite sur le **même** SimpleSprite, MoveSprite si déplacement, confirmer publication et retour API. Ne modifier le numéro d'image du record qu'après confirmation. Préserver les 100 cycles P2m, la fermeture et le traitement des refus ; aucun Swap implicite ni FreeSprite par changement de frame.
4. Gate A complète sur les deux layouts AP20 : 100 alternances, deux slots, vérification d'adresse et pixels exacts, palette/hauteur incompatible, banque modifiée/effacée, refus d'allocation, référence tardive, échec de confirmation et cleanup, Off/Close/End, régressions Bobs/Pattern/SafePort/DB/IFF/capture. Vérifier budget PC16 et reproduction exacte. Gate B/C : deux images visuellement distinctes de même palette, animation sans Off, mouvement continu, réaffichage et fermeture actifs, absence de fuite nette. Gate D séparée. Ne livrer qu'après Gate A et autorisation de bascule.

P2m reste le seul binaire de test actif. Rien n'est installé par ce jalon.

## Gate A composant — PASS

[CI 45896382931](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45896382931), source `3362f71dcf7519a2d61ade2b1a284c708d252e10`, VASM épinglé, MC68020 Unicorn. **148 cas PASS**, dont 100 alternances avec reçu simulé, vérification des écritures et de l'ABI ; 9 autotests de politique CPU et 17 de livraison PASS. Vérification stricte de la paire P2m avant/après PASS. Documentation/roadmap [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45896382933), politique CPU/livraison [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45896382947). Aucun nouveau binaire installé.

**Point de sécurité pour la publication (pas encore implémentée) :** le MoveSprite V40 écrit le mot bas du pointeur copinit puis le mot haut. Pour la première intégration, ne permettre une bascule que si les deux pointeurs de frame partagent le même mot haut (ou après preuve d'une publication sûre à la frontière de frame). Cette restriction évite un pointeur hybride lors des deux écritures mais ne remplace pas le contrôle des références OS et le fence de réutilisation. Tester une allocation à cheval sur une frontière de 64 Kio ; refus sans destruction de l'image active. Le composant de staging seul ne publie aucun pointeur et n'a pas ce contrôle. Pas de réutilisation du slot précédent tant que la transition n'est pas confirmée. Intégration native publique et Gate A complète S2a encore à faire ; B/C/D non testées.


## Intégration publique suivante

Voir [S2a-P1](M19_S2A_PUBLIC_FRAME_CHANGE_2026-11-26.md), sources et Gate A publique, pas de bascule canonique.
