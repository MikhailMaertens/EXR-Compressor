from pathlib import Path
import OpenEXR as exr
import numpy as np


def has_meaningful_alpha(alpha_channel):
    """Check if the alpha channel contains meaningful data."""
    # If all values are 1 (fully opaque) or 0 (fully transparent), it's not meaningful
    unique_values = np.unique(alpha_channel)
    return len(unique_values) > 2 or (len(unique_values) == 2 and (unique_values[0] != 0 and unique_values[1] != 1))


def process_exr_files(input_dir, compression_type, blacklist, check_alpha, trunc_half_float):
    """Go through a given set of files and compress them"""
    excluded_paths = []
    print(f"Compressing in {input_dir}")
    if blacklist is not None:
        with open (blacklist) as blist:
            excluded_paths = [line.strip() for line in blist]
            print("Loaded", len(excluded_paths), "blacklisted paths.")
    print("Continue? (Y\\N)")
    if input().lower() != 'y':
        print("Not confirmed. Quitting execution.")
        quit()

    input_path = Path(input_dir)

    for file in input_path.glob('**/*.exr'):
        # Check if any part of the file's path is in the excluded paths
        is_excluded = any(excluded_path in str(file.resolve()) for excluded_path in excluded_paths)
        if is_excluded:
            print(f"Skipping {file.name} for compression (reason: blacklist)")
            continue
        else:
            modified = False
            print(f"Processing file {file}")
            infile = exr.File(str(file), separate_channels = True)
            header = infile.header()
            # Read channels
            channels = infile.channels()
            if check_alpha:
                if 'A' in channels: # Check for alpha channel
                    alpha_channel = channels['A'].pixels
                    if not has_meaningful_alpha(alpha_channel):
                        print(f"Removing meaningless alpha from {file.name}")
                        modified = True
                        del channels['A']
                    else:
                        print(f"Alpha channel may contain meaningful data, skipping")
                else:
                    print(f"No alpha channel found in {file.name}")
            # Create new header
            new_header = header

            # Create new channels
            new_channels = channels

            if compression_type is not None:
                compression_settings = {
                    "NONE": exr.NO_COMPRESSION,
                    "RLE": exr.RLE_COMPRESSION,
                    "ZIPS": exr.ZIPS_COMPRESSION,
                    "ZIP": exr.ZIP_COMPRESSION,
                    "PIZ": exr.PIZ_COMPRESSION,
                    "PXR24": exr.PXR24_COMPRESSION,
                    "B44": exr.B44_COMPRESSION,
                    "B44A": exr.B44A_COMPRESSION,
                    "DWAA": exr.DWAA_COMPRESSION,
                    "DWAB": exr.DWAB_COMPRESSION,
                }

                # Set selected compression
                if header['compression'] != compression_settings[compression_type]:
                    new_header['compression'] = compression_settings[compression_type]
                    print(f"Compressing file {file.name} with {compression_type}")
                    modified = True
            # Truncate to 16 bit half-float
            if trunc_half_float:
                for name, channel in channels.items():
                    if name in ['R','G','B','A']:
                        pixels = channel.pixels
                        # Convert to float16 if not already
                        if pixels.dtype == np.float32:
                            print("Converting",name,"channel to 16 bit")
                            pixels = pixels.astype(np.float16)
                            modified = True
                        new_channels[name] = pixels
                    else:
                        # Copy other channels as they are
                        new_channels[name] = channel.pixels.copy()

            # Write the file
            if not modified:
                print(f"Skipping {file.name}, (reason: already compressed)")
            else:
                output_file_path = file
                with exr.File(new_header, new_channels) as outfile:
                    print(f"writing to {output_file_path}" )
                    outfile.write(str(output_file_path))



if __name__ == "__main__":
    from argparse import ArgumentParser

    # Create an ArgumentParser object
    parser = ArgumentParser(
        description="Process EXR files in a directory, optionally ignoring those in the blacklist directory.")

    # Add arguments for input and optional blacklist directories
    parser.add_argument('input_directory', type=Path, help='Directory containing EXR files to process')
    parser.add_argument('--compression-type', type=str, default=None, help='Type of compression to use (default: use files\' existing compression')
    parser.add_argument('--blacklist-directory', type=Path, nargs='?', const=None, default=None,
                        help='Optional directory containing EXR files to ignore (default: None)')
    parser.add_argument('--no-check-alpha', action='store_false',
                        help="Do not check for meaningful alpha channels in EXR files.")
    parser.add_argument('--no-half-float', action='store_false',
                        help="Do not cast 32-bit data to 16 bit half float.")
    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the process_exr_files function with parsed arguments
    process_exr_files(args.input_directory, args.compression_type, args.blacklist_directory, args.no_check_alpha, args.no_half_float)
