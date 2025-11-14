'use client'

import { useState, useEffect } from 'react'
import { Play, Grid3x3, List, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface Video {
  id: string
  title: string
  thumbnail: string
  videoUrl: string
  width: number
  height: number
}

interface VideoStreamerProps {
  userEmail?: string
}

export default function VideoStreamer({ userEmail }: VideoStreamerProps) {
  const [videos, setVideos] = useState<Video[]>([])
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchVideos()
  }, [])

  const fetchVideos = async () => {
    try {
      const response = await fetch('/api/google-photos')
      const data = await response.json()
      console.log('[v0] Fetched videos:', data)
      setVideos(data.videos || [])
      if (data.videos && data.videos.length > 0) {
        setSelectedVideo(data.videos[0])
      }
    } catch (error) {
      console.error('[v0] Failed to fetch videos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' })
    window.location.href = '/login'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading videos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Video Library</h1>
            {userEmail && (
              <p className="text-sm text-muted-foreground mt-1">
                Signed in as {userEmail}
              </p>
            )}
          </div>
          <div className="flex gap-2">
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
            <Button
              variant="outline"
              size="icon"
              onClick={handleLogout}
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>


        {/* Video Player */}
        {selectedVideo && (
          <Card className="mb-6 p-4 lg:p-6">
            <div className="aspect-video bg-black rounded-lg overflow-hidden mb-4">
              <video
                key={selectedVideo.id}
                className="w-full h-full"
                controls
                autoPlay
                src={selectedVideo.videoUrl}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <h2 className="text-xl font-semibold">{selectedVideo.title}</h2>
          </Card>
        )}

        {/* Video Grid/List */}
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4'
              : 'flex flex-col gap-4'
          }
        >
          {videos.map((video) => (
            <Card
              key={video.id}
              className={`cursor-pointer transition-all hover:ring-2 hover:ring-primary ${
                selectedVideo?.id === video.id ? 'ring-2 ring-primary' : ''
              } ${viewMode === 'list' ? 'flex flex-row' : ''}`}
              onClick={() => setSelectedVideo(video)}
            >
              <div
                className={`relative bg-black ${
                  viewMode === 'grid' ? 'aspect-video' : 'w-48 h-32'
                }`}
              >
                <img
                  src={video.thumbnail || "/placeholder.svg"}
                  alt={video.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/50 transition-colors">
                  <div className="bg-white/90 rounded-full p-3">
                    <Play className="h-6 w-6 text-black fill-black" />
                  </div>
                </div>
              </div>
              <div className={viewMode === 'grid' ? 'p-3' : 'flex-1 p-4'}>
                <h3 className="font-medium line-clamp-2">{video.title}</h3>
              </div>
            </Card>
          ))}
        </div>

        {videos.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No videos found in the album</p>
          </div>
        )}
      </div>
    </div>
  )
}
