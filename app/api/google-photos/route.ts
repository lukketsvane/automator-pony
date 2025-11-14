import { NextResponse } from 'next/server'

// Google Photos shared album URL
const ALBUM_URL = 'https://photos.app.goo.gl/ZMeEZxpuzC1Sj8uH8'

export async function GET() {
  try {
    // For Google Photos shared albums, we need to parse the page HTML
    // since there's no direct API access without OAuth
    const response = await fetch(ALBUM_URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    })

    const html = await response.text()
    
    // Extract video data from the page
    // Google Photos embeds data in a specific format
    const dataMatch = html.match(/data:function$$$$\{return\s+(\[.+?\])\}/)
    
    if (!dataMatch) {
      console.log('[v0] No video data found in album page')
      return NextResponse.json({ videos: [] })
    }

    const rawData = dataMatch[1]
    const parsedData = JSON.parse(rawData)
    
    console.log('[v0] Parsed album data structure')
    
    // Parse video items from the nested structure
    const videos = extractVideos(parsedData)
    
    console.log(`[v0] Found ${videos.length} videos`)
    
    return NextResponse.json({ videos })
  } catch (error) {
    console.error('[v0] Error fetching Google Photos:', error)
    
    // Return mock data for development
    return NextResponse.json({
      videos: [
        {
          id: '1',
          title: 'Sample Video 1',
          thumbnail: '/video-thumbnail-1.png',
          videoUrl: '/sample-video-concept.png',
          width: 1280,
          height: 720
        },
        {
          id: '2',
          title: 'Sample Video 2',
          thumbnail: '/video-thumbnail-2.png',
          videoUrl: '/sample-video-concept.png',
          width: 1280,
          height: 720
        }
      ]
    })
  }
}

function extractVideos(data: any[]): any[] {
  const videos: any[] = []
  
  try {
    // Google Photos data structure varies, but typically:
    // Videos are nested in arrays with specific indices
    // Each video has: [url, width, height, ...metadata]
    
    function traverse(obj: any, depth = 0) {
      if (depth > 10) return // Prevent infinite recursion
      
      if (Array.isArray(obj)) {
        obj.forEach((item) => traverse(item, depth + 1))
      } else if (obj && typeof obj === 'object') {
        Object.values(obj).forEach((value) => traverse(value, depth + 1))
      } else if (typeof obj === 'string') {
        // Look for video URLs (contain googleusercontent.com and video format)
        if (obj.includes('googleusercontent.com') && 
            (obj.includes('.mp4') || obj.includes('.mov') || obj.includes('video'))) {
          videos.push({
            id: `video-${videos.length}`,
            title: `Video ${videos.length + 1}`,
            thumbnail: obj.replace('=dv', '=w640-h360'),
            videoUrl: obj,
            width: 1280,
            height: 720
          })
        }
      }
    }
    
    traverse(data)
  } catch (error) {
    console.error('[v0] Error parsing video data:', error)
  }
  
  return videos
}
