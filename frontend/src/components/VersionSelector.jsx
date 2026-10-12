function VersionSelector({ selectedVersion, onVersionChange, disabled }) {
  
  function handleChange(event) {
    onVersionChange(event.target.value);
  }

  return (
    <div className="version-selector">
      <select
        value={selectedVersion || ""}
        onChange={handleChange}
        disabled={disabled}
        data-selected={selectedVersion ? "true" : "false"}
        aria-label="Selecionar versão do chatbot"
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
