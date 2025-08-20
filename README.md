# STM32 Secure Bootloader Tools

This repository contains **Python utilities** for working with the custom STM32 bootloader that implements **seed-key authentication** and **CRC integrity checking**.

It includes:

* **`patch.py`** – Converts an ELF file into a BIN file and embeds metadata (CRC and size).
* **`flash.py`** – Securely flashes the patched BIN file to the STM32 MCU over UART.

---

## Features

✅ Converts `.elf` → `.bin` using `arm-none-eabi-objcopy`
✅ Patches firmware with:

* CRC32 checksum for integrity validation
* Application size metadata

✅ Secure flashing with:

* Seed-key authentication using CRC-based key calculation
* Chunked transfer protocol with acknowledgments
* Error handling for timeouts and unauthorized access

---

## Requirements

* Python 3.8+
* `pyserial` for UART communication
* `arm-none-eabi-binutils` (for `objcopy`)

Install Python dependencies:

```bash
pip install pyserial
```

---

## Usage

### 1. Patch Firmware

Convert an ELF file to a BIN and patch it with CRC + size metadata:

```bash
python patch.py build/firmware.elf
```

This will generate `out.bin`, the patched binary with CRC and size fields.

---

### 2. Flash Firmware

Send the patched binary (`out.bin`) to the MCU:

```bash
python flash.py
```

By default, the script:

* Connects to `/dev/ttyUSB0` at 115200 baud
* Sends `out.bin` to the bootloader in 1KB chunks
* Authenticates using the seed-key challenge

---

## Protocol Overview

* **Authentication:**

  1. Tool requests security access (`0xA2`)
  2. Device sends a 4-byte seed
  3. Tool computes CRC over seed + secret key and returns the key
  4. If correct, device grants permission (`0xB7`)

* **Flashing:**

  * Tool sends request to send (`0xA1`) + file size
  * Device acknowledges (`0xB1`)
  * Data is transferred in 1KB chunks with `SEND_NEXT` acknowledgments
  * Bootloader validates integrity with the CRC in the header

---

## Example Workflow

```bash
# Step 1: Patch ELF
python patch.py build/firmware.elf

# Step 2: Flash Patched Binary
python flash.py
```

---

## Notes

* Adjust the **serial port** in `flash.py` if not using `/dev/ttyUSB0`.
* The bootloader must already be programmed into the MCU.
* The secret key is hardcoded for demonstration but should be securely managed in production.

---

## License

This project is licensed under the GNU General Public License v2.0. See [LICENSE](LICENSE) for details.
