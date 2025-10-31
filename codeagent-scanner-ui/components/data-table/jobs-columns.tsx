"use client"

import type { ColumnDef } from "@tanstack/react-table"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowRight, RotateCcw } from "lucide-react"

export interface JobRow {
  id: string
  repo: string
  status: "completed" | "in-progress" | "failed" | "queued"
  issues: number
  critical: number
  duration: string
  timestamp: string
}

export const jobColumns: ColumnDef<JobRow>[] = [
  {
    accessorKey: "repo",
    header: "Repository",
    cell: ({ row }) => <span className="font-medium">{row.getValue("repo")}</span>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      return (
        <Badge variant={status === "completed" ? "default" : status === "in-progress" ? "secondary" : "destructive"}>
          {status}
        </Badge>
      )
    },
  },
  {
    accessorKey: "issues",
    header: "Issues",
  },
  {
    accessorKey: "critical",
    header: "Critical",
    cell: ({ row }) => {
      const critical = row.getValue("critical") as number
      return critical > 0 ? (
        <span className="text-error font-medium">{critical}</span>
      ) : (
        <span className="text-success">0</span>
      )
    },
  },
  {
    accessorKey: "duration",
    header: "Duration",
  },
  {
    accessorKey: "timestamp",
    header: "Time",
    cell: ({ row }) => <span className="text-muted text-sm">{row.getValue("timestamp")}</span>,
  },
  {
    id: "actions",
    header: () => <div className="text-right">Actions</div>,
    cell: ({ row }) => (
      <div className="flex justify-end gap-2">
        <Link href={`/jobs/${row.original.id}`}>
          <Button variant="ghost" size="sm" className="text-primary hover:text-primary cursor-pointer">
            <ArrowRight size={16} />
          </Button>
        </Link>
        {row.original.status === "completed" && (
          <Button variant="ghost" size="sm" className="cursor-pointer">
            <RotateCcw size={16} />
          </Button>
        )}
      </div>
    ),
  },
]
