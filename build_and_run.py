from __future__ import annotations

import argparse
import math
import os 
import shutil
import subprocess
import sys
from pathlib import Path 

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
FLOPPY_BYTES = 1_474_560
SECTOR_SIZE = 512
MAX_KERNEL_BYTES = 0xDC00

def find_executable(name: str, env_name: str, extra_dirs: list[Path] | None = None) -> str:
    configured = os.environ.get(env_name)
    candidates: list[Path] = []

    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.is_file():
            return str(configured_path.resolve())
        candidates.append(configured_path / (name + ".exe"))
        candidates.append(configured_path / name)

    for directory in extra_dirs or []:
        candidates.extend((directory / (name + ".exe"), directory / name))

    found = shutil.which(name) or shutil.which(name + ".exe")
    if found:
        return found

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())

    raise FileNotFoundError(
        f"Cannot find {name}. Set {env_name} to the executable path, "
        "add it to PATH, or install the required tool."
    )


def watcom_dirs() -> list[Path]:
    dirs: list[Path] = []
    watcom = os.environ.get("WATCOM")
    if watcom:
        base = Path(watcom)
        dirs.extend((base / "binnt64", base / "binnt", base / "binw"))

    for base in (Path("C:/WATCOM"), Path("C:/watcom"), Path("C:/Program Files/Open Watcom V2")):
        dirs.extend((base / "binnt64", base / "binnt", base / "binw"))

    return dirs


def run_tool(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", subprocess.list2cmdline(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EagleOS and optionally launch it in QEMU.")
    parser.add_argument("--no-run", action="store_true", help="build the floppy image without launching QEMU")
    parser.add_argument("--clean", action="store_true", help="remove generated build files before building")
    args = parser.parse_args()

    if args.clean and BUILD.exists(): shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True, exist_ok=True)

    wdirs = watcom_dirs()
    fasm = find_executable("fasm", "FASM_EXE", [ROOT / "tools" / "fasm"])
    wcc = find_executable("wcc", "WCC_EXE", wdirs)
    wasm = find_executable("wasm", "WASM_EXE", wdirs)
    wlink = find_executable("wlink", "WLINK_EXE", wdirs)

    # Compile C for 8086, 16-bit small model.
    run_tool([wcc, "-0", "-ms", "-s", "-zl",f"-fo={BUILD / 'main.obj'}",str(ROOT / "src" / "kernel" / "main.c"),])

    run_tool([wasm, "-0", "-mt",f"-fo={BUILD / 'entry.obj'}",str(ROOT / "src" / "kernel" / "entry.asm"),])
    linker_script = BUILD / "kernel.lnk"
    linker_script.write_text(
        "format dos com\n"
        "option start=_cs_\n"
        "option nodefaultlibs\n"
        "option map=build\\kernel.map\n"
        "name build\\kernel.com\n"
        "file build\\entry.obj, build\\main.obj\n",
        encoding="ascii",
    )
    run_tool([wlink, "@build\\kernel.lnk"])

    kernel_path = BUILD / "kernel.com"
    if not kernel_path.is_file():
        raise FileNotFoundError("WLINK completed but build/kernel.com was not created.")

    kernel = kernel_path.read_bytes()
    if not kernel:
        raise RuntimeError("The linked kernel is empty.")
    if len(kernel) > MAX_KERNEL_BYTES:
        raise RuntimeError(
            f"Kernel is {len(kernel)} bytes; maximum for this starter is "
            f"{MAX_KERNEL_BYTES} bytes so the 16-bit stack has room."
        )

    sectors = math.ceil(len(kernel) / SECTOR_SIZE)
    if sectors > (80 * 2 * 18 - 1):
        raise RuntimeError("Kernel exceeds the capacity of a 1.44 MB floppy image.")

    (BUILD / "kernel_size.inc").write_text(f"KERNEL_SECTORS = {sectors}\n", encoding="ascii")

    boot_bin = BUILD / "boot.bin"
    run_tool([fasm,str(ROOT / "src"/"boot" / "boot.asm"),str(boot_bin),])

    boot = boot_bin.read_bytes()
    if len(boot) != SECTOR_SIZE:
        raise RuntimeError(f"Boot sector must be exactly 512 bytes; got {len(boot)}.")
    if boot[510:512] != b"\x55\xAA":
        raise RuntimeError("Boot sector is missing the 55 AA boot signature.")

    image = bytearray(FLOPPY_BYTES)
    image[0:SECTOR_SIZE] = boot
    image[SECTOR_SIZE:SECTOR_SIZE + len(kernel)] = kernel
    image_path = BUILD / "eagleos.img"
    image_path.write_bytes(image)

    print(f"\nBuild successful: {image_path}")
    print(f"Kernel: {len(kernel)} bytes ({sectors} sectors), loaded at 0800:0100")

    if args.no_run:
        return 0

    qemu = find_executable("qemu-system-i386", "QEMU_EXE", [Path("C:/Program Files/qemu"), Path("C:/Program Files/QEMU")])

    run_tool([qemu,"-machine", "pc","-m", "16M","-drive", f"file={image_path},format=raw,if=floppy","-boot", "a",])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"\nBUILD ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
