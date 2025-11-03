"use client";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Document } from "@/lib/types";
import { format } from "date-fns";
import { Calendar, ExternalLink, FileText } from "lucide-react";

interface DocumentListProps {
  companyId: number;
  documents: Document[];
  loading: boolean;
}

export function DocumentList({
  companyId: _companyId,
  documents,
  loading,
}: DocumentListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-5 w-48 bg-muted rounded" />
              <div className="h-4 w-32 bg-muted rounded mt-2" />
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground py-8">
            No documents found for this company. Start extraction to discover
            PDFs.
          </p>
        </CardContent>
      </Card>
    );
  }

  // Group documents by fiscal year
  const documentsByYear = documents.reduce((acc, doc) => {
    const year = doc.fiscal_year;
    acc[year] ??= [];
    acc[year].push(doc);
    return acc;
  }, {} as Record<number, Document[]>);

  const sortedYears = Object.keys(documentsByYear)
    .map(Number)
    .sort((a, b) => b - a);

  return (
    <div className="space-y-6">
      {sortedYears.map((year) => (
        <div key={year}>
          <h3 className="text-lg font-semibold mb-4">Fiscal Year {year}</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {documentsByYear[year]!.map((doc) => (
              <Card key={doc.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-muted-foreground" />
                      <CardTitle className="text-lg">
                        {doc.document_type}
                      </CardTitle>
                    </div>
                    <Badge variant="secondary">FY {doc.fiscal_year}</Badge>
                  </div>
                  <CardDescription className="flex items-center gap-2">
                    <Calendar className="h-3 w-3" />
                    {doc.created_at
                      ? format(new Date(doc.created_at), "MMM dd, yyyy")
                      : "Unknown date"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline flex items-center gap-1"
                    >
                      View Source <ExternalLink className="h-3 w-3" />
                    </a>
                    {doc.file_path && (
                      <div className="text-xs text-muted-foreground">
                        Downloaded: {doc.file_path.split("/").pop()}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
