from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
import copy
from werkzeug.exceptions import RequestedRangeNotSatisfiable
from secret import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

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


@app.route("/delete/<int:id>")
def delete(id):
    try:
        for i in range(len(session["ids_db"])):
            session["ids_db"] = list(filter(lambda i: i["id"] != id, session["ids_db"]))
        # renumber:
        for i in range(len(session["ids_db"])):
            session["ids_db"][i]["id"] = i + 1
        session.modified = True
        return redirect("/create")
    except:
        return "There was an error while deleting that specification."


@app.route("/duplicate/<int:id>")
def duplicate(id):
    try:
        for i in range(len(session["ids_db"])):
            if session["ids_db"][i]["id"] == id:
                new = copy.deepcopy(session["ids_db"][i])
                new["id"] = id + 1
                session["ids_db"].insert(id, new)
                session.modified = True
        # renumber:
        for j in range(len(session["ids_db"])):
            session["ids_db"][j]["id"] = j + 1
            session.modified = True
        return redirect("/create")
    except:
        return "There was an error while duplicating that specification."


@app.route("/add_specification")
def add_specification():
    for i in range(len(session["ids_db"])):
        session["ids_db"][i]["id"] = i + 1
    session["ids_db"].append(
        {
            "id": len(session["ids_db"]) + 1,
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


@app.route("/add_requirement/<id>")
def add_requirement(id):
    sid, part, type = id.split(".")
    sid = int(sid) - 1
    val = "" #my %s..." % type
    if type == 'entity':
        session["ids_db"][sid]['applicability'][0]['value'].append(val) 
    else:
        req = {"id": len(session["ids_db"][sid][part]) + 1, "type": type, "value": val}
        if type == "property":
            req["pset"] = ""
            req["property"] = ""
        elif type == "classification":
            req["system"] = ""
        session["ids_db"][sid][part].append(req)
    session.modified = True
    return redirect("/create")


@app.route("/delete_requirement/<id>")
def delete_requirement(id):
    sid, rid, part, type = id.split(".")
    sid = int(sid) - 1
    rid = int(rid)
    try:
        if type == "entity":
            if len(session["ids_db"][sid]['applicability'][0]['value']) > 1:
                del session["ids_db"][sid]['applicability'][0]['value'][-1]
            else:
                #TODO should inform user with a toast: 'can't delete the last entity'
                pass
        else:
            for i in range(len(session["ids_db"][sid][part])):
                session["ids_db"][sid][part] = list(filter(lambda i: i["id"] != rid, session["ids_db"][sid][part]))
            # renumber:
            for i in range(len(session["ids_db"][sid][part])):
                session["ids_db"][sid][part][i]["id"] = i + 1
        session.modified = True
        return redirect("/create")
    except:
        return "There was an error while deleting that requirement"


@app.route("/validate")
def validate_page():
    if "ids_db" not in session:
        session["ids_db"] = DEFAULT_IDS
        session.modified = True
    return render_template("validate.html", ids=session["ids_db"])


@app.route("/documentation")
def documentation_page():
    if "ids_db" not in session:
        session["ids_db"] = DEFAULT_IDS
        session.modified = True
    return render_template("documentation.html", ids=session["ids_db"])

DEFAULT_IDS = [
    {
        "id": 1,
        "name": "Fire requirement specification",
        "applicability": [
            {"id": 1, "type": "entity", "value": ["IfcWall"]},
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
]

if __name__ == "__main__":
    app.run()
