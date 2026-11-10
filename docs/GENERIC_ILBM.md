# Generic ILBM R1 — 0.5.0

Base auditée : main `9d9d06924377d8f27f18d067e72968a441aa5ecb`.
Base binaire exclusive : R5 0.4.6, SHA256
`33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715`.
R5R1/R5R2 ne sont ni importés ni utilisés.

Candidat expérimental : `dist/experimental/AMOSPro_AGA_M5_v0.5.0_GENERIC_R1.Lib`.
Même contenu dans `dist/AMOSPro_AGA.Lib`, **6436 octets**, SHA256
`b9bcf0efc444edc6d284988feabebcc33cd7ad88b21f1231ff155380f1b5941a`.
Ce candidat a passé les contrôles structurels et CPU, **pas la validation visuelle AMOS**.
R5 et LAST_GOOD sont inchangés. Au premier échec sur une image auparavant fonctionnelle,
restaurer le candidat courant depuis l'archive R5 ; conserver le candidat rejeté pour comparaison.

## Inventaire réel

[Tableau des 41 fichiers](ILBM_INVENTORY.md) et [données complètes](ILBM_INVENTORY.json).
Recherche récursive insensible à la casse, incluant `.Iff`, sans liste de noms prédéfinie.
Les 41 FORM sont ILBM. Toutes les images possèdent BMHD, CMAP et BODY ; deux n'ont pas CAMG.
39 BODY ByteRun1 et 2 RAW. Profondeurs présentes : 3, 4, 5, 6, 8.
CMAP : 8, 16, 32, 64, 256 entrées. Masking=0 partout.
LoRes, HiRes, entrelacé, EHB et overscan sont présents ; aucun HAM6/HAM8 dans le dépôt.
Dimensions : 320×200, 320×256, 640×256, 640×400, 640×512,
704×566, 724×482 et 736×482.
Chunks inconnus rencontrés : GRAB, DPPS, CRNG, DRNG, DPI espace.
Leurs longueurs et paddings sont consignés individuellement dans le JSON.

Deux points observés, sans exception de code par fichier :

- Un FORM est suivi de 820 octets supplémentaires : ils ne font pas partie de l'image.
- Un CAMG ancien vaut $4000 : le bit SPRITES est filtré selon la spécification.
  Un autre fichier a une hauteur de 512 avec un CAMG non entrelacé : celui-ci est conservé,
  sans déduire arbitrairement LACE de la hauteur ; le défilement permet d'explorer l'image.

## Causes établies et delta

R5 conservait un scanner/décodeur spécialisé : largeur 320, rowBytes 40,
ByteRun1 seulement, seuils de hauteur/profondeur, boucles guidées par la destination.
Il ne validait pas suffisamment la compatibilité entre l'image et le bitmap.
Open imposait des bornes 160..1280/160..512, une largeur multiple de 16,
et refusait EHB/HAM. PicInfo pouvait retourner un champ avant d'avoir validé la fin du FORM.
Le test prenait le nombre d'entrées CMAP pour la profondeur écran, ce qui n'est pas général.

La mauvaise palette R4 est documentée dans M5_STATUS. R5 utilise LoadRGB32 pour les
petites palettes. Le nouveau candidat conserve ce choix d'API et l'étend à une table
complète, indices explicites 0..N-1, RGB8 répliqué en RGB32. Il ne cherche pas à reproduire
les garde-fous R5R1/R5R2. Leur rejet runtime reste acquis ; aucun nouveau diagnostic
ne prétend établir rétroactivement la cause exacte de R5R2.

Trois segments publics doivent évoluer ensemble : Open (géométrie/modes),
PicInfo (métadonnées fiables), Iff Load (validation et décodage). C'est nécessaire pour
le corpus HiRes/overscan/EHB réellement trouvé. Les autres segments sont inchangés.

## Architecture et ABI

Inspect → Validate → Prepare screen → Decode → Apply palette → Present.
Le test inspecte, ouvre l'écran et alloue Double Buffer. Le loader relit et revalide
le fichier sélectionné : une modification du fichier entre PicInfo et Load ne contourne
pas les contrôles de compatibilité.

- `read_file` : chaîne AMOS, DOS Open/Read, FORM borné, allocations contrôlées.
- `inspect` : scan intégral, padding, propriétés uniques, types/tailles et métadonnées.
- `validate_screen` : état, dimensions/profondeur/mode, bitmap, stride, rows, pointeurs.
- `decode` : prévalidation complète sans écriture, puis même décodeur avec écriture.
- `prepare_palette` : allocation de la table RGB32 avant les écritures bitmap.
- `palette` : LoadRGB32 puis WaitTOF ; pas de reconfiguration à chaud du ViewPort.
- `cleanup` : ferme le fichier, libère table/FORM/nom, ferme DOS même après échec partiel.
- Present reste `Aga Swap`, inchangé.

Les helpers sont générés depuis une source commune, localement dans chaque segment
qui en a besoin. Aucune dépendance BSR inter-segment n'est introduite pour le compilateur.
Les branches/LEA sont résolues par labels, jamais par un scan heuristique d'opcodes.

### Registres live

L'ancien scanner R5 réutilisait D0/D1 comme calculs de borne/avancement,
D2 comme taille de chunk, D3 comme ID, D4 comme taille FORM puis pointeur de cleanup,
D5 comme taille CMAP puis index palette/ligne, D6 comme indicateur BMHD puis offset ligne,
D7 comme taille BODY puis compte palette. A0/A1 parcouraient les chunks ;
A2/A4 portaient CMAP/BODY ; A3 portait FORM puis BitMap ; A6 alternait payload/base système.
Ces rôles évoluaient selon la phase : ajouter un helper sans sauver les valeurs live
était dangereux. Le nouveau loader n'insère pas de helper dans cette ancienne séquence.

Entrées publiques : contrat GetP conservé ; chaîne dans D3 pour Load ; dernier argument
dans D3 et chaîne via (A3)+ pour PicInfo. À l'entrée A5 est la base AMOS.
La zone extension est capturée depuis 456(A5), puis A5 devient un contexte temporaire
sur la pile (128 octets), restauré à la sortie. Aucun état global parallèle n'est créé.
D3 est le résultat ; D2=0. Les autres registres sont restaurés comme dans R5.

Contrat commun de **chaque helper** :

| Helper | Entrées dans le contexte A5 | Sorties |
|---|---|---|
| read_file | STR | ressources CSTR/DOS/FH/FORM, SIZE |
| inspect | FORM, SIZE | BMHD, CMAP, NC, BODY, BS, W/H/depth/mask/compression/rowBytes/CAMG/mode |
| validate_screen | STATE et métadonnées | SCREEN, BITMAP, STRIDE |
| decode | BODY/BS, métadonnées, WRITE, bitmap si WRITE=1 | validation ou pixels |
| prepare_palette | CMAP, NC | PTABLE allouée et remplie |
| palette | PTABLE, SCREEN, STATE | ColorMap appliquée et synchronisée |
| cleanup | ressources acquises | ressources libérées |

Pour chacun : D0=1/0 ; **modifiés : D0 et CCR** ; **préservés : D1-D7/A0-A6** ;
CCR final issu de TST.L D0 (Z=0 succès, Z=1 échec). A7 équilibré.
Le wrapper public n'interprète pas un CCR accidentel : il teste explicitement D0.
Le helper local Open pour les tags prend A1=fin de taglist, ajoute AutoScroll/TAG_DONE,
rend D0=0, avance A1, préserve D1-D7/A0/A2-A6, CCR Z=1 et A7 équilibré.

### Format et limites explicites

RowBytes = ((width+15)//16)*2 ; stride destination lu dans BitMap, jamais supposé égal.
Ordre ligne puis plan. RAW et ByteRun1 (y compris NOP) sont bornés par ligne et BODY.
Les plans de masque sont consommés ; le chargement plein écran ne fait pas de compositing.
L'image entière est validée avant la première écriture bitmap/palette.
Le format absent du corpus sans CMAP est refusé proprement, sans inventer de palette.
Les images 24 plans, lasso, dual playfield, compression inconnue et CAMG étendu incohérent
sont refusés. Aucun de ces cas n'est présent dans le corpus.
HAM6/HAM8 ont le chemin matériel CAMG et des tests synthétiques CPU, mais aucun PASS visuel.
EHB affiche les couleurs dérivées par le matériel ; le CMAP est transmis tel quel.

Open accepte les dimensions positives représentables par les WORD signés d'Intuition
(1..32767), profondeur 1..8 via une capacité de palette puissance de deux.
La disponibilité du mode et la mémoire Chip restent décidées par AmigaOS ; Open=0
si l'écran ne peut pas être alloué. Le CAMG étendu est conservé ; les anciens bits
non destinés à un ModeID sont filtrés. CAMG absent/0 utilise le moniteur par défaut,
sans imposer PAL ou NTSC. AutoScroll ne change ni CAMG ni dimensions du bitmap.

### Aga Pic Info

Champs 0..5 compatibles : largeur, hauteur, profondeur, entrées CMAP, compression,
**CAMG brut** (0 absent). Deux champs supplémentaires, sans nouveau token :
6 = ModeID utilisable après filtrage legacy ; 7 = capacité écran `2^depth`.
Retour -1 sur fichier invalide/non pris en charge ou champ hors 0..7.
PicInfo valide toute la structure, mais ne décompresse pas BODY.

## Reproduction et résultats

```text
python -m pip install capstone==5.0.9 unicorn==2.1.4
python tools/validate_ilbm.py
python tools/build_m5_generic.py
python tools/test_m5_generic.py
python tools/build_m5_generic.py --promote
python tools/verify_artifacts.py
python tools/check_no_blocking_waits.py
```

Sans `--promote`, le builder ne touche pas à la Lib courante.
Avec `--promote`, il exécute les tests CPU avant remplacement.
SHA256 et taille attendus sont figés dans le builder ; double construction identique,
audit AP20 sans erreur, tables GetP/tokens inchangées, segments non ciblés identiques.
L'ancien helper R5 reste présent, inchangé et non appelé ; aucun token diagnostic ajouté.

[Résultats CPU](GENERIC_CPU_TESTS.json) : les **instructions binaires réelles** tournent
en modèle 68000 dans Unicorn. DOS/Exec/graphics/Intuition sont simulés ; D1/A0/A1 sont
volontairement écrasés après chaque appel système. Contrôle de la pile et des registres
publics, ressources libérées, toutes les lignes/plans comparés au décodeur Python,
strides plus grands que rowBytes, padding destination intact, tous les indices CMAP.
Les 8 champs PicInfo et les tags d'ouverture sont vérifiés sur chaque fichier.
41/41 images PASS ; 127 fichiers malformés, 5 mismatches, 3 échecs d'allocation et
12 cas synthétiques (RAW/ByteRun1/masques/HAM/EHB/1 et 8 plans/NOP final) PASS.
Les 11 tests historiques R6A passent ; aucun Wait/WaitPort interdit.

## Validation runtime restante — obligatoire

1. Exécuter `tests/current/M5_GENERIC_ILBM.asc` pour les 41 images, sous AMOS365
   interprété : Open → DB → Load → Swap → géométrie/pixels/palette → Close.
   Vérifier aussi l'autoscroll, les moniteurs PAL/NTSC disponibles, l'EHB et le retour
   à l'éditeur sans Guru/hang après plusieurs sélections.
2. Compiler ce même test, puis refaire le lot et les erreurs fichier/écran/allocation.

Une fenêtre WinUAE était ouverte pendant le développement, mais l'autorisation Computer
Use a expiré avant capture. Aucune validation visuelle de ce candidat n'a été obtenue.
Un retour 1 dans l'émulateur CPU ne vaut jamais PASS visuel ni validation AmigaOS.

## Références

- [Spécification ILBM, BMHD/CMAP/CAMG/ByteRun1](https://wiki.amigaos.net/wiki/ILBM_IFF_Interleaved_Bitmap).
- [Structures/tags Intuition V39](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0602.html).
- [Écrans Intuition, overscan et AutoScroll](https://wiki.amigaos.net/wiki/Intuition_Screens).
- Les offsets BitMap/Screen ont aussi été recoupés avec les includes Commodore du
  checkout AMOS365 local ; les LVO utilisés sont ceux des builders R5 déjà validés.
