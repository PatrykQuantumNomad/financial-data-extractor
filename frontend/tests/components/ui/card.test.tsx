import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

describe("Card Components", () => {
  describe("Card", () => {
    it("renders a card", () => {
      render(<Card data-testid="card">Card Content</Card>);
      const card = screen.getByTestId("card");
      expect(card).toBeInTheDocument();
      expect(card).toHaveClass("rounded-lg", "border");
    });

    it("applies custom className", () => {
      render(<Card className="custom-card-class">Card</Card>);
      const card = screen.getByText("Card");
      expect(card).toHaveClass("custom-card-class");
    });

    it("forwards ref correctly", () => {
      const ref = vi.fn();
      render(<Card ref={ref}>Card</Card>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe("CardHeader", () => {
    it("renders CardHeader with children", () => {
      render(
        <Card>
          <CardHeader data-testid="header">Header Content</CardHeader>
        </Card>
      );
      expect(screen.getByTestId("header")).toBeInTheDocument();
      expect(screen.getByText("Header Content")).toBeInTheDocument();
    });

    it("applies correct padding", () => {
      render(
        <Card>
          <CardHeader data-testid="header">Header</CardHeader>
        </Card>
      );
      const header = screen.getByTestId("header");
      expect(header).toHaveClass("p-6");
    });
  });

  describe("CardTitle", () => {
    it("renders CardTitle with text", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      );
      expect(screen.getByText("Card Title")).toBeInTheDocument();
    });

    it("renders as an h3 element", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
          </CardHeader>
        </Card>
      );
      const title = screen.getByText("Title");
      expect(title.tagName).toBe("H3");
    });

    it("has correct styling", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Styled Title</CardTitle>
          </CardHeader>
        </Card>
      );
      const title = screen.getByText("Styled Title");
      expect(title).toHaveClass("text-2xl", "font-semibold");
    });
  });

  describe("CardDescription", () => {
    it("renders CardDescription with text", () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Description text</CardDescription>
          </CardHeader>
        </Card>
      );
      expect(screen.getByText("Description text")).toBeInTheDocument();
    });

    it("renders as a p element", () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Desc</CardDescription>
          </CardHeader>
        </Card>
      );
      const desc = screen.getByText("Desc");
      expect(desc.tagName).toBe("P");
    });

    it("has muted foreground color", () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Muted Desc</CardDescription>
          </CardHeader>
        </Card>
      );
      const desc = screen.getByText("Muted Desc");
      expect(desc).toHaveClass("text-muted-foreground");
    });
  });

  describe("CardContent", () => {
    it("renders CardContent with children", () => {
      render(
        <Card>
          <CardContent data-testid="content">Content</CardContent>
        </Card>
      );
      expect(screen.getByTestId("content")).toBeInTheDocument();
      expect(screen.getByText("Content")).toBeInTheDocument();
    });

    it("applies correct padding", () => {
      render(
        <Card>
          <CardContent data-testid="content">Content</CardContent>
        </Card>
      );
      const content = screen.getByTestId("content");
      expect(content).toHaveClass("p-6", "pt-0");
    });
  });

  describe("CardFooter", () => {
    it("renders CardFooter with children", () => {
      render(
        <Card>
          <CardFooter data-testid="footer">Footer</CardFooter>
        </Card>
      );
      expect(screen.getByTestId("footer")).toBeInTheDocument();
      expect(screen.getByText("Footer")).toBeInTheDocument();
    });

    it("has flexbox layout", () => {
      render(
        <Card>
          <CardFooter data-testid="footer">Footer</CardFooter>
        </Card>
      );
      const footer = screen.getByTestId("footer");
      expect(footer).toHaveClass("flex", "items-center");
    });

    it("applies correct padding", () => {
      render(
        <Card>
          <CardFooter data-testid="footer">Footer</CardFooter>
        </Card>
      );
      const footer = screen.getByTestId("footer");
      expect(footer).toHaveClass("p-6", "pt-0");
    });
  });

  describe("Complete Card Structure", () => {
    it("renders a complete card with all components", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>Test Content</CardContent>
          <CardFooter>Test Footer</CardFooter>
        </Card>
      );

      expect(screen.getByText("Test Title")).toBeInTheDocument();
      expect(screen.getByText("Test Description")).toBeInTheDocument();
      expect(screen.getByText("Test Content")).toBeInTheDocument();
      expect(screen.getByText("Test Footer")).toBeInTheDocument();
    });

    it("applies correct styling hierarchy", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
            <CardDescription>Description</CardDescription>
          </CardHeader>
          <CardContent>Content</CardContent>
        </Card>
      );

      const title = screen.getByText("Title");
      const description = screen.getByText("Description");
      const content = screen.getByText("Content");

      expect(title).toHaveClass("text-2xl");
      expect(description).toHaveClass("text-sm");
      expect(content).toHaveClass("p-6");
    });
  });
});
