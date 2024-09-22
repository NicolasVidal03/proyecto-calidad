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

app.config[os.getenv('valor')] = os.getenv('key')

exception_html = "exceptionGeneral.html"
indexAdmin_html = "indexAdmin.html"
index_html = "index.html"
detalleProducto_html = "verDetalleDeProducto.html"
success_html = "success.html"

union_categoria = "$union.categoria"
detalle_pedido = "$detallePedido"
project_call = "$project"
id_producto = "$detallePedido.idProducto"
id_cliente = "_id.idCliente"
agrupar = "$group"
ordenar = "$sort"
union_nombre = "$union.nombre"
id_usuario = "$idUsuario"
pedido_cantidad = "$detallePedido.cantidad"
unir = "$union"
filtrar = "$match"
unir_descripcion = "$union.descripcion"
descomponer_array = "$unwind"
unir_precio = "$union.precio"
unir_id = "$union._id"
combinar_coleciones = "$lookup"
id_producto_usuario = "$_id.idProducto"
id_producto_dentro = "_id.idProducto"
llamado_productos = "$productos"
llamado_id_productos = "productos.idProducto"
productos_subtotal = "$productos.subtotal"
limite = "$limit"


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
        return render_template(exception_html, error = "Debes llenar todos los campos")
    else:
        print("CELULAR CELULAR CELULAR")
        print(celular.isdigit())
        if celular.isdigit() == True:
            resultado = usuarios.find_one({"email":email})
            if resultado:
                return render_template(exception_html, error = "Ya existe una cuenta con ese correo")
            else:
                usuarios.insert_one({ "nombre":nombre,  "apellido":apellido, "direccion":direccion,"email":email, "contrasenia":contrasenia, "estadoDeCuenta":True, "celular":celular, "favoritos": []})
                return render_template('inicio.html')
        else:
            return render_template(exception_html, error = "El numero de telefono debe tener digitos")
            
    
    

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
        return render_template(indexAdmin_html,categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos)
    else:
        if email == "" or contrasenia =="":
            return render_template(exception_html, error = "Debes llenar todos los campos")
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
                pipeline=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idCliente":id_usuario,"idProducto":id_producto},"cantidadProductosPedidosPorUsuario":{"$sum":pedido_cantidad}}},{filtrar:{id_cliente:ObjectId(idCliente)}},{ordenar:SON([("cantidadProductosPedidosPorUsuario",-1)])},{project_call:{"_idProductosFavs":id_producto_usuario,"_id":0}},{combinar_coleciones:{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
                productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
                pipeline2=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idProducto":id_producto},"cantidadVecesPedido":{"$sum":pedido_cantidad}}},{ordenar:SON([("cantidadVecesPedido",-1)])},{limite:9},{combinar_coleciones:{"from":"Productos","localField":id_producto_dentro,"foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
                productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
                return render_template(index_html,categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
            else:
               # print("el correo y/o la contrasenia son incorrectos")
                return render_template('noEncontrado.html')
            


@app.route('/index') 
def index():
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    productosSolicitadosTodos=list(db.Productos.find())
    pipeline=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idCliente":id_usuario,"idProducto":id_producto},"cantidadProductosPedidosPorUsuario":{"$sum":pedido_cantidad}}},{filtrar:{id_cliente:ObjectId(idCliente)}},{ordenar:SON([("cantidadProductosPedidosPorUsuario",-1)])},{project_call:{"_idProductosFavs":id_producto_usuario,"_id":0}},{combinar_coleciones:{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
    productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
    pipeline2=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idProducto":id_producto},"cantidadVecesPedido":{"$sum":pedido_cantidad}}},{ordenar:SON([("cantidadVecesPedido",-1)])},{limite:9},{combinar_coleciones:{"from":"Productos","localField":id_producto_dentro,"foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
    productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
    return render_template(index_html,categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
            
    

@app.route('/indexAdmin') 
def indexAdmin():
    productosSolicitadosTodos=list(db.Productos.find())
    return render_template(indexAdmin_html,productosRecibidosTodos=productosSolicitadosTodos)

@app.route('/') 
def inicio():
    productosSolicitadosTodos=list(db.Productos.find())
    pipeline=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idCliente":id_usuario,"idProducto":id_producto},"cantidadProductosPedidosPorUsuario":{"$sum":pedido_cantidad}}},{filtrar:{id_cliente:ObjectId("637ad222cca958ea8f837c20")}},{ordenar:SON([("cantidadProductosPedidosPorUsuario",-1)])},{project_call:{"_idProductosFavs":id_producto_usuario,"_id":0}},{combinar_coleciones:{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
    productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
    pipeline2=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idProducto":id_producto},"cantidadVecesPedido":{"$sum":pedido_cantidad}}},{ordenar:SON([("cantidadVecesPedido",-1)])},{limite:9},{combinar_coleciones:{"from":"Productos","localField":id_producto_dentro,"foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
    productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
    return render_template('inicio.html',categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)



@app.route('/irLogin')
def irLogin():
    return render_template('login.html')
@app.route('/productosPorCategoria/<categoriaSolicitada>')
def productosPorCategoria(categoriaSolicitada):
    a = 0
    pipeline=[{filtrar:{"categoria":categoriaSolicitada}}]
    productosSolicitados=list(db.Productos.aggregate(pipeline))
    correoCliente = str(session['usuario'])
    for i in productosSolicitados:
        a = a + 1
    if a !=  0:
        return render_template('productosPorCategoria.html',productosRecibidos=productosSolicitados, correoClienteRecibido = correoCliente)
    else:
        return render_template(exception_html, error="No existen productos de esa categoria")



@app.route('/verDetalleDeProducto/<_idSolicitado>')
def verDetalleDeProducto(_idSolicitado):
    
    pipeline=[{filtrar:{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline)))[0]
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2 = [{descomponer_array:llamado_productos},{filtrar:{"idCliente":ObjectId(idCliente),llamado_id_productos :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline2)))
    
    
    return render_template(detalleProducto_html,productoRecibido=productoSolicitado, estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente)



@app.route('/success')
def success():
    return render_template(success_html)
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
    return render_template(success_html)


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
    
    pipeline = [{descomponer_array:llamado_productos},{filtrar:{"idCliente":ObjectId(idCliente),llamado_id_productos:ObjectId(idP)}},{project_call:{"_id":False,"idProducto":"$productos.idProducto" ,"cantidad":"$productos.cantidad","subtotal":productos_subtotal}}]
    obtenerParametros = (list(db.Carrito.aggregate(pipeline)))
    

    
    db.Carrito.update_one({"idCliente":ObjectId(idCliente)},{"$pull":{"productos": obtenerParametros[0] }})
    #CAMBIAR POR UN succersCarrito
    return render_template('successCarrito.html',idProductoPedido=idP,mensaje="Se elimino el productod el carrito")

@app.route('/verCarrito')
def verCarrito():
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
    pipeline=[{filtrar:{"idCliente":ObjectId(idCliente)}},{descomponer_array:llamado_productos},{combinar_coleciones:{"from": "Productos","localField": llamado_id_productos,"foreignField": "_id", "as": "extension"}},{descomponer_array:"$extension"},{project_call:{"_id":False,"idProducto":"$productos.idProducto","nombre":"$extension.nombre","categoria":"$extension.categoria","cantidad":"$productos.cantidad","subtotal":productos_subtotal}}]
    
    productosEnCarrito=list(db.Carrito.aggregate(pipeline))
    
    pipeline2=[{filtrar:{"idCliente":ObjectId(idCliente)}},{descomponer_array:llamado_productos},{agrupar:{"_id":"$idCliente","total":{"$sum":productos_subtotal}}}]
    total = float(list(db.Carrito.aggregate(pipeline2))[0].get('total'))
    
    
    return render_template('carritoDeProductos.html', productosRecibidos=productosEnCarrito, totalAPagar=total)

##############DEL ALE###############
@app.route('/agregarProductoAFavs/<_idSolicitado>')
def agregarAFavs(_idSolicitado):
    a = 0
   # print(session.get('usuario'))
    pipeline = [{descomponer_array: "$favoritos"},{filtrar: {"$and": [{'email':session.get('usuario')}, {"favoritos": ObjectId(_idSolicitado)}]}}]
    estaEnFavoritosDeUsuario = usuarios.aggregate(pipeline)
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2=[{filtrar:{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline2)))[0]
    
    
    pipeline3 = [{descomponer_array:llamado_productos},{filtrar:{"idCliente":ObjectId(idCliente),llamado_id_productos :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline3)))
    
    for element in estaEnFavoritosDeUsuario:
        a = a + 1
    if a == 0:
        email = session.get("usuario")
        filter = {'email': email}
        newvalues = { "$push": { 'favoritos': ObjectId(_idSolicitado) } }
        res = usuarios.update_one(filter, newvalues)
        return render_template(detalleProducto_html,productoRecibido=productoSolicitado, exito=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message= "Producto añadido a favoritos exitosamente.")
    elif a > 0:
        return render_template(detalleProducto_html,productoRecibido=productoSolicitado, error=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="Este producto ya fue añadido previamente.")
####################################



##############DEL ALE 3###############
@app.route('/eliminarDeFavs/<_idSolicitado>')
def eliminarDeFavs(_idSolicitado):
    a = 0
   # print(session.get('usuario'))
    pipeline = [{descomponer_array: "$favoritos"},{filtrar: {"$and": [{'email':session.get('usuario')}, {"favoritos": ObjectId(_idSolicitado)}]}}]
    estaEnFavoritosDeUsuario = usuarios.aggregate(pipeline)
    
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
        
    pipeline2=[{filtrar:{"_id":ObjectId(_idSolicitado)}}]
    productoSolicitado=(list(db.Productos.aggregate(pipeline2)))[0]
    
    
    pipeline3 = [{descomponer_array:llamado_productos},{filtrar:{"idCliente":ObjectId(idCliente),llamado_id_productos :ObjectId(_idSolicitado)}}]
    enCarrito = len(list(db.Carrito.aggregate(pipeline3)))
    
    for element in estaEnFavoritosDeUsuario:
        a = a + 1
    if a != 0:
        email = session.get("usuario")
        filter = {'email': email}
        newvalues = { "$pull": { 'favoritos': ObjectId(_idSolicitado) } }
        res = usuarios.update_one(filter, newvalues)
        return render_template(detalleProducto_html,productoRecibido=productoSolicitado, exito=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="Producto eliminado de favoritos correctamente.")
    elif a == 0:
        return render_template(detalleProducto_html,productoRecibido=productoSolicitado, info=True,estaEnCarrito=enCarrito,correoClienteRecibido=correoCliente, message="El producto no se encuentra en favoritos")
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
        return render_template(indexAdmin_html, categorias=categoriasDelPrograma, productosRecibidosTodos=productosSolicitadosTodos)
    
        
        
    
    if correoCliente!="admin":
        correoCliente = str(session['usuario'])
        consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
        idCliente = consultaCliente[0].get('_id')
        productosSolicitadosTodos=list(db.Productos.find())
        pipeline=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idCliente":id_usuario,"idProducto":id_producto},"cantidadProductosPedidosPorUsuario":{"$sum":pedido_cantidad}}},{filtrar:{id_cliente:ObjectId(idCliente)}},{ordenar:SON([("cantidadProductosPedidosPorUsuario",-1)])},{project_call:{"_idProductosFavs":id_producto_usuario,"_id":0}},{combinar_coleciones:{"from":"Productos","localField":"_idProductosFavs","foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
        productosSolicitadosMasComprados=list(db.Pedidos.aggregate(pipeline))
        pipeline2=[{descomponer_array:detalle_pedido},{agrupar:{"_id":{"idProducto":id_producto},"cantidadVecesPedido":{"$sum":pedido_cantidad}}},{ordenar:SON([("cantidadVecesPedido",-1)])},{limite:9},{combinar_coleciones:{"from":"Productos","localField":id_producto_dentro,"foreignField":"_id","as":"union"}},{descomponer_array:unir},{project_call:{"_id":unir_id,"nombre":union_nombre,"categoria":union_categoria,"precio":unir_precio,"descripcion":unir_descripcion}}]
        productosSolicitadosMasVendidos=list(db.Pedidos.aggregate(pipeline2))
        return render_template(index_html,categorias=categoriasDelPrograma,productosRecibidosTodos=productosSolicitadosTodos,productosMasComprados=productosSolicitadosMasComprados,productosMasVendidos=productosSolicitadosMasVendidos)
     
@app.route('/checkOut/<total>')
def checkOut(total):
    
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))
    idCliente = consultaCliente[0].get('_id')
    
     
        
    pipeline=[{filtrar:{"idCliente":ObjectId(idCliente)}},{combinar_coleciones:{"from":"Usuarios","localField":"idCliente","foreignField":"_id","as": "extension" }},{descomponer_array:"$extension"},{project_call:{"_id":False,"idCliente":True,"nombre":"$extension.nombre","apellido":"$extension.apellido","email":"$extension.email","celular":"$extension.celular","direccion":"$extension.direccion","productos":True}}]
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
        
        return render_template(success_html)

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
    pipeline=[{filtrar:{"_id":ObjectId(_idSolicitado)}}]
    usuarioSolicitado=(list(db.Usuarios.aggregate(pipeline)))[0]
    
    clientess =  usuarios.find({})
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))

    return render_template('verCuenta.html',usuario=usuarioSolicitado, clientes = clientess,correoClienteRecibido=correoCliente)


################################################################################

@app.route('/verMiCuenta')
def verMiCuenta():
    pipeline=[{filtrar:{"email":session.get("usuario")}}]
    usuarioSolicitado=(list(db.Usuarios.aggregate(pipeline)))[0]

    clientess =  usuarios.find({})
    correoCliente = str(session['usuario'])
    consultaCliente = list(db.Usuarios.find({'email':correoCliente},{'_id':1}))

    return render_template('verCuenta.html',usuario=usuarioSolicitado, clientes = clientess,correoClienteRecibido=correoCliente)


if __name__=='__main__':
    app.run(debug = False)




