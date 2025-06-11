import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State management
  const [file, setFile] = useState(null);
  const [position, setPosition] = useState('');
  const [mustHave, setMustHave] = useState(['']);
  const [niceToHave, setNiceToHave] = useState(['']);
  const [processing, setProcessing] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);

  // Handle file drop
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.name.toLowerCase().endsWith('.zip')) {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please upload a ZIP file');
    }
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile?.name.toLowerCase().endsWith('.zip')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please upload a ZIP file');
    }
  };

  // Handle requirement list changes
  const handleRequirementChange = (index, value, type) => {
    if (type === 'must') {
      const newMustHave = [...mustHave];
      newMustHave[index] = value;
      setMustHave(newMustHave);
    } else {
      const newNiceToHave = [...niceToHave];
      newNiceToHave[index] = value;
      setNiceToHave(newNiceToHave);
    }
  };

  // Add new requirement field
  const addRequirement = (type) => {
    if (type === 'must') {
      setMustHave([...mustHave, '']);
    } else {
      setNiceToHave([...niceToHave, '']);
    }
  };

  // Remove requirement field
  const removeRequirement = (index, type) => {
    if (type === 'must') {
      const newMustHave = mustHave.filter((_, i) => i !== index);
      setMustHave(newMustHave.length ? newMustHave : ['']);
    } else {
      const newNiceToHave = niceToHave.filter((_, i) => i !== index);
      setNiceToHave(newNiceToHave.length ? newNiceToHave : ['']);
    }
  };

  // Start CV screening
  const handleSubmit = async () => {
    try {
      setProcessing(true);
      setError(null);

      const formData = new FormData();
      formData.append('zip_file', file);
      formData.append('role', JSON.stringify({
        position,
        must_have: mustHave.filter(Boolean),
        nice_to_have: niceToHave.filter(Boolean)
      }));

      const response = await fetch('http://localhost:7444/screen-cvs', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to start processing');
      }

      const data = await response.json();
      setTaskId(data.task_id);

    } catch (err) {
      setError(err.message);
      setProcessing(false);
    }
  };

  // Check task status
  useEffect(() => {
    let interval;
    if (taskId) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:7444/task-status/${taskId}`);
          const data = await response.json();

          setProgress(data);

          if (data.status === 'COMPLETED') {
            setProcessing(false);
            clearInterval(interval);
            window.location.href = `http://localhost:7444/download-result/${taskId}`;
          } else if (data.status === 'FAILED') {
            setProcessing(false);
            setError(data.error);
            clearInterval(interval);
          }

        } catch (err) {
          setError(err.message);
          setProcessing(false);
          clearInterval(interval);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 CV Screener</h1>
      </header>

      <main className="App-main">
        {/* File upload section */}
        <section className="upload-section">
          <div
            className="dropzone"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".zip"
              id="file-input"
            />
            <label htmlFor="file-input">
              {file ? file.name : 'Drop ZIP file here or click to upload'}
            </label>
          </div>
        </section>

        {/* Job details section */}
        <section className="job-details">
          <div className="input-group">
            <label>Position Title:</label>
            <input
              type="text"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              placeholder="e.g., Senior Software Engineer"
            />
          </div>

          {/* Must-have requirements */}
          <div className="requirements-group">
            <h3>Must-Have Requirements:</h3>
            {mustHave.map((req, index) => (
              <div key={`must-${index}`} className="requirement-input">
                <input
                  type="text"
                  value={req}
                  onChange={(e) => handleRequirementChange(index, e.target.value, 'must')}
                  placeholder="e.g., Python programming"
                />
                <button onClick={() => removeRequirement(index, 'must')}>×</button>
              </div>
            ))}
            <button onClick={() => addRequirement('must')}>+ Add Requirement</button>
          </div>

          {/* Nice-to-have requirements */}
          <div className="requirements-group">
            <h3>Nice-to-Have Requirements:</h3>
            {niceToHave.map((req, index) => (
              <div key={`nice-${index}`} className="requirement-input">
                <input
                  type="text"
                  value={req}
                  onChange={(e) => handleRequirementChange(index, e.target.value, 'nice')}
                  placeholder="e.g., Docker experience"
                />
                <button onClick={() => removeRequirement(index, 'nice')}>×</button>
              </div>
            ))}
            <button onClick={() => addRequirement('nice')}>+ Add Requirement</button>
          </div>
        </section>

        {/* Action buttons */}
        <section className="actions">
          <button
            className="submit-button"
            onClick={handleSubmit}
            disabled={!file || !position || processing}
          >
            {processing ? 'Processing...' : 'Start CV Screening'}
          </button>
        </section>

        {/* Progress indicator */}
        {processing && progress && (
          <section className="progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress.progress.percentage}%` }}
              />
            </div>
            <p>{progress.progress.status}</p>
            <p>
              Processed: {progress.progress.processed} / {progress.progress.total} CVs
            </p>
          </section>
        )}

        {/* Error display */}
        {error && (
          <section className="error">
            <p>{error}</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App; 