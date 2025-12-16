import random
import math
from .constantes import MAX_COORDENADA, COSTO_BASE, COSTO_KM 

def calcular_distancia(x1, y1, x2, y2):
    """Calcula la distancia euclidiana entre dos puntos (en km)."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calcular_costo_viaje(origen_x, origen_y, destino_x, destino_y):
    """Calcula el costo total del viaje."""
    distancia = calcular_distancia(origen_x, origen_y, destino_x, destino_y)
    return COSTO_BASE + (distancia * COSTO_KM)

def generar_coordenada_aleatoria():
    """Genera una tupla de coordenadas dentro del rango máximo."""
    return (random.randint(0, MAX_COORDENADA), random.randint(0, MAX_COORDENADA))

def desempatar_por_calificacion(taxi_candidato_1, taxi_candidato_2):
    """
    Retorna True si el taxi 2 tiene mejor calificación que el taxi 1.
    """
    return taxi_candidato_2.calificacion > taxi_candidato_1.calificacion