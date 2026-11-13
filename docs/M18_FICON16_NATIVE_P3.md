# M18/P3 — Fast Icon CPU natif 68000, X libre et pixel exact

**Statut : code proposé et tests CPU Unicorn soumis à la Gate A**, sans bibliothèque installable. Travail sur `main`, sans nouvelle branche. Référence protégée : **R60 v0.13.5 LAST_GOOD**.

## Implémentation

- [`m18_ficon16_native_shifted_emit.py`](../tools/m18_ficon16_native_shifted_emit.py) : nouveau noyau Motorola **68000**, source Unity AGA 16×16 × 8 plans, 288 octets par icône, lecture par le CPU depuis Fast ou Chip, écriture sur les **huit bitplanes du back buffer privé**.
- **X et Y au pixel exact** : X = −15..−1, X = 1..15, les multiples de 16 et les bords fonctionnent sans arrondi silencieux. Division signée de X par 16 avec **ASR** et traitement de deux mots de destination au maximum par ligne et plan. Masques gauche/droite et préservation des pixels voisins ; clipping vertical et du dernier mot incomplet de l'écran.
- **Modes 0 et 1** : opaque y compris la couleur 0, ou transparent lorsque la couleur source est zéro selon le masque Unity. Pas de conversion silencieuse de la transparence AGAPIC indépendante.
- **ABI interne inchangée par rapport à P2** : A0=slot déjà validé, A1=table de 8 pointeurs Chip déjà validés, D0=X signé, D1=Y signé, D2=stride en octets, D3=mode 0/1, D4=largeur pixels, D5=hauteur. Retour D3=1 succès/no-op ou D3=0 rejet, D2=0, A3 intact ; autres registres sauvés, pile équilibrée.
- Validations avant écriture : coordonnées signées 16 bits, mode, largeur/hauteur, stride pair suffisant, pointeurs de source/table/8 bitplanes non nuls et pairs. Les adresses réelles, l'appartenance au back buffer, la Safe et la taille de l'allocation restent **à contrôler par le futur wrapper**.

## Tests

[`test_m18_ficon16_native_shifted.py`](../tools/test_m18_ficon16_native_shifted.py) pilote les vraies instructions dans **Unicorn M68000**, puis compare les huit bitplanes octet par octet au modèle P1 indépendant ; positions négatives, tous les décalages X de 0 à 15, masques opaque/transparent/partiel, quatre côtés, dernier mot partiel. Comparaison aussi avec le noyau aligné P2 sur des positions communes. Vérifications de la source immuable, des gardes mémoire, de l'ABI, de la pile et du refus sans écriture.

**À confirmer :** résultat de la Gate A CI de ce commit. Aucun résultat WinUAE/Compiler n'est déduit du succès du simulateur CPU.

## Après validation

Le chemin CPU **P2 aligné** reste une optimisation spécifique ; **P3 général** est le fallback pixel exact. Étapes suivantes, à traiter séparément : wrapper AP20 et banques AMOS Fast Icon (identifiant 1-based), validation back buffer/Safe, puis cache Chip avec source masquée et copie Blitter réelle, et enfin benchmark **8 plans à rendu identique**, coûts Fast→Chip compris. Aucun changement de backend définitif avant cette mesure.

**Pas de nouvelle API publique, de banque créée, d'ASC actif, de binaire R61, de Gate B/C/D ou de changement de `LAST_GOOD`.**
