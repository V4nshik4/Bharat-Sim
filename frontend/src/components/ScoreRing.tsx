import type { CSSProperties } from "react";

interface ScoreRingProps {
  score: number;
}

export default function ScoreRing({ score }: ScoreRingProps) {
  return (
    <div
      className="score-ring"
      style={{ "--score": `${score}%` } as CSSProperties}
    >
      <span>
        <b>{score}</b>
        <small>/100</small>
      </span>
    </div>
  );
}
