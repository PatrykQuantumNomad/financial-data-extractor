"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useDocumentsByCompany, useTriggerExtractDocument } from "@/lib/hooks";
import { documentKeys } from "@/lib/hooks/use-documents";
import type { Company, Document } from "@/lib/types";
import { getErrorMessage, isMutationPending } from "@/lib/utils/query-utils";
import { useQueryClient } from "@tanstack/react-query";
import { AlertCircle, Brain, Loader2 } from "lucide-react";
import { useState } from "react";
import { TaskStatusMonitor } from "./task-status-monitor";

interface DocumentActionsProps {
  company: Company;
}

export function DocumentActions({ company }: DocumentActionsProps) {
  const [activeTaskIds, setActiveTaskIds] = useState<Map<number, string>>(
    new Map()
  );
  const queryClient = useQueryClient();
  const { data: documents, isLoading: documentsLoading } =
    useDocumentsByCompany(company.id);

  // Refetch documents when individual document tasks complete successfully
  const handleDocumentTaskSuccess = () => {
    void queryClient.invalidateQueries({
      queryKey: documentKeys.byCompany(company.id),
    });
  };

  const extractMutation = useTriggerExtractDocument();

  const isAnyLoading = isMutationPending(extractMutation);

  const handleExtract = async (documentId: number) => {
    try {
      const response = await extractMutation.mutateAsync(documentId);
      setActiveTaskIds((prev) =>
        new Map(prev).set(documentId, response.task_id)
      );
    } catch {
      // Error is handled by mutation
    }
  };

  const renderDocumentCard = (doc: Document) => {
    const taskId = activeTaskIds.get(doc.id);

    return (
      <Card key={doc.id} className="relative">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">
            {doc.url.split("/").pop()}
          </CardTitle>
          <CardDescription className="mt-1">
            Fiscal Year: {doc.fiscal_year} • Type: {doc.document_type}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {!doc.file_path ? (
            <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3">
              <p className="text-sm text-yellow-800">
                Document not downloaded. Use "Process All Documents"
                company-level operation to download it.
              </p>
            </div>
          ) : (
            <Button
              size="sm"
              variant="default"
              onClick={() => handleExtract(doc.id)}
              disabled={isAnyLoading}
              className="w-full transition-all duration-200 hover:shadow-md hover:scale-[1.02] hover:bg-primary/90 active:scale-[0.98]"
              title="Extract financial statements using LLM"
            >
              <Brain className="mr-2 h-4 w-4" />
              Extract Financial Statements
            </Button>
          )}

          {taskId && (
            <TaskStatusMonitor
              taskId={taskId}
              onComplete={() => {
                setActiveTaskIds((prev) => {
                  const next = new Map(prev);
                  next.delete(doc.id);
                  return next;
                });
              }}
              onSuccess={handleDocumentTaskSuccess}
            />
          )}
        </CardContent>
      </Card>
    );
  };

  if (documentsLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
          <CardDescription>
            No documents found. Scrape the investor relations website first.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Extract Financial Statements</CardTitle>
          <CardDescription>
            Extract financial statements from downloaded documents for{" "}
            {company.name}. Found {documents.length} document
            {documents.length !== 1 ? "s" : ""}.
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {documents.map(renderDocumentCard)}
      </div>

      {extractMutation.error && (
        <Card>
          <CardContent className="pt-6">
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-destructive" />
                <p className="text-sm text-destructive">
                  {getErrorMessage(
                    extractMutation.error,
                    "An error occurred while extracting financial statements"
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
