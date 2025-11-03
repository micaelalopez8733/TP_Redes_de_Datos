#!/usr/bin/env python3
"""
Módulo de utilidades compartidas para cálculo de CRC, construcción y parsing de mensajes.
"""

import struct

CRC_POLY = 0x1021


# client.py usa es funcion para generar el CRC y server.py para recalcular el CRC
def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC-16-CCITT bit a bit.
    """
    crc = 0xFFFF  
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC_POLY
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


#El cliente la usa para empaquetar el mensaje antes de enviarlo. Solo tenes que pasarle el numero de secuencia y el mensaje.
#message lo podes capturar con un escaner

def build_message(seq: int, message: str) -> bytes:
    """
    Construye el paquete: seq (1 byte) | len(msg) (2 bytes) | msg (bytes) | crc (2 bytes).
    Calcula CRC sobre (seq + len + msg).
    """
    if seq not in (0, 1):
        raise ValueError("Seq debe ser 0 o 1")
    msg_bytes = message.encode('utf-8')
    len_msg = len(msg_bytes)
    if len_msg > 65535:
        raise ValueError("Mensaje demasiado largo")
    
    # Datos para CRC: seq + len + msg
    data_for_crc = struct.pack('!BH', seq, len_msg) + msg_bytes
    crc = crc16_ccitt(data_for_crc)
    
    # Paquete completo
    return struct.pack('!BH', seq, len_msg) + msg_bytes + struct.pack('!H', crc)


#Desempaqueta los datos binarios recibidos en tres partes:

    # seq (número de secuencia)

    # message (el texto original en string)

    # crc_recibido (el valor CRC adjuntado por el cliente)

def parse_message(data: bytes) -> tuple[int, str, int]:
    """
    Parsea el paquete: extrae seq, mensaje y CRC recibido.
    Retorna (seq, message, crc_recibido)
    """
    if len(data) < 5:
        raise ValueError("Paquete inválido: demasiado corto")
    
    seq, len_msg = struct.unpack('!BH', data[:3])
    if seq not in (0, 1):
        raise ValueError("Seq inválido")
    if len(data) != 3 + len_msg + 2:
        raise ValueError("Longitud inconsistente")
    
    msg_bytes = data[3:3+len_msg]
    crc_recibido = struct.unpack('!H', data[-2:])[0]
    
    return seq, msg_bytes.decode('utf-8'), crc_recibido
