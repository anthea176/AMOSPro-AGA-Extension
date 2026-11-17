# M19 P0j-a — précontrôle des 64 images avant le premier Blit

## Pourquoi ce jalon intermédiaire

P0i ([rapport](M19_P0I_MULTIBANK_DRAW_GATE_A_2026-11-17.md), Gate A PASS 76 vérifications) sait peindre 64 Bobs multi-banques, mais une image inexistante sur le 64e Bob est détectée **après** que les précédents ont déjà modifié le back buffer. P0j-a protège ce cas sans toucher au source natif P0i ni à la Lib installée.

## Fonction native MC68020

L'entrée privée `image_frame_preflight_entry` appelle le P0h (sources des 64 objets), puis pour chaque objet actif utilise le relais P0g, **Bnk.GetAdr de sa banque enregistrée** et le répertoire AGBO source (32 octets d'entête ; entrées de 40 octets), avec vérification TypeOfMem au début et à la fin. Elle recherche l'ID d'image demandé, puis vérifie **largeur, hauteur, profondeur, stride, longueur des plans de pixels, masque et limites des offsets** des images réellement utilisées, par rapport à la profondeur AGA et à la taille du payload. Les entrées non utilisées et le padding restent validés par P0c lors du staging. Elle ne modifie jamais `bank_active_state`, n'alloue pas de Chip et n'utilise pas le Blitter.

`routed_paint_prechecked_entry` ne transmet à `routed_paint_all_entry` (P0i exactement inchangé) que si **toutes** les images passent ce contrôle. Cela empêche toute peinture pour les images absentes ou incompatibles en début de frame, même sur l'objet 64. La préparation Chip et le contrôle complet du répertoire/masques/offsets restent la responsabilité des routines P0c/P0d.

### Précaution

Cette étape **ne supprime PAS** la projection temporaire du shadow privé `bank_active_state` de P0i, car trois routines propriétaires (registry prepare, lookup, image resolver) en dépendent encore. Il faudra un véritable routage explicite par banque à ces trois niveaux, en conservant leur validation d'identité, les ressources Chip et le callback End. La peinture P0i reste non réentrante et un échec tardif de SafePort/Chip ou un changement de données après le précontrôle peut encore laisser un back buffer partiel. Aucune frame atomique complète n'est revendiquée.

## Fichiers et validation

- [Émetteur source](../tools/m19_p0j_frame_image_preflight_emit.py)
- [Builder AP20 source-only](../tools/build_m19_p0j_frame_image_preflight_in_memory.py)
- [Banc natif MC68020](../tools/test_m19_p0j_frame_image_preflight_gate_a.py)
- **Gate A MC68020 PASS — 68 vérifications** sur deux implantations mémoire de type Runtime/Compiler simulées : [CI 44167065047](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44167065047). Cas couverts : 64 images issues des banques 10/11, image inexistante n°64, corruptions réelles du répertoire AGBO (profondeur, stride, drapeau masque, longueur des pixels), corruption de génération, refus CPU<020, rendu pixel-exact valide et fermeture Chip. Les services OS/Blitter restent simulés.
- **Provenance SHA figée :** code natif P0j BOBS **18 176 octets**, SHA256 `a91a0b99a05811a7f333738e1327b90a90dfe1aa947ec712d4290f568b88f618` (+846 octets par rapport à P0i). Candidate AP20 reconstruite **uniquement en mémoire** **98 652 octets**, SHA256 `4d43956a5dfbc1ae9cb1baf7058f48e6748f8bf80ef948fcc6b0a1872960a4ab`, 85 commandes, 178 sections, quatre unités [142,153,156,177], portée PC16 max 854 octets.
- Gates B/C/D P0j-a : **non exécutées**
- Ancienne candidate P0i : 97 820 octets, SHA256 `004a04f9819fc2df9498ec8887e3de8a6533a7f620f04743c1fa1ae6ee872fa4`, source SHA-pinné
- Bibliothèque canonique : **96 908 octets** SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, ASC actif `M19_AP20_ISLANDS_01.asc`, `LAST_GOOD` R84 et archives tous protégés.

**Aucune commande publique `Aga Bob Draw` et aucune bascule WinUAE.**
