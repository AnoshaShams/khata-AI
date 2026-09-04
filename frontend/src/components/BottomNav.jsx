import { NavLink } from "react-router-dom";

const navClass = ({ isActive }) => (isActive ? "active" : "");

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      <NavLink to="/dashboard" className={navClass}>
        <span>Khata</span>
      </NavLink>
      <NavLink to="/score" className={navClass}>
        <span>Trust Score</span>
      </NavLink>

      <NavLink to="/upload" className="fab" aria-label="Add ledger photo">
        <CameraIcon />
      </NavLink>

      <NavLink to="/reminders" className={navClass}>
        <span>Reminders</span>
      </NavLink>
    </nav>
  );
}

function CameraIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z" />
      <circle cx="12" cy="13" r="3.5" />
    </svg>
  );
}
