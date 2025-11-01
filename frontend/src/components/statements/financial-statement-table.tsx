"use client";

import { useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { CompiledStatement } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils/formatters";

interface FinancialStatementTableProps {
  statement: CompiledStatement;
}

interface StatementRow {
  lineItem: string;
  values: Array<{ year: string; value: number | null; restated?: boolean }>;
  level?: number;
  isTotal?: boolean;
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
      data.lineItems.forEach((item: any) => {
        const row: StatementRow = {
          lineItem: item.name || item.lineItem || "",
          values: [],
          level: item.level || 0,
          isTotal: item.isTotal || false,
        };

        Object.keys(item).forEach((key) => {
          if (key !== "name" && key !== "lineItem" && key !== "level" && key !== "isTotal") {
            const year = key;
            yearSet.add(year);
            row.values.push({
              year,
              value: typeof item[key] === "number" ? item[key] : null,
              restated: item[`${key}_restated`] || false,
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
          (data.rows as any[]).forEach((rowData: any) => {
            const row: StatementRow = {
              lineItem: rowData.name || rowData.lineItem || "",
              values: [],
              level: rowData.level || 0,
              isTotal: rowData.isTotal || false,
            };

            (data.columns as string[]).forEach((year) => {
              row.values.push({
                year,
                value: rowData[year] !== undefined ? rowData[year] : null,
                restated: rowData[`${year}_restated`] || false,
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
            const yearData = data[key] as Record<string, any>;
            Object.keys(yearData).forEach((lineItemName) => {
              if (!lineItemMap.has(lineItemName)) {
                lineItemMap.set(lineItemName, {
                  lineItem: lineItemName,
                  values: [],
                });
              }
              const row = lineItemMap.get(lineItemName)!;
              row.values.push({
                year: key,
                value: yearData[lineItemName],
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
      if ((a.level || 0) !== (b.level || 0)) {
        return (a.level || 0) - (b.level || 0);
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
                style={{ paddingLeft: `${(row.level || 0) * 16 + 16}px` }}
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
                      <span className="ml-1 text-xs text-muted-foreground">*</span>
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
