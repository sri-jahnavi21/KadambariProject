'use client'

import Link from 'next/link'
import { Heart, Menu, Search, ShoppingBag, UserRound, X } from 'lucide-react'
import { useState } from 'react'

export default function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <button type="button" className="site-header__menu" onClick={() => setMenuOpen((open) => !open)} aria-label={menuOpen ? 'Close menu' : 'Open menu'}>
          {menuOpen ? <X data-icon="inline-start" /> : <Menu data-icon="inline-start" />}
        </button>
        <Link href="/" className="site-header__brand" aria-label="Kadambari home">कादंबरी</Link>
        <nav className={`site-header__nav ${menuOpen ? 'site-header__nav--open' : ''}`} aria-label="Main navigation">
          <Link href="/#shop" onClick={() => setMenuOpen(false)}>Shop</Link>
          <Link href="/#story" onClick={() => setMenuOpen(false)}>Our story</Link>
          <Link href="/#journal" onClick={() => setMenuOpen(false)}>Journal</Link>
        </nav>
        <div className="site-header__actions">
          <button type="button" aria-label="Search"><Search data-icon="inline-start" /></button>
          <Link href="/login" aria-label="Account"><UserRound data-icon="inline-start" /></Link>
          <button type="button" aria-label="Wishlist"><Heart data-icon="inline-start" /></button>
          <button type="button" aria-label="Shopping bag"><ShoppingBag data-icon="inline-start" /></button>
        </div>
      </div>
    </header>
  )
}
