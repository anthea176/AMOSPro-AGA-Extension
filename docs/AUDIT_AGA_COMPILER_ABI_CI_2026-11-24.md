# Passage 20 — Compiler, ABI, AP20, relocations et CI

**24 novembre 2026 — passage 20/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

## 1. Construction et compatibilité

[build_m19_p2d_in_memory.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/tools/build_m19_p2d_in_memory.py) vérifie l'ancêtre P2c, réunit BOBS et service, recalcule mapping tokens/stubs et vérifie les limites, unpack AP20, HUNK et signatures. P2d : 203 entrées, BOBS 60 928 octets, marge arithmétique 4 608 octets par rapport à 65 536 ; **ce n'est pas un budget de patch garanti**. Le pc16_max=854 rapporté concerne les déplacements de stubs vérifiés par ce builder, pas toutes les branches natives.

[M19_P2D_BOBS_EDITABLE](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_BOBS_EDITABLE.s) préserve les formes ABI AMOS Main et les index GETADR=797, CHANGE=819, LIST_CREATE=91, LIST_DELETE=93. Les pseudo-ops ($FE11,$F700,index), formats PC32 explicites, valeurs State+offset et sept LEA input ne doivent pas être convertis en adresses supposées libres. Préserver GetP, convention D3/D2 et avancée A3 selon la signature, les registres et les appels OS MC68020.

[build_m19_p2d_editable_asm.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/tools/build_m19_p2d_editable_asm.py) contient la preuve de reconstruction source. Le master [M19_P2D_LINKED_EDITABLE.s](../src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s) a historiquement été assemblé byte-identique avec vasm -Fbin -m68020 -no-opt. Aucun nouveau calcul de SHA ni assemblage ici. Toute future correction doit recalculer liaisons AP20, tailles, PC16/PC32, offsets State et comparer les sept LEA ; ne pas modifier le reliquat de données historique R80 sans preuve d'accessibilité.

## 2. AGA-005 : contradiction actuelle de cibles CI

| Source | Constat |
|---|---|
| [active_library.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/tools/active_library.py) | S1-P1e explicitement reconnue comme active, P2d comme LAST_GOOD. Validation séparée des SHA et du préfixe AP20 hérité. |
| [build_m19_s1p1e_get_sprite_ap20.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/tools/build_m19_s1p1e_get_sprite_ap20.py) | Construction S1 à partir de P2d exacte, 2 tokens ajoutés, liens PC16 historiques conservés. |
| [test_current_input_state_offsets.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/tools/test_current_input_state_offsets.py) | BINARY=dist/AMOSPro_AGA.Lib ; chemin spécifique P2d exige active==frozen. S1 absente des branches d'identité reconnues par ce contrôle historique : ne pas déduire une corruption input de ce rejet. |
| [m19-p2d-editable-asm.yml](../.github/workflows/m19-p2d-editable-asm.yml) | Le contrôle final impose la SHA P2d aux **deux** Lib. Déclencheurs source, planification et manuel. Sur l'état gelé actuel, cette assertion ne peut pas être vraie si l'étape est atteinte. |
| [artifact-regression-full.yml](../.github/workflows/artifact-regression-full.yml), [artifact-integrity.yml](../.github/workflows/artifact-integrity.yml), [aga-docs-fast.yml](../.github/workflows/aga-docs-fast.yml) | Périmètres et déclencheurs distincts. Le workflow docs ne constitue ni validation de tout le natif ni essai AMOS. |

AGA-005 **P2 confirmé sur le code des contrôles**, indépendamment de toute nouvelle exécution. Il faut cibler explicitement P2d gelée par son chemin/SHA et S1 par son propre contrat ; contrôler la conservation des entrées héritées et les sept opérandes dans les deux contextes si applicable. Ne jamais supprimer une assertion de sécurité, accepter arbitrairement toute SHA, ou remplacer la candidate par LAST_GOOD pour rendre la CI verte.

## 3. Gates et preuve

A = vérifications CPU/source/AP20/HUNK avec services simulés ; B = vrai Runtime WinUAE et ASC exact, C = vrai exécutable produit par AMOS Compiler et même oracle, D = matériel. Un succès A, un dump d'AP20 ou un script docs vert ne prouve jamais C.

P2d conserve les 2 PASS historiques sur le seul M19_P2_ALL_IN_ONE.asc exact. S1-P1e conserve sa Gate A historique, pas de transfert B/C/D. Le journal doit identifier le vrai binaire installé, le mode Prg State et les assets. Les variantes T07/T14 et la qualification B/C du nouveau binaire corrigé restent à réaliser après autorisation. T15 Sprite suspendu.

**Bilan :** aucune nouvelle anomalie Compiler reproduite ; AGA-005 et cohérence documentaire AGA-012 à régler dans une phase distincte autorisée. Pas de changement des workflows ni des scripts.
