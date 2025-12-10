// Configuración base de la API
const API_BASE_URL = '/api/v1';

// Función helper para hacer fetch con manejo de errores
async function apiFetch(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Servicios para Novelas
export const novelsApi = {
  // Obtener las mejores novelas (top rated)
  getBestNovels: async (limit = 10) => {
    return apiFetch(`/novels/best/?limit=${limit}`);
  },

  // Obtener todas las novelas con filtros y paginación
  getNovels: async (params = {}) => {
    const { skip = 0, limit = 20, status, min_rate } = params;
    let queryString = `?skip=${skip}&limit=${limit}`;

    if (status) queryString += `&status=${status}`;
    if (min_rate) queryString += `&min_rate=${min_rate}`;

    return apiFetch(`/novels/${queryString}`);
  },

  // Buscar novelas
  searchNovels: async (params = {}) => {
    const { q, genre_id, status, min_rating, skip = 0, limit = 20 } = params;
    let queryString = `?skip=${skip}&limit=${limit}`;

    if (q) queryString += `&q=${encodeURIComponent(q)}`;
    if (genre_id) queryString += `&genre_id=${genre_id}`;
    if (status) queryString += `&status=${status}`;
    if (min_rating) queryString += `&min_rating=${min_rating}`;

    return apiFetch(`/novels/search/${queryString}`);
  },

  // Obtener novela específica
  getNovelById: async (novelId) => {
    return apiFetch(`/novels/${novelId}`);
  },

  // Obtener capítulos de una novela
  getNovelChapters: async (novelId, params = {}) => {
    const { skip = 0, limit = 50 } = params;
    return apiFetch(`/novels/${novelId}/chapters?skip=${skip}&limit=${limit}`);
  },

  // Obtener capítulo específico
  getChapterById: async (chapterId) => {
    return apiFetch(`/chapters/${chapterId}`);
  },
};

// Servicios para Géneros
export const genresApi = {
  // Obtener todos los géneros
  getGenres: async (params = {}) => {
    const { skip = 0, limit = 50 } = params;
    return apiFetch(`/genres/?skip=${skip}&limit=${limit}`);
  },

  // Obtener género específico
  getGenreById: async (genreId) => {
    return apiFetch(`/genres/${genreId}`);
  },
};

// Health check
export const healthApi = {
  checkHealth: async () => {
    return apiFetch('/');
  },
};

// Función para transformar los datos de la API al formato esperado por los componentes
export const transformNovelData = (novel) => {
  // Mapear estados de la API a los usados por los componentes
  const statusMapping = {
    'completed': 'finished',
    'ongoing': 'ongoing',
    'hiatus': 'hiatus',
    'dropped': 'dropped'
  };

  return {
    ...novel,
    // Mapear cover_url a cover_path para compatibilidad (usar URL relativa para el proxy)
    cover_path: novel.cover_url ? novel.cover_url.replace('http://localhost:8000', '') : novel.cover_path,
    // Mapear genres a tags si existe
    tags: novel.genres ? novel.genres.map(g => g.name.toUpperCase()) : novel.tags || [],
    // Asegurar que chapters_count se mapee a chapters
    chapters: novel.chapters_count || novel.chapters || 0,
    // Asegurar formato de fechas
    updated_at: novel.updated_at || novel.created_at,
    // Mapear estados
    status: statusMapping[novel.status] || novel.status,
  };
};

// Función para transformar lista de novelas
export const transformNovelsList = (novels) => {
  return novels.map(transformNovelData);
};
