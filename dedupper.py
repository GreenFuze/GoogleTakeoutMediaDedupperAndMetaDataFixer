import json
import subprocess
import sys
import tempfile
import urllib

import imagehash
import pillow_heif
from PIL import Image, ImageFile
from datetime import datetime
from typing import Any, Tuple, List, Dict
import os
import ext_fixer

userprofile = os.environ['USERPROFILE']
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_supported_extensions() -> List[str]:
	command = ['exiftool', '-listf']
	result = subprocess.run(command, capture_output=True, text=True, check=True)
	extensions = []
	for line in result.stdout.splitlines():
		if line.startswith(' '):
			extensions.extend(line.strip().split())
	return [f".{ext.lower()}" for ext in extensions]


SUPPORTED_EXTENSIONS = get_supported_extensions()


def is_media_item_extension(file_full_path: str) -> bool:
	extension = os.path.splitext(file_full_path)[1].lower()
	return extension in SUPPORTED_EXTENSIONS


def get_image_info(file_path: str) -> Dict[str, Any]:
	# use ExifTool to get resolution and date taken time
	# if the file is not a media item, raise error
	# Use ExifTool to get resolution and date taken time
	command = ['exiftool', '-ImageSize', '-DateTimeOriginal', '-j', file_path]
	result = subprocess.run(command, capture_output=True, text=True, check=True)
	metadata = json.loads(result.stdout)[0]
	
	resolution = metadata.get('ImageSize', '0x0')
	date_taken = metadata.get('DateTimeOriginal', None)
	
	# convert date_taken to datetime object and then to isoformat()
	if date_taken is not None:
		date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
		date_taken = date_taken.isoformat()
	
	return {"file_path": file_path, "resolution": resolution, "extension": os.path.splitext(file_path)[1].lower(), "photoTakenTime": date_taken}


def is_video_extension(file_path: str) -> bool:
	extension = os.path.splitext(file_path)[1].lower()
	return extension in ['.mp4', '.mov', '.mp', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.3gp', '.3g2', '.m4v', '.ts', '.mts', '.m2ts', '.vob', '.ogv', '.ogg', '.qt', '.divx', '.xvid', '.rm', '.rmvb', '.asf', '.amv', '.m2v', '.m4v', '.mpeg', '.mpg', '.mpe', '.mpv', '.mp2', '.m2p', '.m2t', '.m2ts',
	                     '.mts', '.mp']


def is_image_extension(file_path: str) -> bool:
	extension = os.path.splitext(file_path)[1].lower()
	return extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif', '.heics', '.heifs', '.heic', '.heif', '.heics', '.heifs', '.heic', '.heif', '.heics', '.heifs', '.heic', '.heif', '.heics', '.heifs']


def get_image_hash(file_path: str) -> str:
	# video extension:
	if is_video_extension(file_path):
		# Generate a temporary file path in the default temp directory
		frame_path = os.path.join(tempfile.gettempdir(), os.path.basename(file_path) + '_frame.png')
		
		phash = None
		try:
			# Extract a frame from the video
			command = ['ffmpeg', '-i', file_path, '-vf', 'thumbnail', '-frames:v', '1', '-update', '1', frame_path]
			subprocess.run(command, check=True)
			
			# Open the extracted frame
			frame_image = Image.open(frame_path)
			
			# Generate the perceptual hash
			phash = imagehash.phash(frame_image)
		except Exception as e:
			print(f"Error extracting frame from video {file_path}: {str(e)}")
			return ''
		finally:
			# Clean up the extracted frame
			try:
				os.remove(frame_path)
			except Exception as e:
				print(f"Error deleting frame {frame_path}: {str(e)}")
		
		if phash is None:
			return ''
		
		return str(phash)
	
	elif is_image_extension(file_path):
		try:
			if file_path.lower().endswith('.heic'):
				pillow_heif.register_heif_opener()
				heif_file = pillow_heif.open_heif(file_path)
				image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
			else:
				# Open the image
				image = Image.open(file_path)
		except Exception as e:
			print(f"Error opening image {file_path}: {str(e)}")
			raise
		
		# Generate the perceptual hash
		try:
			phash = imagehash.phash(image)
		except Exception as e:
			print(f"Error generating perceptual hash for image {file_path}: {str(e)}")
			raise
		
		return str(phash)
	else:
		raise ValueError(f"Unsupported file extension: {file_path}")


def is_live_photo(image_path: str) -> str | None:
	video_path = os.path.splitext(image_path)[0] + '.mp4'
	if os.path.exists(video_path):
		return video_path
	video_path = os.path.splitext(image_path)[0] + '.mp'
	if os.path.exists(video_path):
		return video_path
	video_path = os.path.splitext(image_path)[0] + '.mov'
	if os.path.exists(video_path):
		return video_path
	return None


def get_images_info(root_dir: str) -> dict[str, Any]:
	images_info = None
	if os.path.exists('exif_images_info.json'):
		with open('exif_images_info.json', 'r', encoding='utf-8') as f:
			images_info = json.load(f)
	
	if images_info is None:
		# run exif tool once recursively on the root directory
		# to get all the images' info.
		# store them in a list of dictionaries where the key is the full path of the image
		# and the value is a dictionary of the image info
		command = ['exiftool', '-ImageSize', '-DateTimeOriginal', '-j', '-r', root_dir]
		print('Running exiftool to extract images/videos info...')
		result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
		
		if result.stdout is None or result.stdout == '':
			raise ValueError('Failed to extract images info')
		
		# write result.stdout to a json file
		with open('exif_images_info.json', 'w', encoding='utf-8') as f:
			f.write(result.stdout)
		
		images_info = json.loads(result.stdout)
	
	# convert date_taken to datetime object and then to isoformat()
	for img in images_info:
		if 'DateTimeOriginal' in img:
			date_taken = img['DateTimeOriginal']
			if date_taken is not None and date_taken != '' and date_taken != '0000:00:00 00:00:00':
				date_taken = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
				img['DateTimeOriginal'] = date_taken.isoformat()
	
	return {img['SourceFile']: img for img in images_info}


def find_duplicate_photos(root_dir: str, output_json_path: str) -> None:
	image_hashes: Dict[str, List[Dict[str, Any]]] = {}
	
	images_info = get_images_info(root_dir)
	
	print('Done extracting images/videos info')
	
	files_to_process = []
	for root, _, files in os.walk(root_dir):
		for file in files:
			if is_media_item_extension(file):
				files_to_process.append(os.path.join(root, file))
	
	i = 0
	for file in files_to_process:
		i += 1
		
		if i % 50 == 0:
			print(f'Processing {(i / len(files_to_process) * 100):.3f}%')
		
		# replace '\' with '/' in the file path to match exif output
		file = file.replace('\\', '/')
		
		img_hash = get_image_hash(file)
		if img_hash is None or img_hash == '':
			print('Failed to get image hash for file:', file)
			continue
		
		img_info = images_info[file]
		if is_live_photo(file) is not None:
			img_info["live_photo_video"] = is_live_photo(file)
		if img_hash in image_hashes:
			image_hashes[img_hash].append(img_info)
		else:
			image_hashes[img_hash] = [img_info]
	
	duplicates = {k: v for k, v in image_hashes.items() if len(v) > 1}
	
	with open(output_json_path, 'w', encoding='utf-8') as f:
		try:
			# iterate recursively "duplicates" and make sure that all entries are serializable.
			# if not, convert the entries to serializable format
			for img_hash, images in duplicates.items():
				for img in images:
					if 'photoTakenTime' in img:
						if isinstance(img['photoTakenTime'], datetime):
							img['photoTakenTime'] = img['photoTakenTime'].isoformat()
						elif img['photoTakenTime'] is None:
							img['photoTakenTime'] = ''
			
			json.dump(duplicates, f, ensure_ascii=False, indent=4)
		except Exception as e:
			print('failed to write to json file')


def remove_duplicated_photos(log_file_path: str, is_delete: bool = False) -> None:
	def parse_resolution(resolution: str) -> Tuple[int, int]:
		width, height = map(int, resolution.split('x'))
		return width, height
	
	def get_photo_taken_time(datetime_entry: str) -> int:
		
		if datetime_entry is None or datetime_entry == '' or datetime_entry == '0000:00:00 00:00:00':
			return 2 ** 31 - 1
		
		return int(datetime.fromisoformat(datetime_entry).timestamp())
	
	with open(log_file_path, 'r', encoding='utf-8') as f:
		duplicates: Dict[str, List[Dict[str, Any]]] = json.load(f)
	
	files_to_delete = []
	
	i = 0
	for img_hash, images in duplicates.items():
		
		# check if there is an image that is already selected
		# if so, skip the rest of the images
		if any('selected' in img for img in images):
			# append to files_to_delete all the images that are not selected
			for img in images:
				if 'selected' not in img:
					files_to_delete.append(img['SourceFile'])
					if 'live_photo_video' in img and img['SourceFile'].lower() != img['SourceFile'].lower():
						files_to_delete.append(img['live_photo_video'])
						
			continue
		
		i += 1
		if i % 50 == 0:
			print(f'Processing {(i / len(duplicates) * 100):.3f}%')
		
		# oneliner for "if DateTimeOriginal in img, return it, otherwise return 2**31-1"
		
		images.sort(key=lambda img: (-parse_resolution(img['ImageSize'])[0] * parse_resolution(img['ImageSize'])[1],  # Highest resolution
		                             int(get_photo_taken_time(img['DateTimeOriginal'])) if 'DateTimeOriginal' in img else 2 ** 31 - 1,  # Earliest photo taken time
		                             os.path.splitext(img['SourceFile'])[1].lower() != '.png'  # Prefer PNGs
		                             ))
		
		# Mark the first image as selected and delete the rest
		images[0]['selected'] = True
		images_to_delete = images[1:]
		for img in images_to_delete:
			files_to_delete.append(img['SourceFile'])
			if 'live_photo_video' in img and img['SourceFile'].lower() != img['SourceFile'].lower():
				files_to_delete.append(img['live_photo_video'])
	
	print('Writing updated log file...')
	
	with open(log_file_path, 'w', encoding='utf-8') as f:
		json.dump(duplicates, f, ensure_ascii=False, indent=4)
	
	if is_delete:
		print(f'delete {len(files_to_delete)} files...')
		
		for file in files_to_delete:
			try:
				print('delete: ', file)
				os.remove(file)
			except FileNotFoundError:
				print(f"File not found: {file}")
			except Exception as e:
				print(f"Error deleting file {file}: {str(e)}")
	else:
		print('skipping deletion')
	
	print(f'Done deleting {len(files_to_delete)} files')


def escape_url(url: str) -> str:
	return urllib.parse.quote(url, safe='')


def write_html():
	if not os.path.exists('duplicates.json'):
		print('duplicates.json not found. Run --find-dups first.')
		print('To show also selection for deletion run --delete-dry after --find-dups')
	
	with open('duplicates.json', 'r', encoding='utf-8') as f:
		duplicates = json.load(f)
	
	# create a webpage with the duplicate images
	with open('duplicates.html', 'w', encoding='utf-8') as f:
		f.write('<!DOCTYPE html>\n')
		f.write('<html>\n')
		f.write('<head>\n')
		f.write('<title>Duplicate Images</title>\n')
		f.write('</head>\n')
		f.write('<body>\n')
		f.write('<h1>Duplicate Images</h1>\n')
		for img_hash, images in duplicates.items():
			f.write(f'<h2>{img_hash}</h2>\n')
			for img in images:
				if 'done' in img:  # skip "done" entry
					continue
				
				if 'selected' in img:
					f.write(f'<img src="{escape_url(img["SourceFile"])}" style="border: 2px solid red; width: 20%; height: 20%;">\n')
				else:
					f.write(f'<img src="{escape_url(img["SourceFile"])}" style="width: 20%; height: 20%;">\n')
		f.write('</body>\n')
		f.write('</html>\n')


if __name__ == '__main__':
	tsvi_root = f'{userprofile}\\OneDrive\\Pictures\\'
	nohary_root = 'c:\\Users\\nohar\\OneDrive\\Pictures\\'
	shahar_root = f'{userprofile}\\OneDrive\\Pictures Family\\'
	
	sys.argv = '--delete'
	
	root = shahar_root
	
	if '--delete' in sys.argv:
		if os.path.exists('duplicates.json'):
			remove_duplicated_photos('duplicates.json', not ('--delete-dry' in sys.argv))
		else:
			print('duplicates.json not found')
	elif '--fix-extension' in sys.argv:
		ext_fixer.rename_to_correct_extension(root)
	elif '--find-dups' in sys.argv:  # find duplicates and create duplicates.json
		if not os.path.exists('duplicates.json'):
			find_duplicate_photos(root, 'duplicates.json')
		else:
			print('duplicates.json exist - skipping...')
	elif '--write-html' in sys.argv:
		write_html()
	else:
		msg = """--delete-dry | --delete: delete duplicate files by duplications.json\n--fix-extension: fix file extensions\n--find-dups: find duplicate files and write duplications.json\n"""
		print(msg)
