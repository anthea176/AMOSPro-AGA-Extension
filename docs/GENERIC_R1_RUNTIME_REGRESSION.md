# Generic R1 0.5.0 — défaut de couleurs runtime

Diagnostic complété pendant l'image en pause : les plans 0..6 sont exacts,
le plan 7 est nul et les 256 couleurs du ColorMap sont exactes.
Voir [le correctif R2 et ses tests](GENERIC_R2.md). Le repli R5 décrit ci-dessous
précède la publication du candidat expérimental R2.

Retour utilisateur : le chargement paraît fonctionner, mais les couleurs sont
incorrectes sur toutes les images. Capture fournie pour Clown. Le binaire du dossier
Amiga monté DH6 a le SHA256 attendu de R1 :
`b9bcf0efc444edc6d284988feabebcc33cd7ad88b21f1231ff155380f1b5941a`.

R1 n'est pas validé. Le candidat courant est restauré depuis R5 0.4.6 ; l'archive
R1 est conservée intacte et sa promotion automatique est désactivée.

## Observation précise

Une comparaison des pixels de la capture au décodage de Clown donne 63941 pixels
sur 64000 compatibles avec `CMAP[index & 127]`, avec une tolérance de 5 niveaux RGB
pour le filtre/capture WinUAE. Exemples : 128 apparaît comme 0, 255 comme 127.
Cela oriente vers le bit de poids fort absent ou une duplication de demi-palette,
et non vers une simple permutation des composantes RGB.

La table générée pour LoadRGB32 et sa convention A0=ViewPort/A1=table sont conformes
à l'Autodoc. Ce fait ne prouve pas que l'état affiché est correct après Swap.
Les tests CPU simulent les appels système ; ils ne pouvaient pas valider cet état.

Une lecture de mémoire WinUAE après fermeture retrouve des fragments des plans,
mais l'état extension est déjà remis à zéro : cette mémoire libérée ne constitue
pas une preuve exploitable du bitmap ou de la palette au moment de l'affichage.
La vérification doit se faire pendant l'image, émulation en pause.

## Suite

Comparer en lecture seule les 8 plans actifs, le ColorMap et l'état d'affichage
pendant la capture. Aucun changement du décodeur ni de la palette ne doit être
présenté comme un correctif confirmé à partir de cette seule capture.

Source faisant foi : `tools/build_m5_generic.py` et `tools/m68k_emit.py`.
Voir aussi `src/README.md` : les `.s` historiques ne sont pas le source complet de R1.
