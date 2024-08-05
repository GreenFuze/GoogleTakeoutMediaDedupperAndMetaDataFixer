# Google Takeout Photos. Embed & Dedup

So I tried to migrate my cloud provider for my photo and video library. As you know, it is not that straightforward (you're here after all, right?).

First I wanted to embed Google's metadata into the photos and videos, for that I used _exiftool_ (section 1).
For the deduplication, I did not find anything that worked as I wanted, so I wrote a small python script to get the job done.

## Embed MetaData from Google Takeout JSON files into photos & videos

Notice:
1. I'll write "photo" to refer to both photos and videos
2. I have only tested the following in windows, but the applications are cross-platform, so it _should_ be okay.

Using _exiftool_ we can recursively embed metadata from Google Takeout JSON files into photos. The following command will embed the metadata from the JSON files into the photos. The command will overwrite the original files.

To install exiftool:
```bash
# windows
winget install OliverBetz.ExifTool

# mac
brew install exiftool

# linux
sudo apt install exiftool

```

Using exiftool we can run recursively and map the JSON fields
into the metadata fields within the photo.

I am moving to OneDrive, therefore I am embedding the metadata
into fields I know OneDrive will read.

Here's an explanation of the command:
- `-r` recursively process directories
- `-tagsfromfile` copy tags from a file
- `"%d/%F.json"` the source file to copy tags from
  - `%d` - directory
  - `%F` - file name without extension
  - `.json` - JSON file extension
- `"-Title<title"` copy the title from the JSON file to the title field in the photo
- `"-Description<description"` copy the description from the JSON file to the description field in the photo
- `"-DateTimeOriginal<photoTakenTime.timestamp"` copy the photo taken time from the JSON file to the photo taken time field in the photo
- `"-GPSLatitude<geoData.latitude"` copy the latitude from the JSON file to the latitude field in the photo
- `"-GPSLongitude<geoData.longitude"` copy the longitude from the JSON file to the longitude field in the photo
- `"-GPSAltitude<geoData.altitude"` copy the altitude from the JSON file to the altitude field in the photo
- `"-Keywords<people.name"` copy the people name from the JSON file to the keywords field in the photo
- `"-XMP:DeviceType<googlePhotosOrigin.mobileUpload.deviceType"` copy the device type from the JSON file to the device type field in the photo
- `-d "%s"` set the date format to UNIX time
- `-ext "*"` process all file extensions (will ignore non-supported extensions)
- `-ext mp` process MP4 files with the extension `.mp` (some mobile phones keep live photos in MP4 format and `.mp` extension)
- `-overwrite_original` overwrite the original file metadata with the new metadata
- `-progress` show progress
- `--ext json` process only JSON files
- `.` starting processing from the current directory

Here is the command line as a one-liner for easy copy-paste into the command prompt or PowerShell:

```bash
exiftool -r -tagsfromfile "%d/%F.json" "-Title<title" "-Description<description" "-DateTimeOriginal<photoTakenTime.timestamp" "-GPSLatitude<geoData.latitude" "-GPSLongitude<geoData.longitude" "-GPSAltitude<geoData.altitude" "-Keywords<people.name" "-XMP:DeviceType<googlePhotosOrigin.mobileUpload.deviceType" -d "%s" -ext "*" -ext mp -overwrite_original -progress --ext json .
```
The output of the command will display the progress of the operations and any errors and warning that may occur.
If you want to save the output to a file, you can redirect the output to a file using the following command:
(simple adds the `> output.txt` at the end of the command).

```bash
exiftool -r -tagsfromfile "%d/%F.json" "-Title<title" "-Description<description" "-DateTimeOriginal<photoTakenTime.timestamp" "-GPSLatitude<geoData.latitude" "-GPSLongitude<geoData.longitude" "-GPSAltitude<geoData.altitude" "-Keywords<people.name" "-XMP:DeviceType<googlePhotosOrigin.mobileUpload.deviceType" -d "%s" -ext "*" -ext mp -overwrite_original -progress --ext json . > output.txt
```

### Matching Last Modified Date with DateTimeOriginal
```bash
exiftool -r "-FileModifyDate<DateTimeOriginal" -ext "*" .
```

### Deleting the JSON files

After embedding the metadata into the photos, you can delete the JSON files using the following command:

```bash
# windows
del /s *.json

# windows (powershell)
Get-ChildItem -Path "." -Filter *.json -Recurse | Remove-Item -Force

# mac/linux
find . -name "*.json" -type f -delete
```

## Deduplication

Unfortunately, I did not find a good tool that can deduplicate
via the command line for both photos and videos

I found a tool that can deduplicate only photos, and it works only on windows.
- [visipics](https://visipics.info/download/) (windows only - pics only)

As I also needed to dedup videos, so I wrote a script to dedup photos and videos,
and it works very well.
- Notice 1: My script dedups **only** identical photos and videos from content point of view. It does dedups if they have different resolutions or file type.
- Notice 2: If you need to dedup only images, and you're on windows, I recommend using visipics as it is more customizable and faster than a Python script.
- Notice 3: I have used the script for my photos/videos library that contain JPG, PNG, HEIC, MP4, MOV, (MP - MP4 live photos), and it worked very well. Other formats may not work as expected and require additional code.

### Prerequisites
1. Install Python3.6 or higher
```
# windows
winget install Python.Python.3.11

# mac
brew install python

# linux
sudo apt install python3
```
2. Install the required Python packages
```bash
pip install -r requirements.txt

# to choose a specific python version
python3.11 -m pip install -r requirements.txt
```
3. Install ffmpeg (required to extract the first frame of the video to compare with other videos)
```
# windows
winget install Gyan.FFmpeg

# mac
brew install ffmpeg

# linux
sudo apt install ffmpeg
```

### Using the script:
Run the following commands in the root directory of your images/videos library.

1. Make sure to ran exiftool as described in the previous section. The dedup script uses _DateTimeOriginal_ field.
2. Fix extensions (i.e. if the file extension is .png but the header is .jpg, rename to .jpg):
```bash
python3 dedupper.py --fix-extension
```
3. Find duplicates - generates exif_image_info.json and duplications.json file with the duplicates found
```bash
python3 dedupper.py --find-dups
```
4. Select and dry delete duplicates - Chooses which file to keep and updates the duplications.json accordingly.
The selection is the file with the highest resolution, then the file with the earliest DateTimeOriginal, 
then the file with the height quality (currently PNG, you can change it in line 268 of `dedupper.py`)
```bash
python3 dedupper.py --delete-dry
```

5. Generate duplicates.html file to review the duplicates and selected files to keep. The image to **keep** is marked with a red border.
```bash
python3 dedupper.py --write-html
```

6. If you're happy with the results, go on and delete the duplicates:
```bash
python3 dedupper.py --delete
```

