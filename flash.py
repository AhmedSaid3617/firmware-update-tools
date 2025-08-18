import serial
import os

CHUNK_SIZE = 1024  # 1KB
TIMEOUT = 5  # 5 seconds

# Protocol constants
CMD_REQ_TO_SEND  = b"\xA1"
CMD_OK_TO_SEND   = b"\xB1"
CMD_SEND_NEXT = b"\xB2"

class Flasher:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200, timeout=TIMEOUT)

    def flash(self, path):
        filesize = os.path.getsize(path)
        print(f"Flashing {path} of size {filesize} bytes")
        self.ser.write(CMD_REQ_TO_SEND)
        self.ser.write(filesize.to_bytes(4, byteorder='big'))

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