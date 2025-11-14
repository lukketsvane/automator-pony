import { auth } from "@/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  const isAuthenticated = !!req.auth
  const isLoginPage = req.nextUrl.pathname === '/login'
  
  // Redirect authenticated users away from login page
  if (isAuthenticated && isLoginPage) {
    return NextResponse.redirect(new URL('/', req.url))
  }
  
  // Redirect unauthenticated users to login page
  if (!isAuthenticated && !isLoginPage) {
    return NextResponse.redirect(new URL('/login', req.url))
  }
  
  return NextResponse.next()
})

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$).*)']
}
