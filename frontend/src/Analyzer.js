import React, { useState, useEffect } from "react";

function Analyzer() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [history, setHistory] = useState(() => {
    // Load history from localStorage when app starts
    const saved = localStorage.getItem("history");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    // Save history to localStorage whenever it changes
    localStorage.setItem("history", JSON.stringify(history));
  }, [history]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await response.json();
      const message = data.message;

      setAnswer(message);
      setHistory(prev => [...prev, { question, answer: message }]);
      setQuestion("");
    } catch (error) {
      console.error("Error:", error);
      setAnswer("Backend not reachable");
    }
  };

  return (
    <div>
      <h1>AI Business Advisory App</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>

      <p><strong>Latest Answer:</strong> {answer}</p>

      <h2>History</h2>
      <ul>
        {history.map((item, index) => (
          <li key={index}>
            <strong>Q:</strong> {item.question} <br />
            <strong>A:</strong> {item.answer}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Analyzer;
