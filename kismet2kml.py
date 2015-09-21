#!/usr/bin/env python3
import argparse
import os
import re
from lxml import etree

bad_chars = re.compile("(&|<|>)")
annoying_aps = ['btwi', 'btopenzone', 'o2 wifi', 'the cloud', 'print', 'chromecast',
        'ee-brightbox', 'stagecoach']

class AccessPoint(object):
    """Represents a wireless access point"""

    def __init__(self, bssid:str, ssid:str, manu:str, enc:list,
            lat:str, lon:str, alt:str):
        self.bssid = bad_chars.sub("", bssid)
        self.ssid  = bad_chars.sub("", ssid)
        self.manu  = bad_chars.sub("", manu)
        self.enc   = [bad_chars.sub("", enc_item) for enc_item in enc]
        self.lat   = bad_chars.sub("", lat)
        self.lon   = bad_chars.sub("", lon)
        self.alt   = bad_chars.sub("", alt)

    def __str__(self) -> str:
        return """<Placemark>
    <name>{}</name>
    <description>
        <![CDATA[
            <b>BSSID: </b>{}<br />
            <b>Manufacturer: </b> {}<br />
            <b>Encryption: </b> {}<br />
        ]]>
    </description>
    <Point>
        <coordinates>{},{},{}</coordinates>
    </Point>
</Placemark>""".format(self.ssid, self.bssid, self.manu,
                " ".join(self.enc), self.lon, self.lat,
                self.alt)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert Kismet data into a Google Earth KML File.")
    parser.add_argument("-n", "--net-xml-file", help="The path to the .netxml file.",
            required=True)
    parser.add_argument("-o", "--output", help="The path to the output file.",
            required=False)
    parser.add_argument("-re", "--remove-encrypted", help="Filter out non-open access points.",
            required=False, action='store_true')
    parser.add_argument("-ra", "--remove-annoying", help="Remove annoying access points (subjective).",
            required=False, action='store_true')
    parser.add_argument("-rh", "--remove-hidden", help="Remove hidden SSIDs from output.",
            required=False, action='store_true')
    args = parser.parse_args()
    args.net_xml_file = os.path.abspath(args.net_xml_file)
    if args.output is not None:
        args.output = os.path.abspath(args.output)
    return args

def main():
    args = parse_args()
    tree = etree.parse(args.net_xml_file)
    aps = []
    for wn in tree.iterfind(".//wireless-network"):
        # Skip if the network is not an AP
        if not 'infrastructure' in wn.values():
            continue
        bssid = wn.find("BSSID").text
        ssid  = wn.find("SSID").find("essid").text or "Hidden SSID"
        manu  = wn.find("manuf").text
        enc   = [enc_e.text for enc_e in wn.find("SSID").findall("encryption")]

        if args.remove_hidden and ssid == "Hidden SSID":
            continue

        skip = False
        if args.remove_annoying:
            for annoying in annoying_aps:
                if annoying in ssid.lower():
                    skip = True
        if skip:
            continue

        if args.remove_encrypted and 'None' not in enc:
            continue

        gps_info = wn.find("gps-info")
        # Skip if there is no gps information
        if gps_info is None:
            continue

        lat = wn.find("gps-info").find("avg-lat").text
        lon = wn.find("gps-info").find("avg-lon").text
        alt = wn.find("gps-info").find("avg-alt").text

        aps.append(AccessPoint(bssid, ssid, manu, enc, lat, lon, alt))

    output = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Folder>
<name>Kismet Wardrive</name>
<description>Output from the kismet2kml script!</description>
{}
</Folder>
</kml>
""".format("\n".join([str(ap) for ap in aps]))
    
    if args.output is None:
        print(output)
    else:
        with open(args.output, 'w') as f:
            f.write(output)

if __name__ == '__main__':
    main()
