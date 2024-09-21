#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 16:07:50 2022

@author: usere
"""

import json
from flask import Flask, render_template, request, redirect, url_for,session
from bson import ObjectId
from pymongo import MongoClient
from bson.son import SON
from dotenv import load_dotenv


from datetime import datetime
import os


load_dotenv()
app = Flask(__name__)
categoriasDelPrograma=["Lacteos","Bebida","Cereales","Galleta"]
client = MongoClient("mongodb://localhost:27017")
db = client["MyPROYECTO"]
usuarios = db["Usuarios"]
productos=db["Productos"]
pedidos=db["Pedidos"]
carrito=db["Carrito"]

app.config['key'] = os.getenv('key')

##############
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
##############


@app.route('/actionRegistrarCuenta', methods=['POST'])
def actionRegistrarCuenta():
    resultat = request.form
    nombre = request.values.get("nombre")
    apellido = request.values.get("apellido")
    email = request.values.get("email")
    contrasenia = request.values.get("contrasenia")
    celular = request.values.get("celular")
    direccion = request.values.get("direccion")
    if nombre == "" or apellido=="" or email == "" or contrasenia == "" or celular == "" or direccion == "":
        return render_template('exceptionGeneral.html', error = "Debes llenar todos los campos")
    else:
        print("CELULAR CELULAR CELULAR")
        print(celular.isdigit())
        if celular.isdigit() == True:
            resultado = usuarios.find_one({"email":email})
            if resultado:
                return render_template('exceptionGeneral.html', error = "Ya existe una cuenta con ese correo")
            else:
                usuarios.insert_one({ "nombre":nombre,  "apellido":apellido, "direccion":direccion,"email":email, "contrasenia":contrasenia, "estadoDeCuenta":True, "celular":celular, "favoritos": []})
                return render_template('inicio.html')
        else:
            return render_template('exceptionGeneral.html', error = "El numero de telefono debe tener digitos")
            
    
    

@app.route('/validarCuenta', methods=['POST'])
def validarCuenta():
    email = request.values.get("Correo")
    contrasenia = request.values.get("Contrasenia")
    if email == "admin" and contrasenia == "erslce":
        resultado = usuarios.find_one( {"email":email, "contrasenia":contrasenia })
        session["usuario"] = email
        idUsr = resultado.get('_id')
        idUsuario = JSONEncoder().encode(idUsr)
        session["idUser"] = idUsuario
        productosSolicitadosTodos=list(db.Productos.find())
        return render_template('indexAdmin.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos)
    else:
        if email == "" or contrasenia =="":
            return render_template('exceptionGeneral.html', error = "Debes llenar todos los campos")
        else:
            resultado = usuarios.find_one( {"email":email, "contrasenia":contrasenia })
            if resultado:
                #ir a la pagina principal pero con distinto parametro
                session["usuario"] = email
                idUsr = resultado.get('_id')
                idUsuario = JSONEncoder().encode(idUsr)
                session["idUser"] = idUsuario
                print(idUsuario)
                #en lugar de ese return podrias colocar el menu principal al cual le pasas el id
                
                correoCliente = str(session['usuario'])
                consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
                idCliente = consultaCliente[0].get('_id')
                
                productosSolicitadosTodos=list(db.Productos.find())
                pipeline=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idCliente":"$idUsuario","idProducto":"$detallePedido.idProducto"},"cantidadProductosPedidosPorUsuario":{"$sum":"$detallePedido.cantidad"}}},{"$match":{"_id.idCliente":ObjectId(idCliente)}},{"$sort":SON([("cantidadProductosPedidosPorUsuario",-1)])},{"$project":{"_idProductosFavs":"$_id.idProducto","_id":0}},{"$lookup":{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
                productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
                pipeline2=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idProducto":"$detallePedido.idProducto"},"cantidadVecesPedido":{"$sum":"$detallePedido.cantidad"}}},{"$sort":SON([("cantidadVecesPedido",-1)])},{"$limit":9},{"$lookup":{"from":"Productos","localField":"_id.idProducto","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
                productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
                return render_template('index.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
            else:
               # print("el correo y/o la contrasenia son incorrectos")
                return render_template('noEncontrado.html')
            


@app.route('/index') 
def index():
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    productosSolicitadosTodos=list(db.Productos.find())
    pipeline=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idCliente":"$idUsuario","idProducto":"$detallePedido.idProducto"},"cantidadProductosPedidosPorUsuario":{"$sum":"$detallePedido.cantidad"}}},{"$match":{"_id.idCliente":ObjectId(idCliente)}},{"$sort":SON([("cantidadProductosPedidosPorUsuario",-1)])},{"$project":{"_idProductosFavs":"$_id.idProducto","_id":0}},{"$lookup":{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
    productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
    pipeline2=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idProducto":"$detallePedido.idProducto"},"cantidadVecesPedido":{"$sum":"$detallePedido.cantidad"}}},{"$sort":SON([("cantidadVecesPedido",-1)])},{"$limit":9},{"$lookup":{"from":"Productos","localField":"_id.idProducto","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
    productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
    return render_template('index.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
            
    

@app.route('/indexAdmin') 
def indexAdmin():
    productosSolicitadosTodos=list(db.Productos.find())
    return render_template('indexAdmin.html',productosRecibidosTodos=productosSolicitadosTodos)

@app.route('/') 
def inicio():
    productosSolicitadosTodos=list(db.Productos.find())
    pipeline=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idCliente":"$idUsuario","idProducto":"$detallePedido.idProducto"},"cantidadProductosPedidosPorUsuario":{"$sum":"$detallePedido.cantidad"}}},{"$match":{"_id.idCliente":ObjectId("637ad222cca958ea8f837c20")}},{"$sort":SON([("cantidadProductosPedidosPorUsuario",-1)])},{"$project":{"_idProductosFavs":"$_id.idProducto","_id":0}},{"$lookup":{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
    productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
    pipeline2=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idProducto":"$detallePedido.idProducto"},"cantidadVecesPedido":{"$sum":"$detallePedido.cantidad"}}},{"$sort":SON([("cantidadVecesPedido",-1)])},{"$limit":9},{"$lookup":{"from":"Productos","localField":"_id.idProducto","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
    productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
    return render_template('inicio.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)



@app.route('/irLogin')
def irLogin():
    return render_template('login.html')
@app.route('/productosPorCategoria/<categoriaSolicitada>')
def productosPorCategoria(categoriaSolicitada):
    a = 0
    pipeline=[{"$match":{"categoria":categoriaSolicitada}}]
    productosSolicitados=list(db.Productos.aggregate(pipeline))
    correoCliente = str(session['usuario'])
    for i in productosSolicitados:
        a = a + 1
    if a !=  0:
        return render_template('productosPorCategoria.html',productosRecibidos=productosSolicitados, correoClienteRecibido = correoCliente)
    else:
        return render_template('exceptionGeneral.html', error="No existen productos de esa categoria")



@app.route('/verDetalleDeProducto/<_idSolicitado>')
def verDetalleDeProducto(_idSolicitado):
    
    pipeline=[{"$match":{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline)))[0]
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2 = [{"$unwind":"$productos"},{"$match":{"idCliente":ObjectId(idCliente),"productos.idProducto" :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline2)))
    
    
    return render_template('verDetalleDeProducto.html',productoRecibido=productoSolicitado, estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente)



@app.route('/success')
def success():
    return render_template('success.html')
@app.route('/irNuevaCuenta')
def irNuevaCuenta():
    return render_template('/nuevaCuenta.html')
#CATALOGO
@app.route('/crearProductoEnCatalogo')
def crearProductoEnCatalogo():
    return render_template('crearProductoEnCatalogo.html',categoriasRecibidas=categoriasDelPrograma)


@app.route('/registradorDeProductoEnCatalogo',methods = ['POST'])
def registradorDeProductoEnCatalogo():
    if request.method == 'POST':
        
        nombreP = request.form['np']
        categoriaP= request.form['cp']
        precioP= request.form['pp']
        descripcionP= request.form['dp']
        urlP = request.form['up']
        precioP=int(precioP)
        nuevo_producto={"nombre":nombreP,"categoria":categoriaP,"precio":precioP,"descripcion":descripcionP, "url":urlP}
        x=productos.insert_one(nuevo_producto)
        print("Id:",x.inserted_id)
        return redirect(url_for('success'))
@app.route('/verCatalogoCompleto')
def verCatalogoCompleto():
    productosSolicitados=list(db.Productos.find())
    return render_template('productosPorCategoria.html',productosRecibidos=productosSolicitados)

@app.route('/modificarProductoDelCatalogo/<id>')
def modificarProductoDelCatalogo(id):
    productoSolicitadoModificar=list(db.Productos.find({"_id":ObjectId(id)}))[0]
    return render_template('modificarProducto.html',productoRecibidoModificar=productoSolicitadoModificar,categoriasRecibidas=categoriasDelPrograma)

@app.route('/modificadorDeProductoEnCatalogo',methods = ['POST'])
def modificadorDeProductoEnCatalogo():
    if request.method == 'POST':
        _idP=request.form['ip']
        nombreP = request.form['np']
        categoriaP= request.form['cp']
        precioP= request.form['pp']
        descripcionP= request.form['dp']
        urlP=request.form['up']
        precioP=int(precioP)
        productos.update_one({"_id":ObjectId(_idP)},{"$set":{"nombre":nombreP,"categoria":categoriaP,"precio":precioP,"descripcion":descripcionP,"url":urlP}})
        return redirect(url_for('success'))
    
@app.route('/eliminadorProductoDelCatalogo/<id>')
def eliminadorProductoDelCatalogo(id):
    productos.delete_one({"_id":ObjectId(id)})
    return render_template('success.html')


##############################################################################

@app.route('/aniadirACarrito/<idP>/<precio>', methods = ['POST'])
def aniadirACarrito(idP, precio):
    if request.method == 'POST':
        
        correoCliente = str(session['usuario'])
        consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
        idCliente = consultaCliente[0].get('_id')
        
        
        cantidad = request.form['cant']
        subtotal =  float(cantidad)*float(precio)
        
        carrito.update_one({"idCliente":ObjectId(idCliente)},{ "$addToSet":{"productos": {"idProducto": ObjectId(idP), "cantidad":float(cantidad), "subtotal":float(subtotal)} } },True)
        #CAMBIAR POR UN succersCarrito
        return render_template('successCarrito.html',idProductoPedido=idP,mensaje="Se agrego el producto al carrito")
        
    
@app.route('/eliminarDeCarrito/<idP>')
def eliminarDeCarrito(idP):
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
    pipeline = [{"$unwind":"$productos"},{"$match":{"idCliente":ObjectId(idCliente),"productos.idProducto":ObjectId(idP)}},{"$project":{"_id":False,"idProducto":"$productos.idProducto" ,"cantidad":"$productos.cantidad","subtotal":"$productos.subtotal"}}]
    obtenerParametros = (list(db.Carrito.aggregate(pipeline)))
    

    
    db.Carrito.update_one({"idCliente":ObjectId(idCliente)},{"$pull":{"productos": obtenerParametros[0] }})
    #CAMBIAR POR UN succersCarrito
    return render_template('successCarrito.html',idProductoPedido=idP,mensaje="Se elimino el productod el carrito")

@app.route('/verCarrito')
def verCarrito():
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
    pipeline=[{"$match":{"idCliente":ObjectId(idCliente)}},{"$unwind":"$productos"},{"$lookup":{"from": "Productos","localField": "productos.idProducto","foreignField": "_id", "as": "extension"}},{"$unwind":"$extension"},{"$project":{"_id":False,"idProducto":"$productos.idProducto","nombre":"$extension.nombre","categoria":"$extension.categoria","cantidad":"$productos.cantidad","subtotal":"$productos.subtotal"}}]
    
    productosEnCarrito=list(db.Carrito.aggregate(pipeline))
    
    pipeline2=[{"$match":{"idCliente":ObjectId(idCliente)}},{"$unwind":"$productos"},{"$group":{"_id":"$idCliente","total":{"$sum":"$productos.subtotal"}}}]
    total = float(list(db.Carrito.aggregate(pipeline2))[0].get('total'))
    
    
    return render_template('carritoDeProductos.html', productosRecibidos=productosEnCarrito, totalAPagar=total)

##############DEL ALE###############
@app.route('/agregarProductoAFavs/<_idSolicitado>')
def agregarAFavs(_idSolicitado):
    a = 0
   # print(session.get('usuario'))
    pipeline = [{"$unwind": "$favoritos"},{"$match": {"$and": [{'email':session.get('usuario')}, {"favoritos": ObjectId(_idSolicitado)}]}}]
    estaEnFavoritosDeUsuario = usuarios.aggregate(pipeline)
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2=[{"$match":{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline2)))[0]
    
    
    pipeline3 = [{"$unwind":"$productos"},{"$match":{"idCliente":ObjectId(idCliente),"productos.idProducto" :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline3)))
    
    for element in estaEnFavoritosDeUsuario:
        a = a + 1
    if a == 0:
        email = session.get("usuario")
        filter = {'email': email}
        newvalues = { "$push": { 'favoritos': ObjectId(_idSolicitado) } }
        res = usuarios.update_one(filter, newvalues)
        return render_template('verDetalleDeProducto.html',productoRecibido=productoSolicitado, exito=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message= "Producto añadido a favoritos exitosamente.")
    elif a > 0:
        return render_template('verDetalleDeProducto.html',productoRecibido=productoSolicitado, error=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="Este producto ya fue añadido previamente.")
####################################



##############DEL ALE 3###############
@app.route('/eliminarDeFavs/<_idSolicitado>')
def eliminarDeFavs(_idSolicitado):
    a = 0
   # print(session.get('usuario'))
    pipeline = [{"$unwind": "$favoritos"},{"$match": {"$and": [{'email':session.get('usuario')}, {"favoritos": ObjectId(_idSolicitado)}]}}]
    estaEnFavoritosDeUsuario = usuarios.aggregate(pipeline)
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2=[{"$match":{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline2)))[0]
    
    
    pipeline3 = [{"$unwind":"$productos"},{"$match":{"idCliente":ObjectId(idCliente),"productos.idProducto" :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline3)))
    
    for element in estaEnFavoritosDeUsuario:
        a = a + 1
    if a != 0:
        email = session.get("usuario")
        filter = {'email': email}
        newvalues = { "$pull": { 'favoritos': ObjectId(_idSolicitado) } }
        res = usuarios.update_one(filter, newvalues)
        return render_template('verDetalleDeProducto.html',productoRecibido=productoSolicitado, exito=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="Producto eliminado de favoritos correctamente.")
    elif a == 0:
        return render_template('verDetalleDeProducto.html',productoRecibido=productoSolicitado, info=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="El producto no se encuentra en favoritos")
####################################

    
@app.route('/buscar',methods = ['POST'])
def buscar():
    if request.method == 'POST':
        nombreProducto=request.form['vb']
        correoCliente = str(session['usuario'])
        consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
        idCliente = consultaCliente[0].get('_id')
        
        #solo busca poniendo la primera letra
        busqueda="^"+nombreProducto
   
        busquedaMinuscula=busqueda.lower()
   
        busquedaMayuscula=busqueda.upper()
    
    
    
        consulta={'$or':[{'nombre':{'$regex':busquedaMinuscula}},{'nombre':{'$regex':busquedaMayuscula}}]}
        productosBuscadosSolicitados=list(productos.find(consulta))
    
    
        return render_template('productosBuscados.html', productosBuscadosRecibidos=productosBuscadosSolicitados,correoClienteRecibido=correoCliente)
@app.route('/vaciarCarrito')
def vaciarCarrito():
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
   
    
    db.Carrito.delete_one({"idCliente":ObjectId(idCliente)})
    correoCliente = str(session['usuario'])
    if correoCliente=="admin":
       
        productosSolicitadosTodos=list(db.Productos.find())
        return render_template('indexAdmin.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos)
    
        
        
    
    if correoCliente!="admin":
        correoCliente = str(session['usuario'])
        consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
        idCliente = consultaCliente[0].get('_id')
        productosSolicitadosTodos=list(db.Productos.find())
        pipeline=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idCliente":"$idUsuario","idProducto":"$detallePedido.idProducto"},"cantidadProductosPedidosPorUsuario":{"$sum":"$detallePedido.cantidad"}}},{"$match":{"_id.idCliente":ObjectId(idCliente)}},{"$sort":SON([("cantidadProductosPedidosPorUsuario",-1)])},{"$project":{"_idProductosFavs":"$_id.idProducto","_id":0}},{"$lookup":{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
        productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
        pipeline2=[{"$unwind":"$detallePedido"},{"$group":{"_id":{"idProducto":"$detallePedido.idProducto"},"cantidadVecesPedido":{"$sum":"$detallePedido.cantidad"}}},{"$sort":SON([("cantidadVecesPedido",-1)])},{"$limit":9},{"$lookup":{"from":"Productos","localField":"_id.idProducto","foreignField":"_id","as":"union"}},{"$unwind":"$union"},{"$project":{"_id":"$union._id","nombre":"$union.nombre","categoria":"$union.categoria","precio":"$union.precio","descripcion":"$union.descripcion"}}]
        productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
        return render_template('index.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
     
@app.route('/checkOut/<total>')
def checkOut(total):
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
     
        
    pipeline=[{"$match":{"idCliente":ObjectId(idCliente)}},{"$lookup":{"from":"Usuarios","localField":"idCliente","foreignField":"_id","as": "extension" }},{"$unwind":"$extension"},{"$project":{"_id":False,"idCliente":True,"nombre":"$extension.nombre","apellido":"$extension.apellido","email":"$extension.email","celular":"$extension.celular","direccion":"$extension.direccion","productos":True}}]
    resumenDePedido = list(db.Carrito.aggregate(pipeline))[0]
    
    
    return render_template('checkOut.html', resumenPedido=resumenDePedido, total=total)


@app.route('/realizarPedido/<total>', methods=['POST'])
def realizarPedido(total):
    
    if request.method == 'POST':
        
        correoCliente = str(session['usuario'])
        consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
        idCliente = consultaCliente[0].get('_id')
        
        
    
        consultaProducto = list(db.Carrito.find({'idCliente': ObjectId(idCliente)}))

        fechaHora = datetime.now()
        nota = request.form['nt']
        tipoDePago = request.form['mp']
        detallePedido = consultaProducto[0].get('productos')
        montoTotal = float(total)
    
        db.Pedidos.insert_one({"idProducto":ObjectId(idCliente), "fechaHora":fechaHora, "nota":nota, "tipoDePago":tipoDePago, "detallePedido":detallePedido, "montoTotal":montoTotal })
        db.Carrito.delete_one({"idCliente":ObjectId(idCliente)})
        
        return render_template('success.html')

#################### DEL ALE 2 ###############################################
@app.route('/mostrarClientes')
def mostrarClientes():
    clientess =  usuarios.find({})
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    return render_template('verClientes.html', clientes = clientess,correoClienteRecibido=correoCliente)
##############################################################################



###################### DEL ALE 4 ###############################################

@app.route('/verCuenta/<_idSolicitado>')
def verCuenta(_idSolicitado):
    pipeline=[{"$match":{"_id":ObjectId(_idSolicitado)}}]
    usuarioSolicitado=(list(db.Usuarios.aggregate(pipeline)))[0]
    
    clientess =  usuarios.find({})
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))

    return render_template('verCuenta.html',usuario=usuarioSolicitado, clientes = clientess,correoClienteRecibido=correoCliente)


################################################################################

@app.route('/verMiCuenta')
def verMiCuenta():
    pipeline=[{"$match":{"email":session.get("usuario")}}]
    usuarioSolicitado=(list(db.Usuarios.aggregate(pipeline)))[0]

    clientess =  usuarios.find({})
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))

    return render_template('verCuenta.html',usuario=usuarioSolicitado, clientes = clientess,correoClienteRecibido=correoCliente)


if __name__=='__main__':
    app.run(debug = False)




