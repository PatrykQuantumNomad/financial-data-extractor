import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { StatementPageLoading } from "@/components/statements/statement-page-loading";

describe("StatementPageLoading", () => {
  it("renders loading skeleton", () => {
    const { container } = render(<StatementPageLoading />);

    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("renders header skeleton", () => {
    const { container } = render(<StatementPageLoading />);

    const headers = container.querySelectorAll(".h-8");
    const subheaders = container.querySelectorAll(".h-4");
    expect(headers.length).toBeGreaterThan(0);
    expect(subheaders.length).toBeGreaterThan(0);
  });

  it("renders navigation skeleton with 3 tabs", () => {
    const { container } = render(<StatementPageLoading />);

    const navSkeletons = container.querySelectorAll(".h-10");
    expect(navSkeletons.length).toBeGreaterThanOrEqual(3);
  });

  it("renders table skeleton", () => {
    const { container } = render(<StatementPageLoading />);

    const card = container.querySelector(".rounded-lg");
    expect(card).toBeInTheDocument();

    const tableRows = container.querySelectorAll(".space-y-3 > div");
    expect(tableRows.length).toBeGreaterThanOrEqual(5);
  });

  it("applies pulse animation to skeleton elements", () => {
    const { container } = render(<StatementPageLoading />);

    const pulseElements = container.querySelectorAll(".animate-pulse");
    expect(pulseElements.length).toBeGreaterThan(0);
  });

  it("renders all skeleton sections", () => {
    const { container } = render(<StatementPageLoading />);

    const card = container.querySelector(".space-y-6");
    expect(card).toBeInTheDocument();
  });

  it("has correct spacing classes", () => {
    const { container } = render(<StatementPageLoading />);

    const mainContainer = container.querySelector(".space-y-6");
    expect(mainContainer).toBeInTheDocument();
  });
});
