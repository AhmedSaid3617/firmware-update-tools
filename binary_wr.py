import sys
import subprocess
from pathlib import Path
import os

HEADER_SIZE = 512

# CRC32 class
class Crc32:
    crc_table = {}

    def __init__(self, _poly):
        # Generate CRC table for polynomial
        for i in range(256):
            c = i << 24
            for j in range(8):
                c = (c << 1) ^ _poly if (c & 0x80000000) else c << 1
            self.crc_table[i] = c & 0xFFFFFFFF

    # Calculate CRC from input buffer
    def calculate(self, buf):
        crc = 0xFFFFFFFF

        i = 0
        while i < len(buf):
            b = [buf[i+3], buf[i+2], buf[i+1], buf[i+0]]
            i += 4
            for byte in b:
                crc = ((crc << 8) & 0xFFFFFFFF) ^ self.crc_table[(crc >> 24) ^ byte]
        return crc
    
    # Create bytes array from integer input
    def crc_int_to_bytes(self, i):
        return [(i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF]
    

def elf_to_bin(elf_path: Path) -> Path:
    """Convert ELF to BIN using objcopy and return bin path."""
    bin_path = elf_path.with_suffix(".bin")
    # Run objcopy (requires arm-none-eabi-binutils installed)
    subprocess.run(
        ["arm-none-eabi-objcopy", "-O", "binary", str(elf_path), str(bin_path)],
        check=True
    )
    return bin_path


def patch_bin(bin_path: Path, out_path: Path):
    """Read a binary, patch it, and save to new file."""
    
    with open(bin_path, "rb") as f:
        #f.seek(512)
        data = bytearray(f.read())
    
    crc = Crc32(0x04C11DB7)
    crc_val = crc.calculate(data[HEADER_SIZE:])

    print(hex(crc_val))
    data[0:4] = crc_val.to_bytes(4, "little")  # Patch CRC into the binary
    data[4:8] = os.path.getsize(bin_path).to_bytes(4, "little") # Patch app size into the binary

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"Patched binary saved to: {out_path}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <firmware.elf>")
        sys.exit(1)

    elf_path = Path(sys.argv[1])
    if not elf_path.exists():
        print(f"Error: ELF file {elf_path} not found.")
        sys.exit(1)

    # Convert ELF → BIN
    bin_path = elf_to_bin(elf_path)

    # Output patched file
    out_path = bin_path.with_name(Path.cwd().stem + "_patched.bin")
    out_path = Path("./out.bin")
    patch_bin(bin_path, out_path)

if __name__ == "__main__":
    main()
