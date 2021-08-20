from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from flask import jsonify
from flask import send_file
from flask_cors import CORS
from flask import flash
from werkzeug.utils import secure_filename
import copy
from werkzeug.exceptions import RequestedRangeNotSatisfiable
from secret import SECRET_KEY #UPLOAD_FOLDER
from datetime import date
import os
from libs.ifcopenshell import ids
from xmlschema.validators.exceptions import XMLSchemaChildrenValidationErrorlibs

app = Flask(__name__)
CORS(app)
app.secret_key = SECRET_KEY

UPLOAD_FOLDER = '\server_files\ids'
ALLOWED_EXTENSIONS = {'ids', 'xml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000    # Max 10Mb files


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/create/", methods=["POST", "GET"])
def create_page():
    if request.method == "POST":
        # TODO implement form actions
        # ids_db.append({'id': request.form['id'], 'content': request.form['content']})
        # session.modified = True
        return redirect("/create")
    else:
        if "ids_db" not in session:
            session["ids_db"] = DEFAULT_IDS
        session.modified = True
        # TODO prevent accordion collapse on refresh
        # if 'ids_ui' not in session:
        #     session['ids_ui'] = {'accordions': ([0]*len(session['ids_db']))}
        #     session['ids_ui']['accordions'][0] = 1
        # session.modified = True
        return render_template("create.html", ids=session["ids_db"])


@app.route("/delete/<int:id>/")
def delete(id):
    try:
        for i in range(len(session["ids_db"]['specifications'])):
            session["ids_db"]['specifications'] = list(filter(lambda i: i["id"] != id, session["ids_db"]['specifications']))
        # renumber:
        for i in range(len(session["ids_db"]['specifications'])):
            session["ids_db"]['specifications'][i]["id"] = i + 1
        session.modified = True
        return redirect("/create")
    except:
        return "There was an error while deleting that specification."


@app.route("/duplicate/<int:id>/")
def duplicate(id):
    try:
        for i in range(len(session["ids_db"]['specifications'])):
            if session["ids_db"]['specifications'][i]["id"] == id:
                new = copy.deepcopy(session["ids_db"]['specifications'][i])
                new["id"] = id + 1
                session["ids_db"]['specifications'].insert(id, new)
                session.modified = True
        # renumber:
        for j in range(len(session["ids_db"]['specifications'])):
            session["ids_db"]['specifications'][j]["id"] = j + 1
            session.modified = True
        return redirect("/create")
    except:
        return "There was an error while duplicating that specification."


@app.route("/add_specification/")
def add_specification():
    for i in range(len(session["ids_db"]['specifications'])):
        session["ids_db"]['specifications'][i]["id"] = i + 1
    session["ids_db"]['specifications'].append(
        {
            "id": len(session["ids_db"]['specifications']) + 1,
            "name": "New specification",
            "applicability": [{"id": 1, "type": "entity", "value": ["IfcElement"]}],
            "requirements": [
                # {'id': 1.1, 'type':'property', 'pset':'Thermal', 'property':'U-value', 'value':'0.30'},
                # {'id': 1.2, 'type':'property', 'pset':'Thermal', 'property':'U-value', 'value':'0.30'},
                # {'id': 1.3, 'type':'property', 'pset':'Thermal', 'property':'U-value', 'value':'0.30'},
            ],
        }
    )
    session.modified = True
    return redirect("/create")


@app.route("/add_requirement/<id>/")
def add_requirement(id):
    sid, part, type = id.split(".")
    sid = int(sid) - 1
    val = "" #my %s..." % type
    if type == 'entity':
        session["ids_db"]['specifications'][sid]['applicability'][0]['value'].append(val) 
    else:
        req = {"id": len(session["ids_db"]['specifications'][sid][part]) + 1, "type": type, "value": val}
        if type == "property":
            req["pset"] = ""
            req["property"] = ""
        elif type == "classification":
            req["system"] = ""
        session["ids_db"]['specifications'][sid][part].append(req)
    session.modified = True
    return redirect("/create")


@app.route("/delete_requirement/<id>/")
def delete_requirement(id):
    sid, rid, part, type = id.split(".")
    sid = int(sid) - 1
    rid = int(rid)
    try:
        if type == "entity":
            if len(session["ids_db"]['specifications'][sid]['applicability'][0]['value']) > 1:
                del session["ids_db"]['specifications'][sid]['applicability'][0]['value'][-1]
            else:
                #TODO should inform user with a toast: 'can't delete the last entity'
                pass
        else:
            for i in range(len(session["ids_db"]['specifications'][sid][part])):
                session["ids_db"]['specifications'][sid][part] = list(filter(lambda i: i["id"] != rid, session["ids_db"]['specifications'][sid][part]))
            # renumber:
            for i in range(len(session["ids_db"]['specifications'][sid][part])):
                session["ids_db"]['specifications'][sid][part][i]["id"] = i + 1
        session.modified = True
        return redirect("/create")
    except:
        return "There was an error while deleting that requirement"


@app.route("/validate/")
def validate_page():
    if "ids_db" not in session:
        session["ids_db"] = DEFAULT_IDS
        session.modified = True
    return render_template("validate.html", ids=session["ids_db"])


@app.route("/documentation/")
def documentation_page():
    if "ids_db" not in session:
        session["ids_db"] = DEFAULT_IDS
        session.modified = True
    return render_template("documentation.html", ids=session["ids_db"])


@app.route("/api/<fieldName>&<fieldValue>/")
def updateField(fieldName, fieldValue):
    print("'"+fieldName+"'"+" set to "+"'"+fieldValue+"'")
    session["ids_db"][fieldName] = fieldValue
    session.modified = True
    # print(request.data)
    # return jsonify({'name':'Jimit', 'number':random.randint(1, 10)})
    # return jsonify(session["ids_db"]) #['specifications'][i]["id"]
    return 'success'

@app.route("/api/specificationName&<specId>&<fieldValue>/")
def updateSpecificationName(specId, fieldValue):
    print("Name of the '"+str(specId)+"' specification set to '"+fieldValue+"'")
    session["ids_db"]['specifications'][int(specId)-1]['name'] = fieldValue
    session.modified = True
    return 'success'

@app.route("/api/specification", methods=["POST", "GET"]) #&<specId>&<type>&<reqId>&<fieldValue>/")
def updateSpecification():   # specId, reqId, type, fieldValue
    data = request.json['id'].split('.') 
    session["ids_db"]['specifications'][int(data[1])-1][data[2]][int(data[3])-1][data[4]] = request.json['value']
    session.modified = True
    return 'success'

@app.route("/api/entity", methods=["POST", "GET"]) #&<specId>&<type>&<reqId>&<fieldValue>/")
def updateEntity():   # specId, reqId, type, fieldValue
    data = request.json['id'].split('.') 
    session["ids_db"]['specifications'][int(data[1])-1][data[2]][int(data[3])-1]['value'][int(data[4])-1] = request.json['value']
    session.modified = True
    return 'success'

@app.route("/api/download-ids", methods=['GET', 'POST'])   # <folder>&<path:filename>/"    
def downloadFile():
    filename = os.path.join(app.static_folder, 'custom_ids', "User_" + request.remote_addr + '.xml')
    try:
        convertToIds(session["ids_db"], filename)
    except XMLSchemaChildrenValidationError as e: 
        print(e)
        return str(e)
    else:   
        return send_file(filename,
                        mimetype='text/xml',
                        download_name= date.today().isoformat()+"_IDS_"+session["ids_db"]['name']+".xml",
                        as_attachment=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/upload/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('download_file', name=filename))
#     return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''

DEFAULT_IDS = {
    'name':'My Information Delivery Specification', 
    'ifcversion':'', 
    'description':'', 
    'author':'', 
    'copyright':'', 
    'version':'', 
    'creation_date': date.today().isoformat(), 
    'purpose':'', 
    'milestone':'',
    'specifications':[
    {
        "id": 1,
        "name": "Fire requirement specification",
        "applicability": [
            {"id": 1, "type": "entity", "value": ["IfcWall"]},      # TODO add "collapsed":"true", 
            {"id": 2, "type": "predefined", "value": "CLADDING"},
        ],
        "requirements": [
            {"id": 1, "type": "material", "value": "TIMBER"},
            {
                "id": 2,                
                "type": "property",
                "pset": "Structural",
                "property": "Strength class",
                "value": "C30",
            },
        ],
    },
    {
        "id": 2,
        "name": "Test specification",
        "applicability": [
            {"id": 1, "type": "entity", "value": ["IfcWall"]},
            {"id": 2, "type": "predefined", "value": "TEST"},
            {"id": 3, "type": "material", "value": "TEST"},
            {"id": 4, "type": "classification", "value": "TEST", "system":"TEST"},
            {"id": 5, "type": "property", "value": "TEST", "pset":"TEST", "property":"TEST"}
        ],
        "requirements": [
            {"id": 1, "type": "predefined", "value": "TEST"},
            {"id": 2, "type": "material", "value": "TEST"},
            {"id": 3, "type": "classification", "value": "TEST", "system":"TEST"},
            {"id": 4, "type": "property", "value": "TEST", "pset":"TEST", "property":"TEST"}
        ],
    },
]}

def convertToIds(dict, filename):
    # TODO allow restrictions
    i = ids.ids(
            ifcversion = None if dict['ifcversion'] == 'Any' else dict['ifcversion'] if dict['ifcversion'] else None,
            description = dict['description'] if dict['description'] else None,
            author = dict['author'] if dict['author'] else None,
            copyright = dict['copyright'] if dict['copyright'] else None,
            version = float(dict['version']) if dict['version'] else None,
            creation_date = dict['creation_date'] if dict['creation_date'] else None,
            purpose = dict['purpose'] if dict['purpose'] else None,
            milestone = dict['milestone'] if dict['milestone'] else None,
    )
    for spec in dict['specifications']:
        i.specifications.append(ids.specification(name=spec['name']))
        # TODO add location type/instance option
        for req in spec['applicability']:
            r = None
            if req['type'] == 'entity':
                r = ids.entity.create(name=req['value'][0])  #, predefinedtype="Test_PredefinedType")
                # TODO should work for more entities (duplicating specification)
            elif req['type'] == 'classification':
                r = ids.classification.create(location="any", value=req['value'], system=req['system'])
            elif req['type'] == 'property':
                r = ids.property.create(location="any", propertyset=req['pset'], name=req['property'], value=req['value'])
            elif req['type'] == 'material':
                r = ids.material.create(location="any", value=req['value'])
            # TODO elif req['type'] == 'predefined':
            if r:
                i.specifications[-1].add_applicability(r)
        for req in spec['requirements']:
            r = None
            if req['type'] == 'classification':
                r = ids.classification.create(location="any", value=req['value'], system=req['system'])
            elif req['type'] == 'property':
                r = ids.property.create(location="any", propertyset=req['pset'], name=req['property'], value=req['value'])
            elif req['type'] == 'material':
                r = ids.material.create(location="any", value=req['value'])
            # TODO elif req['type'] == 'predefined':
                # r = ids.entity.create(name=req['value'][0])  #, predefinedtype="Test_PredefinedType")
            if r:
                i.specifications[-1].add_requirement(r)

    i.to_xml(filename)

        
        
# TODO def ChangeDictToIDS() then to XML()


# TODO
# IFC_ENTITIES = [...]

# from Thomas:
# import ifcopenshell
# S = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
# S.declaration_by_name("IfcColumn").all_attributes()
# S.declaration_by_name("IfcColumn").supertype().name()
# S.declaration_by_name("IfcRoot").subtypes()
# [decl.name() for decl in S.declarations()]

if __name__ == "__main__":
    app.run()
