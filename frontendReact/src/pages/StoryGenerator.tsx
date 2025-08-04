import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Wand2, Copy, Download } from 'lucide-react';
import { storyApi } from '../services/api';
import { useApiMutation } from '../hooks/useApi';
import { useComponentLogger } from '../hooks/useComponentLogger';
import type { Framework, StoryGenerationRequest, Story } from '../types';

interface StoryForm {
  primary_character: string;
  secondary_character: string;
}

const StoryGenerator: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState<Framework>('semantic-kernel');
  const [generatedStory, setGeneratedStory] = useState<Story | null>(null);
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm<StoryForm>();
  const logger = useComponentLogger('StoryGenerator');
  
  const { mutate: generateStory, loading } = useApiMutation(
    (data: StoryGenerationRequest) => storyApi.generate(selectedFramework, data),
    {
      onSuccess: (story) => {
        logger.info('Story generated successfully', { 
          framework: selectedFramework,
          storyLength: story.story.length,
          storyId: story.id 
        });
        setGeneratedStory(story);
        reset();
      },
      successMessage: 'Story generated successfully!',
    }
  );

  const onSubmit = (data: StoryForm) => {
    const startTime = Date.now();
    logger.logUserAction('Generate Story', { 
      framework: selectedFramework,
      characters: data 
    });
    
    generateStory(data);
    
    // Log performance when done
    setTimeout(() => {
      logger.logPerformance('Story Generation', startTime);
    }, 100);
  };

  const copyToClipboard = async () => {
    if (generatedStory) {
      await navigator.clipboard.writeText(generatedStory.story);
      logger.logUserAction('Copy Story', { storyId: generatedStory.id });
    }
  };

  const downloadStory = () => {
    if (generatedStory) {
      const content = `${generatedStory.primary_character} and ${generatedStory.secondary_character}\n\n${generatedStory.story}`;
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `story-${generatedStory.id}.txt`;
      a.click();
      URL.revokeObjectURL(url);
      
      logger.logUserAction('Download Story', { 
        storyId: generatedStory.id,
        fileName: `story-${generatedStory.id}.txt` 
      });
    }
  };

  const frameworks = [
    { id: 'semantic-kernel' as Framework, name: 'Semantic Kernel', color: 'bg-blue-500' },
    { id: 'langchain' as Framework, name: 'LangChain', color: 'bg-green-500' },
    { id: 'langgraph' as Framework, name: 'LangGraph', color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">AI Story Generator</h1>
        <p className="mt-2 text-gray-600">Create amazing stories with different AI frameworks</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-gray-900">Story Parameters</h2>
          </div>
          <div className="card-body">
            {/* Framework Selection */}
            <div className="mb-6">
              <label className="form-label">Select Framework:</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2">
                {frameworks.map((framework) => (
                  <button
                    key={framework.id}
                    type="button"
                    onClick={() => setSelectedFramework(framework.id)}
                    className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                      selectedFramework === framework.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className={`w-3 h-3 rounded-full ${framework.color} mx-auto mb-2`} />
                    <span className="text-sm font-medium">{framework.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="form-label">Primary Character</label>
                <input
                  type="text"
                  className={`form-input ${errors.primary_character ? 'border-red-500' : ''}`}
                  placeholder="e.g., Alice"
                  {...register('primary_character', { required: 'Primary character is required' })}
                />
                {errors.primary_character && (
                  <p className="mt-1 text-sm text-red-600">{errors.primary_character.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Secondary Character</label>
                <input
                  type="text"
                  className={`form-input ${errors.secondary_character ? 'border-red-500' : ''}`}
                  placeholder="e.g., Bob"
                  {...register('secondary_character', { required: 'Secondary character is required' })}
                />
                {errors.secondary_character && (
                  <p className="mt-1 text-sm text-red-600">{errors.secondary_character.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="spinner w-4 h-4 mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 mr-2" />
                    Generate Story
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Generated Story */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Generated Story</h2>
              {generatedStory && (
                <div className="flex space-x-2">
                  <button
                    onClick={copyToClipboard}
                    className="btn-secondary btn-sm"
                    title="Copy to clipboard"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={downloadStory}
                    className="btn-secondary btn-sm"
                    title="Download story"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="card-body">
            {loading && (
              <div className="text-center py-12">
                <div className="spinner w-8 h-8 mx-auto mb-4" />
                <p className="text-gray-500">Generating your story...</p>
              </div>
            )}

            {!loading && !generatedStory && (
              <div className="text-center py-12 text-gray-500">
                <Wand2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Your story will appear here...</p>
              </div>
            )}

            {generatedStory && (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>
                    {generatedStory.primary_character} & {generatedStory.secondary_character}
                  </span>
                  <div className="flex items-center space-x-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      frameworks.find(f => f.id === generatedStory.framework)?.color || 'bg-gray-500'
                    } text-white`}>
                      {frameworks.find(f => f.id === generatedStory.framework)?.name}
                    </span>
                    <span>{new Date(generatedStory.created_at).toLocaleString()}</span>
                  </div>
                </div>

                {/* Story Metadata */}
                <div className="bg-blue-50 rounded-lg p-3 text-xs text-gray-600 space-y-1">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-medium">Story ID:</span> {generatedStory.id}
                    </div>
                    {generatedStory.transaction_guid && (
                      <div>
                        <span className="font-medium">Transaction ID:</span> {generatedStory.transaction_guid}
                      </div>
                    )}
                    {generatedStory.total_tokens && (
                      <div>
                        <span className="font-medium">Tokens:</span> {generatedStory.total_tokens.toLocaleString()}
                      </div>
                    )}
                    {generatedStory.generation_time_ms && (
                      <div>
                        <span className="font-medium">Generation Time:</span> {Math.round(generatedStory.generation_time_ms)}ms
                      </div>
                    )}
                    {generatedStory.estimated_cost_usd && (
                      <div>
                        <span className="font-medium">Est. Cost:</span> ${generatedStory.estimated_cost_usd.toFixed(6)}
                      </div>
                    )}
                    {generatedStory.request_id && (
                      <div>
                        <span className="font-medium">Request ID:</span> {generatedStory.request_id}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="prose max-w-none">
                  <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap">
                    {generatedStory.story}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryGenerator;