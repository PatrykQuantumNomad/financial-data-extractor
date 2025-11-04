import { Navbar } from "@/components/layout/navbar";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("Navbar", () => {
  it("renders the navbar with logo and title", () => {
    render(<Navbar />);

    const logo = screen.getByAltText("Financial Data Extractor Logo");
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute("src", "/images/logo.png");

    expect(screen.getByText("Financial Data Extractor")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<Navbar />);

    const companiesLink = screen.getByRole("link", { name: /companies/i });
    expect(companiesLink).toBeInTheDocument();
    expect(companiesLink).toHaveAttribute("href", "/");

    const extractionLink = screen.getByRole("link", { name: /extraction/i });
    expect(extractionLink).toBeInTheDocument();
    expect(extractionLink).toHaveAttribute("href", "/extraction");
  });

  it("renders all navigation buttons with ghost variant", () => {
    render(<Navbar />);

    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);

    // All buttons should have ghost styling
    buttons.forEach((button) => {
      expect(button).toHaveClass("hover:bg-accent");
    });
  });

  it("has correct container styling", () => {
    render(<Navbar />);

    const navbar = screen.getByRole("navigation");
    expect(navbar).toBeInTheDocument();
    expect(navbar).toHaveClass(
      "border-b",
      "bg-background/95",
      "backdrop-blur-sm",
      "shadow-sm",
      "sticky",
      "top-0",
      "z-50"
    );
  });

  it("renders home link with logo and text", () => {
    render(<Navbar />);

    const homeLink = screen.getByText("Financial Data Extractor").closest("a");
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute("href", "/");
  });

  it("applies hover effects to links", () => {
    render(<Navbar />);

    const homeLink = screen.getByText("Financial Data Extractor").closest("a");
    expect(homeLink).toHaveClass("hover:opacity-80");
  });

  it("displays correct flex layout", () => {
    render(<Navbar />);

    const navbar = screen.getByRole("navigation");
    const container = navbar.firstChild;
    expect(container).toHaveClass("container", "mx-auto", "flex");
  });
});
