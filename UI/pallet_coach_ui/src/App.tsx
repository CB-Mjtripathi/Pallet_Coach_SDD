import { AppShell } from "./components/AppShell";
import { AppRoutes } from "./routes";

export default function App(): JSX.Element {
  return (
    <AppShell>
      <AppRoutes />
    </AppShell>
  );
}
