import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatementError } from "@/components/statements/statement-error";

describe("StatementError", () => {
  it("renders error card with default state", () => {
    render(<StatementError companyId={1} />);

    expect(screen.getByText("Unable to Load Data")).toBeInTheDocument();
    expect(screen.getByText(/the backend api server/i)).toBeInTheDocument();
  });

  it("renders 404 error when company not found", () => {
    render(<StatementError companyId={1} is404={true} />);

    expect(screen.getByText("Company Not Found")).toBeInTheDocument();
    expect(screen.getByText("The company you're looking for doesn't exist in the database.")).toBeInTheDocument();
  });

  it("renders statements not generated state", () => {
    render(<StatementError companyId={1} companyName="Test Company" is404={true} />);

    expect(screen.getByText("Financial Statements Not Available")).toBeInTheDocument();
    expect(screen.getByText(/financial statement for/i)).toBeInTheDocument();
    expect(screen.getByText("Test Company")).toBeInTheDocument();
  });

  it("displays custom error message", () => {
    render(<StatementError companyId={1} error="Network error" />);

    expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    expect(screen.getByText("Network error")).toBeInTheDocument();
  });

  it("displays extraction button when statements not generated", () => {
    render(<StatementError companyId={1} companyName="Test Company" is404={true} />);

    expect(screen.getByRole("link", { name: /start extraction/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /start extraction/i })).toHaveAttribute("href", "/extraction");
  });

  it("displays try again button for non-404 errors", () => {
    render(<StatementError companyId={1} error="Server error" />);

    const tryAgainButton = screen.getByRole("button", { name: /try again/i });
    expect(tryAgainButton).toBeInTheDocument();
  });

  it("displays back to companies button", () => {
    render(<StatementError companyId={1} />);

    const backButton = screen.getByRole("link", { name: /back to companies/i });
    expect(backButton).toBeInTheDocument();
    expect(backButton).toHaveAttribute("href", "/");
  });

  it("displays go to extraction button for non-404 errors", () => {
    render(<StatementError companyId={1} error="Error" />);

    const extractionButton = screen.getByRole("link", { name: /go to extraction/i });
    expect(extractionButton).toBeInTheDocument();
    expect(extractionButton).toHaveAttribute("href", "/extraction");
  });

  it("renders different statement type labels", () => {
    const { rerender } = render(
      <StatementError companyId={1} companyName="Test" is404={true} statementType="income_statement" />
    );
    expect(screen.getByText(/income statement/i)).toBeInTheDocument();

    rerender(
      <StatementError companyId={1} companyName="Test" is404={true} statementType="balance_sheet" />
    );
    expect(screen.getByText(/balance sheet/i)).toBeInTheDocument();

    rerender(
      <StatementError companyId={1} companyName="Test" is404={true} statementType="cash_flow_statement" />
    );
    expect(screen.getByText(/cash flow statement/i)).toBeInTheDocument();
  });

  it("shows extraction instructions for statements not generated", () => {
    render(<StatementError companyId={1} companyName="Test Company" is404={true} />);

    expect(screen.getByText(/to generate financial statements/i)).toBeInTheDocument();
    expect(screen.getByText(/go to the extraction page/i)).toBeInTheDocument();
  });

  it("shows possible causes for other errors", () => {
    render(<StatementError companyId={1} error="Error" />);

    expect(screen.getByText(/possible causes/i)).toBeInTheDocument();
    expect(screen.getByText(/backend api server/i)).toBeInTheDocument();
  });

  it("renders with company name in description", () => {
    render(<StatementError companyId={1} companyName="Test Company" error="Error" />);

    expect(screen.getByText(/test company/i)).toBeInTheDocument();
  });

  it("renders with company ID when no name provided", () => {
    render(<StatementError companyId={123} error="Error" />);

    expect(screen.getByText(/company id 123/i)).toBeInTheDocument();
  });
});
