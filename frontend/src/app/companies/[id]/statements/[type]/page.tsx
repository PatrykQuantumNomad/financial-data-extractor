import { Navbar } from "@/components/layout/navbar";
import { StatementError } from "@/components/statements/statement-error";
import { StatementView } from "@/components/statements/statement-view";
import { companiesApi } from "@/lib/api/companies";
import { statementsApi } from "@/lib/api/statements";
import type { CompiledStatement, StatementType } from "@/lib/types";

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

  if (isNaN(companyId)) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <StatementError companyId={companyId} is404={true} />
        </main>
      </div>
    );
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

  try {
    const company = await companiesApi.getById(companyId);
    let statement: CompiledStatement | null = null;
    let statementError: any = null;

    try {
      statement = await statementsApi.getByCompanyAndType(
        companyId,
        type as StatementType
      );
    } catch (error: any) {
      statementError = error;
      // Statement doesn't exist yet, which is fine (404 expected)
      // Only log if it's not a 404 error
      if (error?.status !== 404) {
        console.error(
          `Error loading ${type} statement for company ${companyId}:`,
          error
        );
      }
    }

    // If company exists but statement doesn't (404), show helpful error page
    if (company && statementError?.status === 404 && !statement) {
      return (
        <div className="min-h-screen bg-background">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <StatementError
              companyId={companyId}
              companyName={company.name}
              is404={true}
              statementType={type}
            />
          </main>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <StatementView
            company={company}
            statement={statement}
            statementType={type as StatementType}
          />
        </main>
      </div>
    );
  } catch (error: any) {
    // Determine if this is a 404 (company doesn't exist) or another error
    const is404 = error?.status === 404;
    const errorMessage =
      error?.message ||
      (error?.status ? `HTTP ${error.status}` : "Unknown error");

    // Always try to get company name from companies list as fallback
    // This helps when API is having issues but company exists in the list
    let companyName: string | undefined;
    try {
      const companies = await companiesApi.getAll();
      const foundCompany = companies.find((c) => c.id === companyId);
      if (foundCompany) {
        companyName = foundCompany.name;
      }
    } catch {
      // Ignore errors when trying to get company name
      // If this also fails, we'll show the generic error
    }

    // If we found the company name, treat it as statements not generated
    // rather than company not found (since we know the company exists)
    const statementsNotGenerated = is404 && companyName;

    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <StatementError
            companyId={companyId}
            companyName={companyName}
            error={statementsNotGenerated ? undefined : errorMessage}
            is404={statementsNotGenerated ? true : is404}
            statementType={type}
          />
        </main>
      </div>
    );
  }
}
