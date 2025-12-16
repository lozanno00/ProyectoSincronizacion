import threading
import time
import random

# Importaciones simplificadas (asume que los archivos están en la misma carpeta)
from .constantes import MAX_COORDENADA
from .calculos import generar_coordenada_aleatoria

# Importamos los recursos críticos del módulo central como SC para robustez
from . import sistema_central as SC 

class Cliente(threading.Thread):
    """
    Representa un cliente que solicita viajes al sistema.
    """
    def __init__(self, cliente_id, nombre, tarjeta_credito):
        super().__init__()
        self.id = cliente_id
        self.nombre = nombre
        self.tarjeta_credito = tarjeta_credito
        self.servicios_realizados = 0
        print(f"Cliente {self.id} afiliado.")

    def run(self):
        """Ciclo de vida del cliente: solicita viajes aleatoriamente."""
        while SC.HILOS_ACTIVADOS:
            time.sleep(random.uniform(5, 15)) 

            self.solicitar_viaje()
            self.servicios_realizados += 1

            time.sleep(random.uniform(20, 40)) 
            
            self.registrar_calificacion_simulada()
            
    def solicitar_viaje(self):
        """
        Crea un payload de solicitud de viaje y lo envía al sistema central.
        """
        origen_x, origen_y = generar_coordenada_aleatoria()
        destino_x, destino_y = generar_coordenada_aleatoria()
        
        solicitud = {
            'cliente_id': self.id,
            'origen_x': origen_x,
            'origen_y': origen_y,
            'destino_x': destino_x,
            'destino_y': destino_y
        }
        
        SC.registrar_solicitud(solicitud)
        print(f"Cliente {self.id} solicitó viaje de ({origen_x}, {origen_y}) a ({destino_x}, {destino_y}).")

    def registrar_calificacion_simulada(self):
        """
        Simula la calificación del último viaje y la registra.
        """
        calificacion = random.randint(1, 5)
        
        taxi_ids = list(SC.DB_TAXIS.keys())
        if not taxi_ids:
            return 

        taxi_a_calificar = random.choice(taxi_ids)
        
        reporte = {
            'cliente_id': self.id,
            'taxi_id': taxi_a_calificar,
            'calificacion': calificacion
        }
        
        SC.registrar_reporte_calidad(reporte)
        print(f"Cliente {self.id} calificó al Taxi {taxi_a_calificar} con {calificacion} estrellas.")