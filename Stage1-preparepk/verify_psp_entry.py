import sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

def load_public_key(pubkey_path):
    try:
        with open(pubkey_path, 'rb') as f:
            data = f.read(0x440)
    except FileNotFoundError:
        print(f"[-] pk not found {pubkey_path}")
        sys.exit(1)

    if len(data) < 0x440:
        print(f"[-] pk size is not 0x440 (cur: {hex(len(data))})")
        sys.exit(1)

    pubexp_bits = int.from_bytes(data[0x38:0x3C], byteorder='little')
    modulus_bits = int.from_bytes(data[0x3C:0x40], byteorder='little')

    pubexp_size = pubexp_bits // 8
    modulus_size = modulus_bits // 8

    pubexp_bytes = data[0x40 : 0x40 + pubexp_size]
    modulus_bytes = data[0x40 + pubexp_size : 0x40 + pubexp_size + modulus_size]

    e = int.from_bytes(pubexp_bytes, byteorder='little')
    n = int.from_bytes(modulus_bytes, byteorder='little')

    public_numbers = rsa.RSAPublicNumbers(e, n)
    return public_numbers.public_key()

def verify_psp_entry(pubkey_path, entry_path):
    print("=" * 60)
    print(f"using: {pubkey_path}")
    print(f"verify: {entry_path}")
    print("=" * 60)

    public_key = load_public_key(pubkey_path)

    try:
        with open(entry_path, 'rb') as f:
            entry_data = f.read()
    except FileNotFoundError:
        print(f"[-] no entry {entry_path}")
        sys.exit(1)

    if len(entry_data) < 0x100:
        print("[-] entry without 0x100 Header")
        sys.exit(1)

    is_encrypted = int.from_bytes(entry_data[0x18:0x1C], byteorder='little') == 1
    is_compressed = int.from_bytes(entry_data[0x48:0x4C], byteorder='little') == 1
    
    if is_encrypted or is_compressed:
        print("[!] enc or compressed")


    size_signed = int.from_bytes(entry_data[0x14:0x18], byteorder='little')

    sig_type = int.from_bytes(entry_data[0x34:0x38], byteorder='little')

    rom_size = int.from_bytes(entry_data[0x6C:0x70], byteorder='little')

    if sig_type == 0x0:
        sig_size = 0x100
        hash_algo = hashes.SHA256()
        salt_len = 32
        print("[+] sig: RSA-2048 (SHA-256)")
    elif sig_type == 0x2:
        sig_size = 0x200
        hash_algo = hashes.SHA384()
        salt_len = 48
        print("[+] sig: RSA-4096 (SHA-384)")
    else:
        print(f"[-] err {hex(sig_type)}")
        sys.exit(1)

    print(f"[+] len: {hex(size_signed)} (total {hex(size_signed + 0x100)})")


    signed_data_len = 0x100 + size_signed
    if signed_data_len > len(entry_data):
        print("[-] no enough len")
        sys.exit(1)
        
    signed_data = entry_data[:signed_data_len]

    if rom_size > 0 and rom_size <= len(entry_data):
        signature = entry_data[rom_size - sig_size : rom_size]
    else:
        signature = entry_data[-sig_size:]

    if len(signature) != sig_size:
        print(f"[-] ({len(signature)})({sig_size})")
        sys.exit(1)

    try:
        public_key.verify(
            signature,
            signed_data,
            padding.PSS(
                mgf=padding.MGF1(hash_algo),
                salt_length=salt_len
            ),
            hash_algo
        )
        print("\n[✓] verify ok")
    except InvalidSignature:
        print("\n[x] verify failed.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: python verify_psp_entry.py <pubkey_file.bin> <entry_file.bin>")
        print("example: python verify_psp_entry.py pkmilan_amd.bin my_entry.bin")
    else:
        verify_psp_entry(sys.argv[1], sys.argv[2])