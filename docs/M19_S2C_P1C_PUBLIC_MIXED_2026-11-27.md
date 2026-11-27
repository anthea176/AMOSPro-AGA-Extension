# M19 S2c-P1c — intégration publique mixte et Close/End (27-11-2026)

Statut : source et banc de qualification engagés, **pas de Lib installée**. La S2r-P1 qualifiée reste active. LAST_GOOD inchangée.

- Parent P1a reconstruit et identifié par SHA256 exact. Capture 2/4 plans, mêmes arguments publics.
- Même sélection locale de banque dans l'îlot Sprite. Les trois couples GetP/RBSR d'affichage passent avant l'îlot, qui passe de 207 à 213 ; les deux stubs capture gardent 204/206. Les cinq RBSR ciblent 213. Les trois mots de token concernés changent d'index, aucune commande ajoutée. Réserve 16384 octets testée par extension fictive de l'îlot ; aucun emplacement de code persistant.
- UNIT142 réassemblée avec retraite mixte et registre v5 dans l'espace S2r libéré ; preuve byte-exacte hors du trou et des quatre dispatchs déjà autorisés ; ancre et taille identiques.
- Public Sprite choisit la profondeur du répertoire validé, prépare l'allocation correspondante, insère le reçu v5, acquiert les canaux et publie via graphics.library. Le Move/Change attaché réutilise P0c/P0d. Le Change revalide la sélection et le snapshot AMOS après les deux WaitTOF avant staging. Pas de conversion de profondeur en cours d'affichage : Off puis Show.
- Palette : aucune écriture ColorMap. Les 15 couleurs attachées occupent les pens 17..31 ; les simples doivent correspondre à leur sous-palette de paire. Hotspot nul, largeur 16, hauteur 1..256, limites d'écran et génération de banque inchangées.
- Off, Bank Free, Close, End utilisent la même retraite v5. Deux fences ne constituent pas une preuve DMA réelle. Les tests CPU/OS modélisés ne remplacent ni WinUAE ni le vrai Compiler.
- CI : reconstruction exacte, capture, régressions historiques et combinaisons 2/4 plans, animation, Move, Off, Bank Free et Close/End. Les bancs hérités résolvent maintenant l'index AP20 depuis le stub et le stride depuis les métadonnées (défauts historiques conservés).
- Avant livraison : Gate A intégrée PASS, campagne ASC dédiée source vérifiée et préflight, autorisation explicite de bascule. Puis Gates B/C et test DMA. Aucun changement de branche.
