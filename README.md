<div align="center">
  <a href="https://oliverbarreto.com">
    <img src="https://www.oliverbarreto.com/images/site-logo.png" />
  </a>
</div>
</br>
</br>
<div align="center">
  <h1>🎧 Podcastarr | When Podcast killed the Youtube Video Start </h1>
  <strong>Self-hosted application that allows creating a personal podcast channel with episodes created extracting audio from Youtube videos</strong>
  </br>
  </br>
  <p>Created with ❤️ by Oliver Barreto</p>
</div>

</br>
</br>

# YouTube Audio Downloader - PodcastARR Backend

This the backend for the YouTube Audio Downloader.

It is built using FastAPI and Docker for deployment.

## Introduction

The backend is in charge of downloading the audio from the Youtube videos and storing it in the database.

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [PytubeFix](https://github.com/jdevera/pytubefix)
- [SQLite](https://www.sqlite.org/)
- [LogGuru](https://loguru.readthedocs.io/en/stable/)
- [Docker](https://www.docker.com/)

## Features:

- API to download the audio from the Youtube videos and store it in the database
- API to get the list of podcast channels available in the database
- API to get the status of a download (Pending, Completed, Failed)

### Prerequisites for local development

Make sure you have the following installed on your machine:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/)
- [SQLite](https://www.sqlite.org/)
- [Docker](https://www.docker.com/)

You also need to have a virtual environment with at least Python 3.10 installed.

To create a virtual environment, you can use the following command:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

If you prefer to use Conda, you can use the following command:

```bash
conda create -n podcastarr python=3.10  #to create the virtual environment
conda activate podcastarr               # to activate the virtual environment
conda deactivate                        # to deactivate the virtual environment
```

### Local development

1. Clone the gith repository

```bash
git clone https://github.com/oliverbarreto/podcastarr-api-poc.git
cd podcastarr-api-poc
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Setup Variables by adding `.env` in the root directory of the project using the template 'env.example' file with database connection string:

```yaml
# For local development
DATABASE_PATH=./data/downloads.db
DOWNLOADS_PATH=./downloads
```

4. Run migrations

```bash
python -m app/migrations/add_video_id.py
python -m app/migrations/add_videoname.py
```

6. First, run the FastAPI development server locally:

```bash
 uvicorn app.main:app --reload
```

6. Open [http://localhost:3000/docs](http://localhost:3000/docs) with your browser to access the API Swagger Documentation and test the endpoints.

## Deploy with Docker

0. Copy the contents of the project to a folder in your server

1. Modify `.env` file with `DATABASE_URL` with DB location for prisma client for Docker location:

<!-- ```bash
DATABASE_URL="file:/app/prisma/dev.db"
``` -->

2. Run Docker compose file to run the project:

```bash
docker compose up -d --build
```

> NOT USED:
> Maybe you want to seed the database: Seed the database using the script in `prisma/seed.ts` > `docker exec -it nextjs-app-dev npm run seed`
