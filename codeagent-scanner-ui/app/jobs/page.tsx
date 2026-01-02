"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { JobsTable } from "@/components/jobs/jobs-table";
import { JobsFilters } from "@/components/jobs/jobs-filters";

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 md:ml-0">
        <Header title="Scan Jobs" />
        <div className="p-6 space-y-6">
          <JobsFilters
            statusFilter={statusFilter}
            onStatusChange={setStatusFilter}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
          />
          <JobsTable statusFilter={statusFilter} searchQuery={searchQuery} />
        </div>
      </main>
    </div>
  );
}
