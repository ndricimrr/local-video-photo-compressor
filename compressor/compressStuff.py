import os
import json
import sys
import ffmpeg
from PIL import Image

# Constants for output folder name and progress file
OUTPUT_FOLDER_NAME = "output"
PROGRESS_FILE_NAME = "saved-progress.json"

def save_progress(cutoff_file):
    """Saves the last processed file path to the progress file."""
    with open(PROGRESS_FILE_NAME, 'w') as f:
        json.dump({'cutoff_file': cutoff_file}, f)

def load_progress():
    """Loads the last processed file path from the progress file."""
    if os.path.exists(PROGRESS_FILE_NAME):
        with open(PROGRESS_FILE_NAME, 'r') as f:
            data = json.load(f)
            return data.get('cutoff_file')
    return None

def compress_image(input_file, output_file):
    """Compresses an image and saves it to the output file."""
    img = Image.open(input_file)
    img.save(output_file, optimize=True, quality=85)

def compress_video(input_file, output_file, crf):
    """Compresses a video and saves it to the output file."""
    ffmpeg.input(input_file).output(output_file, **{'crf': crf}).run(overwrite_output=True)

def process_files(folder, processed_files, resume):
    """Recursively processes files in the given folder."""
    total_original_images_size = 0
    total_final_images_size = 0
    total_original_videos_size = 0
    total_final_videos_size = 0
    processed_images_count = 0
    processed_videos_count = 0
    
    # Load the last processed file to resume only if resuming
    cutoff_file = load_progress() if resume else None
    
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            input_file = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(input_file, folder)
            output_file = os.path.join(folder, OUTPUT_FOLDER_NAME, relative_path)

            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Skip files that have already been processed
            if input_file in processed_files:
                continue

            # Check if we need to resume processing
            if resume and cutoff_file and input_file != cutoff_file:
                continue
            else:
                cutoff_file = input_file  # Update the cutoff to the current file

            # Process based on file type
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                print(f"\033[32mCompressing image: {input_file}\033[0m")
                original_size = os.path.getsize(input_file)
                total_original_images_size += original_size
                compress_image(input_file, output_file)
                final_size = os.path.getsize(output_file)
                total_final_images_size += final_size
                processed_images_count += 1
                print(f"Processed {input_file}: {original_size / (1024 * 1024):.2f} MB -> {final_size / (1024 * 1024):.2f} MB")

            elif filename.lower().endswith(('.mp4', '.mkv', '.mov')):
                input_size = os.path.getsize(input_file)
                input_size_mb = input_size / (1024 * 1024)
                crf = 47  # Default CRF value

                # Determine CRF based on file size
                if input_size_mb < 50:
                    print(f"Skipping video (too small): {input_file}")
                    output_file = input_file  # Just copy the file
                elif 50 <= input_size_mb < 150:
                    crf = 40
                elif 150 <= input_size_mb < 300:
                    crf = 41
                elif 300 <= input_size_mb < 500:
                    crf = 42
                elif 500 <= input_size_mb < 1024:
                    crf = 45
                else:
                    crf = 47
                
                print(f"\033[33mCompressing video (CRF {crf}): {input_file}\033[0m")
                original_size = os.path.getsize(input_file)
                total_original_videos_size += original_size
                compress_video(input_file, output_file, crf)
                final_size = os.path.getsize(output_file)
                total_final_videos_size += final_size
                processed_videos_count += 1
                percentage_decrease = 100 * (original_size - final_size) / original_size if original_size > 0 else 0
                print(f"Processed {input_file}: {original_size / (1024 * 1024):.2f} MB -> {final_size / (1024 * 1024):.2f} MB (Decrease: {percentage_decrease:.2f}%)")

            # Save progress after each file
            processed_files.add(input_file)
            save_progress(cutoff_file)

    print(f"\nProcessed {processed_images_count} images with total original size: {total_original_images_size / (1024 * 1024):.2f} MB and total final size: {total_final_images_size / (1024 * 1024):.2f} MB.")
    print(f"Processed {processed_videos_count} videos with total original size: {total_original_videos_size / (1024 * 1024):.2f} MB and total final size: {total_final_videos_size / (1024 * 1024):.2f} MB.")

def main():
    """Main function to execute the script."""
    if len(sys.argv) < 2:
        print("Usage: python compressStuff.py <folder_path> [-R]")
        return
    
    folder = sys.argv[1]
    if not os.path.exists(folder):
        print(f"Error: The folder {folder} does not exist.")
        return

    # Use a set to track processed files
    processed_files = set()

    # Check if resuming from progress file
    resume = "-R" in sys.argv
    if resume:
        cutoff_file = load_progress()
        if cutoff_file:
            print(f"Resuming from: {cutoff_file}")
        else:
            print("No progress file found. Starting fresh.")

    # Start processing files
    process_files(folder, processed_files, resume)

if __name__ == "__main__":
    main()
