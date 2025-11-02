import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatementTypeNav } from "@/components/statements/statement-type-nav";

describe("StatementTypeNav", () => {
  it("renders all three statement type links", () => {
    render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    expect(screen.getByRole("link", { name: /income statement/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /balance sheet/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /cash flow/i })).toBeInTheDocument();
  });

  it("highlights active statement type", () => {
    render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    const activeLink = screen.getByRole("link", { name: /income statement/i });
    const button = activeLink.querySelector("button");
    expect(button).toHaveClass("border-primary");
  });

  it("does not highlight inactive statement types", () => {
    render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    const inactiveLink = screen.getByRole("link", { name: /balance sheet/i });
    const button = inactiveLink.querySelector("button");
    expect(button).not.toHaveClass("border-primary");
    expect(button).toHaveClass("border-transparent");
  });

  it("generates correct href for income statement", () => {
    render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    const link = screen.getByRole("link", { name: /income statement/i });
    expect(link).toHaveAttribute("href", "/companies/1/statements/income_statement");
  });

  it("generates correct href for balance sheet", () => {
    render(<StatementTypeNav companyId={1} currentType="balance_sheet" />);

    const link = screen.getByRole("link", { name: /balance sheet/i });
    expect(link).toHaveAttribute("href", "/companies/1/statements/balance_sheet");
  });

  it("generates correct href for cash flow", () => {
    render(<StatementTypeNav companyId={1} currentType="cash_flow_statement" />);

    const link = screen.getByRole("link", { name: /cash flow/i });
    expect(link).toHaveAttribute("href", "/companies/1/statements/cash_flow_statement");
  });

  it("handles different company IDs", () => {
    render(<StatementTypeNav companyId={42} currentType="income_statement" />);

    const link = screen.getByRole("link", { name: /income statement/i });
    expect(link).toHaveAttribute("href", "/companies/42/statements/income_statement");
  });

  it("applies active styling to current type", () => {
    render(<StatementTypeNav companyId={1} currentType="cash_flow_statement" />);

    const activeLink = screen.getByRole("link", { name: /cash flow/i });
    const button = activeLink.querySelector("button");
    expect(button).toHaveClass("border-primary");
  });

  it("applies ghost variant to inactive buttons", () => {
    render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    const inactiveLinks = [
      screen.getByRole("link", { name: /balance sheet/i }),
      screen.getByRole("link", { name: /cash flow/i }),
    ];

    inactiveLinks.forEach((link) => {
      const button = link.querySelector("button");
      expect(button).toHaveClass("hover:bg-accent");
    });
  });

  it("renders with border-b class", () => {
    const { container } = render(<StatementTypeNav companyId={1} currentType="income_statement" />);

    const nav = container.querySelector(".border-b");
    expect(nav).toBeInTheDocument();
  });
});
