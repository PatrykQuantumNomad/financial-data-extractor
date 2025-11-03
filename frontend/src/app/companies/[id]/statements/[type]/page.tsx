import { Navbar } from "@/components/layout/navbar";
import { StatementError } from "@/components/statements/statement-error";
import { StatementPageContent } from "@/components/statements/statement-page-content";
import { companiesApi } from "@/lib/api/companies";
import type { StatementType } from "@/lib/types";
import { notFound } from "next/navigation";

interface PageProps {
  params: Promise<{
    id: string;
    type: string;
  }>;
}

const VALID_STATEMENT_TYPES: StatementType[] = [
  "income_statement",
  "balance_sheet",
  "cash_flow_statement",
];

export default async function StatementPage({ params }: PageProps) {
  const { id, type } = await params;
  const companyId = parseInt(id);

  // Invalid company ID in URL - show standard 404 page not found
  if (isNaN(companyId)) {
    notFound();
  }

  // Validate company exists at page level - if company doesn't exist, show 404
  try {
    await companiesApi.getById(companyId);
  } catch (error: unknown) {
    if (
      typeof error === "object" &&
      error !== null &&
      "status" in error &&
      typeof (error as { status: unknown }).status === "number" &&
      (error as { status: number }).status === 404
    ) {
      notFound();
    }
  }

  if (!VALID_STATEMENT_TYPES.includes(type as StatementType)) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <StatementError
            companyId={companyId}
            error="Invalid statement type"
            is404={false}
          />
        </main>
      </div>
    );
  }

  return (
    <StatementPageContent
      companyId={companyId}
      statementType={type as StatementType}
    />
  );
}
