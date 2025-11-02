import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders a badge with default variant", () => {
    render(<Badge>Default Badge</Badge>);
    const badge = screen.getByText("Default Badge");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-primary");
  });

  it("renders a badge with different variants", () => {
    const { rerender } = render(<Badge variant="secondary">Secondary</Badge>);
    let badge = screen.getByText("Secondary");
    expect(badge).toHaveClass("bg-secondary");

    rerender(<Badge variant="destructive">Destructive</Badge>);
    badge = screen.getByText("Destructive");
    expect(badge).toHaveClass("bg-destructive");

    rerender(<Badge variant="outline">Outline</Badge>);
    badge = screen.getByText("Outline");
    expect(badge).toHaveClass("text-foreground");
  });

  it("applies custom className", () => {
    render(<Badge className="custom-badge-class">Custom</Badge>);
    const badge = screen.getByText("Custom");
    expect(badge).toHaveClass("custom-badge-class");
  });

  it("renders as a div by default", () => {
    render(<Badge>Test Badge</Badge>);
    const badge = screen.getByText("Test Badge");
    expect(badge.tagName).toBe("DIV");
  });

  it("forwards props correctly", () => {
    render(
      <Badge data-testid="badge" id="test-id">
        Test
      </Badge>
    );
    const badge = screen.getByTestId("badge");
    expect(badge).toHaveAttribute("id", "test-id");
  });

  it("applies focus styles", () => {
    render(<Badge tabIndex={0}>Focusable Badge</Badge>);
    const badge = screen.getByText("Focusable Badge");
    expect(badge).toHaveClass("focus:ring-2", "focus:ring-ring");
  });

  it("renders children correctly", () => {
    render(
      <Badge>
        <span>Badge with span</span>
      </Badge>
    );
    expect(screen.getByText("Badge with span")).toBeInTheDocument();
  });

  it("has correct default styling", () => {
    render(<Badge>Styled Badge</Badge>);
    const badge = screen.getByText("Styled Badge");
    expect(badge).toHaveClass(
      "inline-flex",
      "items-center",
      "rounded-full",
      "border",
      "px-2.5",
      "py-0.5",
      "text-xs",
      "font-semibold"
    );
  });
});
