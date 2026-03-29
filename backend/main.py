from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from image_processing import decode_image, preprocess_image, detect_regions
from graph_builder import build_adjacency_graph, adjacency_to_json
from coloring import color_graph
from renderer import render_colored_map, make_debug_region_image, encode_image_to_base64_png

app = FastAPI(title="Map Coloring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"message": "Map Coloring API is running"}


@app.post("/process-map")
async def process_map(file: UploadFile = File(...)):
    try:
        print("ADA started ")
        file_bytes = await file.read()
        image_bgr = decode_image(file_bytes)
        print("ADA decoed image ")
        gray, line_mask = preprocess_image(image_bgr)
        print("ADA process image ")
        region_labels, region_ids = detect_regions(line_mask)
        print("ADA started detected regions")
        if not region_ids:
            raise HTTPException(
                status_code=400,
                detail="No closed regions detected. Use a cleaner map with closed boundaries."
            )

        adjacency = build_adjacency_graph(region_labels, region_ids)
        coloring = color_graph(adjacency, max_colors=4)

        if coloring is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to color graph with 4 colors. Region detection may be noisy."
            )

        colored_map = render_colored_map(image_bgr, line_mask, region_labels, coloring)
        region_debug = make_debug_region_image(region_labels)

        return {
            "num_regions": len(region_ids),
            "adjacency": adjacency_to_json(adjacency),
            "coloring": {str(k): int(v) for k, v in coloring.items()},
            "colored_image_base64": encode_image_to_base64_png(colored_map),
            "debug_regions_base64": encode_image_to_base64_png(region_debug),
            "line_mask_base64": encode_image_to_base64_png(line_mask),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))