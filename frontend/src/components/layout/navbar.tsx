import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <Image
            src="/images/logo.png"
            alt="Financial Data Extractor Logo"
            width={32}
            height={32}
            className="h-8 w-8"
            priority
          />
          <span className="text-xl font-bold">Financial Data Extractor</span>
        </Link>
        <div className="flex gap-4">
          <Link href="/">
            <Button variant="ghost">Companies</Button>
          </Link>
          <Link href="/extraction">
            <Button variant="ghost">Extraction</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}
