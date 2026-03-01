import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/chat');
  };

  return (
    <div className="home-page">
      <header className="hero-section">
        <div className="stars"></div>
        <h1 className="title">Imagio</h1>
        <p className="slogan">Don't just read it, visualize it.</p>
        <button className="get-started-button" onClick={handleGetStarted}>
          Get Started
        </button>
      </header>

      <section className="demo-section">
        <h2>See it in action</h2>
        <div className="demo-video-placeholder">
          <p>Demo video will appear here</p>
        </div>
      </section>

      <section className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Easy to Use</h3>
            <p>Simply input your topic and get a video explanation.</p>
          </div>
          <div className="feature-card">
            <h3>Visual Learning</h3>
            <p>Understand complex concepts through visualizations.</p>
          </div>
          <div className="feature-card">
            <h3>Fast Results</h3>
            <p>Get your explanation video in minutes.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;