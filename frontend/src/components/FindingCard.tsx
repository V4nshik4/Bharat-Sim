import { CircleAlert, FileSearch, CheckCircle2 } from "lucide-react";
import { type Finding, cls } from "../api";

interface FindingCardProps {
  finding: Finding;
}

export default function FindingCard({ finding: f }: FindingCardProps) {
  return (
    <article className="finding-card">
      <div className="finding-top">
        <span className={"severity-icon " + cls(f.severity)}>
          <CircleAlert size={17} />
        </span>
        <div className="finding-title">
          <span className="finding-kind">{f.kind.toUpperCase() + " · " + f.id}</span>
          <h3>{f.title}</h3>
        </div>
        <span className={"risk-badge " + cls(f.severity)}>{f.severity}</span>
      </div>
      <p>{f.explanation}</p>
      <div className="evidence-box">
        <div>
          <FileSearch size={14} /> SOURCE EVIDENCE
        </div>
        {f.evidence.map((ev, i) => (
          <code key={i}>{"L" + ev.line + ": " + ev.text}</code>
        ))}
      </div>
      <div className="recommendation">
        <CheckCircle2 size={16} />
        <span>
          <b>Suggested next step</b>
          {f.recommendation}
        </span>
      </div>
    </article>
  );
}
