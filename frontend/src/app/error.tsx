"use client";

import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AlertTriangle, Bug, Home, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error to console for debugging
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <AlertTriangle className="h-16 w-16 text-destructive" />
              </div>
              <CardTitle className="text-3xl mb-2">
                Something went wrong!
              </CardTitle>
              <CardDescription className="text-lg">
                An unexpected error occurred while processing your request.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {error.message && (
                <div className="rounded-md bg-destructive/10 border border-destructive/20 p-4">
                  <p className="text-sm font-medium text-destructive mb-1">
                    Error Details:
                  </p>
                  <p className="text-sm text-destructive/90 font-mono break-all">
                    {error.message}
                  </p>
                  {error.digest && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Error ID: {error.digest}
                    </p>
                  )}
                </div>
              )}

              <div className="rounded-md bg-muted p-4">
                <p className="text-sm text-muted-foreground mb-2">
                  <strong>What you can do:</strong>
                </p>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>Try refreshing the page</li>
                  <li>Check your internet connection</li>
                  <li>Go back to the home page and try again</li>
                  <li>If the problem persists, contact support</li>
                </ul>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button onClick={reset} size="lg" className="w-full sm:w-auto">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </Button>
                <Link href="/" className="w-full sm:w-auto">
                  <Button variant="outline" size="lg" className="w-full">
                    <Home className="mr-2 h-4 w-4" />
                    Back to Home
                  </Button>
                </Link>
              </div>

              {process.env.NODE_ENV === "development" && (
                <div className="mt-6 pt-6 border-t">
                  <details className="text-sm">
                    <summary className="cursor-pointer text-muted-foreground hover:text-foreground font-medium mb-2">
                      <Bug className="inline h-4 w-4 mr-1" />
                      Development Error Stack
                    </summary>
                    <pre className="mt-2 p-4 bg-muted rounded-md overflow-auto text-xs">
                      {error.stack ?? "No stack trace available"}
                    </pre>
                  </details>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
