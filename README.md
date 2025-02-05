# EXR Compressor

This is a Python script that recursively finds and compresses OpenEXR (`.exr`) files in a specified directory, optionally truncating 32-bit pixel data to 16 bit half precision floats, as well as optionally stripping unnecessary alpha channels, with support for blacklisting directories.

## Prerequisites

- **Python**: Tested on Python 3.11. Any Python >=3.7 may work.
- **Libraries**: requires the `OpenEXR` and `numpy` libraries. You can install them using pip:
  ```
  pip install OpenEXR numpy
  ```

## Usage

### Basic Command

```
python process_exr_files.py /path/to/input_directory --compression-type DWAA
```

### Arguments
- `--compression-type <TYPE>`: Set the compression type. If the argument isn't passed, it will use whatever compression the file already has, and just try to strip alpha channels. Supported types are:

  -`NONE`
  
  -`RLE`

  -`ZIPS`

  -`ZIP`

  -`PIZ`

  -`PXR24`

  -`B44`

  -`B44A`

  -`DWAA`

  -`DWAB`

### Optional Arguments
- `--blacklist-directory`: Path to a file of newline-delimited paths to exclude from being processed.
- `--no-check-alpha`: Do not check for meaningful alpha channels in EXR files.
- `--no-half-float`: Do not cast 32-bit data to 16 bit half float.

### Compression
If you want lossless compression, you probably want to use either `ZIP` or `PIZ`, as they're usually the smallest lossless options. If you don't mind lossy compression, `DWAA` or `DWAB` might be your best bets, as they're small, fast, and usually essentially perceptually lossless.

[See here](https://en.wikipedia.org/wiki/OpenEXR#Compression_methods) for more information on OpenEXR supported compression types.

If your files are already compressed using a lossy compression method, you should be careful using this program on them. The program will overwrite the images in place, and with lossy options this will further degrade the image every time.

### Truncation

By default the script will convert 32-bit floats to 16 bit, unless the ```--no-half-float``` argument is passed. 16 bit is much more efficient to store than 32-bit, and is usually fine for normal image data, but be careful- some uses (e.g. cryptomattes) require 32 bit precision. **If your data needs to be in 32-bit precision, you should think very carefully about how and whether you really want to use this script on those files. If it needs 32-bit precision, it likely can't be used with lossy compression of any kind.**

### Examples

1. **Compress EXR files in `/input` with DWAA**
   ```
   python process_exr_files.py /input --compression-type DWAA
   ```

2. **Ignore files listed in `/blacklist`:**
   ```
   python process_exr_files.py /input --compression-type DWAA --blacklist-directory /blacklist.txt
   ```
   
3. **Do not try to strip alpha channels:**
   ```
   python process_exr_files.py /input --compression-type DWAA --no-check-alpha
   ```
   
4. **Just strip superfluous alpha channels, not changing the compression type:**
   ```
   python process_exr_files.py /input --no-check-alpha
   ```
   
5. **Don't try to truncate 32-bit pixel data to float16:**
   ```
   python process_exr_files.py /input --compression-type DWAA --no-half-float
   ```
   
6. **Combine multiple options:**
   ```
   python process_exr_files.py /input --compression-type DWAA --blacklist-directory /blacklist.txt --no-check-alpha
   ```
