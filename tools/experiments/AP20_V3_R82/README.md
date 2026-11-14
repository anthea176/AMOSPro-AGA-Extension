# AMOSPro AGA — historiques P3 / P4 et tests P5

> **Depuis `main` :** la bibliothèque `dist/AMOSPro_AGA.Lib` désigne R82 stable. La P5 expérimentale réside au même chemin **uniquement sur la branche `experiment/ap20-v3-multiunit-64k`**. Ne pas confondre les deux téléchargements.

**Un seul binaire actif sur cette branche expérimentale :**

- [`../../../dist/AMOSPro_AGA.Lib`](../../../dist/AMOSPro_AGA.Lib) — **P5, 3 unités AP20**, 76 188 octets, SHA256 `db55149f19f2d4753232cb5768167f38c82e86c5e2613a056e093fa9c23897af`.
- [`../../../dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../../dist/AMOSPro_AGA_LAST_GOOD.Lib) — **R82 stable**, 64 112 octets, inchangée.

Les anciens fichiers binaires P3/P4 et la copie P5 de ce répertoire
ont été retirés de l'arbre de la branche pour éviter toute confusion.
Ils restent récupérables dans l'historique Git, ainsi que dans les
anciens artefacts de CI si encore disponibles.

Seuls les scripts ASC de test et la documentation restent ici :

- [`P5_R82_3UNITS_SMOKE.asc`](P5_R82_3UNITS_SMOKE.asc)
- [`P5_WINUAE_TEST.md`](P5_WINUAE_TEST.md)
- [`P4_R82_SPLIT_SMOKE.asc`](P4_R82_SPLIT_SMOKE.asc) (historique)
- [`P4_WINUAE_TEST.md`](P4_WINUAE_TEST.md) (historique)

**À installer sous WinUAE : `dist/AMOSPro_AGA.Lib` uniquement**, à
renommer si nécessaire dans `APSystem` sous le même nom. Le sélecteur
AMOS extension n°14 doit afficher `THREE GENUINE NATIVE UNITS`.
