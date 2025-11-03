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
import struct 
import time

#Importamos las funciones binarias de nuestro módulo utils.py
from utils import build_message, parse_ack_nack 

# ===================== CONFIGURACIÓN =====================
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 50000
TIMEOUT_S = 1.0       # Tiempo máximo de espera (segundos)
MAX_RETRIES = 5       # Cantidad máxima de reintentos
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
            # Usamos build_message para construir la trama binaria (incluye el CRC).
            full_msg_bytes = build_message(seq, message)
            
            print(f"[Cliente] Enviando mensaje seq={seq} (Intento {retries + 1}/{MAX_RETRIES})")
            sock.sendto(full_msg_bytes, server_addr) # Enviamos los bytes binarios

            # 2. Esperamos respuesta
            response, _ = sock.recvfrom(1024)
            
            # 3. Verificamos la respuesta del servidor (ACK/NACK)
            is_ack, received_seq = parse_ack_nack(response)

            if received_seq != seq:
                # El servidor respondió con una secuencia diferente, lo ignoramos por seguridad.
                print(f"[Cliente] Recibido ACK/NACK para seq {received_seq}, esperado {seq}. Ignorando.")
                continue

            if is_ack:
                # Si el servidor responde ACK, el paquete fue entregado correctamente.
                print(f"[Cliente] ACK {seq} recibido. Transferencia OK.")
                return True # Éxito, salimos del bucle.

            elif not is_ack:
                # Si recibo NACK: Hubo corrupción en la trama, volvemos a intentar.
                print(f"[Cliente] NACK {seq} recibido. Corrupción detectada. Reintentando...")
                retries += 1
            
            else:
                # Si la respuesta es inválida, también reintentamos.
                retries += 1
        
        # 4. Si fallamos, manejamos el Timeout
        except socket.timeout:
            # Si el servidor no respondió en 1 segundo (paquete o ACK se perdió).
            print("[Cliente] Timeout. Paquete o ACK perdido. Reintentando...")
            retries += 1
        except ValueError as e:
            # Capturamos errores graves (formato incorrecto, etc.).
            print(f"[Cliente] Error crítico en el paquete: {e}. Devolviendo envío.")
            return False 
            
    # Fallo total de retransmisión
    # El bucle terminó porque se agotó el máximo de 5 intentos.
    print(f"[Cliente] FALLO: Agotados los {MAX_RETRIES} intentos. Deteniendo envío.")
    return False


# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Cliente] Iniciando comunicación con {SERVER_HOST}:{SERVER_PORT}")

    # 1. Creamos el socket UDP y la dirección donde está el servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (SERVER_HOST, SERVER_PORT)
    
    # Establecemos el timeout, esto nos ayuda a saber cuándo el paquete o el ACK se perdió
    sock.settimeout(TIMEOUT_S) 

    seq = 0  # Iniciamos la secuencia que alternará entre 0 y 1

    while True:
        # 2. Le pedimos al usuario el mensaje para enviar
        message = input("Mensaje a enviar (deja vacío para salir) > ") 

        if not message:
            print("[Cliente] Cerrando conexión...")
            break

        # 3. Mandamos el mensaje y esperamos que se confirme el envío
        success = send_with_retries(sock, server_addr, seq, message)

       # 4. Cambiamos la secuencia si el Servidor nos confirmó el envío
        if success:
            seq = 1 - seq  # Invertimos la secuencia (de 0 a 1, o de 1 a 0).

    sock.close()


if __name__ == "__main__":
    main()
