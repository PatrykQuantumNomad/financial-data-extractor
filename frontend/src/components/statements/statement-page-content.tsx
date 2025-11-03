"use client";

import { Navbar } from "@/components/layout/navbar";
import { StatementError } from "@/components/statements/statement-error";
import { StatementPageLoading } from "@/components/statements/statement-page-loading";
import { StatementView } from "@/components/statements/statement-view";
import { useCompany, useStatementByCompanyAndType } from "@/lib/hooks";
import type { StatementType } from "@/lib/types";
import { getErrorMessage, isNotFoundError } from "@/lib/utils/query-utils";
import { Suspense } from "react";

interface StatementDataLoaderProps {
  companyId: number;
  statementType: StatementType;
}

function StatementDataLoader({
  companyId,
  statementType,
}: StatementDataLoaderProps) {
  // Get company data first (for display in page and error pages)
  const { data: company, isLoading: isLoadingCompany } = useCompany(companyId);

  const {
    data: statement,
    error: statementError,
    isError: isStatementError,
    isLoading: isLoadingStatement,
  } = useStatementByCompanyAndType(companyId, statementType);

  // Show loading state while fetching company or statement
  if (isLoadingCompany || isLoadingStatement) {
    return <StatementPageLoading />;
  }

  // Company should always exist at this point (404 handled by parent)
  // If somehow company is missing, show error with company context
  if (!company) {
    return (
      <StatementError
        companyId={companyId}
        error="Company data could not be loaded. Please try refreshing the page."
        is404={false}
        statementType={statementType}
      />
    );
  }

  // Handle statement errors only
  if (isStatementError) {
    const is404 = isNotFoundError(statementError);

    // 404 for statement is expected (statements not generated yet)
    if (is404 && !statement) {
      return (
        <StatementError
          companyId={companyId}
          companyName={company.name}
          is404={true}
          statementType={statementType}
        />
      );
    }

    // Other errors loading statement (network, server errors, etc.)
    const errorMessage = getErrorMessage(
      statementError,
      "Failed to load financial statement. Please check your connection and try again."
    );

    return (
      <StatementError
        companyId={companyId}
        companyName={company.name}
        error={errorMessage}
        is404={false}
        statementType={statementType}
      />
    );
  }

  // Show statement view (statement might be null if it doesn't exist)
  return (
    <StatementView
      company={company}
      statement={statement ?? null}
      statementType={statementType}
    />
  );
}

export function StatementPageContent({
  companyId,
  statementType,
}: StatementDataLoaderProps) {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Suspense fallback={<StatementPageLoading />}>
          <StatementDataLoader
            companyId={companyId}
            statementType={statementType}
          />
        </Suspense>
      </main>
    </div>
  );
}
