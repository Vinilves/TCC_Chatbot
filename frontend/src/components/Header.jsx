import logo from "../assets/logo.png";

function Header({ sessionActive, onSessionEnd }) {
  return (
    <header className="header">
      <div className="logo-container">
        <img src={logo} alt="Logo do chatbot" className="logo" />
      </div>

      {sessionActive && (
        <button className="end-session-button" onClick={onSessionEnd}>
          Encerrar sessão
        </button>
      )}
    </header>
  );
}

export default Header;
