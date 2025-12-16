import threading
import time
import random

# Importación del módulo central simplificada
from . import sistema_central as SC 

# Importaciones auxiliares simplificadas
from .calculos import calcular_distancia, calcular_costo_viaje
from .constantes import TIEMPO_VIAJE_MIN, TIEMPO_VIAJE_MAX, COMISION_EMPRESA

class Taxi(threading.Thread):
    """
    Representa un vehículo y su conductor, ejecutándose como un hilo concurrente.
    """
    def __init__(self, taxi_id, marca, modelo, placa, x_inicial, y_inicial, calificacion_inicial=5.0):
        super().__init__()
        self.id = taxi_id
        self.marca = marca
        self.modelo = modelo
        self.placa = placa
        
        self.ubicacion_actual_x = x_inicial
        self.ubicacion_actual_y = y_inicial
        
        self.estado = "DISPONIBLE" 
        self.calificacion = calificacion_inicial
        self.saldo_acumulado = 0.0 
        self.servicio_asignado = None 
        print(f"Taxi {self.id} afiliado. Ubicación inicial: ({x_inicial}, {y_inicial}).")

    def run(self):
        """Ciclo de vida del taxi."""
        while SC.HILOS_ACTIVADOS:
            if self.estado == "DISPONIBLE":
                time.sleep(random.uniform(0.5, 1.5)) 
                
            elif self.estado == "OCUPADO" and self.servicio_asignado:
                print(f"\n--- Taxi {self.id} asignado a un viaje. Recogiendo cliente... ---")
                
                cliente_id = self.servicio_asignado['cliente_id']
                origen_x = self.servicio_asignado['origen_x']
                origen_y = self.servicio_asignado['origen_y']
                destino_x = self.servicio_asignado['destino_x']
                destino_y = self.servicio_asignado['destino_y']
                
                self.simular_movimiento(origen_x, origen_y, "recoger cliente")
                print(f"Taxi {self.id} recogió al cliente {cliente_id}. Viaje a destino ({destino_x}, {destino_y}).")
                
                costo_viaje = calcular_costo_viaje(origen_x, origen_y, destino_x, destino_y)
                tiempo_viaje = self.simular_movimiento(destino_x, destino_y, "llevar a destino")
                
                self.finalizar_viaje(costo_viaje, cliente_id)
                print(f"--- Taxi {self.id} finaliza viaje. Duración: {tiempo_viaje:.2f}s. Costo: ${costo_viaje:.2f}. ---")
                
                self.servicio_asignado = None
                self.set_estado("DISPONIBLE")
            
            time.sleep(0.1)

    def simular_movimiento(self, target_x, target_y, proposito):
        """Simula el movimiento del taxi a un punto (incluye actualización de ubicación)."""
        
        distancia = calcular_distancia(self.ubicacion_actual_x, self.ubicacion_actual_y, target_x, target_y)
        tiempo_viaje = random.uniform(TIEMPO_VIAJE_MIN, TIEMPO_VIAJE_MAX) * (distancia / 10) 
        
        print(f"Taxi {self.id} moviéndose a ({target_x}, {target_y}) para {proposito}... Tiempo estimado: {tiempo_viaje:.2f}s")
        time.sleep(tiempo_viaje)
        
        with SC.SEMAFORO_TAXIS:
            self.ubicacion_actual_x = target_x
            self.ubicacion_actual_y = target_y

        return tiempo_viaje

    def set_estado(self, nuevo_estado):
        """Método seguro para cambiar el estado del taxi."""
        with SC.SEMAFORO_TAXIS:
            self.estado = nuevo_estado
            
    def finalizar_viaje(self, costo_total, cliente_id):
        """Procesa el pago y actualiza el saldo del taxista y la ganancia de la empresa."""
        
        comision_taxi = costo_total * (1 - COMISION_EMPRESA)
        comision_empresa = costo_total * COMISION_EMPRESA
        
        with SC.SEMAFORO_SOLICITUDES_CONTADOR: 
            self.saldo_acumulado += comision_taxi
            
            SC.CONTADOR_INGRESOS_EMPRESA += comision_empresa
            
            print(f"Pago procesado. Taxi {self.id} gana ${comision_taxi:.2f}. Empresa gana ${comision_empresa:.2f}.")
            
    def asignar_servicio(self, solicitud):
        """Asigna un servicio al taxi, llamado desde el Sistema Central (Match)."""
        if self.estado == "DISPONIBLE":
            self.servicio_asignado = solicitud
            self.set_estado("OCUPADO")
            return True
        return False