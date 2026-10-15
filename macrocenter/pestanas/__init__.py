"""Una pestaña del tablero por archivo. Cada una tiene `mostrar(...)`, que recibe por nombre lo que usa de la página
(datos y funciones de app.py): así se ve de qué depende cada pestaña sin leer el resto (ver `abrir` en app.py)."""
from . import (actividad, bolsas, bonos, comercio, cripto, dinero, dolar, fiscal, historia, inflacion, inicio,
               ministros_economia, reservas, salarios, tasas)

__all__ = ["actividad", "bolsas", "bonos", "comercio", "cripto", "dinero", "dolar", "fiscal", "historia", "inflacion",
           "inicio", "ministros_economia", "reservas", "salarios", "tasas"]
