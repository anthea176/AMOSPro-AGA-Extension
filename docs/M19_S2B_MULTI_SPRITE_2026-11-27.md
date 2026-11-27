# S2b — plusieurs Sprites matériels indépendants

27/11/2026, autorisation auteur « oui lanimation est ok on peux continuer ». Parent exact S2a-P1, [A/B/C PASS](M19_S2A_RUNTIME_COMPILER_2026-11-27.md), Lib 151164 octets SHA256 `1d13ff815aa3b448e420f6783dbac967c03efca2fbb65932e783ec72502e58d2`, blob `190504fd46494224c6c32e20f17dcc3d6a027684`. Source officielle builder `tools/build_m19_s2a_in_memory.py` sur main. Cible MC68020+. Aucun changement de Lib active, ASC, ABK ou LAST_GOOD.

## Première tranche proposée

Conserver la réservation d'une paire par objet : canaux 2/3, 4/5, 6/7, soit **jusqu'à trois objets 16px/3 couleurs opaques**, sous réserve de disponibilité OS. 0/1 exclus. Seul l'even est publié ; l'odd est réservé (pas attaché, pas de descripteur publié) comme dans S2a, pour ne jamais manipuler un voisin potentiellement attaché. Ce plafond de trois est conservateur, pas la limite matérielle AGA finale. Une future tranche pourra exploiter davantage de canaux après preuve de la coexistence. Ne pas ajouter de token : ID logique 1..64, pas numéro du canal. Rechercher ID existant avant d'allouer une paire. Même ID = déplacement/changement d'image ; nouvel ID = nouvel objet ; Off ciblé, Bank Free ciblé par banque, Close/End tous les objets. Pas de nouveau Swap implicite. Ne pas modifier automatiquement les palettes. Avec les bases de palette 16/16 validées dans p2i_palette, groupes envisagés 21..23, 25..27, 29..31 ; vérifier par source OS et qualification réelle. La sélection doit tenir compte des couleurs exactes ; ne jamais remplacer la palette du fond à l'aveugle.

## Point critique de l'architecture

Le root v3 P2m contient une seule adresse de record (40 octets) et les preuves owner/State/Screen/Task. Le chemin Close/End dans UNIT142 appelle le retrait d'un seul record et efface le root. UNIT142 a 110 octets libres, donc impossible d'ajouter des copies de routines par objet. Avant toute intégration multi-objet, définir un registry multi-record borné et versionné (même nom privé, schéma incompatible refusé), une preuve de propriété distincte pour chaque paire, et **un chemin Close/End qui parcourt tous les records**. Une erreur tardive doit conserver les records non retirés ; pas de libération en bloc ni de perte de reçu. Revoir/recompiler depuis les sources officielles du builder, compacter/mutualiser les routines UNIT142 et UNIT207, préserver les stubs/tokens et la réserve PC16. Ne pas simplement transformer le premier pointeur de v3 en liste en laissant le cleanup P2m l'interpréter. Gate A intégrée obligatoire avant toute activation, B/C/D distinctes.

## Travaux

1. Généraliser la retraite de paire et ses vérifications OS, composant indépendant sans publication DMA.
2. Registry borné, sélection paire libre et palette compatible, acquisition avec rollback exact. Ne jamais déduire un reçu de possession des seuls bits de réservation OS.
3. Raccorder les chemins publics Show/Move/Change/Off/Bank Free et le Close/End à la nouvelle structure. Rejouer S2a et P2m sur les deux modèles AP20 et les régressions 2D.
4. Préparer une campagne visuelle avec trois objets distincts et palettes différenciées, animation indépendante, Off au milieu, refus saturation, re-show, Close actif, relances et mémoire nette. Pas de livraison sans Gate A exacte.

Source OS : [V40 simplesprites.asm](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/a/simplesprites.asm), blob `9795ab23dfb810f04511002fc05d20df48203027`, GetSprite et FreeSprite, MoveSprite/ChangeSprite. GetSprite réserve un canal spécifique et écrit ss_num, FreeSprite neutralise seulement le canal ciblé dans la table et copinit, MoveSprite peut inspecter le voisin odd lorsqu'il publie un canal pair. Aucun accès matériel direct proposé.
