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
    parser = argparse.ArgumentParser(
        description="Build EagleOS and optionally launch it in QEMU."
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="build the floppy image without launching QEMU"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove generated build files before building"
    )
    args = parser.parse_args()

    if args.clean and BUILD.exists():
        shutil.rmtree(BUILD)

    BUILD.mkdir(parents=True, exist_ok=True)

    # All project paths
    kernel_src = ROOT / "src" / "kernel"
    build_obj = BUILD / "obj"

    build_obj.mkdir(parents=True, exist_ok=True)

    # Find tools
    wdirs = watcom_dirs()

    fasm = find_executable(
        "fasm", "FASM_EXE", [ROOT / "tools" / "fasm"]
    )
    wcc = find_executable("wcc", "WCC_EXE", wdirs)
    wasm = find_executable("wasm", "WASM_EXE", wdirs)
    wlink = find_executable("wlink", "WLINK_EXE", wdirs)

    # Find all C source files recursively
    c_sources = sorted(kernel_src.rglob("*.c"))

    if not c_sources:
        raise FileNotFoundError(
            f"No C source files found in {kernel_src}"
        )

    print(f"\nFound {len(c_sources)} C source files.")

    object_files = []
    watcom_root = Path(
        os.environ.get("WATCOM", r"C:\WATCOM")
    )

    watcom_include = watcom_root / "h"

    if not (watcom_include / "i86.h").is_file():
        raise FileNotFoundError(
            f"Open Watcom header not found: {watcom_include / 'i86.h'}"
        )
    # Compile every C source file
    for source in c_sources:
        relative = source.relative_to(kernel_src)

        # Preserve directory structure to avoid filename collisions
        obj_path = build_obj / relative.with_suffix(".obj")
        obj_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\nCompiling: {relative}")

        run_tool([
            wcc,
            "-0",
            "-ms",
            "-s",
            "-zl",
           f"-i={watcom_include}",
            f"-fo={obj_path}",
            str(source),
        ])

        object_files.append(obj_path)

    # Compile assembly entry point
    entry_asm = kernel_src / "entry.asm"
    entry_obj = BUILD / "entry.obj"

    if not entry_asm.is_file():
        raise FileNotFoundError(f"Missing entry point: {entry_asm}")

    print("\nCompiling kernel entry...")

    run_tool([
        wasm,
        "-0",
        "-mt",
        f"-fo={entry_obj}",
        str(entry_asm),
    ])

    # Generate linker script
    linker_script = BUILD / "kernel.lnk"

    linker_lines = [
        "format dos com",
        "option start=_cs_",
        "option nodefaultlibs",
        "option map=build\\kernel.map",
        "name build\\kernel.com",
        "file build\\entry.obj",
    ]

    for obj in object_files:
        relative_obj = obj.relative_to(ROOT)
        linker_lines.append(f"file {relative_obj}")

    linker_script.write_text(
        "\n".join(linker_lines) + "\n",
        encoding="ascii",
    )

    print("\nLinking kernel...")

    run_tool([
        wlink,
        f"@{linker_script.relative_to(ROOT)}"
    ])

    # Validate kernel output
    kernel_path = BUILD / "kernel.com"

    if not kernel_path.is_file():
        raise FileNotFoundError(
            "WLINK completed but build/kernel.com was not created."
        )

    kernel = kernel_path.read_bytes()

    if not kernel:
        raise RuntimeError("The linked kernel is empty.")

    if len(kernel) > MAX_KERNEL_BYTES:
        raise RuntimeError(
            f"Kernel is {len(kernel)} bytes; maximum for this "
            f"starter is {MAX_KERNEL_BYTES} bytes."
        )

    sectors = math.ceil(len(kernel) / SECTOR_SIZE)

    if sectors > (80 * 2 * 18 - 1):
        raise RuntimeError(
            "Kernel exceeds the capacity of a 1.44 MB floppy image."
        )

    # Generate bootloader sector count include
    (BUILD / "kernel_size.inc").write_text(
        f"KERNEL_SECTORS = {sectors}\n",
        encoding="ascii",
    )

    # Assemble boot sector
    boot_asm = ROOT / "src" / "boot" / "boot.asm"
    boot_bin = BUILD / "boot.bin"

    print("\nAssembling bootloader...")

    run_tool([
        fasm,
        str(boot_asm),
        str(boot_bin),
    ])

    boot = boot_bin.read_bytes()

    if len(boot) != SECTOR_SIZE:
        raise RuntimeError(
            f"Boot sector must be exactly 512 bytes; got {len(boot)}."
        )

    if boot[510:512] != b"\x55\xAA":
        raise RuntimeError(
            "Boot sector is missing the 55 AA boot signature."
        )

    # Create floppy image
    image = bytearray(FLOPPY_BYTES)

    image[0:SECTOR_SIZE] = boot
    image[SECTOR_SIZE:SECTOR_SIZE + len(kernel)] = kernel

    image_path = BUILD / "eagleos.img"
    image_path.write_bytes(image)

    print("\nBuild successful!")
    print(f"Image: {image_path}")
    print(f"Kernel: {len(kernel)} bytes")
    print(f"Sectors: {sectors}")
    print(f"Loaded at: 0800:0100")
    print(f"C modules: {len(c_sources)}")

    if args.no_run:
        return 0

    # Launch QEMU
    qemu = find_executable(
        "qemu-system-i386",
        "QEMU_EXE",
        [
            Path("C:/Program Files/qemu"),
            Path("C:/Program Files/QEMU"),
        ],
    )

    run_tool([
        qemu,
        "-machine", "pc",
        "-m", "16M",
        "-drive", f"file={image_path},format=raw,if=floppy",
        "-boot", "a",
    ])

    return 0



if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"\nBUILD ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
