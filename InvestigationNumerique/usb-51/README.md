# USB 51

Niveau `intro`

## Description

Un document contenant des données sensibles de l'ESA (Agence Spatiale Européenne) semble avoir été exfiltré. 
Retrouvez le contenu du fichier que l'attaquant a récupéré, ainsi que ce qui pourrait se cacher dans celui-ci...

## Ressource

`capture.pcapng`

## Solve

La capture contient des trames USB, en l'ouvrant avec Wireshark et en cherchant très légèrement dedans on trouve un paquet d'environ 48ko correspondant à l'écriture d'un fichier, visiblement un pdf.

Pour l'exporter : `selectionner le paquet intéressant` -> `Leftover Capture Data` -> `fichier` ou `clic droit` -> `Exporter Paquets Octets...` -> `enregistrer`

Après avoir récupéré le pdf, on remarque cette séquence binaire étrange dedans

```
00110100 00110000 00110100 01111011 01110111 01100101 01011111 01100011
01101111 01101101 01100101 01011111 01101001 01101110 01011111 01110000
01100101 01100001 01100011 01100101 01111101
```

Il suffit alors de le converti en ASCII, par exemple sur [binaire -> ascii](https://www.prepostseo.com/tool/fr/binary-translator)


Flag: `404CTF{W3_c0ME_IN_p3aC3}`