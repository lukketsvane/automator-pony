'use client'

import { useState } from 'react'
import { Play, Grid3x3, List } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Home() {
  const videos = [
    {
      id: '1',
      url: 'https://lh3.googleusercontent.com/pw/AP1GczP_YOUR_VIDEO_URL_1',
      title: 'Video 1',
      thumbnail: '/video-thumbnail.png'
    },
    {
      id: '2',
      url: 'https://lh3.googleusercontent.com/pw/AP1GczP_YOUR_VIDEO_URL_2',
      title: 'Video 2',
      thumbnail: '/video-thumbnail.png'
    },
  ]

  const [currentVideo, setCurrentVideo] = useState(videos[0])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4 md:p-6">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Ponyseeo Videos</h1>
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
                      src={video.thumbnail || "/placeholder.svg"}
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

        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h3 className="font-semibold mb-2">How to add your videos:</h3>
          <ol className="text-sm space-y-1 list-decimal list-inside">
            <li>Open your Google Photos album: <a href="https://photos.app.goo.gl/ZMeEZxpuzC1Sj8uH8" className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">Your Album</a></li>
            <li>Click on a video, then click the 3 dots menu and select "Download"</li>
            <li>Cancel the download, then go to chrome://downloads/ and copy the full URL</li>
            <li>Edit app/page.tsx and replace the placeholder URLs with your video URLs</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
