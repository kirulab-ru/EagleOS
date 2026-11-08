<h1 align="center">Eagle OS [DEV]</h1>
<p align="center"><i>My small 16-bit OS, written in FASM (FLAT ASSEMBLER) and C.</i></p>
<p align="center"><b>Warning:</b> Dev branch contain latest and unstable code, don't run it on real hardware.</p>
<h2>How to build and run</h2>

1. Install the required packages:
   - [Open Watcom](https://github.com/open-watcom/open-watcom-v2/releases)
   - [FASM](https://flatassembler.net/)
   - [QEMU](https://www.qemu.org/download/)

2. Clone the repository:

   ```bash
   git clone -b dev https://github.com/kirulab-ru/EagleOS.git
   cd EagleOS
   ```

3. Add Open Watcom to `PATH` and place the FASM folder in `/tools/FASM_FOLDER`.

4. Build and run EagleOS:

   ```bash
   python build_and_run.py
   ```
