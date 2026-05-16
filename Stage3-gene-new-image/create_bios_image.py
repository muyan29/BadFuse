import os
import logging
import shutil
from typing import Tuple, Optional

# Configure logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_file_bytes(filename: str) -> Tuple[bytes, int]:
    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return b"", 0

    try:
        with open(filename, 'rb') as f:
            content = f.read()
            size = len(content)
            logging.info(f"File read successfully: {filename}, Size: {size} bytes")
            return content, size
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return b"", 0

def replace_file_content(filename: str, search_bytes: bytes, replace_bytes: bytes) -> None:
    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return

    try:
        # 1. Read all content
        with open(filename, 'rb') as f:
            content = f.read()

        # 2. Count occurrences
        count = content.count(search_bytes)
        
        if count == 0:
            logging.info(f"No matching content found in '{filename}', no replacement needed.")
            return

        # 3. Perform replacement
        new_content = content.replace(search_bytes, replace_bytes)

        # 4. Write back to file
        with open(filename, 'wb') as f:
            f.write(new_content)

        logging.info(f"File '{filename}' content replacement completed. Replaced {count} occurrence(s).")

    except Exception as e:
        logging.error(f"Error replacing file content: {e}")

def write_at_offset(filename: str, offset: int, data: bytes, write_size: Optional[int] = None) -> None:
    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return

    try:
        # Determine the actual data to write
        data_to_write = data
        if write_size is not None:
            data_to_write = data[:write_size]
        
        data_len = len(data_to_write)

        with open(filename, 'r+b') as f:
            # Get total file size
            f.seek(0, 2) # Move to end of file
            file_total_size = f.tell()

            # Check if offset is out of bounds
            if offset >= file_total_size:
                logging.warning(f"Offset {offset} exceeds file size {file_total_size}, skipping write.")
                return

            # Core Logic: Ensure overwriting does not increase file size
            # If (offset + data_length) > file_total_size, truncate the data
            if offset + data_len > file_total_size:
                logging.warning("Write data exceeds file end. Truncating data to maintain file size.")
                data_to_write = data_to_write[:file_total_size - offset]
                data_len = len(data_to_write)

            # Move pointer and write
            f.seek(offset)
            f.write(data_to_write)
            
            logging.info(f"Successfully overwrote {data_len} bytes at offset {offset}.")

    except Exception as e:
        logging.error(f"Error writing data: {e}")

def copy_file(src_filename: str, dst_filename: str) -> bool:
    if not os.path.exists(src_filename):
        logging.error(f"Source file not found: {src_filename}")
        return False

    try:
        shutil.copy2(src_filename, dst_filename)
        
        # Verify the file was created
        if os.path.exists(dst_filename):
            src_size = os.path.getsize(src_filename)
            dst_size = os.path.getsize(dst_filename)
            logging.info(f"File copied successfully from '{src_filename}' to '{dst_filename}'. Size: {dst_size} bytes.")
            return True
        else:
            logging.error("Copy operation appeared to finish, but destination file was not found.")
            return False

    except IOError as e:
        logging.error(f"IO Error during file copy: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during file copy: {e}")
        return False

def create_blank_file(filename: str, size: int) -> bool:
    try:
        with open(filename, 'wb') as f:
            if size > 0:
                # Move the file pointer to the last byte
                f.seek(size - 1)
                # Write a single null byte to define the file boundary
                f.write(b'\x00')
            else:
                # Just open and close to create an empty (0 byte) file
                pass
        
        logging.info(f"Blank file created successfully: {filename}, Size: {size} bytes.")
        return True

    except Exception as e:
        logging.error(f"Error creating blank file: {e}")
        return False

if __name__ == "__main__":

    # ensure you have "Milan_bl_1008.bin", "Milan_rec_bl_1001.bin", "8036V206.ROM" in this folder, output: "8036V206_MilanLaunchy.ROM"

    # create a new BIOS image
    copy_file("8036V206.ROM", "8036V206_Badfuse.ROM")

    # replace PSP_FW_BOOT_LOADER 
    cus_bl, _ = read_file_bytes("bl.bin")
    write_at_offset("8036V206_Badfuse.ROM",0x11f6400,cus_bl)

    pk, _ = read_file_bytes("pkmilan_cwindy.bin")
    write_at_offset("8036V206_Badfuse.ROM",0x10a6400,pk)

    