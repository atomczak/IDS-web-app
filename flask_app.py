from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
from flask import redirect
from werkzeug.exceptions import RequestedRangeNotSatisfiable

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/create', methods=['POST','GET'])
def create_page():
    if request.method == 'POST':
        global ids_db
        ids_db.append({'id': request.form['id'], 'content': request.form['content']})
        return redirect('/create')
    else:
        return render_template('create.html', ids=ids_db)


@app.route('/delete/<int:id>')
def delete(id):
    global ids_db
    try:
        for i in range(len(ids_db)):
            ids_db = list(filter(lambda i: i['id'] != id, ids_db))
        #renumber:
        for i in range(len(ids_db)):
            ids_db[i]['id'] = i+1
        return redirect('/create')
    except:
        return 'There was an error while deleting that specification.'

@app.route('/add_specification')
def add_specification():
    global ids_db
    for i in range(len(ids_db)):
        ids_db[i]['id'] = i+1
    ids_db.append(
        {'id':len(ids_db)+1, 'name':'New specification', 
        'applicability':[
            {'id': 1.1, 'type':'select', 'pre':'All', 'val':'IfcElements...'}
            ],
        'requirements':[
            # {'id': 1.1, 'type':'text', 'pre':'ZAbc', 'val':'ZDef'}, 
            # {'id': 1.2, 'type':'text', 'pre':'ZAbc2', 'val':'ZDe2f'}, 
            # {'id': 1.3, 'type':'text', 'pre':'ZAbc3', 'val':'ZDef3'}
            ]
        })
    # return str(ids_db)
    return redirect('/create')
 

@app.route('/add_requirement/<id>')
def add_requirement(id):
    id, ar, fac = id.split('.')
    id = int(id)-1
    if fac == 'material':
        type = 'text'
        pre = 'material'
        val = '<your_material>'
    elif fac == 'property':
        type = 'text'
        pre = 'property'
        val = '<your_property>'
    elif fac == 'entity':
        type = 'select'
        pre = 'entity Ifc'
        val = '<your_entity>'
    elif fac == 'predefined':
        type = 'text'
        pre = 'predefined type'
        val = '<your_predefined_type>'
    elif fac == 'classification':
        type = 'text'
        pre = 'classification'
        val = '<your_classification>'

    if ar == 'applicability':
        pre = 'of '+pre
    if ar == 'requirements':
        if fac == 'entity':
            pre = 'an '+pre
        else:
            pre = 'a '+pre

    global ids_db
    ids_db[id][ar].append({'id': len(ids_db[id][ar])+1, 'type':type, 'pre':pre, 'val':val})
    return redirect('/create')

@app.route('/delete_requirement/<id>')
def delete_requirement(id):
    id, rid, ar = id.split('.')
    id = int(id)-1
    rid = int(rid)
    global ids_db
    try:
        for i in range(len(ids_db[id][ar])):
            ids_db[id][ar] = list(filter(lambda i: i['id'] != rid, ids_db[id][ar]))
        #renumber:
        for i in range(len(ids_db[id][ar])):
            ids_db[id][ar][i]['id'] = i+1
        return redirect('/create')
    except:
        return 'There was an error while deleting that requirement'



@app.route('/validate')
def validate_page():
    return render_template('validate.html')



ids_db = [
    {'id':1, 'name':'Fire requirement specification', 
    'applicability':[
        {'id': 1, 'type':'select', 'pre':'All', 'val':'Walls'}, 
        {'id': 2, 'type':'text', 'pre':'of predefined type', 'val':'CLADDING'}, 
        ],
    'requirements':[
        {'id': 1, 'type':'text', 'pre':'a material', 'val':'TIMBER'}, 
        {'id': 2, 'type':'text', 'pre':'a property', 'val':'Class C30'},
        ]
    },
    {'id':2, 'name':'Material specification', 
    'applicability':[
        {'id': 1, 'type':'select', 'pre':'All', 'val':'Windows'}, 
        {'id': 2, 'type':'text', 'pre':'of material', 'val':'timber'}, 
        ],
    'requirements':[
        {'id': 1, 'type':'text', 'pre':'a property', 'val':'U-value'}, 
        ]
    }
    ]

if __name__ == '__main__':
    app.run()

