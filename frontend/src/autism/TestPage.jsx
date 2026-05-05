import React, { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./TestPage.css"; 
// Images
import img1 from "../assets/images/img1.jpg";
import img2 from "../assets/images/img2.jpg";
import img3 from "../assets/images/img3.jpg";
import img4 from "../assets/images/img4.jpg";

const images = [img1, img2, img3, img4];

function TestPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const navigate = useNavigate();

  const [tracking, setTracking] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);

  const gazePoints = useRef([]);

  // 🖼️ Show ONE random image
  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * images.length);
    setCurrentImage(images[randomIndex]);
    localStorage.setItem("imageType", randomIndex);
  }, []);

  // 👁️ Capture gaze every 1 sec
  useEffect(() => {
    let interval;

    if (tracking) {
      interval = setInterval(() => {
        captureFrame();
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [tracking]);

  // 📸 Capture frame
  const captureFrame = async () => {
    if (!videoRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;

    const ctx = canvas.getContext("2d");

    // ✅ FIXED SIZE (MATCH BACKEND)
    ctx.drawImage(video, 0, 0, 400, 300);

    const imageData = canvas.toDataURL("image/jpeg");

    try {
      const res = await fetch("http://127.0.0.1:5000/track_gaze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ image: imageData })
      });

      const data = await res.json();
      console.log("Gaze Data:", data);

      if (data.x !== undefined && data.y !== undefined) {
        gazePoints.current.push({ x: data.x, y: data.y });
      }

    } catch (err) {
      console.log("Tracking error:", err);
    }
  };

  // 🎥 START WEBCAM
  const startTracking = async () => {
    if (tracking) return;

    gazePoints.current = [];
    setTracking(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      videoRef.current.srcObject = stream;
      streamRef.current = stream;

    } catch (err) {
      console.log("Webcam error:", err);
    }
  };

  // ❌ STOP WEBCAM
  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  // 📊 Analyze
  const getResult = async () => {
    console.log("Analyze button clicked");

    stopWebcam();
    setTracking(false);

    const formData = JSON.parse(localStorage.getItem("formData"));

    console.log("Form Data:", formData);
    console.log("Gaze Points:", gazePoints.current);

    try {
      const res = await fetch("http://127.0.0.1:5000/final_prediction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          form_data: formData,
          gaze_points: gazePoints.current,
          image_type: localStorage.getItem("imageType")
        })
      });

      const data = await res.json();
      console.log("Final Result:", data);

      if (data.error) {
        alert(data.error);
        return;
      }

      localStorage.setItem("result", JSON.stringify(data));
      navigate("/result");

    } catch (err) {
      alert("Error getting result");
    }
  };

  // 🧹 Cleanup
  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, []);

  return (
    <div style={{ textAlign: "center" }}>
      <h2>Eye Tracking Test</h2>

      <p style={{ color: "blue" }}>
        Look at the image for 10–15 seconds, then click Analyze.
      </p>

      {/* 🖼️ IMAGE */}
      {currentImage && (
        <img
          src={currentImage}
          width="400"
          height="300"
          alt="Stimulus"
        />
      )}

      <br /><br />

      {/* 🎥 Hidden webcam */}
      <video ref={videoRef} autoPlay style={{ display: "none" }} />
      
      {/* ✅ FIXED CANVAS SIZE */}
      <canvas
        ref={canvasRef}
        width="400"
        height="300"
        style={{ display: "none" }}
      />

      <br /><br />

      <button onClick={startTracking} disabled={tracking}>
        Start Tracking
      </button>

      <button onClick={getResult}>
        Analyze
      </button>
    </div>
  );
}

export default TestPage;