import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Header } from "../components/Header";

describe("Header component", () => {
  it("renders brand title and elexon data source attribution", () => {
    render(<Header />);
    expect(screen.getByText("WindWatch")).toBeInTheDocument();
    expect(screen.getByText("GB day-ahead wind forecast review")).toBeInTheDocument();
    expect(screen.getByText(/Elexon BMRS Live API/)).toBeInTheDocument();
  });
});
