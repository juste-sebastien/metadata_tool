#!/usr/bin/python3
# coding:utf8
import os

import exif
import exifread
import pypdf
import re
import sqlite3
import utils

from PIL import Image
from PIL import ExifTags


def get_meta(file: str):
    """
    Found some metadata in a PDF file
    :param file: name of image
    :return:
    """
    pdf_file = pypdf.PdfReader(open(file, "rb"))
    doc_info = pdf_file.metadata
    info_list = []
    for info in doc_info.keys():
        info_list.append(f"[+] {info}: {doc_info[info]}")
    return info_list


def get_meta_with_regex(file: str):
    """
    Found all metadata in a file
    :param file: name of file
    :return:
    """
    with open(file, "rb") as f:
        content = f.read()
        pattern = re.compile(r"[\S\s]{4,}")
        for match in pattern.finditer(content.decode("utf8", "backslashreplace")):
            return f"[+] {match.string}"


def get_exif(image: str):
    """
    Found all metadata in image's EXIF
    :param image: name of image
    :return:
    """
    exif_dict = {}
    pil_img = Image.open(image)
    exif_dict = utils.add_primary_info(pil_img)
    with open(image, 'rb') as f:
        img = exif.Image(f)
        for item in img.list_all():
            exif_dict[item] = f"{img.get(attribute=f'{item}')}"
        exif_data = pil_img.getexif()

        for data in exif_data.keys():
            exif_dict[data] = f"{data}: {exif_data[data]}"

        if exif_dict == {}:
            return 1, '[-] No metadata found'
        else:
            return 0, exif_dict


def get_gps_coordinate(file: str):
    """
    Found gps location in image's EXIF
    :param file: name of image
    :return:
    """
    with open(file, "rb") as f:
        exif = exifread.process_file(f)
        if not exif:
            return 1, "[-] No metadata found"
        else:
            latitude = exif.get("GPS GPSLatitude")
            latitude_ref = exif.get("GPS GPSLatitudeRef")
            longitude = exif.get("GPS GPSLongitude")
            longitude_ref = exif.get("GPS GPSLongitudeRef")
            if latitude and latitude_ref and longitude and longitude_ref:
                lat = utils.convert_to_degrees(latitude)
                lon = utils.convert_to_degrees(longitude)
                if str(latitude_ref) != "N":
                    lat = -lat
                if str(longitude_ref) != "E":
                    lon = -lon

                return 0, f"[+] https://maps.google.com/maps?q=loc:{lat},{lon}"
            else:
                return 0, f"[-] No valid coordinates"


def get_firefox_info(db_type: str, file: str, option: str):
    """
        With type of db call right function
        :param db_type: name of db that contain cookies
        :param file: name of db that contain cookies
        :param option: user's presentation form
        :return:
        """
    if db_type == "c":
        return get_firefox_cookies(file, option)
    else:
        return get_firefox_places(file, option)


def get_firefox_places(places_db: str, option=None):
    """
        Try to found url in firefox db
        :param places_db: name of db that contain cookies
        :param option: user's presentation form
        :return:
        """
    try:
        conn = sqlite3.connect(places_db)
    except Exception as err:
        return 1, f"[-] Error: {err}"
    else:
        cursor_string = ""
        cursor = conn.cursor()
        cursor.execute(
            "select url, datetime(last_visit_date/1000000, \
         'unixepoch') from moz_places, moz_historyvisits where visit_count > 0 \
         and moz_places.id == moz_historyvisits.place_id"
        )

        header = "<!DOCTYPE html><head></head><body><table><tr><th>URL</th><th>Date</th></tr>"
        body = ""

        for row in cursor.fetchall():
            body += (
                f'<tr><td><a href="{row[0]}">{row[0]}</a></td><td>{row[1]}</td></tr>'
            )
            cursor_string += (
                f"{utils.Color.GREEN}[+] {row[0]}: {row[1]}{utils.Color.END}"
            )

        footer = "</body></html>"
        if option == "html":
            with open("./history.html", "w") as f:
                f.write(header + body + footer)
            return 0, f'[+] File created:{os.path.abspath("./history.html")}'
        else:
            return 0, cursor_string


def get_firefox_cookies(cookies_db: str, option=None):
    """
    Try to found any cookies in firefox db
    :param cookies_db: name of db that contain cookies
    :param option: user's presentation form
    :return:
    """
    try:
        conn = sqlite3.connect(cookies_db)
    except Exception as err:
        return 1, f"[-] Error: {err}"
    else:
        cursor_string = ""
        cursor = conn.cursor()
        cursor.execute("SELECT name, value, host FROM moz_cookies")

        header = "<!DOCTYPE html><head></head><body><table><tr><th>Name</th><th>Value</th><th>Host</th></tr>"
        body = ""

        for row in cursor:
            body += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
            cursor_string += (
                f"{utils.Color.GREEN}[+] Name: {str(row[0])}{utils.Color.END}\n'"
                f"\t[*] Value: {str(row[1])}\n\t[*] Host: {str(row[2])}\n"
            )

        footer = "</body></html>"
        if option == "html":
            with open("./history_cookies.html", "w") as f:
                f.write(header + body + footer)
            return 0, f'[+] File created:{os.path.abspath("./history_cookies.html")}'
        else:
            return 2, cursor_string
