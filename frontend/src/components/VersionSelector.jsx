function VersionSelector({ selectedVersion }) {
  return (
    <div className="version-selector">
      <select
        value={selectedVersion || ""}
        disabled
        data-selected={selectedVersion ? "true" : "false"}
        aria-label="Versão atual do chatbot"
      >
        <option value="" disabled>
          VERSÃO
        </option>

        <option value="A">
          VERSÃO A
        </option>

        <option value="B">
          VERSÃO B
        </option>
      </select>
    </div>
  );
}

export default VersionSelector;
