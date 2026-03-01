import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, ArrowLeft, AlertCircle, Download, Globe } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Starfield from '../components/Starfield';

const API_BASE = 'http://localhost:8000';

// Pipeline can take 1-5 minutes — set a generous timeout.
// AbortController cancels the fetch cleanly if the user navigates away.
const FETCH_TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes

const LANGUAGES = [
  { code: 'en', label: 'English',  flag: '🇺🇸' },
  { code: 'es', label: 'Español',  flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'hi', label: 'हिन्दी',   flag: '🇮🇳' },
];

const ChatPage = () => {
  const [prompt, setPrompt]             = useState('');
  const [language, setLanguage]         = useState('en');
  const [appState, setAppState]         = useState('idle'); // 'idle' | 'generating' | 'completed' | 'error'
  const [videoUrl, setVideoUrl]         = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const navigate    = useNavigate();
  const inputRef    = useRef(null);
  const abortRef    = useRef(null); // holds the AbortController for in-flight requests

  useEffect(() => {
    if (appState === 'idle' && inputRef.current) inputRef.current.focus();
  }, [appState]);

  // Clean up blob URL when component unmounts or a new video is generated
  useEffect(() => {
    return () => {
      if (videoUrl.startsWith('blob:')) {
        console.log('[ChatPage] Revoking blob URL:', videoUrl);
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  // Cancel any in-flight request when the component unmounts
  useEffect(() => {
    return () => {
      if (abortRef.current) {
        console.log('[ChatPage] Component unmounting — aborting in-flight request');
        abortRef.current.abort();
      }
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || appState === 'generating') return;

    const submittedPrompt = prompt.trim();
    console.log(`[ChatPage] ── Submitting ────────────────────────────────`);
    console.log(`[ChatPage] Topic:    ${submittedPrompt}`);
    console.log(`[ChatPage] Language: ${language}`);
    console.log(`[ChatPage] Endpoint: ${API_BASE}/generate`);

    setAppState('generating');
    setVideoUrl('');
    setErrorMessage('');
    setPrompt('');

    // ── AbortController + timeout ────────────────────────────────────────────
    const controller  = new AbortController();
    abortRef.current  = controller;

    const timeoutId = setTimeout(() => {
      console.warn(`[ChatPage] Request timed out after ${FETCH_TIMEOUT_MS / 1000}s — aborting`);
      controller.abort();
    }, FETCH_TIMEOUT_MS);

    try {
      console.log('[ChatPage] fetch() → starting request...');
      const startTime = Date.now();

      const res = await fetch(`${API_BASE}/generate`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ topic: submittedPrompt, lang_code: language }),
        signal:  controller.signal,
      });

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`[ChatPage] fetch() ← response received in ${elapsed}s`);
      console.log(`[ChatPage] HTTP status: ${res.status} ${res.statusText}`);
      console.log(`[ChatPage] Content-Type: ${res.headers.get('content-type')}`);

      if (!res.ok) {
        // Try to parse a JSON error body from FastAPI
        let detail = `Server error ${res.status}`;
        try {
          const errData = await res.json();
          console.error('[ChatPage] Error body from server:', errData);
          detail = errData.detail || detail;
        } catch (parseErr) {
          console.warn('[ChatPage] Could not parse error response body:', parseErr);
        }
        throw new Error(detail);
      }

      // ── Success path ───────────────────────────────────────────────────────
      console.log('[ChatPage] Response OK — reading video blob...');
      const blob = await res.blob();
      console.log(`[ChatPage] Blob received: ${(blob.size / 1024).toFixed(1)} KB  type=${blob.type}`);

      if (blob.size === 0) {
        throw new Error('Server returned an empty video file.');
      }

      const url = URL.createObjectURL(blob);
      console.log('[ChatPage] Blob URL created:', url);

      setVideoUrl(url);
      setAppState('completed');
      console.log('[ChatPage] ✅ Video ready');

    } catch (err) {
      if (err.name === 'AbortError') {
        console.error('[ChatPage] Request was aborted (timeout or navigation)');
        setErrorMessage(
          `Request timed out after ${FETCH_TIMEOUT_MS / 60000} minutes. ` +
          'The pipeline may still be running — please check the server logs.'
        );
      } else {
        console.error('[ChatPage] ❌ Generation error:', err);
        console.error('[ChatPage] Error name:', err.name);
        console.error('[ChatPage] Error message:', err.message);
        setErrorMessage(err.message || 'Failed to generate video. Please try again.');
      }
      setAppState('error');

    } finally {
      clearTimeout(timeoutId);
      abortRef.current = null;
      console.log('[ChatPage] ── Request complete ─────────────────────────');
    }
  };

  const handleBack = () => {
    // Cancel any in-flight request before navigating away
    if (abortRef.current) {
      console.log('[ChatPage] Navigating away — aborting in-flight request');
      abortRef.current.abort();
    }
    navigate('/');
  };

  // ── Language Picker ────────────────────────────────────────────────────────
  const langPicker = (
    <div className="lang-picker">
      <Globe size={14} className="lang-picker-icon" />
      {LANGUAGES.map(lang => (
        <button
          key={lang.code}
          onClick={() => {
            console.log(`[ChatPage] Language changed to: ${lang.code}`);
            setLanguage(lang.code);
          }}
          className={`lang-btn${language === lang.code ? ' lang-btn-active' : ''}`}
          disabled={appState === 'generating'}
          title={lang.label}
        >
          <span className="lang-btn-flag">{lang.flag}</span>
          <span className="lang-btn-label">{lang.label}</span>
        </button>
      ))}
    </div>
  );

  // ── Input form ─────────────────────────────────────────────────────────────
  const inputForm = (
    <form onSubmit={handleSubmit} className="chat-form">
      <input
        ref={inputRef}
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="What should I visualize for you...?"
        disabled={appState === 'generating'}
        className="chat-input-field"
        autoComplete="off"
      />
      <button
        type="submit"
        disabled={appState === 'generating' || !prompt.trim()}
        className="chat-send-btn"
      >
        <Send size={20} style={{ color: prompt.trim() && appState !== 'generating' ? '#000' : '#6b7280' }} />
      </button>
    </form>
  );

  return (
    <div className="app-container chat-layout">
      <Starfield />

      {/* Header */}
      <div className="chat-header-bar">
        <div className="max-w-7xl header-content">
          <button onClick={handleBack} className="back-link">
            <ArrowLeft size={20} />
            <span>Home</span>
          </button>
          <div className="header-title">
            <span>IMAGIO STUDIO</span>
          </div>
        </div>
      </div>

      {/* Main scrollable content */}
      <div className="chat-content-area">
        <AnimatePresence mode="wait">

          {/* ── Idle: centered prompt ───────────────────────────────── */}
          {appState === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.4 }}
              className="centered-view input-wrapper-max"
            >
              <h1 className="concept-title">Concept to Creation.</h1>
              <p className="concept-subtitle">
                Describe a complex scientific or mathematical concept, and watch it become an animated reality.
              </p>

              {/*
                layoutId is ONLY on the idle input wrapper.
                The bottom bar uses a different key ("bottom-bar") to avoid
                Framer Motion trying to animate between two elements sharing
                the same layoutId simultaneously, which causes a layout freeze.
              */}
              <motion.div layoutId="input-container-idle" className="input-container-large glow-border">
                {inputForm}
              </motion.div>

              {langPicker}

              <div className="suggestions-container">
                {["Fourier Transform", "Black Hole Event Horizon", "Neural Network Backpropagation"].map(suggestion => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      console.log(`[ChatPage] Suggestion selected: ${suggestion}`);
                      setPrompt(suggestion);
                    }}
                    className="suggestion-btn"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* ── Active: generating / error / completed ─────────────── */}
          {appState !== 'idle' && (
            <motion.div
              key="active"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="active-view-wrapper"
            >
              {/* Loader */}
              {appState === 'generating' && (
                <div className="loader-container">
                  <div className="loader-orbit-container">
                    <div className="loader-core"></div>
                    <div className="loader-orbit loader-orbit-1"></div>
                    <div className="loader-orbit loader-orbit-2"></div>
                    <div className="loader-orbit loader-orbit-3"></div>
                  </div>
                  <p className="loader-caption">Generating your video… (this can take 2–5 minutes)</p>
                </div>
              )}

              {/* Error */}
              {appState === 'error' && (
                <div className="error-container">
                  <AlertCircle className="error-icon" size={48} />
                  <h3 className="error-title">Generation Failed</h3>
                  <p className="error-msg">{errorMessage}</p>
                  <button
                    className="btn-neon"
                    style={{ marginTop: '1.5rem', maxWidth: '200px' }}
                    onClick={() => {
                      console.log('[ChatPage] Try Again clicked — resetting to idle');
                      setAppState('idle');
                    }}
                  >
                    Try Again
                  </button>
                </div>
              )}

              {/* Video result */}
              {appState === 'completed' && videoUrl && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: "spring", bounce: 0.4 }}
                  className="video-result-container"
                >
                  <div className="video-player-wrapper">
                    <video
                      controls
                      autoPlay
                      className="result-video-element"
                      onPlay={() => console.log('[ChatPage] Video playing')}
                      onError={(e) => console.error('[ChatPage] Video element error:', e)}
                    >
                      <source src={videoUrl} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                    <div className="video-ambient-glow"></div>
                  </div>

                  <div className="download-wrapper">
                    <a
                      href={videoUrl}
                      download="imagio_video.mp4"
                      className="btn-download-primary"
                      onClick={() => console.log('[ChatPage] Download clicked')}
                    >
                      <Download size={20} />
                      Download Full Render
                    </a>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      {/* ── Bottom fixed input bar (non-idle states) ─────────────────── */}
      <AnimatePresence>
        {appState !== 'idle' && (
          <motion.div
            key="bottom-bar"
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="bottom-input-bar"
          >
            <div className="bottom-input-bar-inner">
              <div className="input-container-floating glow-border">
                {inputForm}
              </div>
              {langPicker}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ChatPage;