import { useNavigate } from "react-router-dom";
import { type Run, type Persona, date, displayRunStatus } from "../api";

interface RunsTableProps {
  runs: Run[];
  personas: Persona[];
}

export default function RunsTable({ runs, personas }: RunsTableProps) {
  const navigate = useNavigate();

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>APPLICATION / RUN</th>
            <th>PERSONA</th>
            <th>CREATED</th>
            <th>STATUS</th>
            <th>APK SHA-256</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => {
            const personaName = (personas.find((p) => p.id === r.persona_id) || { name: r.persona_id }).name;
            const statusClass =
              r.status === "completed"
                ? "done"
                : r.status === "failed" || r.status === "timed_out"
                ? "failed"
                : "pending";

            return (
              <tr key={r.id}>
                <td>
                  <button
                    className="text-button"
                    onClick={() => navigate(`/runs/${encodeURIComponent(r.id)}`)}
                  >
                    <b>{r.apk_name || "APK not attached"}</b>
                    <small className="table-sub">{r.id}</small>
                  </button>
                </td>
                <td>{personaName}</td>
                <td>{date(r.created_at)}</td>
                <td>
                  <span className={"run-status " + statusClass}>
                    {displayRunStatus(r.status)}
                  </span>
                </td>
                <td>
                  <code>{r.apk_sha256?.slice(0, 16) || "—"}</code>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
