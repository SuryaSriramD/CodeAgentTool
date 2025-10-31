"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { ReportsTable } from "@/components/reports/reports-table";
import { ReportsFilters } from "@/components/reports/reports-filters";
import type { SeverityLevel } from "@/lib/api-client";

export default function ReportsPage() {
  const [filters, setFilters] = useState<{
    severity?: SeverityLevel;
    tool?: string;
    repo?: string;
  }>({});

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 md:ml-0">
        <Header title="Vulnerability Reports" />
        <div className="p-6 space-y-6">
          <ReportsFilters onFilterChange={setFilters} />
          <ReportsTable
            severity={filters.severity}
            tool={filters.tool}
            repo={filters.repo}
          />
        </div>
      </main>
    </div>
  );
}
