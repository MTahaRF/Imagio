import React, { useEffect, useRef } from 'react';

const Starfield = ({ color }) => {
  const canvasRef = useRef(null);
  const colorRef  = useRef(color);

  // Keep colorRef in sync without restarting the animation loop
  useEffect(() => {
    colorRef.current = color;
  }, [color]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;

    const starCount = 200;
    const stars = Array.from({ length: starCount }, () => ({
      x:      Math.random() * canvas.width,
      y:      Math.random() * canvas.height,
      radius: Math.random() * 1.5,
      alpha:  Math.random() * 0.8 + 0.2,
      speed:  Math.random() * 0.5 + 0.1,
    }));

    let animId;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const baseColor = colorRef.current || '255,255,255';
      stars.forEach(star => {
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${baseColor},${star.alpha})`;
        ctx.fill();
        star.y += star.speed;
        if (star.y > canvas.height) {
          star.y = 0;
          star.x = Math.random() * canvas.width;
        }
      });
      animId = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
    };
  }, []); // only run once

  return <canvas ref={canvasRef} className="starfield-canvas" />;
};

export default Starfield;