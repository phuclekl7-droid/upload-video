import os
import subprocess
import json

def get_video_duration(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0

def split_video(filepath, parts):
    duration = get_video_duration(filepath)
    if duration == 0:
        return [filepath]
    
    part_duration = duration / parts
    output_files = []
    
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    dir_name = os.path.dirname(filepath)
    
    for i in range(parts):
        start_time = i * part_duration
        output_name = f"{name}_part{i+1}{ext}"
        output_path = os.path.join(dir_name, output_name)
        
        try:
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception as e_del:
                    print(f"Warning: Cannot delete existing file {output_path}: {e_del}")
            result = subprocess.run(
                ['ffmpeg', '-y', '-ss', str(start_time), '-i', filepath, '-t', str(part_duration), '-c', 'copy', output_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            output_files.append(output_path)
        except Exception as e:
            err_msg = ""
            if isinstance(e, subprocess.CalledProcessError) and e.stderr:
                err_msg = f" FFMPEG STDERR: {e.stderr.decode('utf-8', errors='replace')}"
            try:
                print(f"Error splitting part {i+1}.{err_msg}")
            except:
                print(f"Error splitting part {i+1} (unicode error formatting exception)")
            
    return output_files

def extract_thumbnails(filepath):
    duration = get_video_duration(filepath)
    if duration == 0:
        return []
        
    timestamps = [duration * 0.25, duration * 0.5, duration * 0.75]
    output_files = []
    
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    dir_name = os.path.dirname(filepath)
    
    for i, ts in enumerate(timestamps):
        output_name = f"{name}_thumb_{i+1}.jpg"
        output_path = os.path.join(dir_name, output_name)
        
        try:
            result = subprocess.run(
                ['ffmpeg', '-y', '-ss', str(ts), '-i', filepath, '-vframes', '1', '-q:v', '2', output_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )
            output_files.append(output_path)
        except subprocess.CalledProcessError as e:
            pass # ignore failure silently or log safely
            
    return output_files
