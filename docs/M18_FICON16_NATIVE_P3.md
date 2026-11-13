# M18/P3 — Fast Icon CPU natif 68000, X libre et pixel exact

**Statut : Gate A CPU 68000 PASS** sur [GitHub Actions 43398986441](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43398986441), sans bibliothèque installable. Travail sur `main`, sans nouvelle branche. Référence protégée : **R60 v0.13.5 LAST_GOOD**.

## Implémentation

- [`m18_ficon16_native_shifted_emit.py`](../tools/m18_ficon16_native_shifted_emit.py) : nouveau noyau Motorola **68000**, source Unity AGA 16×16 × 8 plans, 288 octets par icône, lecture par le CPU depuis Fast ou Chip, écriture sur les **huit bitplanes du back buffer privé**.
- **X et Y au pixel exact** : X = −15..−1, X = 1..15, les multiples de 16 et les bords fonctionnent sans arrondi silencieux. Division signée de X par 16 avec **ASR** et traitement de deux mots de destination au maximum par ligne et plan. Masques gauche/droite et préservation des pixels voisins ; clipping vertical et du dernier mot incomplet de l'écran.
- **Modes 0 et 1** : opaque y compris la couleur 0, ou transparent lorsque la couleur source est zéro selon le masque Unity. Pas de conversion silencieuse de la transparence AGAPIC indépendante.
- **ABI interne inchangée par rapport à P2** : A0=slot déjà validé, A1=table de 8 pointeurs Chip déjà validés, D0=X signé, D1=Y signé, D2=stride en octets, D3=mode 0/1, D4=largeur pixels, D5=hauteur. Retour D3=1 succès/no-op ou D3=0 rejet, D2=0, A3 intact ; autres registres sauvés, pile équilibrée.
- Validations avant écriture : coordonnées signées 16 bits, mode, largeur/hauteur, stride pair suffisant, pointeurs de source/table/8 bitplanes non nuls et pairs. Les adresses réelles, l'appartenance au back buffer, la Safe et la taille de l'allocation restent **à contrôler par le futur wrapper**.

## Tests

[`test_m18_ficon16_native_shifted.py`](../tools/test_m18_ficon16_native_shifted.py) pilote les vraies instructions dans **Unicorn M68000**, puis compare les huit bitplanes octet par octet au modèle P1 indépendant ; positions négatives, tous les décalages X de 0 à 15, masques opaque/transparent/partiel, quatre côtés, dernier mot partiel. Comparaison aussi avec le noyau aligné P2 sur des positions communes. Vérifications de la source immuable, des gardes mémoire, de l'ABI, de la pile et du refus sans écriture.

**Gate A confirmée : PASS sur le commit `328ccb9` et le workflow 43398986441.** Le noyau produit **696 octets de code 68000**. Unicorn valide **528 comparaisons pixel/ABI**, **16 équivalences avec le noyau aligné P2** et **18 refus sans écriture**. Le correctif de bord droit porte sur un piège Motorola 68000 : le masque `$8000` doit être écrit en **WORD**, car `AND.W <disp>(A2),Dn` relit la première moitié d'un slot (et non le mot bas d'un LONG `$00008000`). Tests : huit bitplanes comparés octet par octet au modèle P1, quatre couvertures d'icônes, X libre dont négatif, transparence, clipping aux quatre bords, mémoire sentinelle et préservation pile/registres. **Ce PASS reste CPU sous Unicorn : aucun résultat WinUAE, Compiler, performances, Blitter DMA ni Amiga physique n'en découle.**

## Après validation

Le chemin CPU **P2 aligné** reste une optimisation spécifique ; **P3 général** est le fallback pixel exact. Étapes suivantes, à traiter séparément : wrapper AP20 et banques AMOS Fast Icon (identifiant 1-based), validation back buffer/Safe, puis cache Chip avec source masquée et copie Blitter réelle, et enfin benchmark **8 plans à rendu identique**, coûts Fast→Chip compris. Aucun changement de backend définitif avant cette mesure.

**Pas de nouvelle API publique, de banque créée, d'ASC actif, de binaire R61, de Gate B/C/D ou de changement de `LAST_GOOD`.**
