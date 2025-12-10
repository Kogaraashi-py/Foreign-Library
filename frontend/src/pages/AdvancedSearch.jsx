import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/layaout/Navbar.jsx';
import { SectionHeader } from '../components/novel/SectionHeader.jsx';
import { genresApi } from '../services/api.js';
import { appTheme } from '../config/theme.js';
import { Search, ArrowLeft, X } from 'lucide-react';

export default function AdvancedSearch() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [genres, setGenres] = useState([]);
  const [loadingGenres, setLoadingGenres] = useState(true);

  // Estados del formulario
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [selectedGenre, setSelectedGenre] = useState(searchParams.get('genre_id') || '');
  const [selectedStatus, setSelectedStatus] = useState(searchParams.get('status') || '');
  const [minRating, setMinRating] = useState(searchParams.get('min_rating') || '');

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        setLoadingGenres(true);
        const genresData = await genresApi.getGenres({ limit: 100 });
        setGenres(genresData);
      } catch (err) {
        console.error('Error fetching genres:', err);
      } finally {
        setLoadingGenres(false);
      }
    };

    fetchGenres();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();

    // Construir parámetros de búsqueda
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (selectedGenre) params.set('genre_id', selectedGenre);
    if (selectedStatus) params.set('status', selectedStatus);
    if (minRating) params.set('min_rating', minRating);

    // Navegar a resultados
    navigate(`/search?${params.toString()}`);
  };

  const clearFilters = () => {
    setQuery('');
    setSelectedGenre('');
    setSelectedStatus('');
    setMinRating('');
  };

  const statusOptions = [
    { value: 'ongoing', label: 'En curso' },
    { value: 'completed', label: 'Completada' },
    { value: 'hiatus', label: 'En pausa' },
    { value: 'dropped', label: 'Cancelada' }
  ];

  return (
    <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>
      <Navbar />

      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => navigate(-1)}
            className={`flex items-center gap-2 ${appTheme.colors.textSecondary} hover:text-rose-400 transition-colors`}
          >
            <ArrowLeft size={20} />
            Volver
          </button>
        </div>

        <div className="max-w-2xl mx-auto">
          <SectionHeader title="Búsqueda Avanzada" />

          <div className={`${appTheme.colors.surface} rounded-lg p-6 border ${appTheme.colors.border}`}>
            <form onSubmit={handleSearch} className="space-y-6">
              {/* Búsqueda por nombre */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${appTheme.colors.textPrimary}`}>
                  Buscar por nombre
                </label>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ej: Villano, Romance, Fantasy..."
                  className={`w-full px-4 py-3 rounded-lg border ${appTheme.colors.border} bg-transparent ${appTheme.colors.textPrimary} placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent`}
                />
                <p className={`text-sm ${appTheme.colors.textSecondary} mt-1`}>
                  Búsqueda parcial en el título de las novelas
                </p>
              </div>

              {/* Filtro por género */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${appTheme.colors.textPrimary}`}>
                  Género
                </label>
                <select
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                  className={`w-full px-4 py-3 rounded-lg border ${appTheme.colors.border} bg-transparent ${appTheme.colors.textPrimary} focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent`}
                  disabled={loadingGenres}
                >
                  <option value="">Todos los géneros</option>
                  {loadingGenres ? (
                    <option disabled>Cargando géneros...</option>
                  ) : (
                    genres.map((genre) => (
                      <option key={genre.id} value={genre.id}>
                        {genre.name}
                      </option>
                    ))
                  )}
                </select>
              </div>

              {/* Filtro por estado */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${appTheme.colors.textPrimary}`}>
                  Estado de la novela
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className={`w-full px-4 py-3 rounded-lg border ${appTheme.colors.border} bg-transparent ${appTheme.colors.textPrimary} focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent`}
                >
                  <option value="">Todos los estados</option>
                  {statusOptions.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Rating mínimo */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${appTheme.colors.textPrimary}`}>
                  Rating mínimo
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(e.target.value)}
                  placeholder="0.0 - 10.0"
                  className={`w-full px-4 py-3 rounded-lg border ${appTheme.colors.border} bg-transparent ${appTheme.colors.textPrimary} placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent`}
                />
                <p className={`text-sm ${appTheme.colors.textSecondary} mt-1`}>
                  Solo mostrar novelas con rating igual o superior
                </p>
              </div>

              {/* Botones de acción */}
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-rose-500 hover:bg-rose-600 text-white py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Search size={18} />
                  Buscar
                </button>

                <button
                  type="button"
                  onClick={clearFilters}
                  className={`px-6 py-3 rounded-lg border ${appTheme.colors.border} ${appTheme.colors.textPrimary} hover:bg-gray-800 transition-colors flex items-center gap-2`}
                >
                  <X size={18} />
                  Limpiar
                </button>
              </div>
            </form>

            {/* Información adicional */}
            <div className="mt-8 pt-6 border-t border-gray-700">
              <h3 className={`font-semibold mb-3 ${appTheme.colors.textPrimary}`}>
                Consejos de búsqueda:
              </h3>
              <ul className={`text-sm ${appTheme.colors.textSecondary} space-y-1`}>
                <li>• Puedes combinar múltiples filtros para resultados más precisos</li>
                <li>• La búsqueda por nombre es parcial (encuentra "Villano" en "El Villano...")</li>
                <li>• El rating mínimo filtra novelas con puntuación igual o superior</li>
                <li>• Si no aplicas filtros, verás las novelas más recientes</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
