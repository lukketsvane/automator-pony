import { NextResponse } from 'next/server'

const GOOGLE_PHOTOS_API_KEY = 'AIzaSyDk2u58Ot4wh3Gt7sXY80h7qSFbH70ssz0'
const SHARED_ALBUM_URL = 'https://photos.app.goo.gl/ZMeEZxpuzC1Sj8uH8'

// Extract album ID from the shared URL
async function getAlbumId(shareUrl: string): Promise<string | null> {
  try {
    // Follow redirects to get the actual album ID
    const response = await fetch(shareUrl, {
      redirect: 'follow',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })
    
    const finalUrl = response.url
    console.log('[v0] Final album URL:', finalUrl)
    
    // Extract album ID from URL patterns like:
    // https://photos.google.com/share/{ALBUM_ID}
    const match = finalUrl.match(/\/share\/([A-Za-z0-9_-]+)/)
    return match ? match[1] : null
  } catch (error) {
    console.error('[v0] Error resolving album URL:', error)
    return null
  }
}

export async function GET() {
  try {
    console.log('[v0] Fetching videos from Google Photos album')
    
    // Get the album ID from the shared URL
    const albumId = await getAlbumId(SHARED_ALBUM_URL)
    
    if (!albumId) {
      console.log('[v0] Could not extract album ID from URL')
      return NextResponse.json({ 
        videos: [],
        error: 'Could not access album. The album may need to be made fully public or require OAuth authentication.'
      })
    }
    
    console.log('[v0] Album ID:', albumId)
    
    // Use Google Photos Library API to list media items
    // Note: Shared albums require the sharedAlbums.list endpoint
    const apiUrl = `https://photoslibrary.googleapis.com/v1/sharedAlbums/${albumId}/mediaItems?key=${GOOGLE_PHOTOS_API_KEY}`
    
    const response = await fetch(apiUrl, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('[v0] API Error:', response.status, errorText)
      
      // Try alternative approach: mediaItems.search with albumId
      return await searchMediaItems(albumId)
    }
    
    const data = await response.json()
    console.log('[v0] API Response received')
    
    // Filter for video items only
    const videos = (data.mediaItems || [])
      .filter((item: any) => item.mimeType?.startsWith('video/'))
      .map((item: any, index: number) => ({
        id: item.id,
        title: item.filename || `Video ${index + 1}`,
        thumbnail: `${item.baseUrl}=w640-h360`,
        videoUrl: `${item.baseUrl}=dv`, // Download video format
        width: parseInt(item.mediaMetadata?.width) || 1280,
        height: parseInt(item.mediaMetadata?.height) || 720,
        mimeType: item.mimeType
      }))
    
    console.log(`[v0] Found ${videos.length} videos`)
    
    return NextResponse.json({ videos })
  } catch (error) {
    console.error('[v0] Error fetching Google Photos:', error)
    
    return NextResponse.json({
      videos: [],
      error: 'Failed to fetch videos. Please ensure the album is publicly accessible and the API key is valid.'
    })
  }
}

// Alternative method: Use mediaItems.search endpoint
async function searchMediaItems(albumId: string) {
  try {
    console.log('[v0] Trying mediaItems.search endpoint')
    
    const searchUrl = `https://photoslibrary.googleapis.com/v1/mediaItems:search?key=${GOOGLE_PHOTOS_API_KEY}`
    
    const response = await fetch(searchUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        albumId: albumId,
        pageSize: 100
      })
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('[v0] Search API Error:', response.status, errorText)
      return NextResponse.json({ 
        videos: [],
        error: 'Unable to access album with API key. OAuth authentication may be required for this album.'
      })
    }
    
    const data = await response.json()
    
    // Filter for video items only
    const videos = (data.mediaItems || [])
      .filter((item: any) => item.mimeType?.startsWith('video/'))
      .map((item: any, index: number) => ({
        id: item.id,
        title: item.filename || `Video ${index + 1}`,
        thumbnail: `${item.baseUrl}=w640-h360`,
        videoUrl: `${item.baseUrl}=dv`,
        width: parseInt(item.mediaMetadata?.width) || 1280,
        height: parseInt(item.mediaMetadata?.height) || 720,
        mimeType: item.mimeType
      }))
    
    console.log(`[v0] Found ${videos.length} videos via search`)
    
    return NextResponse.json({ videos })
  } catch (error) {
    console.error('[v0] Search method error:', error)
    return NextResponse.json({ 
      videos: [],
      error: 'All API methods failed. OAuth authentication is required.'
    })
  }
}
