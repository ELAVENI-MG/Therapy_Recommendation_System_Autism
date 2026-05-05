import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate("/home");
  };

  return (
    <div className="center">
      
      {/* 🧸 FLEX WRAPPER */}
      <div className="login-wrapper">
        
        {/* 🎨 LEFT IMAGE */}
        <div className="login-image"></div>
        <h1 className="login-title">Welcome Kudoos !!</h1>
        {/* 🧸 RIGHT FORM */}
        <form onSubmit={handleLogin}>
          <h2 className="login-title">🎈 Login 🎈</h2>

          <input
            type="email"
            placeholder="Email 📧"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password 🔒"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">🚀 Login</button>
        </form>

      </div>

    </div>
  );
}

export default Login;