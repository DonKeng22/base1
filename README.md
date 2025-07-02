# Project Odysseus Hockey Analytics

## Overview
This project is an open-source video analytics pipeline for hockey games, leveraging only open source components and libraries. It provides tools for downloading, processing, and analyzing hockey video data, with a focus on reproducibility and extensibility.

## Architecture
- **Database**: PostgreSQL with PostGIS extension (open source)
- **Processing Environment**: PyTorch (open source, BSD), OpenCV (open source, Apache 2.0), PySceneDetect (open source, MIT), ffmpeg (open source, LGPL/GPL)
- **Orchestration**: Docker Compose (open source, Apache 2.0)
- **Scripts**: Python (open source, PSF)

## Directory Structure
- `scripts/`: Python scripts for database setup and video processing
- `data/`: Raw and processed video data
- `logs/`: Log files and test results
- `ReadMe_docs/`: Additional documentation and plans
- `docker-compose.yml`: Service orchestration

## Quickstart
1. **Clone the repository**
2. **Start services**:
   ```sh
   docker-compose up -d
   ```
3. **Initialize the database**:
   ```sh
   docker-compose exec dev_env python scripts/01_setup_database.py
   ```
4. **Acquire and process videos**:
   ```sh
   docker-compose exec dev_env python scripts/02_acquire_and_process.py
   ```

## Open Source Components Used
- [PostgreSQL](https://www.postgresql.org/) (PostgreSQL License)
- [PostGIS](https://postgis.net/) (GPL)
- [PyTorch](https://pytorch.org/) (BSD)
- [OpenCV](https://opencv.org/) (Apache 2.0)
- [PySceneDetect](https://pyscenedetect.readthedocs.io/) (MIT)
- [ffmpeg](https://ffmpeg.org/) (LGPL/GPL)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (Unlicense)
- [Docker](https://www.docker.com/) (Apache 2.0)

## Documentation
See the `ReadMe_docs/` folder for detailed plans and research notes.

## License
This project will be released under the MIT License. See `LICENSE` for details. 