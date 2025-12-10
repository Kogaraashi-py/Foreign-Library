import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/layaout/Navbar.jsx';
import { SectionHeader } from '../components/novel/SectionHeader.jsx';
import { NovelListItem } from '../components/novel/NovelListItem.jsx';
import { NovelCoverCard } from '../components/novel/NovelCoverCard.jsx';
import { novelsApi, transformNovelsList } from '../services/api.js';
import { appTheme } from '../config/theme.js';
import { Search, ArrowLeft, Filter } from 'lucide-react';

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const query = searchParams.get('q') || '';
  const genreId = searchParams.get('genre_id');
  const status = searchParams.get('status');
  const minRating = searchParams.get('min_rating');

  useEffect(() => {
    const performSearch = async () => {
      try {
        setLoading(true);
        setError(null);

        const searchParams = { limit: 50 };
        if (query) searchParams.q = query;
        if (genreId) searchParams.genre_id = genreId;
        if (status) searchParams.status = status;
        if (minRating) searchParams.min_rating = minRating;

        let searchResults;
        if (query || genreId || status || minRating) {
          // Búsqueda con filtros
          searchResults = await novelsApi.searchNovels(searchParams);
        } else {
          // Si no hay parámetros, mostrar novelas recientes
          searchResults = await novelsApi.getNovels({ limit: 50 });
        }

        const transformedResults = transformNovelsList(searchResults);
        setResults(transformedResults);

      } catch (err) {
        console.error('Error performing search:', err);
        setError('Error al realizar la búsqueda. Inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };

    performSearch();
  }, [query, genreId, status, minRating]);

  const getSearchTitle = () => {
    if (query) {
      return `Resultados para "${query}"`;
    } else if (genreId || status || minRating) {
      return 'Búsqueda con filtros';
    } else {
      return 'Novelas Recientes';
    }
  };

  const getSearchDescription = () => {
    const filters = [];
    if (genreId) filters.push(`Género: ${genreId}`);
    if (status) filters.push(`Estado: ${status}`);
    if (minRating) filters.push(`Rating mínimo: ${minRating}`);
    return filters.length > 0 ? filters.join(', ') : '';
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-500 mx-auto mb-4"></div>
            <p className={`${appTheme.colors.textSecondary}`}>Buscando novelas...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className={`${appTheme.colors.textPrimary} text-xl mb-4`}>Oops!</p>
            <p className={`${appTheme.colors.textSecondary} mb-4`}>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors mr-4"
            >
              Reintentar
            </button>
            <button
              onClick={() => navigate('/')}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>
      <Navbar />

      {/* Header con información de búsqueda */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate('/')}
            className={`flex items-center gap-2 ${appTheme.colors.textSecondary} hover:text-rose-400 transition-colors`}
          >
            <ArrowLeft size={20} />
            Volver al inicio
          </button>

          {(query || genreId || status || minRating) && (
            <button
              onClick={() => navigate('/search/advanced')}
              className="flex items-center gap-2 bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors"
            >
              <Filter size={16} />
              Modificar búsqueda
            </button>
          )}
        </div>

        <div className="mb-6">
          <h1 className={`text-3xl font-bold mb-2 ${appTheme.colors.textPrimary}`}>
            {getSearchTitle()}
          </h1>
          {getSearchDescription() && (
            <p className={`${appTheme.colors.textSecondary} text-lg`}>
              {getSearchDescription()}
            </p>
          )}
          <p className={`${appTheme.colors.textSecondary} mt-2`}>
            {results.length} {results.length === 1 ? 'resultado encontrado' : 'resultados encontrados'}
          </p>
        </div>

        {/* Controles de vista */}
        {results.length > 0 && (
          <div className="flex justify-end mb-4">
            <div className="flex bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  viewMode === 'list'
                    ? 'bg-rose-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Lista
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-rose-500 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                Cuadrícula
              </button>
            </div>
          </div>
        )}

        {/* Resultados */}
        {results.length === 0 ? (
          <div className="text-center py-12">
            <Search size={48} className={`${appTheme.colors.textSecondary} mx-auto mb-4`} />
            <h3 className={`text-xl font-semibold mb-2 ${appTheme.colors.textPrimary}`}>
              No se encontraron resultados
            </h3>
            <p className={`${appTheme.colors.textSecondary} mb-4`}>
              Intenta con otros términos de búsqueda o modifica los filtros.
            </p>
            <button
              onClick={() => navigate('/search/advanced')}
              className="bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors"
            >
              Búsqueda Avanzada
            </button>
          </div>
        ) : viewMode === 'list' ? (
          <div className="space-y-4">
            {results.map((novel) => (
              <NovelListItem key={novel.id} novel={novel} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {results.map((novel) => (
              <NovelCoverCard key={novel.id} novel={novel} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
