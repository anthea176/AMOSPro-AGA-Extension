# Test actif — M19 P0a MC68020 : banque Bob AGBO multi-images

**Bibliothèque active unique :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **79 660 octets**, SHA256
`e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0`.
**ASC actif unique :** [`M19_P0A_MC68020_BANK_GET.asc`](M19_P0A_MC68020_BANK_GET.asc).

**Configuration de test fonctionnel de l'auteur :** WinUAE **68030 + JIT activé**, AGA PAL.
**68020 sans JIT : réservé aux benchmarks** (pas à cette campagne).
Code natif **68020 minimum**, sans chemin 68000. **Gate A MC68020 PASS 74 scénarios** ;
**Gate B WinUAE et Gate C Compiler réel NON TESTÉES**.

## Lancer

1. Installer exactement [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib)
   sous le nom `AMOSPro_AGA.Lib` dans le slot d'extension `APSystem` ; redémarrer AMOS.
2. Créer un programme vierge. Importer
   [`M19_P0A_MC68020_BANK_GET.asc`](M19_P0A_MC68020_BANK_GET.asc)
   via **Project → Merge ASCII**, pas via `Load`.
3. Exécuter d'abord en interprété / Runtime, puis dans AMOS Compiler V2.
   Récupérer le journal `RAM:M19_P0A_INTERPRETED.TXT`,
   `RAM:M19_P0A_RUNTIME.TXT` ou `RAM:M19_P0A_COMPILED.TXT` suivant le mode.
4. Attendu après exécution réelle : `PASS ERR 0`, `ABK RELOADED 1`,
   `CLOSE RETURNED 1`. Toute erreur ou Guru constitue un échec.

**Ressources externes : aucune.** Les formes sont dessinées par `Aga Blit Fill`,
les images sont capturées par `Get AGA Bob`, et le fichier ABK est généré
dans `RAM:` par le programme. La banque AMOS 24 doit être libre au lancement.

## Conservation des anciens jalons

- **R88 v0.13.33 source figée :** [archive originale 75 040 octets](../../dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib),
  SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`.
- **R84 LAST_GOOD :** [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib),
  SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` ; inchangée.
- L'ancien ASC R88 P2.8 n'est plus dans `tests/current/` :
  son contenu est conservé par l'historique Git du jalon R88
  (Git blob `001396551cad6fed57903b714bc374e0988f63ea`).
  Les anciennes ressources ABK/IFF de la campagne R88 restent inchangées,
  mais ne sont pas utilisées par le test P0a.

**Ce n'est pas une promotion LAST_GOOD.** Ne jamais déduire une Gate B/C des seuls tests CPU.
