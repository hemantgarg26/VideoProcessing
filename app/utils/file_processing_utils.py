from app.utils.logger import get_logger

import subprocess
logger = get_logger(__name__)

'''
    Converts a File to MP4 Format
'''
def convert_to_mp4(input_path: str, output_path: str):
    command = [
        'ffmpeg',
        '-i', input_path,  # input file
        '-c:v', 'libx264',  # video codec
        '-preset', 'fast',  # encoding speed
        '-crf', '22',       # quality (lower is better, range: 0-51)
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        logger.info("File Conversion Success")
    except subprocess.CalledProcessError as e:
        logger.error(f"File Conversions Failure : {e}", e)

'''
    Gets a Thumbnail from a Video File
'''
def extract_thumbnail(input_path: str, output_path: str, timestamp: str = "00:00:10"):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-ss', timestamp,
        '-vf', 'scale=320:-1',
        '-frames:v', '1',
        output_path
    ]
    
    try:
        subprocess.run(command, check=True)
        logger.info(f"Thumbnail saved to {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error("Error extracting thumbnail:", e)