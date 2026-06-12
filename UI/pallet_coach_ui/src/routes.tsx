import { Navigate, Route, Routes } from "react-router-dom";
import { Home } from "./pages/Home";
import { Run } from "./pages/Run";

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/runs/:runId" element={<Run />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
