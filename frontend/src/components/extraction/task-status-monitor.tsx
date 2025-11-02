"use client";

import { useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useTaskStatus } from "@/lib/hooks";
import type { TaskStatus } from "@/lib/types";
import { Loader2, CheckCircle2, XCircle, Clock, X, type LucideIcon } from "lucide-react";

interface TaskStatusMonitorProps {
  taskId: string;
  onComplete?: () => void;
}

const STATUS_COLORS: Partial<Record<TaskStatus["status"], string>> = {
  PENDING: "bg-yellow-100 text-yellow-800 border-yellow-200",
  STARTED: "bg-blue-100 text-blue-800 border-blue-200",
  SUCCESS: "bg-green-100 text-green-800 border-green-200",
  FAILURE: "bg-red-100 text-red-800 border-red-200",
  RETRY: "bg-orange-100 text-orange-800 border-orange-200",
  REVOKED: "bg-gray-100 text-gray-800 border-gray-200",
};

const STATUS_ICONS: Partial<Record<TaskStatus["status"], LucideIcon>> = {
  PENDING: Clock,
  STARTED: Loader2,
  SUCCESS: CheckCircle2,
  FAILURE: XCircle,
  RETRY: Loader2,
  REVOKED: XCircle,
};

export function TaskStatusMonitor({ taskId, onComplete }: TaskStatusMonitorProps) {
  const { data: status, isLoading } = useTaskStatus(taskId);

  useEffect(() => {
    if (status && (status.status === "SUCCESS" || status.status === "FAILURE")) {
      if (onComplete) {
        // Auto-hide after showing completion state for 5 seconds
        // This gives user time to see the result
        const timer = setTimeout(() => {
          onComplete();
        }, 5000);
        return () => clearTimeout(timer);
      }
    }
  }, [status, onComplete]);

  const handleDismiss = () => {
    if (onComplete) {
      onComplete();
    }
  };

  if (isLoading || !status) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm text-muted-foreground">Loading task status...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const StatusIcon = STATUS_ICONS[status.status] || Clock;
  const statusColor = STATUS_COLORS[status.status] || "bg-gray-100 text-gray-800 border-gray-200";

  const isComplete = status.status === "SUCCESS" || status.status === "FAILURE";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Task Status</CardTitle>
            <Badge className={statusColor}>
              <StatusIcon className="mr-1 h-3 w-3" />
              {status.status}
            </Badge>
          </div>
          {isComplete && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDismiss}
              className="h-8 w-8 p-0"
              aria-label="Dismiss task status"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        <CardDescription>Task ID: {taskId.slice(0, 8)}...</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {status.status === "SUCCESS" && status.result && (
          <div className="rounded-md bg-green-50 border border-green-200 p-3">
            <p className="text-sm font-medium text-green-900">Task completed successfully!</p>
            {typeof status.result === "object" && (
              <pre className="mt-2 text-xs text-green-800 overflow-auto">
                {JSON.stringify(status.result, null, 2)}
              </pre>
            )}
          </div>
        )}

        {status.status === "FAILURE" && status.error && (
          <div className="rounded-md bg-red-50 border border-red-200 p-3">
            <p className="text-sm font-medium text-red-900">Task failed</p>
            <p className="text-sm text-red-800 mt-1">{status.error}</p>
          </div>
        )}

        {(status.status === "PENDING" || status.status === "STARTED" || status.status === "RETRY") && (
          <div className="rounded-md bg-blue-50 border border-blue-200 p-3">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <p className="text-sm text-blue-900">
                {status.status === "PENDING" && "Task is queued and waiting to start..."}
                {status.status === "STARTED" && "Task is running..."}
                {status.status === "RETRY" && "Task is being retried..."}
              </p>
            </div>
          </div>
        )}

        {status.status === "SUCCESS" && (
          <p className="text-sm text-muted-foreground">
            This panel will auto-dismiss in a few seconds. You may need to refresh the page to see updated data.
          </p>
        )}

        {status.status === "FAILURE" && (
          <p className="text-sm text-muted-foreground">
            This panel will auto-dismiss in a few seconds.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
