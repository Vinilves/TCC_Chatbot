import ReactMarkdown from "react-markdown";

import botIcon from "../assets/bot.png";
import userIcon from "../assets/user.png";

const SENTIMENT_LABELS = {
  positive: "Positivo",
  neutral: "Neutro",
  negative: "Negativo",
};

function DebugPanel({ debug }) {
  if (!debug) {
    return null;
  }

  const sentimentLabel =
    SENTIMENT_LABELS[debug.sentiment] ??
    debug.sentiment ??
    "Não identificado";

  const confidence = debug.sentiment_confidence;

  return (
    <div className="debug-panel">
      <div className="debug-panel-header">
        Análise de sentimento
      </div>

      <div className="debug-panel-content">
        <div className="debug-item">
          <span className="debug-label">
            Sentimento identificado
          </span>

          <span className="debug-value">
            {sentimentLabel}
          </span>
        </div>

        <div className="debug-item">
          <span className="debug-label">
            Confiança do modelo
          </span>

          <span className="debug-value">
            {typeof confidence === "number"
              ? confidence.toFixed(4)
              : "Não disponível"}
          </span>
        </div>
      </div>
    </div>
  );
}

function ChatArea({ messages, isLoading }) {
  return (
    <section className="chat-area">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`message-row ${
            msg.sender === "user"
              ? "user-row"
              : "bot-row"
          }`}
        >
          {msg.sender === "bot" && (
            <div className="bot-avatar">
              <img
                src={botIcon}
                alt="Bot Avatar"
                className="avatar-img"
              />
            </div>
          )}

          <div
            className={`message-bubble ${
              msg.sender === "user"
                ? "user-bubble"
                : "bot-bubble"
            }`}
          >
            <ReactMarkdown>{msg.text}</ReactMarkdown>

            <span className="message-time">
              {msg.time}
            </span>

            {msg.sender === "bot" && (
              <DebugPanel debug={msg.debug} />
            )}
          </div>

          {msg.sender === "user" && (
            <div className="user-avatar">
              <img
                src={userIcon}
                alt="User Avatar"
                className="avatar-img"
              />
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="message-row bot-row">
          <div className="bot-avatar">
            <img
              src={botIcon}
              alt="Bot Avatar"
              className="avatar-img"
            />
          </div>

          <div className="message-bubble bot-bubble typing-bubble">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default ChatArea;