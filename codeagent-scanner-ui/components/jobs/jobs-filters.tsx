"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, X } from "lucide-react";

interface JobsFiltersProps {
  statusFilter: string;
  onStatusChange: (value: string) => void;
  searchQuery: string;
  onSearchChange: (value: string) => void;
}

export function JobsFilters({
  statusFilter,
  onStatusChange,
  searchQuery,
  onSearchChange,
}: JobsFiltersProps) {
  const handleClearFilters = () => {
    onStatusChange("all");
    onSearchChange("");
  };

  const hasActiveFilters = statusFilter !== "all" || searchQuery !== "";

  return (
    <div className="flex flex-col md:flex-row gap-4">
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-3 text-muted" size={18} />
        <Input
          placeholder="Search repositories..."
          className="pl-10 bg-card border-border"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <Select value={statusFilter} onValueChange={onStatusChange}>
        <SelectTrigger className="w-full md:w-40 bg-card border-border">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent className="bg-card border-border">
          <SelectItem value="all">All Status</SelectItem>
          <SelectItem value="completed">Completed</SelectItem>
          <SelectItem value="running">In Progress</SelectItem>
          <SelectItem value="queued">Queued</SelectItem>
          <SelectItem value="failed">Failed</SelectItem>
          <SelectItem value="canceled">Canceled</SelectItem>
        </SelectContent>
      </Select>
      {hasActiveFilters && (
        <Button
          variant="outline"
          className="border-border bg-transparent"
          onClick={handleClearFilters}
        >
          <X size={18} className="mr-2" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}
