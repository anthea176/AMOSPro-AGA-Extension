# Passage 18 — Bobs, clipping, Flip, collisions, priorité et plans

**24 novembre 2026 — passage 18/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

## 1. Géométrie et collisions reliées

[M19_P2A_PUBLIC_COL_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2A_PUBLIC_COL_MC68020.s) (AP20 189) : retour D3=-1 invalide, 0 pas de collision, 1 collision ; D2=0 et consommation des paramètres A3. Le résultat invalide n'est pas un hit. [M19_P2A_COLLISION_QUERY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2A_COLLISION_QUERY_MC68020.s) vérifie mode 0/1 puis résout les deux objets ; [M19_P2A_CHIP_RESOLVE_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2A_CHIP_RESOLVE_MC68020.s) photographie leurs champs et recontrôle les identités avant publication du descripteur partagé.

[M19_P2A_GEOMETRY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2A_GEOMETRY_MC68020.s) vérifie IDs distincts 1..64, largeur/hauteur 1..4096, stride et intersections ; [M19_P1D_LIMIT_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1D_LIMIT_MC68020.s) accepte ID zéro pour limite globale, 1..64 pour objet, bornes exclusives, dimensions positives et contrôle overflow, zéro complet pour reset. [M19_P1D_INTERSECT_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1D_INTERSECT_MC68020.s) traite l'intersection vide. [M19_UNIT142_P0E_OBJECT_CORE_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_UNIT142_P0E_OBJECT_CORE_MC68020.s) borne les coordonnées publiées sur 16 bits signés ; [M19_P1B_HOTSPOT_ORIGIN_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1B_HOTSPOT_ORIGIN_MC68020.s) adapte l'origine et le clip.

[M19_P2B_PAINT_GEOMETRY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_PAINT_GEOMETRY_MC68020.s) partage p2b_variant entre dessin et géométrie de collision : miroir du hotspot W-1-HotX / H-1-HotY, en fonction du mode. Le calcul d'ancre est borné pour les valeurs d'entrée validées. [M19_P2A_COLLISION_KERNEL_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2A_COLLISION_KERNEL_MC68020.s) vérifie les descripteurs et bornes, mode 0 rectangle, mode 1 test de bit du masque ; intersection vide ou simple contact de bords ne suffit pas. Sans masque, pixel 0 reste opaque ; l'opacité ne dépend pas de la couleur indexée.

**Point de vigilance :** le mode rectangle passe lui aussi par la résolution Chip et la géométrie commune avant la branche de collision. Une variante Flip peut donc nécessiter une préparation même pour une requête rectangle. Un refus invalide / allocation est distinct de « pas de collision ». Ne pas changer ce contrat à titre d'optimisation sans preuve ni mesure.

## 2. Priorités et plans

[M19_P1C_PRIORITY_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1C_PRIORITY_MC68020.s) vérifie les modes 0..3. [M19_P1C_ORDER_COLLECT_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1C_ORDER_COLLECT_MC68020.s) construit une liste bornée 1..64, clés Y signé normalisé et ID selon mode ; mode 2 utilise ID. Ne pas extrapoler l'ordre de parcours de tous les modes à partir de la seule clé de tri. Vérifier la superposition réelle avec l'oracle du banc.

[M19_P2C_PLANES_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2C_PLANES_MC68020.s) contrôle le slot actif et le masque 0..255, encodage privé inversé du masque, puis application au Mask du RastPort privé. La sélection des plans d'écriture est distincte du masque d'opacité. Masque de plans nul : aucune modification de pixel attendue ; collisions indépendantes du masque de plans selon le contrat.

## 3. Variantes T07/T08/T10/T18

| Cas | Résultat à vérifier |
|---|---|
| 15/16/17 pixels, bords gauche/droite/haut/bas, coordonnées négatives | Pas de lecture hors image ni écriture hors clip ; mêmes coordonnées dessin/collision. |
| Hotspots aux limites ou hors image autorisés, Flip H/V/HV | Origine et masque transformés de façon identique ; double Flip conforme. |
| Pixel index 0 sans masque, trous du masque, rectangles qui se touchent | Opacité contractuelle ; distinguer -1, 0 et 1. |
| 64 slots, modes de priorité, Y égaux, plans 0 / tous / non contigus | Ordre stable attendu par contrat, pixels des plans non sélectionnés préservés. |
| Refus Chip/cache/banque et répétition | Pas de collision faussement positive sur -1 ; pas de frame partielle publiée ; ressources libérées. |

**Bilan :** aucune divergence de géométrie prouvée sur les chemins examinés. Les anciens PASS P2b/P2c et P2d sont des preuves des bancs exacts, pas de toutes les combinaisons ci-dessus. VM sur les cas limites et performance ; pas de refonte du moteur Bob ni de nouveau P0.
