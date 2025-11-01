"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw, Home, ArrowLeft, FileText, Play } from "lucide-react";

interface StatementErrorProps {
  companyId: number;
  companyName?: string;
  error?: string;
  is404?: boolean;
  statementType?: string;
}

export function StatementError({
  companyId,
  companyName,
  error,
  is404 = false,
  statementType,
}: StatementErrorProps) {
  // If we have a company name but it's a 404, it means statements haven't been generated yet
  const statementsNotGenerated = is404 && companyName;

  const statementTypeLabel =
    statementType === "income_statement"
      ? "Income Statement"
      : statementType === "balance_sheet"
        ? "Balance Sheet"
        : statementType === "cash_flow_statement"
          ? "Cash Flow Statement"
          : "Financial Statement";

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {statementsNotGenerated ? (
              <FileText className="h-12 w-12 text-muted-foreground" />
            ) : (
              <AlertCircle className="h-12 w-12 text-destructive" />
            )}
          </div>
          <CardTitle className="text-2xl">
            {statementsNotGenerated
              ? "Financial Statements Not Available"
              : is404
                ? "Company Not Found"
                : "Unable to Load Data"}
          </CardTitle>
          <CardDescription className="text-base">
            {statementsNotGenerated ? (
              <>
                The {statementTypeLabel.toLowerCase()} for <strong>{companyName}</strong> hasn't
                been generated yet. Start the extraction process to compile financial data from the
                company's annual reports.
              </>
            ) : is404 ? (
              "The company you're looking for doesn't exist in the database."
            ) : companyName ? (
              `We couldn't load financial data for ${companyName}. This might be a temporary issue.`
            ) : (
              `We couldn't load financial data for company ID ${companyId}. This might be a temporary issue.`
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && !is404 && !statementsNotGenerated && (
            <div className="rounded-md bg-muted p-3">
              <p className="text-sm text-muted-foreground">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {statementsNotGenerated && (
            <div className="rounded-md bg-blue-50 border border-blue-200 p-4 space-y-3">
              <div>
                <p className="text-sm font-medium text-blue-900 mb-2">
                  To generate financial statements:
                </p>
                <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                  <li>Go to the Extraction page</li>
                  <li>Select {companyName}</li>
                  <li>Click "Start Full Extraction" to begin the process</li>
                  <li>The system will scrape, extract, and compile financial data</li>
                </ol>
              </div>
            </div>
          )}

          {!is404 && !statementsNotGenerated && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground text-center">Possible causes:</p>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>The backend API server is not running</li>
                <li>Network connectivity issues</li>
                <li>Temporary server error</li>
              </ul>
            </div>
          )}

          <div className="flex flex-col gap-2 pt-4">
            {statementsNotGenerated && (
              <Link href={`/extraction`}>
                <Button className="w-full" variant="default">
                  <Play className="mr-2 h-4 w-4" />
                  Start Extraction for {companyName}
                </Button>
              </Link>
            )}
            {!is404 && !statementsNotGenerated && (
              <Button
                onClick={() => window.location.reload()}
                className="w-full"
                variant="default"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            )}
            <Link href="/">
              <Button className="w-full" variant="outline">
                <Home className="mr-2 h-4 w-4" />
                Back to Companies
              </Button>
            </Link>
            {companyId && !statementsNotGenerated && (
              <Link href={`/extraction`}>
                <Button className="w-full" variant="outline">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Go to Extraction
                </Button>
              </Link>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
