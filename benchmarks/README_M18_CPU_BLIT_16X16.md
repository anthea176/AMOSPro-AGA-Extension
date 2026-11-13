# M18 / R60 — benchmark préliminaire 16×16 CPU AGAPIC vs copie Blitter

**Programme :** [m18_r60_cpu_vs_blit_16x16.asc](m18_r60_cpu_vs_blit_16x16.asc).
**R60 v0.13.5 LAST_GOOD inchangée.** Aucun nouveau moteur Fast Icon n'est exécuté.

## Préparation sous WinUAE

**Profils enregistrés au 13/11/2026 :** (1) **AMOS interprété / WinUAE 68030 avec JIT**, (2) **AMOS interprété / WinUAE 68020 sans JIT, 128 Mo Z3 Fast, cycle-exact indiqué**, (3) **AMOS compilé / même profil 68020 sans JIT déclaré**, (4) **WinUAE 68030 à 50 MHz sans JIT, 128 Mo Z3 Fast, cycle-exact indiqué — mode AMOS NON confirmé**. Les fréquences CPU réelles, paramètres internes WinUAE et SHA du programme/binaire chargés ne sont pas vérifiés. **Les deux modes 68020 ont été mesurés ; l'étape suivante est le diagnostic du temps CPU ~20 ms/appel, pas un nouveau résultat à inventer.** Ne pas mélanger les profils.

1. Copier le programme ASCII et la banque [M16_AGAPIC_SAMPLE_BANK10.abk](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire courant AMOS. **Attention : Load écrase la banque 10** ; utiliser une session WinUAE jetable.
2. Importer dans AMOS vide par Project → Merge ASCII, lancer le test interprété, relever la sortie.
3. Compiler **le même ASC dans un nouvel exécutable** et relever une seconde sortie. La fin volontaire est une boucle Do / Wait Vbl / Loop ; une interruption manuelle à cet endroit est normale.

**Rendus comparés (opaque 16×16, même contenu AGAPIC) :**

- **CPU R60** : appelle Aga Image Region sur le rectangle source (0,0,16,16) dans la banque AGAPIC 10, décode le RLE et peint au CPU dans le back buffer.
- **Blitter R60** : copie avec Aga Blit Copy une image identique préalablement peinte par le CPU à (16,24) ou (17,25), **depuis la Chip RAM vers le même back buffer**. Le staging est **hors chronomètre**.
- **Deux géométries** : X aligné sur 16 et X décalé de 1 pixel. Destination distincte, source préservée.
- **Trois répétitions × 1 200 appels par opération et géométrie**, mode PAL 320×256×16 couleurs ; Timer AMOS 1 tick = 20 ms.
- **Aucun Swap, VBL, Print, préparation palette ni allocation dans les boucles**. Un test Safe initial avant mesure, aucun Wait Vbl entre les appels. AGA Blit Copy effectue ses propres synchronisations.
- **Résultat attendu :** ERR 0, sortie de fermeture et Chip Free relevés. Les lignes ALIGNED et SHIFT donnent trois ticks bruts pour CPU puis BLIT ; relever les six trios.

## Limites et interprétation

**Ceci ne mesure PAS Fast Icon 16×16 en natif.** Les deux voies n'ont volontairement **pas le même coût de préparation** : l'une décode une image AGAPIC v1 compressée à chaque appel ; l'autre recopie un rectangle déjà présent dans le back buffer en Chip RAM, sans compter la préparation. Les performances constatées ne permettront **pas** de conclure qu'un nouveau moteur CPU non compressé est plus rapide ou plus lent qu'un Blitter de Fast Icon. Ce test permet de disposer d'une **baseline mesurée** des primitives existantes sur la même géométrie.

Pour comparer les futurs moteurs Fast Icon, instrumenter séparément : génération ou chargement des 288 octets d'un slot, lecture depuis vraie Fast RAM, copie Fast→Chip et libération éventuelle, écriture CPU, préparation Blitter, attente DMA et contention mémoire ; comparer les sorties pixel à pixel, modes opaque/masqué, coordonnées libres, clipping, 68020/030/040/060/PiStorm. Le temps total doit inclure la préparation **en cas de source Fast**, et l'option AUTO ne sera décidée **qu'après ces mesures réelles**.

Le script est un benchmark **dans benchmarks/**, pas un nouveau test actif dans tests/current/. R60 LAST_GOOD et les tests archivés restent inchangés. **Quatre captures WinUAE enregistrées le 13/11/2026** : [ticks bruts, profils et limites](RESULTATS_M18_R60_CPU_BLIT_16X16_2026-11-13.md). **68030 + JIT interprété** : médianes CPU/Blitter **2/8** aligné, **2/12** en X+1. **68020 sans JIT interprété** : **1232/22** aligné, **1225/28** en X+1 ; Chip Free 1 845 800 avant/après. **68020 sans JIT compilé** : **1179/16** aligné, **1178/21** en X+1 ; `ERR 0`, `CLOSE -1`, Chip Free **1 894 528** avant/après. **68030 50 MHz sans JIT (mode AMOS non précisé)** : médianes **415/10** aligné, **415/15** en X+1 ; `ERR 0`, `CLOSE -1`, Chip Free **1 894 528** inchangé. Le CPU reste à ~20 ms/appel dans les deux modes 68020, mais descend à ~6,9 ms/appel sur le 68030 sans JIT. Le code R60 fait un parcours RLE en deux passes puis un dessin CPU pixel/bitplane ; aucune attente VBL explicite n'a été trouvée. L'hypothèse d'une attente systématique de 20 ms par appel est affaiblie, **le détail des coûts n'est pas mesuré**. Le bandeau local 68020 est absent de l'ASC GitHub ; identité exacte du programme non vérifiée. Aucun relevé ne mesure les futurs Fast Icons natifs.
