import inspect, sys, os
from pprint import pprint
from optparse import OptionParser


def open_xml(path, records):
    import openpyxl   # pip install openpyxl

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    meta = ''
    done = False

    # get the activity name (meta) and the student names
    for cell in ws.columns[0]:
        if cell.value == 'Student Names' or cell.value == 'Class Scoring':
            done = True
            continue
        elif not done:
            if cell.value != None:
                if meta != '':
                    meta += ', '
                meta += str(cell.value)
            continue

        name = cell.value
        if not name in records.keys():
            records[name] = {}
        if not meta in records[name].keys():
            records[name][meta] = {'total': 0}

    # for each student, get each click
    for r in ws.rows[8:]:
        name = None
        cell = r[0]
        if name is None and cell.value in records.keys():
            name = cell.value
        if name is None:
            continue
        for cell in r[3:]:
            if cell.value != None:
                records[name][meta][cell.column] = 1

    # add up all the clicks
    for name in records.keys():
        if meta in records[name].keys():
            records[name][meta]['total'] = len(
                [k for k in records[name][meta].keys() if k != 'total'])
            if records[name][meta]['total'] == 0:
                del records[name][meta]


def yml_parse(path):
    import yaml, io

    with open(path, 'r') as stream:
        data_loaded = yaml.load(stream)
        return data_loaded
    return None

def csv_parse(path):
    import csv

    with open(path, 'r') as stream:
        data_loaded = csv.reader(stream, delimiter=',')
        return [r for r in data_loaded]
    return None

def write_grade_data(ydata, cdata, output):
    import csv

    grades = {}
    for v in ydata.values():
        for i in range(len(v[':submitters'])):
            email = v[':submitters'][i][':email']
            grades[email] = v[':score']

    with open(output, 'w') as stream:
        writer = csv.writer(stream, delimiter=',')
        for row in cdata:                       
            if row[2] in grades.keys(): #row[2] hardcoded to indicate email column.                 
                row[4] = grades[row[2]] #row[4] hardcoded to indicate grades column.  
            writer.writerow(row)
    return None

def rename_pdfs(ydata, cdata, ipath, opath):
    import shutil

    if not os.path.exists(ipath):
        return None
    if not os.path.exists(opath):
        os.mkdir(opath)
    
    name_meta = {}
    for key in ydata.keys():
        v = ydata[key]
        fname = key
        for i in range(len(v[':submitters'])):
            email = v[':submitters'][i][':email']
            name_meta[email] = {'fname': fname}

    for row in cdata:

        email = row[2]
        id = row[0].lstrip("Participant ")
        name = row[1].replace('"', '')
        
        if email in name_meta.keys():
            name_meta[email]['id'] = id
            name_meta[email]['name'] = name

    for entry in name_meta.values():
        fname = entry['fname']
        oname = entry['name'] + '_' + entry['id'] + '_assignsubmission_file_' + fname
        ifilename = ipath + '/' + fname
        ofilename = opath + '/' + oname
        
        if os.path.exists(ifilename):
            shutil.copyfile(ifilename,ofilename)
    return None


if __name__ == '__main__':
    SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))
    data = []

    parser = OptionParser(description='Perform gradescope analysis.')
    parser.add_option("--csv", metavar="PATH", type=str, 
        dest='csv_path', default=None,
        help="path to directory holding CSV data (Moodle file to be modified with grdes).")
    parser.add_option("--yml", metavar="PATH", type=str, 
        dest='yml_path', default=None,
        help="path to directory holding YML data (Gradescope file holding data, in the same directory as PDF submissions from gradescope).")

    (opt, args) = parser.parse_args()
    OPT = opt

    yml_data = yml_parse(opt.yml_path)
    csv_data = csv_parse(opt.csv_path)
    write_grade_data(yml_data, csv_data, opt.csv_path[:-3] + "_output.csv")
    rename_pdfs(yml_data, csv_data, 
                os.path.dirname(opt.yml_path),
                os.path.dirname(opt.yml_path)+'/feedback')
    
    