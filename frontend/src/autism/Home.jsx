import "./Home.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

function Home() {
  const navigate = useNavigate();
  const [openMenu, setOpenMenu] = useState(false);

  return (
    <>
      

      <div className="home-container">
        
        <div className="background">
          <span className="shape s1"></span>
          <span className="shape s2"></span>
          <span className="shape s3"></span>
        </div>


        <div className="hero-section">
          <div className="hero-text">
            <h1>Therapy Recommendations</h1>
            <p className="subtitle">
              Supporting children with autism through personalized therapies
              and care.
            </p>
          </div>

          <img
            src="https://connect.bcbstx.com/cfs-filesystemfile/__key/communityserver-components-secureimagefileviewer/communityserver-blogs-components-weblogfiles-00-00-00-00-02/AdobeStock_5F00_92337021.jpeg.jpg_2D00_680x320x2.jpg?_=637125456085550354"
            alt="child therapy"
            className="hero-img"
          />
        </div>

        <div className="therapy-grid">
          <div className="therapy-card">
            <h3>🧠 Applied Behavior Analysis (ABA)</h3>
            <p>
              ABA therapy focuses on improving communication, social skills,
              learning abilities, and positive behaviors using structured
              techniques and reinforcement.
            </p>
          </div>

          <div className="therapy-card">
            <h3>🗣 Speech Therapy</h3>
            <p>
              Speech therapy helps children enhance speech clarity, language
              comprehension, and communication skills for everyday interactions.
            </p>
          </div>

          <div className="therapy-card">
            <h3>🤸 Occupational Therapy</h3>
            <p>
              Occupational therapy supports motor development, sensory
              integration, and daily living skills to improve independence.
            </p>
          </div>

          <div className="therapy-card">
            <h3>🎵 Music Therapy</h3>
            <p>
              Music therapy uses rhythm and sound to improve emotional expression,
              attention span, and social engagement in children.
            </p>
          </div>

          <div className="therapy-card">
            <h3>🎨 Art Therapy</h3>
            <p>
              Art therapy encourages creativity and emotional expression, helping
              children communicate feelings through drawing and visual activities.
            </p>
          </div>

          <div className="therapy-card">
            <h3>📚 Social Skills Training</h3>
            <p>
              Social skills training helps children develop meaningful social
              interactions, understand emotions, and build friendships in various
              settings.
            </p>
          </div>
        </div>

        <div className="info-section">
        <h2>Why Early Therapy Matters?</h2>
        <p>
          Early intervention plays a crucial role in improving the development of
          children with autism. With the right therapies at the right time, children
          can significantly improve their communication, behavior, and social skills.
        </p>

        <div className="info-cards">
          <div className="info-card">
            <h4>🧩 Better Development</h4>
            <p>Helps children improve cognitive and learning abilities early.</p>
          </div>

          <div className="info-card">
            <h4>💬 Improved Communication</h4>
            <p>Enhances speech, understanding, and interaction skills.</p>
          </div>

          <div className="info-card">
            <h4>😊 Emotional Growth</h4>
            <p>Supports emotional control and reduces anxiety.</p>
          </div>

          <div className="info-card">
            <h4>🤝 Social Interaction</h4>
            <p>Encourages building relationships and social confidence.</p>
          </div>
        </div>
      </div>

        <div className="form-section">
          <button className="form-btn" onClick={() => navigate("/assessment")}>
            Fill Child Assessment Form
          </button>
        </div>
      </div>
    </>
  );
}

export default Home;
