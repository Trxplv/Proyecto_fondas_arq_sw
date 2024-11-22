from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel  # Asegúrate de importar BaseModel
import sqlite3
import jwt

app = FastAPI()
# Resto del código...

# Modelo de Alerta
class Alerta(BaseModel):
    idMesa: int
    descripcion: str

@app.post("/alertas/crear")
def crear_alerta(alerta: Alerta, user=Depends(get_current_user)):
    """
    Crear una nueva alerta asociada a una mesa.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Alertas (idMesa, descripcion, estado)
            VALUES (?, ?, 'Pendiente')
        """, (alerta.idMesa, alerta.descripcion))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la alerta: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Alerta creada exitosamente"}

@app.get("/alertas/fonda/{idFonda}")
def listar_alertas_fonda(idFonda: int, user=Depends(get_current_user)):
    # Solo operadores asignados a la fonda pueden ver las alertas
    if user['tipo'] != 2:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver las alertas.")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Verificar si el operador está asignado a la fonda
        cursor.execute("""
            SELECT * FROM OperadoresFonda
            WHERE idFonda = ? AND idOperador = ?
        """, (idFonda, user['idUser']))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No tienes permisos para ver las alertas de esta fonda.")

        cursor.execute("""
            SELECT a.idAlerta, a.idMesa, a.descripcion, a.estado, a.fecha
            FROM Alertas a
            JOIN Mesas m ON a.idMesa = m.idMesa
            WHERE m.idFonda = ? AND a.estado = 'Pendiente'
        """, (idFonda,))
        alertas = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener alertas: {str(e)}")
    finally:
        conn.close()
    return {"alertas": [dict(alerta) for alerta in alertas]}
