'use client'

import { useState, useEffect } from 'react'
import { Play, Grid3x3, List, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import VideoStreamer from '@/components/video-streamer'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

interface Video {
  id: string
  title: string
  thumbnail: string
  videoUrl: string
  width: number
  height: number
}

export default async function Home() {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')
  const userEmail = cookieStore.get('user_email')
  
  if (!accessToken) {
    redirect('/login')
  }
  
  return <VideoStreamer userEmail={userEmail?.value} />
}

// VideoStreamer component is now imported from '@/components/video-streamer'
