import os
import shutil
from subprocess import run
from pathlib import Path

FASM_PATH = "fasm/FASM.exe" # My custom path to FASM, change it.
QEMU_PATH = "C:/Program Files/qemu/" # Default path to installed QEMU dir, if you have another path - change it.

def assemble(src, out):
    result = run([FASM_PATH, src, out])
    if result.returncode != 0:
        raise Exception(f"Assembly failed: {src}")

def build_img():
    Path("build/img").mkdir(parents=True, exist_ok=True)

    assemble("src/boot.asm", "build/boot.bin")
    assemble("src/kernel.asm", "build/kernel.bin")

    with open("build/img/eagleos.img", "wb") as f:
        f.write(open("build/boot.bin", "rb").read())
        f.write(open("build/kernel.bin", "rb").read())
        f.write(b"\x00" * (1474560 - f.tell()))

    print("[+] Done: eagleos.img")

def run_qemu():
    print("[*] Запуск QEMU...")
    result = run([QEMU_PATH+"qemu-system-i386", "-fda", "build/img/eagleos.img", "-no-reboot", "-serial","stdio"])
    if result.returncode != 0:
        print("[!] Ошибка при запуске QEMU")

if __name__ == "__main__":
    
    build_img()
    run_qemu()
