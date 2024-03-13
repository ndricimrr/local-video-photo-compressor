import os
import subprocess
import sys
import time
from temp import get_cpu_temp

def get_video_bitrate(file_path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration, file_size = map(float, result.stdout.strip().split('\n'))
        bitrate = (file_size * 8) / (duration * 1024)
        return int(bitrate)
    except subprocess.CalledProcessError as e:
        print(f"Error getting bitrate for {file_path}: {e.stderr}")
        return None
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error calculating bitrate for {file_path}: {e}")
        return None

# compress video and pause proess if CPU overheats. 
def compress_video(input_file, output_file, target_bitrate, temperature_threshold, preset='fast'):
    try:
        cmd = ['ffmpeg', '-y', '-i', input_file, '-c:v', 'libx264', '-preset', preset, '-b:v', f'{target_bitrate}k', '-c:a', 'copy', output_file]
        process = subprocess.Popen(cmd)
        while process.poll() is None:
            temp = get_cpu_temp()
            if temp is not None and temp >= temperature_threshold:
                print("CPU temperature is too high. Pausing conversion...")
                process.terminate()
                process.wait()  # Wait for the process to completely terminate
                if os.path.exists(output_file):  # Check if the output file exists
                    os.remove(output_file)  # Remove corrupted output file
                pause_conversion()
                process = subprocess.Popen(cmd)  # Resume the process with slower preset
        print(f"Compressed {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compress {input_file}: {e.stderr}")
        input("Failed press enter to exit")
        # sys.exit(1)  # Exit the script with an error code

def compress_videos_in_folder(input_folder, output_folder, compression_ratio=0.3, temperature_threshold=98):
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' not found.")
        return
    
    if not os.path.exists(output_folder):
        print(f"output folder '{output_folder}' not found.")
        os.makedirs(output_folder)

    for root, _, files in os.walk(input_folder):
        print(f"----- 0 input_folder : '{root}' .")
        for file in files:
            if file.lower().endswith(('.mkv', '.mp4', '.avi', '.mov')):
                print(f"File to convert now : '{file}' .")

                input_file = os.path.join(root, file)
                original_filename, extension = os.path.splitext(file)
                output_file = os.path.join(output_folder, f"{original_filename}_NEW_CONVERTED{extension}")
                original_bitrate = get_video_bitrate(input_file)
                if original_bitrate is not None:
                    print(f"  -Original_bitrate = '{original_bitrate}' .")
                    target_bitrate = int(original_bitrate * compression_ratio)
                    print(f"  -Target_bitrate = '{target_bitrate}' .")
            
                    if target_bitrate > 20000:  # Limit to 20 Mbps (20000 kbps)
                        print(f"  >>>ERROR: Found bitrate > 20k = '{target_bitrate}. Changing to 10000")
                        target_bitrate = 10000
                    compress_video(input_file, output_file, target_bitrate, temperature_threshold)
    print(f"END ____ .")

def pause_conversion():
    print("Pausing conversion...")
    while True:
        temp = get_cpu_temp()
        print(f"Current CPU temp: {temp} ...")
        if temp is not None and temp <= 75:
            break
        time.sleep(5)

# Example usage:
input_folder = r'C:\Users\ndric\Desktop\recover\photos\argert_bilardo'
output_folder = r'C:\Users\ndric\Desktop\recover\photos'
try:
    compress_videos_in_folder(input_folder, output_folder)
except Exception as e:
    print(f"An error occurred: {e}")

input("Press Enter to exit...")
