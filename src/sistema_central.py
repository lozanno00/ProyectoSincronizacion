import threading
import time
import random
from math import inf 

from .constantes import RADIO_BUSQUEDA_KM, COMISION_EMPRESA
from .calculos import calcular_distancia, desempatar_por_calificacion

# -----------------------------------------------------------
# I. RECURSOS CRÍTICOS Y SEMÁFOROS (Variables Globales)
# -----------------------------------------------------------

HILOS_ACTIVADOS = True 

DB_TAXIS = {} 
DB_CLIENTES = {} 

COLA_SOLICITUDES = [] 
COLA_REPORTES_CALIDAD = [] 

CONTADOR_INGRESOS_EMPRESA = 0.0
CONTADOR_SOLICITUDES_ATENDIDAS = 0

SEMAFORO_TAXIS = threading.Lock() 
SEMAFORO_CLIENTES = threading.Lock() 
SEMAFORO_COLAS = threading.Lock() 
SEMAFORO_SOLICITUDES_CONTADOR = threading.Lock() 

# -----------------------------------------------------------
# II. PROCESOS CONCURRENTES (Gestión y Hilos)
# -----------------------------------------------------------

class SistemaCentral(threading.Thread):
    """
    Gestiona el sistema (match, contabilidad, seguimiento) como un hilo independiente.
    """
    def __init__(self):
        super().__init__()
        self.hora_cierre_contable = 12 

    def run(self):
        print(f"[SC] Sistema Central iniciado.")
        while HILOS_ACTIVADOS:
            self.procesar_solicitudes()
            time.sleep(1) 
            self.procesar_reportes_calidad()
        print("[SC] Sistema Central finalizado.")

    def procesar_solicitudes(self):
        """
        Intenta emparejar las solicitudes en la COLA_SOLICITUDES con taxis disponibles.
        """
        solicitudes_a_procesar = []
        
        with SEMAFORO_COLAS:
            if not COLA_SOLICITUDES:
                return
            solicitudes_a_procesar = COLA_SOLICITUDES.copy()
            COLA_SOLICITUDES.clear()

        for solicitud in solicitudes_a_procesar:
            mejor_taxi_id = None
            mejor_distancia = inf

            with SEMAFORO_TAXIS:
                taxis_disponibles = [t for t in DB_TAXIS.values() if t.estado == "DISPONIBLE"]

                if not taxis_disponibles:
                    with SEMAFORO_COLAS:
                        COLA_SOLICITUDES.append(solicitud)
                    continue

                for taxi in taxis_disponibles:
                    distancia = calcular_distancia(
                        taxi.ubicacion_actual_x, taxi.ubicacion_actual_y, 
                        solicitud['origen_x'], solicitud['origen_y']
                    )
                    
                    if distancia < RADIO_BUSQUEDA_KM:
                        if distancia < mejor_distancia:
                            mejor_distancia = distancia
                            mejor_taxi_id = taxi.id
                        elif distancia == mejor_distancia:
                            if desempatar_por_calificacion(DB_TAXIS[mejor_taxi_id], taxi):
                                mejor_taxi_id = taxi.id

            if mejor_taxi_id:
                taxi_asignado = DB_TAXIS[mejor_taxi_id]
                taxi_asignado.asignar_servicio(solicitud)
                print(f"[SC-MATCH] Solicitud {solicitud['cliente_id']} asignada a Taxi {mejor_taxi_id}. Distancia: {mejor_distancia:.2f}km.")

    def procesar_reportes_calidad(self):
        """
        Aplica los reportes de calificación a los taxis.
        """
        reportes_a_procesar = []
        
        with SEMAFORO_COLAS:
            if not COLA_REPORTES_CALIDAD:
                return
            reportes_a_procesar = COLA_REPORTES_CALIDAD.copy()
            COLA_REPORTES_CALIDAD.clear()

        with SEMAFORO_TAXIS:
            for reporte in reportes_a_procesar:
                taxi_id = reporte['taxi_id']
                nueva_calificacion = reporte['calificacion']
                
                if taxi_id in DB_TAXIS:
                    taxi = DB_TAXIS[taxi_id]
                    taxi.calificacion = (taxi.calificacion * 4 + nueva_calificacion) / 5
                    print(f"[SC-CALIDAD] Taxi {taxi_id} calificado con {nueva_calificacion}. Nueva calificación: {taxi.calificacion:.2f}.")

# -----------------------------------------------------------
# III. FUNCIONES DE INTERFAZ
# -----------------------------------------------------------

def afiliar_entidad(entidad, tipo):
    """
    Afiliación segura de taxis o clientes al sistema central.
    """
    if tipo == "TAXI":
        with SEMAFORO_TAXIS:
            if entidad.id not in DB_TAXIS:
                DB_TAXIS[entidad.id] = entidad
                return True
    elif tipo == "CLIENTE":
        with SEMAFORO_CLIENTES:
            if entidad.id not in DB_CLIENTES:
                DB_CLIENTES[entidad.id] = entidad
                return True
    return False

def registrar_solicitud(solicitud):
    """
    Registra una solicitud de viaje en la cola.
    """
    with SEMAFORO_COLAS:
        COLA_SOLICITUDES.append(solicitud)
        print(f"[SC-QUEUE] Nueva solicitud de {solicitud['cliente_id']} registrada.")
        
def registrar_reporte_calidad(reporte):
    """
    Registra un reporte de calificación.
    """
    with SEMAFORO_COLAS:
        COLA_REPORTES_CALIDAD.append(reporte)