import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_psp_keys(pubkey_output="pkmilan_amd.bin", privkey_output="pkmilan_amd_priv.pem"):
    print("gene 4096-bit RSA keypair...")

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    pem_priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(privkey_output, "wb") as f:
        f.write(pem_priv)
    print(f"[+] output: {privkey_output}")

    public_numbers = private_key.public_key().public_numbers()
    exponent = public_numbers.e
    modulus = public_numbers.n

    print("gene AMD PSP pk structure (0x440 bytes)...")
    
    
    header = bytearray(0x40)
    
    
    header[0x00:0x04] = (1).to_bytes(4, byteorder='little')
    
    
    key_id_hex = "94C38E4177D0479292A7AE671D083FB6"
    header[0x04:0x14] = bytes.fromhex(key_id_hex)
    
    
    cert_id_hex = "94C38E4177D0479292A7AE671D083FB6"
    header[0x14:0x24] = bytes.fromhex(cert_id_hex)
    
    #  0x24: Key Usage (0 = AMD_CODE_SIGN) -> 4 Bytes Little Endian
    header[0x24:0x28] = (0).to_bytes(4, byteorder='little')
    
    #  0x2A: Sec Features (0x0) -> 2 Bytes Little Endian
    header[0x2A:0x2C] = (0).to_bytes(2, byteorder='little')
    
    #  0x38:  (4096) -> 4 Bytes Little Endian
    header[0x38:0x3C] = (4096).to_bytes(4, byteorder='little')
    
    #  0x3C:  (4096) -> 4 Bytes Little Endian
    header[0x3C:0x40] = (4096).to_bytes(4, byteorder='little')

    pubexp_bytes = exponent.to_bytes(512, byteorder='little')
    modulus_bytes = modulus.to_bytes(512, byteorder='little')

    psp_pubkey_data = header + pubexp_bytes + modulus_bytes
    
    if len(psp_pubkey_data) != 0x440:
        raise ValueError(f"err: {hex(len(psp_pubkey_data))}")

    with open(pubkey_output, "wb") as f:
        f.write(psp_pubkey_data)
        
    print(f"[+] output: {pubkey_output} (size: {hex(len(psp_pubkey_data))} bytes)")
    print("=" * 50)

if __name__ == '__main__':
    generate_psp_keys("pkmilan_amd.bin", "pkmilan_amd_priv.pem")