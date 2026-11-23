import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const SECTION_INFO = {
  personal: {
    title: "Discover your interests",
    subtitle: "Tell us what you enjoy and what naturally attracts you.",
    number: "01",
  },
  logical: {
    title: "Test your reasoning",
    subtitle: "Solve each question carefully. Choose the best answer.",
    number: "02",
  },
  scenario: {
    title: "Explore real-life situations",
    subtitle: "Choose how you would most likely respond in each situation.",
    number: "03",
  },
};

function formatLabel(value) {
  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [selectedCareers, setSelectedCareers] = useState([]);

  const toggleCareerComparison = (title) => {
    setSelectedCareers((previous) => {
      if (previous.includes(title)) {
        return previous.filter((item) => item !== title);
      }
      if (previous.length >= 3) {
        return previous;
      }
      return [...previous, title];
    });
  };

  useEffect(() => {
    async function loadQuestions() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`${API_URL}/questionnaire`);

        if (!response.ok) {
          throw new Error("Could not load the questionnaire.");
        }

        const data = await response.json();
        // Supports either { questions: [...] } or a direct [...] response.
        const questionList = Array.isArray(data) ? data : data.questions;

        if (!Array.isArray(questionList) || questionList.length === 0) {
          throw new Error("The backend returned no questions.");
        }

        setQuestions(questionList);
      } catch {
      setError(
        "Unable to connect to the backend. Make sure Flask is running at http://127.0.0.1:5000 and try again."
        );
      } finally {
        setLoading(false);
      }
    }

    loadQuestions();
  }, []);

  const currentQuestion = questions[currentIndex];

  const currentSection = currentQuestion
    ? SECTION_INFO[currentQuestion.section] || {
        title: "Your questionnaire",
        subtitle: "Choose the answer that suits you best.",
        number: "01",
      }
    : null;

  const answeredCount = useMemo(
    () => questions.filter((question) => answers[question.id] !== undefined).length,
    [questions, answers]
  );

  const progress = questions.length
    ? (answeredCount / questions.length) * 100
    : 0;

  const handleAnswer = (optionId) => {
    setAnswers((previous) => ({
      ...previous,
      [currentQuestion.id]: optionId,
    }));
    setError("");
  };

  const handleNext = () => {
    if (!currentQuestion || !answers[currentQuestion.id]) {
      setError("Please select an answer before continuing.");
      return;
    }

    setError("");

    if (currentIndex < questions.length - 1) {
      setCurrentIndex((index) => index + 1);
    } else {
      submitAnswers();
    }
  };

  const submitAnswers = async () => {
    if (answeredCount !== questions.length) {
      setError("Please answer all questions before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const response = await fetch(`${API_URL}/profile`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ answers }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to calculate your results.");
      }

      setResults(data);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong. Check that the Flask backend is running."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const restartQuestionnaire = () => {
    setAnswers({});
    setCurrentIndex(0);
    setResults(null);
    setSelectedCareers([]);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (loading) {
    return (
      <main className="app-shell centered-screen">
        <div className="loading-card">
          <div className="loader" />
          <h2>Preparing your journey</h2>
          <p>Loading your career exploration questions...</p>
        </div>
      </main>
    );
  }

  if (error && questions.length === 0) {
    return (
      <main className="app-shell centered-screen">
        <div className="loading-card error-card">
          <div className="error-symbol">!</div>
          <p className="eyebrow">CONNECTION ISSUE</p>
          <h2>We couldn't load your questions</h2>
          <p>{error}</p>
          <button className="primary-button" onClick={() => window.location.reload()}>
            Try again <span>↻</span>
          </button>
        </div>
      </main>
    );
  }

  if (results) {
    const reasoning = results.logical_reasoning || {};
    const interests = results.personal_interest_counts || {};
    const approaches = results.scenario_approach_counts || {};
    const careerRecommendations = Array.isArray(results.career_recommendations)
      ? results.career_recommendations
      : [];
    const careersToCompare = careerRecommendations.filter((career) =>
      selectedCareers.includes(career.title)
    );

    const interestEntries = Object.entries(interests).sort(
      (a, b) => b[1] - a[1]
    );
    const approachEntries = Object.entries(approaches).sort(
      (a, b) => b[1] - a[1]
    );

    const maxInterest = Math.max(1, ...interestEntries.map((item) => item[1]));
    const maxApproach = Math.max(1, ...approachEntries.map((item) => item[1]));

    return (
      <main className="app-shell">
        <header className="topbar">
          <a className="brand" href="#top" onClick={(event) => event.preventDefault()}>
            <span className="brand-mark">C</span>
            <span>Pathfinder<span className="brand-dot">.</span></span>
          </a>
          <a className="topbar-action" href="#questionnaire">Begin your journey <span>↗</span></a>
        </header>

        <section className="results-container" id="top">
          <div className="results-intro">
            <div className="success-icon">✓</div>
            <p className="eyebrow">YOUR EXPLORATION SUMMARY</p>
            <h1>Your journey starts <span>here.</span></h1>
            <p className="intro-copy">
              You have completed the questionnaire. Here is a snapshot of your
              reasoning performance, interests, and approaches to situations.
            </p>
          </div>

          <div className="results-grid">
            <article className="result-card reasoning-card">
              <div className="card-topline">
                <span className="card-icon purple-icon">✳</span>
                <span className="mini-label">LOGICAL REASONING</span>
              </div>
              <div className="score-display">
                <span className="score-number">
                  {Number(reasoning.percentage ?? 0).toFixed(0)}
                </span>
                <span className="score-percent">%</span>
              </div>
              <p className="result-description">Correct answers in the reasoning section</p>
              <div className="score-track">
                <div
                  className="score-fill"
                  style={{
                    width: `${Math.min(100, Math.max(0, Number(reasoning.percentage) || 0))}%`,
                  }}
                />
              </div>
              <p className="score-caption">
                {reasoning.correct_answers ?? 0} out of{" "}
                {reasoning.total_questions ?? 0} questions correct
              </p>
            </article>

            <article className="result-card summary-card">
              <div className="card-topline">
                <span className="card-icon green-icon">◎</span>
                <span className="mini-label">YOUR PROFILE</span>
              </div>
              <h2>More than a score</h2>
              <p className="result-description">
                Your interests and choices can help you reflect on areas worth
                exploring. They do not define your abilities or limit your options.
              </p>
              <div className="summary-tag">Explore · Learn · Grow</div>
            </article>
          </div>

          <section className="result-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">SECTION 01</p>
                <h2>Your interest map</h2>
                <p>What your selected answers suggest you are interested in.</p>
              </div>
              <span className="section-symbol">◈</span>
            </div>

            {interestEntries.length ? (
              <div className="breakdown-card">
                {interestEntries.map(([label, count], index) => (
                  <div className="breakdown-row" key={label}>
                    <div className="breakdown-label">
                      <span className="row-index">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span>{formatLabel(label)}</span>
                    </div>
                    <div className="breakdown-bar-track">
                      <div
                        className="breakdown-bar interest-bar"
                        style={{ width: `${(count / maxInterest) * 100}%` }}
                      />
                    </div>
                    <span className="breakdown-count">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-note">No interest data was returned.</p>
            )}
          </section>

          <section className="result-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">SECTION 02</p>
                <h2>How you approach situations</h2>
                <p>A summary of the approaches represented in your choices.</p>
              </div>
              <span className="section-symbol">⌘</span>
            </div>

            {approachEntries.length ? (
              <div className="breakdown-card">
                {approachEntries.map(([label, count], index) => (
                  <div className="breakdown-row" key={label}>
                    <div className="breakdown-label">
                      <span className="row-index">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span>{formatLabel(label)}</span>
                    </div>
                    <div className="breakdown-bar-track">
                      <div
                        className="breakdown-bar approach-bar"
                        style={{ width: `${(count / maxApproach) * 100}%` }}
                      />
                    </div>
                    <span className="breakdown-count">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-note">No situation-approach data was returned.</p>
            )}
          </section>

          <section className="result-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">SECTION 03</p>
                <h2>Career paths to explore</h2>
                <p>Suggestions based on your strongest interest areas—not a fixed prediction.</p>
              </div>
              <span className="section-symbol">✦</span>
            </div>

            {selectedCareers.length > 0 && (
              <section className="career-comparison" aria-live="polite">
                <div className="comparison-title-row">
                  <div>
                    <p className="eyebrow">CAREER PLANNER</p>
                    <h3>Compare your selected careers</h3>
                    <p>
                      {careersToCompare.length} of 3 comparison slots used.
                      Compare these options as a starting point for exploration.
                    </p>
                  </div>
                  <button
                    type="button"
                    className="compare-clear-button"
                    onClick={() => setSelectedCareers([])}
                  >
                    Clear selection
                  </button>
                </div>

                <div className="comparison-grid">
                  {careersToCompare.map((career) => (
                    <article className="comparison-card" key={career.title}>
                      <div className="comparison-card-top">
                        <div>
                          <p className="comparison-category">
                            {career.interest_area || "Career"} interest
                          </p>
                          <h3>{career.title}</h3>
                        </div>
                        <button
                          type="button"
                          className="comparison-remove-button"
                          onClick={() => toggleCareerComparison(career.title)}
                          aria-label={`Remove ${career.title} from comparison`}
                          title="Remove from comparison"
                        >
                          ×
                        </button>
                      </div>

                      <div className="comparison-score">
                        <span>Exploration score</span>
                        <strong>
                          {Math.max(
                            0,
                            Math.min(100, Number(career.match_score) || 0)
                          )}/100
                        </strong>
                      </div>

                      <h4>Why explore it?</h4>
                      <p>{career.why || "Explore the work and opportunities in this field."}</p>

                      <h4>Skills to explore</h4>
                      {Array.isArray(career.skills) && career.skills.length > 0 ? (
                        <ul>
                          {career.skills.map((skill, index) => (
                            <li key={`${career.title}-comparison-skill-${index}`}>
                              {skill}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>Research the foundational skills for this field.</p>
                      )}

                      <h4>Beginner project</h4>
                      <p>
                        {career.project || "Try a small beginner project in this field."}
                      </p>

                      <h4>Learning roadmap</h4>
                      {Array.isArray(career.learning_roadmap) &&
                      career.learning_roadmap.length > 0 ? (
                        <ol className="comparison-roadmap">
                          {career.learning_roadmap.map((step, index) => (
                            <li key={`${career.title}-comparison-step-${index}`}>
                              <strong>
                                {step.period || `Step ${index + 1}`}
                                {step.title ? ` · ${step.title}` : ""}
                              </strong>
                              <p>{step.task || "Practise the skills you have learned."}</p>
                            </li>
                          ))}
                        </ol>
                      ) : (
                        <p>Learn the fundamentals, practise, and build a small project.</p>
                      )}

                      <button
                        type="button"
                        className="compare-career-button is-selected"
                        onClick={() => toggleCareerComparison(career.title)}
                      >
                        Remove from comparison
                      </button>
                    </article>
                  ))}
                </div>
                <p className="comparison-note">
                  Scores are questionnaire-based exploration guides, not probabilities
                  of career success or measures of ability.
                </p>
              </section>
            )}

            {careerRecommendations.length > 0 ? (
              <div className="results-grid career-grid">
                {results.career_recommendations.map((career) => (
                  <article className="result-card career-card" key={career.title}>
                    <div className="card-topline">
                      <span className="card-icon green-icon">↗</span>
                      <span className="mini-label">
                        {career.interest_area || "Career"} interest
                      </span>
                    </div>

                    <div className="career-match-row">
                      <span className="career-match-label">
                        Relative exploration score
                      </span>
                      <strong className="career-match-value">
                        {Math.max(
                          0,
                          Math.min(100, Number(career.match_score) || 0)
                        )}
                        /100
                      </strong>
                    </div>

                    <div
                      className="career-match-track"
                      role="progressbar"
                      aria-label={`${career.title} relative exploration score`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={Math.max(
                        0,
                        Math.min(100, Number(career.match_score) || 0)
                      )}
                    >
                      <div
                        className="career-match-fill"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(100, Number(career.match_score) || 0)
                          )}%`,
                        }}
                      />
                    </div>

                    <h2>{career.title}</h2>

                    <p className="result-description">
                      {career.why ||
                        "Explore this career to understand its work, skills, and opportunities."}
                    </p>

                    <button
                      type="button"
                      className={`compare-career-button ${
                        selectedCareers.includes(career.title) ? "is-selected" : ""
                      }`}
                      onClick={() => toggleCareerComparison(career.title)}
                      aria-pressed={selectedCareers.includes(career.title)}
                      disabled={
                        !selectedCareers.includes(career.title) &&
                        selectedCareers.length >= 3
                      }
                    >
                      {selectedCareers.includes(career.title)
                        ? "✓ Added to comparison"
                        : selectedCareers.length >= 3
                        ? "Maximum 3 selected"
                        : "+ Compare this career"}
                    </button>

                    {career.match_explanation && (
                      <div className="career-explanation">
                        <span className="career-detail-icon">✦</span>
                        <div>
                          <h3>Why explore this career?</h3>
                          <p>{career.match_explanation}</p>
                        </div>
                      </div>
                    )}

                    <div className="career-detail-section">
                      <h3>Skills to explore</h3>

                      {Array.isArray(career.skills) && career.skills.length > 0 ? (
                        <ul className="career-list">
                          {career.skills.map((skill, index) => (
                            <li key={`${career.title}-skill-${index}`}>{skill}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="result-description">
                          Research the foundational skills required for this career.
                        </p>
                      )}
                    </div>

                    <div className="career-detail-section">
                      <h3>Your beginner project</h3>
                      <p className="result-description">
                        {career.project ||
                          "Choose a small beginner project related to this field and build it step by step."}
                      </p>
                    </div>

                    <div className="career-roadmap">
                      <div className="career-roadmap-heading">
                        <h3>Your learning roadmap</h3>
                        <span>{career.roadmap_duration || "Starter plan"}</span>
                      </div>

                      {Array.isArray(career.learning_roadmap) &&
                      career.learning_roadmap.length > 0 ? (
                        <ol className="career-roadmap-list">
                          {career.learning_roadmap.map((step, index) => (
                            <li
                              className="career-roadmap-step"
                              key={`${career.title}-roadmap-${index}`}
                            >
                              <span className="career-roadmap-period">
                                {step.period || `Step ${index + 1}`}
                              </span>
                              <strong>{step.title || "Learning milestone"}</strong>
                              <p>
                                {step.task || "Practise the skills you have learned."}
                              </p>
                            </li>
                          ))}
                        </ol>
                      ) : (
                        <p className="result-description">
                          Start with the fundamentals, practise core skills, and complete
                          a small project to explore whether this field interests you.
                        </p>
                      )}
                    </div>

                    <p className="career-score-note">
                      This score is a relative, questionnaire-based exploration guide.
                      It is not a probability of career success or a measure of your ability.
                    </p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty-note">No career suggestions were returned. Please try the questionnaire again.</p>
            )}
          </section>

          <div className="disclaimer-card">
            <span className="disclaimer-icon">ⓘ</span>
            <div>
              <h3>A note about your results</h3>
              <p>
                This is an exploratory questionnaire, not a validated
                psychometric or intelligence test. Your answers do not determine
                your personality, intelligence, or future career. Use these
                results as a starting point for reflection, discussion, and
                learning about different fields.
              </p>
            </div>
          </div>

          <div className="results-actions">
            <button className="primary-button" onClick={restartQuestionnaire}>
              Start again <span>↗</span>
            </button>
          </div>
        </section>

        <footer className="site-footer">
          <span>PATHFINDER<span className="brand-dot">.</span></span>
          <span>Discover your possibilities.</span>
        </footer>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" onClick={(event) => event.preventDefault()}>
          <span className="brand-mark">C</span>
          <span>Pathfinder<span className="brand-dot">.</span></span>
        </a>
        <a className="topbar-action" href="#questionnaire">Begin your journey <span>↗</span></a>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-line" /> A LITTLE ABOUT YOU</p>
          <h1>Find your path.<br />Start with <span>yourself.</span></h1>
          <p className="hero-description">
            Discover your interests, explore your reasoning skills, and reflect
            on how you approach everyday challenges. There are no perfect
            personalities or one-size-fits-all careers.
          </p>
          <div className="hero-points">
            <span><span className="point-check">✓</span> Personal interests</span>
            <span><span className="point-check">✓</span> Logical challenges</span>
            <span><span className="point-check">✓</span> Real-life scenarios</span>
          </div>
          <a className="hero-cta" href="#questionnaire">
            Explore your path <span>↗</span>
          </a>
          <p className="hero-meta">30 thoughtful questions <span>·</span> About 5–7 minutes</p>
        </div>

        <div className="hero-art" aria-hidden="true">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="art-sun" />
          <div className="art-card art-card-top">
            <span className="art-card-icon">✳</span>
            <span>Curiosity</span>
          </div>
          <div className="art-card art-card-bottom">
            <span className="art-card-icon">↗</span>
            <span>Possibility</span>
          </div>
          <div className="art-center">
            <span className="art-center-symbol">✦</span>
            <span>Your next<br />chapter</span>
          </div>
          <span className="art-spark spark-one">✳</span>
          <span className="art-spark spark-two">✦</span>
          <span className="art-spark spark-three">·</span>
        </div>
      </section>

      <section className="questionnaire-layout" id="questionnaire">
        <aside className="progress-sidebar">
          <p className="eyebrow">YOUR JOURNEY</p>
          <h3>One step at a time.</h3>
          <p className="sidebar-copy">
            Take your time. Choose the answer that feels most like you.
          </p>

          <div className="overall-progress">
            <div className="overall-progress-label">
              <span>Overall progress</span>
              <strong>{Math.round(progress)}%</strong>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <span className="progress-caption">
              {answeredCount} of {questions.length} answered
            </span>
          </div>

          <div className="step-list">
            {Object.entries(SECTION_INFO).map(([key, section]) => {
              const firstIndex = questions.findIndex((q) => q.section === key);
              const lastIndex = questions.findLastIndex
                ? questions.findLastIndex((q) => q.section === key)
                : questions.map((q) => q.section).lastIndexOf(key);
              const active =
                currentQuestion?.section === key;
              const completed =
                lastIndex >= 0 &&
                questions.slice(firstIndex, lastIndex + 1).every(
                  (q) => answers[q.id] !== undefined
                );

              return (
                <div
                  className={`step-item ${active ? "active" : ""} ${completed ? "completed" : ""}`}
                  key={key}
                >
                  <div className="step-number">
                    {completed ? "✓" : section.number}
                  </div>
                  <div>
                    <strong>{section.title}</strong>
                    <span>
                      {key === "personal"
                        ? "Interest preferences"
                        : key === "logical"
                        ? "Reasoning questions"
                        : "Everyday scenarios"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="sidebar-tip">
            <span>✦</span>
            <p><strong>Remember</strong><br />Be honest with yourself. This is about exploration, not judgment.</p>
          </div>
        </aside>

        <section className="question-panel">
          {currentQuestion && currentSection && (
            <>
              <div className="question-panel-top">
                <span className="section-pill">
                  SECTION {currentSection.number}
                </span>
                <span className="question-counter">
                  QUESTION <strong>{String(currentIndex + 1).padStart(2, "0")}</strong>
                  <span className="counter-divider">/</span>
                  {String(questions.length).padStart(2, "0")}
                </span>
              </div>

              <div className="question-heading">
                <p className="eyebrow">{currentSection.title}</p>
                <h2>{currentQuestion.text}</h2>
                <p className="question-subtitle">{currentSection.subtitle}</p>
              </div>

              <div className="options-list">
                {currentQuestion.options.map((option, index) => {
                  const selected = answers[currentQuestion.id] === option.id;

                  return (
                    <button
                      type="button"
                      key={option.id}
                      className={`option-card ${selected ? "selected" : ""}`}
                      onClick={() => handleAnswer(option.id)}
                      aria-pressed={selected}
                    >
                      <span className="option-letter">
                        {String.fromCharCode(65 + index)}
                      </span>
                      <span className="option-text">{option.text}</span>
                      <span className="option-radio">
                        {selected && <span />}
                      </span>
                    </button>
                  );
                })}
              </div>

              {error && <div className="inline-error">{error}</div>}

              <div className="question-footer">
                <button
                  type="button"
                  className="back-button"
                  onClick={() => {
                    setError("");
                    setCurrentIndex((index) => Math.max(0, index - 1));
                  }}
                  disabled={currentIndex === 0 || submitting}
                >
                  <span>←</span> Previous
                </button>

                <button
                  type="button"
                  className="primary-button"
                  onClick={handleNext}
                  disabled={submitting}
                >
                  {submitting
                    ? "Calculating..."
                    : currentIndex === questions.length - 1
                    ? "See my results"
                    : "Next question"}
                  {!submitting && <span>→</span>}
                </button>
              </div>

              <p className="privacy-note">
                <span>◇</span> Your answers are used to generate this exploration summary.
              </p>
            </>
          )}
        </section>
      </section>

      <footer className="site-footer">
        <span>PATHFINDER<span className="brand-dot">.</span></span>
        <span>Discover your possibilities.</span>
      </footer>
    </main>
  );
}

export default App;