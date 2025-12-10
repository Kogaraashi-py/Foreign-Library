import { appTheme } from '../../config/theme';
import { FlagIcon} from "@heroicons/react/24/solid";
import { ChevronLeft, ChevronRight, Star, Tags } from "lucide-react";
import { useState } from 'react';


export const HeroSection = ({ novels }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!novels || novels.length === 0) return null;

  const novel = novels[currentIndex];

  const nextNovel = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % novels.length);
  };

  const prevNovel = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + novels.length) % novels.length);
  };

  return (
    <div className="relative w-full md:h-[500px] overflow-hidden group">

     {/*--------------FONDO*/}
      <div 
        className="absolute inset-0 bg-cover bg-center blur-xl opacity-40 scale-110"
        style={{ backgroundImage: `url(${novel.cover_path})` }}
      />
      
      {/*--------------OVERLAY*/}
      <div className={`absolute inset-0 bg-linear-to-t md:bg-linear-to-r ${appTheme.colors.overlay}`} />

      <div className="relative z-10 container mx-auto px-4 py-8 h-full flex flex-col md:flex-row items-end md:items-center gap-6 md:gap-10">
        
        {/*-------------- PORTADA IMG*/}
        <div className="hidden md:block w-48 lg:w-64 shrink-0 shadow-2xl rounded-lg overflow-hidden border-2 border-white/10 transform group-hover:scale-105 transition-transform duration-300 relative">
          <img src={novel.cover_path} alt={novel.name} className="w-full h-auto object-cover aspect-2/3" />
          
          {/*-------------- DESTELLO ANIMADO*/}
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <div className="absolute inset-0 bg-linear-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
          </div>
        </div>



        <div className="flex-1 w-full text-left pb-4 md:pb-0">
          <h3 className={`font-bold text-sm tracking-widest mb-2 ${appTheme.colors.textSecondary}`}>
            NOVELA DESTACADA
          </h3>
          
          {/*---------PRINCIPAL TITL*/}
          <h1 className={`text-3xl md:text-5xl font-black leading-tight mb-3 ${appTheme.colors.textPrimary} drop-shadow-lg`}>
            {novel.name}
          </h1>
          
          {/*-----------SUBT */}
          {novel.original_title && (
            <h2 className={`text-lg md:text-xl font-medium mb-4 ${appTheme.colors.textSecondary} opacity-80`}>
              {novel.original_title}
            </h2>
          )}

          {/*---------GENERO*/}
          <Tags tags={novel.tags} />

          {/*----------DESCRIPCION*/}
          <p className={`text-sm md:text-base ${appTheme.colors.textSecondary} line-clamp-3 md:line-clamp-4 max-w-2xl mb-6 leading-relaxed`}>
            {novel.description}
          </p>



          <div className="flex items-center gap-4 mt-auto">
            {/*----------PAIS AUTORIA*/}
            <div className="flex items-center gap-2">
              {novel.country && <FlagIcon country={novel.country} />}
              <span className={`font-medium italic ${appTheme.colors.textPrimary}`}>{novel.author}</span>
            </div>

            {/*------------RATING*/}
            <div className={`flex items-center gap-1 px-3 py-1 rounded-full ${appTheme.colors.surface} border ${appTheme.colors.border}`}>
              <Star size={14} className="text-yellow-400 fill-yellow-400" />
              <span className={`${appTheme.colors.textPrimary} font-bold text-sm`}>{novel.rating}</span>
            </div>

            {/*----------ID BADGE*/}
            <div className="ml-auto md:ml-4 text-xs font-bold bg-white text-black px-2 py-1 rounded">
              NO. {novel.id}
            </div>
          </div>


        </div>
      </div>


      {/*--------NAVEGACION / BTNS*/}
      <button
        onClick={nextNovel}
        className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/30 text-white hover:bg-rose-500 transition-colors hidden md:block"
      >
        <ChevronRight size={24} />
      </button>
      <button
        onClick={prevNovel}
        className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/30 text-white hover:bg-rose-500 transition-colors hidden md:block"
      >
        <ChevronLeft size={24} />
      </button>

    </div>
  );
};