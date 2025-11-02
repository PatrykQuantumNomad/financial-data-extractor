"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Home, RefreshCw } from "lucide-react";

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // Log error to console for debugging
    console.error("Global application error:", error);
  }, [error]);

  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <div className="w-full max-w-md text-center space-y-6">
            <div>
              <AlertTriangle className="h-16 w-16 text-destructive mx-auto mb-4" />
              <h1 className="text-4xl font-bold mb-2">Critical Error</h1>
              <p className="text-muted-foreground">
                A critical error occurred that prevented the application from loading.
              </p>
            </div>

            {error.message && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 p-4 text-left">
                <p className="text-sm font-medium text-destructive mb-1">
                  Error:
                </p>
                <p className="text-sm text-destructive/90 break-all">
                  {error.message}
                </p>
              </div>
            )}

            <div className="flex flex-col gap-3">
              <Button onClick={reset} size="lg" className="w-full">
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
              <Link href="/">
                <Button variant="outline" size="lg" className="w-full">
                  <Home className="mr-2 h-4 w-4" />
                  Go to Home Page
                </Button>
              </Link>
            </div>

            <p className="text-xs text-muted-foreground">
              If this problem persists, please clear your browser cache and try again.
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
