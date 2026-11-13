# M18/R65 — Test unique WinUAE interprété, Gate B PASS

**Candidate active R65 v0.13.10** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **40 116 octets**, SHA256 `6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2`, 58 commandes/65 AP20, [Gate A native 98 cas + modèle hôte 44 PASS, CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43444242260). **R63 `LAST_GOOD` protégée**, Gate C Compiler **uniquement à la fin de M18**, D physique non testée.

**Gate B interprétée du 13/11/2026 : PASS**, deux captures de l'auteur. `RESULT 1`, `CLOSE RETURNED`, deux icônes multicolores conformes au rendu transparent/opaque, formats et masques corrects, banques libérées. [Rapport détaillé](../../docs/M18_R65_FICON8_PUT_WINUAE_GATE_B_2026-11-13.md). **Cette page conserve le protocole pour reproduction ; il n'est plus en attente.**

**Un seul ASC actif** : [`M18_R65_FICON8_PUT_01.asc`](M18_R65_FICON8_PUT_01.asc). Partir d'un programme vide sous AMOS Professional, **Project → Merge ASCII**, puis exécuter **en interprété uniquement** (pas de Compiler). **Les banques 12 et 13 doivent être libres** : `Reserve As Data 13,256` est destructeur s'il existait déjà une banque n°13. Utiliser une session WinUAE jetable. Le test écrira/écrasera `RAM:M18_R65_FICON8.ABK`.

**Protocole :** R64 `Aga F Icon Bank Create(12,4)`, `Reserve As Data 13,256`, 256 `Poke` d'indices couleur, nouvelle commande `Aga F Icon Bank Put` vers slots 1 et 2. Vérifier `SIZE/COUNT 1164/4`, masque première ligne `0`, premier plan `65535`, masque ligne 1 `16380`, premier plan ligne 1 `32771`, slot3 intact, mauvais paramètres rejetés. **Chip et Fast Free avant/après Erase** doivent être égales. `Save/Erase/Load` ABK sur RAM: puis écran AGA 256 couleurs.

**Contrôle visuel :** fond bleu, deux icônes 16×16 à cadre blanc et diagonales **rouge et verte**. À **X=30**, transparence : intérieur bleu ; à **X=90**, opaque : intérieur noir. Une icône vide à X=150 en transparent doit laisser le fond bleu. Relever `RESULT 1`, `CLOSE RETURNED` et absence de Guru. La mémoire après écriture du fichier RAM: est informative, **pas** une mesure de fuite.

L'ASC R64 validé est archivé **à l'identique** dans [`tests/passed/M18_R64_FICON8_CREATE_01.asc`](../passed/M18_R64_FICON8_CREATE_01.asc) ; les banques ABK historiques de test restent disponibles mais ne sont pas utilisées ici.
