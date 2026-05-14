import React, { useState } from 'react';
import './index.css';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number; // Changed to number for calculations
  category: string;
  image: string;
}

const MOCK_PRODUCTS: Product[] = [
  {
    id: 1,
    name: 'Caviar D’Or',
    description: 'Servido sobre blinis de trigo sarraceno y crema agria de trufa blanca.',
    price: 85,
    category: 'Entradas',
    image: 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&q=80&w=200'
  },
  {
    id: 2,
    name: 'Wagyu A5 Grillé',
    description: 'Corte premium con reducción de vino tinto y sal de maldon ahumada.',
    price: 120,
    category: 'Platos Fuertes',
    image: 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=200'
  },
  {
    id: 3,
    name: 'Esfera de Chocolate Noir',
    description: 'Mousse de cacao al 80% con corazón de frambuesa y oro comestible.',
    price: 25,
    category: 'Postres',
    image: 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&q=80&w=200'
  },
  {
    id: 4,
    name: 'Nectar de los Dioses',
    description: 'Cóctel artesanal con gin infusionado y esencias botánicas raras.',
    price: 45,
    category: 'Bebidas',
    image: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&q=80&w=200'
  }
];

const CATEGORIES = ['Todos', 'Entradas', 'Platos Fuertes', 'Bebidas', 'Postres'];

function App() {
  const [activeCategory, setActiveCategory] = useState('Todos');
  const [cart, setCart] = useState<{product: Product, quantity: number}[]>([]);

  const filteredProducts = activeCategory === 'Todos' 
    ? MOCK_PRODUCTS 
    : MOCK_PRODUCTS.filter(p => p.category === activeCategory);

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existing = prev.find(item => item.product.id === product.id);
      if (existing) {
        return prev.map(item => 
          item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  };

  const total = cart.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);

  const checkoutWhatsApp = () => {
    const phone = "5491122334455"; // Richon, aquí pondrías el número del cliente
    let message = "🍱 *Nuevo Pedido - Verix Gourmet*\n\n";
    cart.forEach(item => {
      message += `• ${item.quantity}x ${item.product.name} ($${item.product.price * item.quantity})\n`;
    });
    message += `\n*Total: $${total}*\n\n_Enviado desde Verix Menu_`;
    
    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/${phone}?text=${encodedMessage}`, '_blank');
  };

  return (
    <div className="vantablack-container">
      {/* Hero Section */}
      <section className="hero">
        <img src="/hero.png" alt="Luxury Dish" className="hero-img" />
        <div className="hero-overlay">
          <h1 className="restaurant-name">VERIX GOURMET</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Excluxividad en cada bocado</p>
        </div>
      </section>

      {/* Categories */}
      <div style={{ padding: '0 1rem' }}>
        <div className="categories">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              className={`category-pill ${activeCategory === cat ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Menu Grid */}
      <main className="menu-grid">
        {filteredProducts.map(product => (
          <div key={product.id} className="product-card glass fade-in">
            <div className="product-info">
              <h3 className="product-title">{product.name}</h3>
              <p className="product-desc">{product.description}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.8rem' }}>
                <span className="product-price">${product.price}</span>
                <button 
                  className="add-btn"
                  onClick={() => addToCart(product)}
                >
                  Agregar +
                </button>
              </div>
            </div>
            <img src={product.image} alt={product.name} className="product-img-small" />
          </div>
        ))}
      </main>

      {/* Floating Cart Button */}
      {cart.length > 0 && (
        <button className="cart-fab fade-in" onClick={checkoutWhatsApp}>
          <span className="cart-count">{cart.length}</span>
          🛒 Pedir ahora • ${total}
        </button>
      )}

      {/* Footer / Contact */}
      <footer style={{ padding: '3rem 1rem', textAlign: 'center', opacity: 0.5 }}>
        <p style={{ fontSize: '0.7rem' }}>Powered by VERIX STUDIO</p>
      </footer>
    </div>
  );
}

export default App;
