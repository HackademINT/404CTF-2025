# Comment est votre température ?
Vous êtes en charge de surveiller les serres où poussent les plantes destinées à l'alimentation des passagers du vaisseau dans lequel vous voyagez. Cependant, en arrivant ce matin, vous vous rendez compte que l'écran d'affichage ne fonctionne plus : impossible de savoir quelle est la température et l'hygrométrie de la serre ! Ce sont des données capitales pour s'assurer que les végétaux poussent correctement, vous devez trouver un moyen de récupérer ces valeurs. Vous décidez de vous pencher sur le circuit.
***
Le circuit est basé sur un microcontrôleur qui dialogue avec un capteur SHT40, vous trouverez les spécifications de ce dernier dans les ressources du challenge. Trouvez le numéro de série du capteur ainsi que les valeurs de température (en °C) et d'hygrométrie (en %RH) **réelles** arrondies à l'entier inférieur.
***
Le flag (insensible à la case) est au format `404CTF{<numero de série en hexadécimal>|<température>|<hygrométrie>}`.
> Par exemple si le numéro de série est 7ab01a3e, que la température calculée est de 25.86°C et que l'hygrométrie est de 87.334%RH, le flag sera 404CTF{7ab01a3e|25|87}.
***
Ressources:
- [challenge.csv](challenge.ino)
- [datasheet](HT_DS_Datasheet_SHT4x.pdf)
***
Write-up : https://www.acmo0.org/2025-06-01-404CTF-2025-Hardware-Writeup/#comment-est-votre-temperature-