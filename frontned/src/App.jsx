import React, { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function base64ToImageSrc(base64String) {
  return `data:image/png;base64,${base64String}`;
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function handleFileChange(event) {
    const file = event.target.files?.[0];
    setResult(null);
    setError("");

    if (!file) {
      setSelectedFile(null);
      setPreviewUrl("");
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please choose an image first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE}/process-map`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Processing failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Map Coloring Project</h1>
      <p className="subtitle">
        Upload a line graph / region map image. The backend will detect regions,
        build an adjacency graph, apply the 4-color algorithm, and return the colored map.
      </p>

      <form className="upload-box" onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Upload and Process"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {previewUrl && (
        <div className="section">
          <h2>Original Uploaded Image</h2>
          <img className="image" src={previewUrl} alt="Original upload" />
        </div>
      )}

      {result && (
        <>
          <div className="section">
            <h2>Final Colored Map</h2>
            <img
              className="image"
              src={base64ToImageSrc(result.colored_image_base64)}
              alt="Colored map"
            />
          </div>

          <div className="section">
            <h2>Detected Regions Debug View</h2>
            <img
              className="image"
              src={base64ToImageSrc(result.debug_regions_base64)}
              alt="Detected regions"
            />
          </div>

          <div className="section">
            <h2>Boundary Mask</h2>
            <img
              className="image"
              src={base64ToImageSrc(result.line_mask_base64)}
              alt="Boundary mask"
            />
          </div>

          <div className="section">
            <h2>Detected Information</h2>
            <p><strong>Number of regions:</strong> {result.num_regions}</p>
          </div>

          <div className="section">
            <h2>Color Assignment</h2>
            <pre>{JSON.stringify(result.coloring, null, 2)}</pre>
          </div>

          <div className="section">
            <h2>Adjacency Graph</h2>
            <pre>{JSON.stringify(result.adjacency, null, 2)}</pre>
          </div>
        </>
      )}
    </div>
  );
}