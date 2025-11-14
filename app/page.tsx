import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import VideoStreamer from '@/components/video-streamer'

export default async function Home() {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')
  const userEmail = cookieStore.get('user_email')
  
  if (!accessToken) {
    redirect('/login')
  }
  
  return <VideoStreamer userEmail={userEmail?.value} />
}
