import { Navbar } from "@/components/layout/navbar";
import { CompanyList } from "@/components/dashboard/company-list";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            Companies
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Select a company to view financial statements and extracted data
          </p>
        </div>
        <CompanyList />
      </main>
    </div>
  );
}
