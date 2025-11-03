"use client";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { CompiledStatement } from "@/lib/types";
import { formatCurrency } from "@/lib/utils/formatters";
import { useMemo } from "react";

interface FinancialStatementTableProps {
  statement: CompiledStatement;
}

interface StatementRow {
  lineItem: string;
  values: Array<{ year: string; value: number | null; restated?: boolean }>;
  level?: number;
  isTotal?: boolean;
}

interface LineItemData {
  name?: string;
  lineItem?: string;
  level?: number;
  isTotal?: boolean;
  [key: string]: unknown; // For year values and year_restated flags
}

export function FinancialStatementTable({
  statement,
}: FinancialStatementTableProps) {
  const { rows, years } = useMemo(() => {
    const data = statement.data;
    if (!data || typeof data !== "object") {
      return { rows: [], years: [] };
    }

    // Extract years from the data structure
    // Data format can vary, so we handle multiple possible structures
    const yearSet = new Set<string>();
    const allRows: StatementRow[] = [];

    // Common data formats:
    // 1. { "2024": {...}, "2023": {...} }
    // 2. { "lineItems": [{ "name": "...", "2024": ..., "2023": ... }] }
    // 3. { "columns": ["2024", "2023"], "rows": [...] }

    if (Array.isArray(data.lineItems)) {
      // Format 2
      data.lineItems.forEach((item: unknown) => {
        if (
          !item ||
          typeof item !== "object" ||
          !("name" in item || "lineItem" in item)
        ) {
          return;
        }

        const lineItemData = item as LineItemData;
        const row: StatementRow = {
          lineItem:
            typeof lineItemData.name === "string"
              ? lineItemData.name
              : typeof lineItemData.lineItem === "string"
              ? lineItemData.lineItem
              : "",
          values: [],
          level:
            typeof lineItemData.level === "number" ? lineItemData.level : 0,
          isTotal:
            typeof lineItemData.isTotal === "boolean"
              ? lineItemData.isTotal
              : false,
        };

        Object.keys(lineItemData).forEach((key) => {
          if (
            key !== "name" &&
            key !== "lineItem" &&
            key !== "level" &&
            key !== "isTotal" &&
            !key.endsWith("_restated")
          ) {
            const year = key;
            yearSet.add(year);
            const yearValue: unknown = lineItemData[key];
            const restatedKey = `${key}_restated`;
            const restatedValue: unknown = lineItemData[restatedKey];

            row.values.push({
              year,
              value: typeof yearValue === "number" ? yearValue : null,
              restated:
                typeof restatedValue === "boolean" ? restatedValue : false,
            });
          }
        });

        allRows.push(row);
      });
    } else {
      // Format 1 or 3 - try to extract structure
      Object.keys(data).forEach((key) => {
        if (key === "columns") {
          // Format 3
          (data.columns as string[]).forEach((year) => yearSet.add(year));
        } else if (key === "rows" && Array.isArray(data.rows)) {
          data.rows.forEach((rowData: Record<string, unknown>) => {
            const nameValue: unknown = rowData.name;
            const lineItemValue: unknown = rowData.lineItem;
            const levelValue: unknown = rowData.level;
            const isTotalValue: unknown = rowData.isTotal;

            const row: StatementRow = {
              lineItem:
                typeof nameValue === "string"
                  ? nameValue
                  : typeof lineItemValue === "string"
                  ? lineItemValue
                  : "",
              values: [],
              level: typeof levelValue === "number" ? levelValue : 0,
              isTotal: typeof isTotalValue === "boolean" ? isTotalValue : false,
            };

            (data.columns as string[]).forEach((year) => {
              const yearValue: unknown = rowData[year];
              const restatedValue: unknown = rowData[`${year}_restated`];

              row.values.push({
                year,
                value: typeof yearValue === "number" ? yearValue : null,
                restated:
                  typeof restatedValue === "boolean" ? restatedValue : false,
              });
            });

            allRows.push(row);
          });
        } else if (typeof data[key] === "object" && data[key] !== null) {
          // Format 1 - each year is a key
          yearSet.add(key);
        }
      });

      // If we have years but no rows yet, try to build rows from line items
      if (yearSet.size > 0 && allRows.length === 0) {
        const lineItemMap = new Map<string, StatementRow>();

        Object.keys(data).forEach((key) => {
          if (yearSet.has(key)) {
            const yearData = data[key] as Record<string, unknown>;
            Object.keys(yearData).forEach((lineItemName) => {
              if (!lineItemMap.has(lineItemName)) {
                lineItemMap.set(lineItemName, {
                  lineItem: lineItemName,
                  values: [],
                });
              }
              const row = lineItemMap.get(lineItemName)!;
              const value: unknown = yearData[lineItemName];
              row.values.push({
                year: key,
                value: typeof value === "number" ? value : null,
              });
            });
          }
        });

        allRows.push(...Array.from(lineItemMap.values()));
      }
    }

    const sortedYears = Array.from(yearSet).sort((a, b) => {
      const yearA = parseInt(a);
      const yearB = parseInt(b);
      return isNaN(yearA) || isNaN(yearB) ? a.localeCompare(b) : yearB - yearA;
    });

    // Sort rows by level and name
    allRows.sort((a, b) => {
      if ((a.level ?? 0) !== (b.level ?? 0)) {
        return (a.level ?? 0) - (b.level ?? 0);
      }
      return a.lineItem.localeCompare(b.lineItem);
    });

    return { rows: allRows, years: sortedYears };
  }, [statement.data]);

  if (years.length === 0) {
    return (
      <div className="rounded-md border p-8 text-center text-muted-foreground">
        No financial data available for this statement.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="sticky left-0 z-10 bg-background min-w-[300px]">
              Line Item
            </TableHead>
            {years.map((year) => (
              <TableHead key={year} className="text-right min-w-[120px]">
                {year}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, index) => (
            <TableRow
              key={`${row.lineItem}-${index}`}
              className={row.isTotal ? "font-bold bg-muted/50" : ""}
            >
              <TableCell
                className={`sticky left-0 z-10 bg-background ${
                  row.level ? `pl-${(row.level || 0) * 4}` : ""
                }`}
                style={{ paddingLeft: `${(row.level ?? 0) * 16 + 16}px` }}
              >
                <div className="flex items-center gap-2">
                  {row.lineItem}
                  {row.values.some((v) => v.restated) && (
                    <Badge variant="outline" className="text-xs">
                      Restated
                    </Badge>
                  )}
                </div>
              </TableCell>
              {years.map((year) => {
                const valueData = row.values.find((v) => v.year === year);
                const value = valueData?.value;

                return (
                  <TableCell key={year} className="text-right font-mono">
                    {value !== null && value !== undefined
                      ? formatCurrency(value)
                      : "-"}
                    {valueData?.restated && (
                      <span className="ml-1 text-xs text-muted-foreground">
                        *
                      </span>
                    )}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
