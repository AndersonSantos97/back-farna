from fastapi import FastAPI, Depends, HTTPException, status
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
import datetime as dt
from . import models, schemas
from .conexion import SessionLocal,engine
from sqlalchemy.orm import Session
import bcrypt
from .schemas import TokenData, ventaCreate, Cliente, ClienteCreate
from .models import Venta, DetalleVenta, Stock, Cliente
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (POST, GET, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

#clave secreta para firmar el token
SECRET_KEY = "Andersonelmas"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #DURACION DEL TOKEN EN MINUTOS


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username = username)
    except JWTError:
        raise credentials_exception
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"www-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token,credentials_exception)
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    
    if user is None:
        raise credentials_exception
    
    return user

def format_string(input_str: str):
    
    if len(input_str) == 13:
        formated_str = f"{input_str[:4]}-{input_str[4:8]}-{input_str[8:]}"
        return formated_str
    else:
        raise ValueError("El parametro no tiene la longitud esperada")
    


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Crear el token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.User(username = user.username, password = hashed_password.decode('utf-8'))
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/findDni/{dniP}", response_model=schemas.Cliente)
async def find_dni(dniP:str, db:Session = Depends(get_db)):
    formated_dni = format_string(dniP)
    print(formated_dni)
    dni = db.query(models.Cliente).filter(models.Cliente.dni == formated_dni).first()
    
    if not dni:
        raise HTTPException(status_code=404, detail=f"Cliento con dni {formated_dni} no encontrado")
    
    return dni

@app.get("/product/{idProd}", response_model = schemas.Producto)
async def find_prod(idProd:int, db: Session = Depends(get_db)):
    
    productId = db.query(models.Producto).filter(models.Producto.id ==idProd).first()
    
    if not productId:
        raise HTTPException(status_code=404, detail=f"Producto con id {idProd} no encontrado")
    
    return productId

@app.get("/productname/{name}", response_model= schemas.Producto)
async def finByName(name: str, db: Session = Depends(get_db)):
    
    producName = db.query(models.Producto).filter(models.Producto.description == name).first()
    
    if not producName:
        raise HTTPException(status_code=404, detail=f"Producto con nombre {producName} no encontrado")

    return producName

@app.post("/ventas/")
def crear_venta(venta: ventaCreate, db: Session = Depends(get_db)):
    try:
        #insertar la venta en la tabla venta
        nueva_venta = Venta(
            dni_cliente = venta.dni_cliente,
            total = venta.total,
            fecha = dt.date.today()
        )
        
        db.add(nueva_venta)
        db.commit()
        db.refresh(nueva_venta)
        
        #insertar los detalles en la tabla detalle_venta
        for detalle in venta.detalle:
            nuevo_datalle = DetalleVenta(
                id_venta = nueva_venta.id,
                id_producto = detalle.id_producto,
                cantidad = detalle.cantidad,
                precio = detalle.precio,
                sub_total = detalle.sub_total,
                fecha = dt.date.today()
            )
            
            db.add(nuevo_datalle)
            
            #actualizar el stock
            producto_stock = db.query(Stock).filter(Stock.producto == detalle.id_producto).first()
            if producto_stock is None:
                raise HTTPException(status_code=404, detail="Producto no encontrado en el stock")
            
            if producto_stock.cantidad < detalle.cantidad:
                raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")
            
            producto_stock.cantidad -= detalle.cantidad
        
        db.commit()#confirmar todas las transacciones
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message" : "Venta creada exitosamente", "venta_id":nueva_venta.id}


@app.post("/client/")
def create_client(client: ClienteCreate, db: Session = Depends(get_db)):
    try:
        new_client = Cliente(
            nombre = client.nombre,
            dni = client.dni,
            ingreso = dt.date.today(),
            direccion = client.direccion,
            fecha_nac = client.fecha_nac
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
           
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message" : "Cliente creado exitosamente", "cliente_id": new_client.id}