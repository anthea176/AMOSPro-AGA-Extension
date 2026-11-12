# M16 P0 — prévisualisation de la banque AGAPIC DATA sous AMOS/WinUAE

**À tester : le conteneur ABK, PAS le rendu d'image.** Aucune commande
AGAPIC 68000 n'existe dans la bibliothèque R44 actuelle. Ne pas remplacer
la bibliothèque R44 LAST_GOOD.

## Fichiers à copier dans un même répertoire Amiga

- [M16_AGAPIC_SAMPLE_BANK10.abk](M16_AGAPIC_SAMPLE_BANK10.abk) : banque AMOS
  DATA native, numéro 10, indicateur Fast préféré, masque indépendant.
  64×40×4, **1 856 octets** avec en-tête AmBk de 20 octets.
  SHA256 : **56443d5ed29527a21d043b845e70c545402648ef35fa590943cd62818499edaf**.
- [M16_AGAPIC_ABK_PREVIEW_01.asc](M16_AGAPIC_ABK_PREVIEW_01.asc) :
  programme AMOS natif chargé par **Project → Merge ASCII**.

**Attention :** l'instruction Load réutilise/remplace la **banque AMOS 10**.
Employer un environnement de test où la banque 10 est disponible.
Exécuter depuis le répertoire contenant l'ABK ou adapter la chaîne Load
du programme selon son lecteur/chemin. Pas besoin d'IFF ni d'AMCAF.

## Vérifications demandées

Le programme lit les 32 octets d'en-tête AGAPIC après le Load :
- MAGIE : AGAPIC, VERSION : 1, MASK : 1, CODEC : 1.
- Largeur : 64, hauteur : 40, profondeur : 4, octets/groupe : 10.
- Table lignes : 32, début des flux : 196, premier offset : 196,
  dernier offset : Length(10).
- Résultat attendu : **ABK FORMAT RESULT 1**.

**List Bank :** observer le marqueur F (Fast) ou C (Chip). Les flags
externes de l'ABK demandent DATA/Fast, mais la RAM réellement utilisée
dépend de la disponibilité du système. Un affichage C est un résultat
important à noter, pas une preuve de corruption de la banque.

Le test ne sait pas si l'archive ABK générée sur PC sera acceptée
par AMOS avant l'essai WinUAE : le modèle de format Python PASS ne suffit
pas pour déclarer une Gate B. Une fois ce chargement confirmé, le prochain
sous-jalon R45 pourra implémenter le dessin CPU depuis Start(10)/Length(10).

[Format complet AGAPIC v1](../../docs/M16_AGAPIC_FORMAT_DESIGN.md) ·
[Generator déterministe](../../tools/m16_agapic_sample.py) ·
[Tests CPU modèle hôte](../../tools/test_m16_agapic.py)
