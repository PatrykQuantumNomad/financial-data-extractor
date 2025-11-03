"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useCompanies } from "@/lib/hooks";
import { isQueryLoading } from "@/lib/utils/query-utils";
import type { Company } from "@/lib/types";
import { Building2, ChevronRight } from "lucide-react";
import { ExtractionControls } from "./extraction-controls";
import { DocumentActions } from "./document-actions";

export function ExtractionPageContent() {
  const companiesQuery = useCompanies();
  const { data: companies } = companiesQuery;
  const isLoading = isQueryLoading(companiesQuery);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-6 w-32 bg-muted rounded" />
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (!companies || companies.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground py-8">
            No companies found. Add companies through the backend API.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle>Select Company</CardTitle>
            <CardDescription>
              Choose a company to extract data for
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {companies.map((company) => {
              const isSelected = selectedCompany?.id === company.id;
              return (
                <Button
                  key={company.id}
                  variant={isSelected ? "default" : "outline"}
                  className={`w-full justify-start transition-all duration-200 relative group ${
                    isSelected
                      ? "bg-primary text-primary-foreground shadow-lg border-2 border-primary-foreground/30 font-semibold ring-2 ring-primary ring-offset-2 hover:shadow-xl hover:scale-[1.02] hover:bg-primary/90 active:scale-[0.98]"
                      : "hover:bg-accent hover:text-accent-foreground hover:shadow-md hover:scale-[1.02] active:scale-[0.98]"
                  }`}
                  onClick={() => setSelectedCompany(company)}
                >
                  {isSelected && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-primary-foreground/60 rounded-r" />
                  )}
                  <Building2
                    className={`mr-2 h-4 w-4 flex-shrink-0 ${
                      isSelected ? "text-primary-foreground" : ""
                    }`}
                  />
                  <span className={`flex-1 text-left ${isSelected ? "font-semibold" : ""}`}>
                    {company.name}
                  </span>
                  <ChevronRight
                    className={`h-4 w-4 flex-shrink-0 ml-auto transition-opacity duration-200 ${
                      isSelected
                        ? "text-primary-foreground opacity-100"
                        : "opacity-0 group-hover:opacity-100"
                    }`}
                  />
                </Button>
              );
            })}
          </CardContent>
        </Card>
      </div>

      <div className="lg:col-span-2">
        {selectedCompany ? (
          <div className="space-y-6">
            <ExtractionControls company={selectedCompany} />
            <DocumentActions company={selectedCompany} />
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground py-8">
                Select a company from the list to start extraction
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
