from datetime import date
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    password: str
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str
    
    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None
    

class Cliente(BaseModel):
    id: int
    nombre: str
    dni: str
    ingreso: date
    direccion: str
    fecha_nac: date
    
    class Config:
        orm_mode = True

class ClienteCreate(BaseModel):
    nombre: str
    dni: str
    ingreso: date
    direccion: str
    fecha_nac: date

    class Config:
        orm_mode = True

class DetalleVenta(BaseModel):
    secuencia: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio: float
    sub_total: float
    fecha: date
    
    class Config:
        orm_mode = True

class Producto(BaseModel):
    id: int
    description: str
    precio: float
    estate: int
    img: str
    
    class Config:
        orm_mode = True

class Stock(BaseModel):
    id: int
    producto: int
    cantidad: int
    fecha: date
        
    class Config:
        orm_mode = True

class Venta(BaseModel):

    id: int
    dni_cliente: str
    total: float
    fecha: float
    
    class Config:
        orm_mode = True
        

class DetalleVentaCreate(BaseModel):
    id_producto: int
    cantidad: int 
    precio: float
    sub_total: float
    
    class config:
        orm_mode = True

class ventaCreate(BaseModel):
    dni_cliente: str
    total: float
    detalle: list[DetalleVentaCreate]
    
    class config:
        orm_mode = True