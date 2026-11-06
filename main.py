from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="The Media Shelf API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only; restrict for production
    allow_methods=["*"],
    allow_headers=["*"],
)

KINO_URL = "https://api.kinocheck.com"

@app.get("/")
def home():
    return {
        "message": "Welcome to The Media Shelf API!",
        "status": "success"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy"}


def get_trailer(media_type: str, tmdb_id: int, language: str):
    endpoint = "movies" if media_type == "movie" else "shows"

    try:
        response = requests.get(
            f"{KINO_URL}/{endpoint}",
            params={
                "tmdb_id": tmdb_id,
                "language": language
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to KinoCheck API"
        )

    trailer = data.get("trailer")

    if not trailer or not trailer.get("youtube_video_id"):
        raise HTTPException(
            status_code=404,
            detail="No trailer found for this title"
        )

    video_id = trailer["youtube_video_id"]

    return {
        "title": data.get("title"),
        "tmdb_id": tmdb_id,
        "language": language,
        "trailer": {
            "title": trailer.get("title"),
            "youtube_video_id": video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "embed_url": f"https://www.youtube.com/embed/{video_id}",
            "thumbnail": trailer.get("youtube_thumbnail")
        },
        "source": "KinoCheck"
    }


@app.get("/api/movies/{tmdb_id}/trailer")
def movie_trailer(tmdb_id: int, language: str = "en"):
    return get_trailer("movie", tmdb_id, language)


@app.get("/api/shows/{tmdb_id}/trailer")
def show_trailer(tmdb_id: int, language: str = "en"):
    return get_trailer("show", tmdb_id, language)