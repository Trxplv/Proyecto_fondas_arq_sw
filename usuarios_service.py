from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()
DATABASE = "soa.db"
SECRET_KEY = "tu_secreto_secreto"  # Debes cambiar esto por una clave secreta segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas

# Conexión a la base de datos
def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

# Modelos de datos
class UsuarioRegistro(BaseModel):
    nombre: str
    apellido: str
    tipo: int  # 1: Visitante, 2: Operador, 3: Administrador
    contraseña: str

class UsuarioLogin(BaseModel):
    nombre: str
    contraseña: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para obtener el usuario actual (opcional en este servicio)
def get_current_user(request: Request):
    token = request.headers.get('Authorization')
    if token is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.post("/usuarios/registro")
def registrar_usuario(usuario: UsuarioRegistro):
    """
    Registro de usuarios.
    """
    hashed_password = bcrypt.hashpw(usuario.contraseña.encode('utf-8'), bcrypt.gensalt())
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Usuarios (nombre, apellido, tipo, contraseña)
            VALUES (?, ?, ?, ?)
        """, (usuario.nombre, usuario.apellido, usuario.tipo, hashed_password.decode('utf-8')))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar el usuario: {str(e)}")
    finally:
        conn.close()
    return {"mensaje": "Usuario registrado exitosamente"}

@app.post("/usuarios/login", response_model=Token)
def login(usuario: UsuarioLogin):
    """
    Inicio de sesión de usuarios.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT idUser, contraseña, tipo FROM Usuarios WHERE nombre = ?
    """, (usuario.nombre,))
    usuario_data = cursor.fetchone()
    conn.close()
    if not usuario_data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    stored_hashed_password = usuario_data["contraseña"].encode('utf-8')
    if bcrypt.checkpw(usuario.contraseña.encode('utf-8'), stored_hashed_password):
        # Crear el token JWT
        token_data = {
            "idUser": usuario_data["idUser"],
            "tipo": usuario_data["tipo"],
            "nombre": usuario.nombre
        }
        access_token = create_access_token(data=token_data)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
