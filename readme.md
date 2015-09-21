# kismet2kml.py

```
usage: kismet2kml.py [-h] -n NET_XML_FILE [-o OUTPUT] [-re] [-ra] [-rh]

Convert Kismet data into a Google Earth KML File.

optional arguments:
  -h, --help            show this help message and exit
  -n NET_XML_FILE, --net-xml-file NET_XML_FILE
                        The path to the .netxml file.
  -o OUTPUT, --output OUTPUT
                        The path to the output file.
  -re, --remove-encrypted
                        Filter out non-open access points.
  -ra, --remove-annoying
                        Remove annoying access points (subjective).
  -rh, --remove-hidden  Remove hidden SSIDs from output.
```
