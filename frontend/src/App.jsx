import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import BottomNav from "./components/BottomNav.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import ReviewPage from "./pages/ReviewPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ScorePage from "./pages/ScorePage.jsx";
import RemindersPage from "./pages/RemindersPage.jsx";

const TITLES = {
  "/dashboard": ["KhataAI", "Your digital ledger"],
  "/upload": ["Add entries", "Photograph a khata page"],
  "/review": ["Review entries", "Check before saving"],
  "/score": ["Trust score", "Built from your ledger history"],
  "/reminders": ["Reminders", "Outstanding udhaar"],
};

export default function App() {
  const location = useLocation();
  const [title, sub] = TITLES[location.pathname] || TITLES["/dashboard"];

  return (
    <div className="shell">
      <div className="topbar">
        <h1 className="topbar__title">{title}</h1>
        <p className="topbar__sub">{sub}</p>
      </div>

      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/score" element={<ScorePage />} />
        <Route path="/reminders" element={<RemindersPage />} />
      </Routes>

      <BottomNav />
    </div>
  );
}
