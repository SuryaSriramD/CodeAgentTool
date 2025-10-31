"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, X } from "lucide-react";
import type { SeverityLevel } from "@/lib/api-client";

interface ReportsFiltersProps {
  onFilterChange: (filters: {
    severity?: SeverityLevel;
    tool?: string;
    repo?: string;
  }) => void;
}

export function ReportsFilters({ onFilterChange }: ReportsFiltersProps) {
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<SeverityLevel | "all">("all");
  const [tool, setTool] = useState<string>("all");

  const handleSearchChange = (value: string) => {
    setSearch(value);
    onFilterChange({
      severity: severity !== "all" ? severity : undefined,
      tool: tool !== "all" ? tool : undefined,
      repo: value || undefined,
    });
  };

  const handleSeverityChange = (value: string) => {
    setSeverity(value as SeverityLevel | "all");
    onFilterChange({
      severity: value !== "all" ? (value as SeverityLevel) : undefined,
      tool: tool !== "all" ? tool : undefined,
      repo: search || undefined,
    });
  };

  const handleToolChange = (value: string) => {
    setTool(value);
    onFilterChange({
      severity: severity !== "all" ? severity : undefined,
      tool: value !== "all" ? value : undefined,
      repo: search || undefined,
    });
  };

  const handleClearFilters = () => {
    setSearch("");
    setSeverity("all");
    setTool("all");
    onFilterChange({});
  };

  const hasActiveFilters = search || severity !== "all" || tool !== "all";

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 text-muted" size={18} />
          <Input
            placeholder="Search by repository URL or job ID..."
            className="pl-10 bg-card border-border"
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
        </div>
        <Select value={severity} onValueChange={handleSeverityChange}>
          <SelectTrigger className="w-full md:w-40 bg-card border-border">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            <SelectItem value="all">All Severity</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
        <Select value={tool} onValueChange={handleToolChange}>
          <SelectTrigger className="w-full md:w-40 bg-card border-border">
            <SelectValue placeholder="Tool" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            <SelectItem value="all">All Tools</SelectItem>
            <SelectItem value="semgrep">Semgrep</SelectItem>
            <SelectItem value="bandit">Bandit</SelectItem>
            <SelectItem value="depcheck">DepCheck</SelectItem>
          </SelectContent>
        </Select>
        {hasActiveFilters && (
          <Button
            variant="outline"
            className="border-border bg-transparent"
            onClick={handleClearFilters}
          >
            <X size={18} />
            Clear Filters
          </Button>
        )}
      </div>
    </div>
  );
}
