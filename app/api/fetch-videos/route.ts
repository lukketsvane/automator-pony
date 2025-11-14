import { NextResponse } from 'next/server'

const GOOGLE_PHOTOS_ALBUM = 'https://photos.app.goo.gl/ZMeEZxpuzC1Sj8uH8'

export async function GET() {
  console.log('[v0] Fetching Google Photos album:', GOOGLE_PHOTOS_ALBUM)
  
  try {
    // Fetch the album page
    const response = await fetch(GOOGLE_PHOTOS_ALBUM, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      },
      redirect: 'follow'
    })

    console.log('[v0] Response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch album: ${response.status}`)
    }

    const html = await response.text()
    console.log('[v0] HTML length:', html.length)
    
    // Extract video data from the page
    // Google Photos embeds data in JavaScript variables
    const videos: any[] = []
    
    // Try to find data in the HTML
    // Look for patterns like ["https://...",width,height,...]
    const urlPattern = /\["(https:\/\/lh3\.googleusercontent\.com[^"]+)"/g
    const matches = html.matchAll(urlPattern)
    
    let index = 0
    for (const match of matches) {
      const url = match[1]
      // Filter for video URLs (they often contain "=m" or "=dv" parameters)
      if (url.includes('=m') || url.includes('=dv') || url.includes('video')) {
        videos.push({
          id: `video-${index}`,
          url: url,
          title: `Video ${index + 1}`,
          thumbnail: url.replace(/=m\d+/, '=w400-h300') // Convert to thumbnail size
        })
        index++
      }
      
      // Limit to first 50 videos
      if (index >= 50) break
    }

    console.log('[v0] Found videos:', videos.length)

    if (videos.length === 0) {
      // Return mock data for testing if scraping fails
      console.log('[v0] No videos found via scraping, using test approach')
      return NextResponse.json({
        videos: [],
        message: 'Unable to automatically fetch videos from Google Photos. The album may require authentication or the format has changed.'
      })
    }

    return NextResponse.json({ videos })
  } catch (error) {
    console.error('[v0] Error fetching videos:', error)
    return NextResponse.json(
      { 
        error: 'Failed to fetch videos',
        details: error instanceof Error ? error.message : 'Unknown error',
        videos: []
      },
      { status: 500 }
    )
  }
}
