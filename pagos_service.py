from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel  # Asegúrate de importar BaseModel
import sqlite3
import jwt

app = FastAPI()
# Resto del código...


class Pago(BaseModel):
    idReserva: int
    monto: float
    metodo_pago: str  # 'debito', 'credito', 'efectivo'

@app.post("/pagos/procesar")
def procesar_pago(pago: Pago, user=Depends(get_current_user)):
    """
    Simula el procesamiento de un pago.
    """
    # Validar que la reserva pertenece al usuario
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT idUser FROM Reservas WHERE idReserva = ?
        """, (pago.idReserva,))
        reserva = cursor.fetchone()
        if not reserva:
            raise HTTPException(status_code=404, detail="La reserva no existe.")
        if reserva["idUser"] != user['idUser']:
            raise HTTPException(status_code=403, detail="No tienes permiso para pagar esta reserva.")

        # Aquí se simula el procesamiento del pago
        id_pago = str(uuid.uuid4())
        return {
            "mensaje": "Pago procesado exitosamente",
            "idPago": id_pago,
            "estado": "Completado"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el pago: {str(e)}")
    finally:
        conn.close()
