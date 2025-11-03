#!/usr/bin/env python3
"""
Servidor UDP con verificación CRC y simulación de errores.
Materia: Redes de Datos - Universidad de Pilar
Docente: Mariana Gil
Objetivo:
- Recibir mensajes desde un cliente UDP.
- Calcular y verificar el CRC.
- Responder con ACK o NACK según corresponda.
- (Opcional) Simular errores en los datos recibidos.
"""

import socket
import struct
from utils import parse_message, crc16_ccitt

# ===================== CONFIGURACIÓN =====================
HOST = "127.0.0.1"  # Dirección IP local
PORT = 50000  # Puerto de escucha del servidor
ERROR_PROB = 0.2  # Probabilidad de error (20%) - No se usa si se omite simulación
# ==========================================================

# ------------------ CONSTRUCCIÓN DE ACK/NACK ------------------
def build_ack(seq: int) -> bytes:
    """
    Construye respuesta ACK + seq (1 byte).
    """
    return b'ACK' + struct.pack('!B', seq)

def build_nack(seq: int) -> bytes:
    """
    Construye respuesta NACK + seq (1 byte).
    """
    return b'NACK' + struct.pack('!B', seq)

# ------------------ PROGRAMA PRINCIPAL ------------------
def main():
    print(f"[Servidor] Escuchando en {HOST}:{PORT}")
    
    # Crear socket UDP y bind
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    
    # Mantenemos track del seq esperado para evitar duplicados (inicia en 0)
    expected_seq = 0
    
    while True:
        # Recibir datos del cliente
        data, addr = sock.recvfrom(1024)  # Buffer de 1024 bytes
        print(f"[Servidor] Paquete recibido de {addr}: {len(data)} bytes")
        
        try:
            seq, message, crc_recibido = parse_message(data) #Parse extrae la info de data y la devuelve en tres partes
            
            # Verificar si el seq es el esperado (para evitar duplicados)
            if seq != expected_seq:
                print(f"[Servidor] Seq duplicado o inesperado: {seq} (esperado: {expected_seq}). Ignorando.")
                continue 
            
            # Recalcular CRC en tres pasos
            msg_bytes = message.encode('utf-8')
            data_for_crc = struct.pack('!BH', seq, len(msg_bytes)) + msg_bytes
            crc_calculado = crc16_ccitt(data_for_crc)
            
            # Comparar con crc_recibido
            if crc_calculado == crc_recibido:
                print(f"[Servidor] Mensaje válido: '{message}' (seq: {seq})")
                response = build_ack(seq)
                sock.sendto(response, addr)
                # Alternar seq esperado
                expected_seq = 1 - expected_seq
            else:
                print(f"[Servidor] Error en CRC para seq {seq} (calculado: {crc_calculado}, recibido: {crc_recibido})")
                response = build_nack(seq)
                sock.sendto(response, addr)
        except ValueError as e:
            print(f"[Servidor] Paquete inválido: {e}. Enviando NACK.")
            # Si no se puede parsear, envía NACK genérico (seq 255 como error)
            response = build_nack(255)
            sock.sendto(response, addr)

if __name__ == "__main__":
    main()