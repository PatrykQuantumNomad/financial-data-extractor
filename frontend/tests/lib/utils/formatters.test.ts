import { describe, it, expect } from "vitest";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
} from "@/lib/utils/formatters";

describe("Formatters", () => {
  describe("formatCurrency", () => {
    it("returns '-' for null or undefined", () => {
      expect(formatCurrency(null)).toBe("-");
      expect(formatCurrency(undefined)).toBe("-");
    });

    it("returns '-' for NaN", () => {
      expect(formatCurrency(NaN)).toBe("-");
    });

    it("formats billions correctly", () => {
      expect(formatCurrency(1500)).toBe("$1.5B");
      expect(formatCurrency(2000)).toBe("$2.0B");
      expect(formatCurrency(-1500)).toBe("$-1.5B");
    });

    it("formats millions correctly", () => {
      expect(formatCurrency(100)).toBe("$100.0M");
      expect(formatCurrency(999)).toBe("$999.0M");
      expect(formatCurrency(-100)).toBe("$-100.0M");
    });

    it("formats small values correctly", () => {
      expect(formatCurrency(0.5)).toBe("$0.50");
      expect(formatCurrency(0.99)).toBe("$0.99");
      expect(formatCurrency(-0.5)).toBe("$-0.50");
    });

    it("handles zero", () => {
      expect(formatCurrency(0)).toBe("$0.00");
    });

    it("handles edge cases", () => {
      expect(formatCurrency(1)).toBe("$1.0M");
      expect(formatCurrency(1000)).toBe("$1.0B");
      expect(formatCurrency(999.999)).toBe("$1000.0M");
    });
  });

  describe("formatNumber", () => {
    it("returns '-' for null or undefined", () => {
      expect(formatNumber(null)).toBe("-");
      expect(formatNumber(undefined)).toBe("-");
    });

    it("returns '-' for NaN", () => {
      expect(formatNumber(NaN)).toBe("-");
    });

    it("formats integers correctly", () => {
      expect(formatNumber(0)).toBe("0");
      expect(formatNumber(1)).toBe("1");
      expect(formatNumber(1000)).toBe("1,000");
      expect(formatNumber(1000000)).toBe("1,000,000");
    });

    it("formats decimals correctly", () => {
      expect(formatNumber(1.5)).toBe("1.5");
      expect(formatNumber(1.99)).toBe("1.99");
      expect(formatNumber(1.999)).toBe("2");
      expect(formatNumber(1.123456)).toBe("1.12");
    });

    it("handles negative numbers", () => {
      expect(formatNumber(-100)).toBe("-100");
      expect(formatNumber(-1000)).toBe("-1,000");
      expect(formatNumber(-1.5)).toBe("-1.5");
    });

    it("handles very large numbers", () => {
      expect(formatNumber(1234567890)).toBe("1,234,567,890");
    });

    it("rounds to 2 decimal places max", () => {
      expect(formatNumber(1.999)).toBe("2");
      expect(formatNumber(1.995)).toBe("2");
    });
  });

  describe("formatPercent", () => {
    it("returns '-' for null or undefined", () => {
      expect(formatPercent(null)).toBe("-");
      expect(formatPercent(undefined)).toBe("-");
    });

    it("returns '-' for NaN", () => {
      expect(formatPercent(NaN)).toBe("-");
    });

    it("formats percentages correctly", () => {
      expect(formatPercent(0)).toBe("0.00%");
      expect(formatPercent(0.5)).toBe("50.00%");
      expect(formatPercent(1)).toBe("100.00%");
      expect(formatPercent(0.25)).toBe("25.00%");
    });

    it("handles decimals correctly", () => {
      expect(formatPercent(0.123)).toBe("12.30%");
      expect(formatPercent(0.999)).toBe("99.90%");
      expect(formatPercent(0.123456)).toBe("12.35%");
    });

    it("handles negative percentages", () => {
      expect(formatPercent(-0.5)).toBe("-50.00%");
      expect(formatPercent(-0.25)).toBe("-25.00%");
    });

    it("handles over 100%", () => {
      expect(formatPercent(1.5)).toBe("150.00%");
      expect(formatPercent(2)).toBe("200.00%");
    });
  });
});
