"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { StatementType } from "@/lib/types";

interface StatementTypeNavProps {
  companyId: number;
  currentType: StatementType;
}

const STATEMENT_TYPES: Array<{ type: StatementType; label: string }> = [
  { type: "income_statement", label: "Income Statement" },
  { type: "balance_sheet", label: "Balance Sheet" },
  { type: "cash_flow_statement", label: "Cash Flow" },
];

export function StatementTypeNav({ companyId, currentType }: StatementTypeNavProps) {
  return (
    <div className="flex gap-2 border-b">
      {STATEMENT_TYPES.map(({ type, label }) => {
        const isActive = type === currentType;
        return (
          <Link
            key={type}
            href={`/companies/${companyId}/statements/${type}`}
          >
            <Button
              variant={isActive ? "default" : "ghost"}
              className={cn(
                "rounded-b-none border-b-2 border-transparent",
                isActive && "border-primary"
              )}
            >
              {label}
            </Button>
          </Link>
        );
      })}
    </div>
  );
}
