import { ChevronRight } from 'lucide-react';
import { appTheme } from '../../config/theme';

export const SectionHeader = ({ title }) => (
  <div className="flex items-center justify-between mb-4 mt-8 px-1">
    
    <h2 className={`text-xl font-bold uppercase tracking-wide border-l-4 border-rose-500 pl-3 ${appTheme.colors.textPrimary}`}>
      {title}
    </h2>
    <a href="#" className={`flex items-center text-sm font-medium ${appTheme.colors.textSecondary} hover:text-white transition-colors`}>
      VER TODO <ChevronRight size={16} />
    </a>
  </div>
);