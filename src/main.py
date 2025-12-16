import time
import random
import uuid

# --- Importaciones de Entidades y Utilidades (RELATIVAS) ---
from .taxi import Taxi
from .cliente import Cliente
from .constantes import MAX_COORDENADA

# --- Importación y Asignación del Sistema Central (RELATIVA) ---
from . import sistema_central as SC 

SistemaCentral = SC.SistemaCentral
afiliar_entidad = SC.afiliar_entidad
HILOS_ACTIVADOS = SC.HILOS_ACTIVADOS

# --- Parámetros de Simulación ---
NUM_TAXIS = 5
NUM_CLIENTES = 8

def inicializar_y_ejecutar_simulacion():
    """
    Función principal para inicializar y gestionar la ejecución de todos los hilos.
    """
    print("====================================================")
    print(f"  INICIANDO SIMULACIÓN UNIETAXI ({NUM_TAXIS} Taxis, {NUM_CLIENTES} Clientes)")
    print("====================================================")
    
    hilos_activos = []

    # 1. Iniciar el Sistema Central de Atención
    sistema_central_thread = SistemaCentral()
    sistema_central_thread.start()
    hilos_activos.append(sistema_central_thread)
    
    print("\n--- Afiliación de Taxistas ---")
    # 2. Crear y afiliar N Taxis
    for i in range(NUM_TAXIS):
        taxi_id = f"T-{i:02d}"
        x_inicial = random.randint(0, MAX_COORDENADA)
        y_inicial = random.randint(0, MAX_COORDENADA)

        nuevo_taxi = Taxi(
            taxi_id=taxi_id, 
            marca=f"Marca{i}", 
            modelo=f"Modelo{i}", 
            placa=f"PLACA-{i}", 
            x_inicial=x_inicial, 
            y_inicial=y_inicial
        )
        if afiliar_entidad(nuevo_taxi, tipo="TAXI"):
            nuevo_taxi.start()
            hilos_activos.append(nuevo_taxi)

    print("\n--- Afiliación de Clientes ---")
    # 3. Crear y afiliar M Clientes
    for j in range(NUM_CLIENTES):
        cliente_id = f"C-{j:02d}"
        
        nuevo_cliente = Cliente(
            cliente_id=cliente_id, 
            nombre=f"Cliente{j}", 
            tarjeta_credito=str(uuid.uuid4())
        )
        if afiliar_entidad(nuevo_cliente, tipo="CLIENTE"):
            nuevo_cliente.start()
            hilos_activos.append(nuevo_cliente)

    # 4. Monitorear y Esperar (Join)
    SIMULATION_DURATION = 60 # segundos
    print(f"\n[SIMULACION] Ejecutando simulación durante {SIMULATION_DURATION} segundos. Observar la concurrencia...")
    time.sleep(SIMULATION_DURATION) 
    
    # 5. Finalización controlada
    print("\n====================================================")
    print("[SIMULACION] Tiempo de simulación terminado. Finalizando hilos...")
    print("====================================================")

    SC.HILOS_ACTIVADOS = False 
    
    for t in hilos_activos:
        if t.is_alive():
            t.join(timeout=5) 

    print("\n[SIMULACION] Todos los hilos finalizados. Proyecto UNIETAXI completado.")

if __name__ == "__main__":
    inicializar_y_ejecutar_simulacion()