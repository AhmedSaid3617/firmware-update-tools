import serial
import os
from crc import Crc32

CHUNK_SIZE = 1024  # 1KB
TIMEOUT = 5  # 5 seconds

CMD_REQ_TO_SEND = b'\xA1'
CMD_SECURITY_ACCESS = b'\xA2'

CMD_OK_TO_SEND = b'\xB1'
CMD_SEND_NEXT = b'\xB2'
CMD_LOADING_ERR = b'\xB3'
CMD_APP_INVALID = b'\xB4'
CMD_UNAUTHORIZED = b'\xB5'
CMD_TIMEOUT = b'\xB6'
CMD_PERMISSION_GRANTED = b'\xB7'

SECRET_KEY = bytearray([0xDE, 0xAD, 0xBE, 0xEF])

class Flasher:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200, timeout=TIMEOUT)

    def flash(self, path):
        filesize = os.path.getsize(path)
        print(f"Flashing {path} of size {filesize} bytes")

        # Send security access command.
        self.ser.write(CMD_SECURITY_ACCESS)

        # Get seed for CRC calculation
        seed = self.ser.read(4)

        # Calculate and send key.
        crc_input = SECRET_KEY[::-1] + bytearray(seed)
        crc = Crc32(0x04C11DB7)
        crc_val = crc.calculate(crc_input)
        print(hex(crc_val))
        self.ser.write(crc_val.to_bytes(4, byteorder='little'))

        # Wait for permission granted
        ack = self.ser.read(1)
        if ack != CMD_PERMISSION_GRANTED:
            raise Exception("Failed to receive PERMISSION_GRANTED from device")

        # Send request to send.
        self.ser.write(CMD_REQ_TO_SEND)
        self.ser.write(filesize.to_bytes(4, byteorder='little'))

        ack = self.ser.read(1)
        if ack != CMD_OK_TO_SEND:
            raise Exception("Failed to receive OK_TO_SEND from device")

        f = open(path, "rb")
        page_num = 0
        while filesize > 0:
            chunk = f.read(CHUNK_SIZE)
            self.ser.write(chunk)
            filesize -= len(chunk)
            print(f"Sent page {page_num} of length {len(chunk)} bytes")

            # If more data is remaining
            if filesize:
                ack = self.ser.read(1)
                if ack != CMD_SEND_NEXT:
                    raise Exception("Failed to receive SEND_NEXT from device")
                page_num += 1

        print("Flashing complete")
        f.close()
        
        

def main():
    flasher = Flasher('/dev/ttyUSB0')
    flasher.flash('out.bin')


if __name__ == "__main__":
    main()