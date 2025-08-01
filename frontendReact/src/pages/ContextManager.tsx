import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Upload, FileText, Play, Trash2, File, MessageCircle } from 'lucide-react';
import { contextApi } from '../services/api';
import { useApiMutation } from '../hooks/useApi';
import type { Framework } from '../types';
import { loadPrompt } from '../utils/promptLoader';


const ContextManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'files' | 'system' | 'user' | 'result'>('files');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [systemPrompt, setSystemPrompt] = useState<string>(loadPrompt('system'));
  const [userPrompt, setUserPrompt] = useState<string>(loadPrompt('user'));
  const [selectedFramework, setSelectedFramework] = useState<Framework>('semantic-kernel');
  const [executionResult, setExecutionResult] = useState<string | null>(null);
  
  
  // Fetch uploaded files
  const { data: files, refetch: refetchFiles } = useQuery(
    'contextFiles',
    contextApi.getFiles
  );
  
  // Note: Execution history was removed to simplify the interface

  // Upload files mutation
  const { mutate: uploadFiles, loading: uploading } = useApiMutation(
    (files: FileList) => contextApi.uploadFiles(files),
    {
      onSuccess: (result) => {
        refetchFiles();
        setSelectedFiles([]);
        // Auto-select the newly uploaded files
        if (result.results && Array.isArray(result.results)) {
          const newFileIds = result.results.map((upload: any) => upload.file_id);
          setSelectedFileIds(newFileIds);
        }
      },
      successMessage: 'Files uploaded successfully!'
    }
  );

  // Execute prompt mutation
  const { mutate: executePrompt, loading: executing } = useApiMutation(
    (data: { framework: Framework; prompt: string; file_ids: string[]; userPrompt?: string }) => contextApi.executePrompt(data),
    {
      onSuccess: (result) => {
        setExecutionResult(result.llm_response);
      },
      successMessage: 'Prompt executed successfully!'
    }
  );

  // Delete file mutation
  const { mutate: deleteFile } = useApiMutation(
    (id: string) => contextApi.deleteFile(id),
    {
      onSuccess: () => refetchFiles(),
      successMessage: 'File deleted successfully'
    }
  );

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFiles(Array.from(event.target.files));
    }
  };

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      const fileList = new DataTransfer();
      selectedFiles.forEach(file => fileList.items.add(file));
      uploadFiles(fileList.files);
    }
  };


  const frameworks = [
    { id: 'semantic-kernel' as Framework, name: 'Semantic Kernel' },
    { id: 'langchain' as Framework, name: 'LangChain' },
    { id: 'langgraph' as Framework, name: 'LangGraph' },
  ];

  const executePromptWithState = () => {
    if (userPrompt.trim() && selectedFileIds.length > 0) {
      executePrompt({
        framework: selectedFramework,
        prompt: systemPrompt,
        file_ids: selectedFileIds,
        userPrompt: userPrompt
      });
    }
  };

  const tabs = [
    { id: 'files' as const, name: 'File Selection', icon: FileText },
    { id: 'system' as const, name: 'System Prompt', icon: Upload },
    { id: 'user' as const, name: 'User Prompt', icon: MessageCircle },
    { id: 'result' as const, name: 'Result', icon: Play },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Context Manager</h1>
        <p className="mt-2 text-gray-600">Upload files and execute prompts with context</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {/* File Selection Tab */}
        {activeTab === 'files' && (
          <div className="space-y-6">
            {/* Upload Files */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900">Upload Context Files</h2>
              </div>
              <div className="card-body">
                <div className="mb-4">
                  <input
                    type="file"
                    multiple
                    accept=".txt,.md,.json,.xml,.csv"
                    onChange={handleFileSelect}
                    className="form-input"
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Supported formats: TXT, MD, JSON, XML, CSV
                  </p>
                </div>
                
                {selectedFiles.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Selected Files:</h4>
                    <ul className="space-y-1">
                      {selectedFiles.map((file, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-center">
                          <File className="w-4 h-4 mr-2" />
                          {file.name} ({(file.size / 1024).toFixed(1)} KB)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <button
                  onClick={handleUpload}
                  disabled={selectedFiles.length === 0 || uploading}
                  className="btn-primary w-full"
                >
                  {uploading ? (
                    <>
                      <div className="spinner w-4 h-4 mr-2" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Files
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Select Files for Context */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900">Select Files for Context</h2>
              </div>
              <div className="card-body">
                {files && files.length > 0 ? (
                  <div className="space-y-3">
                    {files.map((file) => (
                      <label key={file.id} className="flex items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                        <input
                          type="checkbox"
                          checked={selectedFileIds.includes(file.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedFileIds([...selectedFileIds, file.id]);
                            } else {
                              setSelectedFileIds(selectedFileIds.filter(id => id !== file.id));
                            }
                          }}
                          className="mr-3"
                        />
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-900">{file.name}</span>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                deleteFile(file.id);
                              }}
                              className="text-red-500 hover:text-red-700 ml-2"
                              title="Delete file"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {(file.size / 1024).toFixed(1)} KB • {new Date(file.upload_date).toLocaleDateString()}
                          </p>
                        </div>
                      </label>
                    ))}
                    
                    <div className="pt-4 border-t">
                      <p className="text-sm text-gray-600 mb-3">
                        Selected files: {selectedFileIds.length}
                      </p>
                      <button
                        onClick={() => setActiveTab('system')}
                        disabled={selectedFileIds.length === 0}
                        className="btn-primary"
                      >
                        Next: System Prompt
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">Upload files first to use as context</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* System Prompt Tab */}
        {activeTab === 'system' && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">System Prompt</h2>
              <p className="text-sm text-gray-600">Define the AI's role and behavior (optional)</p>
            </div>
            <div className="card-body space-y-6">
              <div>
                <label className="form-label">Framework</label>
                <select
                  value={selectedFramework}
                  onChange={(e) => setSelectedFramework(e.target.value as Framework)}
                  className="form-select"
                >
                  {frameworks.map((framework) => (
                    <option key={framework.id} value={framework.id}>
                      {framework.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label">System Instructions</label>
                <textarea
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  rows={6}
                  className="form-textarea"
                  placeholder="You are a helpful assistant that analyzes the provided context files and answers questions based on their content..."
                />
                <p className="mt-1 text-sm text-gray-500">
                  The system prompt helps define how the AI should behave and approach the task.
                </p>
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setActiveTab('files')}
                  className="btn-secondary"
                >
                  Previous: Files
                </button>
                <button
                  onClick={() => setActiveTab('user')}
                  className="btn-primary"
                >
                  Next: User Prompt
                </button>
              </div>
            </div>
          </div>
        )}

        {/* User Prompt Tab */}
        {activeTab === 'user' && (
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">User Prompt</h2>
              <p className="text-sm text-gray-600">Your question or request to the AI</p>
            </div>
            <div className="card-body space-y-6">
              <div>
                <label className="form-label">Your Question/Request</label>
                <textarea
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  rows={8}
                  className="form-textarea"
                  placeholder="What would you like to know about the uploaded files? Ask any question or request analysis..."
                  required
                />
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Context Summary:</h4>
                <p className="text-sm text-blue-700">
                  • Framework: <strong>{frameworks.find(f => f.id === selectedFramework)?.name}</strong>
                </p>
                <p className="text-sm text-blue-700">
                  • Files: <strong>{selectedFileIds.length} selected</strong>
                </p>
                <p className="text-sm text-blue-700">
                  • System prompt: <strong>{systemPrompt ? 'Yes' : 'None'}</strong>
                </p>
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setActiveTab('system')}
                  className="btn-secondary"
                >
                  Previous: System Prompt
                </button>
                <button
                  onClick={() => {
                    executePromptWithState();
                    setActiveTab('result');
                  }}
                  disabled={!userPrompt.trim() || executing}
                  className="btn-primary"
                >
                  {executing ? (
                    <>
                      <div className="spinner w-4 h-4 mr-2" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Execute Prompt
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Result Tab */}
        {activeTab === 'result' && (
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Execution Result</h2>
                  <button
                    onClick={() => {
                      setSystemPrompt('');
                      setUserPrompt('');
                      setExecutionResult(null);
                      setActiveTab('files');
                    }}
                    className="btn-secondary btn-sm"
                  >
                    New Session
                  </button>
                </div>
              </div>
              <div className="card-body">
                {executing ? (
                  <div className="text-center py-12">
                    <div className="spinner w-8 h-8 mx-auto mb-4" />
                    <p className="text-gray-500">Processing your request...</p>
                  </div>
                ) : executionResult ? (
                  <div className="space-y-4">
                    <div className="bg-gray-50 rounded-lg p-6">
                      <div className="whitespace-pre-wrap text-gray-800">
                        {executionResult}
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <button
                        onClick={() => setActiveTab('user')}
                        className="btn-secondary"
                      >
                        Edit Prompt
                      </button>
                      <button
                        onClick={() => navigator.clipboard.writeText(executionResult)}
                        className="btn-primary btn-sm"
                      >
                        Copy Result
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Play className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No result yet. Execute a prompt to see results here.</p>
                    <button
                      onClick={() => setActiveTab('user')}
                      className="btn-primary mt-4"
                    >
                      Go to User Prompt
                    </button>
                  </div>
                )}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default ContextManager;