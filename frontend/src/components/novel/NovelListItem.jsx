import { User, Clock, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { appTheme } from '../../config/theme';
import { FlagIcon } from '../ui/FlagIcon';
import { TimeAgo } from '../ui/TimeAgo';

export const NovelListItem = ({ novel }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/novel/${novel.id}`);
  };

  return (
    <button
      onClick={handleClick}
      className={`group w-full text-left flex gap-4 p-3 rounded-lg transition-all duration-300 ${appTheme.colors.surface} ${appTheme.colors.surfaceHover} border border-transparent hover:border-slate-700`}
    >
    <div className="relative w-20 shrink-0 rounded overflow-hidden shadow-lg">
      <img src={novel.cover_path} alt={novel.name} className="w-full h-28 object-cover transition-transform duration-500 group-hover:scale-110" />
      {novel.country && (
        <div className="absolute bottom-0 left-0 right-0 p-1 bg-black/60 backdrop-blur-sm flex justify-center">
          <FlagIcon country={novel.country} />
        </div>
      )}
    </div>

    <div className="flex-1 flex flex-col justify-between min-w-0">
      <div>
        <h4 className={`font-bold text-lg truncate group-hover:text-rose-400 transition-colors ${appTheme.colors.textPrimary}`}>
          {novel.name}
        </h4>
        
        <div className="flex items-center gap-2 mt-1">
          {/*--------------GENRO PRINCIPAL */}
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 ${appTheme.colors.accent} uppercase tracking-wider`}>
            {novel.tags[0]}
          </span>

          {/*--------------N# CAP*/}
          {novel.chapters > 0 && (
            <span className={`text-sm font-medium ${appTheme.colors.textPrimary}`}>
              Cap. {novel.chapters}
            </span>
          )}

          {/*--------------ESTADO*/}
          {novel.status === 'ongoing' && (
            <span className="text-[10px] bg-blue-500 text-white px-1.5 py-0.5 rounded font-bold">ON</span>
          )}
          {novel.status === 'finished' && (
            <span className="text-[10px] bg-emerald-500 text-white px-1.5 py-0.5 rounded font-bold">FIN</span>
          )}
        </div>
      </div>

      <div className="mt-2">
        <p className={`text-sm flex items-center gap-1 ${appTheme.colors.textSecondary}`}>
          <User size={12} />
          <span className="truncate">{novel.author}</span>
        </p>
      </div>

      <div className={`flex items-center justify-between mt-auto pt-2 text-xs ${appTheme.colors.textSecondary}`}>
        <div className="flex items-center gap-1">
          <Clock size={12} />
          <TimeAgo dateString={novel.updated_at} />
        </div>
        <div className="flex items-center gap-1 hover:text-white cursor-pointer">
          <MessageSquare size={12} />
        </div>
      </div>
    </div>
  </button>
);
};
