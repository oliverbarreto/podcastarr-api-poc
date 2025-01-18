# Product Requirements Document (PRD)

Product Name: YouTube Audio Downloader Backend

Version:1.0

# 1. Overview

## 1.1 Purpose

The YouTube Audio Downloader is an application designed to allow users to download the best-quality audio from YouTube videos. Users will provide a YouTube URL through a web-based interface, and the backend will process the request and make the audio file available for download.

## 1.2 Objectives

Provide a simple, intuitive interface for users to download YouTube audio.

Ensure high performance and reliability for processing downloads.

Offer publicly accessible storage for downloaded audio files.

## 1.3 Target Audience

Content creators who need audio tracks.

Casual users who want to download audio for offline use.

Individuals seeking audio-only versions of educational content or podcasts.

# 2. Features

## 2.1 Core Features

Frontend (Next.js 15):

Input field for users to paste YouTube URLs.

Button to initiate the download process.

Display of download progress and status (e.g., success or error).

List of previously downloaded files (publicly accessible).

Backend (Python, FastAPI):

Validate the provided YouTube URL.

Use the pytubefix library to download the best-quality audio.

Store the downloaded audio file in a local or cloud-based file system.

Provide APIs for:

Submitting a YouTube URL for processing.

Fetching the status of a download.

Listing publicly available files.

## 2.2 Public File Access

Make downloaded files accessible through a unique public URL.

Implement directory listing for browsing downloadable files.

## 2.3 Error Handling

Handle invalid URLs or unsupported formats gracefully.

Notify users of errors (e.g., video unavailable, network issues).

Log errors for backend troubleshooting.

## 2.4 Security

Rate limiting to prevent abuse.

Optional CAPTCHA for user verification.

Sanitize input to prevent injection attacks.

## 2.5 Performance

Use asynchronous processing for downloads to handle multiple requests simultaneously.

Optimize storage and retrieval of audio files for fast access.

## 2.6 Logging

Use the loguru library for logging.
This implementation:

- Creates a centralized logging configuration
- Logs to both console and file with different levels
- Includes rotation and retention policies for log files
- Adds structured logging with timestamps and module information
- Tracks all important events and errors
- Uses different log levels appropriately (DEBUG, INFO, WARNING, ERROR)

The logs will be stored in the logs directory with daily rotation and 7-day retention. You'll see:

- All requests and their outcomes
- Download progress and completion
- Any errors that occur during processing
- File management operations
- Application startup and initialization

# 3. Technical Requirements

## 3.1 Frontend

Framework: Next.js 15.

Pages:

- Home Page: Input for YouTube URL and submission button.
- Downloads Page: List of public audio files.
- Error/Status Page: Display of download progress/errors.
- Deployment: Dockerized container.

## 3.2 Backend

Framework: FastAPI.

Libraries:

- pytubefix for downloading audio.
- uvicorn for serving the application.
- asyncio for handling concurrent requests.

Deployment: Dockerized container.

## 3.3 Storage

Local storage for audio files initially.

Future scalability to cloud storage (e.g., AWS S3).

## 3.4 Database

SQLite for managing:

- User download requests.
- Metadata of downloaded files (e.g., filename, URL, timestamp).

## 3.5 APIs

- POST /download: Accepts a YouTube URL and initiates download.
- GET /status/{id}: Returns the status of a specific download request.
- GET /files: Lists publicly available audio files.

## 3.6 Migrations

Migrations are run automatically when the application starts.

Migrations are stored in the `app/migrations` directory.

## 3.7 Logging

Logging is implemented using the `loguru` library.

## 3.8 Environment Variables

Environment variables are stored in the `.env` file.

## 3.9 Serve audio files from a public URL with statistics

The FastAPI app will shares audio files using a public route and will store the access information in a database while serving audio files from the local public folder is a great approach.

Here’s how you can implement it:

- Database Table: Use a database table to track file access counts.
- Static Files Serving: Serve the files from the public directory.
- Increment Count: Each time a file is accessed, update the database.

### How It Works

- Static File Serving: Files are stored in the public folder, and the FileResponse class serves them directly.
- Database Tracking: Every time an audio file is accessed, the app checks the file_access table.
  - If the file exists, it increments the count column.
  - If it doesn’t exist, it creates a new entry for that file.
- Error Handling: The app checks if the file exists in the public directory before serving it. If the file is missing, it raises a 404 error.
- Statistics Route: The /stats route retrieves and returns the access counts for all files in the database.

### Directory Structure

Ensure your project is structured like this:

```bash
/project
│
├── main.py          # FastAPI app
├── public/          # Directory containing audio files
│   ├── file1.mp3
│   ├── file2.mp3
│   └── ...
├── file_access.db   # SQLite database
└── requirements.txt # Python dependencies
```

### Advanced Features for statistics

Here’s the updated implementation that includes timestamps for tracking access, file type/size validation, and pagination for the /stats route.

- Timestamps: Track when files are accessed by adding a last_accessed column with a datetime type.
- File Size Validation: Validate file types or sizes to ensure only appropriate assets are served.
- Pagination in /stats: Add pagination to handle large datasets.

How it works:

1. Track Last Access Timestamp
   - Added a last_accessed column to the FileAccess table.
   - Automatically updates the last_accessed field with the current UTC timestamp whenever a file is accessed.
2. File Validation
   - Ensures that only audio files (mp3, wav, ogg, flac) are served.
   - Limits file size to 10 MB (adjustable by changing the max_file_size_mb variable).
3. Pagination for /stats
   - Added skip (default 0) and limit (default 10) query parameters to the /stats endpoint.
   - The response includes paginated data along with metadata:
     - total: Total number of files tracked in the database.
     - skip and limit: Indicate the current slice of data.

Example Usage:

- Serve Audio File:

  - Request: `GET /audio/file1.mp3`
  - Response: Serves the file if it exists, is an audio file, and is within size limits.

- Get File Access Statistics:

  - Request: `GET /stats?skip=0&limit=5`
  - Response (example):

```json
{
  "data": [
    {
      "filename": "file1.mp3",
      "count": 12,
      "last_accessed": "2025-01-16T15:30:00"
    },
    {
      "filename": "file2.wav",
      "count": 5,
      "last_accessed": "2025-01-16T14:00:00"
    }
  ],
  "total": 20,
  "skip": 0,
  "limit": 5
}
```

## 3.10 Prepare Model for Production before integration with Frontend

Acutally we have a model for podcast episodes, but we need to prepare it for production before integration with Frontend.

Please do not use any ORM like SQLAlchemy. Use only raw SQLite.

Current Models where we have two tables:

- downloads
- file_access

We need to create a new table for podcast episodes from scratch.

- New table named: episodes

- We don not need to migrate any data.
- We will create a new table with the whole data needed and forget the previous table and data.
- We need to add the fields fo the table "file_access" in the new "episodes" table to track the access to the audio files.
- We need to modify the structure so it has:

### EPISODES:

Needed for the frontend functionality:

- id: UUID - Primary Key
- url: string (the same url passed to download the audio function)
- createdAt
- updatedAt
- status: string (pending, downloaded, error)
- tags: str (not used for iTunes XML)

Needed for the statistics feature:

- count: int (number of times the audio file has been accessed)
- lastaccessedAt: datetime (timestamp of the last time the audio file was accessed)

Needed for the backend functionality to create the iTunes RSS feed:

- videoid: string (extracted from the youtube video url passed to download the audio function, and used to create the id for the episode. There cannot be two episodes with the same videoid in the same podcast channel/feed. It is used to create the id for the episode in the iTunes RSS feed with a unique identifier for the podcast channel eg: "com.uuebcast.uuid.{}".format(episode.videoid)" vs UUID)
- title (Needed for generating XML iTunes feed)
- subtitle (Needed for generating XML iTunes feed)
- summary (Needed for generating XML iTunes feed)
- position: int (Needed for generating XML iTunes feed)
- imageurl (Needed for generating XML iTunes feed - it is named "image" in the object to create the iTunes RSS feed)
- publishedAt: datetime (Needed for generating XML iTunes feed - named "publication_date" in the object to create the iTunes RSS feed: `pytz.utc.localize(episode.date_created)`)
- explicit: Bool (Needed for generating XML iTunes feed)

Needed to create the Media object for every episode in the iTunes RSS feed:

- mediaurl: string (Needed for generating XML iTunes feed - mediaurl eg "http://localhost:8000/audio/file1.mp3 or http://server.com/audio/file1.mp3")
- mediasize: int (Needed for generating XML iTunes feed - used when creating media object)

Needed to create other fields for the episode for the iTunes RSS feed:

- author (Needed for generating XML iTunes feed. The "Subtitle" of the episode is created with the author ,eg: "by Rene Ritchie published on Tuesday, June 8 2021 at 11:52:27")
- keywords: string (Needed for generating XML iTunes feed. The "keywords" are added to the summary of the episode)

Other stored data of the episode extracted from the youtube video library:

- mediaduration: int (Not used for iTunes XML)
- medialength: int (Not used for iTunes XML)

### CHANNEL:

- id UUID - primary_key
- name String - index, unique=False
- description String
- websiteurl String
- explicit Boolean
- imageurl String
- copyright String
- language String
- feed_url String
- category String
- authors String
- authors_email String
- owner String
- owner_email String
- createdAt
- updatedAt

## 3.11 Future Intergration with Frontend

Integrate with Frontend: Build a frontend (e.g., in NextJS) to download files, show current downloaded fieles, use status to provide feedback to the user in the fronten UI, and display stats of file access.

## 3.12 Additional Features

- Preloading Database: Preload database entries with initial file metadata (e.g., on app startup).
- Rate Limiting
- Optional CAPTCHA for user verification
- Sanitize input to prevent injection attacks
- Enhance Filtering: Add query parameters to filter by file name, date ranges, or access counts.

# 4. Non-Functional Requirements

## 4.1 Performance

Handle 10 concurrent download requests with minimal latency.

## 4.2 Scalability

Modular architecture to allow for future integration with cloud services and additional features.

## 4.3 Security

Ensure compliance with YouTube’s terms of service.

Encrypt sensitive data in transit.

## 4.4 Usability

Intuitive UI with clear feedback on actions.

Mobile-responsive design.

## 4.5 Maintainability

Clear documentation for APIs and deployment.

Modular codebase for ease of updates and troubleshooting.

# Why this architecture?

## Advantages of Next.js for the Frontend:

### Server-Side Rendering (SSR):

Next.js offers SSR, which can improve SEO and initial load performance for your app.
This is beneficial if you plan to index pages where users can publicly access files or interact with the app.

### API Routes:

Next.js can handle simple API endpoints directly, but in your case, having Python for more complex backend logic is more powerful.

### Modern Features:

With React under the hood, Next.js provides access to a robust ecosystem and modern UI development practices.
Features like app router in Next.js 15 simplify client-server interactions.

### Static and Dynamic Pages:

Next.js allows you to create both static and dynamic pages easily, which is useful for displaying publicly accessible files or user-specific data.

### Performance Optimizations:

Built-in optimizations, such as image handling and bundling, improve the app's performance.

## Advantages of Python for the Backend:

### Powerful Libraries:

Python has libraries like pytubefix for downloading YouTube videos and many others for tasks like file handling and database interactions.

⚠ IMPORTANT NOTE: PitubeFix DOES NOT WORK for downloading audio of Kids videos from YouTube. TODO: find a way to download audio of Kids videos from YouTube. Maybe using a different library or loggin in.

### FastAPI:

Using FastAPI ensures you get a high-performance backend with automatic documentation and great developer experience.
It works well with asynchronous tasks, which are helpful for handling video/audio downloads.

### Asynchronous Capabilities:

Python allows for asynchronous handling, ideal for downloading large files without blocking other requests.

### Flexibility:

Python’s versatility lets you easily integrate databases, file storage systems, and other services.

## How They Complement Each Other:

### Separation of Concerns:

The backend focuses solely on handling API requests, business logic, and file processing, while the frontend handles the user interface.
This modular approach is clean and makes scaling easier.

### Communication:

The frontend can interact with the backend through RESTful APIs or even WebSocket connections for real-time updates (e.g., progress bars for downloads).

## Technology Interoperability:

Next.js (Node.js-based) and Python communicate seamlessly over HTTP/HTTPS APIs.

## Potential Challenges:

### Deployment:

Deploying two different stacks might require extra setup, like managing environments for Python (e.g., Docker) and Node.js.
Tools like Vercel (for Next.js) and AWS, Heroku, or Fly.io (for Python) can simplify deployment.

### Latency:

A small overhead may arise if frontend-backend communication occurs over the network, but it's negligible for most applications.

## When Is This Not Ideal?

If your app’s frontend is very simple and doesn’t need React features, you could consider Python frameworks like Flask or Django for both frontend and backend to simplify the stack.
For very high-performance apps, merging the frontend and backend to reduce network overhead might be better (though this sacrifices modularity).

## Conclusion:

The choice of Next.js for the frontend and Python for the backend is excellent for modularity, developer experience, and leveraging the strengths of both technologies.

If you're confident in managing the deployment and interactions between the two, it's a modern and scalable stack.
