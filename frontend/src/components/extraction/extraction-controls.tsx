"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { tasksApi } from "@/lib/api/tasks";
import type { Company, TaskStatus } from "@/lib/types";
import { Play, RefreshCw, Loader2 } from "lucide-react";
import { TaskStatusMonitor } from "./task-status-monitor";

interface ExtractionControlsProps {
  company: Company;
}

export function ExtractionControls({ company }: ExtractionControlsProps) {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExtractCompany = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await tasksApi.triggerExtractCompany(company.id);
      setActiveTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start extraction");
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrapeOnly = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await tasksApi.triggerScrapeCompany(company.id);
      setActiveTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start scraping");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecompile = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await tasksApi.triggerRecompileCompany(company.id);
      setActiveTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start recompilation");
    } finally {
      setIsLoading(false);
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
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Full Extraction Workflow</h4>
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
              className="w-full"
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

          <div className="border-t pt-4">
            <h4 className="text-sm font-medium mb-2">Individual Steps</h4>
            <div className="grid gap-2 md:grid-cols-2">
              <Button
                onClick={handleScrapeOnly}
                disabled={isLoading}
                variant="outline"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Scrape Only
              </Button>
              <Button
                onClick={handleRecompile}
                disabled={isLoading}
                variant="outline"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Recompile Statements
              </Button>
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {activeTaskId && (
        <TaskStatusMonitor taskId={activeTaskId} onComplete={() => setActiveTaskId(null)} />
      )}
    </div>
  );
}
