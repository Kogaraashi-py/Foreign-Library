import { appTheme } from '../../config/theme';

export const TagList = ({ tags }) => (
  <div className="flex flex-wrap gap-2 my-2">
    
    {tags.slice(0, 3).map((tag, idx) => (
      <span key={idx} className={`text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 ${appTheme.colors.accent} uppercase tracking-wider`}>
        {tag}
      </span>
    ))}
  </div>
);