# Où se trouve le source du candidat générique ?

## M6 / R15 0.7.2 (candidat Clear, runtime non validé)

Le builder actif `tools/build_m6_blit_clear_r15.py` utilise **l'archive R14 Fill validée** pour produire `dist/AMOSPro_AGA.Lib` (R15) et son archive versionnée. L'entrée 21 `Aga Blit Clear` est une petite routine 68000 générée par `tools/m68k_emit.py`, qui adapte les quatre paramètres AMOS avant un BSR vers **la routine Fill déjà validée** : entrées R14 0..19 intactes, entrée 20 prolongée uniquement par `GetP`. Voir `docs/M6_BLITTER_R15.md`. Builders R13/R14 historiques n'écrasent pas l'actif R15. `LAST_GOOD` R10 inchangée ; CPU/CI ≠ PASS WinUAE.

---


**Candidat courant R2 0.5.1** : `tools/build_m5_generic_r2.py` utilise le générateur
commun `tools/build_m5_generic.py` avec la synchronisation WaitBlit activée.
Le label `wait_before_cpu_write` identifie les trois instructions ajoutées.
Voir `docs/GENERIC_R2.md`. Le reste de cette page décrit la structure commune à R1/R2.

Le source faisant foi pour Generic R1 0.5.0 est actuellement du **Python qui émet
les instructions 68000**, et non le fichier historique `AMOSPro_AGA.s` :

- `tools/build_m5_generic.py` : fonctions read_file, inspect_file, validate_screen,
  decode_body, prepare_palette, palette, cleanup ; enveloppe AP20 et patch Open.
- `tools/m68k_emit.py` : encodage des instructions et résolution des labels.
- `tools/test_m5_generic.py` : exécution des octets produits sur CPU 68000 simulé.
- `tools/validate_ilbm.py` : parseur/décodeur Python indépendant, hors Amiga.

Le builder reprend les routines inchangées du binaire R5 dont le SHA256 est vérifié.
Il ne s'agit donc **pas d'une reconstruction intégrale de l'extension depuis un
source assembleur autonome**. Les anciens `.s` de ce dossier ne représentent pas
à eux seuls la version générique. Une migration vers un véritable source assembleur
unique devra vérifier l'identité binaire des routines conservées.

État runtime : R1 0.5.0 est rejeté après le défaut de couleurs signalé sur toutes
les images. Voir `docs/GENERIC_R1_RUNTIME_REGRESSION.md`.
