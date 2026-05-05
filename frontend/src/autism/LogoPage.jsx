import { useNavigate } from "react-router-dom";
import "../index.css";
import playingImg from "../assets/images/playing.png";
import autism_logo from "../assets/images/autism-logo.png";

function LogoPage() {
  const navigate = useNavigate();

  return (
    <div className="logo-container">

      {/* BACKGROUND */}
      <div className="background">
        <span className="shape s1"></span>
        <span className="shape s2"></span>
        <span className="shape s3"></span>
        <span className="shape s4"></span>
      </div>

      {/* TOP BRAND */}
      <div className="top-brand">
        <h1 className="brand-name">AutiCare 🫂Accept Difference</h1>
        <p className="tagline">
          Supporting children with autism through personalized care
        </p>
      </div>

      {/* MAIN CARD */}
      <div className="logo-card">

        {/* LEFT IMAGE */}
        <div className="left-image">
          <img src={playingImg} alt="happy child" />
        </div>

        {/* RIGHT CONTENT */}
        <div className="right-content">
          
          <img
            src={autism_logo}
            alt="Autism Logo"
            className="autism-logo"
          />

          <h2 className="title">Therapy Recommendation System</h2>

          <div className="button-group">
            <button className="login-btn" onClick={() => navigate("/login")}>
              Login
            </button>
            <button className="signup-btn" onClick={() => navigate("/signup")}>
              Signup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LogoPage;