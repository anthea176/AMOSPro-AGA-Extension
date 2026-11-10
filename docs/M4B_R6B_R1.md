# M4b R6B-R1 — séparation Swap / synchronisation finale

Le premier R6B a montré un blocage runtime dans `Aga Swap` alors que WinUAE et AMOS restaient réactifs.

La cause est isolée comme une attente bloquante interne à l'extension. Le protocole RKRM ne demande pas d'attendre systématiquement Safe puis Disp immédiatement après chaque `ChangeScreenBuffer`.

R6B-R1 transforme donc le test en diagnostic en deux phases :

1. `Aga Swap` effectue un seul `ChangeScreenBuffer`, met à jour l'index et marque la transition en vol, puis retourne.
2. `Aga Screen Close` attend les notifications finales Safe et Disp avant de libérer les ScreenBuffers et les ports.

Cette révision ne prétend pas encore implémenter une boucle double-buffer complète. Elle sert à localiser précisément la notification ou l'étape qui bloque avant de généraliser le protocole.

Artefact :
- `dist/experimental/AMOSPro_AGA_M4b_v0.0.8_R6B_R1.Lib`
- 2472 octets
- SHA256 `6c5e4dba8d91a2d80abc45630155a18e86bc663667441529acec1e47a9b9da15`
- jumps `185,2,8,8,48,167,193,75,141,15,141,70,1,0`
