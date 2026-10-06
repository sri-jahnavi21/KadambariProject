'use client'

// Product text shown directly under each product picture, above the reviews strip.
// It reuses the reviews strip's own colours (#1b3a2b background, #f5f0e1 text),
// padding and line height, and the chat bubble's yellow for the button.
// Keep these descriptions in sync with data/products.json in the repo root.
const PRODUCTS = [
  {
    name: 'Black Kalamkari Sneaker',
    price: '5000 INR',
    tagline: 'Black on the outside, a story on the side.',
    description:
      'A low-top sneaker in black with a grey and white paisley-style panel in red and black, finished with white laces and a clean white sole. The dark panels keep the look easy to wear, while the printed side carries the Kalamkari story. The artwork on each pair is hand-painted, so no two pairs are exactly alike.',
    highlights: [
      'Low-top style',
      'Kalamkari-inspired print in red and black',
      'White laces and white sole',
      'Hand-painted, so each pair is slightly unique',
    ],
  },
  {
    name: 'Green Kalamkari Sneaker',
    price: '5000 INR',
    tagline: 'For people who want the art noticed first.',
    description:
      'A bold low-top sneaker with a green overlay and white toe over a vivid Kalamkari-inspired print in red, blue, yellow and green, finished with white laces and a white sole. It is made to be the first thing people notice. The artwork on each pair is hand-painted, so no two pairs are exactly alike.',
    highlights: [
      'Low-top style',
      'Multicolour Kalamkari-inspired print with a green overlay',
      'White laces and white sole',
      'Hand-painted, so each pair is slightly unique',
    ],
  },
]

export default function ProductInfo({ index }: { index: 0 | 1 }) {
  const product = PRODUCTS[index]

  function askAboutProduct() {
    window.dispatchEvent(new CustomEvent('kadambari:ask', { detail: `Tell me about the ${product.name}` }))
  }

  return (
    <div
      className="product-info"
      style={{
        background: '#1b3a2b',
        color: '#f5f0e1',
        padding: '2rem',
        textAlign: 'center',
        lineHeight: 1.6,
        borderBottom: '1px solid rgba(245, 240, 225, 0.25)',
      }}
    >
      <h2 style={{ margin: '0 0 0.25rem 0', fontSize: '1.4rem', fontWeight: 700 }}>{product.name}</h2>
      <p style={{ margin: '0 0 0.25rem 0', fontWeight: 700 }}>{product.price}</p>
      <p style={{ margin: '0 0 1rem 0', fontStyle: 'italic' }}>{product.tagline}</p>
      <p style={{ margin: '0 auto 1rem auto', maxWidth: '40rem' }}>{product.description}</p>
      <p style={{ margin: '0 auto 1.25rem auto', maxWidth: '40rem', fontSize: '0.9rem', opacity: 0.85 }}>
        {product.highlights.join(' · ')}
      </p>
      <button
        type="button"
        onClick={askAboutProduct}
        style={{
          background: '#ffd400',
          color: '#111',
          border: '2px solid #111',
          borderRadius: '999px',
          padding: '0.5rem 1.2rem',
          font: 'inherit',
          cursor: 'pointer',
        }}
      >
        Ask about this shoe
      </button>
    </div>
  )
}
