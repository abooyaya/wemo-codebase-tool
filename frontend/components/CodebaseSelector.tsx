"use client";

import { Badge } from "@/components/ui/badge";
import { ALL_CODEBASES } from "@/lib/api";

interface Props {
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function CodebaseSelector({ selected, onChange }: Props) {
  const allSelected = selected.length === 0 || selected.length === ALL_CODEBASES.length;

  const toggle = (name: string) => {
    if (allSelected) {
      // 從全選變成只選這一個
      onChange(ALL_CODEBASES.filter((c) => c !== name));
      return;
    }
    if (selected.includes(name)) {
      const next = selected.filter((c) => c !== name);
      onChange(next.length === ALL_CODEBASES.length ? [] : next);
    } else {
      const next = [...selected, name];
      onChange(next.length === ALL_CODEBASES.length ? [] : next);
    }
  };

  const isActive = (name: string) => allSelected || selected.includes(name);

  return (
    <div className="flex flex-wrap gap-2 px-4 py-2 border-b bg-muted/30">
      <span className="text-xs text-muted-foreground self-center mr-1">Codebase：</span>
      {ALL_CODEBASES.map((name) => (
        <Badge
          key={name}
          variant={isActive(name) ? "default" : "outline"}
          className="cursor-pointer select-none text-xs"
          onClick={() => toggle(name)}
        >
          {name}
        </Badge>
      ))}
      {!allSelected && (
        <Badge
          variant="outline"
          className="cursor-pointer select-none text-xs text-muted-foreground"
          onClick={() => onChange([])}
        >
          全選
        </Badge>
      )}
    </div>
  );
}
