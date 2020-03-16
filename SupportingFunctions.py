try:
    import os
    import sys
    import json
    import csv
    import requests
    import re
    import glob
    import pandas as pd
    import time
    import datetime
    import math
    import string
    import command
    import urllib.request
    import xlsxwriter
    from geopy.geocoders import Nominatim
except ImportError:
    print("ERROR ! Module Import Failed - " + os.path.basename(__file__), "Console")
    print(sys.exc_info())
    input("Press Enter to continue...")
    exit(99)


def get_start_end_date_by_frequency(frequency):
    ed = datetime.datetime.now().date()
    if frequency.upper() == "DAILY":
        sd = ed - datetime.timedelta(1)
    elif frequency.upper() == "WEEKLY":
        sd = ed - datetime.timedelta(7)
    elif frequency.upper() == "MONTHLY":
        sd = ed - datetime.timedelta(30)
    elif frequency.upper() == "QUARTERLY":
        sd = ed - datetime.timedelta(90)
    else:
        sd = ed

    return str(sd), str(ed)


def clean_filetype_in_folder(path, extension):
    files = glob.glob(path + "\\*." + extension)
    for f in files:
        if os.path.isfile(f):
            os.remove(f)


def convert_ms_to_hours(millis):
    millis = int(millis)
    seconds = int((millis/1000) % 60)
    minutes = int((millis / (1000 * 60)) % 60)
    hours = int((millis / (1000 * 3600)) % 24)

    return str(hours) + ":" + str(minutes) + ":" + str(seconds)


def check_date_in_period(period, date):
    date = date.replace("/", "-")
    today = datetime.datetime.now()
    my_end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_range = today - my_end_date
    if date_range.days <= int(period):
        return True
    else:
        return False


def jsonwrite(file, content):
    with open(file, 'w') as json_file:
        json.dump(content, json_file)

def log_to_report(file, mode, content):
    rf = open(file, "a")
    rf.write(content + "\n")
    rf.close()


def log_to_xlsx_file_dt_df(worksheet, content, reset=None):
    global start_row
    start_col = 0
    if reset is not None:
        start_row = 0

    for col_name, col in content.iterrows():
        col_value = list(col.values)
        col_value = str(col_value).replace("[", "")
        col_value = str(col_value).replace("]", "")
        col_value = str(col_value).replace("'", "")
        col_content = col_value.split(",")
        for value in col_content:
            worksheet.write(start_row, start_col, value)
            start_col = start_col + 1
        start_row = start_row + 1
        start_col = 0


def log_to_xlsx_file_dt_comma_string(worksheet, content, reset=None):
    global start_row
    start_col = 0
    if reset is not None:
        start_row = 0

    col_content = str(content).split(",")
    for value in col_content:
        worksheet.write(start_row, start_col, value)
        start_col = start_col + 1
    start_row = start_row + 1


def merge_xlsx_file(excel_name, o_file):
    workbook = xlsxwriter.Workbook(o_file)
    for sourcefile in excel_name:
        xls = pd.ExcelFile(sourcefile)
        sheets = xls.sheet_names
        for sheet in sheets:
            sheet = workbook.add_worksheet(sheet)
            data = pd.read_excel(sourcefile, sheet_name=sheet, header=None)
            log_to_xlsx_file_dt_df(sheet, data, "Reset")
    workbook.close()


def reverse(value):
    return value[::-1]


def split_string_by_length(strs, leng):
    return [strs[start:start + leng] for start in range(0, len(strs), leng)]


def Query(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    the_page = response.read()
    jason = json.loads(the_page)
    return jason


def QueryLocationData(city, country):
    try:
        geolocator = Nominatim()
        loc = None
        loc = geolocator.geocode(city + ',' + country)
        if loc is None:
            return "NA", "NA"
        else:
            return loc.latitude, loc.longitude
    except:
        return "NA", "NA"

# ************************************************************************************************************
# Func Name    : zip_contents
# Input Parm 1 :
# Input Parm 2 :
# Input Parm 3 : Password (Optional)
# ************************************************************************************************************
def zip_contents(zip_file_name, zip_folder_list, password=None):
    if password is not None:
        zip_me = "zip -P" + password + " -r " + zip_file_name + " " + "FOLDER1/" + " " + "FOLDER2"
    else:
        zip_me = "zip -r " + zip_file_name + " " + "FOLDER1/" + " " + "FOLDER2"
    command.run(zip_me)


