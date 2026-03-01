import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Code, Cpu, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Starfield from '../components/Starfield';
import architectureImg from '../assets/diagram.png'; // Update with your actual filename
import sampleVid from '../assets/imagio_video.mp4'; // Update with your filename
import { useRef, useState } from 'react';
import { Play, Pause } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();

  const videoRef = useRef(null);
const [isPlaying, setIsPlaying] = useState(false);

  const handleTogglePlay = () => {
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };


  return (
    <div className="app-container">
      <Starfield />

      <nav className="navbar">
        <div className="max-w-7xl nav-content">
          <div className="nav-logo">IMAGIO</div>
          <div className="nav-links">
            <a href="#about" className="nav-link">About</a>
            <a href="#features" className="nav-link">Features</a>
            <a href="#how-it-works" className="nav-link">How it Works</a>
          </div>
          <button
            onClick={() => navigate('/chat')}
            className="btn-primary"
          >
            Get Started
          </button>
        </div>
      </nav>

      <section className="hero-section">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="hero-title"
        >
          IMAGIO
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="hero-subtitle"
        >
          Don't just read it, <span className="highlight-text">visualize it.</span>
        </motion.p>

        <motion.div
  initial={{ scale: 0.9, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  transition={{ delay: 0.4 }}
  className="video-preview relative overflow-hidden rounded-xl border border-white/10 cursor-pointer group"
  onClick={handleTogglePlay}
>
  {/* Video Element (Removed autoPlay) */}
  <video
    ref={videoRef}
    src={sampleVid}
    loop
    muted
    playsInline
    className="absolute inset-0 w-full h-full object-cover"
  />

  {/* Overlay: Fades out when playing */}
  <div className={`video-overlay absolute inset-0 bg-black/50 z-10 transition-opacity duration-300 ${isPlaying ? 'opacity-0' : 'opacity-100'}`} />
  
  <div className="relative z-20 flex flex-col items-center justify-center h-full">
    {/* Dynamic Icon: Switches between Play and Pause */}
    <motion.div 
      whileHover={{ scale: 1.1 }}
      className={`p-5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 transition-opacity ${isPlaying ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'}`}
    >
      {isPlaying ? <Pause size={48} className="text-white" /> : <Play size={48} className="text-white fill-current" />}
    </motion.div>
    
    <div className={`video-label-container mt-auto pb-6 px-6 w-full text-left transition-transform ${isPlaying ? 'translate-y-4 opacity-0' : 'translate-y-0 opacity-100'}`}>
      <p className="video-label text-xs uppercase tracking-widest text-blue-400 font-bold">Sample Render</p>
      <p className="video-title text-xl text-white font-medium">"The Black Hole Event Horizon"</p>
    </div>
  </div>
</motion.div>
      </section>

      <section id="features" className="max-w-7xl section-container">
        <h2 className="section-heading">Powerful Features</h2>
        <div className="features-grid">
          {[
            {
              icon: <Sparkles size={32} />,
              title: "AI Scripter",
              desc: "Our models weave dry technical facts into compelling narratives."
            },
            {
              icon: <Code size={32} />,
              title: "Manim Core",
              desc: "Industrial-grade mathematical animations via 3Blue1Brown's engine."
            },
            {
              icon: <Cpu size={32} />,
              title: "Auto-Sync",
              desc: "No manual editing. Voice and visuals merge in the cloud."
            },
            {
              icon: <Zap size={32} />,
              title: "Lightning Fast",
              desc: "Get your complete visualization rendered within 20 seconds."
            }
          ].map((feat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i }}
              viewport={{ once: true }}
              className="feature-card glass-panel-animated"
            >
              <div className="feature-icon-container">{feat.icon}</div>
              <h3 className="feature-title">{feat.title}</h3>
              <p className="feature-desc">{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section id="how-it-works" className="max-w-7xl section-container">
        <h2 className="section-heading">How It Works</h2>
        <div className="how-it-works-content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flow-diagram-container glass-panel-animated"
          >
            <h3 className="sub-heading text-center mb-4">Architecture Flow</h3>
            <div className="architecture-img-wrapper">
              <img
                src={architectureImg}
                alt="Imagio Architecture Flow"
                className="architecture-img"
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="youtube-container glass-panel-animated"
          >
            <h3 className="sub-heading text-center mb-4">Project Overview</h3>
            <div className="video-player-wrapper">
              <iframe
                width="100%"
                height="100%"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ?si=placeholder"
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerPolicy="strict-origin-when-cross-origin"
                allowFullScreen
                className="youtube-iframe"
              ></iframe>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;