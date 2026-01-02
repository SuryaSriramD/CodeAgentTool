"use client"

import { Button } from "@/components/ui/button"
import type React from "react"

interface EmptyStateProps {
  title: string
  description: string
  icon?: React.ReactNode
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {icon && <div className="mb-4 text-muted">{icon}</div>}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-muted text-sm mb-6 max-w-sm">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="cursor-pointer">
          {action.label}
        </Button>
      )}
    </div>
  )
}
