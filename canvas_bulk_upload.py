import os
from argparse import ArgumentParser
from canvasapi import Canvas


def yml_parse(path):
    import yaml

    with open(path, 'r') as stream:
        data_loaded = yaml.load(stream)
        return data_loaded
    return None


if __name__ == '__main__':
    SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

    parser = ArgumentParser(description='Upload Gradescope data to canvas')    
    parser.add_argument("--yml", metavar='PATH', type=str, 
        dest='yml', default=None, required=True,
        help="path to file holding YML data (Gradescope file holding data, in the same directory as PDF submissions from gradescope).")
    parser.add_argument("--ASSIGNMENT_ID", type=int, 
        dest='ASSIGNMENT_ID', default=None, required=True,
        help="Canvas Assignment ID")
    parser.add_argument("--COURSE_ID", type=int, 
        dest='COURSE_ID', default=None, required=True,
        help="Canvas Course ID")
    parser.add_argument("--API_URL", type=str, 
        dest='API_URL', default=None, required=True,
        help="Canvas API URL")
    parser.add_argument("--API_KEY", type=str, 
        dest='API_KEY', default=None, required=True,
        help="Canvas API URL")

    OPT = vars(parser.parse_args())

    # open up the YML
    yml_data = yml_parse(OPT['yml'])

    # dict data[sid] = <feedback and score info>
    data = {}
    for key in yml_data.keys():
        val = yml_data[key]
        for i in range(len(val[':submitters'])):
            id = val[':submitters'][i][':sid']
            data[id] = {
                'score': val[':score'],
                'name': val[':submitters'][i][':name'],
                'path': os.path.dirname(os.path.abspath(OPT['yml']))+'/'+ key
            }

    canvas = Canvas(OPT['API_URL'], OPT['API_KEY'])
    course = canvas.get_course(OPT['COURSE_ID'])
    assignment = course.get_assignment(OPT['ASSIGNMENT_ID'])
    print("Uploading score data for Assignment", assignment, "for", course.name)

    assignment = assignment.edit(assignment={'muted' : True})
    print("Muted assignment")

    for sid in data:
        submission = assignment.get_submission(sid)
        print("For student '"+data[sid]['name']+"'")

        print("\t Setting score:", data[sid]['score'])
        result = submission.edit(submission={'posted_grade': data[sid]['score']})
        if not result:
            print("Failed to set grade", file=sys.stderr)
            exit(1)

        print("\t Uploading feedback:", data[sid]['path'])
        
        result, response = submission.upload_comment(data[sid]['path'])
        #print(response)
        if not result:
            print("Failed to set grade:", response, file=sys.stderr)
            exit(1)
        