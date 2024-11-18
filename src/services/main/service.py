import json
import os

import pymongo
import requests
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from datetime import datetime, timedelta

load_dotenv()
DB_URL = os.getenv("DB_URL")
tareas_bp = Blueprint("tareas_bp", __name__)
colaboradores_bp = Blueprint("colaboradores_bp", __name__)

client = pymongo.MongoClient(DB_URL)
db = client.examen
tareas = db.tareas
colaboradores = db.colaboradores   
asignaciones = db.asignaciones   

# #En el modelo conceptual de Gente! distinguiremos dos tipos de elementos:
# ● Tareas. Las tareas en las que se puede colaborar, descritas por las siguientes características:
# o responsable: dirección de email del usuario responsable de la tarea (el que crea la tarea).
# o descripción: título o descripción breve de la tarea (hasta 50 caracteres).
# o habilidades: una serie de habilidades (términos) adecuadas para participar en la tarea.
# o segmentos: duración estimada de la tarea (en segmentos de 1 hora de trabajo).
# ● Colaboradores. Representa a los usuarios de la aplicación, con las siguientes características:
# o email: dirección de email del colaborador.
# o nombre: nombre del usuario.
# o habilidades: una serie de habilidades (términos) que posee el colaborador

#GET ALL /tareas/

@tareas_bp.route("/", methods = ['GET'])
def get_tareas():
    try:
        print("GET ALL TAREAS")
        resultado = tareas.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /tareas/<id>

@tareas_bp.route("/<id>", methods = ["GET"])
def get_tareas_by_id(id):
    try:
        resultado = tareas.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de tarea por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el mensaje con id {id}")
        return jsonify({"error":"Mensaje con id especificado no encontrada"}), 404

# POST /tareas/

@tareas_bp.route("/", methods = ['POST'])
def create_tarea():
    datos = request.json

    if not datos or not datos["responsable"] or not datos["descripcion"] or not datos["habilidades"] or not datos["segmentos"]:
        print("Error: Parametros de entrada inválidos")

    descripcion = datos["descripcion"]
    responsable = datos["responsable"]
    segmentos = datos["segmentos"]
    tarea_existente = tareas.find_one({"descripcion":descripcion})

    if len(descripcion) > 50:
        return jsonify({"error": "La descripcion no puede tener mas de 50 caracteres"}), 400
    
    if segmentos % 1 != 0:
        return jsonify({"error": "Los segmentos deben ser un numero entero"}), 400

    if tarea_existente:
        return jsonify({"error": f"Tarea con descripcion {descripcion} ya existe"}), 404
    else:
        tareas.insert_one(datos)
        return jsonify({"response": f"Tarea con responsable {responsable} y descripcion {descripcion} creado correctamente"}), 201

#PUT /tareas/<id>

@tareas_bp.route("/<id>", methods=["PUT"])
def update_tarea(id):
    data = request.json
    dataFormateada = {"$set":data}
    respuesta = tareas.find_one_and_update({"_id":ObjectId(id)}, dataFormateada, return_document=True)
    print(respuesta)

    if respuesta is None:
        return jsonify({"error":f"Error al actualizar la tarea con id {id}"}), 404
    else:
        return jsonify({"response":f"Tarea con id {id} actualizada correctamente"}), 200

#DELETE /tareas/<id>

@tareas_bp.route("/<id>", methods=['DELETE'])
def delete_tarea(id):

    try:
        tarea = tareas.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El usuario {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = tareas.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar la tarea con id {id}", 400
    if borrado.deleted_count == 0:
        return f"La tarea {id} no existe, por lo tanto no se puede borrar", 200

    return "La tarea ha sido borrada con exito", 200






#CRUD DE LOS COLABORADORES


#GET ALL /colaboradores/

@colaboradores_bp.route("/", methods = ['GET'])
def get_colaboradores():
    try:
        print("GET ALL COLABORADORES")
        resultado = colaboradores.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /tareas/<id>

@colaboradores_bp.route("/<id>", methods = ["GET"])
def get_colaboradores_by_id(id):
    try:
        resultado = colaboradores.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "ID invalido"}), 400
    if resultado:
        print("Busqueda de colaborador por id")
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    else:
        print(f"Error al obtener el mensaje con id {id}")
        return jsonify({"error":"Mensaje con id especificado no encontrada"}), 404

# POST /tareas/

@colaboradores_bp.route("/", methods = ['POST'])
def create_colaboradores():
    datos = request.json

    if not datos or not datos["email"] or not datos["nombre"] or not datos["habilidades"]:
        print("Error: Parametros de entrada inválidos")

    email = datos["email"]
    nombre = datos["nombre"]
    tarea_existente = colaboradores.find_one({"email":email})

    if tarea_existente:
        return jsonify({"error": f"Colaborador con email {email} ya existe"}), 404
    else:
        colaboradores.insert_one(datos)
        return jsonify({"response": f"Colaborador con nombre {nombre} y email {email} creado correctamente"}), 201

#DELETE /colaboradores_bp/<id>

@colaboradores_bp.route("/<id>", methods=['DELETE'])
def delete_colaboradores(id):

    try:
        colaborador = colaboradores.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"El colaborador con {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404

    try:
        borrado = colaboradores.delete_one({"_id":ObjectId(id)})
    except Exception as e:
        return f"Error al borrar la tarea con id {id}", 400
    if borrado.deleted_count == 0:
        return f"El colaborador con {id} no existe, por lo tanto no se puede borrar", 200

    return "El colaborador ha sido borrada con exito", 200

# CRUD de habilidades de un colaborador: GET ALL (devuelve todas sus habilidades), POST (añade una habilidad
# al colaborador), DELETE (elimina una habilidad). Observa que no hay operación PUT, ni GET individual.

#LAS HABILIDADES DE LOS COLABORADORES ESTAN EN UN ARRAY DE STRINGS DENTRO DE LA COLECCION DE COLABORADORES

#GET ALL /colaboradores/<id>/habilidades

@colaboradores_bp.route("/<id>/habilidades", methods = ['GET'])

def get_habilidades_colaborador(id):
    try:
        print("GET ALL HABILIDADES DE COLABORADOR")
        resultado = colaboradores.find_one({"_id":ObjectId(id)})
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado["habilidades"]))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400
    
#POST /colaboradores/<id>/habilidades

@colaboradores_bp.route("/<id>/habilidades", methods = ['POST'])

def add_habilidad_colaborador(id):
    datos = request.json

    if not datos or not datos["habilidad"]:
        print("Error: Parametros de entrada inválidos")

    habilidad = datos["habilidad"]
    colaborador = colaboradores.find_one({"_id":ObjectId(id)})
    habilidades = colaborador["habilidades"]

    if habilidad in habilidades:
        return jsonify({"error": f"Habilidad {habilidad} ya existe en el colaborador"}), 404
    else:
        colaboradores.update_one({"_id":ObjectId(id)}, {"$push": {"habilidades": habilidad}})
        return jsonify({"response": f"Habilidad {habilidad} añadida al colaborador"}), 201

#DELETE /colaboradores/<id>/habilidades

@colaboradores_bp.route("/<id>/habilidades", methods = ['DELETE'])

def delete_habilidad_colaborador(id):
    datos = request.json

    if not datos or not datos["habilidad"]:
        print("Error: Parametros de entrada inválidos")

    habilidad = datos["habilidad"]
    colaborador = colaboradores.find_one({"_id":ObjectId(id)})
    habilidades = colaborador["habilidades"]

    if habilidad not in habilidades:
        return jsonify({"error": f"Habilidad {habilidad} no existe en el colaborador"}), 404
    else:
        colaboradores.update_one({"_id":ObjectId(id)}, {"$pull": {"habilidades": habilidad}})
        return jsonify({"response": f"Habilidad {habilidad} eliminada del colaborador"}), 200
    

#CRUD DE ASIGNACIONES

#GET ALL /tareas/asignaciones/

@tareas_bp.route("/asignaciones", methods = ['GET'])

def get_asignaciones():
    try:
        print("GET ALL ASIGNACIONES")
        resultado = asignaciones.find()
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        return jsonify({"error": "Error al procesar resultados"}), 400


#POST /asignaciones/

@tareas_bp.route("/asignaciones", methods = ['POST'])
def create_asignacion():
    datos = request.json

    if not datos or not datos["nombre"] or not datos["tarea"] or not datos["segmento"]:
        print("Error: Parametros de entrada inválidos")

    nombre = datos["nombre"]
    tarea = ObjectId(datos["tarea"])
    datos["tarea"] = tarea
    asignacion_existente = asignaciones.find_one({"nombre":nombre, "tarea":ObjectId(tarea)})

    if asignacion_existente:
        return jsonify({"error": f"Asignacion con nombre {nombre} y tarea {tarea} ya existe"}), 404
    else:
        asignaciones.insert_one(datos)
        return jsonify({"response": f"Asignacion con nombre {nombre} y tarea {tarea} creado correctamente"}), 201

#DELETE /asignaciones/<id>  

@tareas_bp.route("/asignaciones/<id>", methods=['DELETE'])
def delete_asignacion(id):
    
        try:
            asignacion = asignaciones.find_one({"_id":ObjectId(id)})
        except Exception as e:
            return f"La asignacion con {id} no existe, por lo tanto no se puede borrar (no encontrado)", 404
    
        try:
            borrado = asignaciones.delete_one({"_id":ObjectId(id)})
        except Exception as e:
            return f"Error al borrar la asignacion con id {id}", 400
        if borrado.deleted_count == 0:
            return f"La asignacion con {id} no existe, por lo tanto no se puede borrar", 200
    
        return "La asignacion ha sido borrada con exito", 200


#Ampliarás la funcionalidad de la API REST con las siguientes operaciones:
# ● Tareas que requieren una determinada habilidad, devolviendo una lista de tareas.
# ● Tareas asignadas a un determinado colaborador, el cual se obtiene con un argumento de query en el link, devolviendo una lista de tareas.
# ● Asignar un colaborador a una tarea, para lo cual se comprobará que el colaborador posea al menos una de las
# habilidades requeridas por la tarea.
# ● Buscar candidatos a colaborar en una tarea, devolviendo una lista de emails de colaboradores que posean al
# menos una de las habilidades requeridas por la tarea.
# ● Tareas completamente asignadas, que devolverá las tareas que tengan asignados tantos colaboradores como
# segmentos de los que consta la tarea.
# ● Buscar los colaboradores de un determinado usuario, devolviendo una lista de emails de colaboradores que
# participen en alguna de las tareas de las que el usuario es responsable.

#GET /tareas?habilidad=

@tareas_bp.route("/", methods = ['GET'])
def get_tareas_by_habilidad():
    try:
        print("GET TAREAS POR HABILIDAD")
        habilidad = request.args.get("habilidad")
        print(f"habilidad: {habilidad}")
        resultado = tareas.find({"habilidades": habilidad})
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /tareas/getTareas?colaborador=

@tareas_bp.route("/getTareas", methods = ['GET'])

def get_tareas_by_colaborador():
    try:
        print("GET TAREAS POR COLABORADOR")
        colaborador = request.args.get("colaborador")
        print(f"colaborador: {colaborador}")
        resultado = asignaciones.find({"nombre": colaborador})
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        return jsonify({"error": "Error al procesar resultados"}), 400

#POST /asignarColaborador

@tareas_bp.route("/asignarColaborador", methods = ['POST'])

def asignar_colaborador():
    datos = request.json

    if not datos or not datos["nombre"] or not datos["tarea"] or not datos["segmento"]:
        print("Error: Parametros de entrada inválidos")

    nombre = datos["nombre"]
    tarea = ObjectId(datos["tarea"])
    datos["tarea"] = tarea
    colaborador = colaboradores.find_one({"nombre":nombre})
    habilidades = colaborador["habilidades"]
    tarea = tareas.find_one({"_id":tarea})
    habilidades_tarea = tarea["habilidades"]

    if not set(habilidades).isdisjoint(habilidades_tarea):
        asignaciones.insert_one(datos)
        return jsonify({"response": f"Colaborador {nombre} asignado a la tarea {tarea} correctamente"}), 201
    else:
        return jsonify({"error": f"Colaborador {nombre} no tiene las habilidades necesarias para la tarea {tarea}"}), 404

#GET /candidatos?tarea=

@tareas_bp.route("/candidatos", methods = ['GET'])

def get_candidatos():
    try:
        print("GET CANDIDATOS")
        tarea = request.args.get("tarea")
        print(f"tarea: {tarea}")
        tarea = tareas.find_one({"_id":ObjectId(tarea)})
        habilidades_tarea = tarea["habilidades"]
        resultado = colaboradores.find({"habilidades": {"$in": habilidades_tarea}})
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /tareasCompletamenteAsignadas

@tareas_bp.route("/tareasCompletamenteAsignadas", methods=['GET'])
def get_tareas_completamente_asignadas():
    try:
        print("GET TAREAS COMPLETAMENTE ASIGNADAS")
        # Para cada id de tarea, contar cuantas asignaciones hay con ese id
        tareas_completamente_asignadas = []
        tareas_ids = tareas.find()
        for tarea in tareas_ids:
            tarea_id = tarea["_id"]
            conteo_asignaciones = asignaciones.count_documents({"tarea": tarea_id})
            if conteo_asignaciones == tarea["segmentos"]:
                tareas_completamente_asignadas.append(tarea_id)
        resultado = tareas.find({"_id": {"$in": tareas_completamente_asignadas}})
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        return jsonify({"error": "Error al procesar resultados"}), 400

#GET /colaboradoresUsuario?responsable=

@colaboradores_bp.route("/colaboradoresUsuario", methods = ['GET'])

def get_colaboradores_usuario():
    try:
        print("GET COLABORADORES DE UN USUARIO")
        responsable = request.args.get("responsable")
        print(f"responsable: {responsable}")
        tareas_responsable = tareas.find({"responsable": responsable})
        tareas_responsable_ids = []
        for tarea in tareas_responsable:
            tareas_responsable_ids.append(tarea["_id"])
        resultado = asignaciones.find({"tarea": {"$in": tareas_responsable_ids}})
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 404
    try:
        resultado_json = json.loads(json_util.dumps(resultado))
        return jsonify(resultado_json)
    except Exception as e:
        print(f"Error al procesar resultados: {e}")
        return jsonify({"error": "Error al procesar resultados"}), 400
