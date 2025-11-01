"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { companiesApi } from "@/lib/api/companies";
import { ExtractionControls } from "./extraction-controls";
import type { Company } from "@/lib/types";
import { Building2 } from "lucide-react";

export function ExtractionPageContent() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

  useEffect(() => {
    async function fetchCompanies() {
      try {
        const data = await companiesApi.getAll();
        setCompanies(data);
      } catch (error) {
        console.error("Failed to load companies:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchCompanies();
  }, []);

  if (loading) {
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

  if (companies.length === 0) {
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
            <CardDescription>Choose a company to extract data for</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {companies.map((company) => {
              const isSelected = selectedCompany?.id === company.id;
              return (
                <Button
                  key={company.id}
                  variant={isSelected ? "default" : "outline"}
                  className={`w-full justify-start transition-all duration-200 relative ${
                    isSelected
                      ? "bg-primary text-primary-foreground shadow-lg border-2 border-primary-foreground/30 font-semibold ring-2 ring-primary ring-offset-2"
                      : "hover:bg-accent hover:text-accent-foreground"
                  }`}
                  onClick={() => setSelectedCompany(company)}
                >
                  {isSelected && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-primary-foreground/60 rounded-r" />
                  )}
                  <Building2
                    className={`mr-2 h-4 w-4 ${
                      isSelected ? "text-primary-foreground" : ""
                    }`}
                  />
                  <span className={isSelected ? "font-semibold" : ""}>{company.name}</span>
                </Button>
              );
            })}
          </CardContent>
        </Card>
      </div>

      <div className="lg:col-span-2">
        {selectedCompany ? (
          <ExtractionControls company={selectedCompany} />
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
