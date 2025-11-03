#!/usr/bin/env python3
"""
Servidor UDP con verificación CRC y simulación de errores.
Materia: Redes de Datos - Universidad de Pilar
Docente: Mariana Gil
"""

import socket
import random
from utils import crc16_ccitt, parse_message, build_ack, build_nack

HOST = "127.0.0.1"
PORT = 50000
ERROR_PROB = 0.2

def maybe_corrupt(data: bytes, p: float) -> bytes:
    """
    Con cierta probabilidad, altera un bit aleatorio del mensaje.
    """
    if random.random() < p and data:
        pos = random.randint(0, len(data) - 1)
        bit = random.randint(0, 7)
        altered_byte = data[pos] ^ (1 << bit)
        print(f"[Servidor] CORRUPCIÓN SIMULADA: byte {pos}, bit {bit} alterado")
        return data[:pos] + bytes([altered_byte]) + data[pos+1:]
    return data

def main():
    print(f"[Servidor] Escuchando en {HOST}:{PORT}")
    print(f"[Servidor] Probabilidad de corrupción: {ERROR_PROB*100}%")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    expected_seq = 0

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"[Servidor] Paquete recibido de {addr}: {len(data)} bytes")

        # Aplicar corrupción al mensaje recibido
        corrupted_data = maybe_corrupt(data, ERROR_PROB)

        try:
            seq, message, crc_recibido = parse_message(corrupted_data)
            data_for_crc = f"{seq}|{message}".encode('utf-8')
            crc_calculado = crc16_ccitt(data_for_crc)

            if crc_calculado == crc_recibido:
                print(f"[Servidor] Mensaje válido: '{message}' (seq: {seq})")
                print(f"[Servidor] Enviando ACK para seq {seq}")
                sock.sendto(build_ack(seq), addr)
                if seq == expected_seq:
                    expected_seq = 1 - expected_seq
            else:
                print(f"[Servidor] Error CRC (calc={crc_calculado:04X}, recv={crc_recibido:04X})")
                print(f"[Servidor] Enviando NACK para seq {seq}")
                sock.sendto(build_nack(seq), addr)

        except ValueError as e:
            print(f"[Servidor] Paquete inválido: {e}")
            print(f"[Servidor] Enviando NACK para seq 255")
            sock.sendto(build_nack(255), addr)

if __name__ == "__main__":
    main()