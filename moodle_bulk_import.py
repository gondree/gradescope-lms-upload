import inspect, sys, os
from pprint import pprint
from optparse import OptionParser


def yml_parse(path):
    import yaml

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
            name = v[':submitters'][i][':name']
            grades[name] = v[':score']

    with open(output, 'w') as stream:
        writer = csv.writer(stream, delimiter=',')
        for row in cdata:
            if row[1] in grades.keys(): #row[1] hardcoded to indicate name column.
                row[4] = grades[row[1]] #row[4] hardcoded to indicate grades column.
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
            name = v[':submitters'][i][':name']
            name_meta[name] = {'fname': fname}

    for row in cdata:
        print(row)
        email = row[2]
        id = row[0].lstrip("Participant ")
        full_name = row[1].replace('"', '')

        if full_name in name_meta.keys():
            name_meta[full_name]['id'] = id
            name_meta[full_name]['name'] = full_name

    for entry in name_meta.values():
        print(entry)
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
        help="path to file holding CSV data (Moodle file to be modified with grades).")
    parser.add_option("--yml", metavar="PATH", type=str,
        dest='yml_path', default=None,
        help="path to file holding YML data (Gradescope file holding data, in the same directory as PDF submissions from gradescope).")

    (opt, args) = parser.parse_args()
    OPT = opt

    if opt.yml_path is None or opt.csv_path is None:
        sys.exit("Missing arguments. Run with -h for usage.")

    yml_data = yml_parse(opt.yml_path)
    csv_data = csv_parse(opt.csv_path)
    write_grade_data(yml_data, csv_data, opt.csv_path[:-3] + "_output.csv")
    rename_pdfs(yml_data, csv_data,
                os.path.dirname(opt.yml_path),
                os.path.dirname(opt.yml_path)+'/feedback')

