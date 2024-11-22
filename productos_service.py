from fastapi import FastAPI

app = FastAPI()



@app.get("/productos/fonda/{idFonda}/promociones")
def listar_promociones_fonda(idFonda: int):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT idProducto, nombre, precio, stock, esPromocion
            FROM Productos
            WHERE idFonda = ? AND esPromocion = 1
        """, (idFonda,))
        productos = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener promociones: {str(e)}")
    finally:
        conn.close()
    return {"promociones": [dict(producto) for producto in productos]}
