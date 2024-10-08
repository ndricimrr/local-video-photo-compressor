import os
import json
import sys
import subprocess
import shutil  # For copying files
import signal  # For handling Ctrl+C signal
from PIL import Image, UnidentifiedImageError, ExifTags
import piexif
import time


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
            print("Loaded progress successfully")
            return set(data.get('processed_files', []))
   
    print("Error: " + PROGRESS_FILE_NAME + " not found. Loading progress failed.")
    return set()

def load_image(input_file):
    """Loads an image from the input file and returns the image object."""
    try:
        return Image.open(input_file)
    except UnidentifiedImageError:
        print(f"\033[31mFailed to process image (corrupt) (Copying anyway...): {input_file}\033[0m")
        failed_files.append(input_file)
        return None

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

def save_compressed_image(img, output_file, exif_data=None):
    """Saves the image with compression and optional EXIF data."""

        
    quality = 20
    if image_quality:
        quality = image_quality
        print("Compressing with quality: ", quality)
    try:
        if exif_data is None: 
            img.save(output_file, optimize=True, quality=quality)
        else:
            print("Saving with exif data present")
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

    exif_data = img.getexif().tobytes()

    if not exif_data:
        print("No exif found")

    save_compressed_image(img, output_file, exif_data=exif_data)

def compress_video(input_file, output_file, crf, worker):
    """Compresses a video and saves it to the output file."""

    image_quality
    speed = "fast"
    if video_compression_speed:
        speed = video_compression_speed
        print("Compressing with speed: ", speed)

    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-movflags', 'use_metadata_tags',
        '-map_metadata', '0',
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', speed,
        output_file
    ]
    # subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Suppress FFmpeg output

    # Run ffmpeg using Popen so we can terminate it if needed
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while process.poll() is None:  # While ffmpeg is running
            if not worker._is_running:  # If stop is requested
                print("Stopping the ffmpeg process")
                process.terminate()  # Stop the ffmpeg process
                process.wait()  # Wait for it to terminate gracefully
                break
            time.sleep(1)  # Sleep for a bit before checking again

        if process.poll() is not None:  # Process finished
            print(f"Finished processing {input_file}")

    except Exception as e:
        print(f"Error while processing: {e}")
        process.terminate()  # Ensure ffmpeg is stopped on error
        process.wait()  # Ensure the process is cleaned up
    

def process_files(folder, outputFolder, shouldLoadProgress, worker, video_compression_speed_value, image_quality_value):
    """Recursively processes files in the given folder."""
    global processed_images_count, processed_videos_count, skipped_videos_count, unsupported_files_count
    global total_original_images_size, total_final_images_size
    global total_original_videos_size, total_final_videos_size
    global total_unsupported_files_size, total_skipped_videos_size
    global image_quality, video_compression_speed

    # Load processed files if resuming
    
    global processed_files
    if shouldLoadProgress: 
        processed_files = load_progress()
    else:
        print("\n\n\n\nRestarting without loading progress.****")
        total_original_images_size = 0
        total_original_videos_size = 0
        processed_files = set()
        if os.path.exists(PROGRESS_FILE_NAME):
            os.remove(PROGRESS_FILE_NAME)
            print(f"{PROGRESS_FILE_NAME} has been removed. Fresh start...")

    if video_compression_speed_value:
        video_compression_speed = video_compression_speed_value
    if image_quality_value:
        image_quality = image_quality_value
    

    if outputFolder:
        # Create the output folder inside the given outputFolder path
        output_folder = os.path.join(outputFolder, OUTPUT_FOLDER_NAME)
    else:
        # Create the output folder as a sibling directory
        output_folder = os.path.join(os.path.dirname(folder), OUTPUT_FOLDER_NAME)

    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    print(f"Output folder: {output_folder}")  # Print the output folder location
    
    for dirpath, _, filenames in os.walk(folder):
        if not worker._is_running:
            print("Processing stopped by user (Outer loop).")
            break
        for filename in filenames:
            if not worker._is_running:
                print("Processing stopped by user (Inner Loop).")
                break
            input_file = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(input_file, folder)
            output_file = os.path.join(output_folder, relative_path)  # Update to use the sibling output folder

            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Skip files that have already been processed
            if input_file in processed_files:
                continue
            
            notify_data = {
                "processed_images_count": 0,
                "processed_videos_count": 0,
                "total_original_images_size": 0,
                "total_original_videos_size": 0
            }   
            
            # Process based on file type
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                print(f"\033[32mCompressing image: {input_file}\033[0m")
                original_size = os.path.getsize(input_file)
                total_original_images_size += original_size

                start_time = time.time()  # Record the start time
                compress_image(input_file, output_file)
                end_time = time.time()  # Record the end time
                elapsed_time = end_time - start_time

                print(f"Compression finished in {elapsed_time:.4f} seconds.") 

                final_size = os.path.getsize(output_file)
                total_final_images_size += final_size
                
                processed_images_count += 1
                notify_data['processed_images_count'] = processed_images_count
                notify_data['total_original_images_size'] = total_original_images_size
                notify_data['processed_videos_count'] = processed_videos_count
                notify_data['total_original_videos_size'] = total_original_videos_size

                worker.progress.emit(notify_data)
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
                    compress_video(input_file, output_file, crf, worker)

                    final_size = os.path.getsize(output_file)
                    total_final_videos_size += final_size

                    processed_videos_count += 1

                    notify_data['processed_images_count'] = processed_images_count
                    notify_data['total_original_images_size'] = total_original_images_size
                    notify_data['processed_videos_count'] = processed_videos_count
                    notify_data['total_original_videos_size'] = total_original_videos_size

                    worker.progress.emit(notify_data)

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
        print("Usage: python compressStuff.py <folder_path> [--compression-analysis] [-R]")
        return
    
    folder = sys.argv[1]
    if not os.path.exists(folder):
        print(f"Error: The folder {folder} does not exist.")
        return

    if '--compression-analysis' in sys.argv:
        # Check if a specific speed option is provided
        if '-speed' in sys.argv:
            speed_index = sys.argv.index('-speed') + 1
            if speed_index < len(sys.argv):
                speed_option = sys.argv[speed_index]
                analyze_compression_time(folder, speed=speed_option)
            else:
                print("Error: No speed option provided after '-speed'.")
        else:
            analyze_compression_time(folder)  # Default to 'fast'
    else:
        # Start processing files
        process_files(folder)

def format_time(minutes):
    """Convert time in minutes to hours and minutes if necessary, and round it."""
    rounded_minutes = round(minutes)  # Round minutes to remove decimals
    if rounded_minutes >= 60:
        hours = rounded_minutes // 60
        remaining_minutes = rounded_minutes % 60
        return f"{hours}h {remaining_minutes}m"
    return f"{rounded_minutes} minutes"

# Define speed multipliers based on compression settings
speed_multipliers = {
    'ultrafast': 0.5,
    'veryfast': 1.0,
    'fast': 1.5,
    'slow': 2.0
}

def estimate_compression_time(size_in_gb, speed, file_type):
    """Estimate compression time based on file size and compression speed."""
    base_time_per_gb = {
        'image': 0.6,  # Base time: 0.6 minutes per GB for images
        'video': 8,  # Base time: 15 minutes per GB for videos (adjust as needed)
        'copy': 1  # Base time: 1 minute per GB for unsupported files (copying)
    }
    
    # Get the base time for the file type (image/video/copy)
    base_time = base_time_per_gb[file_type]

    # Apply the speed multiplier
    multiplier = speed_multipliers.get(speed, 1.0)

    # Estimate total time
    if (file_type == "image"):
        estimated_time = size_in_gb * base_time
    else:
        estimated_time = size_in_gb * base_time * multiplier
    return estimated_time

def analyze_compression_time(folder, speed='fast'):
    """Analyzes the folder for compression stats and estimated time."""
    total_files_count = 0
    total_size = 0
    image_files_count = 0
    video_files_count = 0
    unsupported_files_count = 0
    total_image_size = 0
    total_video_size = 0
    total_unsupported_size = 0

    image_filetypes = set()
    video_filetypes = set()
    unsupported_filetypes = set()

    # Walk through the directory to analyze file types
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            file_size = os.path.getsize(input_file)
            total_files_count += 1
            total_size += file_size

            # Categorize files based on extension
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_files_count += 1
                total_image_size += file_size
                image_filetypes.add(filename.split('.')[-1].lower())
            elif filename.lower().endswith(('.mp4', '.mkv', '.mov')):
                video_files_count += 1
                total_video_size += file_size
                video_filetypes.add(filename.split('.')[-1].lower())
            else:
                unsupported_files_count += 1
                total_unsupported_size += file_size
                unsupported_filetypes.add(filename.split('.')[-1].lower())

    # Convert sizes to GB for time estimation
    total_image_size_gb = total_image_size / (1024 * 1024 * 1024)
    total_video_size_gb = total_video_size / (1024 * 1024 * 1024)
    total_unsupported_size_gb = total_unsupported_size / (1024 * 1024 * 1024)

    # Estimate compression times
    estimated_image_time = estimate_compression_time(total_image_size_gb, speed, 'image')
    estimated_video_time = estimate_compression_time(total_video_size_gb, speed, 'video')
    estimated_unsupported_time = estimate_compression_time(total_unsupported_size_gb, speed, 'copy')

    total_estimated_time = estimated_image_time + estimated_video_time + estimated_unsupported_time

    # Convert time to hours + minutes if needed
    estimated_image_time_str = format_time(estimated_image_time)
    estimated_video_time_str = format_time(estimated_video_time)
    estimated_unsupported_time_str = format_time(estimated_unsupported_time)
    total_estimated_time_str = format_time(total_estimated_time)

    # Format total size to GB if necessary
    formatted_total_size = format_size(total_size)
    formatted_image_size = format_size(total_image_size)
    formatted_video_size = format_size(total_video_size)
    formatted_unsupported_size = format_size(total_unsupported_size)

    # Print the analysis
    print(f"\n\033[34mCompression Analysis Report\033[0m")
    print(f"Total files found: {total_files_count}")
    print(f"Total folder size: {formatted_total_size}")
    print(f"  - Image files: {image_files_count} ({formatted_image_size}) with filetypes: {', '.join(image_filetypes)}")
    print(f"  - Video files: {video_files_count} ({formatted_video_size}) with filetypes: {', '.join(video_filetypes)}")
    print(f"  - Unsupported files: {unsupported_files_count} ({formatted_unsupported_size}) with filetypes: {', '.join(unsupported_filetypes)}")
    print(f"\nEstimated Compression Time (at {speed} speed):")
    print(f"  - Images: {estimated_image_time_str}")
    print(f"  - Videos: {estimated_video_time_str}")
    print(f"  - Unsupported files (copying): {estimated_unsupported_time_str}")
    print(f"  - Total: {total_estimated_time_str}")
    return {
        'total_estimated_time': total_estimated_time,
        'total_estimated_time_str': total_estimated_time_str,
        'total_files_count': total_files_count.__str__(),
        'total_size': total_size,
        'formatted_total_size': formatted_total_size,
        'image_files_count': image_files_count.__str__(),
        'formatted_image_size': formatted_image_size,
        'video_files_count': video_files_count.__str__(),
        'formatted_video_size': formatted_video_size,
        'unsupported_files_count': unsupported_files_count.__str__(),
        'formatted_unsupported_size': formatted_unsupported_size
    }



if __name__ == "__main__":
    main()
