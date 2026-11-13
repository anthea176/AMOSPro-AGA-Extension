# Test actif M18/R63 — cache Chip et Blitter masqué

**R63 v0.13.8 candidate non promue : Gate A CPU PASS (260 cas), Gate B WinUAE interprétée à faire, Gate C Compiler manuelle seulement à la fin du chantier M18.** R62 Gate A était PASS mais son essai interprété a affiché `RESULT 0` (tous les BLIT 0) ; R63 corrige la vérification du champ natif de banque AMOS après `Load`.

**Seule bibliothèque de travail :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **38 736 octets**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. R60 `LAST_GOOD` inchangée ; R61 A/B/C PASS [archivée](../passed/M18_R61_FICON_01.asc).

**Un seul ASC actif :** [`M18_R63_CHIP_BLIT_01.asc`](M18_R63_CHIP_BLIT_01.asc) et deux ABK : [FICON8 source banque 10](M18_FICON8_SAMPLE_BANK10.abk), [FICHIP8 Chip pré-stagée banque 11](M18_FICHIP8_SAMPLE_BANK11.abk), **1 188 octets**.

**Test interprété :** installer R63 dans AMOS, redémarrer, mettre les deux ABK dans le dossier de travail, importer l'ASC dans un programme vide avec Project → Merge ASCII. **Load écrase les banques 10 et 11**, donc session WinUAE jetable. Exécuter en **interprété seulement** pour cette étape. Le bandeau n'affirme plus de compilation. Le test lit sans modifier le mot natif `Deek(Start(11)-12)` et affiche **`FICHIP 11 FLAGS`** : noter cette valeur pour confirmer ou écarter l'hypothèse des flags normalisés.

**Attendu :** `RESULT 1`, `CLOSE -1`, `NOS 0`, `SWAP 1`, Chip Free avant/après identique. `ICON`, `BLIT`, `SHIFT`, `CLIP`, `OUT` doivent tous renvoyer 1 et `BAD` / `BCBAD` 0. Vérifier les icônes CPU et Blitter à l'écran ainsi que le clipping. Le code utilise un cache **préparé hors AMOS**, sans mesure du staging Fast→Chip.

[Contrat complet du cache](../../docs/M18_FAST_ICON_CACHE.md) · [diagnostic R62 / technique P5](../../docs/M18_FICON16_NATIVE_P5.md). **Ne pas demander de compilé AMOS avant la fin de M18.**
