"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useCompanies } from "@/lib/hooks";
import { getErrorMessage, isQueryLoading } from "@/lib/utils/query-utils";
import { Building2, ExternalLink, FileText, ChevronRight } from "lucide-react";

export function CompanyList() {
  const companiesQuery = useCompanies();
  const { data: companies, error } = companiesQuery;
  const isLoading = isQueryLoading(companiesQuery);

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-6 w-32 bg-muted rounded" />
              <div className="h-4 w-24 bg-muted rounded mt-2" />
            </CardHeader>
            <CardContent>
              <div className="h-4 w-full bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-destructive">
            Error: {getErrorMessage(error, "Failed to load companies")}
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!companies || companies.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center py-8">
            No companies found. Add companies through the backend API.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {companies.map((company) => (
        <Card
          key={company.id}
          className="hover:shadow-xl transition-all duration-200 hover:border-primary/50 hover:-translate-y-1 group hover:shadow-primary/5"
        >
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-muted-foreground" />
                <CardTitle className="text-xl">{company.name}</CardTitle>
              </div>
              {company.primary_ticker && (
                <Badge variant="secondary">{company.primary_ticker}</Badge>
              )}
            </div>
            <CardDescription>
              ID: {company.id} • Fiscal Year: {new Date().getFullYear()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <a
                  href={company.ir_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline flex items-center gap-1"
                  onClick={(e) => e.stopPropagation()}
                >
                  Investor Relations <ExternalLink className="h-3 w-3" />
                </a>
              </div>
              <Link href={`/companies/${company.id}/statements/income_statement`}>
                <Button className="w-full group-hover:bg-primary/90 transition-colors flex items-center justify-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span className="flex-1 text-left">View Statements</span>
                  <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
