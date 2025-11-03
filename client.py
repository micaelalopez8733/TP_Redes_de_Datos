#!/usr/bin/env python3
"""
Cliente UDP con verificación CRC y retransmisión.
Materia: Redes de Datos - Universidad de Pilar
Docente: Mariana Gil

Objetivo:
- Enviar mensajes al servidor.
- Calcular CRC y adjuntarlo al mensaje.
- Esperar respuesta (ACK/NACK).
- Retransmitir si hay error o timeout.
"""

import socket
import time

from crc_utils import crc16_ccitt

# ===================== CONFIGURACIÓN =====================
SERVER_HOST = "127.0.0.1"  # IP del servidor
SERVER_PORT = 50000        # Puerto del servidor
TIMEOUT_S = 1.0            # Tiempo máximo de espera (segundos)
MAX_RETRIES = 5            # Cantidad máxima de reintentos
# ==========================================================

# ------------------ ENVÍO CON RETRANSMISIÓN ------------------
def send_with_retries(sock, server_addr, seq, message):
    """
    Envía un mensaje con número de secuencia 'seq' y retransmite
    si no recibe un ACK en el tiempo establecido.
    """
    retries = 0
    
    # Este bucle controla los intentos de envío (máximo 5)
    while retries < MAX_RETRIES:
        try:
            # 1. Preparamos el paquete para el envío
            # Usamos la función CRC para calcular el código
            crc_calc = crc16_ccitt(message.encode('utf-8')) 
            
            # Armamos el mensaje completo: Número de Secuencia | Mensaje | Código CRC
            full_msg = f"{seq}|{message}|{crc_calc:04X}"
            
            print(f"[Cliente] Enviando {full_msg} (Intento {retries + 1}/{MAX_RETRIES})")
            sock.sendto(full_msg.encode('utf-8'), server_addr)

            # 2. Esperamos respuesta
            # Acá el código se pausa hasta que el servidor responde (máximo 1 segundo).
            response, _ = sock.recvfrom(1024)
            response_str = response.decode('utf-8')

           # 3. Verificamos la respuesta del Servidor (ACK/NACK)
            if response_str == f"ACK {seq}":
                # Si el servidor responde ACK, el paquete fue entregado correctamente.
                print(f"[Cliente] ACK {seq} recibido. Transferencia OK.")
                return True # Termina la función con éxito

            elif response_str == f"NACK {seq}":
                # Si recibo NACK: Hubo corrupción en la trama, volvemos a intentar.
                print(f"[Cliente] NACK {seq} recibido. Corrupción detectada. Reintentando...")
                retries += 1 # Sumamos un intento fallido

            else:
                # Si la respuesta es inválida, también reintentamos.
                retries += 1
        
        # 4. Si fallamos, manejamos el Timeout
        except socket.timeout:
            # Si el servidor no respondió en 1 segundo (paquete o ACK se perdió).
            print("[Cliente] Timeout. Paquete o ACK perdido. Reintentando...")
            retries += 1 # Sumamos un intento fallido
        
    # Fallo total de retransmisión
    # Si el bucle terminó, es porque llegamos al intento 5 sin éxito.
    print(f"[Cliente] FALLO: Agotados los {MAX_RETRIES} intentos. Deteniendo envío.")
    return False

# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Cliente] Comunicándose con {SERVER_HOST}:{SERVER_PORT}")

    # 1. Creamos el socket UDP y la dirección del servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (SERVER_HOST, SERVER_PORT)
    
    # Establecemos el timeout para detectar la pérdida de ACK/paquete.
    sock.settimeout(TIMEOUT_S) 

    seq = 0 # Iniciamos el número de secuencia alternante (0/1)

    while True:
        # 2. Pedimos el mensaje al usuario
        message = input("Mensaje a enviar (deja vacío para salir) > ") 

        if not message:
            print("[Cliente] Cerrando conexión...")
            break

        # 3. Llamamos a la función de envío con el control de reintentos
        success = send_with_retries(sock, server_addr, seq, message)

        # 4. Alternamos secuencia si el envío fue confirmado por el Servidor (ACK)
        if success:
            seq = 1 - seq # Cambiamos 0 por 1, o 1 por 0.

    sock.close()
    print("[Cliente] Conexión cerrada.")

if __name__ == "__main__":
    main()
