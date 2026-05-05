// frontend/src/autism/AssessmentForm.jsx

import React, { useState } from "react";
import "./AssessmentForm.css";
import { useNavigate } from "react-router-dom";

const AssessmentForm = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    child_name: "",
    age: "",
    gender: "",
    observer: "",
    behaviour: null,       // 0=armflapping,1=headbanging,2=spinning
    duration: "",
    frames_sec: "",
    bodypart: null,        // High=1, Low=0
    intensity: null,       // Low=1, Medium=2, High=3
    behaviour_count: "",
    bc_hl: null,           // High=1, Low=0
    frequency_hl: null,    // High=1, Low=0
    stops_when_called: null, // High=1, Low=0
    social_interaction: null,// High=1, Low=0
    sensory_sensitivity: null // High=1, Low=0
  });

  const [errors, setErrors]   = useState({});
  const [loading, setLoading] = useState(false);

  // ── Auto-calculated features ──────────────────────────
  const dur = parseFloat(form.duration) || 0;
  const bc  = parseFloat(form.behaviour_count) || 0;
  const frm = (parseFloat(form.frames_sec) || 0) * 30;
  const frequency_rate         = dur > 0 ? (bc / dur).toFixed(4) : "—";
  const frames_per_duration    = dur > 0 ? (frm / dur).toFixed(3) : "—";
  const behaviour_per_duration = dur > 0 ? (bc / dur).toFixed(4)  : "—";
  const intensity_x_behaviour  = form.intensity && bc
    ? (form.intensity * bc).toFixed(2) : "—";

  // ── Helpers ───────────────────────────────────────────
  const setField = (key, val) => setForm(f => ({ ...f, [key]: val }));

  const HLButton = ({ groupKey, value, label, encoded, desc, colorClass }) => (
    <button
      type="button"
      className={`hl-btn ${form[groupKey] === value ? colorClass : ""}`}
      onClick={() => setField(groupKey, value)}
    >
      <div className="hl-dot" />
      <span className="hl-label">{label}</span>
      <span className="hl-encoded">encoded → {encoded}</span>
      <p className="hl-desc">{desc}</p>
    </button>
  );

  // ── Validation ────────────────────────────────────────
  const validate = () => {
    const e = {};
    if (!form.child_name.trim()) e.child_name = "Required";
    if (!form.duration)          e.duration   = "Required";
    if (!form.behaviour_count)   e.behaviour_count = "Required";
    if (form.behaviour === null) e.behaviour  = "Select a behaviour";
    if (form.intensity === null) e.intensity  = "Select intensity";
    return e;
  };

  // ── Submit → send to Flask backend ───────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }

    setLoading(true);
    const payload = {
      child_name:            form.child_name,
      age:                   form.age,
      gender:                form.gender,
      behaviour:             form.behaviour,
      frames:                frm,
      duration:              parseFloat(form.duration),
      bodypart:              form.bodypart,
      intensity:             form.intensity,
      behaviour_count:       bc,
      frames_per_duration:   parseFloat(frames_per_duration) || 0,
      behaviour_per_duration:parseFloat(behaviour_per_duration) || 0,
      intensity_x_behaviour: parseFloat(intensity_x_behaviour) || 0,
      frequency_rate:        parseFloat(frequency_rate) || 0,
      stops_when_called:     form.stops_when_called,
      social_interaction:    form.social_interaction,
      sensory_sensitivity:   form.sensory_sensitivity,
    };

    try {
      const res  = await fetch("http://localhost:5000/predict", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });
      //const data = await res.json();
      // Pass result to Result page
      //navigate("/result", { state: { result: data, form: payload } });

         const data = await res.json();
         // Save SSBD result to localStorage
        localStorage.setItem("ssbdResult", JSON.stringify(data));
        localStorage.setItem("formData",   JSON.stringify(payload));
        // Go to webcam page
        navigate("/test"); 
    } catch (err) {
      alert("Backend connection failed. Make sure Flask is running.");
    } finally {
      setLoading(false);
    }
  };

  // ── Progress ──────────────────────────────────────────
  const fields = [
    form.child_name, form.duration, form.behaviour_count,
    form.behaviour, form.bodypart, form.intensity,
    form.bc_hl, form.frequency_hl, form.stops_when_called,
    form.social_interaction
  ];
  const answered = fields.filter(f => f !== null && f !== "").length;
  const progress = Math.round((answered / fields.length) * 100);

  return (
    <div className="af-page">
      <div className="af-header">
        <span className="af-tag">SSBD Assessment · Autism Early Detection</span>
        <h1 className="af-title">Behavioral Observation Form</h1>
        <p className="af-sub">
          Answer each question based on what you observed.
          All High / Low options are converted to numbers automatically.
        </p>
      </div>

      {/* Progress bar */}
      <div className="af-progress">
        <div className="af-progress-track">
          <div className="af-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="af-progress-labels">
          <span>{answered} of {fields.length} answered</span>
          <span>{progress}%</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="af-form">

        {/* ── Q1: Child Info ── */}
        <div className="af-card">
          <div className="af-qnum">Question 01</div>
          <div className="af-qtitle">What is the child's name and age?</div>
          <div className="af-two">
            <div className="af-field">
              <input
                type="text"
                placeholder="Child's full name"
                value={form.child_name}
                onChange={e => setField("child_name", e.target.value)}
                className={errors.child_name ? "err" : ""}
              />
              {errors.child_name && <span className="af-err">{errors.child_name}</span>}
            </div>
            <input
              type="number" placeholder="Age in years"
              value={form.age} min="1" max="18"
              onChange={e => setField("age", e.target.value)}
            />
          </div>
          <div className="af-two" style={{ marginTop: 10 }}>
            <select value={form.gender} onChange={e => setField("gender", e.target.value)}>
              <option value="">Gender</option>
              <option value="1">Male</option>
              <option value="0">Female</option>
              <option value="2">Other</option>
            </select>
            <select value={form.observer} onChange={e => setField("observer", e.target.value)}>
              <option value="">Observed by</option>
              <option value="1">Parent</option>
              <option value="2">Therapist</option>
              <option value="3">Teacher</option>
              <option value="4">Doctor</option>
            </select>
          </div>
        </div>

        {/* ── Q2: Behaviour Type ── */}
        <div className="af-card">
          <div className="af-qnum">Question 02 · <code>category → 0 / 1 / 2</code></div>
          <div className="af-qtitle">Which repetitive movement did you observe?</div>
          {errors.behaviour && <span className="af-err">{errors.behaviour}</span>}
          <div className="af-beh-group">
            {[
              { lbl: "Arm Flapping",  val: 0, desc: "Rapid up-and-down arm movement",          enc: 0, color: "#E6F1FB", tc: "#185FA5" },
              { lbl: "Head Banging",  val: 1, desc: "Repetitive head hitting on surfaces",      enc: 1, color: "#FAECE7", tc: "#993C1D" },
              { lbl: "Spinning",      val: 2, desc: "Body or head rotating in circles",         enc: 2, color: "#EAF3DE", tc: "#3B6D11" },
            ].map(b => (
              <button
                key={b.val} type="button"
                className={`af-beh-btn ${form.behaviour === b.val ? "beh-sel" : ""}`}
                onClick={() => setField("behaviour", b.val)}
              >
                <div>
                  <div className="beh-name">{b.lbl}</div>
                  <div className="beh-desc">{b.desc}</div>
                </div>
                <span className="beh-badge" style={{ background: b.color, color: b.tc }}>
                  encoded → {b.enc}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* ── Q3: Duration ── */}
        <div className="af-card">
          <div className="af-qnum">Question 03 · <code>duration + frames</code></div>
          <div className="af-qtitle">How long was the observation session?</div>
          <div className="af-qsub">Enter total session time and movement-visible time in seconds</div>
          <div className="af-two">
            <div className="af-field">
              <label>Total session (sec)</label>
              <input type="number" placeholder="e.g. 120" value={form.duration} min="1"
                onChange={e => setField("duration", e.target.value)}
                className={errors.duration ? "err" : ""} />
            </div>
            <div className="af-field">
              <label>Movement visible (sec)</label>
              <input type="number" placeholder="e.g. 30" value={form.frames_sec} min="1"
                onChange={e => setField("frames_sec", e.target.value)} />
            </div>
          </div>
          {/* Auto values */}
          <div className="af-auto-row">
            <div className="af-auto-card">
              <div className="ac-label">frequency_rate</div>
              <div className="ac-val">{frequency_rate}</div>
            </div>
            <div className="af-auto-card">
              <div className="ac-label">frames_per_duration</div>
              <div className="ac-val">{frames_per_duration}</div>
            </div>
            <div className="af-auto-card">
              <div className="ac-label">beh_per_duration</div>
              <div className="ac-val">{behaviour_per_duration}</div>
            </div>
          </div>
        </div>

        {/* ── Q4: Body Part HIGH / LOW ── */}
        <div className="af-card">
          <div className="af-qnum">Question 04 · <code>bodypart → High=1 / Low=0</code></div>
          <div className="af-qtitle">Is the body part involvement High or Low?</div>
          <div className="af-qsub">High = full body or head · Low = only arms or legs</div>
          <div className="af-hl-row">
            <HLButton groupKey="bodypart" value={1} label="High" encoded={1}
              desc="Full body or head is the primary mover" colorClass="hl-high" />
            <HLButton groupKey="bodypart" value={0} label="Low"  encoded={0}
              desc="Only arms or legs involved" colorClass="hl-low" />
          </div>
        </div>

        {/* ── Q5: Intensity LOW / MEDIUM / HIGH ── */}
        <div className="af-card">
          <div className="af-qnum">Question 05 · <code>intensity → Low=1 / Medium=2 / High=3</code></div>
          <div className="af-qtitle">What is the intensity of the movement?</div>
          <div className="af-qsub">
            From your SSBD chart: Headbanging = High · Spinning = Low
          </div>
          {errors.intensity && <span className="af-err">{errors.intensity}</span>}
          <div className="af-lmh-row">
            <HLButton groupKey="intensity" value={1} label="Low"    encoded={1}
              desc="Barely noticeable, gentle"  colorClass="hl-low" />
            <HLButton groupKey="intensity" value={2} label="Medium" encoded={2}
              desc="Clearly visible, moderate"  colorClass="hl-med" />
            <HLButton groupKey="intensity" value={3} label="High"   encoded={3}
              desc="Forceful, hard to ignore"   colorClass="hl-high" />
          </div>
        </div>

        {/* ── Q6: Behaviour Count ── */}
        <div className="af-card">
          <div className="af-qnum">Question 06 · <code>behaviour_count</code></div>
          <div className="af-qtitle">How many times did the repetitive movement occur?</div>
          <div className="af-qsub">Most SSBD videos show 1–7 occurrences</div>
          <input type="number" placeholder="Enter exact count e.g. 3"
            value={form.behaviour_count} min="1"
            onChange={e => setField("behaviour_count", e.target.value)}
            className={errors.behaviour_count ? "err" : ""}
            style={{ marginBottom: 12 }} />
          <div className="af-qsub">Is the count High or Low overall?</div>
          <div className="af-hl-row">
            <HLButton groupKey="bc_hl" value={1} label="High" encoded={1}
              desc="More than 4 occurrences" colorClass="hl-high" />
            <HLButton groupKey="bc_hl" value={0} label="Low"  encoded={0}
              desc="1 to 3 occurrences"      colorClass="hl-low" />
          </div>
        </div>

        {/* ── Q7: Frequency Rate ── */}
        <div className="af-card">
          <div className="af-qnum">Question 07 · <code>frequency_rate → High=1 / Low=0</code></div>
          <div className="af-qtitle">Is the frequency rate of movement High or Low?</div>
          <div className="af-qsub">
            Auto-calculated: <strong>{frequency_rate}</strong> rep/sec
            &nbsp;· High = above 0.040 · Low = below 0.040
          </div>
          <div className="af-hl-row">
            <HLButton groupKey="frequency_hl" value={1} label="High" encoded={1}
              desc="Above 0.040 rep/sec" colorClass="hl-high" />
            <HLButton groupKey="frequency_hl" value={0} label="Low"  encoded={0}
              desc="Below 0.040 rep/sec" colorClass="hl-low" />
          </div>
        </div>

        {/* ── Q8: Stops When Called ── */}
        <div className="af-card">
          <div className="af-qnum">Question 08 · <code>stops_when_called → High=1 / Low=0</code></div>
          <div className="af-qtitle">Does the child stop when called or redirected?</div>
          <div className="af-hl-row">
            <HLButton groupKey="stops_when_called" value={1} label="High" encoded={1}
              desc="Stops immediately or usually" colorClass="hl-high" />
            <HLButton groupKey="stops_when_called" value={0} label="Low"  encoded={0}
              desc="Rarely or never stops"         colorClass="hl-low" />
          </div>
        </div>

        {/* ── Q9: Social Interaction ── */}
        <div className="af-card">
          <div className="af-qnum">Question 09 · <code>social_interaction → High=1 / Low=0</code></div>
          <div className="af-qtitle">Is the child's social interaction High or Low?</div>
          <div className="af-qsub">High = makes eye contact · Low = avoids interaction</div>
          <div className="af-hl-row">
            <HLButton groupKey="social_interaction" value={1} label="High" encoded={1}
              desc="Engages, makes eye contact" colorClass="hl-high" />
            <HLButton groupKey="social_interaction" value={0} label="Low"  encoded={0}
              desc="Avoids interaction"          colorClass="hl-low" />
          </div>
        </div>

        {/* ── Q10: Sensory Sensitivity ── */}
        <div className="af-card">
          <div className="af-qnum">Question 10 · <code>sensory_sensitivity → High=1 / Low=0</code></div>
          <div className="af-qtitle">Is the child's sensory sensitivity High or Low?</div>
          <div className="af-qsub">High = overreacts to noise/light · Low = normal response</div>
          <div className="af-hl-row">
            <HLButton groupKey="sensory_sensitivity" value={1} label="High" encoded={1}
              desc="Overreacts to noise, lights, touch" colorClass="hl-high" />
            <HLButton groupKey="sensory_sensitivity" value={0} label="Low"  encoded={0}
              desc="Normal sensory response"             colorClass="hl-low" />
          </div>
        </div>

        <button type="submit" className="af-submit" disabled={loading}>
          {loading ? "Analyzing..." : "Submit Assessment →"}
        </button>
      </form>
    </div>
  );
};

export default AssessmentForm;