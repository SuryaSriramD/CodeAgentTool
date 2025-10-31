import type { LucideIcon } from "lucide-react"

interface KPICardProps {
  title: string
  value: string
  icon: LucideIcon
  trend: string
  variant?: "default" | "success" | "error"
}

export function KPICard({ title, value, icon: Icon, trend, variant = "default" }: KPICardProps) {
  const variantClasses = {
    default: "from-primary to-accent",
    success: "from-success to-emerald-600",
    error: "from-error to-red-600",
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-muted text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-lg bg-gradient-to-br ${variantClasses[variant]}`}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
      <p className="text-xs text-muted">{trend}</p>
    </div>
  )
}
