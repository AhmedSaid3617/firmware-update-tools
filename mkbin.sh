if [ -z "$1" ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

input_file="$1"
arm-none-eabi-objcopy -O binary $input_file out.bin