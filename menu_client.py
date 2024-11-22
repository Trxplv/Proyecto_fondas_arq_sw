import requests
import datetime

BASE_URL = "http://localhost"

# Variables globales para sesión
USUARIO_ACTUAL = None
ROL_ACTUAL = None
TOKEN = None

# Menú principal
def menu_principal():
    global USUARIO_ACTUAL, ROL_ACTUAL, TOKEN

    while True:
        print("\n=== Menú Principal ===")
        print("1. Registrarse")
        print("2. Iniciar Sesión")
        print("3. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            if iniciar_sesion():
                if ROL_ACTUAL == 1:
                    menu_visitante()
                elif ROL_ACTUAL == 2:
                    menu_operador()
                elif ROL_ACTUAL == 3:
                    menu_administrador()
        elif opcion == "3":
            print("¡Gracias por usar el sistema! Saliendo...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

# Menús por rol
def menu_visitante():
    while True:
        print("\n=== Menú Visitante ===")
        print("1. Ver Fondas")
        print("2. Reservar Mesa")
        print("3. Mis Opiniones")
        print("4. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            ver_fondas()
        elif opcion == "2":
            reservar_mesa()
        elif opcion == "3":
            mis_opiniones()
        elif opcion == "4":
            break
        else:
            print("Opción no válida.")

def menu_operador():
    while True:
        print("\n=== Menú Operador ===")
        print("1. Ver y Modificar Productos")
        print("2. Ver Opiniones de Mi Fonda")
        print("3. Gestionar Promociones")
        print("4. Alertas de Mesas")
        print("5. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            ver_modificar_productos()
        elif opcion == "2":
            ver_opiniones_fonda()
        elif opcion == "3":
            gestionar_promociones()
        elif opcion == "4":
            alertas_mesas()
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")

def menu_administrador():
    while True:
        print("\n=== Menú Administrador ===")
        print("1. Crear Fonda")
        print("2. Editar o Eliminar Fonda")
        print("3. Gestionar Operadores")
        print("4. Ver Reservas")
        print("5. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            crear_fonda()
        elif opcion == "2":
            editar_eliminar_fonda()
        elif opcion == "3":
            gestionar_operadores()
        elif opcion == "4":
            ver_reservas()
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")

# Funciones generales
def registrar_usuario():
    print("\n=== Registrarse ===")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    contraseña = input("Contraseña: ")
    data = {"nombre": nombre, "apellido": apellido, "tipo": 1, "contraseña": contraseña}
    try:
        response = requests.post(f"{BASE_URL}:8001/usuarios/registro", json=data)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al registrarse:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al registrarse:", e)

def iniciar_sesion():
    global USUARIO_ACTUAL, ROL_ACTUAL, TOKEN

    print("\n=== Iniciar Sesión ===")
    nombre = input("Nombre: ")
    contraseña = input("Contraseña: ")
    data = {"nombre": nombre, "contraseña": contraseña}
    try:
        response = requests.post(f"{BASE_URL}:8001/usuarios/login", json=data)
        if response.status_code == 200:
            usuario = response.json()
            TOKEN = usuario["access_token"]
            headers = {'Authorization': f'Bearer {TOKEN}'}
            # Obtener información del usuario actual
            USUARIO_ACTUAL, ROL_ACTUAL = obtener_info_usuario(headers)
            print(f"Sesión iniciada como {nombre} (Rol: {ROL_ACTUAL})")
            return True
        else:
            print("Credenciales inválidas.")
            return False
    except Exception as e:
        print("Error al iniciar sesión:", e)
        return False

def obtener_info_usuario(headers):
    try:
        response = requests.get(f"{BASE_URL}:8001/usuarios/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["idUser"], data["tipo"]
        else:
            print("Error al obtener información del usuario.")
            return None, None
    except Exception as e:
        print("Error al obtener información del usuario:", e)
        return None, None

# Funciones de visitante
def ver_fondas():
    print("\n=== Ver Fondas ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8002/fondas", headers=headers)
        if response.status_code == 200:
            fondas = response.json().get("fondas", [])
            if not fondas:
                print("No hay fondas disponibles.")
                return
            print("\nFondas Disponibles:")
            for fonda in fondas:
                calificacion = round(fonda.get('calificacion_promedio', 0), 2)
                print(f"- ID: {fonda['id']}, Nombre: {fonda['nombre']}, Calificación: {calificacion}/5")
            # Opciones adicionales
            print("\n¿Deseas ver detalles de una fonda?")
            opcion = input("Escribe 's' para sí o cualquier otra tecla para volver: ")
            if opcion.lower() == 's':
                id_fonda = int(input("Ingresa el ID de la fonda: "))
                ver_detalles_fonda(id_fonda)
        else:
            print("Error al listar fondas:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al listar fondas:", e)

def ver_detalles_fonda(id_fonda):
    print("\n=== Detalles de la Fonda ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        # Obtener detalles de la fonda (si hay un endpoint específico)
        # Aquí asumimos que el endpoint /fondas/{idFonda} devuelve detalles
        response = requests.get(f"{BASE_URL}:8002/fondas/{id_fonda}", headers=headers)
        if response.status_code == 200:
            fonda = response.json()
            print(f"Nombre: {fonda['nombre']}")
            print(f"Descripción: {fonda['descripcion']}")
            print(f"Calificación Promedio: {round(fonda.get('calificacion_promedio', 0), 2)}/5")
            # Opciones para ver opiniones o precios
            print("\nOpciones:")
            print("1. Ver Opiniones")
            print("2. Ver Precios y Promociones")
            print("3. Volver")
            opcion = input("Selecciona una opción: ")
            if opcion == "1":
                ver_opiniones_fonda(id_fonda)
            elif opcion == "2":
                ver_precios_promociones(id_fonda)
            elif opcion == "3":
                return
            else:
                print("Opción no válida.")
        else:
            print("Error al obtener detalles de la fonda:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener detalles de la fonda:", e)

def ver_opiniones_fonda(id_fonda):
    print("\n=== Opiniones de la Fonda ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8003/opiniones/fonda/{id_fonda}", headers=headers)
        if response.status_code == 200:
            opiniones = response.json().get("opiniones", [])
            if not opiniones:
                print("No hay opiniones para esta fonda.")
                return
            for opinion in opiniones:
                print(f"\nUsuario: {opinion['usuario']}")
                print(f"Calificación: {opinion['calificacion']}/5")
                print(f"Comentario: {opinion['opinion']}")
                respuesta = opinion.get('respuesta')
                if respuesta:
                    print(f"Respuesta del Operador: {respuesta}")
        else:
            print("Error al obtener opiniones:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener opiniones:", e)

def ver_precios_promociones(id_fonda):
    print("\n=== Precios y Promociones ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        # Obtener productos normales
        response_productos = requests.get(f"{BASE_URL}:8005/productos/fonda/{id_fonda}", headers=headers)
        # Obtener promociones
        response_promociones = requests.get(f"{BASE_URL}:8005/productos/fonda/{id_fonda}/promociones", headers=headers)
        if response_productos.status_code == 200 and response_promociones.status_code == 200:
            productos = response_productos.json().get("productos", [])
            promociones = response_promociones.json().get("promociones", [])
            print("\n--- Promociones ---")
            if not promociones:
                print("No hay promociones disponibles.")
            else:
                for producto in promociones:
                    print(f"Producto: {producto['nombre']}, Precio: {producto['precio']}, Stock: {producto['stock']}")
            print("\n--- Productos ---")
            if not productos:
                print("No hay productos disponibles.")
            else:
                for producto in productos:
                    print(f"Producto: {producto['nombre']}, Precio: {producto['precio']}, Stock: {producto['stock']}")
        else:
            print("Error al obtener precios y promociones.")
    except Exception as e:
        print("Error al obtener precios y promociones:", e)

def reservar_mesa():
    print("\n=== Reservar Mesa ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8002/fondas", headers=headers)
        if response.status_code == 200:
            fondas = response.json().get("fondas", [])
            if not fondas:
                print("No hay fondas disponibles para reservas.")
                return

            print("\nFondas Disponibles:")
            for idx, fonda in enumerate(fondas, start=1):
                print(f"{idx}. {fonda['nombre']} (ID: {fonda['id']})")

            seleccion = int(input("\nSelecciona una fonda por número: "))
            if seleccion < 1 or seleccion > len(fondas):
                print("Selección no válida.")
                return

            id_fonda = fondas[seleccion - 1]["id"]

            response = requests.get(f"{BASE_URL}:8004/reservas/disponibilidad/{id_fonda}", headers=headers)
            if response.status_code == 200:
                disponibilidad = response.json().get("mesas_disponibles", 0)
                if disponibilidad <= 0:
                    print("No hay mesas disponibles en esta fonda.")
                    return

                cantidad_personas = int(input("Indica la cantidad de personas del grupo: "))
                hora_inicio = input("Ingresa la hora de inicio (YYYY-MM-DD HH:MM): ")
                hora_termino = input("Ingresa la hora de término (YYYY-MM-DD HH:MM): ")
                data = {
                    "idFonda": id_fonda,
                    "cantidad_personas": cantidad_personas,
                    "hora_inicio": hora_inicio,
                    "hora_termino": hora_termino
                }
                response = requests.post(f"{BASE_URL}:8004/reservas/crear", json=data, headers=headers)
                if response.status_code == 200:
                    print(f"Reserva creada exitosamente. Mesa asignada: {response.json()['idMesa']}")
                    # Opciones adicionales
                    print("\n¿Deseas pagar la reserva ahora?")
                    opcion_pago = input("Escribe 's' para sí o cualquier otra tecla para volver: ")
                    if opcion_pago.lower() == 's':
                        monto = float(input("Ingresa el monto a pagar: "))
                        metodo_pago = input("Método de pago (debito/credito/efectivo): ")
                        data_pago = {
                            "idReserva": response.json()['idReserva'],
                            "monto": monto,
                            "metodo_pago": metodo_pago
                        }
                        response_pago = requests.post(f"{BASE_URL}:8006/pagos/procesar", json=data_pago, headers=headers)
                        if response_pago.status_code == 200:
                            print(response_pago.json()["mensaje"])
                        else:
                            print("Error al procesar el pago:", response_pago.json().get("detail", "Error desconocido"))
                else:
                    print("Error al realizar la reserva:", response.json().get("detail", "Error desconocido"))
            else:
                print("Error al verificar disponibilidad de mesas:", response.json().get("detail", "Error desconocido"))
        else:
            print("Error al listar fondas:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al reservar mesa:", e)

def mis_opiniones():
    print("\n=== Mis Opiniones ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8003/opiniones/usuario/{USUARIO_ACTUAL}", headers=headers)
        if response.status_code == 200:
            opiniones = response.json().get("opiniones", [])
            if not opiniones:
                print("No has realizado opiniones aún.")
                return
            for idx, opinion in enumerate(opiniones, start=1):
                print(f"\n{idx}. Fonda ID: {opinion['idFonda']}, Calificación: {opinion['calificacion']}/5")
                print(f"Comentario: {opinion['opinion']}")
            # Opciones para editar o eliminar
            print("\n¿Deseas editar o eliminar alguna opinión?")
            opcion = input("Escribe 's' para sí o cualquier otra tecla para volver: ")
            if opcion.lower() == 's':
                seleccion = int(input("Selecciona el número de la opinión: "))
                if seleccion < 1 or seleccion > len(opiniones):
                    print("Selección no válida.")
                    return
                id_opinion = opiniones[seleccion - 1]["idOpinion"]
                print("\nOpciones:")
                print("1. Editar Opinión")
                print("2. Eliminar Opinión")
                accion = input("Selecciona una opción: ")
                if accion == "1":
                    editar_opinion(id_opinion)
                elif accion == "2":
                    eliminar_opinion(id_opinion)
                else:
                    print("Opción no válida.")
        else:
            print("Error al obtener tus opiniones:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener tus opiniones:", e)

def editar_opinion(id_opinion):
    print("\n=== Editar Opinión ===")
    nueva_calificacion = int(input("Nueva Calificación (1-5): "))
    nuevo_comentario = input("Nuevo Comentario: ")
    data = {"calificacion": nueva_calificacion, "opinion": nuevo_comentario}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.put(f"{BASE_URL}:8003/opiniones/{id_opinion}", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al editar la opinión:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al editar la opinión:", e)

def eliminar_opinion(id_opinion):
    print("\n=== Eliminar Opinión ===")
    confirmacion = input("¿Estás seguro de que deseas eliminar esta opinión? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.delete(f"{BASE_URL}:8003/opiniones/{id_opinion}", headers=headers)
            if response.status_code == 200:
                print(response.json()["mensaje"])
            else:
                print("Error al eliminar la opinión:", response.json().get("detail", "Error desconocido"))
        except Exception as e:
            print("Error al eliminar la opinión:", e)
    else:
        print("Operación cancelada.")

# Funciones de operador
def ver_modificar_productos():
    print("\n=== Ver y Modificar Productos de Mi Fonda ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        # Obtener la fonda asociada al operador
        id_fonda = obtener_fonda_operador()
        if id_fonda is None:
            print("No tienes una fonda asignada.")
            return
        response = requests.get(f"{BASE_URL}:8005/productos/fonda/{id_fonda}", headers=headers)
        if response.status_code == 200:
            productos = response.json().get("productos", [])
            if not productos:
                print("No hay productos registrados.")
            else:
                for idx, producto in enumerate(productos, start=1):
                    print(f"{idx}. Producto: {producto['nombre']}, Precio: {producto['precio']}, Stock: {producto['stock']}")
            # Opciones para modificar
            print("\nOpciones:")
            print("1. Añadir Producto")
            print("2. Modificar Producto")
            print("3. Eliminar Producto")
            print("4. Volver")
            opcion = input("Selecciona una opción: ")
            if opcion == "1":
                añadir_producto(id_fonda)
            elif opcion == "2":
                seleccion = int(input("Selecciona el número del producto a modificar: "))
                if seleccion < 1 or seleccion > len(productos):
                    print("Selección no válida.")
                    return
                id_producto = productos[seleccion - 1]["idProducto"]
                modificar_producto(id_producto)
            elif opcion == "3":
                seleccion = int(input("Selecciona el número del producto a eliminar: "))
                if seleccion < 1 or seleccion > len(productos):
                    print("Selección no válida.")
                    return
                id_producto = productos[seleccion - 1]["idProducto"]
                eliminar_producto(id_producto)
            elif opcion == "4":
                return
            else:
                print("Opción no válida.")
        else:
            print("Error al obtener productos:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener productos:", e)

def obtener_fonda_operador():
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8002/fondas/mis_fondas", headers=headers)
        if response.status_code == 200:
            fondas = response.json().get("fondas", [])
            if not fondas:
                return None
            # Asumimos que el operador tiene una sola fonda asignada
            return fondas[0]["idFonda"]
        else:
            print("Error al obtener la fonda del operador.")
            return None
    except Exception as e:
        print("Error al obtener la fonda del operador:", e)
        return None

def añadir_producto(id_fonda):
    print("\n=== Añadir Producto ===")
    nombre = input("Nombre del Producto: ")
    precio = float(input("Precio: "))
    stock = int(input("Stock: "))
    data = {"idFonda": id_fonda, "nombre": nombre, "precio": precio, "stock": stock}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.post(f"{BASE_URL}:8005/productos/crear", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al añadir producto:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al añadir producto:", e)

def modificar_producto(id_producto):
    print("\n=== Modificar Producto ===")
    nombre = input("Nuevo Nombre del Producto: ")
    precio = float(input("Nuevo Precio: "))
    stock = int(input("Nuevo Stock: "))
    es_promocion = input("¿Es promoción? (s/n): ").lower() == 's'
    data = {"nombre": nombre, "precio": precio, "stock": stock, "esPromocion": es_promocion}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.put(f"{BASE_URL}:8005/productos/{id_producto}", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al modificar producto:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al modificar producto:", e)

def eliminar_producto(id_producto):
    print("\n=== Eliminar Producto ===")
    confirmacion = input("¿Estás seguro de que deseas eliminar este producto? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.delete(f"{BASE_URL}:8005/productos/{id_producto}", headers=headers)
            if response.status_code == 200:
                print(response.json()["mensaje"])
            else:
                print("Error al eliminar producto:", response.json().get("detail", "Error desconocido"))
        except Exception as e:
            print("Error al eliminar producto:", e)
    else:
        print("Operación cancelada.")

def ver_opiniones_fonda():
    print("\n=== Ver Opiniones de Mi Fonda ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        id_fonda = obtener_fonda_operador()
        if id_fonda is None:
            print("No tienes una fonda asignada.")
            return
        response = requests.get(f"{BASE_URL}:8003/opiniones/fonda/{id_fonda}", headers=headers)
        if response.status_code == 200:
            opiniones = response.json().get("opiniones", [])
            if not opiniones:
                print("No hay opiniones para tu fonda.")
                return
            for idx, opinion in enumerate(opiniones, start=1):
                print(f"\n{idx}. Usuario: {opinion['usuario']}, Calificación: {opinion['calificacion']}/5")
                print(f"Comentario: {opinion['opinion']}")
                respuesta = opinion.get('respuesta')
                if respuesta:
                    print(f"Respuesta: {respuesta}")
            # Opciones para responder
            print("\n¿Deseas responder alguna opinión?")
            opcion = input("Escribe 's' para sí o cualquier otra tecla para volver: ")
            if opcion.lower() == 's':
                seleccion = int(input("Selecciona el número de la opinión: "))
                if seleccion < 1 or seleccion > len(opiniones):
                    print("Selección no válida.")
                    return
                id_opinion = opiniones[seleccion - 1]["idOpinion"]
                responder_opinion(id_opinion)
        else:
            print("Error al obtener opiniones:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener opiniones:", e)

def responder_opinion(id_opinion):
    print("\n=== Responder Opinión ===")
    respuesta = input("Escribe tu respuesta: ")
    data = {"respuesta": respuesta}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.post(f"{BASE_URL}:8003/opiniones/{id_opinion}/respuesta", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al responder la opinión:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al responder la opinión:", e)

def gestionar_promociones():
    print("\n=== Gestionar Promociones ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        id_fonda = obtener_fonda_operador()
        if id_fonda is None:
            print("No tienes una fonda asignada.")
            return
        response = requests.get(f"{BASE_URL}:8005/productos/fonda/{id_fonda}/promociones", headers=headers)
        if response.status_code == 200:
            promociones = response.json().get("promociones", [])
            if not promociones:
                print("No hay promociones registradas.")
            else:
                for idx, promo in enumerate(promociones, start=1):
                    print(f"{idx}. Producto: {promo['nombre']}, Precio: {promo['precio']}, Stock: {promo['stock']}")
            # Opciones para gestionar
            print("\nOpciones:")
            print("1. Añadir Promoción")
            print("2. Modificar Promoción")
            print("3. Eliminar Promoción")
            print("4. Volver")
            opcion = input("Selecciona una opción: ")
            if opcion == "1":
                añadir_promocion(id_fonda)
            elif opcion == "2":
                seleccion = int(input("Selecciona el número de la promoción a modificar: "))
                if seleccion < 1 or seleccion > len(promociones):
                    print("Selección no válida.")
                    return
                id_promocion = promociones[seleccion - 1]["idProducto"]
                modificar_promocion(id_promocion)
            elif opcion == "3":
                seleccion = int(input("Selecciona el número de la promoción a eliminar: "))
                if seleccion < 1 or seleccion > len(promociones):
                    print("Selección no válida.")
                    return
                id_promocion = promociones[seleccion - 1]["idProducto"]
                eliminar_promocion(id_promocion)
            elif opcion == "4":
                return
            else:
                print("Opción no válida.")
        else:
            print("Error al obtener promociones:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al gestionar promociones:", e)

def añadir_promocion(id_fonda):
    print("\n=== Añadir Promoción ===")
    nombre = input("Nombre de la Promoción: ")
    precio = float(input("Precio: "))
    stock = int(input("Stock: "))
    data = {"idFonda": id_fonda, "nombre": nombre, "precio": precio, "stock": stock, "esPromocion": True}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.post(f"{BASE_URL}:8005/productos/crear", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al añadir promoción:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al añadir promoción:", e)

def modificar_promocion(id_promocion):
    print("\n=== Modificar Promoción ===")
    nombre = input("Nuevo Nombre de la Promoción: ")
    precio = float(input("Nuevo Precio: "))
    stock = int(input("Nuevo Stock: "))
    data = {"nombre": nombre, "precio": precio, "stock": stock, "esPromocion": True}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.put(f"{BASE_URL}:8005/productos/{id_promocion}", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al modificar promoción:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al modificar promoción:", e)

def eliminar_promocion(id_promocion):
    print("\n=== Eliminar Promoción ===")
    confirmacion = input("¿Estás seguro de que deseas eliminar esta promoción? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.delete(f"{BASE_URL}:8005/productos/{id_promocion}", headers=headers)
            if response.status_code == 200:
                print(response.json()["mensaje"])
            else:
                print("Error al eliminar promoción:", response.json().get("detail", "Error desconocido"))
        except Exception as e:
            print("Error al eliminar promoción:", e)
    else:
        print("Operación cancelada.")

def alertas_mesas():
    print("\n=== Alertas de Mesas ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        id_fonda = obtener_fonda_operador()
        if id_fonda is None:
            print("No tienes una fonda asignada.")
            return
        response = requests.get(f"{BASE_URL}:8007/alertas/fonda/{id_fonda}", headers=headers)
        if response.status_code == 200:
            alertas = response.json().get("alertas", [])
            if not alertas:
                print("No hay alertas pendientes.")
                return
            for alerta in alertas:
                print(f"\nID Alerta: {alerta['idAlerta']}, Mesa: {alerta['idMesa']}")
                print(f"Descripción: {alerta['descripcion']}")
                print(f"Fecha: {alerta['fecha']}")
        else:
            print("Error al obtener alertas:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al obtener alertas:", e)

# Funciones de administrador
def crear_fonda():
    print("\n=== Crear Fonda ===")
    nombre = input("Nombre de la Fonda: ")
    descripcion = input("Descripción de la Fonda: ")
    cantidad_mesas = int(input("Cantidad de Mesas: "))

    data = {"nombre": nombre, "descripcion": descripcion, "cantidad_mesas": cantidad_mesas}
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.post(f"{BASE_URL}:8002/fondas/crear", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al crear fonda:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al crear fonda:", e)

def editar_eliminar_fonda():
    print("\n=== Editar o Eliminar Fonda ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8002/fondas", headers=headers)
        if response.status_code != 200:
            print("Error al obtener la lista de fondas:", response.json().get("detail", "Error desconocido"))
            return

        fondas = response.json().get("fondas", [])
        if not fondas:
            print("No hay fondas disponibles para editar o eliminar.")
            return

        print("\nFondas Disponibles:")
        for idx, fonda in enumerate(fondas, start=1):
            print(f"{idx}. ID: {fonda['id']}, Nombre: {fonda['nombre']}, Mesas: {fonda['cantidad_mesas']}")

        seleccion = int(input("\nSelecciona una fonda por número: "))
        if seleccion < 1 or seleccion > len(fondas):
            print("Selección no válida.")
            return

        id_fonda = fondas[seleccion - 1]["id"]

        print("\nOpciones:")
        print("1. Editar Fonda")
        print("2. Eliminar Fonda")
        print("3. Cancelar")
        accion = input("Selecciona una opción: ")

        if accion == "1":
            editar_fonda(id_fonda)
        elif accion == "2":
            eliminar_fonda(id_fonda)
        elif accion == "3":
            print("Operación cancelada.")
        else:
            print("Opción no válida.")
    except Exception as e:
        print("Error al editar o eliminar la fonda:", e)

def editar_fonda(id_fonda):
    print("\n=== Editar Fonda ===")
    nuevo_nombre = input("Nuevo Nombre de la Fonda: ")
    nueva_descripcion = input("Nueva Descripción de la Fonda: ")
    nuevas_mesas = int(input("Nueva Cantidad de Mesas: "))

    data = {
        "nombre": nuevo_nombre,
        "descripcion": nueva_descripcion,
        "cantidad_mesas": nuevas_mesas
    }

    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.put(f"{BASE_URL}:8002/fondas/{id_fonda}", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al editar la fonda:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al editar la fonda:", e)

def eliminar_fonda(id_fonda):
    print("\n=== Eliminar Fonda ===")
    confirmacion = input("¿Estás seguro de que deseas eliminar esta fonda? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.delete(f"{BASE_URL}:8002/fondas/{id_fonda}", headers=headers)
            if response.status_code == 200:
                print(response.json()["mensaje"])
            else:
                print("Error al eliminar la fonda:", response.json().get("detail", "Error desconocido"))
        except Exception as e:
            print("Error al eliminar la fonda:", e)
    else:
        print("Operación cancelada.")

def gestionar_operadores():
    print("\n=== Gestionar Operadores ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        # Obtener lista de fondas
        response_fondas = requests.get(f"{BASE_URL}:8002/fondas", headers=headers)
        if response_fondas.status_code != 200:
            print("Error al obtener la lista de fondas:", response_fondas.json().get("detail", "Error desconocido"))
            return

        fondas = response_fondas.json().get("fondas", [])
        if not fondas:
            print("No hay fondas disponibles.")
            return

        print("\nFondas Disponibles:")
        for idx, fonda in enumerate(fondas, start=1):
            print(f"{idx}. ID: {fonda['id']}, Nombre: {fonda['nombre']}")

        seleccion = int(input("\nSelecciona una fonda por número: "))
        if seleccion < 1 or seleccion > len(fondas):
            print("Selección no válida.")
            return

        id_fonda = fondas[seleccion - 1]["id"]

        # Obtener operadores de la fonda
        response_operadores = requests.get(f"{BASE_URL}:8002/fondas/{id_fonda}/operadores", headers=headers)
        if response_operadores.status_code == 200:
            operadores = response_operadores.json().get("operadores", [])
            print("\nOperadores Asignados:")
            for idx, operador in enumerate(operadores, start=1):
                print(f"{idx}. ID: {operador['idUser']}, Nombre: {operador['nombre']} {operador['apellido']}")
        else:
            print("Error al obtener operadores:", response_operadores.json().get("detail", "Error desconocido"))

        # Opciones para gestionar operadores
        print("\nOpciones:")
        print("1. Asignar Operador")
        print("2. Eliminar Operador")
        print("3. Cancelar")
        opcion = input("Selecciona una opción: ")
        if opcion == "1":
            asignar_operador(id_fonda)
        elif opcion == "2":
            if not operadores:
                print("No hay operadores asignados para eliminar.")
                return
            seleccion_op = int(input("Selecciona el número del operador a eliminar: "))
            if seleccion_op < 1 or seleccion_op > len(operadores):
                print("Selección no válida.")
                return
            id_operador = operadores[seleccion_op - 1]["idUser"]
            eliminar_operador(id_fonda, id_operador)
        elif opcion == "3":
            print("Operación cancelada.")
        else:
            print("Opción no válida.")
    except Exception as e:
        print("Error al gestionar operadores:", e)

def asignar_operador(id_fonda):
    print("\n=== Asignar Operador ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        # Obtener lista de operadores disponibles
        response_usuarios = requests.get(f"{BASE_URL}:8001/usuarios/tipo/2", headers=headers)
        if response_usuarios.status_code != 200:
            print("Error al obtener la lista de operadores:", response_usuarios.json().get("detail", "Error desconocido"))
            return

        operadores = response_usuarios.json().get("usuarios", [])
        if not operadores:
            print("No hay operadores disponibles para asignar.")
            return

        print("\nOperadores Disponibles:")
        for idx, operador in enumerate(operadores, start=1):
            print(f"{idx}. ID: {operador['idUser']}, Nombre: {operador['nombre']} {operador['apellido']}")

        seleccion = int(input("\nSelecciona un operador por número: "))
        if seleccion < 1 or seleccion > len(operadores):
            print("Selección no válida.")
            return

        id_operador = operadores[seleccion - 1]["idUser"]

        data = {"idOperador": id_operador}
        response = requests.post(f"{BASE_URL}:8002/fondas/{id_fonda}/asignar_operador", json=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["mensaje"])
        else:
            print("Error al asignar operador:", response.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al asignar operador:", e)

def eliminar_operador(id_fonda, id_operador):
    print("\n=== Eliminar Operador ===")
    confirmacion = input("¿Estás seguro de que deseas eliminar este operador de la fonda? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.delete(f"{BASE_URL}:8002/fondas/{id_fonda}/operadores/{id_operador}", headers=headers)
            if response.status_code == 200:
                print(response.json()["mensaje"])
            else:
                print("Error al eliminar operador:", response.json().get("detail", "Error desconocido"))
        except Exception as e:
            print("Error al eliminar operador:", e)
    else:
        print("Operación cancelada.")

def ver_reservas():
    print("\n=== Ver Reservas ===")
    try:
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(f"{BASE_URL}:8002/fondas", headers=headers)
        if response.status_code != 200:
            print("Error al obtener la lista de fondas:", response.json().get("detail", "Error desconocido"))
            return

        fondas = response.json().get("fondas", [])
        if not fondas:
            print("No hay fondas disponibles.")
            return

        print("\nFondas Disponibles:")
        for idx, fonda in enumerate(fondas, start=1):
            print(f"{idx}. ID: {fonda['id']}, Nombre: {fonda['nombre']}")

        seleccion = int(input("\nSelecciona una fonda por número para ver sus reservas: "))
        if seleccion < 1 or seleccion > len(fondas):
            print("Selección no válida.")
            return

        id_fonda = fondas[seleccion - 1]["id"]

        response_reservas = requests.get(f"{BASE_URL}:8004/reservas/fonda/{id_fonda}", headers=headers)
        if response_reservas.status_code == 200:
            reservas = response_reservas.json().get("reservas", [])
            if not reservas:
                print("No hay reservas para esta fonda.")
                return
            for reserva in reservas:
                print(f"\nID Reserva: {reserva['idReserva']}, Mesa: {reserva['idMesa']}, Usuario: {reserva['usuario']}")
                print(f"Cantidad de Personas: {reserva['cantidad_personas']}")
                print(f"Hora Inicio: {reserva['hora_inicio']}, Hora Término: {reserva['hora_termino']}")
                print(f"Estado: {reserva['estado']}")
        else:
            print("Error al obtener reservas:", response_reservas.json().get("detail", "Error desconocido"))
    except Exception as e:
        print("Error al ver reservas:", e)

# Punto de entrada principal
if __name__ == "__main__":
    menu_principal()
