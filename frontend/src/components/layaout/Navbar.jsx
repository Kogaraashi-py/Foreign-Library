import { appTheme } from '../../config/theme';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Settings } from 'lucide-react';

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleAdvancedSearch = () => {
    navigate('/search/advanced');
  };

  return (
    <nav className={`
      ${isScrolled ? appTheme.colors.surface : 'bg-transparent'}
      border-b
      ${isScrolled ? appTheme.colors.border : 'border-transparent'}
      px-4 py-3 flex items-center sticky top-0 z-50
      transition-all duration-300
    `}>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-rose-500 rounded flex items-center justify-center font-bold text-white">N</div>
        <span className={`font-bold text-xl ${appTheme.colors.textPrimary}`}>Foreign Library</span>
      </div>

      {/* Barra de búsqueda */}
      <div className="flex items-center gap-4 flex-1 max-w-md mx-4">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar novelas..."
            className={`w-full px-4 py-2 pl-10 rounded-full border transition-all duration-300 ${
              isScrolled
                ? 'bg-white/90 border-gray-300 text-gray-900 placeholder-gray-500'
                : 'bg-black/20 border-white/30 text-white placeholder-white/70'
            } focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent`}
          />
          <Search
            size={18}
            className={`absolute left-3 top-1/2 transform -translate-y-1/2 ${
              isScrolled ? 'text-gray-400' : 'text-white/70'
            }`}
          />
        </form>

        <button
          onClick={handleAdvancedSearch}
          className={`flex items-center gap-2 px-3 py-2 rounded-full transition-all duration-300 ${
            isScrolled
              ? 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              : 'text-white/80 hover:text-white hover:bg-white/10'
          }`}
        >
          <Settings size={16} />
          <span className="hidden sm:inline text-sm">Búsqueda Avanzada</span>
        </button>
      </div>

    </nav>
  );
};