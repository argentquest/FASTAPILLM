import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useForm } from 'react-hook-form';
import { Search, Calendar, User, Book, Download, Eye, Trash } from 'lucide-react';
import { storyApi } from '../services/api';
import { useApiMutation } from '../hooks/useApi';
import type { Story } from '../types';

interface SearchForm {
  character: string;
}

const StoryHistory: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  
  const { register, handleSubmit } = useForm<SearchForm>();
  
  // Fetch all stories initially
  const { data: stories, isLoading, refetch } = useQuery(
    ['stories', searchQuery],
    () => searchQuery ? storyApi.searchByCharacter(searchQuery) : storyApi.getAll(),
    {
      keepPreviousData: true
    }
  );

  // Delete all stories mutation
  const { mutate: deleteAllStories, loading: deletingAll } = useApiMutation(
    () => storyApi.deleteAll(),
    {
      onSuccess: () => {
        refetch();
      },
      successMessage: 'All stories deleted successfully'
    }
  );

  const onSearch = (data: SearchForm) => {
    setSearchQuery(data.character);
  };

  const clearSearch = () => {
    setSearchQuery('');
    refetch();
  };

  const downloadStory = (story: Story) => {
    const content = `${story.primary_character} and ${story.secondary_character}\n\nGenerated with: ${story.framework}\nCreated: ${new Date(story.created_at).toLocaleString()}\n\n${story.story}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `story-${story.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const frameworks = {
    'semantic-kernel': { name: 'Semantic Kernel', color: 'bg-blue-500' },
    'langchain': { name: 'LangChain', color: 'bg-green-500' },
    'langgraph': { name: 'LangGraph', color: 'bg-purple-500' },
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Story History</h1>
            <p className="mt-2 text-gray-600">Browse and search through your generated stories</p>
          </div>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to delete ALL stories? This action cannot be undone.')) {
                deleteAllStories({});
              }
            }}
            disabled={deletingAll || !stories?.length}
            className="btn-secondary text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50"
            title="Clear all stories"
          >
            {deletingAll ? (
              <div className="w-4 h-4 spinner" />
            ) : (
              <>
                <Trash className="w-4 h-4 mr-2" />
                Clear All
              </>
            )}
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSubmit(onSearch)} className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  className="form-input pl-10"
                  placeholder="Search by character name..."
                  {...register('character')}
                />
              </div>
            </div>
            <button type="submit" className="btn-primary">
              Search
            </button>
            {searchQuery && (
              <button type="button" onClick={clearSearch} className="btn-secondary">
                Clear
              </button>
            )}
          </form>
          
          {searchQuery && (
            <p className="mt-2 text-sm text-gray-600">
              Showing results for: <strong>"{searchQuery}"</strong>
            </p>
          )}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="spinner w-8 h-8 mx-auto mb-4" />
          <p className="text-gray-500">Loading stories...</p>
        </div>
      )}

      {/* Stories Grid */}
      {!isLoading && stories && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stories.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              <Book className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No stories found</p>
              {searchQuery && (
                <button onClick={clearSearch} className="btn-primary mt-4">
                  View all stories
                </button>
              )}
            </div>
          ) : (
            stories.map((story) => (
              <div key={story.id} className="card">
                <div className="card-body">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-sm">
                        {story.primary_character} & {story.secondary_character}
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium text-white ${
                      frameworks[story.framework as keyof typeof frameworks]?.color || 'bg-gray-500'
                    }`}>
                      {frameworks[story.framework as keyof typeof frameworks]?.name || story.framework}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm line-clamp-3">
                      {story.story.length > 150 
                        ? `${story.story.substring(0, 150)}...` 
                        : story.story
                      }
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                    <div className="flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      {new Date(story.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex items-center">
                      <User className="w-3 h-3 mr-1" />
                      ID: {story.id.substring(0, 8)}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setSelectedStory(story)}
                      className="btn-primary btn-sm flex-1 flex items-center justify-center"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </button>
                    <button
                      onClick={() => downloadStory(story)}
                      className="btn-secondary btn-sm"
                      title="Download story"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Story Modal */}
      {selectedStory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {selectedStory.primary_character} & {selectedStory.secondary_character}
                </h2>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span className={`px-2 py-1 rounded text-xs font-medium text-white ${
                    frameworks[selectedStory.framework as keyof typeof frameworks]?.color || 'bg-gray-500'
                  }`}>
                    {frameworks[selectedStory.framework as keyof typeof frameworks]?.name || selectedStory.framework}
                  </span>
                  <span>{new Date(selectedStory.created_at).toLocaleString()}</span>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => downloadStory(selectedStory)}
                  className="btn-secondary"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </button>
                <button
                  onClick={() => setSelectedStory(null)}
                  className="btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              <div className="prose max-w-none">
                <div className="bg-gray-50 rounded-lg p-6 whitespace-pre-wrap">
                  {selectedStory.story}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryHistory;