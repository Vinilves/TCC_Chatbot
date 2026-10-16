import { useEffect, useState } from "react";

import Header from "./components/Header";
import ChatArea from "./components/ChatArea";
import ChatInput from "./components/ChatInput";

import {startSession, sendMessage, endSession} from "./services/chatService";

import attentionIcon from "./assets/atention.png";
import checkIcon from "./assets/check.png";

import "./App.css";

const PYTHON_DOCUMENTATION_URL =
  "https://docs.python.org/pt-br/3/tutorial/";

const DEBUG_MODE =
  new URLSearchParams(window.location.search).get("debug") === "true";

const PARTICIPANT_ID_KEY = "chatbot-participant-id";
const BASE_COMPLETED_KEY = "chatbot-base-completed";
const EXPERIMENT_COMPLETED_KEY = "chatbot-experiment-completed";

function createParticipantId() {
  if (
    typeof crypto === "undefined" ||
    typeof crypto.randomUUID !== "function"
  ) {
    throw new Error(
      "Não foi possível gerar o identificador anônimo do participante."
    );
  }

  return crypto.randomUUID();
}

function getStoredValue(key, fallback = "") {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

function getOrCreateParticipantId() {
  try {
    const storedId = localStorage.getItem(PARTICIPANT_ID_KEY);

    if (storedId) {
      return storedId;
    }

    const participantId = createParticipantId();

    localStorage.setItem(PARTICIPANT_ID_KEY, participantId);

    return participantId;
  } catch {
    return createParticipantId();
  }
}

function getCurrentTime() {
  return `Hoje ${new Date().toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  })}`;
}

function formatDuration(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const formattedMinutes = String(minutes).padStart(2, "0");
  const formattedSeconds = String(seconds).padStart(2, "0");

  if (hours > 0) {
    return `${String(hours).padStart(2, "0")}:${formattedMinutes}:${formattedSeconds}`;
  }

  return `${formattedMinutes}:${formattedSeconds}`;
}

function App() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("chatbot-theme") === "dark"
        ? "dark"
        : "light";
    } catch {
      return "light";
    }
  });

  const [participantId, setParticipantId] = useState(() =>
    getOrCreateParticipantId()
  );

  const [baseCompleted, setBaseCompleted] = useState(
    () => getStoredValue(BASE_COMPLETED_KEY) === "true"
  );

  const [experimentCompleted, setExperimentCompleted] = useState(
    () => getStoredValue(EXPERIMENT_COMPLETED_KEY) === "true"
  );

  const [selectedVersion, setSelectedVersion] = useState("");
  const [completedVersion, setCompletedVersion] = useState("");
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [showEndConfirmation, setShowEndConfirmation] = useState(false);
  const [showSessionSummary, setShowSessionSummary] = useState(false);
  const [sessionDuration, setSessionDuration] = useState(null);
  const [endSessionError, setEndSessionError] = useState("");
  const [isEndingSession, setIsEndingSession] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);

    try {
      localStorage.setItem("chatbot-theme", theme);
    } catch {

    }
  }, [theme]);

  useEffect(() => {
    try {
      localStorage.setItem(
        BASE_COMPLETED_KEY,
        String(baseCompleted)
      );

      localStorage.setItem(
        EXPERIMENT_COMPLETED_KEY,
        String(experimentCompleted)
      );
    } catch {

    }
  }, [baseCompleted, experimentCompleted]);

  useEffect(() => {
    function handleBeforeUnload(event) {
      if (sessionActive) {
        event.preventDefault();
        event.returnValue = "";
      }
    }

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener(
        "beforeunload",
        handleBeforeUnload
      );
    };
  }, [sessionActive]);


  useEffect(() => {
    if (!showEndConfirmation && !showSessionSummary) {
      return undefined;
    }

    function handleEscape(event) {
      if (event.key === "Escape" && !isEndingSession) {
        setShowEndConfirmation(false);
        setShowSessionSummary(false);
        setEndSessionError("");
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [
    showEndConfirmation,
    showSessionSummary,
    isEndingSession,
  ]);

  function handleToggleTheme() {
    setTheme((currentTheme) =>
      currentTheme === "light" ? "dark" : "light"
    );
  }

  function handleVersionChange(version) {
    if (
      sessionActive ||
      isLoading ||
      isEndingSession ||
      experimentCompleted
    ) {
      return;
    }

    if (baseCompleted && version !== "B") {
      return;
    }

    if (!baseCompleted && version !== "A") {
      return;
    }

    setSelectedVersion(version);
  }


  async function handleSendMessage(messageText) {
    if (
      !selectedVersion ||
      isLoading ||
      isEndingSession ||
      experimentCompleted
    ) {
      return false;
    }

    if (baseCompleted && selectedVersion !== "B") {
      return false;
    }

    if (!baseCompleted && selectedVersion !== "A") {
      return false;
    }

    setIsLoading(true);

    let currentSessionId = sessionId;

    try {
    
      if (!currentSessionId) {
        const session = await startSession(
          participantId,
          selectedVersion
        );

        currentSessionId = session.session_id;

        if (!currentSessionId) {
          throw new Error(
            "O backend não retornou o identificador da sessão."
          );
        }

        setSessionId(currentSessionId);
        setSessionActive(true);
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          text: messageText,
          sender: "user",
          time: getCurrentTime(),
        },
      ]);

      const result = await sendMessage(
        currentSessionId,
        messageText,
        DEBUG_MODE
      );

      if (!result || typeof result.answer !== "string") {
        throw new Error(
          "O backend não retornou uma resposta válida."
        );
      }

      let answerText = result.answer;


      if (
        typeof result.code === "string" &&
        result.code.trim()
      ) {
        answerText += `\n\n\`\`\`python\n${result.code}\n\`\`\``;
      }


      if (result.documentation_url) {
        answerText += `\n\n[Consulte a documentação oficial do Python](${result.documentation_url})`;
      } else if (result.source) {
        answerText += `\n\n[Consulte a documentação oficial do Python](${PYTHON_DOCUMENTATION_URL})`;
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          text: answerText,
          sender: "bot",
          time: getCurrentTime(),
          debug:
            DEBUG_MODE && selectedVersion === "B"
              ? result.debug ?? null
              : null,
        },
      ]);

      return true;
    } catch (error) {
      console.error(
        "Erro na comunicação com o chatbot:",
        error
      );

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          text: currentSessionId
            ? "Não foi possível obter uma resposta do chatbot. Tente enviar sua mensagem novamente."
            : "Não foi possível iniciar a sessão. Verifique a conexão com o servidor e tente novamente.",
          sender: "bot",
          time: getCurrentTime(),
        },
      ]);

      return false;
    } finally {
      setIsLoading(false);
    }
  }


  function handleSessionEnd() {
    if (!sessionActive || !sessionId) {
      return;
    }

    setEndSessionError("");
    setShowEndConfirmation(true);
  }

  function handleCancelEndSession() {
    if (isEndingSession) {
      return;
    }

    setShowEndConfirmation(false);
    setEndSessionError("");
  }


  async function handleConfirmEndSession() {
    if (!sessionId || isLoading || isEndingSession) {
      if (isLoading) {
        setEndSessionError(
          "Aguarde o processamento da mensagem antes de encerrar a sessão."
        );
      }

      return;
    }

    setIsEndingSession(true);
    setEndSessionError("");

    try {
      const result = await endSession(sessionId);

      if (
        !result ||
        result.status !== "completed" ||
        typeof result.duration_seconds !== "number"
      ) {
        throw new Error(
          "O servidor não confirmou corretamente o encerramento."
        );
      }

      const versionJustCompleted = selectedVersion;

      setCompletedVersion(versionJustCompleted);
      setSessionDuration(result.duration_seconds);

      setSessionActive(false);
      setSessionId(null);
      setMessages([]);

      if (versionJustCompleted === "A") {
        setBaseCompleted(true);
        setSelectedVersion("B");
      } else {
        setExperimentCompleted(true);
        setSelectedVersion("");
      }

      setShowEndConfirmation(false);
      setShowSessionSummary(true);
    } catch (error) {
      console.error(
        "Erro ao encerrar a sessão:",
        error
      );

      setEndSessionError(
        "Não foi possível encerrar a sessão. Verifique sua conexão e tente novamente."
      );
    } finally {
      setIsEndingSession(false);
    }
  }

  function handleCloseSummary() {
    setShowSessionSummary(false);
    setSessionDuration(null);

    if (experimentCompleted) {
      const nextParticipantId = createParticipantId();

      setParticipantId(nextParticipantId);
      setBaseCompleted(false);
      setExperimentCompleted(false);
      setSelectedVersion("");
      setCompletedVersion("");

      try {
        localStorage.setItem(
          PARTICIPANT_ID_KEY,
          nextParticipantId
        );

        localStorage.setItem(BASE_COMPLETED_KEY, "false");
        localStorage.setItem(EXPERIMENT_COMPLETED_KEY, "false");
      } catch {

      }
    }
  }

  const isVersionSelectionDisabled =
    sessionActive ||
    isLoading ||
    isEndingSession ||
    experimentCompleted;

  return (
    <div className="app">
      <Header
        sessionActive={sessionActive}
        onSessionEnd={handleSessionEnd}
        theme={theme}
        onToggleTheme={handleToggleTheme}
      />

      <main className="chat-container">
        <ChatArea
          messages={messages}
          isLoading={isLoading}
        />

        <ChatInput
          version={selectedVersion}
          sessionActive={sessionActive}
          isLoading={isLoading || isEndingSession}
          onVersionChange={handleVersionChange}
          onSendMessage={handleSendMessage}
        />
      </main>


      {showEndConfirmation && (
        <div
          className="modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget &&
              !isEndingSession
            ) {
              handleCancelEndSession();
            }
          }}
        >
          <section
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="end-session-title"
            aria-describedby="end-session-description"
          >
            <div className="modal-icon modal-icon-warning">
              <img
                src={attentionIcon}
                alt=""
                aria-hidden="true"
              />
            </div>

            <h2 id="end-session-title">
              Encerrar sessão?
            </h2>

            <p id="end-session-description">
              Deseja realmente encerrar sua sessão de conversa?
              {selectedVersion === "A"
                ? " Após a conclusão, você poderá testar a versão B."
                : " Após a conclusão, sua participação no experimento será finalizada."}
            </p>

            {endSessionError && (
              <div className="modal-error" role="alert">
                {endSessionError}
              </div>
            )}

            <div className="modal-actions">
              <button
                type="button"
                className="modal-button modal-button-secondary"
                onClick={handleCancelEndSession}
                disabled={isEndingSession}
              >
                Continuar conversando
              </button>

              <button
                type="button"
                className="modal-button modal-button-danger"
                onClick={handleConfirmEndSession}
                disabled={isEndingSession || isLoading}
              >
                {isEndingSession
                  ? "Encerrando..."
                  : "Encerrar sessão"}
              </button>
            </div>
          </section>
        </div>
      )}


      {showSessionSummary && sessionDuration !== null && (
        <div className="modal-overlay">
          <section
            className="modal-card modal-card-summary"
            role="dialog"
            aria-modal="true"
            aria-labelledby="session-summary-title"
            aria-describedby="session-summary-description"
          >
            <div className="modal-icon modal-icon-success">
              <img
                src={checkIcon}
                alt=""
                aria-hidden="true"
              />
            </div>

            <h2 id="session-summary-title">
              Sessão encerrada!
            </h2>

            <p id="session-summary-description">
              {completedVersion === "B"
                ? "Sua participação no experimento foi concluída."
                : "A versão A foi concluída. Agora você pode prosseguir para a versão B."}
            </p>

            <div className="duration-display">
              <span className="duration-label">
                Duração da sessão
              </span>

              <strong>
                {formatDuration(sessionDuration)}
              </strong>
            </div>

            <button
              type="button"
              className="modal-button modal-button-primary"
              onClick={handleCloseSummary}
              autoFocus
            >
              Concluir
            </button>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;