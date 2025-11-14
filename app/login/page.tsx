'use client'

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Suspense } from "react"
import { useSearchParams } from 'next/navigation'
import { Alert, AlertDescription } from "@/components/ui/alert"

function LoginContent() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')
  
  const handleGoogleLogin = () => {
    const clientId = '160495080765-k7r6l919gpfo6i3m9a67muvdu8vjhf8o.apps.googleusercontent.com'
    const redirectUri = `${window.location.origin}/api/auth/callback`
    const scope = encodeURIComponent('openid email profile https://www.googleapis.com/auth/photoslibrary.readonly')
    
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${redirectUri}&` +
      `response_type=code&` +
      `scope=${scope}&` +
      `access_type=offline&` +
      `prompt=consent`
    
    console.log('[v0] Redirecting to Google OAuth:', authUrl)
    console.log('[v0] Redirect URI:', redirectUri)
    window.location.href = authUrl
  }

  const getErrorMessage = (error: string | null) => {
    switch (error) {
      case 'access_denied':
        return 'Access denied. Please grant the required permissions.'
      case 'no_code':
        return 'No authorization code received from Google.'
      case 'token_exchange_failed':
        return 'Failed to exchange token. This might be a redirect URI mismatch. Check Google Cloud Console.'
      case 'redirect_uri_mismatch':
        return `Redirect URI mismatch. Add ${window.location.origin}/api/auth/callback to Google Cloud Console authorized redirect URIs.`
      default:
        return error ? `Authentication error: ${error}` : null
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">
            Sign in with your Google account to access your video library
          </p>
        </div>
        
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{getErrorMessage(error)}</AlertDescription>
          </Alert>
        )}
        
        <Button onClick={handleGoogleLogin} className="w-full" size="lg">
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Sign in with Google
        </Button>
        
        <p className="text-xs text-muted-foreground mt-6 text-center">
          By signing in, you agree to access your Google Photos library
        </p>
        
        <div className="mt-4 p-3 bg-muted rounded-md">
          <p className="text-xs text-muted-foreground mb-1">Required redirect URI:</p>
          <code className="text-xs break-all">{typeof window !== 'undefined' ? `${window.location.origin}/api/auth/callback` : ''}</code>
        </div>
      </Card>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>}>
      <LoginContent />
    </Suspense>
  )
}
