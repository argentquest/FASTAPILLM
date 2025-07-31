import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { DollarSign, TrendingUp, Activity, Calendar, Trash } from 'lucide-react';
import { costApi } from '../services/api';
import { useApiMutation } from '../hooks/useApi';

const CostTracking: React.FC = () => {
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [viewMode, setViewMode] = useState<'summary' | 'transactions'>('transactions');

  const { data: costData, isLoading, refetch } = useQuery(
    ['costUsage', startDate, endDate],
    () => costApi.getUsage(startDate, endDate),
    {
      keepPreviousData: true
    }
  );

  // Calculate days for transactions query
  const daysDiff = Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
  
  const { data: transactionData, isLoading: isLoadingTransactions } = useQuery(
    ['costTransactions', daysDiff],
    () => costApi.getTransactions(daysDiff),
    {
      keepPreviousData: true,
      enabled: viewMode === 'transactions'
    }
  );

  // Clear all cost data mutation
  const { mutate: clearAllCostData, loading: clearingAll } = useApiMutation(
    () => costApi.clearAll(),
    {
      onSuccess: () => {
        refetch();
      },
      successMessage: 'All cost data cleared successfully'
    }
  );

  const handleDateFilter = () => {
    refetch();
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Cost Tracking</h1>
            <p className="mt-2 text-gray-600">Monitor your AI usage and estimated costs</p>
          </div>
          <button
            onClick={() => {
              if (confirm('Are you sure you want to clear ALL cost data? This will delete all stories, chats, and context executions. This action cannot be undone.')) {
                clearAllCostData({});
              }
            }}
            disabled={clearingAll || !costData?.usage_data?.length}
            className="btn-secondary text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50"
            title="Clear all cost data"
          >
            {clearingAll ? (
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

      {/* Date Filter */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <label className="form-label">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="form-input"
              />
            </div>
            <div>
              <label className="form-label">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="form-input"
              />
            </div>
            <div className="md:col-span-2">
              <button onClick={handleDateFilter} className="btn-primary w-full">
                <Calendar className="w-4 h-4 mr-2" />
                Apply Filter
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="flex justify-center space-x-4 mb-6">
        <button
          onClick={() => setViewMode('summary')}
          className={`px-4 py-2 rounded-lg font-medium ${
            viewMode === 'summary'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Summary View
        </button>
        <button
          onClick={() => setViewMode('transactions')}
          className={`px-4 py-2 rounded-lg font-medium ${
            viewMode === 'transactions'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Transaction Details
        </button>
      </div>

      {/* Loading State */}
      {(isLoading || (viewMode === 'transactions' && isLoadingTransactions)) && (
        <div className="text-center py-12">
          <div className="spinner w-8 h-8 mx-auto mb-4" />
          <p className="text-gray-500">Loading cost data...</p>
        </div>
      )}

      {/* Summary Cards */}
      {costData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <div className="card-body text-center">
                <Activity className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                <h3 className="text-2xl font-bold text-gray-900">
                  {costData.summary.total_requests}
                </h3>
                <p className="text-gray-600">Total Requests</p>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                <h3 className="text-2xl font-bold text-gray-900">
                  {costData.summary.total_tokens.toLocaleString()}
                </h3>
                <p className="text-gray-600">Total Tokens</p>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <DollarSign className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                <h3 className="text-2xl font-bold text-gray-900">
                  ${costData.summary.estimated_cost.toFixed(6)}
                </h3>
                <p className="text-gray-600">Estimated Cost</p>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <DollarSign className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                <h3 className="text-2xl font-bold text-gray-900">
                  ${costData.summary.avg_cost_per_request.toFixed(6)}
                </h3>
                <p className="text-gray-600">Avg Cost/Request</p>
              </div>
            </div>
          </div>

          {/* Conditional Table Rendering based on View Mode */}
          {viewMode === 'summary' ? (
            // Summary Table (original)
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900">Daily Usage Summary</h2>
              </div>
              <div className="card-body p-0">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Framework
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Model
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Requests
                        </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tokens
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Est. Cost
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {costData.usage_data.map((entry, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(entry.date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                            {entry.framework}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.model}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.request_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.total_tokens.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${entry.estimated_cost.toFixed(6)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          ) : (
            // Transaction Details Table
            <div className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900">Transaction Details</h2>
              </div>
              <div className="card-body p-0">
                {transactionData && transactionData.transactions && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date/Time
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Method
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Model
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Description
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Tokens
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Cost
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {transactionData.transactions.map((transaction: any) => (
                          <tr key={`${transaction.type}-${transaction.id}`}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(transaction.created_at).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-medium rounded ${
                                transaction.type === 'story' ? 'bg-purple-100 text-purple-800' :
                                transaction.type === 'chat' ? 'bg-blue-100 text-blue-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {transaction.type}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {transaction.method}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {transaction.model}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                              {transaction.type === 'story' && transaction.primary_character && transaction.secondary_character
                                ? `${transaction.primary_character} & ${transaction.secondary_character}`
                                : transaction.conversation_title || transaction.content_preview || '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {transaction.total_tokens?.toLocaleString() || '0'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              ${transaction.estimated_cost_usd?.toFixed(6) || '0.000000'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!isLoading && costData && costData.usage_data.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <DollarSign className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No usage data found for the selected period</p>
        </div>
      )}
    </div>
  );
};

export default CostTracking;