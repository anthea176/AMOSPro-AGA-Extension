# M11 — test graphique AMOS/AGA actif

**Unique `.asc` courant :** [`M11_R25_AMOS_TEXT_01.asc`](M11_R25_AMOS_TEXT_01.asc), bandeau `M11-R25-AMOS-TEXT-01`. La bibliothèque reste **R25 0.9.1** inchangée ; **M11 NON TESTÉE sous WinUAE**.

Importer par **Project → Merge ASCII**, choisir [`examples/demo.iff`](../../examples/demo.iff) (320×256×8 PAL). Pendant 300 VBL, observer le **panneau bleu** de l'écran Intuition AGA et vérifier si le texte `AMOS TEXT VISIBLE?` apparaît dessus. Le programme ferme ensuite l'écran ; la console doit indiquer `DRAWERR 0` et `CLOSE RETURNED`.

**Ne pas conclure automatiquement à l'impossibilité de compatibilité AMOS/AMCAF si le texte est absent.** L'expérience vérifie uniquement le résultat visible de `Text` natif sur l'écran Intuition AGA. [Rapport et protocole M11](../../docs/M11_TEXT_COMPAT.md). Le [test R25 validé](../passed/M10_R25_RECT_OVERLAP_VISUAL_01.asc) reste archivé sans modification.
