import { AlertTriangle } from "lucide-react";
import { Link, useRouteError } from "react-router-dom";

export function RouteError() {
  const error = useRouteError();
  return <main className="route-error"><AlertTriangle aria-hidden="true" /><h1>Control Center route failed</h1><p>{error instanceof Error ? error.message : "The requested route could not be rendered."}</p><Link to="/command-center">Return to Command Center</Link></main>;
}
