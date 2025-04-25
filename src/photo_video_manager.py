# photo_video_manager.py
import argparse
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

import hachoir.metadata
import hachoir.parser
from PIL import Image, ExifTags
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


def get_photo_date_taken(filepath):
    """ Get the date the photo was taken from EXIF or the date the file was modified """
    try:
        image = Image.open(filepath)
        exif_data = image.getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    try:
        return datetime.fromtimestamp(filepath.stat().st_mtime)
    except Exception:
        return None


def get_video_date_taken(filepath):
    """ Get the date the video was shot via hachoir or by modification """
    if hachoir is None:
        return datetime.fromtimestamp(filepath.stat().st_mtime)
    try:
        parser = createParser(str(filepath))
        if not parser:
            return None
        with parser:
            metadata = extractMetadata(parser)
        if metadata and metadata.has("creation_date"):
            return metadata.get("creation_date")
    except Exception:
        pass
    return datetime.fromtimestamp(filepath.stat().st_mtime)


def hash_file(filepath):
    """ Calculate MD5 hash of a file to find duplicates """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_target_filename(base_path, date, original_ext):
    """ Generate a target name based on the date, adding a counter in case of conflicts """
    base_name = date.strftime("%Y-%m-%d_%H-%M-%S")
    target = base_path / f"{base_name}{original_ext}"
    counter = 1
    while target.exists():
        target = base_path / f"{base_name}_{counter}{original_ext}"
        counter += 1
    return target


def move_file(filepath, target_dir, date_taken, log_file, keep_original):
    """ Move or copy the file to the appropriate folder with a rename """
    try:
        ext = filepath.suffix.lower()
        target_path = target_dir / str(date_taken.year) / f"{date_taken.month:02}"
        target_path.mkdir(parents=True, exist_ok=True)
        new_file = get_target_filename(target_path, date_taken, ext)
        if keep_original:
            shutil.copy2(str(filepath), str(new_file))  # save metadata
            log_file.write(f"Copied: {filepath} -> {new_file}\n")
        else:
            shutil.move(str(filepath), str(new_file))
            log_file.write(f"Moved: {filepath} -> {new_file}\n")
    except Exception as e:
        log_file.write(f"Failed to move {filepath}: {e}\n")


def main(source, photos_dest, videos_dest, keep_original):
    """ Main function: process all files in the source directory """
    seen_hashes = set()
    source_path = Path(source)
    all_files = list(source_path.rglob("*"))

    with open("sort_log.txt", "w", encoding="utf-8") as log_file:
        for filepath in all_files:
            if not filepath.is_file():
                continue

            try:
                file_hash = hash_file(filepath)
                if file_hash in seen_hashes:
                    log_file.write(f"Duplicate removed: {filepath}\n")
                    if not keep_original:
                        filepath.unlink()  # Remove duplicates
                    continue
                seen_hashes.add(file_hash)

                ext = filepath.suffix.lower()
                if ext in [".jpg", ".jpeg", ".png"]:
                    date = get_photo_date_taken(filepath)
                    if date:
                        move_file(filepath, Path(photos_dest), date, log_file, keep_original)
                    else:
                        log_file.write(f"No date found: {filepath}\n")
                elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
                    date = get_video_date_taken(filepath)
                    if date:
                        move_file(filepath, Path(videos_dest), date, log_file, keep_original)
                    else:
                        log_file.write(f"No video date found: {filepath}\n")
                else:
                    log_file.write(f"Skipped (unknown extension): {filepath}\n")
            except Exception as e:
                log_file.write(f"Error processing {filepath}: {e}\n")


if __name__ == "__main__":
    """ Entry point: command line argument processing """
    parser = argparse.ArgumentParser(description="Photo/video sorter by date")
    parser.add_argument("--source", required=True, help="Folder with originals")
    parser.add_argument("--photos", required=True, help="Where to put the photo")
    parser.add_argument("--videos", required=True, help="Where to put the video")
    parser.add_argument("--keep", action="store_true",
                        help="Leave original files (copy instead of move))")
    args = parser.parse_args()

    main(args.source, args.photos, args.videos, args.keep)
