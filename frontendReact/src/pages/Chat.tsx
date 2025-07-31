import React, { useState, useRef, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useForm } from 'react-hook-form';
import { Send, Trash2, Plus, MessageCircle, Trash } from 'lucide-react';
import { chatApi } from '../services/api';
import { useApiMutation } from '../hooks/useApi';
import { formatDate, formatTime } from '../utils/dateUtils';
import type { Framework, ChatRequest, ChatMessage } from '../types';

interface ChatForm {
  message: string;
}

const Chat: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState<Framework>('semantic-kernel');
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ChatForm>();
  
  // Fetch conversations
  const { data: conversations, refetch: refetchConversations } = useQuery(
    'conversations',
    chatApi.getConversations
  );
  
  // Fetch conversation messages when conversation is selected
  const { refetch: refetchMessages } = useQuery(
    ['conversation', selectedConversation],
    () => selectedConversation ? chatApi.getConversation(selectedConversation) : null,
    {
      enabled: !!selectedConversation,
      onSuccess: (data) => {
        if (data) {
          setMessages(data.messages);
        }
      }
    }
  );

  // Send message mutation
  const { mutate: sendMessage, loading: sendingMessage } = useApiMutation(
    (data: ChatRequest) => chatApi.sendMessage(selectedFramework, data),
    {
      onSuccess: (newMessage) => {
        setMessages(prev => [...prev, newMessage]);
        refetchConversations();
        if (selectedConversation) {
          refetchMessages();
        }
      }
    }
  );

  // Delete conversation mutation
  const { mutate: deleteConversation } = useApiMutation(
    (id: string) => chatApi.deleteConversation(id),
    {
      onSuccess: () => {
        refetchConversations();
        if (selectedConversation) {
          setSelectedConversation(null);
          setMessages([]);
        }
      },
      successMessage: 'Conversation deleted successfully'
    }
  );

  // Delete all conversations mutation
  const { mutate: deleteAllConversations, loading: deletingAll } = useApiMutation(
    () => chatApi.deleteAllConversations(),
    {
      onSuccess: () => {
        refetchConversations();
        setSelectedConversation(null);
        setMessages([]);
      },
      successMessage: 'All conversations deleted successfully'
    }
  );

  const onSubmit = (data: ChatForm) => {
    if (data.message.trim()) {
      // Add user message immediately for better UX
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: data.message,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      
      sendMessage({
        message: data.message,
        conversation_id: selectedConversation || undefined
      });
      
      reset();
    }
  };

  const startNewConversation = () => {
    setSelectedConversation(null);
    setMessages([]);
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const frameworks = [
    { id: 'semantic-kernel' as Framework, name: 'Semantic Kernel', color: 'bg-blue-500' },
    { id: 'langchain' as Framework, name: 'LangChain', color: 'bg-green-500' },
    { id: 'langgraph' as Framework, name: 'LangGraph', color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">AI Chat Interface</h1>
        <p className="mt-2 text-gray-600">Have conversations with different AI frameworks</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[600px]">
        {/* Conversations Sidebar */}
        <div className="lg:col-span-1">
          <div className="card h-full flex flex-col">
            <div className="card-header flex-shrink-0">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={startNewConversation}
                    className="btn-primary btn-sm"
                    title="New conversation"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Are you sure you want to delete all conversations? This action cannot be undone.')) {
                        deleteAllConversations({});
                      }
                    }}
                    disabled={deletingAll || !conversations?.length}
                    className="btn-secondary btn-sm text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50"
                    title="Clear all conversations"
                  >
                    {deletingAll ? (
                      <div className="w-4 h-4 spinner" />
                    ) : (
                      <Trash className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto">
              {conversations && conversations.length > 0 ? (
                <div className="space-y-2 p-4">
                  {conversations.map((conversation) => (
                    <div
                      key={conversation.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedConversation === conversation.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedConversation(conversation.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {conversation.title || 'Untitled Conversation'}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {formatDate(conversation.created_at)}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteConversation(conversation.id);
                          }}
                          className="text-gray-400 hover:text-red-500 ml-2"
                          title="Delete conversation"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No conversations yet</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <div className="card h-full flex flex-col">
            <div className="card-header flex-shrink-0">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Chat</h2>
                
                {/* Framework Selection */}
                <div className="flex space-x-2">
                  {frameworks.map((framework) => (
                    <button
                      key={framework.id}
                      onClick={() => setSelectedFramework(framework.id)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        selectedFramework === framework.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {framework.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="flex-1 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>Start a conversation or select an existing one</p>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message, index) => (
                    <div
                      key={message.id || index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[75%] p-3 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
                        }`}>
                          {formatTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {sendingMessage && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 text-gray-900 p-3 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <div className="spinner w-4 h-4" />
                          <span>Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Message Input */}
            <div className="border-t border-gray-200 p-4 flex-shrink-0">
              <form onSubmit={handleSubmit(onSubmit)} className="flex space-x-2">
                <div className="flex-1">
                  <input
                    type="text"
                    className={`form-input ${errors.message ? 'border-red-500' : ''}`}
                    placeholder="Type your message..."
                    {...register('message', { required: 'Message is required' })}
                  />
                </div>
                <button
                  type="submit"
                  disabled={sendingMessage}
                  className="btn-primary flex items-center"
                >
                  {sendingMessage ? (
                    <div className="spinner w-4 h-4" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;