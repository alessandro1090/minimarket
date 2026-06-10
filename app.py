from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = "minimarket_secret"

ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_CLIENTES  = "clientes.json"
ARCHIVO_COMPRAS   = "compras.json"

PRODUCTOS_INICIALES = [
    {"id": 1, "nombre": "Arroz Extra (1kg)",     "precio": 4.50, "stock": 50, "categoria": "abarrotes", "imagen": "https://www.elcomercio.com/wp-content/uploads/2024/01/arroz.jpg"},
    {"id": 2, "nombre": "Fideos Tallarin (500g)", "precio": 2.80, "stock": 40, "categoria": "abarrotes", "imagen": "https://promart.vteximg.com.br/arquivos/ids/2357732-1000-1000/imagen-del-producto.jpg"},
    {"id": 3, "nombre": "Aceite de Cocina (1L)",  "precio": 8.50, "stock": 30, "categoria": "abarrotes", "imagen": "https://wong.vteximg.com.br/arquivos/ids/231810-1000-1000/7751040.jpg"},
    {"id": 4, "nombre": "Leche Evaporada",         "precio": 4.20, "stock": 60, "categoria": "lacteos",   "imagen": "https://wong.vteximg.com.br/arquivos/ids/289397-1000-1000/LECHE-EVAPORADA-GLORIA-TARRO-400G.jpg"},
    {"id": 5, "nombre": "Yogurt (1L)",             "precio": 6.50, "stock": 20, "categoria": "lacteos",   "imagen": "https://wong.vteximg.com.br/arquivos/ids/205230-1000-1000/yogurt-gloria-fresa-1l.jpg"},
    {"id": 6, "nombre": "Gaseosa 1.5L",            "precio": 6.00, "stock": 35, "categoria": "bebidas",   "imagen": "https://wong.vteximg.com.br/arquivos/ids/193163-1000-1000/coca-cola-1-5l.jpg"},
    {"id": 7, "nombre": "Agua de Mesa (625ml)",    "precio": 1.50, "stock": 100,"categoria": "bebidas",   "imagen": "https://wong.vteximg.com.br/arquivos/ids/192521-1000-1000/agua-san-luis-625ml.jpg"},
    {"id": 8, "nombre": "Detergente (500g)",       "precio": 5.90, "stock": 25, "categoria": "limpieza",  "imagen": "https://wong.vteximg.com.br/arquivos/ids/205944-1000-1000/detergente-ariel-500g.jpg"},
    {"id": 9, "nombre": "Lejia (1L)",              "precio": 3.50, "stock": 30, "categoria": "limpieza",  "imagen": "https://wong.vteximg.com.br/arquivos/ids/200104-1000-1000/lejia-clorox-1l.jpg"},
    {"id": 10,"nombre": "Chifles (100g)",           "precio": 2.00, "stock": 45, "categoria": "snacks",    "imagen": "https://wong.vteximg.com.br/arquivos/ids/193856-1000-1000/chifles-don-victorio-100g.jpg"},
]

# ── helpers ──────────────────────────────────────────────
def cargar(archivo, iniciales=[]):
    if not os.path.exists(archivo):
        guardar(archivo, iniciales)
        return iniciales
    with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def nuevo_id(lista):
    return max([x["id"] for x in lista], default=0) + 1

# ── INICIO ───────────────────────────────────────────────
@app.route("/")
def inicio():
    total_productos = len(cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES))
    total_clientes  = len(cargar(ARCHIVO_CLIENTES))
    total_compras   = len(cargar(ARCHIVO_COMPRAS))
    return render_template("base.html", pagina="inicio",
                           total_productos=total_productos,
                           total_clientes=total_clientes,
                           total_compras=total_compras)

# ── PRODUCTOS CRUD ────────────────────────────────────────
@app.route("/productos")
def productos():
    lista     = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    busqueda  = request.args.get("q", "").lower()
    categoria = request.args.get("categoria", "")
    if busqueda:
        lista = [p for p in lista if busqueda in p["nombre"].lower()]
    if categoria:
        lista = [p for p in lista if p["categoria"] == categoria]
    categorias = ["abarrotes", "bebidas", "lacteos", "limpieza", "snacks"]
    return render_template("base.html", pagina="productos", productos=lista,
                           busqueda=busqueda, categorias=categorias, categoria_sel=categoria)

@app.route("/productos/agregar", methods=["GET", "POST"])
def agregar_producto():
    if request.method == "POST":
        lista = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
        lista.append({
            "id":        nuevo_id(lista),
            "nombre":    request.form["nombre"],
            "precio":    float(request.form["precio"]),
            "stock":     int(request.form["stock"]),
            "categoria": request.form["categoria"],
            "imagen":    request.form["imagen"] or "https://via.placeholder.com/200x140?text=Sin+imagen"
        })
        guardar(ARCHIVO_PRODUCTOS, lista)
        flash("Producto agregado.", "success")
        return redirect(url_for("productos"))
    return render_template("base.html", pagina="form_producto", accion="agregar")

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    lista    = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    producto = next((p for p in lista if p["id"] == id), None)
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos"))
    if request.method == "POST":
        producto["nombre"]    = request.form["nombre"]
        producto["precio"]    = float(request.form["precio"])
        producto["stock"]     = int(request.form["stock"])
        producto["categoria"] = request.form["categoria"]
        producto["imagen"]    = request.form["imagen"] or producto["imagen"]
        guardar(ARCHIVO_PRODUCTOS, lista)
        flash("Producto actualizado.", "success")
        return redirect(url_for("productos"))
    return render_template("base.html", pagina="form_producto", accion="editar", producto=producto)

@app.route("/productos/eliminar/<int:id>")
def eliminar_producto(id):
    lista = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    guardar(ARCHIVO_PRODUCTOS, [p for p in lista if p["id"] != id])
    flash("Producto eliminado.", "danger")
    return redirect(url_for("productos"))

# ── CLIENTES CRUD ─────────────────────────────────────────
@app.route("/clientes")
def clientes():
    lista    = cargar(ARCHIVO_CLIENTES)
    busqueda = request.args.get("q", "").lower()
    if busqueda:
        lista = [c for c in lista if busqueda in c["nombre"].lower() or busqueda in c["dni"]]
    return render_template("base.html", pagina="clientes", clientes=lista, busqueda=busqueda)

@app.route("/clientes/agregar", methods=["GET", "POST"])
def agregar_cliente():
    if request.method == "POST":
        lista = cargar(ARCHIVO_CLIENTES)
        lista.append({
            "id":       nuevo_id(lista),
            "nombre":   request.form["nombre"],
            "dni":      request.form["dni"],
            "telefono": request.form["telefono"]
        })
        guardar(ARCHIVO_CLIENTES, lista)
        flash("Cliente agregado.", "success")
        return redirect(url_for("clientes"))
    return render_template("base.html", pagina="form_cliente", accion="agregar")

@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    lista   = cargar(ARCHIVO_CLIENTES)
    cliente = next((c for c in lista if c["id"] == id), None)
    if not cliente:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes"))
    if request.method == "POST":
        cliente["nombre"]   = request.form["nombre"]
        cliente["dni"]      = request.form["dni"]
        cliente["telefono"] = request.form["telefono"]
        guardar(ARCHIVO_CLIENTES, lista)
        flash("Cliente actualizado.", "success")
        return redirect(url_for("clientes"))
    return render_template("base.html", pagina="form_cliente", accion="editar", cliente=cliente)

@app.route("/clientes/eliminar/<int:id>")
def eliminar_cliente(id):
    lista = cargar(ARCHIVO_CLIENTES)
    guardar(ARCHIVO_CLIENTES, [c for c in lista if c["id"] != id])
    flash("Cliente eliminado.", "danger")
    return redirect(url_for("clientes"))

# ── COMPRAS ───────────────────────────────────────────────
@app.route("/compras")
def compras():
    lista     = cargar(ARCHIVO_COMPRAS)
    clientes  = cargar(ARCHIVO_CLIENTES)
    productos = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    clientes_dict  = {c["id"]: c["nombre"] for c in clientes}
    productos_dict = {p["id"]: p for p in productos}
    return render_template("base.html", pagina="compras", compras=lista,
                           clientes_dict=clientes_dict, productos_dict=productos_dict)

@app.route("/compras/nueva", methods=["GET", "POST"])
def nueva_compra():
    clientes  = cargar(ARCHIVO_CLIENTES)
    productos = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    if request.method == "POST":
        compras_lista = cargar(ARCHIVO_COMPRAS)
        cliente_id    = int(request.form["cliente_id"])
        producto_id   = int(request.form["producto_id"])
        cantidad      = int(request.form["cantidad"])
        producto = next((p for p in productos if p["id"] == producto_id), None)
        if not producto:
            flash("Producto no válido.", "danger")
            return redirect(url_for("nueva_compra"))
        if cantidad > producto["stock"]:
            flash(f"Stock insuficiente. Solo hay {producto['stock']} unidades.", "danger")
            return redirect(url_for("nueva_compra"))
        producto["stock"] -= cantidad
        guardar(ARCHIVO_PRODUCTOS, productos)
        compras_lista.append({
            "id":          nuevo_id(compras_lista),
            "cliente_id":  cliente_id,
            "producto_id": producto_id,
            "cantidad":    cantidad,
            "total":       round(cantidad * producto["precio"], 2)
        })
        guardar(ARCHIVO_COMPRAS, compras_lista)
        flash("Compra registrada correctamente.", "success")
        return redirect(url_for("compras"))
    return render_template("base.html", pagina="form_compra",
                           clientes=clientes, productos=productos)

@app.route("/compras/eliminar/<int:id>")
def eliminar_compra(id):
    lista = cargar(ARCHIVO_COMPRAS)
    guardar(ARCHIVO_COMPRAS, [c for c in lista if c["id"] != id])
    flash("Compra eliminada.", "danger")
    return redirect(url_for("compras"))

if __name__ == "__main__":
    app.run(debug=True)
    app.run(debug=True)
