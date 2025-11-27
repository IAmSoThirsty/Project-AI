import { useState } from 'react';

function ImageGeneration() {
  const [prompt, setPrompt] = useState('');
  const [generatedImage, _setGeneratedImage] = useState(null);

  const handleGenerate = async () => {
    // TODO: Implement image generation API call
    console.log('Generating image with prompt:', prompt);
  };

  return (
    <div className="dashboard">
      <nav className="sidebar">
        <h2>Project-AI</h2>
        {/* Sidebar navigation */}
      </nav>
      <main className="content">
        <h1>Image Generation</h1>
        <div className="form-group">
          <label>Enter Prompt:</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows="4"
            placeholder="Describe the image you want to generate..."
          />
        </div>
        <button onClick={handleGenerate}>Generate Image</button>
        {generatedImage && (
          <div className="generated-image">
            <img src={generatedImage} alt="Generated" />
          </div>
        )}
      </main>
    </div>
  );
}

export default ImageGeneration;
