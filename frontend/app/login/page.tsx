'use client'

import Link from 'next/link'
import { ArrowLeft, Eye, EyeOff } from 'lucide-react'
import { FormEvent, useState } from 'react'
import SiteFooter from '@/components/site-footer'
import SiteHeader from '@/components/site-header'

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitted(true)
  }

  return <div className="account-page"><SiteHeader /><main className="login-main"><Link href="/" className="login-back"><ArrowLeft data-icon="inline-start" /> Back to shop</Link><section className="login-card" aria-labelledby="login-title"><p className="eyebrow">Welcome back</p><h1 id="login-title">Your Kadambari account</h1><p className="login-intro">Sign in to view your orders, save favourites, and continue your story.</p>{submitted && <div className="login-success" role="status">Thanks. Your sign-in details are ready to be submitted.</div>}<form className="login-form" onSubmit={handleSubmit}><label htmlFor="email">Email address</label><input id="email" name="email" type="email" autoComplete="email" placeholder="you@example.com" required /><div className="login-label-row"><label htmlFor="password">Password</label><Link href="#forgot">Forgot password?</Link></div><div className="password-field"><input id="password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Enter your password" required /><button type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? <EyeOff data-icon="inline-start" /> : <Eye data-icon="inline-start" />}</button></div><button className="login-submit" type="submit">Sign in</button></form><p className="login-create">New to Kadambari? <Link href="#create-account">Create an account</Link></p></section></main><SiteFooter /></div>
}
