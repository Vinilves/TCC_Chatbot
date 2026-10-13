import VersionSelector from "./VersionSelector";

function ChatInput({version, sessionActive, isLoading, onVersionChange, onSendMessage,}) {
  async function handleSubmit(event) {
    event.preventDefault();

    const input = event.currentTarget.elements.message;
    const message = input.value.trim();

    if (!message || !version || isLoading) {
      return;
    }

    const success = await onSendMessage(message);
    if (success) {
      input.value = "";
    }
  }

  return (
    <form className="input-wrapper" onSubmit={handleSubmit}>
      <input
        type="text"
        name="message"
        placeholder="Digite aqui sua dúvida sobre Python"
        className="message-input"
        autoComplete="off"
        disabled={isLoading}
      />

      <VersionSelector
        selectedVersion={version}
        onVersionChange={onVersionChange}
        disabled={sessionActive || isLoading}
      />

      <button
        type="submit"
        className="send-button"
        disabled={!version || isLoading}
      >
        {isLoading ? "AGUARDE..." : "ENVIAR"}
      </button>
    </form>
  );
}

export default ChatInput;
