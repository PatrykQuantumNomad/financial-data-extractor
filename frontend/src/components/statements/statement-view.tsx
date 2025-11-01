"use client";

import Link from "next/link";
import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FinancialStatementTable } from "./financial-statement-table";
import { StatementTypeNav } from "./statement-type-nav";
import { DocumentList } from "../documents/document-list";
import { ExtractionControls } from "../extraction/extraction-controls";
import { documentsApi } from "@/lib/api/documents";
import type { Company, CompiledStatement, StatementType, Document } from "@/lib/types";
import { ArrowLeft } from "lucide-react";

interface StatementViewProps {
  company: Company;
  statement: CompiledStatement | null;
  statementType: StatementType;
}

const STATEMENT_LABELS: Record<StatementType, string> = {
  income_statement: "Income Statement",
  balance_sheet: "Balance Sheet",
  cash_flow_statement: "Cash Flow Statement",
};

export function StatementView({ company, statement, statementType }: StatementViewProps) {
  const [documents, setDocuments] = React.useState<Document[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function loadDocuments() {
      try {
        const docs = await documentsApi.getByCompany(company.id);
        setDocuments(docs);
      } catch (error) {
        console.error("Failed to load documents:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDocuments();
  }, [company.id]);

  return (
    <div className="space-y-6">
      <div>
        <Link href="/">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Companies
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">{company.name}</h1>
        <p className="text-muted-foreground mt-1">
          {company.primary_ticker || "N/A"} • Financial Statements
        </p>
      </div>

      <StatementTypeNav companyId={company.id} currentType={statementType} />

      <Tabs defaultValue="statement" className="w-full">
        <TabsList>
          <TabsTrigger value="statement">Financial Statement</TabsTrigger>
          <TabsTrigger value="documents">Documents ({documents.length})</TabsTrigger>
          <TabsTrigger value="extract">Extract Data</TabsTrigger>
        </TabsList>

        <TabsContent value="statement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{STATEMENT_LABELS[statementType]}</CardTitle>
              <CardDescription>
                10-year compiled view with restated data prioritized
              </CardDescription>
            </CardHeader>
            <CardContent>
              {statement ? (
                <FinancialStatementTable statement={statement} />
              ) : (
                <div className="text-center py-12">
                  <p className="text-muted-foreground mb-2">
                    No compiled statement available for this company yet.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Use the "Extract Data" tab to start the extraction process.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents">
          <DocumentList companyId={company.id} documents={documents} loading={loading} />
        </TabsContent>

        <TabsContent value="extract">
          <ExtractionControls company={company} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
