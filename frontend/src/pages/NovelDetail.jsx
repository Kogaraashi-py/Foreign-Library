import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/layaout/Navbar.jsx';
import { SectionHeader } from '../components/novel/SectionHeader.jsx';
import { novelsApi, genresApi, transformNovelData } from '../services/api.js';
import { appTheme } from '../config/theme.js';
import { ArrowLeft, Star, User, Calendar, Tag, BookOpen, ChevronRight } from 'lucide-react';

export default function NovelDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [novel, setNovel] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [novelBasicInfo, setNovelBasicInfo] = useState(null);
  const [loadingChapter, setLoadingChapter] = useState(null);

  useEffect(() => {
    const fetchNovelData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Intentar cargar detalles completos de la novela
        try {
          const novelData = await novelsApi.getNovelById(id);
          const transformedNovel = transformNovelData(novelData);
          setNovel(transformedNovel);
          setNovelBasicInfo(transformedNovel);
        } catch (detailError) {
          console.warn('Could not fetch detailed novel info, trying to get basic info from lists:', detailError);

          // Intentar obtener información básica de las listas de novelas que sí funcionan
          try {
            const [bestNovels, recentNovels] = await Promise.all([
              novelsApi.getBestNovels(50), // Obtener más para tener más chances de encontrar la novela
              novelsApi.getNovels({ limit: 50 })
            ]);

            const allNovels = [...bestNovels, ...recentNovels];
            const foundNovel = allNovels.find(novel => novel.id === parseInt(id));

            if (foundNovel) {
              setNovelBasicInfo(transformNovelData(foundNovel));
            } else {
              // Si no encontramos la novela en las listas, usar info básica
              setNovelBasicInfo({
                id: parseInt(id),
                name: `Novela ${id}`,
                author: 'Desconocido',
                rating: 0,
                status: 'unknown',
                cover_path: 'https://via.placeholder.com/300x450/374151/ffffff?text=Sin+Imagen',
                description: 'Información no disponible en este momento.'
              });
            }
          } catch (listError) {
            console.warn('Could not fetch from lists either:', listError);
            // Fallback final
            setNovelBasicInfo({
              id: parseInt(id),
              name: `Novela ${id}`,
              author: 'Desconocido',
              rating: 0,
              status: 'unknown',
              cover_path: 'https://via.placeholder.com/300x450/374151/ffffff?text=Sin+Imagen',
              description: 'Información no disponible en este momento.'
            });
          }
        }

        // Cargar capítulos de la novela (esto sí funciona)
        const chaptersData = await novelsApi.getNovelChapters(id, { limit: 100 });
        setChapters(chaptersData);

      } catch (err) {
        console.error('Error fetching novel data:', err);
        setError('Error al cargar la novela. Inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchNovelData();
    }
  }, [id]);

  const handleChapterClick = (chapterId) => {
    setLoadingChapter(chapterId);
    // Pequeño delay para mostrar el feedback visual
    setTimeout(() => {
      navigate(`/chapter/${chapterId}`);
    }, 150);
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-500 mx-auto mb-4"></div>
            <p className={`${appTheme.colors.textSecondary}`}>Cargando novela...</p>
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

  if (!novelBasicInfo) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className={`${appTheme.colors.textSecondary}`}>Novela no encontrada</p>
            <button
              onClick={() => navigate('/')}
              className="bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors mt-4"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Usar información completa si está disponible, sino la básica
  const displayNovel = novel || novelBasicInfo;

  return (
    <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>
      <Navbar />

      {/* Botón de volver */}
      <div className="container mx-auto px-4 py-4">
        <button
          onClick={() => navigate('/')}
          className={`flex items-center gap-2 ${appTheme.colors.textSecondary} hover:text-rose-400 transition-colors`}
        >
          <ArrowLeft size={20} />
          Volver al inicio
        </button>
      </div>

      <div className="container mx-auto px-4">
        {/* Información principal de la novela */}
        <div className="flex flex-col md:flex-row gap-8 mb-12">
          {/* Portada */}
          <div className="flex-shrink-0">
            <div className="w-48 h-72 rounded-lg overflow-hidden shadow-2xl mx-auto md:mx-0">
              <img
                src={displayNovel.cover_path}
                alt={displayNovel.name}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Información detallada */}
          <div className="flex-1">
            <h1 className={`text-3xl md:text-4xl font-bold mb-4 ${appTheme.colors.textPrimary}`}>
              {displayNovel.name}
            </h1>

            {/* Nombres alternativos */}
            {displayNovel.alternative_names && displayNovel.alternative_names.length > 0 && (
              <div className="mb-4">
                <h3 className={`text-lg font-semibold mb-2 ${appTheme.colors.textPrimary}`}>
                  Títulos alternativos:
                </h3>
                <div className="flex flex-wrap gap-2">
                  {novel.alternative_names.map((altName, index) => (
                    <span
                      key={index}
                      className={`px-3 py-1 rounded-full text-sm ${appTheme.colors.surface} border ${appTheme.colors.border}`}
                    >
                      {altName.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Información básica */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className={`flex items-center gap-2 ${appTheme.colors.textSecondary}`}>
                <User size={18} />
                <span>Autor: {displayNovel.author}</span>
              </div>

              <div className={`flex items-center gap-2 ${appTheme.colors.textSecondary}`}>
                <Star size={18} className="text-yellow-400 fill-yellow-400" />
                <span>Rating: {displayNovel.rating}</span>
              </div>

              <div className={`flex items-center gap-2 ${appTheme.colors.textSecondary}`}>
                <BookOpen size={18} />
                <span>Estado: {displayNovel.status === 'ongoing' ? 'En curso' : displayNovel.status === 'completed' ? 'Completada' : displayNovel.status}</span>
              </div>

              <div className={`flex items-center gap-2 ${appTheme.colors.textSecondary}`}>
                <Calendar size={18} />
                <span>Capítulos: {displayNovel.chapters_count || chapters.length}</span>
              </div>
            </div>

            {/* Géneros */}
            {displayNovel.genres && displayNovel.genres.length > 0 && (
              <div className="mb-6">
                <h3 className={`text-lg font-semibold mb-3 ${appTheme.colors.textPrimary}`}>
                  Géneros:
                </h3>
                <div className="flex flex-wrap gap-2">
                  {novel.genres.map((genre) => (
                    <span
                      key={genre.id}
                      className={`px-3 py-1 rounded-full text-sm bg-rose-500/10 text-rose-400 border border-rose-500/20`}
                    >
                      {genre.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Descripción */}
            {displayNovel.description && (
              <div className="mb-6">
                <h3 className={`text-lg font-semibold mb-3 ${appTheme.colors.textPrimary}`}>
                  Sinopsis:
                </h3>
                <p className={`${appTheme.colors.textSecondary} leading-relaxed`}>
                  {displayNovel.description}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Lista de capítulos */}
        <SectionHeader title={`Capítulos (${chapters.length})`} />

        <div className={`rounded-lg ${appTheme.colors.surface} border ${appTheme.colors.border} overflow-hidden`}>
          {chapters.length === 0 ? (
            <div className="p-8 text-center">
              <p className={`${appTheme.colors.textSecondary}`}>No hay capítulos disponibles aún.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700">
              {chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  onClick={() => handleChapterClick(chapter.id)}
                  disabled={loadingChapter === chapter.id}
                  className={`w-full p-4 text-left hover:bg-gray-800/50 transition-colors group ${appTheme.colors.textPrimary} ${
                    loadingChapter === chapter.id ? 'opacity-75 cursor-wait' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className={`font-medium group-hover:text-rose-400 transition-colors ${
                        loadingChapter === chapter.id ? 'text-rose-400' : ''
                      }`}>
                        {loadingChapter === chapter.id ? 'Cargando...' : chapter.title}
                      </h4>
                      <p className={`text-sm ${appTheme.colors.textSecondary} mt-1`}>
                        Capítulo {chapter.order_number}
                      </p>
                    </div>
                    {loadingChapter === chapter.id ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-rose-400"></div>
                    ) : (
                      <ChevronRight size={20} className={`${appTheme.colors.textSecondary} group-hover:text-rose-400 transition-colors`} />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
