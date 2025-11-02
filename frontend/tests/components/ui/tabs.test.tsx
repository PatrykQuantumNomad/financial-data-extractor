import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

describe("Tabs Components", () => {
  it("renders tabs with list and triggers", () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2">Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Content 1</TabsContent>
        <TabsContent value="tab2">Content 2</TabsContent>
      </Tabs>
    );

    expect(screen.getByText("Tab 1")).toBeInTheDocument();
    expect(screen.getByText("Tab 2")).toBeInTheDocument();
    expect(screen.getByText("Content 1")).toBeInTheDocument();
  });

  it("renders TabsList with correct styling", () => {
    render(
      <Tabs>
        <TabsList data-testid="list">
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
        </TabsList>
      </Tabs>
    );

    const list = screen.getByTestId("list");
    expect(list).toHaveClass(
      "inline-flex",
      "h-10",
      "items-center",
      "justify-center",
      "rounded-md",
      "bg-muted"
    );
  });

  it("renders TabsTrigger with correct styling", () => {
    render(
      <Tabs>
        <TabsList>
          <TabsTrigger data-testid="trigger" value="tab1">
            Tab 1
          </TabsTrigger>
        </TabsList>
      </Tabs>
    );

    const trigger = screen.getByTestId("trigger");
    expect(trigger).toHaveClass("inline-flex", "items-center", "justify-center");
  });

  it("renders TabsContent", () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
        </TabsList>
        <TabsContent data-testid="content" value="tab1">
          Content
        </TabsContent>
      </Tabs>
    );

    const content = screen.getByTestId("content");
    expect(content).toHaveClass("ring-offset-background");
    expect(screen.getByText("Content")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(
      <Tabs>
        <TabsList>
          <TabsTrigger value="tab1" className="custom-tab-class">
            Tab
          </TabsTrigger>
        </TabsList>
      </Tabs>
    );

    const trigger = screen.getByText("Tab");
    expect(trigger).toHaveClass("custom-tab-class");
  });

  it("handles tab navigation", async () => {
    const user = userEvent.setup();
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2">Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Content 1</TabsContent>
        <TabsContent value="tab2">Content 2</TabsContent>
      </Tabs>
    );

    expect(screen.getByText("Content 1")).toBeInTheDocument();
    expect(screen.queryByText("Content 2")).not.toBeInTheDocument();

    const tab2 = screen.getByText("Tab 2");
    await user.click(tab2);

    expect(screen.queryByText("Content 1")).not.toBeInTheDocument();
    expect(screen.getByText("Content 2")).toBeInTheDocument();
  });
});
