# M6 R15 0.7.2 — Aga Blit Clear (PASS AMOS/WinUAE)

**Clôturé pour le test AMOS interprété/WinUAE le 10/11/2026 :** `Aga Blit Clear(x,y,w,h)` Gate A (CPU/CI) **PASS** ([GitHub Actions #42857827475](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42857827475)) et Gate B **PASS** sur MYGIRL.IFF. Gate C AMOS Compiler et Gate D Amiga réel **NON TESTÉES**.

## Artefacts officiels

| Élément | Fichier |
|---|---|
| **Candidat courant** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — **R15 0.7.2, 9 784 octets** |
| **Archive exacte** | [`dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib`](../dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib) |
| **SHA256 R15** | `44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e` |
| **Base figée R14 Fill** | `dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib`, SHA256 `a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f` |
| **LAST_GOOD** | `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1, **protégée** |
| **Builder** | `tools/build_m6_blit_clear_r15.py` |
| **CPU et ABI** | `tools/test_m6_blit_clear_r15.py` |
| **Test AMOS passé** | [`tests/passed/M6_R15_BLIT_CLEAR_01.asc`](../tests/passed/M6_R15_BLIT_CLEAR_01.asc), contenu inchangé |

## Contrat fonctionnel

```amos
_OK=Aga Blit Clear(x,y,width,height)
```

La fonction met les pixels d'un rectangle du **back buffer** à l'**index de palette 0**, avec origine (0,0) en pixels. Il s'agit d'un effacement à l'index 0, **pas nécessairement d'un noir RGB strict**, car la palette peut associer une autre couleur à cet index.

- **1** : tous les bitplanes ont été effacés et synchronisés.
- **0** : rectangle hors limites, dimensions nulles/négatives, absence de double buffer ou de Bitmap valide, ou échec d'une opération. Comme pour Fill, une erreur AmigaOS sur un plan tardif peut avoir déjà modifié des plans antérieurs.
- Même gestion sûre des bornes, des pointeurs de bitplanes et des `WaitBlit` que le **Fill R14 validé**. Aucun accès direct aux registres chipset ajouté.
- Le front buffer n'est pas modifié par notre routine ; l'affichage intervient à `Aga Swap`.

## Implémentation minimale, sans duplication de Fill

Le code R15 contient **une routine d'adaptation de 38 octets en 68000**, pas une nouvelle réimplémentation du Blitter :

1. AMOS appelle `Clear` avec `D3=h` et trois longs sur `(A3)+` : `w,y,x`.
2. La routine constitue sur la pile CPU un bloc temporaire `[h,w,y,x]`, place son adresse dans A3 et force `D3=0` (index couleur).
3. **`BSR.W` vers l'entrée R14 `Aga Blit Fill` existante.** Ce code validé effectue les contrôles, les `BltBitMap` plan par plan et les `WaitBlit`.
4. La routine restaure la pile CPU et avance l'A3 **original** de 12 octets, puis renvoie le résultat entier en `D3`, `D2=0`.

**Contrôles de non-régression AP20 :** entrées R14 **0..19 strictement identiques** ; entrée 20 Fill prolongée uniquement par le séparateur `GetP` ; entrée 21 nouvelle commande Clear, signature `00,0,0,0`. Le saut PC-relatif est validé contre le début réel de l'entrée 20. Builders R13 et R14 historiques peuvent régénérer leurs archives, **sans écraser l'actif R15**.

## Validation prévue

**Gate A : PASS** ([CI #42857827475](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42857827475)). Unicorn/Capstone 68000 : **27 scénarios Clear valides + 25 rejets/erreurs** ; A3 +12 octets, SP équilibrée, BSR vers la vraie entrée Fill, 1/2/4/8 plans, coordonnées limites et non alignées, pixels exacts, conservation du contour, rejets sans écriture et échec simulé, régressions Fill R14 et Copy R13. HUNK/AP20, SHA256 et builder reproductible également PASS.

**Gate B : PASS AMOS Professional interprété/WinUAE**, d'après deux captures utilisateur datées du 10/11/2026. Avec **MYGIRL.IFF 320×256×8**, deux rectangles colorés ont leur intérieur effacé et le premier apparaît recopié en bas. Les appels invalides retournent 0. **Sortie observée :**

```text
F1 1 C1 1 F2 1 C2 1
NEG 0 EDGE 0 ZERO 0
COPY 1 SWAP 1
KEY 97 CLOSE RETURNED
```

Le retour AMOS est confirmé par `End of program at line 79.` **Gate C Compiler et D vrai Amiga : NON TESTÉES.** Ne pas promouvoir R15 dans `LAST_GOOD` sans décision explicite. Le test WinUAE complète ici la CI, sans certifier un fonctionnement exhaustif.

## Suite

**M6 clôturé pour ses trois commandes sous AMOS interprété/WinUAE :** Copy R13, Fill R14, Clear R15. Le test R15 est archivé à l'identique dans `tests/passed/` et `tests/current/` est vide de `.asc`. R15 reste le candidat courant ; R10 `LAST_GOOD` est inchangée. Compiler, matériel et stress restent en dehors de cette clôture.
