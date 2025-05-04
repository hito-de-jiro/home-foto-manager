# 📸 Photo & Video Sorter
A script for automatically sorting photos and videos by shooting date into a `YYYY/MM/` folder structure.<br>
Photos and videos are stored separately — for convenient archiving.
---
## 🔧 Main features

- Determining the shooting date (EXIF for photos or metadata/titles for videos)
- Splitting into photos and videos
- Creating a `Photo/YYYY/MM/` and `Video/YYYY/MM/` folder structure
- Skipping duplicates or renaming for uniqueness

## ▶️ Usage
```bash
    python src/photo_video_manager.py /path/to/incoming_folder /path/to/outgoing_folder 
```
- Add the _--keep_ flag if you want to keep the input files
- 📝 Tip: Test on copies of files first to make sure everything works as expected.

## 📂 Example structure

- Before:
```
/input
  ├── IMG_1234.JPG
  ├── video_2023-08-21.mp4
```
- After:
```
/output
├── Foto/
│   └── 2023/
│       └── 08/
│           └── IMG_1234.JPG
└── Video/
    └── 2023/
        └── 08/
            └── video_2023-08-21.mp4
```
# ⚖️ License
- This project is licensed under the MIT License — feel free to use, modify, and distribute the code.

# 🙌 Collaboration
- Pull requests, issues, and suggestions are always welcome!

