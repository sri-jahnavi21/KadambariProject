import Link from 'next/link'
import { Link2, Mail } from 'lucide-react'

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer__grid">
        <div><p className="site-footer__mark">कादंबरी</p><p className="site-footer__copy">Kalamkari stories, made for every step.</p></div>
        <div><p className="site-footer__heading">Explore</p><Link href="/#shop">Shop all</Link><Link href="/#story">Our story</Link><Link href="/login">Account</Link></div>
        <div><p className="site-footer__heading">Help</p><Link href="/shipping">Shipping & returns</Link><Link href="/contact">Contact us</Link><Link href="/size-guide">Size guide</Link></div>
        <div><p className="site-footer__heading">Stay in the loop</p><p className="site-footer__copy">New stories, small releases, and thoughtful notes.</p><form className="site-footer__subscribe"><label className="sr-only" htmlFor="footer-email">Email address</label><input id="footer-email" type="email" placeholder="Your email address" /><button type="submit" aria-label="Subscribe"><Mail data-icon="inline-start" /></button></form></div>
      </div>
      <div className="site-footer__bottom"><span>© 2026 Kadambari</span><span>Made with care in India</span><div className="site-footer__social"><Link href="#" aria-label="Social links"><Link2 data-icon="inline-start" /></Link></div></div>
      <p style={{ textAlign: 'center', fontSize: '0.8rem', opacity: 0.75, margin: '0.75rem 0 0 0' }}>Demo store built for a student project. Product images are for demonstration only.</p>
    </footer>
  )
}
