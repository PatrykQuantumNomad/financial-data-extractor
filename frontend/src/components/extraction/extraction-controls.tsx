"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  useTriggerExtractCompany,
  useTriggerProcessAllDocuments,
  useTriggerRecompileCompany,
  useTriggerScrapeCompany,
} from "@/lib/hooks";
import { documentKeys } from "@/lib/hooks/use-documents";
import type { Company } from "@/lib/types";
import { getErrorMessage, isMutationPending } from "@/lib/utils/query-utils";
import { useQueryClient } from "@tanstack/react-query";
import { Database, FileText, Globe, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { TaskStatusMonitor } from "./task-status-monitor";

interface ExtractionControlsProps {
  company: Company;
}

export function ExtractionControls({ company }: ExtractionControlsProps) {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const extractMutation = useTriggerExtractCompany();
  const scrapeMutation = useTriggerScrapeCompany();
  const recompileMutation = useTriggerRecompileCompany();
  const processAllDocsMutation = useTriggerProcessAllDocuments();

  // Refetch documents when tasks complete successfully
  const handleTaskSuccess = () => {
    void queryClient.invalidateQueries({
      queryKey: documentKeys.byCompany(company.id),
    });
  };

  const isLoading =
    isMutationPending(extractMutation) ??
    isMutationPending(scrapeMutation) ??
    isMutationPending(recompileMutation) ??
    isMutationPending(processAllDocsMutation);
  const error =
    extractMutation.error ??
    scrapeMutation.error ??
    recompileMutation.error ??
    processAllDocsMutation.error;

  const handleExtractCompany = async () => {
    try {
      const response = await extractMutation.mutateAsync(company.id);
      setActiveTaskId(response.task_id);
    } catch (err: unknown) {
      console.error(err);
    }
  };

  const handleScrapeOnly = async () => {
    try {
      const response = await scrapeMutation.mutateAsync(company.id);
      setActiveTaskId(response.task_id);
    } catch (err: unknown) {
      console.error(err);
    }
  };

  const handleRecompile = async () => {
    try {
      const response = await recompileMutation.mutateAsync(company.id);
      setActiveTaskId(response.task_id);
    } catch (err: unknown) {
      console.error(err);
    }
  };

  const handleProcessAllDocuments = async () => {
    try {
      const response = await processAllDocsMutation.mutateAsync(company.id);
      setActiveTaskId(response.task_id);
    } catch (err: unknown) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Extract Financial Data</CardTitle>
          <CardDescription>
            Trigger the complete extraction workflow for {company.name}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Full Extraction Workflow */}
          <div>
            <h4 className="text-sm font-medium mb-2">
              Full Extraction Workflow
            </h4>
            <div className="text-sm text-muted-foreground mb-4">
              <p className="mb-2">This will:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Scrape the investor relations website</li>
                <li>Discover and classify PDF documents</li>
                <li>Download PDFs locally</li>
                <li>Extract financial statements using LLM</li>
                <li>Normalize and compile 10 years of data</li>
              </ul>
            </div>
            <Button
              onClick={handleExtractCompany}
              disabled={isLoading}
              className="w-full transition-all duration-200 hover:shadow-md hover:scale-[1.02] hover:bg-primary/90 active:scale-[0.98]"
              size="lg"
            >
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Start Full Extraction
            </Button>
          </div>

          {/* Company-Level Individual Steps */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium mb-3">
              Company-Level Operations
            </h4>
            <div className="space-y-2">
              <Button
                onClick={handleScrapeOnly}
                disabled={isLoading}
                variant="secondary"
                className="w-full justify-start h-auto py-3 px-4 transition-all duration-200 hover:shadow-md hover:scale-[1.02] hover:bg-secondary/80 active:scale-[0.98] border border-border"
              >
                <Globe className="mr-3 h-5 w-5 flex-shrink-0" />
                <div className="flex-1 text-left">
                  <div className="font-medium text-sm">
                    Scrape Investor Relations
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Discover and download PDF documents
                  </div>
                </div>
              </Button>
              <Button
                onClick={handleProcessAllDocuments}
                disabled={isLoading}
                variant="secondary"
                className="w-full justify-start h-auto py-3 px-4 transition-all duration-200 hover:shadow-md hover:scale-[1.02] hover:bg-secondary/80 active:scale-[0.98] border border-border"
              >
                <FileText className="mr-3 h-5 w-5 flex-shrink-0" />
                <div className="flex-1 text-left">
                  <div className="font-medium text-sm">
                    Process All Documents
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Classify, download, and extract all documents
                  </div>
                </div>
              </Button>
              <Button
                onClick={handleRecompile}
                disabled={isLoading}
                variant="secondary"
                className="w-full justify-start h-auto py-3 px-4 transition-all duration-200 hover:shadow-md hover:scale-[1.02] hover:bg-secondary/80 active:scale-[0.98] border border-border"
              >
                <Database className="mr-3 h-5 w-5 flex-shrink-0" />
                <div className="flex-1 text-left">
                  <div className="font-medium text-sm">
                    Recompile Statements
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Normalize and compile all financial statements
                  </div>
                </div>
              </Button>
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
              <p className="text-sm text-destructive">
                {getErrorMessage(
                  error,
                  "An error occurred while processing your request"
                )}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {activeTaskId && (
        <TaskStatusMonitor
          taskId={activeTaskId}
          onComplete={() => setActiveTaskId(null)}
          onSuccess={handleTaskSuccess}
        />
      )}
    </div>
  );
}
