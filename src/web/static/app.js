// 数学小助手 JavaScript

class MathTutorChat {
    constructor() {
        this.ws = null;
        this.studentId = null;
        this.studentName = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.isConnected = false;
        this.messageHistory = [];

        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        // 聊天相关
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator');

        // 状态相关
        this.studentNameDisplay = document.getElementById('student-name');
        this.studentLevelDisplay = document.getElementById('student-level');
        this.studentXpDisplay = document.getElementById('student-xp');
        this.connectionStatus = document.getElementById('connection-status');
        this.statusDot = this.connectionStatus.querySelector('.status-dot');
        this.statusText = this.connectionStatus.querySelector('.status-text');

        // 弹窗相关
        this.nameModal = document.getElementById('name-modal');
        this.studentNameInput = document.getElementById('student-name-input');
        this.startButton = document.getElementById('start-button');
    }

    initEventListeners() {
        // 发送按钮
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // 输入框回车发送
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 输入框变化时启用/禁用发送按钮
        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = this.messageInput.value.trim() === '';
        });

        // 弹窗开始按钮
        this.startButton.addEventListener('click', () => this.startSession());

        // 弹窗输入框回车
        this.studentNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.startSession();
            }
        });

        // 页面关闭时断开连接
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
    }

    startSession() {
        const name = this.studentNameInput.value.trim();
        if (!name) {
            this.studentNameInput.style.borderColor = '#F44336';
            return;
        }

        this.studentName = name;
        this.studentId = name.toLowerCase().replace(/\s+/g, '_');

        // 更新显示
        this.studentNameDisplay.textContent = name;

        // 隐藏弹窗
        this.nameModal.style.display = 'none';

        // 清除欢迎消息
        const welcomeMsg = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        // 连接WebSocket
        this.connectWebSocket();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/${this.studentId}`;

        this.updateConnectionStatus('connecting');

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                console.log('WebSocket connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (e) {
                    console.error('Failed to parse message:', e);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');

                // 尝试重连
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => {
                        this.updateConnectionStatus('reconnecting');
                        this.connectWebSocket();
                    }, this.reconnectDelay);
                } else {
                    this.showError('连接失败，请刷新页面重试');
                }
            };
        } catch (e) {
            console.error('Failed to create WebSocket:', e);
            this.showError('无法连接到服务器');
        }
    }

    handleMessage(message) {
        const { type, content, data } = message;

        switch (type) {
            case 'message':
                this.hideTypingIndicator();
                this.addMessage('assistant', content);
                this.saveMessage('assistant', content);
                break;

            case 'status':
                if (data && data.status === 'connected') {
                    this.updateConnectionStatus('connected');
                }
                if (data && data.level !== undefined) {
                    this.studentLevelDisplay.textContent = data.level;
                }
                if (data && data.xp !== undefined) {
                    this.studentXpDisplay.textContent = data.xp;
                }
                break;

            case 'report':
                this.addMessage('assistant', content);
                break;

            case 'error':
                this.showError(content);
                this.hideTypingIndicator();
                break;

            case 'pong':
                // 心跳响应，无需处理
                break;

            default:
                console.log('Unknown message type:', type);
        }
    }

    sendMessage() {
        const text = this.messageInput.value.trim();
        if (!text || !this.isConnected) {
            return;
        }

        // 添加用户消息到界面
        this.addMessage('user', text);
        this.saveMessage('user', text);

        // 清空输入框
        this.messageInput.value = '';
        this.sendButton.disabled = true;

        // 显示打字指示器
        this.showTypingIndicator();

        // 发送消息
        try {
            this.ws.send(JSON.stringify({
                type: 'message',
                content: text
            }));
        } catch (e) {
            console.error('Failed to send message:', e);
            this.hideTypingIndicator();
            this.showError('发送消息失败');
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        // AI消息添加头像
        if (role === 'assistant') {
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = '🤖';
            messageDiv.appendChild(avatar);
        }

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // 简单的Markdown处理
        const formattedContent = this.formatMessage(content);
        bubble.innerHTML = formattedContent;

        messageDiv.appendChild(bubble);

        // 添加到聊天容器
        this.chatContainer.appendChild(messageDiv);

        // 滚动到底部
        this.scrollToBottom();
    }

    formatMessage(content) {
        // 简单的Markdown格式化
        let formatted = content
            // 粗体
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // 斜体
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // 换行
            .replace(/\n/g, '<br>');

        return formatted;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 10);
    }

    updateConnectionStatus(status) {
        this.statusDot.className = 'status-dot ' + status;

        const statusTexts = {
            'connected': '已连接',
            'disconnected': '未连接',
            'connecting': '连接中...',
            'reconnecting': '重连中...'
        };

        this.statusText.textContent = statusTexts[status] || '未知';
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '⚠️';
        errorDiv.appendChild(avatar);

        const bubble = document.createElement('div');
        bubble.className = 'error-message';
        bubble.textContent = message;
        errorDiv.appendChild(bubble);

        this.chatContainer.appendChild(errorDiv);
        this.scrollToBottom();

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    saveMessage(role, content) {
        this.messageHistory.push({ role, content, timestamp: Date.now() });
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new MathTutorChat();
});