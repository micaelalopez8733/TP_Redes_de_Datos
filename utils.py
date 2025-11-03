#!/usr/bin/env python3
"""
Módulo de utilidades compartidas para cálculo de CRC, construcción y parsing de mensajes.
"""

import struct
from typing import Tuple

CRC_POLY = 0x1021

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


def build_message(seq: int, message: str, crc: int) -> bytes:
    """
    Construye el paquete <seq>|<message>|<crc_hex>
    CRC se pasa como parámetro (ya calculado externamente).
    """
    if seq not in (0, 1):
        raise ValueError("Seq debe ser 0 o 1")
    if not 0 <= crc <= 0xFFFF:
        raise ValueError("CRC fuera de rango")

    crc_hex = f"{crc:04X}"
    full_msg_str = f"{seq}|{message}|{crc_hex}"
    return full_msg_str.encode('utf-8')


def parse_message(data: bytes) -> Tuple[int, str, int]:
    """
    Parsea el paquete <seq>|<message>|<crc_hex> y retorna (seq, message, crc_int)
    """
    try:
        full_str = data.decode('utf-8')
        parts = full_str.split('|')
        if len(parts) != 3:
            raise ValueError("Formato inválido: no exactamente 3 partes")

        seq_str, message, crc_hex = parts
        seq = int(seq_str)
        crc_recibido = int(crc_hex, 16)

        if seq not in (0, 1):
            raise ValueError("Seq inválido")
        if not 0 <= crc_recibido <= 0xFFFF:
            raise ValueError("CRC inválido")

        return seq, message, crc_recibido

    except UnicodeDecodeError:
        raise ValueError("Datos no válidos como UTF-8")


def build_ack(seq: int) -> bytes:
    """Construye respuesta ACK + seq (1 byte)."""
    return b'ACK' + struct.pack('!B', seq)


def build_nack(seq: int) -> bytes:
    """Construye respuesta NACK + seq (1 byte)."""
    return b'NACK' + struct.pack('!B', seq)


def parse_ack_nack(response: bytes) -> Tuple[bool, int]:
    """
    Parsea respuesta ACK/NACK + seq (1 byte).
    Retorna (is_ack, seq)
    """
    if len(response) < 4:
        raise ValueError(f"Respuesta demasiado corta: {len(response)} bytes")
    
    if response.startswith(b'ACK'):
        if len(response) < 4:
            raise ValueError("ACK muy corto")
        seq = struct.unpack('!B', response[3:4])[0]
        return True, seq
    elif response.startswith(b'NACK'):
        if len(response) < 5:
            raise ValueError("NACK muy corto")
        seq = struct.unpack('!B', response[4:5])[0]
        return False, seq
    else:
        raise ValueError(f"Comando inválido: {response[:10]}")