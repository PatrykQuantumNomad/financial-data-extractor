import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";

describe("Table Components", () => {
  describe("Table", () => {
    it("renders a table wrapper", () => {
      render(
        <Table data-testid="table">
          <TableBody>
            <TableRow>
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const wrapper = screen.getByTestId("table").parentElement;
      expect(wrapper).toHaveClass("relative", "w-full", "overflow-auto");
    });

    it("renders a table element", () => {
      render(<Table data-testid="table" />);
      const table = screen.getByTestId("table");
      expect(table.tagName).toBe("TABLE");
    });

    it("applies custom className", () => {
      render(
        <Table className="custom-table-class" data-testid="table">
          <TableBody>
            <TableRow>
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const table = screen.getByTestId("table");
      expect(table).toHaveClass("custom-table-class");
    });

    it("forwards ref correctly", () => {
      const ref = vi.fn();
      render(
        <Table ref={ref}>
          <TableBody>
            <TableRow>
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      expect(ref).toHaveBeenCalled();
    });
  });

  describe("TableHeader", () => {
    it("renders TableHeader as thead", () => {
      render(
        <Table>
          <TableHeader data-testid="header">
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      const header = screen.getByTestId("header");
      expect(header.tagName).toBe("THEAD");
    });

    it("applies correct styling", () => {
      render(
        <Table>
          <TableHeader data-testid="header">
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      const header = screen.getByTestId("header");
      expect(header).toHaveClass("[&_tr]:border-b");
    });

    it("forwards ref correctly", () => {
      const ref = vi.fn();
      render(
        <Table>
          <TableHeader ref={ref}>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      expect(ref).toHaveBeenCalled();
    });
  });

  describe("TableBody", () => {
    it("renders TableBody as tbody", () => {
      render(
        <Table>
          <TableBody data-testid="body">
            <TableRow>
              <TableCell>Body</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const body = screen.getByTestId("body");
      expect(body.tagName).toBe("TBODY");
    });

    it("applies correct styling", () => {
      render(
        <Table>
          <TableBody data-testid="body">
            <TableRow>
              <TableCell>Body</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const body = screen.getByTestId("body");
      expect(body).toHaveClass("[&_tr:last-child]:border-0");
    });
  });

  describe("TableRow", () => {
    it("renders TableRow as tr", () => {
      render(
        <Table>
          <TableBody>
            <TableRow data-testid="row">
              <TableCell>Row</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const row = screen.getByTestId("row");
      expect(row.tagName).toBe("TR");
    });

    it("applies hover styles", () => {
      render(
        <Table>
          <TableBody>
            <TableRow data-testid="row">
              <TableCell>Row</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const row = screen.getByTestId("row");
      expect(row).toHaveClass("hover:bg-muted/50");
    });
  });

  describe("TableHead", () => {
    it("renders TableHead as th", () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead data-testid="head">Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      const head = screen.getByTestId("head");
      expect(head.tagName).toBe("TH");
    });

    it("applies correct styling", () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead data-testid="head">Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      const head = screen.getByTestId("head");
      expect(head).toHaveClass("h-12", "px-4", "text-left");
    });
  });

  describe("TableCell", () => {
    it("renders TableCell as td", () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell data-testid="cell">Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const cell = screen.getByTestId("cell");
      expect(cell.tagName).toBe("TD");
    });

    it("applies correct padding", () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell data-testid="cell">Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      const cell = screen.getByTestId("cell");
      expect(cell).toHaveClass("p-4");
    });
  });

  describe("Complete Table Structure", () => {
    it("renders a complete table", () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Header 1</TableHead>
              <TableHead>Header 2</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Cell 1</TableCell>
              <TableCell>Cell 2</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );

      expect(screen.getByText("Header 1")).toBeInTheDocument();
      expect(screen.getByText("Header 2")).toBeInTheDocument();
      expect(screen.getByText("Cell 1")).toBeInTheDocument();
      expect(screen.getByText("Cell 2")).toBeInTheDocument();
    });
  });
});
