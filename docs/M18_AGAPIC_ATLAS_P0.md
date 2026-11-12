# M18 — AGAPIC atlas, CBlock AGA, équivalent F 16 Icon

**Ouverture le 12 novembre 2026 — uniquement sur main.**
**Statut : P0 modèle hôte expérimental.** Il ne s'agit PAS d'une nouvelle
commande AMOS, d'une nouvelle bibliothèque installable ni d'une Gate A 68000.

**Référence inchangée : R59 v0.13.4 LAST_GOOD**, 32 984 octets,
SHA256 00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d.
Aucun binaire alternatif, aucun programme ASC actif, aucune nouvelle branche.

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

**Point historique avéré :** le manuel AMOS Pro documente Get Cblock /
Put Cblock et un arrondi de X et de la largeur à des multiples de
8 pixels. Un CBlock AGA moderne devra choisir explicitement
**arrondi compatible ou coordonnées exactes**, sans annoncer une
compatibilité binaire avec les blocs AMOS :
https://amospromanual.dev/07-07-icons-and-blocks.html

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
2. **P1 R60** : choisir une unique signature native de dessin
   sous-rectangle ; partir de R59 avec les fonctions
   unwrap_native_parts_v2 / wrap_native_ap20_v2.
   Tests CPU 68000, ABI, Safe, pixels/masque, mémoire, AP20 et
   relocalisation AVANT de publier une candidate.
3. **B/C R60** : seulement après Gate A, un seul binaire de
   travail dist/AMOSPro_AGA.Lib et un seul ASC tests/current.
   WinUAE interprété puis un NOUVEL exécutable Compiler.
4. **CBlock / F 16 Icon** : audits et contrats distincts avant code ;
   AUTO seulement après mesures comparatives.
5. **Promotion** : après Gates A/B/C, régression complète sur
   HEAD exact et accord exprès de l'auteur.

**Pendant l'étude, la R59 LAST_GOOD et les tests passés restent intacts.**
