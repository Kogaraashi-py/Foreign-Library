import { useNavigate } from 'react-router-dom';
import { appTheme } from '../../config/theme';

export const NovelCoverCard = ({ novel }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/novel/${novel.id}`);
  };

  return (
    <button onClick={handleClick} className="group w-full text-left relative">
      {/*--------------CONTENEDOR DE IMAGEN*/}
      <div className="relative rounded-lg overflow-hidden aspect-2/3 mb-2">
        <img
          src={novel.cover_path}
          alt={novel.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-linear-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-4">
          <span className="bg-rose-500 text-white text-xs font-bold px-3 py-1.5 rounded-full transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300 shadow-lg">
            Leer Ahora
          </span>
        </div>

        {/*--------------BADGE DE RATING*/}
        <div className="absolute top-0 right-0 bg-rose-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-bl group-hover:pr-2 transition-all duration-300">
          {novel.rating}
        </div>
      </div>

      {/*--------------TITULO NOVELA*/}
      <h5 className={`text-sm font-medium truncate ${appTheme.colors.textPrimary} group-hover:text-rose-400 transition-colors`}>
        {novel.name}
      </h5>

      {/*--------------GENERO*/}
      <p className={`text-xs ${appTheme.colors.textSecondary}`}>
        {novel.tags && novel.tags[0] ? novel.tags[0] : 'Sin género'}
      </p>
    </button>
  );
};