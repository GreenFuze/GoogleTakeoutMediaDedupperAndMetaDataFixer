import os
import re


# fix extension doesn't match file header - rename file + rename associated json file if such exists
def rename_to_correct_extension(root_dir: str) -> None:
	
	def is_png_file(file_path: str) -> bool:
		png_signature = b'\x89PNG\r\n\x1a\n'
		with open(file_path, 'rb') as f:
			file_header = f.read(8)
		return file_header == png_signature
	
	def is_gif_file(file_path: str) -> bool:
		gif_signature = b'GIF89a'
		with open(file_path, 'rb') as f:
			file_header = f.read(6)
		return file_header == gif_signature
	
	def is_jpeg_file(file_path: str) -> bool:
		jpeg_signature = b'\xff\xd8\xff'
		with open(file_path, 'rb') as f:
			file_header = f.read(3)
		return file_header == jpeg_signature
	
	def is_heic_file(file_path: str) -> bool:
		heic_signature = b'ftypheic'
		with open(file_path, 'rb') as f:
			file_header = f.read(8)
		return file_header == heic_signature
	
	def is_tiff_file(file_path: str) -> bool:
		tiff_signature = b'II*\x00'
		with open(file_path, 'rb') as f:
			file_header = f.read(4)
		return file_header == tiff_signature
	
	def is_mp4_file(file_path: str) -> bool:
		mp4_signature = b'\x00\x00\x00 ftypmp42'
		with open(file_path, 'rb') as f:
			file_header = f.read(12)
		return file_header == mp4_signature
	
	def is_mov_file(file_path: str) -> bool:
		mov_signature = b'\x00\x00\x00 ftypqt'
		with open(file_path, 'rb') as f:
			file_header = f.read(12)
		return file_header == mov_signature
	
	def is_webp_file(file_path: str) -> bool:
		webp_signature = b'RIFF....WEBPVP8 '
		with open(file_path, 'rb') as f:
			file_header = f.read(12)
		return file_header == webp_signature
	
	def is_bmp_file(file_path: str) -> bool:
		bmp_signature = b'BM'
		with open(file_path, 'rb') as f:
			file_header = f.read(2)
		return file_header == bmp_signature
	
	files_to_process = []
	for root, _, files in os.walk(root_dir):
		for file in files:
			files_to_process.append(os.path.join(root, file))
	
	i = 0
	for file_path in files_to_process:
		i += 1
		
		if i % 100 == 0:
			print(f'\nProcessing {(i / len(files_to_process)) * 100:.3f}%')
		else:
			print('.', end='')
		
		# if the file extension doesn't match the file header, rename the file
		# and rename the associated json file if such exists
		
		if is_png_file(file_path) and not file_path.lower().endswith('.png'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .png extension
			new_file_path = re.sub(rf'{file_ext}$', '.png', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.png.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_gif_file(file_path) and not file_path.lower().endswith('.gif'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .gif extension
			new_file_path = re.sub(rf'{file_ext}$', '.gif', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.gif.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_jpeg_file(file_path) and not file_path.lower().endswith('.jpg') and not file_path.lower().endswith('.jpeg'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .jpg extension
			new_file_path = re.sub(rf'{file_ext}$', '.jpg', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.jpg.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_heic_file(file_path) and not file_path.lower().endswith('.heic'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .heic extension
			new_file_path = re.sub(rf'{file_ext}$', '.heic', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.heic.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_tiff_file(file_path) and not file_path.lower().endswith('.tiff'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .tiff extension
			new_file_path = re.sub(rf'{file_ext}$', '.tiff', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.tiff.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_mp4_file(file_path) and not file_path.lower().endswith('.mp4'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .mp4 extension
			new_file_path = re.sub(rf'{file_ext}$', '.mp4', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.mp4.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_mov_file(file_path) and not file_path.lower().endswith('.mov'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .mov extension
			new_file_path = re.sub(rf'{file_ext}$', '.mov', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.mov.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_webp_file(file_path) and not file_path.lower().endswith('.webp'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .webp extension
			new_file_path = re.sub(rf'{file_ext}$', '.webp', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.webp.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)
		
		elif is_bmp_file(file_path) and not file_path.lower().endswith('.bmp'):
			# get file extension
			file_ext = os.path.splitext(file_path)[1]
			
			# rename the file to have a .bmp extension
			new_file_path = re.sub(rf'{file_ext}$', '.bmp', file_path, flags=re.IGNORECASE)
			
			os.rename(file_path, new_file_path)
			
			# rename the associated json file if such exists
			json_path = file_path + '.json'
			if os.path.exists(json_path):
				new_json_path = re.sub(rf'{file_ext}$', '.bmp.json', json_path, flags=re.IGNORECASE)
				os.rename(json_path, new_json_path)