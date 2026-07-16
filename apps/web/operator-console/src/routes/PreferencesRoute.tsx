import { useEffect, useState } from "react";
import { MonitorCog } from "lucide-react";

import { PageHeading } from "../components";

type Density = "comfortable" | "compact";

export function PreferencesRoute() {
  const [density, setDensity] = useState<Density>(() => localStorage.getItem("project-ai-density") === "compact" ? "compact" : "comfortable");
  const [reducedMotion, setReducedMotion] = useState(() => localStorage.getItem("project-ai-reduced-motion") === "true");

  useEffect(() => {
    document.documentElement.dataset.density = density;
    localStorage.setItem("project-ai-density", density);
  }, [density]);

  useEffect(() => {
    document.documentElement.dataset.reducedMotion = String(reducedMotion);
    localStorage.setItem("project-ai-reduced-motion", String(reducedMotion));
  }, [reducedMotion]);

  return <div className="console-page"><PageHeading title="Display preferences" description="Browser-local presentation settings for this device." />
    <div className="preference-notice"><MonitorCog /><div><strong>Local preference boundary</strong><p>These settings stay in this browser. They do not change your account, role, permissions, or governance authority.</p></div></div>
    <section className="preference-panel"><div><h2>Interface density</h2><p>Choose how much information is shown in each view.</p></div><fieldset><legend className="sr-only">Interface density</legend><label><input type="radio" name="density" checked={density === "comfortable"} onChange={() => setDensity("comfortable")} /> Comfortable</label><label><input type="radio" name="density" checked={density === "compact"} onChange={() => setDensity("compact")} /> Compact</label></fieldset></section>
    <section className="preference-panel"><div><h2>Motion</h2><p>Reduce non-essential interface transitions on this device.</p></div><label className="switch-row"><input type="checkbox" checked={reducedMotion} onChange={(event) => setReducedMotion(event.target.checked)} /> Reduce motion</label></section>
  </div>;
}
