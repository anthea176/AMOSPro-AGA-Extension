# Prototype M1/M2 — AMOSPro AGA 0.0.2 R1

## Résultats validés sous WinUAE

**31 octobre 2026, confirmation utilisateur :**

1. Chargement de `AMOSPro_AGA.Lib`, slot 14 : OK.
2. Programme exécuté dans l'interpréteur AMOS 365 : `AGA PROBE : OK`, `AGA DETECT = -1`.
3. Diagnostic AMOS en interprété : valeur brute `-1`, égale à `-1` vrai, égale à `1` faux, non nul vrai.
4. Programme compilé par AMOS Professional 365 et exécuté : **« ca marche compilé »**, confirmation explicite du développeur. La valeur brute du résultat compilé n'a pas été retranscrite.

**API retenue :** `Aga Detect` est booléen, **faux si `0`, vrai si non nul**. Ne pas exiger le nombre exact `1`. Le code assembleur envisageait la valeur 1, mais l'interpréteur affiche -1 ; l'origine de cette différence ne fait pas partie de la validation fonctionnelle.

## Fonctionnement prévu

La fonction vérifie :
- ExecBase.AttnFlags, présence du 68020 (bit 1 du mot à $128 ; octet bas à $129 en big endian).
- Ouverture de graphics.library V39+.
- GfxBase.ChipRevBits0 et masque Alice/Lisa `$0C`.

Sur une machine sans AGA, l'API doit renvoyer faux (0) ; **ce scénario reste à valider réellement**. La fonction ne modifie pas les écrans.

## Installation (copie de test uniquement)

1. Quitter AMOS. Sauvegarder la bibliothèque précédente.
2. Copier [AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib) dans `APSystem/`.
3. Conserver le slot 14 pour `AMOSPro_AGA.Lib`, redémarrer AMOS.
4. Charger [AGA_DETECT.asc](../tests/AGA_DETECT.asc), exécuter en interprété puis en compilé.

Le HUNK expérimental a 340 octets, SHA256 :
`69ace1d90a39a19cf47105fce8ef14fa44f7c6cca98d0a068f0d9f80abb21cfc`.

Source : adaptation binaire reproductible de l'extension Requester publique d'AMOS 365. Le source assembleur du dépôt est **candidat, non encore assemblé avec Genam**. La réussite native est établie par les essais du développeur, pas par un assemblage Genam.

## Étape suivante

[M3 : écran AGA 256 couleurs](M3_SCREEN_DESIGN.md).
