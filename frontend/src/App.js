import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jsonData, setJsonData] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select or drop a file.");
    const formData = new FormData();
    formData.append('file', selectedFile);
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/extract', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Upload failed");
      setJsonData(result);
    } catch (err) {
      console.error(err);
      setJsonData({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <h1>📄 Smart File Extractor</h1>

      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <p>Drag & Drop your PDF or Image here</p>
        <input type="file" onChange={handleFileChange} />
        <span>or click to select</span>
      </div>

      {selectedFile && (
        <p className="filename">Selected: {selectedFile.name}</p>
      )}

      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Extracting...' : 'Upload & Extract'}
      </button>

      {jsonData && (
        <>
          <button onClick={handleDownload} className="download-btn">
            📥 Download JSON
          </button>
        </>
      )}

      <h2>🧠 Extracted JSON:</h2>
      <pre className="json-output">
        {jsonData ? JSON.stringify(jsonData, null, 2) : 'No data yet.'}
      </pre>
    </div>
  );
}

export default App;
