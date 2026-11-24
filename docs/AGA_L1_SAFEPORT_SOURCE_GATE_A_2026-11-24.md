# L1 — Correctif SafePort des deux writers P0, qualification source-only

**24 novembre 2026 · main exclusivement · auteur « ok go » après L0.**
Référence P2d exacte : 136 020 octets, SHA256 ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f, 100 commandes / 203 entrées. Gate A ASM historique reconfirmée par run 45396999267. Active S1-P1e 142 000 octets SHA256 1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106 préservée. **Aucune Lib distribuée, aucune promotion.**

## 1. Périmètre et choix

- AGA-001 : IFF Load. Après les deux préconditions de parsing/validation BODY et l'allocation de la table RGB, avant WaitBlit puis seconde passe écrivant les plans, acquisition Safe conditionnelle. Vérification du bitmap déjà sélectionné. Refus immédiat D3=0, D2=0 par le chemin cleanup historique, aucune mutation de plans ni ColorMap.
- AGA-010 : Back Fill. Après vérification du bitmap back et avant allocation RastPort, même acquisition. **Choix de compatibilité** pour l'instruction sans retour : un essai immédiat, maximum trois WaitTOF et trois nouvelles tentatives ; port manquant ou timeout = retour sans dessin. Ne pas confondre retour de contrôle avec succès de remplissage. Préservation du masque pen sur 8 bits, SetRast plein bitmap y compris padding, WaitBlit et FreeVec. Aucun Swap implicite.
- Acquisition commune : GetMsg(-372) du port DB+12 seulement si DB+20 bit0 posé ; effacer uniquement bit0 sur message réellement obtenu, jamais Disp bit1. Aucun WaitPort.
- AGA-011 Screen Pattern : inchangée, cible physique réelle à qualifier. AGA-002 premier Bind B8 : lot L2. Contrat Clear→décor→Swap inchangé.

## 2. Implémentation sans déplacer l'historique

[Commit source 4ae2dfb](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/4ae2dfbce3cf9c089f4c4da1be865dd2246dee64).
[Overlay ASM](../src/native/m19_p2d_l1/) et [builder](../tools/build_m19_p2d_l1_safeport_in_memory.py). Le builder reconstruit P2d depuis le builder historique, compare LAST_GOOD et le master éditable direct vasm MC68020, puis assemble une copie temporaire des **sources** avec les deux relais BRA.L de 6 octets. Le helper est append-only dans UNIT142, sous la limite Compiler 65534 octets. Les anciens labels/offsets State et les sept LEA sont conservés par comparaison exacte de tout le préfixe hors deux points de patch. Tous les autres AP20 inchangés, mêmes tokens, mêmes PC16, mêmes groupes ; titre distinct L1. Repack en mémoire, aucune sortie installable.

## 3. Gate A

[Commit tests e7eb631](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/e7eb63176c9d262ce01ab560cf01c89a960c4b58).
[Test](../tools/test_m19_p2d_l1_safeport_gate_a.py) et [workflow lecture seule](../.github/workflows/m19-p2d-l1-safeport-gate-a.yml). Vasm épinglé 8b85ef6 ; Unicorn MC68020, deux modèles AP20 (BSR.W et JSR absolu). Teste le vrai code assemblé de Back Fill et IFF complet (DOS/Exec/Gfx simulés, deux bitmaps, BODY brut/ByteRun1, palette, padding, ABI, cleanup, alloc failure, Safe absent/disponible/acquis, latence jusqu'à 3 VBL, refus/reprise). Le simulateur SetRast représente l'effet du Blitter, pas le DMA réel. Le témoin P2d sans Safe pending doit conserver les résultats. **Gate A PASS — 172 cas**, source et identité vérifiées, voir preuve ci-dessous. Aucun essai WinUAE ni Compiler réel ni matériel. Une Gate A positive ne permet pas de remplacer automatiquement dist ou LAST_GOOD.

T04/T05/T12/T19 partiellement couverts par cette Gate A ; T06/T17 et toutes les Gates B/C restent ouvertes. Le banc intégré historique unique reste intact. Aucun changement de la syntaxe AMOS.

## 4. Résultat Gate A exact (13:03 UTC)

[CI PASS 45399337278](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45399337278), [job 138463494082](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45399337278/job/138463494082), [commit 072907c](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/072907ca78f3a9577ca44fbee69bac22ff513941). Politique [CPU/delivery PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45399337110). Le premier essai 45399089924 avait assemblé et vérifié les octets/liaisons puis échoué sur notre comptage incluant le token dummy AP20 initial. Le test a été aligné sur le comptage des commandes nommées du contrôle README ; les assertions sur les octets des tokens, les 203 entrées et les PC16 sont conservées. Aucun changement ASM entre ce refus du builder et le PASS.

| Métadonnée | Mesure réelle CI |
|---|---|
| Candidate P2d-L1 (RAM uniquement) | 136 248 octets |
| SHA256 | `f3adabb4c7f0f8d103586ee8eeb6b1db6a3e3cde5fe86ca16788eceb7b65cbcb` |
| UNIT142 | 62 960 octets (62 740 + 220) |
| Taille maximale AP20 | 65 534 ; marge UNIT142 2 574 octets |
| Relais Back Fill, IFF | UNIT142+62804 / +62870 (cibles calculées) |
| Commandes / entrées | 100 / 203, inchangées |
| PC16 max | 854, ensemble des liens inchangé |
| Gate A MC68020 | PASS 172 cas, dont témoins P2d et modèles de relocation BSR.W/JSR absolu |
| Gate B/C/D | NON TESTÉES |

**AGA-001/010 : correctifs source L1 qualifiés en A, non installés.** Les observations sur la bibliothèque P2d officielle restent valables jusqu'à une bascule autorisée. AGA-011 Screen Pattern et AGA-002 B8 restent hors de ce correctif. S1-P1e active et LAST_GOOD P2d intacts ; aucune promotion. L'étape suivante recommandée est de qualifier T06 puis L2 source-only et préparer une campagne B/C unique ; toute bascule de la Lib exige l'accord auteur. Ne pas annoncer les scénarios T04/T19 intégralement PASS en WinUAE.
