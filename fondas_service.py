from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import sqlite3
import jwt

app = FastAPI()
DATABASE = "soa.db"
SECRET_KEY = "tu_secreto"
ALGORITHM = "HS256"

# Conexión a la base de datos
def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Modelo de Fonda
class Fonda(BaseModel):
    nombre: str
    descripcion: str
    cantidad_mesas: int

# Modelo para Asociar Operador a Fonda
class OperadorFonda(BaseModel):
    idOperador: int

# Dependencia para obtener el usuario actual
def get_current_user(request: Request):
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.post("/fondas/crear")
def crear_fonda(fonda: Fonda, user=Depends(get_current_user)):
    # Solo administradores pueden crear fondas
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear fondas")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Fondas WHERE nombre = ?", (fonda.nombre,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre de la fonda ya existe.")

        cursor.execute("""
            INSERT INTO Fondas (nombre, descripcion, cantidad_mesas)
            VALUES (?, ?, ?)
        """, (fonda.nombre, fonda.descripcion, fonda.cantidad_mesas))
        id_fonda = cursor.lastrowid

        # Crear mesas asociadas a la fonda
        for numero_mesa in range(1, fonda.cantidad_mesas + 1):
            cursor.execute("""
                INSERT INTO Mesas (idFonda, numero, disponible)
                VALUES (?, ?, 1)
            """, (id_fonda, numero_mesa))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear la fonda: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Fonda creada exitosamente"}

@app.get("/fondas")
def listar_fondas():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        fondas = cursor.execute("""
            SELECT f.idFonda, f.nombre, f.descripcion, f.cantidad_mesas,
            IFNULL(AVG(o.calificacion), 0) as calificacion_promedio
            FROM Fondas f
            LEFT JOIN Opiniones o ON f.idFonda = o.idFonda
            GROUP BY f.idFonda
        """).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar fondas: {str(e)}")
    finally:
        conn.close()
    return {"fondas": [{"id": f["idFonda"], "nombre": f["nombre"], "descripcion": f["descripcion"], "cantidad_mesas": f["cantidad_mesas"], "calificacion_promedio": f["calificacion_promedio"]} for f in fondas]}

@app.put("/fondas/{idFonda}")
def editar_fonda(idFonda: int, fonda: Fonda, user=Depends(get_current_user)):
    # Solo administradores pueden editar fondas
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar esta fonda")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Fondas WHERE idFonda = ?", (idFonda,))
        fonda_db = cursor.fetchone()
        if not fonda_db:
            raise HTTPException(status_code=404, detail="La fonda no existe.")

        # Actualizar los datos de la fonda
        cursor.execute("""
            UPDATE Fondas SET nombre = ?, descripcion = ?, cantidad_mesas = ?
            WHERE idFonda = ?
        """, (fonda.nombre, fonda.descripcion, fonda.cantidad_mesas, idFonda))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al editar la fonda: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Fonda editada exitosamente"}

@app.delete("/fondas/{idFonda}")
def eliminar_fonda(idFonda: int, user=Depends(get_current_user)):
    # Solo administradores pueden eliminar fondas
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta fonda")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Fondas WHERE idFonda = ?", (idFonda,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="La fonda no existe.")

        cursor.execute("DELETE FROM Fondas WHERE idFonda = ?", (idFonda,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar la fonda: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Fonda eliminada exitosamente"}

@app.post("/fondas/{idFonda}/asignar_operador")
def asignar_operador(idFonda: int, operador: OperadorFonda, user=Depends(get_current_user)):
    # Solo administradores pueden asignar operadores a fondas
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para asignar operadores")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Fondas WHERE idFonda = ?", (idFonda,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="La fonda no existe.")

        cursor.execute("SELECT * FROM Usuarios WHERE idUser = ? AND tipo = 2", (operador.idOperador,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El operador no existe.")

        cursor.execute("""
            INSERT INTO OperadoresFonda (idFonda, idOperador)
            VALUES (?, ?)
        """, (idFonda, operador.idOperador))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El operador ya está asignado a esta fonda.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al asignar operador: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Operador asignado exitosamente"}

@app.get("/fondas/{idFonda}/operadores")
def listar_operadores_fonda(idFonda: int, user=Depends(get_current_user)):
    # Solo administradores pueden listar operadores de una fonda
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para listar operadores")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.idUser, u.nombre, u.apellido
            FROM OperadoresFonda of
            JOIN Usuarios u ON of.idOperador = u.idUser
            WHERE of.idFonda = ?
        """, (idFonda,))
        operadores = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar operadores: {str(e)}")
    finally:
        conn.close()
    return {"operadores": [dict(operador) for operador in operadores]}

@app.delete("/fondas/{idFonda}/operadores/{idOperador}")
def eliminar_operador_fonda(idFonda: int, idOperador: int, user=Depends(get_current_user)):
    # Solo administradores pueden eliminar operadores de una fonda
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar operadores")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM OperadoresFonda
            WHERE idFonda = ? AND idOperador = ?
        """, (idFonda, idOperador))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="El operador no está asignado a esta fonda.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar operador: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Operador eliminado exitosamente"}
