# M19 P0h — précontrôle natif d'une frame de 64 Bobs

## Objet et provenance

Cible **MC68020 minimum**, source exclusive sur `main`. Hérite du **P0g Gate A PASS** : [lecteur vérifié](../tools/m19_p0g_checked_read_emit.py) et [builder source-pinné](../tools/build_m19_p0g_checked_read_in_memory.py), candidate 96 752 octets, SHA256 `e1f8f8c04e24a38651ade50b6878cffb1dd288a766b104fb5c9fa9ae314d9536`.

L'entrée privée `frame_bank_preflight_entry` examine les IDs **1 à 64 dans l'ordre**. Une lecture brute refusée signifie « objet non actif / indisponible » et l'ID est ignoré ; **si une lecture brute réussit mais que `identity_check` refuse, toute la frame échoue** avant DMA. Le résultat de frame est **D3=1/0, D2=0**. Cette étape ne dessine rien, ne prépare aucune allocation Chip, ne fait aucun `Swap` et n'expose pas encore `Aga Bob Draw`.

Le source P0g ayant déjà une portée PC16 de 32 590 octets (marge seulement 176), le nouveau précontrôle est intégré dans **un layout AP20 V2 par îlots** et non en ajout direct à l'ancienne table : quatre groupes natifs et 85 commandes inchangés ; stubs `GetP` remis aux emplacements requis. Les groupes AGA et toutes les sources publiques sont conservés, et l'ancienne Lib installée n'est **pas modifiée**.

## Source, Gate A et limites

- [Émetteur natif](../tools/m19_p0h_frame_preflight_emit.py) : vérification CPU, propriétaire AMOS, état AGA ouvert ; boucle privée avec scratch sur pile, lecture brute puis lecture vérifiée pour chaque objet actif.
- [Builder AP20](../tools/build_m19_p0h_frame_preflight_in_memory.py) : reconstruction uniquement en mémoire depuis P0g, appel au `dispatch_islands`, contrôles ABI, HUNK, groupes inchangés et PC16.
- [Banc MC68020](../tools/test_m19_p0h_frame_preflight_gate_a.py) : exécution dans Unicorn sur les deux implantations de groupes, plus test des 64 IDs et refus d'une banque à identité périmée.

**Gate A MC68020 : PASS**, [CI M19 44153906156](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44153906156) : **60 contrôles** en deux implantations natives (interpreted/compiled simulés) ; 64 objets actifs, dernier objet sur une autre banque, corruption de génération du 64e objet refusée après 63 objets conformes, CPU <020 refusé, propriétaire AMOS incorrect, fausse signature AGA avant Init, fermeture/inactivation. **Gate B Runtime / Gate C véritable Compiler / Gate D Amiga réel : NON TESTÉES pour P0h.** Aucun binaire ou ASC actif modifié.

**Provenance figée** : émetteur BOBS MC68020 **16 762 octets** (suffixe privé 318), SHA256 `2d5a9e7a7f53696427786e4cdaffd0786b9cbcdfa5b9f2039cdef480dcd6cc8b`. Bibliothèque AP20 **uniquement reconstruite en mémoire** : **97 248 octets**, SHA256 `2c5c371754a3b54c797c7b413769ef2536db92cdad7eba3db8185bb88dea7782`, **85 commandes, 178 entrées, 4 unités** aux indices 142/153/156/177, portée PC16 max **854**. Ces deux SHA et tailles sont contrôlés par les builders ; ne pas confondre la candidate en mémoire avec `dist/AMOSPro_AGA.Lib` installée.

### Limite fonctionnelle avant le dessin

Les helpers existants `registry_prepare`, `registry_lookup` et `safe_bank_blit` travaillent avec la **banque sélectionnée par `Aga Bob Bank`**, tandis que chaque Bob peut conserver une autre banque source. Le prochain jalon doit résoudre ce routage Chip **sans détruire la sélection utilisateur, sans banque AMOS supplémentaire et sans recopie par frame**. Le contrôle P0h ne prouve pas encore l'existence de l'image, son allocation Chip, sa compatibilité avec l'écran ou la capacité de rendre une frame atomiquement.

**Bibliothèque active protégée :** `dist/AMOSPro_AGA.Lib`, 96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`. Aucun changement à `LAST_GOOD`, aux archives ni au seul ASC.
