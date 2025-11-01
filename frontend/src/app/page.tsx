import { Navbar } from "@/components/layout/navbar";
import { CompanyList } from "@/components/dashboard/company-list";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Companies</h1>
          <p className="text-muted-foreground mt-2">
            Select a company to view financial statements and extracted data
          </p>
        </div>
        <CompanyList />
      </main>
    </div>
  );
}
