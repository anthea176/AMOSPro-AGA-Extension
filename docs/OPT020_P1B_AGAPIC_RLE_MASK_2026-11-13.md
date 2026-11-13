# OPT020 — P1b : groupe AGAPIC multiplan, masque et RLE

**Date : 13 novembre 2026. Statut actuel : prototype **PASS** dans Musashi sur 68EC020/68020, [CI dédiée 43490985555](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43490985555).** Ce développement reste **autonome**, sans nouvelle bibliothèque ni nouvelle commande AMOS.

[Émetteur natif 68020](../tools/opt020_p1b_multiplane_emit.py) · [Répartiteur de régions et fallback](../tools/opt020_p1b_region.py) · [Banc natif](../tools/test_opt020_p1b_native.py) · [Workflow dédié P1/P1b](../.github/workflows/opt020-p1.yml)

## Périmètre du prototype

L'ancien sous-noyau P1 copiait un groupe opaque d'un seul plan. **P1b** propose un nouveau noyau **68020/68EC020** capable de traiter **1 à 8 plans** en boucle avec les pointeurs de plans indépendants (sans supposer la contiguïté des bitplanes Intuition).

Contrat machine autonome : `A0` = mots source consécutifs, `A1` = table de pointeurs de destination par plan, `D0` = décalage 0..7, `D2.w` = masque effectif 16 bits, `D6.w` = profondeur 1..8. Le noyau combine `BFEXTU` source, `BFEXTU` destination et `BFINS` après fusion `(source & mask) | (old & ~mask)`. **L'index couleur 0 reste opaque en mode 0** ; le masque indépendant est pris en compte seulement en mode 1. Les bits hors champ ne doivent pas changer. `A3`, `D0`, `D2`, `D5` et la pile sont contrôlés, mais il ne s'agit **pas** de l'ABI AP20.

Le répartiteur hôte s'appuie sur le **format AGAPIC v1 exact** ([source](../tools/m16_agapic.py)) : lignes RLE, paquets répétés/littéraux, découpe d'atlas, largeur partielle, masque facultatif, mode opaque/masqué et profondeur 1/2/4/8. Toute la banque est validée **avant le moindre dessin**. Les groupes source de 16 pixels entièrement visibles et dont le champ BFINS reste **dans la ligne bitmap** empruntent le noyau natif. Les groupes tronqués par le rectangle source, le bord écran ou la longueur physique de ligne empruntent un **fallback scalaire borné**. Ce comportement protège le premier et le dernier octet de chaque ligne, même pour X non multiple de 8.

### Limite de périmètre importante

**Le décodeur RLE et la sélection du chemin restent en Python hôte.** Seule la boucle d'écriture des mots planaires est réellement exécutée en opcodes **68EC020/68020** dans Musashi. C'est une preuve d'intégration expérimentale du **sous-noyau**, **pas encore une `Aga Image Region` native 020 complète**. Aucune mesure de vitesse sous WinUAE ou sur Amiga physique.

## Validation effective du banc (PASS)

- Motifs aléatoires et extrêmes, masques pleins/vides/alternés, offsets X 0..7, profondeurs 1/2/4/8 ; décodage Capstone des instructions 020 et exécution réelle sur les **deux types CPU**.
- Pointeurs distincts par plan, octets de garde placés de part et d'autre des zones écrites, contrôle de la pile, des registres non autorisés et de la source.
- Images de 65×11 pixels (dernier groupe partiel) compressées en **RLE literal + repeat**, sous-rectangles et positions incluant clipping négatif, droite/bas et hors écran ; comparaison à l'oracle de pixels indépendant issu du banc AGAPIC existant.
- Refus de données invalides (crop, mode, métadonnées, fin de RLE tronquée, contrôle RLE incorrect) avant tout appel natif ou mutation des plans.
- Pipeline distinct du contrôle R68 et aucune écriture dans `dist/`, `archive/`, `tests/current/` ni `tests/passed/`.

### Relevé de l'exécution native réelle

| Vérification | Résultat sous Musashi |
|---|---:|
| Comparaisons directes du noyau (1/2/4/8 plans, masques, offsets), deux CPU | **320 PASS** |
| Comparaisons complètes AGAPIC RLE / recadrage / clipping à oracle indépendant | **432 PASS** |
| Groupes complets exécutés par le noyau natif | **5 352** |
| Pixels des fragments protégés par fallback | **25 816** |
| Paquets RLE répétés / littéraux traversés | **4 752 / 4 752** |
| Refus non destructifs pour entrée invalide | **8 PASS** |
| Erreurs de pixels, canaries, registres, source ou pile | **0** |

**Noyau natif : 36 octets**, SHA256 `74ef53d4f0e5d53fee8603553daea0cf2de834271b63475fa62c37bcca218138`. Les deux CPU 68EC020 et 68020 exécutent les mêmes instructions `BFEXTU/BFINS`. Le test couvre le mask 0 (aucune écriture), le mask 0xFFFF (opaque), les masques partiels, l'index 0 réellement écrit en opaque et les positions X 0..7 ; l'oracle compare tous les plans avec les octets de garde. Les refus vérifient qu'aucun appel natif ni écriture de destination n'intervient si le flux AGAPIC est invalide.

[Journal de test autonome, PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43490985555) · [Commit natif testé](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/6dfa49fb5df49ed948e7d43526f40108fc1311ba).

**Les cycles d'émulation ne sont pas des temps matériels.** Les 432 comparaisons couvrent les images testées et le fallback Python ; aucune Gate B/C et aucun moteur 020 complet ne sont démontrés.

**Étape suivante après PASS** : mesurer le coût d'un décodeur et d'un wrapper réellement **natifs 020**, puis comparer la même fonction sous WinUAE 68020/14 MHz et 68030/28 MHz **JIT OFF** par séries répétées. Aucun gain de vitesse n'est déduit des cycles Musashi.

**Protection :** R68 v0.13.13 et `LAST_GOOD` restent identiques, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Les Gates AMOS B/C et D physique ne sont pas exécutées pour OPT020.
