# M16 P0 — prévisualisation de la banque AGAPIC DATA sous AMOS/WinUAE

**PASS utilisateur (12/11/2026) : conteneur ABK chargé sous AMOS/WinUAE. Aucun rendu d'image natif.** Aucune commande
AGAPIC 68000 n'existe dans la bibliothèque R44 actuelle. Ne pas remplacer
la bibliothèque R44 LAST_GOOD.

## Fichiers à copier dans un même répertoire Amiga

- [M16_AGAPIC_SAMPLE_BANK10.abk](../current/M16_AGAPIC_SAMPLE_BANK10.abk) : banque AMOS
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

**List Bank :** la capture WinUAE affiche `10 - AGAPIC S: $40413010 L: 1836` ; **S correspond à l'adresse Start, pas à un indicateur Fast/Chip**. Cette sortie ne comporte pas de F/C explicite : le placement RAM reste à confirmer via la configuration WinUAE ou `exec.library/TypeOfMem`. Le flag externe demande DATA/Fast, sans garantir la mémoire réelle.

Le chargement du fichier généré sur PC est confirmé par la capture utilisateur : `ABK FORMAT RESULT 1`, Magic `AGAPIC`, Version 1, profondeur 4, offsets exacts, banque DATA 10. [Rapport de validation](../../docs/M16_AGAPIC_WINUAE_P0_PASS.md). Le programme ASC original reste inchangé ; ce PASS est celui **du format P0 uniquement**, pas la Gate B d'une commande R45. [Contrat proposé pour le futur rendu CPU R45](../../docs/M16_R45_IMAGE_DRAW_CONTRACT.md).

[Format complet AGAPIC v1](../../docs/M16_AGAPIC_FORMAT_DESIGN.md) ·
[Generator déterministe](../../tools/m16_agapic_sample.py) ·
[Tests CPU modèle hôte](../../tools/test_m16_agapic.py)
