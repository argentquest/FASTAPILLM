// AI Story Generator - Enhanced JavaScript with Bootstrap Integration

class StoryGenerator {
    constructor() {
        this.currentStory = '';
        this.currentProvider = null;
        this.stories = [];
        this.currentConversation = null;
        this.conversations = [];
        this.selectedFramework = 'semantic-kernel';
        this.selectedFrameworkName = 'Semantic Kernel';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadProviderInfo();
        this.setupNavigation();
    }

    setupEventListeners() {
        // Form submission
        document.getElementById('storyForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateStory();
        });

        // Character input validation
        const primaryChar = document.getElementById('primaryCharacter');
        const secondaryChar = document.getElementById('secondaryCharacter');
        
        [primaryChar, secondaryChar].forEach(input => {
            input.addEventListener('input', () => this.validateInput(input));
            input.addEventListener('blur', () => this.validateCharacters());
        });

        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendChatMessage();
        });

        // Chat input character count
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('input', () => {
            const charCount = chatInput.value.length;
            document.getElementById('charCount').textContent = charCount;
            
            // Enable/disable send button
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = charCount === 0;
        });

        // Enable chat input when typing begins
        chatInput.addEventListener('focus', () => {
            if (!this.currentConversation) {
                chatInput.disabled = false;
                document.getElementById('sendBtn').disabled = false;
            }
        });
    }

    setupNavigation() {
        // Page navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showPage(e.target.dataset.page);
                this.updateNavigation(e.target);
            });
        });
    }

    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
        });

        // Show selected page
        const targetPage = document.getElementById(pageId + 'Page');
        if (targetPage) {
            targetPage.style.display = 'block';
            
            // Load data for specific pages
            if (pageId === 'history') {
                this.loadStories();
            } else if (pageId === 'chat') {
                this.loadConversations();
                this.enableChatInput();
            }
        }
    }

    updateNavigation(activeLink) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        activeLink.classList.add('active');
    }

    validateInput(input) {
        const value = input.value.trim();
        const maxLength = parseInt(input.getAttribute('maxlength'));
        
        // Remove any existing validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        if (value.length === 0) {
            input.classList.add('is-invalid');
        } else if (value.length > maxLength) {
            input.classList.add('is-invalid');
        } else {
            input.classList.add('is-valid');
        }
    }

    validateCharacters() {
        const primary = document.getElementById('primaryCharacter').value.trim().toLowerCase();
        const secondary = document.getElementById('secondaryCharacter').value.trim().toLowerCase();
        
        if (primary && secondary && primary === secondary) {
            this.showAlert('Characters must be different!', 'warning');
            document.getElementById('secondaryCharacter').classList.add('is-invalid');
        }
    }

    async generateStory() {
        const primaryCharacter = document.getElementById('primaryCharacter').value.trim();
        const secondaryCharacter = document.getElementById('secondaryCharacter').value.trim();
        const method = document.getElementById('method').value;
        
        if (!primaryCharacter || !secondaryCharacter) {
            this.showAlert('Please enter both characters', 'danger');
            return;
        }

        if (primaryCharacter.toLowerCase() === secondaryCharacter.toLowerCase()) {
            this.showAlert('Characters must be different!', 'warning');
            return;
        }

        const generateBtn = document.getElementById('generateBtn');
        const originalText = generateBtn.innerHTML;
        
        // Show loading state
        generateBtn.classList.add('btn-loading');
        generateBtn.disabled = true;
        generateBtn.innerHTML = 'Generating...';
        
        // Hide previous results
        document.getElementById('storyResult').style.display = 'none';
        this.clearAlerts();

        try {
            const startTime = Date.now();
            
            const response = await fetch(`/api/${method}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    primary_character: primaryCharacter,
                    secondary_character: secondaryCharacter
                })
            });

            const endTime = Date.now();
            const responseTime = endTime - startTime;

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(this.formatErrorMessage(errorData, response.status));
            }

            const data = await response.json();
            this.currentStory = data.story;
            
            this.displayStory(data, responseTime);
            this.showAlert('Story generated successfully!', 'success');
            
        } catch (error) {
            console.error('Error generating story:', error);
            this.showAlert(`Error generating story: ${error.message}`, 'danger');
        } finally {
            // Restore button state
            generateBtn.classList.remove('btn-loading');
            generateBtn.disabled = false;
            generateBtn.innerHTML = originalText;
        }
    }

    formatErrorMessage(errorData, status) {
        if (status === 422 && errorData.error && errorData.error.details) {
            const details = errorData.error.details.map(detail => 
                `${detail.field}: ${detail.message}`
            ).join(', ');
            return `Validation error: ${details}`;
        }
        
        return errorData.error?.message || errorData.detail || 'Unknown error occurred';
    }

    displayStory(data, responseTime) {
        document.getElementById('storyContent').textContent = data.story;
        document.getElementById('storyMethod').textContent = data.method;
        document.getElementById('storyProvider').textContent = this.currentProvider?.provider || 'Unknown';
        document.getElementById('storyTime').textContent = `${data.generation_time_ms || responseTime}ms`;
        
        // Display token information
        const tokenInfo = document.getElementById('storyTokens');
        if (tokenInfo && data.total_tokens) {
            tokenInfo.textContent = `${data.input_tokens}/${data.output_tokens} tokens (${data.total_tokens} total)`;
            tokenInfo.style.display = 'inline';
        }
        
        document.getElementById('storyResult').style.display = 'block';
        document.getElementById('storyResult').scrollIntoView({ behavior: 'smooth' });
    }

    async loadProviderInfo() {
        try {
            const response = await fetch('/api/provider');
            if (response.ok) {
                this.currentProvider = await response.json();
                this.updateProviderDisplay();
            }
        } catch (error) {
            console.error('Error loading provider info:', error);
        }
    }

    updateProviderDisplay() {
        const providerElement = document.getElementById('currentProvider');
        if (this.currentProvider && providerElement) {
            providerElement.textContent = this.currentProvider.provider;
        }

        // Update provider modal
        const providerInfo = document.getElementById('providerInfo');
        if (this.currentProvider && providerInfo) {
            providerInfo.innerHTML = this.formatProviderInfo(this.currentProvider);
        }
    }

    formatProviderInfo(provider) {
        let html = `
            <div class="mb-3">
                <strong>Provider:</strong> 
                <span class="badge bg-primary">${provider.provider}</span>
            </div>
        `;

        if (provider.model) {
            html += `
                <div class="mb-3">
                    <strong>Model:</strong> 
                    <span class="badge bg-secondary">${provider.model}</span>
                </div>
            `;
        }

        if (provider.endpoint) {
            html += `
                <div class="mb-3">
                    <strong>Endpoint:</strong> 
                    <code>${provider.endpoint}</code>
                </div>
            `;
        }

        if (provider.available_models) {
            html += `
                <div class="mb-3">
                    <strong>Available Models:</strong>
                    <ul class="list-unstyled mt-2">
                        ${provider.available_models.map(model => 
                            `<li><span class="badge bg-light text-dark">${model}</span></li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }

        return html;
    }

    async loadStories() {
        const loadingElement = document.getElementById('historyLoading');
        const gridElement = document.getElementById('storiesGrid');
        
        loadingElement.style.display = 'block';
        gridElement.innerHTML = '';

        try {
            const response = await fetch('/api/stories');
            if (response.ok) {
                this.stories = await response.json();
                this.displayStories(this.stories);
            } else {
                throw new Error('Failed to load stories');
            }
        } catch (error) {
            console.error('Error loading stories:', error);
            gridElement.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Error loading stories: ${error.message}
                    </div>
                </div>
            `;
        } finally {
            loadingElement.style.display = 'none';
        }
    }

    displayStories(stories) {
        const gridElement = document.getElementById('storiesGrid');
        
        if (stories.length === 0) {
            gridElement.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-book"></i>
                        <h4 class="mt-3">No stories yet</h4>
                        <p>Generate your first story to see it here!</p>
                    </div>
                </div>
            `;
            return;
        }

        gridElement.innerHTML = stories.map(story => `
            <div class="col-md-6 col-lg-4">
                <div class="card story-card shadow-sm h-100" onclick="storyGenerator.viewStory(${story.id})">
                    <div class="card-body">
                        <h6 class="card-title text-primary">
                            <i class="bi bi-people me-2"></i>
                            ${story.combined_characters}
                        </h6>
                        <div class="story-preview mb-3">
                            <p class="card-text text-muted small">
                                ${story.story_preview}
                            </p>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-primary me-1">${story.method}</span>
                                <span class="badge bg-secondary">${story.provider}</span>
                                ${story.total_tokens ? `<span class="badge bg-warning text-dark ms-1">${story.total_tokens}t</span>` : ''}
                            </div>
                            <small class="text-muted">
                                ${story.generation_time_ms ? story.generation_time_ms + 'ms' : ''}
                            </small>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="bi bi-clock me-1"></i>
                                ${new Date(story.created_at).toLocaleDateString()}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async viewStory(storyId) {
        try {
            const response = await fetch(`/api/stories/${storyId}`);
            if (response.ok) {
                const story = await response.json();
                this.showStoryModal(story);
            } else {
                throw new Error('Failed to load story');
            }
        } catch (error) {
            console.error('Error loading story:', error);
            this.showAlert('Error loading story details', 'danger');
        }
    }

    showStoryModal(story) {
        const modalContent = document.getElementById('modalStoryContent');
        modalContent.innerHTML = `
            <div class="mb-3">
                <h6 class="text-primary">
                    <i class="bi bi-people me-2"></i>
                    ${story.combined_characters}
                </h6>
                <div class="d-flex gap-2 mb-3">
                    <span class="badge bg-primary">${story.method}</span>
                    <span class="badge bg-secondary">${story.provider} - ${story.model}</span>
                    <span class="badge bg-info">${story.generation_time_ms}ms</span>
                    ${story.total_tokens ? `<span class="badge bg-warning text-dark">${story.input_tokens}/${story.output_tokens} tokens (${story.total_tokens} total)</span>` : ''}
                </div>
            </div>
            <div class="story-content">
                ${story.story_content}
            </div>
            <div class="mt-3 text-muted small">
                <i class="bi bi-clock me-1"></i>
                Generated on ${new Date(story.created_at).toLocaleString()}
            </div>
        `;
        
        // Store current modal story for copying
        this.currentModalStory = story.story_content;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('storyModal'));
        modal.show();
    }

    async searchStoriesByCharacter() {
        const searchTerm = document.getElementById('searchCharacter').value.trim();
        if (!searchTerm) {
            this.loadStories();
            return;
        }

        const loadingElement = document.getElementById('historyLoading');
        const gridElement = document.getElementById('storiesGrid');
        
        loadingElement.style.display = 'block';

        try {
            const response = await fetch(`/api/stories/search/characters?character=${encodeURIComponent(searchTerm)}`);
            if (response.ok) {
                const stories = await response.json();
                this.displayStories(stories);
            } else {
                throw new Error('Search failed');
            }
        } catch (error) {
            console.error('Error searching stories:', error);
            this.showAlert('Error searching stories', 'danger');
        } finally {
            loadingElement.style.display = 'none';
        }
    }

    searchStories(event) {
        if (event.key === 'Enter') {
            this.searchStoriesByCharacter();
        }
    }

    copyStory() {
        if (!this.currentStory) return;
        
        navigator.clipboard.writeText(this.currentStory).then(() => {
            const copyBtn = event.target;
            copyBtn.classList.add('copy-success');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
            
            setTimeout(() => {
                copyBtn.classList.remove('copy-success');
                copyBtn.innerHTML = originalText;
            }, 2000);
        }).catch(() => {
            this.showAlert('Failed to copy story', 'warning');
        });
    }

    copyModalStory() {
        if (!this.currentModalStory) return;
        
        navigator.clipboard.writeText(this.currentModalStory).then(() => {
            this.showAlert('Story copied to clipboard!', 'success');
        }).catch(() => {
            this.showAlert('Failed to copy story', 'warning');
        });
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="bi bi-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    clearAlerts() {
        const alertContainer = document.getElementById('alertContainer');
        alertContainer.innerHTML = '';
    }

    // Chat functionality
    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            if (response.ok) {
                this.conversations = await response.json();
                this.displayConversations();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    displayConversations() {
        const container = document.getElementById('conversationsList');
        
        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div class="p-3 text-center text-muted">
                    <i class="bi bi-chat-square-dots"></i>
                    <p class="mb-0 mt-2 small">No conversations yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.conversations.map(conv => `
            <div class="conversation-item p-3 border-bottom ${this.currentConversation?.id === conv.id ? 'bg-primary bg-opacity-10' : ''}" 
                 onclick="storyGenerator.selectConversation(${conv.id})" 
                 style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1 text-truncate">${conv.title}</h6>
                        <div class="d-flex gap-1 mb-1">
                            <span class="badge bg-primary badge-sm">${conv.method}</span>
                            <span class="badge bg-secondary badge-sm">${conv.message_count} msgs</span>
                        </div>
                        ${conv.last_message_preview ? `<p class="mb-1 small text-muted">${conv.last_message_preview}</p>` : ''}
                        <small class="text-muted">${new Date(conv.updated_at).toLocaleDateString()}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="event.stopPropagation(); storyGenerator.deleteConversation(${conv.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async selectConversation(conversationId) {
        try {
            const response = await fetch(`/api/chat/conversations/${conversationId}`);
            if (response.ok) {
                this.currentConversation = await response.json();
                this.displayConversation();
                this.displayConversations(); // Refresh to show selection
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
            this.showAlert('Error loading conversation', 'danger');
        }
    }

    displayConversation() {
        if (!this.currentConversation) return;

        // Update header
        document.getElementById('chatTitle').textContent = this.currentConversation.title;
        document.getElementById('chatMethod').textContent = `Using ${this.currentConversation.method} • ${this.currentConversation.provider}`;

        // Update framework selector
        this.selectedFramework = this.currentConversation.method;
        this.selectedFrameworkName = this.getFrameworkDisplayName(this.currentConversation.method);
        document.getElementById('frameworkSelector').textContent = this.selectedFrameworkName;

        // Display messages
        const messagesContainer = document.getElementById('chatMessages');
        const chatPlaceholder = document.getElementById('chatPlaceholder');
        if (chatPlaceholder) chatPlaceholder.style.display = 'none';
        
        messagesContainer.innerHTML = this.currentConversation.messages.map(msg => {
            const isUser = msg.role === 'user';
            return `
                <div class="mb-3 d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'}">
                    <div class="message-bubble ${isUser ? 'user-message' : 'ai-message'} p-3 rounded-3 shadow-sm" style="max-width: 70%;">
                        <div class="message-content">${msg.content}</div>
                        <div class="message-meta text-muted small mt-1">
                            ${new Date(msg.created_at).toLocaleTimeString()}
                            ${msg.generation_time_ms ? ` • ${msg.generation_time_ms}ms` : ''}
                            ${msg.total_tokens ? ` • ${msg.input_tokens}/${msg.output_tokens} tokens (${msg.total_tokens} total)` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Enable input
        this.enableChatInput();
    }

    startNewChat() {
        this.currentConversation = null;
        const chatTitle = document.getElementById('chatTitle');
        const chatMethod = document.getElementById('chatMethod');
        const chatMessages = document.getElementById('chatMessages');
        const chatPlaceholder = document.getElementById('chatPlaceholder');
        
        if (chatTitle) chatTitle.textContent = 'New Conversation';
        if (chatMethod) chatMethod.textContent = `Using ${this.selectedFrameworkName}`;
        if (chatMessages) chatMessages.innerHTML = '';
        if (chatPlaceholder) chatPlaceholder.style.display = 'flex';
        
        this.enableChatInput();
        this.displayConversations(); // Refresh to remove selection
    }

    selectFramework(framework, displayName) {
        this.selectedFramework = framework;
        this.selectedFrameworkName = displayName;
        document.getElementById('frameworkSelector').textContent = displayName;
        
        if (!this.currentConversation) {
            document.getElementById('chatMethod').textContent = `Using ${displayName}`;
        }
    }

    getFrameworkDisplayName(framework) {
        const names = {
            'semantic-kernel': 'Semantic Kernel',
            'langchain': 'LangChain',
            'langgraph': 'LangGraph'
        };
        return names[framework] || framework;
    }

    enableChatInput() {
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.focus();
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (!input || !sendBtn) {
            console.error('Required chat elements not found');
            return;
        }
        
        const message = input.value.trim();
        if (!message) return;

        const originalBtnText = sendBtn.innerHTML;
        
        // Show loading state
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        input.disabled = true;

        try {
            // Add user message to UI immediately
            this.addMessageToUI(message, 'user');
            input.value = '';
            const charCount = document.getElementById('charCount');
            if (charCount) charCount.textContent = '0';

            // Send message to API
            const response = await fetch(`/api/chat/${this.selectedFramework}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversation?.id
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || 'Failed to send message');
            }

            const data = await response.json();
            
            // Update current conversation
            this.currentConversation = data.conversation;
            
            // Add AI response to UI
            const tokenInfo = {
                input_tokens: data.message.input_tokens,
                output_tokens: data.message.output_tokens,
                total_tokens: data.message.total_tokens
            };
            this.addMessageToUI(data.message.content, 'assistant', data.message.generation_time_ms, tokenInfo);
            
            // Update conversation title if this was a new conversation
            if (this.currentConversation.messages.length === 2) {
                document.getElementById('chatTitle').textContent = this.currentConversation.title;
                this.loadConversations(); // Refresh sidebar
            }

            // Hide placeholder
            const chatPlaceholder = document.getElementById('chatPlaceholder');
            if (chatPlaceholder) chatPlaceholder.style.display = 'none';

        } catch (error) {
            console.error('Error sending message:', error);
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            // Restore button state
            sendBtn.disabled = false;
            sendBtn.innerHTML = originalBtnText;
            input.disabled = false;
            input.focus();
        }
    }

    addMessageToUI(content, role, generationTime = null, tokenInfo = null) {
        const messagesContainer = document.getElementById('chatMessages');
        const isUser = role === 'user';
        
        // Check if content is JSON and format accordingly
        let displayContent = content;
        if (!isUser && this.isJson(content)) {
            displayContent = this.displayJsonResponse(content);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'}`;
        messageDiv.innerHTML = `
            <div class="message-bubble ${isUser ? 'user-message' : 'ai-message'} p-3 rounded-3 shadow-sm" style="max-width: 70%;">
                <div class="message-content">${displayContent}</div>
                <div class="message-meta text-muted small mt-1">
                    ${new Date().toLocaleTimeString()}
                    ${generationTime ? ` • ${generationTime}ms` : ''}
                    ${tokenInfo ? ` • ${tokenInfo.input_tokens}/${tokenInfo.output_tokens} tokens (${tokenInfo.total_tokens} total)` : ''}
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    isJson(str) {
        try {
            const parsed = JSON.parse(str);
            return typeof parsed === 'object' && parsed !== null;
        } catch (e) {
            return false;
        }
    }

    displayJsonResponse(content) {
        try {
            const jsonData = JSON.parse(content);
            const escapedContent = content.replace(/'/g, "\\'").replace(/"/g, '\\"');
            return `
                <div class="json-response">
                    <div class="json-header">
                        <i class="bi bi-code-square"></i> JSON Response
                        <button class="btn btn-sm btn-outline-primary ms-2" onclick="storyGenerator.copyJson('${escapedContent}')">
                            <i class="bi bi-clipboard"></i> Copy
                        </button>
                    </div>
                    <pre class="json-content">${JSON.stringify(jsonData, null, 2)}</pre>
                </div>
            `;
        } catch (e) {
            return content; // Return as regular text if not valid JSON
        }
    }

    copyJson(jsonString) {
        // Unescape the string
        const unescaped = jsonString.replace(/\\'/g, "'").replace(/\\"/g, '"');
        navigator.clipboard.writeText(unescaped).then(() => {
            this.showAlert('JSON copied to clipboard!', 'success');
        }).catch(() => {
            this.showAlert('Failed to copy JSON', 'warning');
        });
    }

    async deleteConversation(conversationId) {
        if (!confirm('Are you sure you want to delete this conversation?')) {
            return;
        }

        try {
            const response = await fetch(`/api/chat/conversations/${conversationId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // If this was the current conversation, clear it
                if (this.currentConversation?.id === conversationId) {
                    this.startNewChat();
                }
                
                // Refresh conversations list
                this.loadConversations();
                this.showAlert('Conversation deleted', 'success');
            } else {
                throw new Error('Failed to delete conversation');
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            this.showAlert('Error deleting conversation', 'danger');
        }
    }
}

// Initialize the application
const storyGenerator = new StoryGenerator();

// Global functions for onclick handlers
function searchStories(event) {
    storyGenerator.searchStories(event);
}

function searchStoriesByCharacter() {
    storyGenerator.searchStoriesByCharacter();
}

function loadStories() {
    storyGenerator.loadStories();
}

function copyStory() {
    storyGenerator.copyStory();
}

function copyModalStory() {
    storyGenerator.copyModalStory();
}