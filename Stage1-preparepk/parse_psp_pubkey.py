import sys
import binascii

def get_key_usage_str(usage):
    mapping = {
        0: 'AMD_CODE_SIGN (AMD code sign)',
        1: 'BIOS_CODE_SIGN (BIOS sign)',
        2: 'AMD_AND_BIOS_CODE_SIGN (AMD and BIOS sign)',
        8: 'PLATFORM_SECURE_BOOT (psb)'
    }
    return mapping.get(usage, 'UNKNOWN_KEY_USAGE')

def get_security_features_str(features):
    feature_list = []
    if features & 0b001:
        feature_list.append('DISABLE_BIOS_KEY_ANTI_ROLLBACK')
    if features & 0b010:
        feature_list.append('DISABLE_AMD_BIOS_KEY_USE')
    if features & 0b100:
        feature_list.append('DISABLE_SECURE_DEBUG_UNLOCK')
    return ', '.join(feature_list) if feature_list else 'None'

def parse_pubkey(file_path):
    try:
        with open(file_path, 'rb') as f:

            data = f.read(0x440)
    except FileNotFoundError:
        print(f"err: not found {file_path}")
        return

    if len(data) < 0x440:
        print(f"err: size is not 0x440 bytes ({hex(len(data))})")
        return

    print("=" * 50)
    print(f"parsing AMD PSP 4096-bit file: {file_path}")
    print("=" * 50)

    version = int.from_bytes(data[0x00:0x04], byteorder='little')
    key_id = data[0x04:0x14]
    cert_id = data[0x14:0x24]
    key_usage = int.from_bytes(data[0x24:0x28], byteorder='little')
    sec_features = int.from_bytes(data[0x2A:0x2C], byteorder='little')
    
    pubexp_bits = int.from_bytes(data[0x38:0x3C], byteorder='little')
    modulus_bits = int.from_bytes(data[0x3C:0x40], byteorder='little')

    print("[ Header (0x40 Bytes) ]")
    print(f"  (Version)         : {version}")
    print(f"  (Key ID)       : {binascii.hexlify(key_id).decode('ascii').upper()}")
    print(f"  (Certifying ID): {binascii.hexlify(cert_id).decode('ascii').upper()}")
    print(f"  (Key Usage)   : {key_usage} -> {get_key_usage_str(key_usage)}")
    print(f"  (Sec Features): {hex(sec_features)} -> {get_security_features_str(sec_features)}")
    print(f"  pubexp_bits           : {pubexp_bits} bits")
    print(f"  modulus_bits     : {modulus_bits} bits")
    print("-" * 50)


    pubexp_size = pubexp_bits // 8
    modulus_size = modulus_bits // 8


    if pubexp_size != 512 or modulus_size != 512:
        print("err not 4096-bit")
        return

    pubexp_data = data[0x40 : 0x40 + pubexp_size]
    modulus_data = data[0x40 + pubexp_size : 0x40 + pubexp_size + modulus_size]

    pubexp_val = int.from_bytes(pubexp_data, byteorder='little')
    
    print("[ Crypto Material (0x400 Bytes) ]")

    print(f"  (Pub Exponent): {pubexp_val} ({hex(pubexp_val)})")
    

    modulus_hex = binascii.hexlify(modulus_data).decode('ascii').upper()
    print(f"  (Modulus)         : {modulus_hex[:64]} ... {modulus_hex[-32:]}")
    print("=" * 50)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python parse_psp_pubkey.py <pubkey_file.bin>")
    else:
        parse_pubkey(sys.argv[1])