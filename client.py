#!/usr/bin/env python3
"""
Cliente UDP con verificación CRC y retransmisión.
Materia: Redes de Datos - Universidad de Pilar
Docente: Mariana Gil
"""

import socket
from utils import crc16_ccitt, build_message, parse_ack_nack

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 50000
TIMEOUT_S = 1.0
MAX_RETRIES = 5


def send_with_retries(sock, server_addr, seq, message):
    """
    Envía mensaje con número de secuencia y CRC calculado.
    Retransmite en caso de error o timeout.
    """
    retries = 0
    data_for_crc = f"{seq}|{message}".encode('utf-8')
    crc = crc16_ccitt(data_for_crc)
    msg_bytes = build_message(seq, message, crc)

    while retries < MAX_RETRIES:
        try:
            print(f"[Cliente] Enviando seq={seq} (intento {retries+1}/{MAX_RETRIES})")
            sock.sendto(msg_bytes, server_addr)

            response, _ = sock.recvfrom(1024)
            is_ack, received_seq = parse_ack_nack(response)

            if received_seq != seq:
                print(f"[Cliente] Seq mismatch: {received_seq} vs {seq}")
                retries += 1
                continue

            if is_ack:
                print(f"[Cliente] ACK recibido para seq {seq}")
                return True
            else:
                print(f"[Cliente] NACK recibido para seq {seq}. Corrupción detectada. Reintentando...")
                retries += 1

        except socket.timeout:
            print("[Cliente] Timeout — reintentando...")
            retries += 1
        except ValueError as e:
            print(f"[Cliente] Error en respuesta: {e}")
            retries += 1

    print("[Cliente] Agotados los reintentos. Fallo en envío.")
    return False

def main():
    print(f"[Cliente] Conectando a {SERVER_HOST}:{SERVER_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_S)
    server_addr = (SERVER_HOST, SERVER_PORT)

    seq = 0

    while True:
        message = input("Mensaje a enviar (vacío para salir) > ")
        if not message:
            print("[Cliente] Cerrando cliente.")
            break

        success = send_with_retries(sock, server_addr, seq, message)
        if success:
            seq = 1 - seq

    sock.close()


if __name__ == "__main__":
    main()