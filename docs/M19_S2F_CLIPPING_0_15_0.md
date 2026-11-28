# S2f — clipping des sprites, cible 0.15.0-alpha.3

**S2f P1 — chantier source-only autorisé par continuation « oui », cible de développement 0.15.0-alpha.3.** Noyau MC68020 indépendant : ancre signée, intersection écran 320x256, placement borné, translation des pixels dans une image de taille inchangée, remplissage transparent. Tests CPU/ABI, sentinelles et oracle bitplane, reconstruction exacte du parent S2e. Aucun raccord API/AP20, changement de la Lib/ASC/ABK courants, promotion, archive ni release. Gate A P1 à établir par CI ; P2 doit prouver cache immutable, staging et retraite des données DMA, retour depuis hors écran, refus sans corruption, Off/Close/End et mémoire. B/C/D S2f non testées.

## Base autoritative

S2e 0.15.0-alpha.2, commit [65f0cce](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/65f0cce933d7bcf471378231a2a29d5e81580388), Lib 160352o SHA256 `3135ba3973b138ec44a07ade3e190baba12a9425746252aaf88853b00d4ae7d3`, reconstruite par `tools/build_m19_s2e_in_memory.py` depuis sources MC68020. Gate A source + B Runtime et visuel PASS : [rapport](M19_S2E_RUNTIME_2026-11-28.md). 105 commandes/219 AP20, UNIT142 65062o (472 libres), UNIT213 18028o (47506 libres), réserve PC16 16384o. LAST_GOOD L2b protégée. Aucune nouvelle commande ni modification AGSP v1 prévue.

## P1 — noyau privé indépendant, non lié à la Lib active

[Source](../src/native/m19_s2/M19_S2F_CLIP_KERNEL_MC68020.s) · [Tests](../tools/test_m19_s2f_clip_kernel_gate_a.py) · [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2f-clip-kernel-gate-a.yml).

- Origine logique O = (X-HotX,Y-HotY), LONG signé. Rejeter overflow, dimensions invalides. Rectangle écran [0,320) × [0,256). Largeurs 16/32/64 et hauteur 1..256.
- Si intersection non vide, origine physique P = clamp(O,0,dimension écran - dimension image), translation d=O-P. Garder la même largeur et hauteur physiques ; chaque pixel de sortie échantillonne la source en (x-dx,y-dy) ou devient transparent zéro hors source. Appliquer exactement le même décalage aux 2/4 plans ; les bits des plans ne se mélangent jamais.
- Géométrie : 0 refus, 1 entier visible (dx=dy=0), 2 partiel, 3 totalement extérieur. Classe 3 ne déclenche pas de découpage ; proposition P2 : objet toujours possédé et réactivable, via l'état caché OS existant. Pas de libération implicite ni nouvelle sémantique publique avant preuve intégrée.
- Raster : un plan MSB-first, source immutable, destination privée disjointe de taille identique, dimensions/longueurs/pointeurs/overflow vérifiés avant écriture. Une routine ne modifie pas les données DMA vivantes et ne prétend pas authentifier la propriété mémoire. Test CPU avec oracle indépendant par entiers de ligne, guards lecture/écriture, registres préservés, cas hors limites et alias. Aucun test natif exécuté localement ; CI VASM épinglé et Unicorn MC68020.
- Chemin entier visible : conserver à terme le Move OS rapide sans copie. Le coût des bords doit être mesuré, pas supposé négligeable.

## P2 — intégration transactionnelle à qualifier

Le code S2d/S2e exige actuellement un rectangle entier dans `s2d_pub_geometry`, `s2d_x_geometry` et le premier Show. Ne pas supprimer simplement ces gardes. Les routines ExtSprite actuelles vérifient hauteur, références des deux canaux, CopInit, table SimpleSprites, LOF/SHF et le cycle de retrait. Le nouveau placement borné conserve ces invariants. L'intégration doit fournir une image source entière privée persistante (même après Erase du bank), et distinguer image logique, représentation affichée et staging. Préparer et vérifier le nouveau rendu avant exposition ; ne jamais réécrire les données actives ou un stage incertain. Réutiliser le hide et les deux WaitTOF du chemin transactionnel S2e ; conserver les protections en cas d'échec. Garder dimensions/largeur commune et palettes. Établir explicitement le nouveau format/numéro de registre et ownership/cache/retire avant toute évolution de Close/End.

Matrice d'intégration : quatre bords, quatre coins, complètement extérieur puis retour, changement d'image et signe du hotspot, largeurs 16/32/64, 2/4 plans, banques effacées après capture, 3 objets indépendants, rejet overflow sans modification, échec allocation/exposition/retrait, changement de largeur et fermeture. Régressions S2e et S2d à rejouer sur binaire exact (AGAPIC, AGSP, Bobs, Pattern, SafePort, DB/IFF/Swap, deux layouts AP20). CI P1 n'établit pas ce contrat. Préparer une seule future campagne ASC/ABK, jamais l'installer avant qualification et autorisation séparée.

## État

P1 source seulement, CI à relever. P2 non implémentée. Gate A alpha.3 complète, B/C/D non établies. Aucune Lib alpha.3 produite/activée. Aucun changement de branche, publication ou promotion.
