import logo from "../assets/logo.png";

function Header({sessionActive, onSessionEnd, theme, onToggleTheme}) {
  const isDarkTheme = theme === "dark";

  return (
    <header className="header">
      <div className="logo-container">
        <img src={logo} alt="Logo do chatbot" className="logo" />
      </div>

      <div className="header-actions">
        <button
          type="button"
          className="theme-toggle-button"
          onClick={onToggleTheme}
          aria-label={
            isDarkTheme
              ? "Ativar tema claro"
              : "Ativar tema escuro"
          }
          title={
            isDarkTheme
              ? "Ativar tema claro"
              : "Ativar tema escuro"
          }
        >
          <span aria-hidden="true">
            {isDarkTheme ? "☀" : "☾"}
          </span>
        </button>

        {sessionActive && (
          <button
            type="button"
            className="end-session-button"
            onClick={onSessionEnd}
          >
            Encerrar sessão
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;
