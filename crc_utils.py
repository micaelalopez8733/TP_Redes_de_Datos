def crc16_ccitt(data: bytes) -> int:
    """
    Calcula el CRC16-CCITT del mensaje
    Polinomio: 0x1021 (x^16 + x^12 + x^5 + 1)
    Valor inicial: 0xFFFF
    """
    crc = 0xFFFF
    polynomial = 0x1021
    
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFFFF
    
    return crc