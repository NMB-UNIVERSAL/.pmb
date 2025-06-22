import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [converting, setConverting] = useState(false);
  const [convertedFile, setConvertedFile] = useState(null);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef(null);
  const dragAreaRef = useRef(null);

  // Reset progress when starting a new conversion
  useEffect(() => {
    if (converting) {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev < 90) {
            return prev + 10;
          }
          return prev;
        });
      }, 300);
      
      return () => clearInterval(interval);
    } else {
      if (progress > 0 && progress < 100 && convertedFile) {
        setProgress(100);
      }
    }
  }, [converting, convertedFile, progress]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
      setStatus('');
      setConvertedFile(null);
      setProgress(0);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const droppedFile = files[0];
      if (droppedFile.type.startsWith('image/')) {
        setFile(droppedFile);
        setFileName(droppedFile.name);
        setError('');
        setStatus('');
        setConvertedFile(null);
        setProgress(0);
      } else {
        setError('Please select a valid image file.');
      }
    }
  };

  const handleFileButtonClick = () => {
    fileInputRef.current.click();
  };

  const convertToPMB = async () => {
    if (!file) {
      setError('Please select an image file first.');
      return;
    }

    try {
      setConverting(true);
      setStatus('Reading image data...');

      // Create a FileReader to read the image file
      const reader = new FileReader();
      
      reader.onload = async (event) => {
        setStatus('Processing image...');
        
        // Create an Image object to get dimensions and pixel data
        const img = new Image();
        img.src = event.target.result;
        
        img.onload = async () => {
          setStatus('Converting to PMB format...');
          
          // Create a canvas to draw the image and get pixel data
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          canvas.width = img.width;
          canvas.height = img.height;
          
          // Draw the image on the canvas
          ctx.drawImage(img, 0, 0);
          
          // Get the pixel data
          const imageData = ctx.getImageData(0, 0, img.width, img.height).data;
          
          // Generate PMB content
          let pmbContent = '';
          
          // First line: file name without extension
          const baseFileName = fileName.split('.').slice(0, -1).join('.');
          const uniqueId = Math.random().toString(36).substring(2, 10);
          const pmbFileName = `${baseFileName}_${uniqueId}`;
          pmbContent += pmbFileName + '\n';
          
          // Second line: width, height
          pmbContent += `${img.width},${img.height}\n`;
          
          // Process pixel data (RGBA format in imageData, RGB in PMB)
          let x = 0;
          for (let i = 0; i < imageData.length; i += 4) {
            const r = imageData[i];
            const g = imageData[i + 1];
            const b = imageData[i + 2];
            
            // Add pixel data
            pmbContent += `(${r}, ${g}, ${b})`;
            
            x++;
            if (x === img.width) {
              // End of row, add N marker
              pmbContent += 'N\n';
              x = 0;
            } else {
              pmbContent += '\n';
            }
          }
          
          // Create a downloadable blob with the PMB content
          const blob = new Blob([pmbContent], { type: 'text/plain' });
          const pmbFile = new File([blob], `${pmbFileName}.pmb`, { type: 'text/plain' });
          
          // Create a download URL for the PMB file
          const pmbUrl = URL.createObjectURL(pmbFile);
          
          setConvertedFile({
            name: `${pmbFileName}.pmb`,
            url: pmbUrl
          });
          
          setConverting(false);
          setStatus('Conversion complete!');
        };
      };
      
      reader.onerror = () => {
        setError('Failed to read the image file.');
        setConverting(false);
      };
      
      // Read the image file as a data URL
      reader.readAsDataURL(file);
    } catch (error) {
      setError(`Error converting image: ${error.message}`);
      setConverting(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1>PMB Image Converter</h1>
        <p className="app-description">
          Convert any image to our custom PMB format with a single click
        </p>
        
        {error && <div className="alert alert-error">{error}</div>}
        {status && <div className="status">{status}</div>}
        
        {convertedFile && (
          <div className="alert alert-success">
            File successfully converted to PMB format!
            <div>
              <a 
                href={convertedFile.url} 
                download={convertedFile.name}
                className="download-link"
              >
                Download {convertedFile.name}
              </a>
            </div>
          </div>
        )}
        
        <div 
          className={`drag-area ${dragActive ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleFileButtonClick}
          ref={dragAreaRef}
        >
          <div className="icon">
            <span className="material-icons">file_upload</span>
          </div>
          <header>Drag & Drop to Upload File</header>
          <span>OR</span>
          <div className="custom-file-upload">
            Choose an Image
            <input 
              type="file" 
              id="file" 
              onChange={handleFileChange}
              accept="image/*"
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
          </div>
          {fileName && <div className="file-name">Selected: {fileName}</div>}
        </div>
        
        {converting && (
          <div className="conversion-progress">
            <div 
              className="progress-bar"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}
        
        <button 
          className="btn" 
          onClick={convertToPMB} 
          disabled={!file || converting}
        >
          {converting ? (
            <>
              <span>Converting...</span>
              <span className="loading-spinner"></span>
            </>
          ) : (
            'Convert to PMB'
          )}
        </button>
      </div>
    </div>
  );
}

export default App; 