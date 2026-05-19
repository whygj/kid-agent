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

        // 语音相关
        this.speechRecognition = null;
        this.isRecording = false;
        this.autoPlay = true;
        this.currentUtterance = null;

        this.initElements();
        this.initEventListeners();
        this.initSpeechRecognition();
        this.loadAutoPlaySetting();
    }

    initElements() {
        // 聊天相关
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator');

        // 语音相关
        this.micButton = document.getElementById('mic-button');
        this.speakerToggle = document.getElementById('speaker-toggle');
        this.stopSpeechButton = document.getElementById('stop-speech');

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

        // 麦克风按钮
        this.micButton.addEventListener('click', () => this.toggleRecording());

        // 朗读开关
        this.speakerToggle.addEventListener('click', () => this.toggleAutoPlay());

        // 停止朗读
        this.stopSpeechButton.addEventListener('click', () => this.stopSpeaking());

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

    initSpeechRecognition() {
        // 检查浏览器是否支持语音识别
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('浏览器不支持语音识别');
            this.micButton.style.display = 'none';
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.speechRecognition = new SpeechRecognition();

        this.speechRecognition.continuous = false;
        this.speechRecognition.interimResults = true;
        this.speechRecognition.lang = 'zh-CN';
        this.speechRecognition.maxAlternatives = 1;

        this.speechRecognition.onstart = () => {
            this.isRecording = true;
            this.micButton.classList.add('recording');
            this.micButton.title = '停止录音';
        };

        this.speechRecognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                this.messageInput.value = finalTranscript;
                this.sendButton.disabled = false;
            } else if (interimTranscript) {
                this.messageInput.placeholder = `正在识别: ${interimTranscript}`;
            }
        };

        this.speechRecognition.onerror = (event) => {
            console.error('语音识别错误:', event.error);
            this.stopRecording();
            this.messageInput.placeholder = '输入你的答案或问题...';

            if (event.error === 'not-allowed') {
                this.showError('请允许麦克风权限');
            }
        };

        this.speechRecognition.onend = () => {
            this.stopRecording();

            // 如果识别成功且有内容，自动发送
            if (this.messageInput.value.trim()) {
                this.sendMessage();
            }
        };
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        if (!this.speechRecognition) {
            this.showError('浏览器不支持语音识别');
            return;
        }

        try {
            this.speechRecognition.start();
            this.messageInput.placeholder = '正在聆听...';
        } catch (e) {
            console.error('启动录音失败:', e);
        }
    }

    stopRecording() {
        if (this.speechRecognition && this.isRecording) {
            this.speechRecognition.stop();
        }
        this.isRecording = false;
        this.micButton.classList.remove('recording');
        this.micButton.title = '语音输入';
        this.messageInput.placeholder = '输入你的答案或问题...';
    }

    toggleAutoPlay() {
        this.autoPlay = !this.autoPlay;
        this.speakerToggle.classList.toggle('active', this.autoPlay);
        localStorage.setItem('autoPlay', this.autoPlay);
    }

    loadAutoPlaySetting() {
        const saved = localStorage.getItem('autoPlay');
        if (saved !== null) {
            this.autoPlay = saved === 'true';
            this.speakerToggle.classList.toggle('active', this.autoPlay);
        }
    }

    speak(text) {
        if (!this.autoPlay || !text) return;

        // 停止当前朗读
        this.stopSpeaking();

        // 检查浏览器是否支持语音合成
        if (!('speechSynthesis' in window)) {
            console.warn('浏览器不支持语音合成');
            return;
        }

        // 清理文本用于朗读
        const cleanText = this.cleanTextForSpeech(text);
        if (!cleanText) return;

        // 获取中文语音
        const voices = window.speechSynthesis.getVoices();
        let voice = voices.find(v => v.lang.startsWith('zh'));

        // 如果没有中文语音，使用默认
        if (!voice && voices.length > 0) {
            voice = voices[0];
        }

        this.currentUtterance = new SpeechSynthesisUtterance(cleanText);

        // 设置语音参数
        if (voice) {
            this.currentUtterance.voice = voice;
        }
        this.currentUtterance.rate = 0.9;  // 语速稍慢，适合小学生
        this.currentUtterance.pitch = 1.0;
        this.currentUtterance.volume = 1.0;

        // 显示停止按钮
        this.stopSpeechButton.style.display = 'block';

        // 事件处理
        this.currentUtterance.onend = () => {
            this.stopSpeechButton.style.display = 'none';
            this.currentUtterance = null;
        };

        this.currentUtterance.onerror = (e) => {
            console.error('语音合成错误:', e);
            this.stopSpeechButton.style.display = 'none';
            this.currentUtterance = null;
        };

        window.speechSynthesis.speak(this.currentUtterance);
    }

    stopSpeaking() {
        if (this.currentUtterance) {
            window.speechSynthesis.cancel();
            this.currentUtterance = null;
        }
        this.stopSpeechButton.style.display = 'none';
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
                // 自动朗读AI回复
                this.speak(content);
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

    // 清理文本用于语音朗读（移除Markdown符号等）
    cleanTextForSpeech(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '$1')  // 移除粗体标记
            .replace(/\*(.*?)\*/g, '$1')     // 移除斜体标记
            .replace(/`([^`]+)`/g, '$1')     // 移除代码标记
            .replace(/\n+/g, '，')            // 换行转为逗号
            .replace(/\s+/g, ' ')             // 多个空格转为单个空格
            .trim();
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