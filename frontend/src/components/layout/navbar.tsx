import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Building2, Database, FileText } from "lucide-react";

export function Navbar() {
  return (
    <nav className="border-b bg-background/95 backdrop-blur-sm shadow-sm sticky top-0 z-50">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity group">
          <div className="relative">
            <Image
              src="/images/logo.png"
              alt="Financial Data Extractor Logo"
              width={32}
              height={32}
              className="h-8 w-8 group-hover:scale-110 transition-transform"
              priority
            />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            Financial Data Extractor
          </span>
        </Link>
        <div className="flex gap-1">
          <Link href="/">
            <Button variant="ghost" className="relative group">
              <Building2 className="mr-2 h-4 w-4" />
              Companies
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary scale-x-0 group-hover:scale-x-100 transition-transform" />
            </Button>
          </Link>
          <Link href="/extraction">
            <Button variant="ghost" className="relative group">
              <FileText className="mr-2 h-4 w-4" />
              Extraction
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary scale-x-0 group-hover:scale-x-100 transition-transform" />
            </Button>
          </Link>
          <Link href="/storage">
            <Button variant="ghost" className="relative group">
              <Database className="mr-2 h-4 w-4" />
              Storage
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary scale-x-0 group-hover:scale-x-100 transition-transform" />
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}
