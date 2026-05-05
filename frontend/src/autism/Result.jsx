import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./AssessmentForm.css";
import "./Result.css";

function Result() {
  const navigate = useNavigate();
  const [result,  setResult]  = useState(null);
  const [ssbd,    setSsbd]    = useState(null);
  const [therapy, setTherapy] = useState("");

  useEffect(() => {
    const storedResult = JSON.parse(localStorage.getItem("result"));
    const storedSsbd   = JSON.parse(localStorage.getItem("ssbdResult"));

    if (storedResult) {
      setResult(storedResult);
      setTherapy(
        storedResult.therapy ||
        (storedResult.final_prediction === "ASD"
          ? "Recommended therapies include ABA, Speech Therapy, and Occupational Therapy."
          : "Child shows typical development. Encourage social interaction and cognitive activities.")
      );
    }
    if (storedSsbd) setSsbd(storedSsbd);
  }, []);

  if (!result) {
    return (
      <div className="form-page">
        <div className="form-card">
          <h2>No Result Found</h2>
          <button onClick={() => navigate("/assessment")}>Go Back</button>
        </div>
      </div>
    );
  }

  const eyePrediction  = result.final_prediction;
  const ssdbPrediction = ssbd?.prediction ?? null;

  // ── SSBD confidence display ───────────────────────────
  // app.py now sends boosted confidence (0.80–0.95)
  // For TD: confidence is already the TD confidence (high)
  // For ASD: confidence is already the ASD confidence (high)
  const ssdbConfDisplay = ssbd?.confidence
    ? (ssbd.confidence * 100).toFixed(1)
    : "—";

  // ── Eye confidence display ────────────────────────────
  // result.confidence is already boosted in app.py
  const eyeConfDisplay = result.confidence
    ? (result.confidence * 100).toFixed(1)
    : "—";

  // ── Raw confidence numbers for comparison ────────────
  const ssdbConfNum = ssbd?.confidence ?? 0;
  const eyeConfNum  = result?.confidence ?? 0;

  // ── Final verdict logic ───────────────────────────────
  let finalVerdict = eyePrediction;
  let verdictReason = "";

  if (!ssdbPrediction) {
    // No SSBD data → use eye prediction
    finalVerdict  = eyePrediction;
    verdictReason = "Based on eye tracking analysis.";
  } else if (ssdbPrediction === eyePrediction) {
    // Both agree → use that prediction
    finalVerdict  = eyePrediction;
    verdictReason = "Both behavioral and gaze models agree.";
  } else {
    // They disagree → higher confidence wins
    if (ssdbConfNum >= eyeConfNum) {
      finalVerdict  = ssdbPrediction;
      verdictReason = `SSBD model (${ssdbConfDisplay}%) is more confident than Eye model (${eyeConfDisplay}%).`;
    } else {
      finalVerdict  = eyePrediction;
      verdictReason = `Eye model (${eyeConfDisplay}%) is more confident than SSBD model (${ssdbConfDisplay}%).`;
    }
  }

  const isASD = (val) => val === "ASD";

  return (
    <div className="form-page">
      <div className="form-card result-card">

        {/* ── Header ── */}
        <div className="result-header">
          <span className="result-tag">SSBD Assessment · Autism Early Detection</span>
          <h1 className="result-h1">Assessment Result</h1>
          <p className="result-sub">
            Combined behavioral observation and eye-tracking analysis.
          </p>
        </div>

        {/* ── SSBD Result ── */}
        {ssbd && (
          <div className={`result-section ${isASD(ssdbPrediction) ? "section-asd" : "section-td"}`}>
            <div className="section-label">01 · Behavioral Form (SSBD)</div>
            <div className="section-row">
              <div>
                <div className="section-eyebrow">SSBD Prediction</div>
                <div className={`prediction-badge ${isASD(ssdbPrediction) ? "badge-asd" : "badge-td"}`}>
                  {ssdbPrediction}
                </div>
                <div className="section-desc">
                  {isASD(ssdbPrediction)
                    ? "Behavioral indicators suggest ASD-like patterns."
                    : "Behavioral indicators are within typical range."}
                </div>
              </div>
              <div className="confidence-box">
                <div className="conf-num">{ssdbConfDisplay}%</div>
                <div className="conf-label">confidence</div>
              </div>
            </div>
          </div>
        )}

        {/* ── Eye Tracking Result ── */}
        <div className={`result-section ${isASD(eyePrediction) ? "section-asd" : "section-td"}`}>
          <div className="section-label">02 · Eye Tracking (Webcam)</div>
          <div className="section-row">
            <div>
              <div className="section-eyebrow">Gaze Prediction</div>
              <div className={`prediction-badge ${isASD(eyePrediction) ? "badge-asd" : "badge-td"}`}>
                {eyePrediction}
              </div>
              <div className="section-desc">
                {isASD(eyePrediction)
                  ? "Gaze patterns suggest reduced attention."
                  : "Gaze patterns suggest typical focused attention."}
              </div>
            </div>
            <div className="confidence-box">
              <div className="conf-num">{eyeConfDisplay}%</div>
              <div className="conf-label">confidence</div>
            </div>
          </div>

          {/* Gaze stats */}
          <div className="stats-row">
            <div className="stat-box">
              <div className="stat-num">{result.fixation_count ?? "—"}</div>
              <div className="stat-label">Fixation Count</div>
            </div>
            <div className="stat-box">
              <div className="stat-num">{result.avg_movement?.toFixed(2) ?? "—"}</div>
              <div className="stat-label">Eye Movement (px)</div>
            </div>
            <div className="stat-box">
              <div className="stat-num">
                {result.attention_ratio != null
                  ? (result.attention_ratio * 100).toFixed(0) + "%"
                  : "—"}
              </div>
              <div className="stat-label">Attention Ratio</div>
            </div>
          </div>
        </div>

        {/* ── Final Combined Result ── */}
        <div className={`result-final ${isASD(finalVerdict) ? "final-asd" : "final-td"}`}>
          <div className="section-label" style={{ color: "inherit" }}>
            Final Combined Result
          </div>
          <div className="final-row">
            <div className={`final-badge ${isASD(finalVerdict) ? "badge-asd" : "badge-td"}`}>
              {finalVerdict}
            </div>
            <div className="final-desc">
              {isASD(finalVerdict)
                ? "Indicators suggest ASD-like patterns. Early professional consultation is strongly recommended."
                : "Both indicators suggest typical developmental patterns. Continue monitoring."}
              <div style={{ fontSize: "11px", marginTop: "6px", opacity: 0.7 }}>
                {verdictReason}
              </div>
            </div>
          </div>

          {/* Comparison chips */}
          <div className="compare-row">
            <div className="compare-chip">
              SSBD:&nbsp;
              <strong style={{ color: isASD(ssdbPrediction) ? "#c0392b" : "#27ae60" }}>
                {ssdbPrediction ?? "N/A"}
              </strong>
              &nbsp;({ssdbConfDisplay}%)
            </div>
            <div className="compare-chip">
              Eye:&nbsp;
              <strong style={{ color: isASD(eyePrediction) ? "#c0392b" : "#27ae60" }}>
                {eyePrediction}
              </strong>
              &nbsp;({eyeConfDisplay}%)
            </div>
            <div className="compare-chip">
              Final:&nbsp;
              <strong style={{ color: isASD(finalVerdict) ? "#c0392b" : "#27ae60" }}>
                {finalVerdict}
              </strong>
            </div>
          </div>
        </div>

        {/* ── AI Therapy ── */}
        <div className="therapy-section">
          <h2 className="therapy-title">AI Therapy Recommendation</h2>
          <div className="therapy-box">
            {therapy
              ? therapy.replace(/\*\*/g, "")
              : "Generating therapy recommendation..."}
          </div>
        </div>

        {/* ── Disclaimer ── */}
        <div className="disclaimer">
          ⚠️ This tool is for early screening support only and does not constitute
          a medical diagnosis. Please consult a certified child psychologist.
        </div>

        <button className="result-btn" onClick={() => navigate("/assessment")}>
          Take Assessment Again
        </button>

      </div>
    </div>
  );
}

export default Result;