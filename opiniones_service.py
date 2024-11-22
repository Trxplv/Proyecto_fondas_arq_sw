from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel  # Asegúrate de importar BaseModel
import sqlite3
import jwt

app = FastAPI()
# Resto del código...


class OpinionRespuesta(BaseModel):
    respuesta: str

# Endpoint para que el operador responda a una opinión
@app.post("/opiniones/{idOpinion}/respuesta")
def responder_opinion(idOpinion: int, respuesta: OpinionRespuesta, user=Depends(get_current_user)):
    # Solo operadores asignados a la fonda pueden responder
    if user['tipo'] != 2:
        raise HTTPException(status_code=403, detail="No tienes permisos para responder opiniones.")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.idFonda
            FROM Opiniones o
            WHERE o.idOpinion = ?
        """, (idOpinion,))
        opinion = cursor.fetchone()
        if not opinion:
            raise HTTPException(status_code=404, detail="La opinión no existe.")

        # Verificar si el operador está asignado a la fonda
        cursor.execute("""
            SELECT * FROM OperadoresFonda
            WHERE idFonda = ? AND idOperador = ?
        """, (opinion["idFonda"], user['idUser']))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No tienes permisos para responder esta opinión.")

        cursor.execute("""
            UPDATE Opiniones
            SET respuesta = ?
            WHERE idOpinion = ?
        """, (respuesta.respuesta, idOpinion))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al responder la opinión: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Respuesta registrada exitosamente"}

# Al listar opiniones, incluimos la respuesta
@app.get("/opiniones/fonda/{idFonda}")
def listar_opiniones_fonda(idFonda: int):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT o.idOpinion, o.calificacion, o.opinion, o.fecha, o.respuesta, u.nombre || ' ' || u.apellido AS usuario
            FROM Opiniones o
            JOIN Usuarios u ON o.idUser = u.idUser
            WHERE o.idFonda = ?
            ORDER BY o.fecha DESC
        """, (idFonda,))
        opiniones = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener opiniones: {str(e)}")
    finally:
        conn.close()
    return {"opiniones": [dict(opinion) for opinion in opiniones]}

def get_current_user(token: str = Depends(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autenticado")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")