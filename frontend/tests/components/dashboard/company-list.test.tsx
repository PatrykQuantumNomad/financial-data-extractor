import { CompanyList } from "@/components/dashboard/company-list";
import * as hooks from "@/lib/hooks";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMockUseCompanies, mockCompanies } from "../../mocks/hooks";

vi.mock("@/lib/hooks");

describe("CompanyList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading skeleton when data is loading", () => {
    const mockUseCompanies = createMockUseCompanies({ isLoading: true });
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    const { container } = render(<CompanyList />);

    // Check for loading skeleton cards
    const cards = container.querySelectorAll(".animate-pulse");
    expect(cards.length).toBeGreaterThan(0);

    // Check for skeleton text elements
    const skeletonDivs = container.querySelectorAll(".bg-muted");
    expect(skeletonDivs.length).toBeGreaterThan(0);
  });

  it("renders error message when query has error", () => {
    const mockError = { message: "Network error", status: 500 };
    const mockUseCompanies = createMockUseCompanies({ error: mockError });
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    expect(screen.getByText(/error:/i)).toBeInTheDocument();
    expect(screen.getByText(/network error/i)).toBeInTheDocument();
  });

  it("renders empty state when no companies found", () => {
    const mockUseCompanies = createMockUseCompanies({ data: [] });
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    expect(
      screen.getByText(
        "No companies found. Add companies through the backend API."
      )
    ).toBeInTheDocument();
  });

  it("renders list of companies when data is loaded", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    expect(screen.getByText("Test Company 1")).toBeInTheDocument();
    expect(screen.getByText("Test Company 2")).toBeInTheDocument();
  });

  it("displays company details correctly", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    // Check company name
    expect(screen.getByText("Test Company 1")).toBeInTheDocument();

    // Check ticker badge
    expect(screen.getByText("TEST1")).toBeInTheDocument();

    // Check company ID
    expect(screen.getByText(/ID: 1/i)).toBeInTheDocument();
  });

  it("renders ticker badge when primary_ticker exists", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    const tickerBadges = screen.getAllByText(/TEST/i);
    expect(tickerBadges.length).toBeGreaterThan(0);
  });

  it("does not render ticker badge when primary_ticker is null", () => {
    const companiesWithoutTicker = [
      {
        ...mockCompanies[0],
        primary_ticker: null,
      },
    ];
    const mockUseCompanies = createMockUseCompanies({
      data: companiesWithoutTicker,
    });
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    expect(screen.queryByText("TEST1")).not.toBeInTheDocument();
  });

  it("renders investor relations link for each company", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    const irLinks = screen.getAllByText("Investor Relations");
    expect(irLinks).toHaveLength(2);

    const firstLink = screen.getAllByText("Investor Relations")[0];
    expect(firstLink.closest("a")).toHaveAttribute(
      "href",
      "https://example.com/investor-relations"
    );
  });

  it("renders view statements button for each company", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    const viewButtons = screen.getAllByRole("link", {
      name: /view statements/i,
    });
    expect(viewButtons).toHaveLength(2);

    expect(viewButtons[0]).toHaveAttribute(
      "href",
      "/companies/1/statements/income_statement"
    );
    expect(viewButtons[1]).toHaveAttribute(
      "href",
      "/companies/2/statements/income_statement"
    );
  });

  it("applies correct grid layout classes", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    const { container } = render(<CompanyList />);

    const gridContainer = container.querySelector(".grid");
    expect(gridContainer).toHaveClass(
      "gap-4",
      "md:grid-cols-2",
      "lg:grid-cols-3"
    );
  });

  it("applies hover effects to company cards", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    const { container } = render(<CompanyList />);

    const firstCard = container.querySelector(".group");
    expect(firstCard).toBeInTheDocument();
    expect(firstCard).toHaveClass("hover:shadow-xl", "hover:border-primary/50");
  });

  it("displays current fiscal year in description", () => {
    const mockUseCompanies = createMockUseCompanies();
    vi.mocked(hooks.useCompanies).mockImplementation(mockUseCompanies);

    render(<CompanyList />);

    const currentYear = new Date().getFullYear();
    expect(
      screen.getAllByText(new RegExp(`Fiscal Year: ${currentYear}`))
    ).toHaveLength(2);
  });
});
