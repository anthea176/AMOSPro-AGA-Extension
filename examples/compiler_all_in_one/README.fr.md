# AMOS Compiler — exemple AGA tout-en-un

[English](README.md) · [Tous les exemples](../README.fr.md) · [Installation](../../INSTALL.fr.md)

Ce dossier contient une **copie renommée pour la distribution** de la démonstration Compiler intégrée **R46 C1**. Elle regroupe dessin AGAPIC (opaque, masqué et décalé), clipping, Plot/Draw/Box/Circle, polices AMCAF et Topaz, double buffering, curseur et nettoyage.

## Fichiers et utilisation

- [`COMPILER_ALL_IN_ONE.asc`](COMPILER_ALL_IN_ONE.asc) — source ASCII ; **seul le nom du fichier AGAPIC chargé a été adapté**.
- [`AGAPIC_SAMPLE_BANK10.abk`](AGAPIC_SAMPLE_BANK10.abk) — image chargée en banque **10**.
- [`Hwarf1252S.abk`](Hwarf1252S.abk) et [sa licence](Hwarf-12xxS.licence) — fonte chargée en banque **25**.

1. Copier **tout le dossier** sur un volume AmigaDOS. L'exécutable doit être lancé avec ce dossier comme **répertoire courant**, car `Load` utilise des chemins relatifs.
2. Installer la [bibliothèque R68 promue](../../dist/AMOSPro_AGA.Lib) dans le slot d'extension `APSystem` configuré, redémarrer AMOS et le Compiler, puis importer `COMPILER_ALL_IN_ONE.asc` dans un programme vierge par **Project → Merge ASCII**.
3. Produire un **nouvel exécutable** et le lancer depuis le dossier contenant les ABK. Pour reproduire la **validation historique exacte R46 C1**, utiliser le ZIP original ci-dessous et la [bibliothèque Compiler-safe historique](../../dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) dans une installation de test distincte.

Le programme **écrase les banques 10 et 25**. Historiquement, il affichait `RESULT 1`, `CLOSE RETURNED`, `CUR 500 ERR 0`, `IMAGE O/M/S 1 1 1` et `CLIP L/R/T/B 1 1 1 1`. Ce sont des **résultats attendus**, pas de nouvelles mesures sur le programme public renommé.

## Conservation du test validé

La [**source R46 C1 originale, inchangée**](../../tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc) et le [rapport de validation](../../docs/GATE_C_R46_MONOLITH_CANDIDATE.md) attestent l'essai Compiler intégré réussi le **12 novembre 2026**.

Seul le nom extérieur de [`COMPILER_ALL_IN_ONE.zip`](../COMPILER_ALL_IN_ONE.zip) est simplifié. **Le contenu du ZIP, son dossier et ses noms internes versionnés sont conservés octet pour octet** pour préserver l'archive réellement validée. L'extraire tel quel pour répéter le test historique. La copie publique `COMPILER_ALL_IN_ONE.asc` utilise en revanche la ressource renommée `AGAPIC_SAMPLE_BANK10.abk` et **n'a pas été recompilée/validée séparément** depuis cette adaptation.

Le scénario vérifie la propreté du retour AMOS mais ne couvre ni toutes les commandes ni le matériel AGA physique. Code sous [MIT](../../LICENSE), police Hwarf sous [licence distincte](Hwarf-12xxS.licence) et illustrations soumises à des [conditions séparées](../../ASSETS_LICENSE.md).
