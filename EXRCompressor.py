from pathlib import Path
import OpenEXR as exr
import numpy as np

##def truncate_to_16bit(data):
##    """Truncate float32 data to 16-bit half-float."""
##    if data.dtype == np.float32:
##        # Convert from float32 to half-float (float16)
##        data = data.astype(np.float16).view('u2')
##        return data
##    elif data.dtype == np.uint32:
##        # Truncate uint32 to uint16
##        data = np.bitwise_and(data, 0xFFFF).astype(np.uint16)
##        return data
##    else:
##        raise ValueError("Unsupported data type for truncation")
##
## Didn't seem to have much of an impact in testing, so disabled for now. May have a second look later

def has_meaningful_alpha(alpha_channel):
    """Check if the alpha channel contains meaningful data."""
    # If all values are 1 (fully opaque) or 0 (fully transparent), it's not meaningful
    unique_values = np.unique(alpha_channel)
    return len(unique_values) > 2 or (len(unique_values) == 2 and (unique_values[0] != 0 and unique_values[1] != 1))


def process_exr_files(input_dir, blacklist):
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
            print(f"Processing file {file}")
            infile = exr.File(str(file), separate_channels = True)
            header = infile.header()
            # Read channels
            channels = infile.channels()
            if 'A' in channels: # Check for alpha channel
                alpha_channel = channels['A'].pixels
                if not has_meaningful_alpha(alpha_channel):
                    print(f"Removing meaningless alpha from {file.name}")
                    del channels['A']
                else:
                    print(f"Alpha channel may contain meaningful data, skipping")
                    #channel_data['A'] = truncate_to_16bit(alpha_channel)
            else:
                print(f"No alpha channel found in {file.name}")

            # Create new header
            new_header = header

            #Create new channels
            new_channels = channels


            # Set DWAB compression with high quality
            new_header['compression'] = exr.DWAB_COMPRESSION
            print(f"Compressing file {file.name}")
            #for ch in ['R','G','B']:
            #   new_channels[ch].pixels = truncate_to_16bit(new_channels[ch].pixels)

            # Write the file
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
    parser.add_argument('--blacklist-directory', type=Path, nargs='?', const=None, default=None,
                        help='Optional directory containing EXR files to ignore (default: None)')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the process_exr_files function with parsed arguments
    process_exr_files(args.input_directory, args.blacklist_directory)