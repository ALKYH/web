'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import ReactMarkdown from 'react-markdown';

interface ChatWidgetProps {
  position?: 'bottom-right' | 'bottom-left';
}

// 辅助函数：从UIMessage中提取文本内容
const getMessageText = (message: any) => {
  if (typeof message.content === 'string') {
    return message.content;
  }
  if (message.parts && Array.isArray(message.parts)) {
    const textParts = message.parts.filter((part: any) => part.type === 'text');
    return textParts.map((part: any) => part.text).join('');
  }
  return '';
};

// Client-only component to prevent hydration mismatch
const ClientTimestamp = ({ date }: { date: Date }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return <>{new Date(date).toLocaleTimeString()}</>;
};

export default function ChatWidget({
  position = 'bottom-right'
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const initialMessages: any[] = [
    {
      id: '1',
      role: 'assistant',
      parts: [
        {
          type: 'text',
          text: '您好！我是启航AI留学规划师 ✨\n\n我可以帮助您：\n• 🎯 推荐适合的学校和专业\n• 📋 查询申请要求和截止日期\n• 👥 匹配合适的学长学姐引路人\n• 🛍️ 推荐相关指导服务\n• 📅 制定申请时间规划\n• 💡 提供文书和面试建议\n\n请告诉我您的留学问题，我会竭诚为您服务！'
        }
      ]
    }
  ];

  const [messages, setMessages] = useState(initialMessages);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      parts: [{ type: 'text' as const, text: messageText }]
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage]
        })
      });

      if (!response.ok) throw new Error('API request failed');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      // 读取流式响应
      const decoder = new TextDecoder();
      let done = false;
      let assistantMessageContent = '';
      let assistantMessageAdded = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          assistantMessageContent += chunk;

          // 只有当有内容时才添加/更新助手消息
          if (assistantMessageContent.trim() && !assistantMessageAdded) {
            const assistantMessage = {
              id: (Date.now() + 1).toString(),
              role: 'assistant' as const,
              parts: [{ type: 'text' as const, text: assistantMessageContent }]
            };
            setMessages(prev => [...prev, assistantMessage]);
            assistantMessageAdded = true;
          } else if (assistantMessageAdded) {
            // 更新现有的助手消息
            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = {
                ...newMessages[newMessages.length - 1],
                parts: [{ type: 'text' as const, text: assistantMessageContent }]
              };
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (input.trim() && !isLoading) {
      sendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const positionClass =
    position === 'bottom-right' ? 'bottom-4 right-4' : 'bottom-4 left-4';

  const quickActions = [
    '我想申请美国的计算机科学硕士，需要什么条件？',
    '推荐一些英国的商科学校',
    '帮我制定留学申请时间规划',
    '找一些经验丰富的引路人'
  ];

  return (
    <div className={`fixed ${positionClass} z-50 flex flex-col items-end`}>
      {/* Chat Widget */}
      {isOpen && (
        <Card className="w-80 h-[500px] mb-4 shadow-2xl animate-in slide-in-from-bottom-2 flex flex-col">
          <CardHeader className="bg-gradient-to-r from-primary to-primary/80 text-white rounded-t-lg p-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Bot className="h-5 w-5" />
                  <div className="absolute -bottom-1 -right-1 h-2 w-2 bg-green-400 rounded-full border border-white"></div>
                </div>
                <div>
                  <CardTitle className="text-sm">学长帮 AI 助手</CardTitle>
                  <p className="text-xs text-white/80">在线 · 随时为您服务</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-white hover:bg-white/20"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-0 flex flex-col flex-1 min-h-0">
            {/* Messages */}
            <div className="flex-1 p-3 overflow-y-auto space-y-3" style={{ minHeight: 0 }}>
              {messages.length === 1 && (
                <>
                  {/* Welcome Message */}
                  <div className="flex gap-2">
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="h-3 w-3 text-primary" />
                      </div>
                    </div>
                    <div className="max-w-[80%]">
                      <div className="bg-muted rounded-lg px-3 py-2">
                        <div className="text-xs">
                          <ReactMarkdown
                            components={{
                              p: ({ node, ...props }) => (
                                <p {...props} className="mb-1 last:mb-0" />
                              ),
                              ul: ({ node, ...props }) => (
                                <ul {...props} className="list-disc pl-3" />
                              ),
                            }}
                          >
                            {getMessageText(messages[0])}
                          </ReactMarkdown>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        <ClientTimestamp date={new Date()} />
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-600">快速问题：</p>
                    {quickActions.map((action, index) => (
                      <button
                        key={index}
                        onClick={() => handleQuickQuestion(action)}
                        className="w-full text-left p-2 text-xs bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                </>
              )}

              {/* Chat Messages */}
              {messages.length > 1 && messages.slice(1).map(message => (
                <div
                  key={message.id}
                  className={`flex gap-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="h-3 w-3 text-primary" />
                      </div>
                    </div>
                  )}

                  <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                    <div
                      className={`rounded-lg px-3 py-2 ${message.role === 'user'
                          ? 'bg-primary text-primary-foreground ml-auto'
                          : 'bg-muted'
                        }`}
                    >
                      <div className="text-xs">
                        <ReactMarkdown
                          components={{
                            p: ({ node, ...props }) => (
                              <p {...props} className="mb-1 last:mb-0" />
                            ),
                            ul: ({ node, ...props }) => (
                              <ul {...props} className="list-disc pl-3" />
                            ),
                          }}
                        >
                          {getMessageText(message)}
                        </ReactMarkdown>
                      </div>
                    </div>
                    <div
                      className={`text-xs text-muted-foreground mt-1 ${message.role === 'user' ? 'text-right' : 'text-left'
                        }`}
                    >
                      <ClientTimestamp date={new Date()} />
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                        <User className="h-3 w-3 text-primary-foreground" />
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && messages.length > 0 && messages[messages.length - 1]?.role === 'user' && (
                <div className="flex gap-2 justify-start">
                  <div className="flex-shrink-0">
                    <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center">
                      <Bot className="h-3 w-3 text-primary" />
                    </div>
                  </div>
                  <div className="max-w-[80%]">
                    <div className="rounded-lg bg-muted px-3 py-2">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span className="text-xs">AI 正在思考...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-3 flex-shrink-0">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入您的留学问题..."
                  disabled={isLoading}
                  className="text-xs"
                />
                <Button
                  size="icon"
                  onClick={handleSendMessage}
                  disabled={!input.trim() || isLoading}
                  className="flex-shrink-0 h-8 w-8"
                >
                  {isLoading ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Send className="h-3 w-3" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-center text-muted-foreground mt-2">
                按 Enter 发送消息 · AI可能会出错，请验证重要信息
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Toggle Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        size="icon"
        className="h-14 w-14 rounded-full shadow-lg bg-gradient-to-r from-primary to-primary/80 hover:shadow-xl transition-all duration-200"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageSquare className="h-6 w-6" />
        )}
      </Button>
    </div>
  );
}