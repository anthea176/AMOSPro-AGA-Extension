# OPT020/P3 — R73 v0.13.18 : Gate B WinUAE interprétée

**Unique bibliothèque de travail :** `dist/AMOSPro_AGA.Lib` R73, **51 608 octets**, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`, 64 commandes, 71 entrées AP20. **Gate A native/ABI ciblée PASS** ; première tentative Gate B intégrée **RESULT 0** à cause du mélange de profondeurs dans l'ASC initial. **Nouvel ASC deux phases : Gate B à rejouer**, Compiler Gate C **différée jusqu’à la fin d’OPT020**. [Rapport P3](../../docs/OPT020_P3_FAST_ICONS_68020_2026-11-13.md).

**Unique ASC actif :** `OPT020_P3_R73_INTERPRETED_01.asc`. Utilise deux banques distinctes, **10 = AGAPIC v1** `M16_AGAPIC_SAMPLE_BANK10.abk` et **11 = FICON8** `M18_FICON8_SAMPLE_BANK10.abk`. Ces `Load` remplacent les banques 10/11 existantes : exécuter dans une session WinUAE de test.

- WinUAE **AGA, 68020 à 14 MHz, JIT OFF, PAL**, AMOS Professional **interprété seulement**. Installer la R73 dans l’unique slot AGA d’`APSystem`, redémarrer complètement AMOS.
- **Phase 1 — 320×256, 16 couleurs / 4 plans** : banque AGAPIC4, `Clear → Fill`, puis `Aga Image Draw` P2, `Aga Image Region` P1e et dessin bancaire historique. L'écran est échangé, maintenu pour l'inspection visuelle, **fermé**, puis les refus hors écran et `Chip Free` sont relevés.
- **Phase 2 — 320×256, 256 couleurs / 8 plans** : ouvre un nouvel écran, puis `Aga F Icon` opaque, masqué, décalé et clippé ; `Aga F Icon Capture` après dessin opaque, comparaison des **288 octets** avec le slot source, refus banque/ID/coordonnées invalides et contrôles après fermeture. **Ne pas exécuter P1e/P2 AGAPIC4 dans cette phase** : le moteur refuse correctement une profondeur différente.
- La console doit montrer les retours attendus, **`FICON CAP/EQ288 1 1`**, `RESULT 1`, `CLOSE RETURNED`, **Chip Free début/intermédiaire/fin identique**, et **aucun Guru**. Le résultat sera à confirmer par les captures réelles de l’auteur : la CI ne remplace pas WinUAE.
- Ne pas mesurer de gains et **ne pas lancer AMOS Compiler** dans ce jalon. Gate C unique en fin de chantier OPT020.

**Intouchables :** R68 `dist/AMOSPro_AGA_LAST_GOOD.Lib` (51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`), archives, `tests/passed/`. R72 interprétée A/B PASS conservée dans l’historique Git (51 468 octets). Aucun second binaire ni ASC de travail.
