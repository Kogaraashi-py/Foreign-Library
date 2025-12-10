import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/layaout/Navbar.jsx';
import { appTheme } from '../config/theme.js';
import { novelsApi } from '../services/api.js';
import { ArrowLeft, ChevronLeft, ChevronRight, Loader } from 'lucide-react';

export default function ChapterReader() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [chapter, setChapter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chaptersList, setChaptersList] = useState([]);

  useEffect(() => {
    const fetchChapterData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Obtener el capítulo específico
        const chapterData = await novelsApi.getChapterById(id);
        setChapter(chapterData);

        // Obtener la lista de capítulos de la novela para navegación
        const chaptersData = await novelsApi.getNovelChapters(chapterData.novel_id, { limit: 200 });
        setChaptersList(chaptersData);

      } catch (err) {
        console.error('Error fetching chapter:', err);
        setError('Error al cargar el capítulo. Inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchChapterData();
    }
  }, [id]);

  const handlePrevChapter = () => {
    if (!chapter || !chaptersList.length) return;

    const currentIndex = chaptersList.findIndex(ch => ch.id === chapter.id);
    if (currentIndex > 0) {
      const prevChapter = chaptersList[currentIndex - 1];
      navigate(`/chapter/${prevChapter.id}`);
    }
  };

  const handleNextChapter = () => {
    if (!chapter || !chaptersList.length) return;

    const currentIndex = chaptersList.findIndex(ch => ch.id === chapter.id);
    if (currentIndex < chaptersList.length - 1) {
      const nextChapter = chaptersList[currentIndex + 1];
      navigate(`/chapter/${nextChapter.id}`);
    }
  };

  const handleBackToNovel = () => {
    navigate(`/novel/${chapter?.novel_id}`);
  };

  // Verificar si hay capítulos anterior/siguiente disponibles
  const hasPrevChapter = chapter && chaptersList.length > 0 &&
    chaptersList.findIndex(ch => ch.id === chapter.id) > 0;

  const hasNextChapter = chapter && chaptersList.length > 0 &&
    chaptersList.findIndex(ch => ch.id === chapter.id) < chaptersList.length - 1;

  if (loading) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-500 mx-auto mb-4"></div>
            <p className={`${appTheme.colors.textSecondary}`}>Cargando capítulo...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !chapter) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className={`${appTheme.colors.textPrimary} text-xl mb-4`}>Oops!</p>
            <p className={`${appTheme.colors.textSecondary} mb-4`}>{error || 'Capítulo no encontrado'}</p>
            <button
              onClick={() => navigate('/')}
              className="bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white`}>
      <Navbar />

      {/* Navegación */}
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={handleBackToNovel}
            className={`flex items-center gap-2 ${appTheme.colors.textSecondary} hover:text-rose-400 transition-colors`}
          >
            <ArrowLeft size={20} />
            Volver a la novela
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevChapter}
              disabled={!hasPrevChapter}
              className={`p-2 rounded ${!hasPrevChapter ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-700'} transition-colors`}
            >
              <ChevronLeft size={20} />
            </button>
            <span className={`${appTheme.colors.textSecondary} text-sm`}>
              Capítulo {chapter.order_number}
            </span>
            <button
              onClick={handleNextChapter}
              disabled={!hasNextChapter}
              className={`p-2 rounded ${!hasNextChapter ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-700'} transition-colors`}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        {/* Contenido del capítulo */}
        <div className={`max-w-4xl mx-auto ${appTheme.colors.surface} rounded-lg p-8 shadow-lg`}>
          <h1 className={`text-2xl md:text-3xl font-bold mb-4 text-center ${appTheme.colors.textPrimary}`}>
            {chapter.title}
          </h1>

          {/* Información del capítulo */}
          <div className="flex justify-center items-center gap-4 mb-8 text-sm text-gray-500">
            <span>Capítulo {chapter.order_number}</span>
            {chaptersList.length > 0 && (
              <>
                <span>•</span>
                <span>{chaptersList.findIndex(ch => ch.id === chapter.id) + 1} de {chaptersList.length}</span>
              </>
            )}
          </div>

          {/* Barra de progreso */}
          {chaptersList.length > 0 && (
            <div className="w-full bg-gray-200 rounded-full h-2 mb-8">
              <div
                className="bg-rose-500 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${((chaptersList.findIndex(ch => ch.id === chapter.id) + 1) / chaptersList.length) * 100}%`
                }}
              ></div>
            </div>
          )}

          {/* Contenido del capítulo */}
          <div className={`${appTheme.colors.textSecondary} leading-relaxed whitespace-pre-line text-lg`}>
            {chapter.content}
          </div>

          {/* Navegación inferior */}
          <div className="flex justify-between items-center mt-12 pt-8 border-t border-gray-200">
            <button
              onClick={handlePrevChapter}
              disabled={!hasPrevChapter}
              className={`flex items-center gap-2 px-4 py-2 rounded transition-colors ${
                hasPrevChapter
                  ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  : 'bg-gray-50 text-gray-400 cursor-not-allowed'
              }`}
            >
              <ChevronLeft size={20} />
              Capítulo Anterior
            </button>

            <button
              onClick={handleNextChapter}
              disabled={!hasNextChapter}
              className={`flex items-center gap-2 px-4 py-2 rounded transition-colors ${
                hasNextChapter
                  ? 'bg-rose-500 hover:bg-rose-600 text-white'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              Siguiente Capítulo
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
