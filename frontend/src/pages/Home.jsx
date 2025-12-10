import { useState, useEffect } from 'react';
import { Navbar } from '../components/layaout/Navbar.jsx'
import { HeroSection } from '../components/novel/HeroSection.jsx';
import { NovelListItem } from '../components/novel/NovelListItem.jsx';
import { NovelCoverCard } from '../components/novel/NovelCoverCard.jsx';
import { SectionHeader } from '../components/novel/SectionHeader.jsx';
import { novelsApi, transformNovelsList } from '../services/api.js';
import { appTheme } from '../config/theme.js';

export default function Home() {
  const [featuredNovel, setFeaturedNovel] = useState(null);
  const [recentNovels, setRecentNovels] = useState([]);
  const [topNovels, setTopNovels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Cargar las 10 mejores novelas (top rated)
        const bestNovels = await novelsApi.getBestNovels(10);
        const transformedBest = transformNovelsList(bestNovels);

        // Usar la primera como destacada en HeroSection
        if (transformedBest.length > 0) {
          setFeaturedNovel(transformedBest[0]);
        }

        // Usar todas las 10 mejores para la sección principal
        setTopNovels(transformedBest);

        // Cargar novelas recientes (últimas agregadas)
        const recentNovelsData = await novelsApi.getNovels({ limit: 12 });
        const transformedRecent = transformNovelsList(recentNovelsData);
        setRecentNovels(transformedRecent);

      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Error al cargar las novelas. Inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-500 mx-auto mb-4"></div>
            <p className={`${appTheme.colors.textSecondary}`}>Cargando novelas...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>
        <Navbar />
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className={`${appTheme.colors.textPrimary} text-xl mb-4`}>Oops!</p>
            <p className={`${appTheme.colors.textSecondary} mb-4`}>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-rose-500 hover:bg-rose-600 text-white px-4 py-2 rounded transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${appTheme.colors.background} font-sans selection:bg-rose-500 selection:text-white pb-20`}>

      <Navbar />

      <HeroSection novels={topNovels} />

      <main className="container mx-auto px-4">


        <SectionHeader title="Top 10 Novelas" />

        {/*-------------CARDS NOVELAS TOP*/}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
          {topNovels.map((novel) => (
            <NovelListItem key={novel.id} novel={novel} />
          ))}
        </div>

        {/*--------------NOVELAS RECIENTES*/}
        <SectionHeader title="Novelas Recientes" />

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {recentNovels.map((novel) => (
            <NovelCoverCard key={`cover-${novel.id}`} novel={novel} />
          ))}
        </div>
      </main>
    </div>
  );
}