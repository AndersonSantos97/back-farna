from sqlalchemy import Column, Integer, String, Date, DECIMAL
from .conexion import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(8))
    password = Column(String(200))
    
class Cliente(Base):
    __tablename__ = 'cliente'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    dni = Column(String(15))
    ingreso = Column(Date())
    direccion = Column(String(250))
    fecha_nac = Column(Date())

class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'
    secuencia = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer)
    id_producto = Column(Integer)
    cantidad = Column(Integer)
    precio = Column(DECIMAL(10,2))
    sub_total = Column(DECIMAL(10,2))
    fecha = Column(Date())

class Producto(Base):
    __tablename__ = 'producto'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(250))
    precio = Column(DECIMAL(10,2))
    estate = Column(Integer)
    img = Column(String(500))

class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, primary_key=True, index=True)
    producto = Column(Integer)
    cantidad = Column(Integer)
    fecha = Column(Date())

class Venta(Base):
    __tablename__ = 'venta'
    id = Column(Integer, primary_key=True, index=True)
    dni_cliente	= Column(String(15))
    total = Column(DECIMAL(10,2))
    fecha = Column(Date())