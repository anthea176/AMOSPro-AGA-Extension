# Validation M2 — AMOSPro AGA v0.0.2 R1

Date du retour utilisateur : 31 octobre 2026.

## Configuration et tests confirmés

- AMOS Professional **365** installé et fonctionnel dans WinUAE. Les essais de cette extension sont validés séparément, en distinguant interpréteur et compilateur.
- Extension **AMOSPro_AGA.Lib** version v0.0.2 R1 installée en **slot 14** sur l'environnement de test.
- Programme `tests/AGA_DETECT.asc` exécuté dans l'**interpréteur** : capture montrant `AGA PROBE : OK` et `AGA DETECT = -1`.
- Programme `tests/AGA_DETECT_DIAG.asc` : `-1` est la valeur numérique effective dans l'interpréteur ; `PLUS UN = 0`.
- **Compilation et exécution du programme de test avec AMOS 365 confirmées par le développeur** : « ca marche compilé ».

Le développeur a choisi de conserver `-1` comme TRUE, conformément à l'utilisation booléenne d'AMOS. Le fonctionnement compilé est confirmé, mais la valeur numérique brute imprimée par l'exécutable compilé n'a pas été précisée.

## Binaire figé pour non-régression

- `archive/AMOSPro_AGA_v0.0.2_R1_M2_OK.Lib` — copie immuable du binaire validé.
- SHA256 attendu : `69ace1d90a39a19cf47105fce8ef14fa44f7c6cca98d0a068f0d9f80abb21cfc`.
- HUNK : 340 octets.
- Générateur : `tools/build_detect.py` (adaptation binaire de l'extension AMOS 365 Requester publique).
- Ce binaire n'est pas un assemblage natif Genam du source candidat.

## Ce que ces tests ne démontrent pas encore

- Une exécution négative sur un chipset ECS sans AGA (la fonction devrait rendre 0).
- La sûreté d'une gestion écran 8 bitplanes sous AMOS/Intuition.
- Le chargement de bibliothèques et le nettoyage de l'état écran après un échec M3.
- La valeur numérique exacte de `Aga Detect` en mode compilé.

Les jalons **M0/M1/M2** sont validés selon ces limites. Ne pas attribuer de fonctions graphiques à la v0.0.2.
