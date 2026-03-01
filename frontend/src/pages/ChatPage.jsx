import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ChatPage.css';

const ChatPage = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate video');
      }

      const data = await response.json();
      setVideoUrl(data.videoUrl);
    } catch (error) {
      console.error('Error generating video:', error);
      alert('Error generating video. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="chat-page">
      <header className="chat-header">
        <button className="back-button" onClick={handleBack}>← Back</button>
        <h1>Create Your Explanation Video</h1>
      </header>

      <div className="chat-container">
        <form onSubmit={handleSubmit} className="prompt-form">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a mathematical or scientific topic you want explained..."
            required
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Video'}
          </button>
        </form>

        {isLoading && (
          <div className="loading-indicator">
            <p>Generating your video explanation...</p>
            <p>This may take a few minutes...</p>
          </div>
        )}

        {videoUrl && (
          <div className="video-result">
            <h3>Your Explanation Video:</h3>
            <video controls src={videoUrl} className="generated-video" />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;