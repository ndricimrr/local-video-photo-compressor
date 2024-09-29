import os
import json
import sys
import subprocess
import shutil  # For copying files
import signal  # For handling Ctrl+C signal
from PIL import Image, UnidentifiedImageError

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

def compress_image(input_file, output_file):
    """Compresses an image and saves it to the output file."""
    try:
        img = Image.open(input_file)
        img.save(output_file, optimize=True, quality=58)
    except UnidentifiedImageError:
        print(f"\033[31mFailed to process image (corrupt): {input_file}\033[0m")
        failed_files.append(input_file)  # Save the failed file to the list
        shutil.copy2(input_file, output_file)  # Copy the corrupt file

def compress_video(input_file, output_file, crf):
    """Compresses a video and saves it to the output file."""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', 'ultrafast',
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
                print(f"Processed {input_file}: {format_size(original_size)} -> {format_size(final_size)}")

            elif filename.lower().endswith(('.mp4', '.mkv', '.mov')):
                input_size = os.path.getsize(input_file)
                input_size_mb = input_size / (1024 * 1024)
                crf = 47  # Default CRF value

                # Determine CRF based on file size
                if input_size_mb < 1:
                    print(f"Copying video (too small (1MB)): {input_file}")
                    # Copy the file instead of compressing
                    shutil.copy2(input_file, output_file)
                    skipped_videos_count += 1
                    total_skipped_videos_size += input_size  # Track skipped video size
                else:
                    if 1 <= input_size_mb < 10:
                        crf = 34
                    if 10 <= input_size_mb < 20:
                        crf = 35
                    if 20 <= input_size_mb < 50:
                        crf = 35
                    if 50 <= input_size_mb < 150:
                        crf = 36
                    elif 150 <= input_size_mb < 300:
                        crf = 37
                    elif 300 <= input_size_mb < 500:
                        crf = 39
                    elif 500 <= input_size_mb < 1024:
                        crf = 40
                    else:
                        crf = 41

                    print(f"\033[33mCompressing video (CRF {crf}): {input_file}\033[0m")
                    original_size = os.path.getsize(input_file)
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
