# M18 — AGAPIC atlas, CBlock AGA, équivalent F 16 Icon

**Ouverture le 12 novembre 2026 — uniquement sur main.**
**Statut du jalon P0 : modèle hôte expérimental.** Le développement natif R60 a ensuite reçu sa **Gate A CPU PASS** ; [rapport R60](M18_R60_IMAGE_REGION.md). Le P0 Python seul ne constitue pas une Gate native.

**Référence inchangée : R59 v0.13.4 LAST_GOOD**, 32 984 octets,
SHA256 00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d.
R59 reste la référence `LAST_GOOD` protégée. R60 est maintenant la seule candidate dans `dist/AMOSPro_AGA.Lib` ; son seul ASC actif est `tests/current/M18_R60_IMAGE_REGION_01.asc`. `main` exclusivement.

## 1. Première tranche : atlas dans une banque AGAPIC v1 inchangée

**Hypothèse rétrocompatible à qualifier :** une image AGAPIC v1 peut
servir d'atlas, découpé en sous-images par rectangles source
(SrcX, SrcY, Width, Height). Une grille régulière peut désigner des
frames par index zéro en ordre ligne-major **dans le modèle hôte**.
On évite ainsi de changer immédiatement le format binaire, le codec RLE,
l'en-tête de la banque DATA et les commandes R59 existantes.

L'animation est pilotée par le programme utilisateur (choix de frame
et position) : **aucun timer, VBL, swap ou état d'animation caché**.

- Source AGAPIC v1 : RLE **par ligne** en groupes planaires de **16 pixels**,
  profondeurs 1 à 8, source DATA possiblement en Fast RAM ; CPU lit
  et dessine dans le back buffer AGA privé en Chip RAM.
- Opaque : la couleur 0 est visible. Masqué : masque indépendant 1 bit,
  0 conserve la destination, 1 dessine le pixel. L'index couleur 0
  n'est **jamais automatiquement transparent**.
- Source : rectangle entièrement compris dans l'atlas. Toute dimension
  nulle, débordement, mauvais mode, mauvais type de banque ou RLE corrompu
  doit être refusé **avant tout pixel modifié**.
- Destination : clipping sur les quatre côtés, même avec abscisse
  non alignée sur 16 pixels ; dessin entièrement hors écran = appel
  valide, mais aucun pixel modifié.
- Profondeur source = profondeur destination. Aucun changement de palette,
  de synchronisation Safe/Disp, de buffer actif ni d'écran implicite.
  Le programme reste responsable du double buffering.
- Aucun nom, paramétrage ou numéro de token AP20 n'est encore arrêté.
  Une future API native devra être décidée avant son implémentation.

### Sources et tests hôte (aucune Gate native)

- tools/m18_agapic_atlas_model.py : sous-rectangle ou frame de grille,
  décodage progressif des lignes via **le vrai codec AGAPIC v1**,
  rendu planaire dans un back buffer simulé **sans décompresser
  l'atlas en entier**.
- tools/test_m18_agapic_atlas_model.py : comparaison pixel à pixel
  indépendante, profondeurs 1/2/4/8, cellules de largeur 19 non alignées,
  modes opaque/masqué, clipping et origines X/Y négatives, sentinelles
  mémoire, refus sans écriture.

**P0 ne prouve pas** : l'ABI AP20, l'accès CPU réel à Fast/Chip,
les performances 68000/68020/030/040/060/PiStorm, ni les Gates
A 68000, B AMOS interprété, C AMOS Compiler, D Amiga physique.
Le nombre de pixels écrits retourné par le modèle n'est pas un
contrat de valeur de retour d'une commande AMOS.

## 2. CBlock : capture et restauration du fond

Objectif : capturer une zone du **back buffer AGA privé** et la
restaurer au même endroit ou ailleurs pour dialogues et animation.
Évaluer **planar brut**, **RLE AGAPIC**, et **copie Blitter depuis Chip**,
en séparant coût de capture, stockage Fast/Chip, staging, dessin
et libération. Ne pas présupposer le format de compression le plus rapide.

Capture : contrôler l'intégralité du rectangle avant allocation ;
banque/identifiant déjà occupé = refus sans destruction ; aucune
modification de palette ou de pixels ; pas de Swap implicite.
Restauration : placement, clipping, Safe, double buffering et
propriété du stockage à contractualiser.

### Décision de l'auteur — CBlock au pixel près (12/11/2026)

**Contrat fonctionnel retenu pour M18 : capture et restauration aux
coordonnées et dimensions exactes, à 1 pixel près.** Aucun arrondi
silencieux de X, Y, largeur ou hauteur pour rendre l'opération plus
rapide. Les pixels hors rectangle doivent rester inchangés, y compris
les bits du même mot planaire en bordure. L'entrée de capture doit
refuser entièrement un rectangle hors écran avant toute allocation ;
les règles de clipping de la restauration seront explicitées avant
l'API native. Ne pas modifier la palette, changer de back buffer,
appeler Swap ou attendre un VBL implicitement.

**Deux chemins internes à comparer à résultat graphique identique :**

- **Chemin aligné 16 pixels** : lorsque source, destination et largeur
  s'y prêtent, copies par mots planaires de 16 bits et/ou Blitter
  Chip→Chip. Éviter les masques et décalages inutiles, sans supposer
  que ce chemin sera toujours plus rapide.
- **Chemin général au pixel près** : positions X non alignées, largeurs
  quelconques et bords ; décalages, masques de premier/dernier mot et
  préservation exacte des pixels voisins. Le résultat ne doit pas
  dépendre de l'alignement ; mêmes conditions Safe et mémoire.

Le chemin effectivement plus rapide sera sélectionné **après mesure**
sur un corpus identique : capture + restauration, aligné/décalé,
rectangles petits/grands, opaque et masqué si retenu, CPU Fast/Chip
contre Blitter Chip→Chip en incluant les coûts de préparation, attente
et allocation. Mesurer séparément les sous-étapes et le total.
Comparer aussi, à périmètre identique, AMOS `Screen Copy` et notre
`Aga Blit Copy`. Le benchmark R57 préexistant donnait 35 contre
69 ticks sur un petit rectangle aligné 64×48 : cela interdit de
déclarer le Blitter plus rapide sans preuve.

**Point historique distinct :** le manuel AMOS Pro documente
`Get Cblock`/`Put Cblock` et un arrondi horizontal à des multiples
de **8 pixels**. Cela correspond à un octet par bitplane, tandis que
16 pixels correspondent à un mot de 16 bits, mais **la cause précise
de l'arrondi AMOS n'est pas démontrée**. Notre CBlock AGA n'imposera
pas cette convention et ne prétendra pas être compatible au niveau
binaire avec les blocs AMOS :
https://amospromanual.dev/07-07-icons-and-blocks.html

**Statut : contrat fonctionnel approuvé, pas d'implémentation,
pas de nouvelle commande AP20 ni de benchmark CBlock exécuté.**

## 3. Équivalent fonctionnel F 16 Icon

**Audit original non terminé.** La roadmap mentionne F 16 Icon,
mais le dépôt et les références actuellement disponibles ne prouvent
pas sa **syntaxe précise**, l'extension propriétaire, le format de
banque d'icônes, les masques, la palette, les dimensions et
conventions d'alignement. Ne pas inventer son ABI ou réutiliser
le nom comme si l'extension était compatible.

Objectif fonctionnel : même résultat graphique sur le back buffer AGA
via deux voies indépendantes :

- **CPU** : source en Fast RAM ou Chip RAM, écriture CPU vers Chip RAM.
- **Blitter** : source **obligatoirement en Chip RAM**, ou staging
  Fast→Chip explicite, coût inclus dans les mesures. Un Blitter
  ne peut pas lire directement la Fast RAM.

**AUTO uniquement après benchmarks**, pas sur une hypothèse de vitesse
du 68040/060/PiStorm ni sur une mesure PC.

## 4. Benchmark futur : protocoles de comparaison

| Scénario | Variables |
|---|---|
| Dimensions | 16×16, 19×11, 32×32, 64×48, 95×72 |
| Profondeur | 1/2/4/8 plans |
| Alpha | opaque et masque indépendant (index 0 visible ou masqué selon masque) |
| Position | X aligné/décalé, clipping L/R/H/B, hors écran |
| Processeur | 68000 puis 020/030/040/060/PiStorm quand disponibles |
| Mémoire | résidence Fast/Chip réellement mesurée ; consommation des deux |
| Temps | chargement, préparation Chip, dessin, attente Blitter, total par frame |

Pas de nombre de FPS promis sans mesure WinUAE contrôlée ou matériel.

## 5. Prochaine tranche, sans promotion automatique

1. **P0** : modèle et tests hôte AGAPIC v1 / atlas (en cours).
2. **P1 R60** : signature `Aga Image Region(Bank,SrcX,SrcY,Width,Height,X,Y,Mode)` et moteur 68000 depuis R59 avec `unwrap_native_parts_v2` / `wrap_native_ap20_v2`, **Gate A CPU/CI PASS sur 86 cas** ; [rapport R60](M18_R60_IMAGE_REGION.md). Gates WinUAE B/C en attente.
3. **B/C R60** : seulement après Gate A, un seul binaire de
   travail dist/AMOSPro_AGA.Lib et un seul ASC tests/current.
   WinUAE interprété puis un NOUVEL exécutable Compiler.
4. **CBlock / F 16 Icon** : audits et contrats distincts avant code ;
   AUTO seulement après mesures comparatives.
5. **Promotion** : après Gates A/B/C, régression complète sur
   HEAD exact et accord exprès de l'auteur.

**Pendant l'étude, la R59 LAST_GOOD et les tests passés restent intacts.**
