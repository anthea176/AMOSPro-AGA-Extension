# M18 / R65 — Remplir une icône FICON8 depuis une banque DATA (contrat)

**Décision de travail du 13/11/2026 :** suite à l'accord « go go soldat » de l'auteur pour la phase de remplissage. Contrat proposé pour la première commande de **remplissage complet**, sans tentative de capture d'écran ni conversion AGAPIC native implicite. **API R65 implémentée et validée en Gate A** (98 exécutions natives 68000, deux dispositions ABI simulées ; modèle hôte 44 cas ; [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43444242260)). **Gate B WinUAE interprétée PASS, visuel et `RESULT 1` confirmés le 13/11/2026** ([rapport](M18_R65_FICON8_PUT_WINUAE_GATE_B_2026-11-13.md)) ; pas de Gate C Compiler ni de promotion.

## API implémentée R65 : copie chunky indexée -> Fast Icon

```amos
_OK=Aga F Icon Bank Put(DestBank,IconID,PixelBank,ByteOffset)
```

- **DestBank** : banque DATA `FICON8  ` existante, par exemple créée par `Aga F Icon Bank Create(12,4)`, numéro 5..65535.
- **IconID** : emplacement existant **1..Count** dans la banque destination.
- **PixelBank** : **autre banque DATA AMOS**, numéro 5..65535, distinct de DestBank, contenant au moins **256 octets chunky de 8 bits par pixel** à l'emplacement visé. Le nom du bloc source est libre. La banque source est dans Fast ou Chip : accès **CPU**.
- **ByteOffset** : décalage **0-based, en octets depuis `Start(PixelBank)`**, non négatif, tel que `ByteOffset+256 ≤ Length(PixelBank)`.
- **Valeur de retour** : `1` si le slot de 288 octets a été entièrement réécrit, `0` si un paramètre, une banque, la structure ou une région mémoire sont invalides. En cas d'échec, **pas de modification** de la destination ni des autres banques.

### Pixels et transparence

Le bloc source contient 256 indices bruts : `ByteOffset + Y*16 + X` pour `X/Y=0..15`. Aucun header, palette, RLE ou alpha n'est inclus dans ce bloc.

Chaque ligne de 16 pixels est convertie dans le format **Unity FICON8** existant :
- mot de masque de préservation **0 à bit de couleur non nulle, 1 à couleur zéro** ;
- huit mots planaires, bit 15 pour X=0 et bit 0 pour X=15 ;
- index de palette 0..255, **sans conversion RVB ni palette modifiée**.

En mode `Aga F Icon(...,1)`, la couleur **0 laisse voir le fond** ; en mode `0`, elle dessine l'index 0. Un masque alpha indépendant AGAPIC (couleur 0 opaque ou couleur non nulle transparente) **n'est pas représentable** : conversion native automatique à partir d'une telle image **non incluse**.

## Garanties et sécurité attendues

1. **Valider toutes les entrées avant la première écriture :** numéros de banques, ID, offset, présence des banques, banque source différente de la destination, type DATA, capacité source, en-tête `FICON8`, longueur réelle et dimensions du destinataire.
2. Vérifier les zones mémoires autorisées en lecture/écriture (dont premier et dernier octet) via les mécanismes déjà audités pour AMOS/Exec, avec contrôle de dépassement arithmétique 32 bits ; accepter la variation native de flags 0/1/3 des banques DATA chargées.
3. **Écrire exactement 288 octets** du slot demandé, sans toucher au header, aux autres icônes ou à la banque source. Préserver l'ABI AP20 (D2=0, D3=1/0, pile A3 consommée). Aucune allocation, suppression ou déplacement d'une banque.
4. Ne pas modifier l'écran AGA, la palette, le curseur, les deux buffers privés, ni déclencher Swap/Wait Vbl. Aucune utilisation du Blitter/DMA.
5. **Attention :** un cache `FICHIP8` construit précédemment à partir de la banque modifiée devient potentiellement périmé. Aucune invalidation automatique possible sans contrat de liaison ; **ré-étager explicitement** les slots avant `Aga F Blit`. Le futur cache dynamique doit gérer la validité.

## Exemple conceptuel

```amos
' Dans AMOS, disposer d'une banque DATA n°13 de >=256 octets,
' contenant les 16x16 indices de pixels dans l'ordre des lignes.
_C=Aga F Icon Bank Create(12,4)
_OK=Aga F Icon Bank Put(12,1,13,0)
' Puis, après ouverture et Double Buffer d'un écran AGA :
_OK=Aga F Icon(12,1,60,70,1)
' Sauvegarder ensuite la banque FICON8 au format ABK standard.
```

Le programme de validation devra créer cette banque source **depuis AMOS**, charger la candidate de travail sans détour ni second binaire, et inspecter les effets.

## Recette à obtenir

- **Modèle hôte** : vérifier la conversion exacte par rapport au modèle `m18_ficon16_model.py`, la préservation des autres slots, les rejets atomiques, les cas limites (coloris 0/1/128/255 ; position X=0/15, Y=0/15 ; Count 4/4096).
- **Gate A CPU/CI** : émuler les instructions 68000 *effectives* et le contrat AP20, tests d'ABI/relocation, validation des banques et de la taille, non-altération en échec, garde de fin de slot, à la fois disposition interpréteur et disposition Compiler V2 simulée.
- **Gate B** : **unique ASC** actif `tests/current/M18_R65_FICON8_PUT_01.asc`, WinUAE **AMOS interprété uniquement**, bannière R65 ; vérifier `RESULT 1`, checksum/planaires, affichage d'un véritable motif multicolore, `Save/Erase/Load` et mémoire.
- **Gate C** : un seul nouveau programme réellement compilé **à la fin de M18** ; Gate D matériel distinct.
- **R63 LAST_GOOD protégée** ; R64 v0.13.9 validée A/B conservée comme base déterministe de R65. **Candidate active R65 v0.13.10 : 40 116 octets, SHA256 `6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2`, 58 commandes / 65 AP20, routine de 968 octets. Gate A native PASS (98 cas) + hôte PASS (44 cas), [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43444242260).** [Test unique R65](../tests/current/M18_R65_FICON8_PUT_01.asc) ; Gate B WinUAE interprétée **PASS** ([rapport](M18_R65_FICON8_PUT_WINUAE_GATE_B_2026-11-13.md)). Aucune promotion automatique.

**Périmètre non autorisé dans cette étape :** commande de dessin pixel à pixel, capture AGA, décompression AGAPIC, import PNG, cache `FICHIP8` dynamique, modification d'AMCAF ou publication Aminet.

Références : [format source](M18_FICON16_SOURCE_P1.md) · [création R64](M18_FICON8_BANK_CREATE_DESIGN.md) · [rapport R64 WinUAE](M18_R64_FICON8_WINUAE_GATE_B_2026-11-13.md) · [règles source](../EXTENSION_SOURCE_RULES.md).
