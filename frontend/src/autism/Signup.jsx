import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css"; 

function Signup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: ""
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = (e) => {
    e.preventDefault();

    // store user (temporary)
    localStorage.setItem("user", JSON.stringify(form));

    alert("Signup successful 🎉");
    navigate("/login");
  };

  return (
    <div className="center">

      {/* 🧸 FLEX WRAPPER */}
      <div className="login-wrapper">

        {/* 🎨 LEFT IMAGE */}
        <div className="login-image"></div>
        <h1 className="login-title">Welcome Kudoos !!</h1>
        {/* 🧸 RIGHT FORM */}
        <form onSubmit={handleSignup}>
          <h2 className="login-title">🎈 Sign Up 🎈</h2>

          <input
            type="text"
            name="name"
            placeholder="Your Name 😊"
            value={form.name}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email 📧"
            value={form.email}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Password 🔒"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button type="submit">🚀 Create Account</button>

          <p style={{ marginTop: "10px" }}>
            Already have an account?{" "}
            <span
              style={{ color: "#ff69b4", cursor: "pointer" }}
              onClick={() => navigate("/login")}
            >
              Login
            </span>
          </p>

        </form>

      </div>

    </div>
  );
}

export default Signup;