# M11/R26 AGA Text — test courant

**Un seul fichier AMOS actif :** [`M11_R26_AGA_TEXT_01.asc`](M11_R26_AGA_TEXT_01.asc). **WinUAE non testé**. Utiliser la **candidate R26 0.9.2** ([binaire](../../dist/AMOSPro_AGA.Lib)), et non l'archive R25.

Importer avec `Project → Merge ASCII`, sélectionner `examples/demo.iff` 320×256×8. Observer pendant environ 220 VBL un **texte vert « AGA TEXT R26 » sur un rectangle bleu**. La console finale doit montrer `BAD 0 TEXT 1 SWAP 1`, `RESULT 1` et `CLOSE RETURNED`. **Ne pas confondre ce texte natif extension avec la commande `Text` d'AMOS.**

Gate A CPU/CI : **64 cas PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42921696298)). Gate B AMOS/WinUAE et Gates C/D encore non testées ; conserver cet unique `.asc` courant jusqu'au résultat réel de l'utilisateur. [Contrat R26](../../docs/M11_TEXT_R26.md).
