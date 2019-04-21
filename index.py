# app.py
from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy 
import importlib.machinery
from distutils.sysconfig import get_python_lib
from flask_marshmallow import Marshmallow 
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix
from models import BlogPost

# if local environment, use psycopg2 installed in python library (site-packages), otherwise use from binary (psycopg2 subdirectory in this folder)
try:
    psycopg2 = importlib.machinery.SourceFileLoader('psycopg2', get_python_lib()+'/psycopg2/__init__.py').load_module()
except:
    import psycopg2

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
          version='0.1',
          title='Our sample API',
          description='This is our sample API'
)

POSTGRES = {
    'user': 'cfqvhzyn',
    'pw': 'X20fx0vIQGCM4-tMeRkQRY1LoZ4RDkWw',
    'db': 'cfqvhzyn',
    'host': 'otto.db.elephantsql.com',
    'port': '5432',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
db.init_app(app)

# Init ma
ma = Marshmallow(app)

class Caminhao(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tipo = db.Column(db.String(100), unique=True)
  
  def __init__(self, tipo):
    self.tipo = tipo
    
# Caminhao Schema
class CaminhaoSchema(ma.Schema):
  class Meta:
    fields = ('id', 'tipo')

# Init schema
caminhao_schema = CaminhaoSchema(strict=True)
caminhoes_schema = CaminhaoSchema(many=True, strict=True)

@app.route('/api/v1/caminhoes', methods=['GET'])
def get_caminhoes():
  all_caminhoes = Caminhao.query.all()
  result = caminhoes_schema.dump(all_caminhoes)
  return jsonify(result.data)

@app.route('/api/v1/caminhoes/<int:id>', methods=['GET'])
def get_caminhao(id):
  caminhao = [caminhao for caminhao in caminhoes if caminhao['id'] == id]
  if len(caminhao) == 0:
    abort(404)
  caminhao = Caminhao.query.get(id)
  return caminhao_schema.jsonify(caminhao)

@app.route('/api/v1/caminhoes', methods=['POST'])
def adicionar_caminhao():
  if not request.json or not 'tipo' in request.json:
        abort(400)

  tipo = request.json['tipo']
  
  novo_caminhao = Caminhao(tipo)
  db.session.add(novo_caminhao)
  db.session.commit()

  return caminhao_schema.jsonify(novo_caminhao)

@api.route('/hello_world')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

@api.route('/blog_posts')
class BlogPosts(Resource):
    model = api.model('BlogPost', {
        'id': fields.Integer,
        'title': fields.String,
        'post': fields.String,
    })
    @api.marshal_with(model, envelope='resource')
    def get(self, **kwargs):
        return BlogPost.query.all()

#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
