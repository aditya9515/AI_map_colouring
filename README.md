# Map Coloring Project

A full-stack web app that takes a line-drawn map or region diagram, detects the
closed regions, builds an adjacency graph, and applies a four-color graph
coloring algorithm. The result is returned as a colored map along with debug
views for detected regions, boundaries, adjacency data, and color assignments.

## Features

- Upload an image from the browser.
- Detect closed regions with OpenCV image preprocessing and connected
  components.
- Build an adjacency graph from neighboring regions.
- Color the graph with up to four colors using a backtracking solver.
- Display the final colored map, detected-region debug view, boundary mask,
  adjacency graph, and color assignment JSON.
- Run locally with Python/Node.js or with Docker Compose.

## Tech Stack

- Backend: FastAPI, Uvicorn, OpenCV, NumPy
- Frontend: React 18, Vite
- Packaging: `uv`, `requirements.txt`, Docker, Docker Compose

## Project Structure

```text
.
|-- main.py                    # FastAPI app and /process-map endpoint
|-- backend/
|   |-- image_processing.py    # Decode, preprocess, and detect regions
|   |-- graph_builder.py       # Build adjacency graph from region labels
|   |-- coloring.py            # Four-color backtracking solver
|   `-- renderer.py            # Render colored/debug images as PNG/base64
|-- frontned/                  # React/Vite frontend
|   |-- src/App.jsx            # Upload UI and result rendering
|   |-- package.json
|   `-- Dockerfile
|-- Dockerfile                 # Backend Docker image
|-- docker-compose.yml         # Backend + frontend services
|-- pyproject.toml             # Python project metadata
|-- requirements.txt           # Locked Python dependencies
|-- image.png                  # Sample/local test image
`-- validate.py                # Local coloring validation script
```

Note: the frontend directory is currently named `frontned`, so commands use that
spelling.

## How It Works

1. The frontend sends an uploaded image to `POST /process-map`.
2. The backend decodes the file into an OpenCV BGR image.
3. The image is converted to grayscale, blurred, edge-detected, dilated, and
   morphologically closed to create a boundary mask.
4. Enclosed regions are found with flood fill and connected components.
5. Region labels are converted into an adjacency graph.
6. The graph is colored with a four-color backtracking algorithm.
7. The API returns base64 PNG images and JSON metadata to the frontend.

## Run With Docker Compose

From the project root:

```powershell
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000
- API docs: http://localhost:8000/docs

## Run Locally

### Backend

Use Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at http://127.0.0.1:8000.

### Frontend

Open a second terminal:

```powershell
cd frontned
npm install
npm run dev
```

The frontend will be available at http://localhost:5173.

The React app currently calls the backend at `http://127.0.0.1:8000`.

## API

### `GET /`

Returns a simple health-check response:

```json
{
  "message": "Map Coloring API is running"
}
```

### `POST /process-map`

Accepts a multipart image upload using the form field name `file`.

Example with PowerShell:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/process-map" -F "file=@image.png"
```

Successful responses include:

- `num_regions`: number of detected closed regions
- `adjacency`: adjacency graph as JSON
- `coloring`: region-to-color assignment
- `colored_image_base64`: final colored map PNG
- `debug_regions_base64`: debug image showing detected regions
- `line_mask_base64`: boundary mask PNG

## Image Input Tips

For best results, use images with:

- Clear, high-contrast boundaries.
- Closed regions with no gaps in the lines.
- Minimal noise, shading, or textured backgrounds.
- Regions large enough to pass the current minimum area filter.

If the API cannot detect closed regions, it returns a `400` response asking for a
cleaner map with closed boundaries.

## Validation

The repository includes a local validation script that reads `image.png`, runs
the preprocessing, graph construction, and coloring pipeline, then reports
whether the coloring is valid:

```powershell
python validate.py
```

During region detection, `backend/image_processing.py` writes the current label
matrix to `output.txt` for debugging.
