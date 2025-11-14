import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET() {
  try {
    const cookieStore = await cookies()
    const accessToken = cookieStore.get('access_token')
    
    if (!accessToken) {
      return NextResponse.json({
        videos: [],
        error: 'Authentication required'
      }, { status: 401 })
    }

    console.log('[v0] Fetching videos from Google Photos Library API')
    
    const response = await fetch(
      'https://photoslibrary.googleapis.com/v1/mediaItems:search',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pageSize: 100,
          filters: {
            mediaTypeFilter: {
              mediaTypes: ['VIDEO']
            }
          }
        })
      }
    )
    
    console.log('[v0] API Response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('[v0] API Error:', errorText)
      throw new Error(`Google Photos API error: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[v0] Found media items:', data.mediaItems?.length || 0)
    
    const videos = (data.mediaItems || [])
      .filter((item: any) => item.mediaMetadata?.video)
      .map((item: any) => ({
        id: item.id,
        title: item.filename || 'Untitled Video',
        thumbnail: item.baseUrl + '=w640-h360-c',
        videoUrl: item.baseUrl + '=dv',
        width: parseInt(item.mediaMetadata?.width) || 1280,
        height: parseInt(item.mediaMetadata?.height) || 720,
        mimeType: item.mimeType
      }))
    
    console.log('[v0] Returning', videos.length, 'videos')
    
    return NextResponse.json({ videos })
    
  } catch (error) {
    console.error('[v0] Error fetching Google Photos:', error)
    
    return NextResponse.json({
      videos: [],
      error: error instanceof Error ? error.message : 'Failed to fetch videos'
    }, { status: 500 })
  }
}
