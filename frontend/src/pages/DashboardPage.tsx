import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Video, Search, Clock } from 'lucide-react'

export function DashboardPage() {
  const stats = [
    {
      title: 'Total Videos',
      value: '0',
      description: 'No videos uploaded yet',
      icon: Video,
    },
    {
      title: 'Total Searches',
      value: '0',
      description: 'No searches performed',
      icon: Search,
    },
    {
      title: 'Processing',
      value: '0',
      description: 'No videos processing',
      icon: Activity,
    },
    {
      title: 'Recent Activity',
      value: '-',
      description: 'No recent activity',
      icon: Clock,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to VisionTrace AI - Intelligent Video Search Platform
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Welcome message */}
      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>
            VisionTrace AI is ready. Here's what you can do next:
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h3 className="font-medium">1. Upload Videos</h3>
            <p className="text-sm text-muted-foreground">
              Upload surveillance or normal videos to make them searchable.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="font-medium">2. Search by Image or Text</h3>
            <p className="text-sm text-muted-foreground">
              Once videos are processed, search using an uploaded image or natural language queries.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="font-medium">3. Review Results</h3>
            <p className="text-sm text-muted-foreground">
              View similarity scores, jump to timestamps, and export reports for human review.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <Card className="border-primary/50 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-sm">AI Disclaimer</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            VisionTrace AI provides similarity matches for human review. This system does not confirm
            the identity of any individual. All results should be reviewed by trained personnel before
            any action is taken.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
