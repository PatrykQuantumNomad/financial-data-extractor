import Link from "next/link";
import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Home, Search, AlertCircle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <div className="mb-8">
            <AlertCircle className="h-24 w-24 text-muted-foreground mx-auto mb-4" />
            <h1 className="text-6xl font-bold mb-4">404</h1>
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Page Not Found
            </h2>
            <p className="text-muted-foreground text-lg max-w-md mx-auto">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <Link href="/">
              <Button size="lg" className="w-full sm:w-auto">
                <Home className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
            </Link>
            <Link href="/extraction">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                <Search className="mr-2 h-4 w-4" />
                Go to Extraction
              </Button>
            </Link>
          </div>

          <div className="mt-12 p-6 bg-muted rounded-lg max-w-md">
            <p className="text-sm text-muted-foreground">
              <strong>Common issues:</strong>
            </p>
            <ul className="text-sm text-muted-foreground mt-2 text-left list-disc list-inside space-y-1">
              <li>Invalid company ID in the URL</li>
              <li>Company doesn't exist in the database</li>
              <li>Typo in the URL</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
