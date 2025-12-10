import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import NovelDetail from './pages/NovelDetail';
import ChapterReader from './pages/ChapterReader';
import SearchResults from './pages/SearchResults';
import AdvancedSearch from './pages/AdvancedSearch';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/novel/:id" element={<NovelDetail />} />
      <Route path="/chapter/:id" element={<ChapterReader />} />
      <Route path="/search" element={<SearchResults />} />
      <Route path="/search/advanced" element={<AdvancedSearch />} />
    </Routes>
  );
}