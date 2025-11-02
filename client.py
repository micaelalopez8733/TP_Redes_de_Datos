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

# ===================== CONFIGURACIÓN =====================
SERVER_HOST = "127.0.0.1"  # IP del servidor
SERVER_PORT = 50000        # Puerto del servidor
TIMEOUT_S = 1.0            # Tiempo máximo de espera (segundos)
MAX_RETRIES = 5            # Cantidad máxima de reintentos
# ==========================================================


# ------------------ FUNCIÓN CRC ------------------
def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC16-CCITT del mensaje a enviar.
    TODO: Implementar el algoritmo bit a bit o con polinomio 0x1021.
    """
    pass


# ------------------ ENVÍO CON RETRANSMISIÓN ------------------
def send_with_retries(sock, server_addr, seq, message):
    """
    Envía un mensaje con número de secuencia 'seq' y retransmite
    si no recibe un ACK en el tiempo establecido.
    TODO: implementar el envío, espera de respuesta y reintentos.
    """
    pass


# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Cliente] Comunicándose con {SERVER_HOST}:{SERVER_PORT}")

    # TODO: crear socket UDP y establecer timeout
    seq = 0  # número de secuencia (0/1)

    while True:
        # TODO: pedir mensaje al usuario
        # TODO: si el mensaje está vacío, terminar
        # TODO: llamar a send_with_retries()
        # TODO: alternar número de secuencia si el envío fue exitoso
        pass


if __name__ == "__main__":
    main()
