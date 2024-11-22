from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel  # Asegúrate de importar BaseModel
import sqlite3
import jwt

app = FastAPI()
# Resto del código...


@app.post("/reservas/crear")
def crear_reserva(reserva: Reserva, user=Depends(get_current_user)):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Obtener mesas disponibles
        cursor.execute("""
            SELECT idMesa 
            FROM Mesas 
            WHERE idFonda = ? AND disponible = 1
            LIMIT 1
        """, (reserva.idFonda,))
        mesa = cursor.fetchone()

        if not mesa:
            raise HTTPException(status_code=400, detail="No hay mesas disponibles.")

        id_mesa = mesa["idMesa"]

        # Actualizar disponibilidad de la mesa
        cursor.execute("""
            UPDATE Mesas 
            SET disponible = 0 
            WHERE idMesa = ?
        """, (id_mesa,))

        # Crear la reserva
        cursor.execute("""
            INSERT INTO Reservas (idUser, idMesa, cantidad_personas, hora_inicio, hora_termino, estado)
            VALUES (?, ?, ?, ?, ?, 'Pendiente')
        """, (user['idUser'], id_mesa, reserva.cantidad_personas, reserva.hora_inicio.isoformat(), reserva.hora_termino.isoformat()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear la reserva: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Reserva creada exitosamente", "idMesa": id_mesa}

@app.get("/reservas/fonda/{idFonda}")
def listar_reservas_fonda(idFonda: int, user=Depends(get_current_user)):
    # Solo administradores pueden ver todas las reservas
    if user['tipo'] != 3:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver las reservas.")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.idReserva, r.idMesa, r.cantidad_personas, r.hora_inicio, r.hora_termino, r.estado, u.nombre || ' ' || u.apellido AS usuario
            FROM Reservas r
            JOIN Mesas m ON r.idMesa = m.idMesa
            JOIN Usuarios u ON r.idUser = u.idUser
            WHERE m.idFonda = ?
        """, (idFonda,))
        reservas = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reservas: {str(e)}")
    finally:
        conn.close()
    return {"reservas": [dict(reserva) for reserva in reservas]}
