import sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(pem_path):
    try:
        with open(pem_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
            )
            return private_key
    except Exception as e:
        print(f"[-] ere load fail -> {e}")
        sys.exit(1)

def resign_psp_entry(privkey_path, entry_path, new_entry_path):
    print("=" * 60)
    print(f"privkey_path    : {privkey_path}")
    print(f"entry_path  : {entry_path}")
    print(f"new_entry_path  : {new_entry_path}")
    print("=" * 60)

    private_key = load_private_key(privkey_path)
    key_size = private_key.key_size
    print(f"[+] load success: {key_size} bits")


    try:
        with open(entry_path, "rb") as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[-] err entry not found {entry_path}")
        sys.exit(1)

    if len(data) < 0x100:
        print("[-] err")
        sys.exit(1)

    is_encrypted = int.from_bytes(data[0x18:0x1C], byteorder='little') == 1
    is_compressed = int.from_bytes(data[0x48:0x4C], byteorder='little') == 1
    if is_encrypted or is_compressed:
        print("[!] err")
        print("-" * 60)

    size_signed = int.from_bytes(data[0x14:0x18], byteorder='little')
    sig_type = int.from_bytes(data[0x34:0x38], byteorder='little')
    rom_size = int.from_bytes(data[0x6C:0x70], byteorder='little')

    if rom_size == 0 or rom_size > len(data):
        rom_size = len(data)

    if sig_type == 0x0:
        sig_size = 0x100
        sign_hash_algo = hashes.SHA256()
        salt_len = 32
        expected_key_size = 2048
        print("[+] RSA-2048 (SHA-256)")
    elif sig_type == 0x2:
        sig_size = 0x200
        sign_hash_algo = hashes.SHA384()
        salt_len = 48
        expected_key_size = 4096
        print("[+] RSA-4096 (SHA-384)")
    else:
        print(f"[-] err {hex(sig_type)}")
        sys.exit(1)

    if key_size != expected_key_size:
        print(f"[-] err")
        sys.exit(1)

    sig_offset = rom_size - sig_size
    print(f"[+] Size Signed: {hex(size_signed)}")
    print(f"[+] (Signature Offset): {hex(sig_offset)}")

    bitfield = int.from_bytes(data[0x58:0x5C], byteorder='big')
    has_sha256 = (bitfield & 0b01) != 0
    has_sha384 = (bitfield & 0b10) != 0

    body_data = data[0x100 : sig_offset]

    if has_sha256:
        print("[+] SHA-256 Checksum...")
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(body_data)
        digest = hasher.finalize()
        data[0xD0 : 0xD0 + 32] = digest
    elif has_sha384:
        print("[+] SHA-384 Checksum...")
        hasher = hashes.Hash(hashes.SHA384())
        hasher.update(body_data)
        digest = hasher.finalize()
        data[0xD0 : 0xD0 + 48] = digest

    signed_data_len = 0x100 + size_signed
    if signed_data_len > len(data):
        print("[-] err")
        sys.exit(1)

    signed_data = data[:signed_data_len]

    print("[+] computing RSA-PSS sig...")
    signature = private_key.sign(
        signed_data,
        padding.PSS(
            mgf=padding.MGF1(sign_hash_algo),
            salt_length=salt_len
        ),
        sign_hash_algo
    )

    if len(signature) != sig_size:
        print(f"[-] err")
        sys.exit(1)

    data[sig_offset : sig_offset + sig_size] = signature

    with open(new_entry_path, "wb") as f:
        f.write(data)

    print(f"\n[✓] success Entry save to: {new_entry_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("usage: python resign_psp_entry.py <privkey.pem> <input_entry.bin> <output_entry.bin>")
        print("example: python resign_psp_entry.py pkmilan_amd_priv.pem old_entry.bin new_entry.bin")
    else:
        resign_psp_entry(sys.argv[1], sys.argv[2], sys.argv[3])