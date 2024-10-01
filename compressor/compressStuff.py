import os
import json
import sys
import subprocess
import shutil  # For copying files
import signal  # For handling Ctrl+C signal
from PIL import Image, UnidentifiedImageError, ExifTags
import piexif

# Constants for output folder name and progress file
OUTPUT_FOLDER_NAME = "output"
PROGRESS_FILE_NAME = "saved-progress.json"

# Global variables for tracking stats
processed_images_count = 0
processed_videos_count = 0
skipped_videos_count = 0
unsupported_files_count = 0
failed_files = []  # To track files that fail
unsupported_files = []  # To track unsupported files
processed_files = set()

# Sizes tracking
total_original_images_size = 0
total_final_images_size = 0
total_original_videos_size = 0
total_final_videos_size = 0
total_unsupported_files_size = 0  # New: Track size of unsupported files
total_skipped_videos_size = 0  # New: Track size of skipped videos

def format_size(size_in_bytes):
    """Returns size in MB or GB depending on the size."""
    if size_in_bytes >= 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def save_progress(processed_files):
    """Saves the processed files and size data to the progress file."""
    data = {
        'processed_files': list(processed_files),
        'total_original_images_size': total_original_images_size,
        'total_final_images_size': total_final_images_size,
        'total_original_videos_size': total_original_videos_size,
        'total_final_videos_size': total_final_videos_size,
        'total_unsupported_files_size': total_unsupported_files_size,  # Save unsupported files size
        'total_skipped_videos_size': total_skipped_videos_size  # Save skipped videos size
    }
    with open(PROGRESS_FILE_NAME, 'w') as f:
        json.dump(data, f)

def load_progress():
    """Loads the processed files and size data from the progress file."""
    global total_original_images_size, total_final_images_size
    global total_original_videos_size, total_final_videos_size
    global total_unsupported_files_size, total_skipped_videos_size

    if os.path.exists(PROGRESS_FILE_NAME):
        with open(PROGRESS_FILE_NAME, 'r') as f:
            data = json.load(f)
            total_original_images_size = data.get('total_original_images_size', 0)
            total_final_images_size = data.get('total_final_images_size', 0)
            total_original_videos_size = data.get('total_original_videos_size', 0)
            total_final_videos_size = data.get('total_final_videos_size', 0)
            total_unsupported_files_size = data.get('total_unsupported_files_size', 0)  # Load unsupported size
            total_skipped_videos_size = data.get('total_skipped_videos_size', 0)  # Load skipped videos size
            return set(data.get('processed_files', []))
    return set()

def load_image(input_file):
    """Loads an image from the input file and returns the image object."""
    try:
        print("Loading image is fine")
        return Image.open(input_file)
    except UnidentifiedImageError:
        print(f"\033[31mFailed to process image (corrupt) (Copying anyway...): {input_file}\033[0m")
        failed_files.append(input_file)
        return None

def correct_orientation(img):
    """Corrects the image orientation based on EXIF data."""
    try:
        exif_data = img.getexif()  # Get EXIF data if available
        if not exif_data:
            return img  # No EXIF, no orientation correction

        # Find the orientation tag in the EXIF data
        # for orientation in ExifTags.TAGS.keys():
        #     if ExifTags.TAGS[orientation] == 'Orientation':
        #         break

        # Find the orientation tag in the EXIF data
        orientation_tag = None
        for tag in ExifTags.TAGS.keys():
            if ExifTags.TAGS[tag] == 'Orientation':
                orientation_tag = tag
                break
        
        if orientation_tag and orientation_tag in exif_data:
            orientation_value = exif_data[orientation_tag]
            # Apply rotation based on the orientation value
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)


        # if orientation in exif_data:
        #     print("Orientation inside")
        #     orientation_value = exif_data[orientation]
        #     if orientation_value == 3:
        #         print("Orientation 3")
        #         img = img.rotate(180, expand=True)
        #     elif orientation_value == 6:
        #         print("Orientation 6")
        #         img = img.rotate(270, expand=True)
        #     elif orientation_value == 8:
        #         print("Orientation 8")
        #         img = img.rotate(90, expand=True)
        print("Orientation is fine")
        return img
    except Exception as e:
        print(f"\033[31mError correcting orientation: {e}\033[0m")
        return img  # Return the unmodified image if any error occurs

def filter_exif_data(exif_data, essential_tags=None):
    """Filters EXIF data to retain only the essential tags."""
    if essential_tags is None:
        essential_tags = [ 
            271, # Manufacturer of the camera used to capture the image.
            272, # Model of the camera used to capture the image.
            274, # Orientation of the image
            36867, # Date and time when the photo was originally taken.
            40962, # Image width in pixels.
            40963, # Image height in pixels.
            # 34853, # GPS data
        ]

    if not exif_data:
        print("No exif found")
        return None

    try:
        exif_dict = piexif.load(exif_data)  # Load EXIF data into a dictionary
        # Filter the EXIF dictionary to retain only essential tags
        filtered_exif_dict = {
            ifd: {tag: value for tag, value in exif_dict[ifd].items() if tag in essential_tags}
            for ifd in exif_dict
        }
        return piexif.dump(filtered_exif_dict)  # Convert filtered EXIF dictionary back to bytes
    except Exception as e:
        print(f"\033[31mFailed to filter EXIF data: Error: {e}\033[0m")
        return None  # Return None if filtering fails

def save_compressed_image(img, output_file, exif_data=None, quality=20):
    """Saves the image with compression and optional EXIF data."""
    try:
        if exif_data is None: 
            img.save(output_file, optimize=True, quality=quality)
        else:
            print("Saving with exif data present")
            print(exif_data)
            img.save(output_file, optimize=True, quality=quality, exif=exif_data)
    except Exception as e:
        print(f"\033[31mError saving image: {output_file}. Error: {e}\033[0m")

def compress_image(input_file, output_file):
    """Compresses an image, corrects orientation, and preserves essential EXIF data."""
    # Load the image
    img = load_image(input_file)
    if img is None:
        shutil.copy2(input_file, output_file)  # Copy the corrupt file if image loading fails
        return

    # Extract original EXIF data
    # exif_data = img.info.get('exif', None)
 
    # exif_data = piexif.load(input_file)

    
    # Correct the image orientation based on EXIF data
    img = correct_orientation(img)

    exif_data = img.getexif().tobytes()


    if not exif_data:
        print("No exif found")
    else: 
        print("Found EXIF =--------------------------------------------------------------->")
        print(img.getexif())

    # Filter EXIF data to keep only essential tags
    # filtered_exif_data_result = filter_exif_data(exif_data)

    # Prepare the EXIF dictionary for piexif
   
    # essential_tags = [ 
    #         271, # Manufacturer of the camera used to capture the image.
    #         272, # Model of the camera used to capture the image.
    #         274, # Orientation of the image
    #         36867, # Date and time when the photo was originally taken.
    #         40962, # Image width in pixels.
    #         40963, # Image height in pixels.
    #         # 34853, # GPS data
    #     ]
    # # Create a new dictionary to hold filtered EXIF data

    
    # try:
    #     exif_dict = piexif.load(exif_data)  # Load EXIF data into a dictionary
    #     # Filter the EXIF dictionary to retain only essential tags
    #     filtered_exif_dict = {
    #         ifd: {tag: value for tag, value in exif_dict[ifd].items() if tag in essential_tags}
    #         for ifd in exif_dict
    #     }
    #     exif_bytes = piexif.dump(filtered_exif_dict)  # Convert filtered EXIF dictionary back to bytes
    # except Exception as e:
    #     print(f"Failed to filter EXIF data: Error: {e}")
    #     return None  # Return None if filtering fails

    # if filtered_exif_data_result is None:
    #     print("None filter")
    # else: 
    #     print("Some filters spotted ===>")

    # Save the compressed image
    save_compressed_image(img, output_file, exif_data=exif_data)

def compress_video(input_file, output_file, crf):
    """Compresses a video and saves it to the output file."""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', 'fast',
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Suppress FFmpeg output

def process_files(folder):
    """Recursively processes files in the given folder."""
    global processed_images_count, processed_videos_count, skipped_videos_count, unsupported_files_count
    global total_original_images_size, total_final_images_size
    global total_original_videos_size, total_final_videos_size
    global total_unsupported_files_size, total_skipped_videos_size

    # Define the output folder as a sibling directory
    output_folder = os.path.join(os.path.dirname(folder), OUTPUT_FOLDER_NAME)
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    print(f"Output folder: {output_folder}")  # Print the output folder location
    
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(input_file, folder)
            output_file = os.path.join(output_folder, relative_path)  # Update to use the sibling output folder

            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Skip files that have already been processed
            if input_file in processed_files:
                continue
            
            # Process based on file type
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                print(f"\033[32mCompressing image: {input_file}\033[0m")
                original_size = os.path.getsize(input_file)
                total_original_images_size += original_size
                compress_image(input_file, output_file)
                final_size = os.path.getsize(output_file)
                total_final_images_size += final_size
                processed_images_count += 1
                print(f"Processed {input_file}: {format_size(original_size)} -> {format_size(final_size)} , (Decrease: {calculate_percentage_decrease(original_size, final_size):.2f} %)")

            elif filename.lower().endswith(('.mp4', '.mkv', '.mov')):
                input_size = os.path.getsize(input_file)
                input_size_mb = input_size / (1024 * 1024)
                crf = 47  # Default CRF value

                # Determine CRF based on file size
                if input_size_mb < 10:
                    print(f"Copying video (too small ({input_size_mb} MB)): {input_file}")
                    # Copy the file instead of compressing
                    shutil.copy2(input_file, output_file)
                    skipped_videos_count += 1
                    total_skipped_videos_size += input_size  # Track skipped video size
                else:
                    if 10 <= input_size_mb < 20:
                        crf = 34
                    elif 20 <= input_size_mb < 50:
                        crf = 35
                    elif 50 <= input_size_mb < 150:
                        crf = 38
                    elif 150 <= input_size_mb < 300:
                        crf = 39
                    elif 300 <= input_size_mb < 500:
                        crf = 40
                    elif 500 <= input_size_mb < 1024:
                        crf = 41
                    else:
                        crf = 42

                    original_size = os.path.getsize(input_file)
                    print(f"\033[33mCompressing video (Size= {format_size(original_size)} ) (CRF {crf}): {input_file}\033[0m")
                   
                    total_original_videos_size += original_size
                    compress_video(input_file, output_file, crf)
                    final_size = os.path.getsize(output_file)
                    total_final_videos_size += final_size
                    processed_videos_count += 1
                    percentage_decrease = 100 * (original_size - final_size) / original_size if original_size > 0 else 0
                    print(f"Processed {input_file}: {format_size(original_size)} -> {format_size(final_size)} (Decrease: {percentage_decrease:.2f}%)")
                processed_videos_count += 1  # Count copied video as processed

            else:
                # Unsupported file type, copy it directly and log it
                print(f"\033[33mCopying unsupported file: {input_file}\033[0m")
                file_size = os.path.getsize(input_file)
                total_unsupported_files_size += file_size  # Track unsupported file size
                shutil.copy2(input_file, output_file)
                unsupported_files.append(input_file)
                unsupported_files_count += 1

            # Save progress after each file
            processed_files.add(input_file)
            save_progress(processed_files)

    print(f"\nProcessed {processed_images_count} images with total original size: {format_size(total_original_images_size)} and total final size: {format_size(total_final_images_size)}.")
    print(f"Processed {processed_videos_count} videos with total original size: {format_size(total_original_videos_size)} and total final size: {format_size(total_final_videos_size)}.")

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    print("\n\n\033[33mGracefully exiting on Ctrl+C...\033[0m")
    print_summary()
    sys.exit(0)

def calculate_percentage_decrease(original_size, final_size):
    """Calculates the percentage decrease in file size."""
    if original_size > 0:
        return 100 * (original_size - final_size) / original_size
    return 0

def print_summary():
    """Prints a summary of processed files with percentage decrease."""
    global processed_images_count, processed_videos_count, skipped_videos_count, unsupported_files_count

    # Calculate percentage decrease for images and videos
    image_decrease_percentage = calculate_percentage_decrease(total_original_images_size, total_final_images_size)
    video_decrease_percentage = calculate_percentage_decrease(total_original_videos_size, total_final_videos_size)

    print("\n\033[34mSummary\033[0m")
    print(f"Processed {processed_images_count} images with total size: {format_size(total_original_images_size)} -> {format_size(total_final_images_size)}. ({image_decrease_percentage:.2f}% file size decrease)")
    print(f"Processed {processed_videos_count} videos with total size: {format_size(total_original_videos_size)} -> {format_size(total_final_videos_size)}. ({video_decrease_percentage:.2f}% file size decrease)")
    print(f"Skipped {skipped_videos_count} videos (too small to compress). (Total Size: {format_size(total_skipped_videos_size)})")  # Skipped videos size
    print(f"Copied {unsupported_files_count} unsupported files. (Total Size: {format_size(total_unsupported_files_size)})")  # Unsupported files size

    if failed_files:
        print(f"\033[31mFailed to process {len(failed_files)} files (copied instead):\033[0m")
        for f in failed_files:
            print(f" - {f}")
    
    if unsupported_files:
        print(f"\033[33mCopied {unsupported_files_count} unsupported files:\033[0m")
        for f in unsupported_files:
            print(f" - {f}")

def main():
    """Main function to execute the script."""
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    if len(sys.argv) < 2:
        print("Usage: python compressStuff.py <folder_path> [-R]")
        return
    
    folder = sys.argv[1]
    if not os.path.exists(folder):
        print(f"Error: The folder {folder} does not exist.")
        return

    # Load processed files if resuming
    global processed_files
    processed_files = load_progress()

    # Start processing files
    process_files(folder)

if __name__ == "__main__":
    main()
