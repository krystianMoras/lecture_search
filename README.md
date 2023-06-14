# Lecture search

Browse course materials (pdfs, videos) with help of semantic search.

## Instructions

Git clone this repository, cd to it, run

```sh
pipenv install
pipenv shell
```

### Download and process files

1. Download all files from your courses, organize into this structure
```
courses/
├─ Course1/
│  ├─ Lecture1/
│  │  ├─ lecture_video.mp4
│  │  ├─ lecture_slides.pdf
├─ Course2/
...
```
To help with downloading videos, use scripts/download_yt.py

1.1. Transcribe videos with scripts/transcribe.py or if you have .srt files simply put them in the same paths as your videos, the names should match e.g. "lecture_1.mp4" and "lecture_1.srt"

    !!! More information about the scripts and how to run them available in scripts/README.MD !!! 

2. Calculate embeddings and index them in db

```sh
python scripts/process_courses.py --course_dir "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses"
```

This will create cozo.db file in your courses_dir that contains all embeddings and tables! Do not delete unless you want to reset.

3. Run the app

```sh
python src/lecture_search/app/main.py --courses_dir "C:\Users\kryst\Documents\Artificial Intelligence\Artificial Intelligence - sem6\courses"
```

4. Bonus - phrase extraction and note generation

for extracting phrases run ./scripts/extract_phrases.py

These extracted phrases could be used for:
- highlighting #todo
- linking #todo
- finding good concepts to generate notes for (see below)

Generating notes script is incomplete - draw inspiration from ./notebooks, however I ran different version of it for my own purposes, here is timelapse of 430 notes for Decision Analysis course being generated in obsidian graph view -> https://www.youtube.com/watch?v=i6B8CVhk0Rk

If you are AI student at PUT and would like to see the notes, dm me.

### Some screenshots

![obraz](https://github.com/krystianMoras/lecture_search/assets/72855171/ea7f4e93-e44d-4ca1-b3cb-4b4004e0b3fd)
![obraz](https://github.com/krystianMoras/lecture_search/assets/72855171/910ac2df-9004-4692-8447-407aaac7f5db)

