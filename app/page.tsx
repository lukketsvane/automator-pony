'use client'

import { useState, useEffect } from 'react'
import { Play, Grid3x3, List, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Video {
  id: string
  url: string
  title: string
  thumbnail: string
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([])
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchVideos = async () => {
    setLoading(true)
    setError(null)
    console.log('[v0] Fetching videos from Google Photos album...')
    
    try {
      const response = await fetch('/api/fetch-videos')
      console.log('[v0] Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch videos: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('[v0] Fetched videos:', data)
      
      if (data.videos && data.videos.length > 0) {
        setVideos(data.videos)
        setCurrentVideo(data.videos[0])
      } else {
        setError('No videos found in the album')
      }
    } catch (err) {
      console.error('[v0] Error fetching videos:', err)
      setError(err instanceof Error ? err.message : 'Failed to load videos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchVideos()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-lg">Loading videos from Google Photos...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <p className="text-lg text-destructive mb-4">{error}</p>
          <Button onClick={fetchVideos}>Try Again</Button>
        </div>
      </div>
    )
  }

  if (!currentVideo) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-lg">No videos available</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4 md:p-6">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Ponyseeo Videos</h1>
          <div className="flex gap-2">
            <Button onClick={fetchVideos} variant="outline" size="icon">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('grid')}
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </header>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-card rounded-lg overflow-hidden border">
              <video
                key={currentVideo.id}
                className="w-full aspect-video bg-black"
                controls
                autoPlay
                src={currentVideo.url}
              >
                Your browser does not support the video tag.
              </video>
              <div className="p-4">
                <h2 className="text-xl font-semibold">{currentVideo.title}</h2>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-card rounded-lg border p-4">
              <h3 className="font-semibold mb-4">All Videos ({videos.length})</h3>
              <div className={viewMode === 'grid' ? 'grid grid-cols-2 gap-2' : 'space-y-2'}>
                {videos.map((video) => (
                  <button
                    key={video.id}
                    onClick={() => setCurrentVideo(video)}
                    className={`relative group overflow-hidden rounded-lg border-2 transition-all ${
                      currentVideo.id === video.id
                        ? 'border-primary'
                        : 'border-transparent hover:border-primary/50'
                    }`}
                  >
                    <img
                      src={video.thumbnail || "/placeholder.svg?height=200&width=300"}
                      alt={video.title}
                      className="w-full aspect-video object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <Play className="h-8 w-8 text-white" />
                    </div>
                    {viewMode === 'list' && (
                      <div className="p-2 bg-card">
                        <p className="text-sm font-medium truncate">{video.title}</p>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
