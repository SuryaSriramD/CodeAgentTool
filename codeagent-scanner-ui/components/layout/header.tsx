"use client"

import { Bell, User } from "lucide-react"

export function Header({ title }: { title: string }) {
  return (
    <header className="sticky top-0 z-30 bg-background/80 backdrop-blur border-b border-border">
      <div className="flex items-center justify-between px-6 py-4">
        <h1 className="text-2xl font-bold">{title}</h1>
        <div className="flex items-center gap-4">
          <button className="p-2 rounded-lg hover:bg-card transition-colors">
            <Bell size={20} className="text-muted" />
          </button>
          <button className="p-2 rounded-lg hover:bg-card transition-colors">
            <User size={20} className="text-muted" />
          </button>
        </div>
      </div>
    </header>
  )
}
