# M19 S1-P1h — correction du publisher AGSP

**24/11/2026 :** Runtime S1-P1g, ERR 7 après succès IFF/palette. L'ASC n'a pas encore atteint Get AGA Sprite. Autorisation auteur « ok go » pour corriger le défaut et livrer après Gate A.

## Cause vérifiée

Dans le source AMOS Professional 365, [+B.s Bnk.Change](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BB.s#L1323) charge `Cur_Banks(a5)` puis `(a0)`. Le champ $05EA est un pointeur vers la cellule de tête du programme, pas la cellule elle-même. Le publisher Bob utilise déjà cette indirection. Le publisher AGSP P1g faisait LEA au lieu de MOVEA.L ; le mock de test reproduisait à tort cette structure directe. Ce défaut est avéré dans le source ; la résolution de l'ERR 7 doit être confirmée en Runtime.

## Correction

- [Publisher MC68020 P1h](../src/native/m19_s1/M19_S1P1H_AGSP_BANK_COMMIT_MC68020.s) charge et contrôle le pointeur de cellule, conserve séparément son adresse et son contenu, revalide les deux avant publication. Refuse aussi un changement de propriétaire sans changement de nœud.
- [Pipeline](../src/native/m19_s1/M19_S1P1H_CAPTURE_PIPELINE_MC68020.s) et [master](../src/native/m19_s1/M19_S1P1H_BANK_PUBLIC_MC68020.s) réutilisent les autres modules historiques inchangés. P1g reste reconstructible.
- [Banc CPU](../tools/test_m19_s1p1c_amos_bank_commit.py) modélise deux cellules distinctes ; P1g négatif, insertion, remplacement, échecs, dérive propriétaire et tête, préservation du reste des banques. Tests publics banque 29 et capture/remplacement.
- [Builder](../tools/build_m19_s1p1h_l2b_bank_fix_ap20.py) assemble les deux masters source, reconstruit P1g historique, modifie uniquement le groupe 207 et le titre. 102 commandes / 208 AP20, 207 autres unités intactes. [Gate A](../tools/test_m19_s1p1h_bank_gate_a.py) contrôle l'assemblage exact testé, les deux dispatchs et les régressions L2b.

## Qualification et livraison

[Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45481353847) PASS sur le commit f321cdf : 142720 octets, SHA256 `900646cc208cc99095c81c209276579a28dbcbbcbd43dd10c4e93be35d2e05eb`, blob `ee7b6bb6ecec3207d193c1e95641b1d9abe8cb62`. Unité 207 : 5878 octets natifs, SHA256 `5aa8554db81399699a7e943066084f00753750e6fc93194906a3ce6db6b90be5` ; les 207 autres unités inchangées. Reconstruction de livraison en mémoire à partir de la base P1g exacte et du code VASM testé fourni par le journal CI, comparaison des empreintes. Autorisation auteur « ok go » ; seule Lib de travail P1h livrée. Gate A native MC68020 PASS (184 Pattern, 172 writers, 10 suites Bob). Les deux CI AGSP annexes corrigées sont PASS (45484855000 et 45484854747). L'audit Input State corrigé dans dfb178f est PASS (étape du run 45484855065) ; le run Artifact integrity complet et la requalification CI historique sur la nouvelle livraison ne sont pas déclarés PASS. LAST_GOOD L2b 136708 octets protégée, ASC et IFF inchangés. Aucun PASS Runtime/Compiler/matériel anticipé. Ne pas relancer P1g.

Le [dossier de test](../tests/proto/agsp_capture/) contient désormais l'IFF versionnée (5428 octets) et l'ASC. Ne pas changer le programme pour masquer le défaut natif. Après livraison P1h, redémarrer AMOS, tester avec ces fichiers ensemble et la banque 29 libre.
