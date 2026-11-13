# M18 / R60 — benchmark préliminaire 16×16 CPU AGAPIC vs copie Blitter

**Programme :** [m18_r60_cpu_vs_blit_16x16.asc](m18_r60_cpu_vs_blit_16x16.asc).
**R60 v0.13.5 LAST_GOOD inchangée.** Aucun nouveau moteur Fast Icon n'est exécuté.

## Préparation sous WinUAE

**Profils à distinguer :** première mesure du 13/11/2026 confirmée par l'auteur en **AMOS interprété / WinUAE 68030 avec JIT activé**, donc non représentative d'un 68020 standard. Pour le prochain relevé, sélectionner un profil **Amiga 1200 PAL, 68020/68EC020 (~14 MHz), JIT désactivé**, et activer **CPU cycle-exact si WinUAE le permet dans cette configuration**. Vérifier que le CPU n'est pas en mode « fastest possible », relever les options exactes et conserver la même configuration RAM entre interprété et compilé. **Ne pas mélanger les résultats de profils différents.**

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

Le script est un benchmark **dans benchmarks/**, pas un nouveau test actif dans tests/current/. R60 LAST_GOOD et les tests archivés restent inchangés. **Première exécution WinUAE PASS (capture du 13/11/2026)** : [ticks relevés et limites](RESULTATS_M18_R60_CPU_BLIT_16X16_2026-11-13.md), médianes **CPU 2 / Blitter 8** aligné et **CPU 2 / Blitter 12** en X+1 ; ERR 0, CLOSE -1, Chip Free stable. **L'auteur a confirmé le mode interprété sous WinUAE 68030 + JIT.** Le relevé en interprété 68020 sans JIT/cycle-exact, puis le passage compilé dans la même configuration, restent à effectuer avec ce même ASC. Ce n'est pas une mesure des futurs Fast Icons natifs.
