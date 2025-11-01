import { Navbar } from "@/components/layout/navbar";
import { ExtractionPageContent } from "@/components/extraction/extraction-page-content";

export default function ExtractionPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Data Extraction</h1>
          <p className="text-muted-foreground mt-2">
            Manage extraction tasks and monitor progress for all companies
          </p>
        </div>
        <ExtractionPageContent />
      </main>
    </div>
  );
}
