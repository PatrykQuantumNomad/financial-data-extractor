import { Navbar } from "@/components/layout/navbar";
import { StoragePdfList } from "@/components/storage/storage-pdf-list";

export default function StoragePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            Storage PDFs
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Query and list PDF files stored in MinIO for each company
          </p>
        </div>
        <StoragePdfList />
      </main>
    </div>
  );
}
