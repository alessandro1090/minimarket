from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os

app = Flask(__name__)
app.secret_key = "minimarket_secret"

ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_CLIENTES  = "clientes.json"
ARCHIVO_COMPRAS   = "compras.json"

ADMIN_USER = "admin"
ADMIN_PASS = "margot123"

PRODUCTOS_INICIALES = [
    {"id": 1, "nombre": "Arroz Extra (1kg)", "precio": 4.50, "stock": 50, "categoria": "abarrotes", "imagen": "https://www.elcomercio.com/wp-content/uploads/2024/01/arroz.jpg"},
    {"id": 2, "nombre": "Fideos Tallarin (500g)", "precio": 2.80, "stock": 40, "categoria": "abarrotes", "imagen": "https://promart.vteximg.com.br/arquivos/ids/2357732-1000-1000/imagen-del-producto.jpg"},
    {"id": 3, "nombre": "Aceite de Cocina (1L)", "precio": 8.50, "stock": 30, "categoria": "abarrotes", "imagen": "https://wong.vteximg.com.br/arquivos/ids/231810-1000-1000/7751040.jpg"},
    {"id": 4, "nombre": "Leche Evaporada", "precio": 4.20, "stock": 60, "categoria": "lacteos", "imagen": "https://wong.vteximg.com.br/arquivos/ids/289397-1000-1000/LECHE-EVAPORADA-GLORIA-TARRO-400G.jpg"},
    {"id": 5, "nombre": "Yogurt (1L)", "precio": 6.50, "stock": 20, "categoria": "lacteos", "imagen": "https://wong.vteximg.com.br/arquivos/ids/205230-1000-1000/yogurt-gloria-fresa-1l.jpg"},
    {"id": 6, "nombre": "Gaseosa 1.5L", "precio": 6.00, "stock": 35, "categoria": "bebidas", "imagen": "https://wong.vteximg.com.br/arquivos/ids/193163-1000-1000/coca-cola-1-5l.jpg"},
    {"id": 7, "nombre": "Agua de Mesa (625ml)", "precio": 1.50, "stock": 100, "categoria": "bebidas", "imagen": "https://wong.vteximg.com.br/arquivos/ids/192521-1000-1000/agua-san-luis-625ml.jpg"},
    {"id": 8, "nombre": "Detergente (500g)", "precio": 5.90, "stock": 25, "categoria": "limpieza", "imagen": "https://wong.vteximg.com.br/arquivos/ids/205944-1000-1000/detergente-ariel-500g.jpg"},
    {"id": 9, "nombre": "Lejia (1L)", "precio": 3.50, "stock": 30, "categoria": "limpieza", "imagen": "https://wong.vteximg.com.br/arquivos/ids/200104-1000-1000/lejia-clorox-1l.jpg"},
    {"id": 10, "nombre": "Chifles (100g)", "precio": 2.00, "stock": 45, "categoria": "snacks", "imagen": "https://wong.vteximg.com.br/arquivos/ids/193856-1000-1000/chifles-don-victorio-100g.jpg"},
]

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

def es_admin():
    return session.get("admin") == True

# ── LOGIN ─────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["usuario"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            flash("Bienvenido, admin.", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("base.html", pagina="login")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("inicio"))

# ── INICIO ───────────────────────────────────────────────
@app.route("/")
def inicio():
    total_productos = len(cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES))
    total_clientes  = len(cargar(ARCHIVO_CLIENTES))
    total_compras   = len(cargar(ARCHIVO_COMPRAS))
    carrito_count   = len(session.get("carrito", []))
    return render_template("base.html", pagina="inicio",
                           total_productos=total_productos,
                           total_clientes=total_clientes,
                           total_compras=total_compras,
                           carrito_count=carrito_count,
                           admin=es_admin())

# ── PRODUCTOS ─────────────────────────────────────────────
@app.route("/productos")
def productos():
    lista     = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    busqueda  = request.args.get("q", "").lower()
    categoria = request.args.get("categoria", "")
    if busqueda:
        lista = [p for p in lista if busqueda in p["nombre"].lower()]
    if categoria:
        lista = [p for p in lista if p["categoria"] == categoria]
    categorias    = ["abarrotes", "bebidas", "lacteos", "limpieza", "snacks"]
    carrito_count = len(session.get("carrito", []))
    return render_template("base.html", pagina="productos", productos=lista,
                           busqueda=busqueda, categorias=categorias,
                           categoria_sel=categoria, admin=es_admin(),
                           carrito_count=carrito_count)

@app.route("/productos/agregar", methods=["GET", "POST"])
def agregar_producto():
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
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
    return render_template("base.html", pagina="form_producto", accion="agregar", admin=es_admin())

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
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
    return render_template("base.html", pagina="form_producto", accion="editar", producto=producto, admin=es_admin())

@app.route("/productos/eliminar/<int:id>")
def eliminar_producto(id):
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
    lista = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    guardar(ARCHIVO_PRODUCTOS, [p for p in lista if p["id"] != id])
    flash("Producto eliminado.", "danger")
    return redirect(url_for("productos"))

# ── CLIENTES ─────────────────────────────────────────────
@app.route("/clientes")
def clientes():
    lista    = cargar(ARCHIVO_CLIENTES)
    busqueda = request.args.get("q", "").lower()
    if busqueda:
        lista = [c for c in lista if busqueda in c["nombre"].lower() or busqueda in c["dni"]]
    return render_template("base.html", pagina="clientes", clientes=lista, busqueda=busqueda, admin=es_admin())

@app.route("/clientes/agregar", methods=["GET", "POST"])
def agregar_cliente():
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
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
    return render_template("base.html", pagina="form_cliente", accion="agregar", admin=es_admin())

@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
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
    return render_template("base.html", pagina="form_cliente", accion="editar", cliente=cliente, admin=es_admin())

@app.route("/clientes/eliminar/<int:id>")
def eliminar_cliente(id):
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
    lista = cargar(ARCHIVO_CLIENTES)
    guardar(ARCHIVO_CLIENTES, [c for c in lista if c["id"] != id])
    flash("Cliente eliminado.", "danger")
    return redirect(url_for("clientes"))

# ── COMPRAS ───────────────────────────────────────────────
@app.route("/compras")
def compras():
    lista          = cargar(ARCHIVO_COMPRAS)
    clientes       = cargar(ARCHIVO_CLIENTES)
    productos      = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    clientes_dict  = {c["id"]: c["nombre"] for c in clientes}
    productos_dict = {p["id"]: p for p in productos}
    return render_template("base.html", pagina="compras", compras=lista,
                           clientes_dict=clientes_dict, productos_dict=productos_dict, admin=es_admin())

@app.route("/compras/nueva", methods=["GET", "POST"])
def nueva_compra():
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
    clientes  = cargar(ARCHIVO_CLIENTES)
    productos = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    if request.method == "POST":
        compras_lista = cargar(ARCHIVO_COMPRAS)
        cliente_id    = int(request.form["cliente_id"])
        producto_id   = int(request.form["producto_id"])
        cantidad      = int(request.form["cantidad"])
        producto = next((p for p in productos if p["id"] == producto_id), None)
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
        flash("Compra registrada.", "success")
        return redirect(url_for("compras"))
    return render_template("base.html", pagina="form_compra",
                           clientes=clientes, productos=productos, admin=es_admin())

@app.route("/compras/eliminar/<int:id>")
def eliminar_compra(id):
    if not es_admin():
        flash("Necesitas iniciar sesión.", "danger")
        return redirect(url_for("login"))
    lista = cargar(ARCHIVO_COMPRAS)
    guardar(ARCHIVO_COMPRAS, [c for c in lista if c["id"] != id])
    flash("Compra eliminada.", "danger")
    return redirect(url_for("compras"))

# ── CARRITO ───────────────────────────────────────────────
@app.route("/carrito/agregar/<int:producto_id>")
def agregar_al_carrito(producto_id):
    productos = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    producto  = next((p for p in productos if p["id"] == producto_id), None)
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos"))
    carrito = session.get("carrito", [])
    item    = next((i for i in carrito if i["producto_id"] == producto_id), None)
    if item:
        if item["cantidad"] < producto["stock"]:
            item["cantidad"] += 1
            flash(f"Una unidad más de {producto['nombre']} agregada.", "success")
        else:
            flash("No hay más stock disponible.", "danger")
    else:
        carrito.append({"producto_id": producto_id, "cantidad": 1})
        flash(f"{producto['nombre']} agregado al carrito.", "success")
    session["carrito"] = carrito
    return redirect(url_for("productos"))

@app.route("/carrito")
def ver_carrito():
    productos      = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    productos_dict = {p["id"]: p for p in productos}
    carrito        = session.get("carrito", [])
    items  = []
    total  = 0
    for item in carrito:
        p = productos_dict.get(item["producto_id"])
        if p:
            subtotal = round(p["precio"] * item["cantidad"], 2)
            total   += subtotal
            items.append({"producto": p, "cantidad": item["cantidad"], "subtotal": subtotal})
    carrito_count = len(carrito)
    return render_template("base.html", pagina="carrito", items=items,
                           total=round(total, 2), carrito_count=carrito_count, admin=es_admin())

@app.route("/carrito/quitar/<int:producto_id>")
def quitar_del_carrito(producto_id):
    carrito = session.get("carrito", [])
    session["carrito"] = [i for i in carrito if i["producto_id"] != producto_id]
    flash("Producto eliminado del carrito.", "danger")
    return redirect(url_for("ver_carrito"))

@app.route("/carrito/confirmar", methods=["POST"])
def confirmar_compra():
    carrito = session.get("carrito", [])
    if not carrito:
        flash("Tu carrito está vacío.", "danger")
        return redirect(url_for("ver_carrito"))
    productos      = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    productos_dict = {p["id"]: p for p in productos}
    compras_lista  = cargar(ARCHIVO_COMPRAS)
    clientes       = cargar(ARCHIVO_CLIENTES)
    cliente_id     = clientes[0]["id"] if clientes else 0
    for item in carrito:
        p = productos_dict.get(item["producto_id"])
        if not p or item["cantidad"] > p["stock"]:
            flash(f"Stock insuficiente para: {p['nombre'] if p else 'producto'}", "danger")
            return redirect(url_for("ver_carrito"))
    for item in carrito:
        p = productos_dict.get(item["producto_id"])
        p["stock"] -= item["cantidad"]
        compras_lista.append({
            "id":          nuevo_id(compras_lista),
            "cliente_id":  cliente_id,
            "producto_id": item["producto_id"],
            "cantidad":    item["cantidad"],
            "total":       round(p["precio"] * item["cantidad"], 2)
        })
    guardar(ARCHIVO_PRODUCTOS, productos)
    guardar(ARCHIVO_COMPRAS, compras_lista)
    session["carrito"] = []
    flash("¡Compra realizada con éxito!", "success")
    return redirect(url_for("inicio"))

# ── DASHBOARD ─────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if not es_admin():
        flash("Acceso solo para admin.", "danger")
        return redirect(url_for("login"))
    productos  = cargar(ARCHIVO_PRODUCTOS, PRODUCTOS_INICIALES)
    compras    = cargar(ARCHIVO_COMPRAS)
    clientes   = cargar(ARCHIVO_CLIENTES)
    categorias = ["abarrotes", "bebidas", "lacteos", "limpieza", "snacks"]

    ventas_cat   = {c: 0 for c in categorias}
    ingresos_cat = {c: 0.0 for c in categorias}
    prod_dict    = {p["id"]: p for p in productos}
    prod_vendidos = {}

    for compra in compras:
        p = prod_dict.get(compra["producto_id"])
        if p:
            cat = p.get("categoria", "otros")
            if cat in ventas_cat:
                ventas_cat[cat]   += compra["cantidad"]
                ingresos_cat[cat] += compra["total"]
            pid = compra["producto_id"]
            prod_vendidos[pid] = prod_vendidos.get(pid, 0) + compra["cantidad"]

    top = sorted(prod_vendidos.items(), key=lambda x: x[1], reverse=True)[:5]
    top_productos = [{"nombre": prod_dict[pid]["nombre"], "vendidos": cant} for pid, cant in top if pid in prod_dict]

    stock_cat = {c: 0 for c in categorias}
    for p in productos:
        cat = p.get("categoria", "otros")
        if cat in stock_cat:
            stock_cat[cat] += p["stock"]

    return render_template("base.html", pagina="dashboard",
                           total_productos=len(productos),
                           total_clientes=len(clientes),
                           total_compras=len(compras),
                           categorias_labels=categorias,
                           categorias_data=[ventas_cat[c] for c in categorias],
                           ingresos_data=[round(ingresos_cat[c], 2) for c in categorias],
                           stock_data=[stock_cat[c] for c in categorias],
                           top_productos=top_productos,
                           admin=es_admin())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
