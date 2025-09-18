'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send,
  Search,
  User,
  Circle,
  Paperclip,
  Mic,
  Image as ImageIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { searchMentors, type MentorPublic } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import { API_CONFIG, getFullUrl } from '@/lib/api-config';
import { aiAgentAPI, type AutoChatRequest, type ChatRequest, type ChatResponse } from '@/lib/ai-agent-api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentType?: 'study_planner' | 'study_consultant';
  agentName?: string;
  sessionId?: string;
}

interface AgentConversation {
  id: string;
  agentType: 'study_planner' | 'study_consultant';
  agentName: string;
  lastMessage?: string;
  lastMessageTime?: Date;
  unreadCount?: number;
  isActive?: boolean;
  sessionId?: string;
}

// 默认智能体配置
const defaultAgents: AgentConversation[] = [
  {
    id: 'planner-1',
    agentType: 'study_planner',
    agentName: '留学规划师',
    lastMessage: '我可以帮你制定个性化的留学申请策略',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 31), // 31 minutes ago
    unreadCount: 0,
    isActive: true,
    sessionId: undefined
  },
  {
    id: 'consultant-1',
    agentType: 'study_consultant',
    agentName: '留学咨询师',
    lastMessage: '我可以解答你的留学疑问',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    unreadCount: 0,
    isActive: true,
    sessionId: undefined
  }
];

export default function AgentChatPage() {
  const router = useRouter();
  const { isAuthenticated, token, initialized, loading } = useAuthStore();
  const [selectedAgent, setSelectedAgent] = useState<AgentConversation | null>(defaultAgents[0]);
  const [conversations, setConversations] = useState<AgentConversation[]>(defaultAgents);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MentorPublic[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Wait for auth initialization to complete
    if (initialized && !loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, initialized, loading, router]);

  // Removed automatic scrolling when messages update
  // useEffect(() => {
  //   scrollToBottom();
  // }, [messages]);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = useCallback(async () => {
    try {
      // TODO: Load conversations from API when MESSAGES endpoint is available
      console.warn('loadConversations: MESSAGES endpoint not available, returning empty conversations');

      // For now, return empty conversations
      setConversations([]);
      return;

      // TODO: Load conversations from API when MESSAGES endpoint is available
      // const response = await fetch(
      //   getFullUrl(API_CONFIG.ENDPOINTS.MESSAGES.CONVERSATIONS),
      //   {
      //     headers: {
      //       Authorization: `Bearer ${token}`,
      //       'Content-Type': 'application/json'
      //     }
      //   }
      // );

      // TODO: Uncomment when MESSAGES endpoint is available
      // if (response.ok) {
      //   const data = await response.json();
      //   // Transform API data to our conversation format
      //   const formattedConversations: Conversation[] = data.map(
      //     (conv: {
      //       tutor_id?: number;
      //       mentor_id?: number;
      //       id?: number;
      //       tutor_name?: string;
      //       mentor_name?: string;
      //       avatar_url?: string;
      //       last_message?: string;
      //       last_message_time?: string;
      //       unread_count?: number;
      //       is_online?: boolean;
      //     }) => ({
      //       tutorId: conv.tutor_id || conv.mentor_id || conv.id || 0,
      //       tutorName: conv.tutor_name || conv.mentor_name || 'Unknown Tutor',
      //       tutorAvatar: conv.avatar_url,
      //       lastMessage: conv.last_message,
      //       lastMessageTime: conv.last_message_time
      //         ? new Date(conv.last_message_time)
      //         : undefined,
      //       unreadCount: conv.unread_count || 0,
      //       isOnline: conv.is_online || false
      //     })
      //   );

      //   // Merge with default tutors, prioritizing API data
      //   const mergedConversations = [...formattedConversations];
      //   defaultTutors.forEach(defaultTutor => {
      //     if (
      //       !mergedConversations.find(c => c.tutorId === defaultTutor.tutorId)
      //     ) {
      //       mergedConversations.push(defaultTutor);
      //     }
      //   });

      //   setConversations(mergedConversations);
      // }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      // Keep default tutors on error
    }
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    }
  }, [isAuthenticated, token, loadConversations]);

  const loadMessages = async (tutorId: number) => {
    try {
      setIsLoading(true);

      // TODO: Load messages from API when MESSAGES endpoint is available
      console.warn('loadMessages: MESSAGES endpoint not available, returning empty messages');
      setMessages([]);
      setIsLoading(false);
      return;

      // TODO: Uncomment when MESSAGES endpoint is available
      // const response = await fetch(
      //   getFullUrl(API_CONFIG.ENDPOINTS.MESSAGES.CONVERSATION_BY_ID(tutorId)),
      //   {
      //     headers: {
      //       Authorization: `Bearer ${token}`,
      //       'Content-Type': 'application/json'
      //     }
      //   }
      // );

      // if (response.ok) {
      //   const data = await response.json();
      //   const formattedMessages: Message[] = data.map(
      //     (msg: {
      //       id?: string | number;
      //       content?: string;
      //       message?: string;
      //       sender_id?: number;
      //       created_at?: string;
      //       timestamp?: string;
      //     }) => ({
      //       id: String(msg.id || Date.now() + Math.random()),
      //       content: msg.content || msg.message || '',
      //       sender: msg.sender_id === tutorId ? 'tutor' : 'user',
      //       timestamp: new Date(msg.created_at || msg.timestamp || Date.now()),
      //       tutorId: tutorId,
      //       tutorName: selectedTutor?.tutorName
      //     })
      //   );
      //   setMessages(formattedMessages);
      // }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchTutors = async () => {
    if (!searchQuery.trim()) return;

    try {
      setIsSearching(true);
      const results = await searchMentors({
        search_query: searchQuery,
        limit: 10
      });
      setSearchResults(results);
    } catch (error) {
      console.error('Failed to search tutors:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const startConversationWithTutor = (tutor: MentorPublic) => {
    const newConversation: Conversation = {
      tutorId: tutor.id,
      tutorName: tutor.title,
      isOnline: true
    };

    // Add to conversations if not already there
    if (!conversations.find(c => c.tutorId === tutor.id)) {
      setConversations([newConversation, ...conversations]);
    }

    setSelectedTutor(newConversation);
    setMessages([]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedAgent) return;

    const userMessage: Message = {
      id: String(Date.now()),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      agentType: selectedAgent.agentType,
      agentName: selectedAgent.agentName,
      sessionId: currentSessionId || undefined
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    try {
      const chatRequest: AutoChatRequest = {
        request: {
          message: currentInput,
          session_id: currentSessionId
        },
        agent_type: selectedAgent.agentType
      };

      const response = await aiAgentAPI.chatWithAutoAgent(chatRequest);

      const agentMessage: Message = {
        id: String(Date.now() + 1),
        content: response.response,
        sender: 'agent',
        timestamp: new Date(),
        agentType: response.agent_type as 'study_planner' | 'study_consultant',
        agentName: selectedAgent.agentName,
        sessionId: response.session_id || undefined
      };

      setMessages(prev => [...prev, agentMessage]);
      setCurrentSessionId(response.session_id);

      // 更新对话列表中的最后消息
      setConversations(prev =>
        prev.map(conv =>
          conv.id === selectedAgent.id
            ? { ...conv, lastMessage: response.response, lastMessageTime: new Date() }
            : conv
        )
      );

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: String(Date.now() + 2),
        content: '抱歉，我现在无法回复，请稍后再试。',
        sender: 'agent',
        timestamp: new Date(),
        agentType: selectedAgent.agentType,
        agentName: selectedAgent.agentName,
        sessionId: currentSessionId || undefined
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const selectAgent = (agent: AgentConversation) => {
    setSelectedAgent(agent);
    setCurrentSessionId(agent.sessionId || null);
    setMessages([]); // 清空消息，开始新对话
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;

    return date.toLocaleDateString('zh-CN');
  };

  // Show loading state while auth is initializing
  if (!initialized || loading) {
    return (
      <div className="container mx-auto p-4 h-[calc(100vh-100px)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8 h-[calc(100vh-100px)]">
      <Card className="h-full p-0 border-blue-200 border-2 shadow-lg">
        <div className="flex h-full">
          {/* Conversations List */}
          <div className="w-full md:w-1/3 h-full flex flex-col">
            <CardHeader className="py-0">
              <CardTitle className="text-lg pt-4 bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent">
                AI智能体对话
              </CardTitle>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="搜索智能体..."
                  className="pl-10 pr-4"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      searchTutors();
                    }
                  }}
                />
              </div>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-hidden">
              <ScrollArea className="h-full">
                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="p-4 border-b-2 border-blue-200">
                    <p className="text-sm text-blue-600 font-medium mb-2">
                      搜索结果
                    </p>
                    {searchResults.map(tutor => (
                      <div
                        key={tutor.id}
                        className="flex items-center gap-3 p-3 hover:bg-blue-50 cursor-pointer rounded-lg transition-colors"
                        onClick={() => startConversationWithTutor(tutor)}
                      >
                        <Avatar>
                          <AvatarFallback>{tutor.title[0]}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-medium">{tutor.title}</p>
                          <p className="text-sm text-gray-500 line-clamp-1">
                            {tutor.description}
                          </p>
                        </div>
                        <Badge className="bg-gradient-to-r from-blue-500 to-sky-500 text-white border-0">
                          开始对话
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}

                {/* Available Agents */}
                <div className="p-2">
                  {conversations.length === 0 && !isSearching && (
                    <p className="text-center text-gray-500 py-8">
                      没有可用的智能体
                    </p>
                  )}
                  {conversations.map(agent => (
                    <div
                      key={agent.id}
                      className={`flex items-center gap-3 p-3 mx-3 hover:bg-blue-50 cursor-pointer rounded-lg transition-colors ${selectedAgent?.id === agent.id
                          ? 'bg-gradient-to-r from-blue-100 to-sky-100 shadow-sm'
                          : ''
                        }`}
                      onClick={() => selectAgent(agent)}
                    >
                      <div className="relative">
                        <Avatar>
                          <AvatarFallback className="bg-gradient-to-r from-blue-500 to-sky-500 text-white">
                            {agent.agentType === 'study_planner' ? '📚' : '💬'}
                          </AvatarFallback>
                        </Avatar>
                        {agent.isActive && (
                          <Circle className="absolute bottom-0 right-0 h-3 w-3 fill-emerald-500 text-emerald-500 animate-pulse" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium truncate">
                            {agent.agentName}
                          </p>
                          {agent.lastMessageTime && (
                            <span className="text-xs text-gray-500">
                              {formatTime(agent.lastMessageTime)}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="outline"
                            className={`text-xs ${agent.agentType === 'study_planner'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-green-500 text-green-600'
                              }`}
                          >
                            {agent.agentType === 'study_planner' ? '规划师' : '咨询师'}
                          </Badge>
                          {agent.lastMessage && (
                            <p className="text-sm text-gray-500 truncate flex-1">
                              {agent.lastMessage}
                            </p>
                          )}
                        </div>
                      </div>
                      {agent.unreadCount && agent.unreadCount > 0 ? (
                        <Badge className="bg-gradient-to-r from-red-500 to-pink-500 text-white border-0 rounded-full">
                          {agent.unreadCount}
                        </Badge>
                      ) : null}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </div>

          {/* Vertical Separator */}
          <Separator
            orientation="vertical"
            className="hidden md:block w-0.5 bg-blue-200"
          />

          {/* Chat Area */}
          <div className="flex-1 h-full flex flex-col">
            {selectedAgent ? (
              <>
                <div className="flex items-center p-4 border-b-2 border-blue-200 bg-gradient-to-r from-blue-50 to-sky-50">
                  <Avatar className="h-10 w-10 mr-3">
                    <AvatarFallback className="bg-gradient-to-r from-blue-500 to-sky-500 text-white">
                      {selectedAgent.agentType === 'study_planner' ? '📚' : '💬'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h2 className="font-semibold">{selectedAgent.agentName}</h2>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="outline"
                        className={`text-xs ${selectedAgent.agentType === 'study_planner'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-green-500 text-green-600'
                          }`}
                      >
                        {selectedAgent.agentType === 'study_planner' ? '留学规划师' : '留学咨询师'}
                      </Badge>
                      <p className="text-xs text-emerald-600 font-medium">
                        🟢 在线
                      </p>
                    </div>
                  </div>
                </div>

                <CardContent className="flex-1 p-0 overflow-hidden">
                  <ScrollArea className="h-full p-4">
                    {isLoading ? (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">加载中...</p>
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">开始与AI智能体对话吧！</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {messages.map(message => (
                          <div
                            key={message.id}
                            className={`flex ${message.sender === 'user'
                              ? 'justify-end'
                              : 'justify-start'
                              }`}
                          >
                            <div
                              className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm ${message.sender === 'user'
                                ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-br-none'
                                : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 rounded-bl-none'
                                }`}
                            >
                              <p>{message.content || ''}</p>
                              <div
                                className={`text-xs mt-1 ${message.sender === 'user'
                                  ? 'text-primary-foreground/70'
                                  : 'text-muted-foreground'
                                  }`}
                              >
                                {message.timestamp.toLocaleTimeString('zh-CN', {
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </div>
                            </div>
                          </div>
                        ))}

                        {isTyping && (
                          <div className="flex justify-start">
                            <div className="bg-gradient-to-r from-gray-100 to-gray-200 rounded-2xl rounded-bl-none px-4 py-2">
                              <div className="flex space-x-1">
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '0ms' }}
                                ></div>
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '150ms' }}
                                ></div>
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '300ms' }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={messagesEndRef} />
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>

                <div className="p-4 border-t-2 border-blue-200">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      className="rounded-full"
                    >
                      <Paperclip className="h-5 w-5" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="rounded-full"
                    >
                      <ImageIcon className="h-5 w-5" />
                    </Button>
                    <div className="flex-1 relative">
                      <Input
                        value={inputMessage}
                        onChange={e => setInputMessage(e.target.value)}
                        placeholder="输入消息..."
                        className="pr-10 rounded-full"
                        onKeyDown={e => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                          }
                        }}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 -translate-y-1/2 rounded-full"
                      >
                        <Mic className="h-5 w-5" />
                      </Button>
                    </div>
                    <Button
                      onClick={sendMessage}
                      size="icon"
                      className="rounded-full bg-gradient-to-r from-blue-500 to-sky-500 hover:from-blue-600 hover:to-sky-600 text-white border-0"
                      disabled={inputMessage.trim() === ''}
                    >
                      <Send className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <User className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">选择一个AI智能体开始对话</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
