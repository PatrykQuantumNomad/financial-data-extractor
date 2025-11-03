"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ApiError } from "@/lib/api/client";
import { useCompanies } from "@/lib/hooks";
import { useStoragePdfs } from "@/lib/hooks/use-storage-pdfs";
import type { Company, StoragePdfFile } from "@/lib/types";
import { formatBytes } from "@/lib/utils/formatters";
import { getErrorMessage, isQueryLoading } from "@/lib/utils/query-utils";
import { format } from "date-fns";
import {
  Building2,
  Calendar,
  ExternalLink,
  FileText,
  Filter,
} from "lucide-react";
import { useEffect, useState } from "react";

interface StoragePdfListProps {
  companyId?: number;
}

export function StoragePdfList({
  companyId: initialCompanyId,
}: StoragePdfListProps) {
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [fiscalYear, setFiscalYear] = useState<number | undefined>(undefined);

  const companiesQuery = useCompanies();
  const storagePdfsQuery = useStoragePdfs(selectedCompany?.id ?? 0, fiscalYear);

  const { data: companies } = companiesQuery;
  const storagePdfsQueryResult = storagePdfsQuery;
  const { data: storageData } = storagePdfsQueryResult;
  const error: ApiError | null =
    storagePdfsQueryResult.error as ApiError | null;
  const isLoading = isQueryLoading(storagePdfsQuery);

  // Set initial company if provided
  useEffect(() => {
    if (
      initialCompanyId &&
      companies &&
      companies.length > 0 &&
      !selectedCompany
    ) {
      const company = companies.find((c) => c.id === initialCompanyId);
      if (company) {
        setSelectedCompany(company);
      }
    }
  }, [initialCompanyId, companies, selectedCompany]);

  const handleCompanyChange = (company: Company) => {
    setSelectedCompany(company);
    setFiscalYear(undefined); // Reset fiscal year when company changes
  };

  const handleFiscalYearChange = (year: number | undefined) => {
    setFiscalYear(year);
  };

  // Extract unique fiscal years from files
  const fiscalYears = storageData?.files
    ? Array.from(
        new Set(
          storageData.files
            .map((file: StoragePdfFile) => {
              // Extract fiscal year from path like "company_1/2023/filename.pdf"
              const match = /company_\d+\/(\d+)\//.exec(file.object_key);
              return match?.[1] ? parseInt(match[1], 10) : null;
            })
            .filter((year): year is number => year !== null)
        )
      ).sort((a, b) => b - a)
    : [];

  // Group files by fiscal year
  const filesByYear =
    storageData?.files.reduce((acc, file: StoragePdfFile) => {
      const match = /company_\d+\/(\d+)\//.exec(file.object_key);
      const year = match?.[1] ? parseInt(match[1], 10) : "unknown";
      acc[year] ??= [];
      acc[year].push(file);
      return acc;
    }, {} as Record<number | "unknown", StoragePdfFile[]>) ?? {};

  if (companiesQuery.isLoading) {
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
              Choose a company to view PDFs from storage
            </CardDescription>
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
                  onClick={() => handleCompanyChange(company)}
                >
                  {isSelected && (
                    <span className="absolute left-0 top-0 bottom-0 w-1 bg-primary-foreground/60 rounded-r" />
                  )}
                  <Building2
                    className={`mr-2 h-4 w-4 ${
                      isSelected ? "text-primary-foreground" : ""
                    }`}
                  />
                  <span className={isSelected ? "font-semibold" : ""}>
                    {company.name}
                  </span>
                </Button>
              );
            })}
          </CardContent>
        </Card>
      </div>

      <div className="lg:col-span-2">
        {selectedCompany ? (
          <div className="space-y-6">
            {/* Fiscal Year Filter */}
            {fiscalYears.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Filter className="h-5 w-5" />
                    Filter by Fiscal Year
                  </CardTitle>
                  <CardDescription>
                    Optionally filter PDFs by fiscal year for{" "}
                    {selectedCompany.name}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={fiscalYear === undefined ? "default" : "outline"}
                      onClick={() => handleFiscalYearChange(undefined)}
                    >
                      All Years
                    </Button>
                    {fiscalYears.map((year) => (
                      <Button
                        key={year}
                        variant={fiscalYear === year ? "default" : "outline"}
                        onClick={() => handleFiscalYearChange(year)}
                      >
                        {year}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Loading State */}
            {isLoading && (
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
            )}

            {/* Error State */}
            {error && (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-destructive">
                    Error:{" "}
                    {getErrorMessage(error, "Failed to load PDFs from storage")}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* No Files Found */}
            {!isLoading && storageData?.count === 0 && (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-muted-foreground text-center py-8">
                    No PDFs found in storage for {selectedCompany.name}
                    {fiscalYear ? ` for year ${fiscalYear}` : ""}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Files List */}
            {!isLoading && storageData && storageData.count > 0 && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>PDF Files in Storage</CardTitle>
                    <CardDescription>
                      Found {storageData.count} file
                      {storageData.count !== 1 ? "s" : ""} in storage for{" "}
                      {selectedCompany.name}
                    </CardDescription>
                  </CardHeader>
                </Card>

                {(Object.keys(filesByYear) as Array<number | "unknown">)
                  .sort((a, b) => {
                    if (a === "unknown") return 1;
                    if (b === "unknown") return -1;
                    return Number(b) - Number(a);
                  })
                  .map((year) => {
                    const files: StoragePdfFile[] =
                      (
                        filesByYear as Record<string | number, StoragePdfFile[]>
                      )[year] ?? [];
                    return (
                      <div key={year}>
                        <h3 className="text-lg font-semibold mb-4">
                          Fiscal Year {year === "unknown" ? "Unknown" : year}
                        </h3>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                          {files.map((file: StoragePdfFile) => {
                            const filename =
                              file.object_key.split("/").pop() ??
                              file.object_key;
                            // Build download URL using the API base URL
                            const apiBaseUrl =
                              process.env.NEXT_PUBLIC_API_URL ??
                              "http://localhost:3030";
                            const downloadUrl = `${apiBaseUrl}/api/v1/documents/storage/download?object_key=${encodeURIComponent(
                              file.object_key
                            )}`;
                            return (
                              <Card
                                key={file.object_key}
                                className="hover:shadow-xl transition-all duration-200 hover:border-primary/50 hover:-translate-y-1 cursor-pointer group w-full col-span-1 hover:shadow-primary/5"
                                style={{ minWidth: "300px", maxWidth: "100%" }}
                                onClick={() => {
                                  window.open(downloadUrl, "_blank");
                                }}
                              >
                                <CardHeader>
                                  <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-2 flex-1 min-w-0">
                                      <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0 group-hover:text-primary transition-colors" />
                                      <CardTitle
                                        className="text-base truncate group-hover:text-primary transition-colors"
                                        title={filename}
                                      >
                                        {filename}
                                      </CardTitle>
                                    </div>
                                    <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                                  </div>
                                  <div className="text-sm text-muted-foreground space-y-1">
                                    <div className="flex items-center gap-2 text-xs">
                                      <span>{formatBytes(file.size)}</span>
                                    </div>
                                    {file.last_modified && (
                                      <div className="flex items-center gap-1 text-xs">
                                        <Calendar className="h-3 w-3" />
                                        {format(
                                          new Date(file.last_modified),
                                          "MMM dd, yyyy HH:mm"
                                        )}
                                      </div>
                                    )}
                                  </div>
                                </CardHeader>
                                <CardContent>
                                  <div className="space-y-2">
                                    <div className="pt-2">
                                      <a
                                        href={downloadUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={(e) => e.stopPropagation()}
                                        className="text-xs text-primary hover:underline flex items-center gap-1"
                                      >
                                        View PDF{" "}
                                        <ExternalLink className="h-3 w-3" />
                                      </a>
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground py-8">
                Select a company from the list to view PDFs from storage
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
