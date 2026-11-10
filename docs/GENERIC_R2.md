# Generic ILBM R2 — 0.5.1

Candidat à tester : `dist/AMOSPro_AGA.Lib`, identique à
`dist/experimental/AMOSPro_AGA_M5_v0.5.1_GENERIC_R2.Lib`.
Taille : **6444 octets**. SHA256 :
`18fdfd059bd6f15f5a0d42eeb9d628a71ee4110849d8bb781a67db9575f93803`.

## Diagnostic et correctif minimal

La lecture de la session WinUAE en pause sur Clown a établi :

- bitmap actif 320×200, stride 40, profondeur 8 ;
- plans 0..6 identiques octet pour octet aux plans décodés du fichier ;
- plan 7 entièrement nul, somme 0 au lieu de 670502 ;
- les **256 entrées RGB du ColorMap sont exactement celles du CMAP** ;
- le code chargé correspond à R1, hormis le dispatcher GetP normalement remplacé par AMOS.

Le défaut visuel ne justifie donc pas de modifier le calcul de la palette.
La perte du dernier plan est compatible avec la copie Blitter asynchrone initiée
par `AllocScreenBuffer(..., SB_COPY_BITMAP)`. R1 n'attendait pas sa fin avant de
modifier le bitmap au CPU. Le WaitBlit de Swap intervenait après le décodage.
La chronologie exacte du Blitter n'a pas été tracée : l'identification de cette
course repose sur le défaut observé, l'appel sans synchronisation et le contrat OS.

R2 ajoute seulement, après validation/préparation et avant WRITE=1 :

```asm
movea.l (a5),a2       ; état extension depuis le contexte temporaire
movea.l 8(a2),a6      ; graphics.library
jsr     -228(a6)      ; WaitBlit
```

À ce point, seul A5/contexte reste live. A2/A6 et les registres volatils système
D0/D1/A0/A1 sont sacrifiables ; aucun CCR n'est utilisé après cet appel.
Le résultat public D3 est établi ensuite, D2=0 à la sortie, pile équilibrée.
Le code palette, le décodeur RAW/ByteRun1, Open, PicInfo, Double Buffer, Swap et
Close restent identiques à R1. Les déplacements locaux sont recalculés par labels.
La construction repart toujours de l'archive R5 vérifiée ; aucun binaire rejeté
R5R1/R5R2 n'est utilisé comme base.

## Tests exécutés

- [Suite générale R2](GENERIC_R2_VALIDATION.json) : 41/41 IFF, tous les plans/pixels,
  tous les indices CMAP, les 8 champs PicInfo, tags écran et ABI ; 127 cas malformés,
  5 incompatibilités écran, 3 échecs d'allocation, 12 cas synthétiques.
- [Régression Blitter différé](GENERIC_R2_CPU_TESTS.json) : les 41 images reproduisent
  une perte du dernier plan sous R1 et passent sous R2. Le modèle termine la copie
  lors de la prochaine synchronisation, sans toucher au padding sentinelle.
- HUNK/AP20, tokens, GetP, segments non modifiés, SHA256 et reproductibilité contrôlés.

Ces tests exécutent les instructions 68000 avec les appels système simulés.
Ils vérifient l'ordre des opérations, **pas encore le rendu réel de R2 sous WinUAE**.

## Construire et tester

```text
python tools/build_m5_generic_r2.py
python tools/test_m5_generic_r2.py
python tools/build_m5_generic_r2.py --promote
python tools/verify_artifacts.py
```

`--promote` exécute les tests avant remplacement de la Lib courante.
R1 reste archivé et son ancien `--promote` est désactivé.
R5 0.4.6 et LAST_GOOD restent intacts.

Test AMOS unique : `tests/current/M5_GENERIC_ILBM.asc`, maintenant titré R2 0.5.1.
Recharger effectivement l'extension dans AMOS avant le test. Vérifier Clown puis
KEKKO et tout le corpus, interprété puis compilé : pixels/palette, aucun hang/Guru,
Swap et cleanup. Un succès CPU n'est pas un PASS visuel.

## Sources

Source du correctif : `tools/build_m5_generic_r2.py` et
`tools/build_m5_generic.py` (`routine`, label `wait_before_cpu_write`).
Encodeur : `tools/m68k_emit.py`. Voir `src/README.md` pour la distinction avec les
anciens fichiers assembleur ; il n'existe pas encore de `.s` autonome complet pour R2.

Référence du contrat de synchronisation :
[Graphics Primitives — When to Wait for the Blitter](https://wiki.amigaos.net/wiki/Graphics_Primitives).
La bibliothèque lance les opérations par plan et peut revenir alors que la dernière
est encore en cours. Le CPU doit attendre avant de modifier la mémoire concernée.
