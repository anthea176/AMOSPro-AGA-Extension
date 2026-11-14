# Test actif R76 : Aga C2P Open + Convert (14 novembre 2026)

**Priorité : avant ce test de rendu C2P, vérifier sous WinUAE les deux scripts RPG M0 utilisateurs sur la candidate R76 ; rapporter le blocage ou l'absence de Guru. La Gate A R76 reproduit et corrige une corruption clavier/souris introduite par R74.**

**Un seul ASC actif : [C2P_R76_CONVERT_01.asc](C2P_R76_CONVERT_01.asc).** Le test R74 Open validé Gate A/B est conservé dans l'historique Git, mais il n'est plus le test courant. Ne pas lancer GDB ni PowerShell.

**Installation :** remplacer seulement la `AMOSPro_AGA.Lib` active dans le slot habituel d'AMOS par la **R76 v0.13.21** ([binaire du dépôt](../../dist/AMOSPro_AGA.Lib), **54 144 octets**). Conserver `LIBS:c2p.library` v1.9 (déjà utilisé pour R74). Redémarrer AMOS Professional. **CPU 68020+ et écran AGA.** L'ASC utilise la banque DATA 12 : vérifier qu'elle est libre avant le test.

1. Dans AMOS Professional, importer **C2P_R76_CONVERT_01.asc** par **Merge ASCII** dans un programme vide, puis lancer **en interprété uniquement**. **Ne pas compiler** : Gate C unique prévue au jalon final du chantier C2P.
2. La première boucle initialise les **81 920 octets** de la banque (mire chunky complète). Sur chaque écran **16, 32, 64, 128 et 256 couleurs**, le test effectue une ouverture C2P, une conversion + Swap puis une seconde conversion + Swap avec une bande horizontale d'une autre couleur. La mire est volontairement répétitive et la bande du second écran doit être visible. Il attend une VBL avant toute nouvelle tentative sur buffer non Safe.
3. **Sur le dernier écran (256 couleurs), l'image reste affichée jusqu'à Échap** (touche brute 69). Tu peux faire **Alt+Tab** pour une capture : cela ne termine pas le programme. Appuyer sur Échap dans WinUAE ferme ensuite l'écran, ce qui permet d'afficher le résultat final. Après chaque fermeture, la console affiche `COL ... O/DB/C 1 1 1` et `CONV/SW 1 1 1 2 1 1 POST 0`. Les deux conversions et les deux Swap doivent avoir réussi. À la fin : `RESULT 1` et `CLOSE RETURNED`, Chip Free avant/après à contrôler.
4. Envoyer **une capture de la console et une capture du rendu AGA**. La console vérifie les retours ; seule l'observation graphique valide effectivement la conversion sur la vraie bibliothèque.

**Statut de validation :** Gate A 24 scénarios CPU hôte R76 **PASS** ; Gate B interprétée WinUAE R76 **NON TESTÉE**, Gate C Compiler R76 **NON TESTÉE**, Gate D physique **NON TESTÉE**. R73 v0.13.18 `LAST_GOOD` reste intacte, aucune promotion.

[Contrat R75 Convert](../../docs/C2P_R75_CONVERT_CONTRACT_2026-11-14.md) · [rapport CPU R75](../../docs/C2P_R75_NATIVE_GATE_A_2026-11-14.md).
