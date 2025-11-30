import React, { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import {
  MessageCircle,
  X,
  Send,
  Bot,
  User,
  Minimize2,
  Maximize2,
  DollarSign,
  Clock,
  Phone,
  Globe,
  Zap,
} from "lucide-react";

const defaultConfig = {
  intro: "Hi! I'm your AI assistant from Codeteki. How can I help you transform your business with AI solutions today?",
};

const FormattedAIResponse = ({ content }) => {
  const formatBlocks = (text) => {
    return text.split("\n\n").filter(Boolean).map((block) => block.trim());
  };

  const getBlock = (block, index) => {
    if (block.match(/\$/) || block.includes("Setup") || block.includes("cost")) {
      return (
        <div
          key={index}
          className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-400 p-3 rounded-lg my-3 animate-in slide-in-from-left duration-500"
          style={{ animationDelay: `${index * 200}ms` }}
        >
          <div className="flex items-start space-x-2">
            <DollarSign className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm font-medium text-gray-800 leading-relaxed">{block}</p>
          </div>
        </div>
      );
    }
    if (block.includes("Third-party") || block.includes("telecom") || block.includes("/month")) {
      return (
        <div
          key={index}
          className="bg-gradient-to-r from-blue-50 to-sky-50 border-l-4 border-blue-400 p-3 rounded-lg my-3 animate-in slide-in-from-left duration-500"
          style={{ animationDelay: `${index * 200}ms` }}
        >
          <div className="flex items-start space-x-2">
            <Clock className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm font-medium text-gray-800 leading-relaxed">{block}</p>
          </div>
        </div>
      );
    }
    if (block.includes("@") || block.includes("+61") || block.toLowerCase().includes("contact")) {
      return (
        <div
          key={index}
          className="bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-400 p-3 rounded-lg my-3 animate-in slide-in-from-left duration-500"
          style={{ animationDelay: `${index * 200}ms` }}
        >
          <div className="flex items-start space-x-2">
            <Phone className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm font-medium text-gray-800 leading-relaxed">{block}</p>
          </div>
        </div>
      );
    }
    if (block.includes("?") || block.toLowerCase().includes("interested") || block.toLowerCase().includes("explore")) {
      return (
        <div
          key={index}
          className="bg-gradient-to-r from-amber-50 to-yellow-50 border-l-4 border-amber-400 p-3 rounded-lg my-3 animate-in slide-in-from-left duration-500"
          style={{ animationDelay: `${index * 200}ms` }}
        >
          <div className="flex items-start space-x-2">
            <Zap className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm font-bold text-gray-800 leading-relaxed">{block}</p>
          </div>
        </div>
      );
    }
    return (
      <div key={index} className="my-3 animate-in fade-in duration-500" style={{ animationDelay: `${index * 150}ms` }}>
        <p className="text-sm leading-relaxed text-gray-800 font-medium">{block}</p>
      </div>
    );
  };

  return <div className="space-y-1">{formatBlocks(content).map(getBlock)}</div>;
};

export default function ChatWidget() {
  const { data: configData } = useQuery({ queryKey: ["/api/chatbot/config/"], staleTime: Infinity });
  const chatbotConfig = configData?.data || defaultConfig;

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [showIntroPopup, setShowIntroPopup] = useState(false);
  const [hasShownIntro, setHasShownIntro] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef(null);
  const sessionId = useState(() => `session_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`)[0];

  useEffect(() => {
    if (!hasShownIntro) {
      const timer = setTimeout(() => {
        const audio = new Audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LFeSIFl2+t8p1eEQ1Nl+D0zn4SDD+C0fDPgzYCLE0=");
        audio.volume = 0.1;
        audio.play().catch(() => {});
        setShowIntroPopup(true);
        setHasShownIntro(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [hasShownIntro]);

  useEffect(() => {
    if (showIntroPopup) {
      const timer = setTimeout(() => setShowIntroPopup(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [showIntroPopup]);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: chatbotConfig.intro,
        timestamp: new Date(),
      },
    ]);
  }, [chatbotConfig.intro]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const ensureConversation = async () => {
    if (conversationId) return conversationId;
    const response = await fetch("/api/chatbot/conversation/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: "chat-widget" }),
    });
    if (!response.ok) throw new Error("Unable to start conversation");
    const payload = await response.json();
    const newId = payload?.data?.conversationId;
    setConversationId(newId);
    return newId;
  };

  const chatMutation = useMutation({
    mutationFn: async (message) => {
      const convId = await ensureConversation();
      const response = await fetch("/api/chatbot/message/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, conversationId: convId, sessionId }),
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "Chat error");
      }
      const payload = await response.json();
      return payload?.data || payload;
    },
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "assistant", content: data.response, timestamp: new Date() }]);
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I'm experiencing a technical issue (${message}). Please try refreshing the page or contact us directly for assistance.`,
          timestamp: new Date(),
        },
      ]);
    },
  });

  const handleSendMessage = () => {
    const trimmed = inputMessage.trim();
    if (!trimmed || chatMutation.isPending) return;
    setMessages((prev) => [...prev, { role: "user", content: trimmed, timestamp: new Date() }]);
    chatMutation.mutate(trimmed);
    setInputMessage("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-[9999]">
        <div className="relative group">
          <button
            onClick={() => {
              setIsOpen(true);
              setShowIntroPopup(false);
            }}
            className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black rounded-full w-14 h-14 sm:w-16 sm:h-16 shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-110 border-2 border-white/20 backdrop-blur-sm flex items-center justify-center focus:outline-none focus:ring-4 focus:ring-[#f9cb07]/50"
            aria-label="Open chat"
            title="Open chat"
          >
            <MessageCircle className="h-6 w-6 sm:h-7 sm:w-7 animate-bounce" />
          </button>
          <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none transform translate-y-2 group-hover:translate-y-0">
            <div className="bg-gray-900 text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap shadow-lg animate-pulse">
              Need help? Chat with us!
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
          {showIntroPopup && (
            <div className="absolute bottom-full right-0 mb-4 animate-in slide-in-from-bottom-4 fade-in duration-700 zoom-in-95 max-w-[90vw] sm:max-w-sm">
              <div className="bg-gradient-to-br from-white via-white to-[#f9cb07]/5 text-gray-800 p-4 sm:p-5 rounded-2xl shadow-2xl border-2 border-[#f9cb07]/20 w-full relative backdrop-blur-sm">
                <button
                  onClick={() => setShowIntroPopup(false)}
                  className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition-all duration-200 hover:rotate-90"
                  aria-label="Close chat introduction popup"
                >
                  <X className="h-4 w-4" />
                </button>
                <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
                  <div className="relative">
                    <Bot className="h-5 w-5 sm:h-6 sm:w-6 text-[#f9cb07] animate-pulse" />
                    <div className="absolute -top-1 -right-1 w-2 h-2 sm:w-3 sm:h-3 bg-green-400 rounded-full animate-ping"></div>
                  </div>
                  <div>
                    <h4 className="font-bold text-sm sm:text-base text-gray-900 animate-in slide-in-from-left duration-500">AI Assistant Ready!</h4>
                    <p className="text-[10px] sm:text-xs text-[#f9cb07] font-medium">Codeteki AI • Online Now</p>
                  </div>
                </div>
                <p className="text-xs sm:text-sm text-gray-700 mb-3 sm:mb-4 font-medium animate-in slide-in-from-left duration-700 delay-100">💡 I can help you with:</p>
                <div className="space-y-2 sm:space-y-3 mb-4 sm:mb-5">
                  <div className="flex items-center space-x-2 sm:space-x-3 p-2 bg-gradient-to-r from-blue-50 to-transparent rounded-lg animate-in slide-in-from-left duration-500 delay-200">
                    <MessageCircle className="h-3 w-3 sm:h-4 sm:w-4 text-blue-600 flex-shrink-0" />
                    <span className="text-xs sm:text-sm font-medium text-gray-700">AI Chatbot Capabilities</span>
                  </div>
                  <div className="flex items-center space-x-2 sm:space-x-3 p-2 bg-gradient-to-r from-green-50 to-transparent rounded-lg animate-in slide-in-from-left duration-500 delay-300">
                    <Phone className="h-3 w-3 sm:h-4 sm:w-4 text-green-600 flex-shrink-0" />
                    <span className="text-xs sm:text-sm font-medium text-gray-700">Voice Assistant Solutions</span>
                  </div>
                  <div className="flex items-center space-x-2 sm:space-x-3 p-2 bg-gradient-to-r from-purple-50 to-transparent rounded-lg animate-in slide-in-from-left duration-500 delay-400">
                    <Globe className="h-3 w-3 sm:h-4 sm:w-4 text-purple-600 flex-shrink-0" />
                    <span className="text-xs sm:text-sm font-medium text-gray-700">SEO & Website Optimization</span>
                  </div>
                  <div className="flex items-center space-x-2 sm:space-x-3 p-2 bg-gradient-to-r from-orange-50 to-transparent rounded-lg animate-in slide-in-from-left duration-500 delay-500">
                    <Zap className="h-3 w-3 sm:h-4 sm:w-4 text-orange-600 flex-shrink-0" />
                    <span className="text-xs sm:text-sm font-medium text-gray-700">Business Automation Advice</span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setIsOpen(true);
                    setShowIntroPopup(false);
                  }}
                  className="w-full bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black text-xs sm:text-sm py-2.5 sm:py-3 px-3 sm:px-4 rounded-xl hover:from-[#e6b800] hover:to-[#f9cb07] transition-all duration-300 font-bold shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  ✨ Start Chatting Now
                </button>
                <div className="absolute top-full right-10 w-0 h-0 border-l-6 border-r-6 border-t-6 border-transparent border-t-white"></div>
              </div>
            </div>
          )}
          <div className="absolute inset-0 rounded-full border-2 border-[#f9cb07] animate-ping pointer-events-none"></div>
          <div className="absolute inset-0 rounded-full bg-[#f9cb07]/20 animate-pulse pointer-events-none"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 right-0 sm:bottom-6 sm:right-6 z-[9999] w-full sm:w-auto">
      <Card className={`w-full sm:w-96 shadow-2xl border-2 border-[#f9cb07]/30 transition-all duration-300 ${isMinimized ? "h-16" : "h-screen sm:h-[600px]"} bg-white/95 backdrop-blur-md sm:rounded-lg rounded-none`}>
        <CardHeader className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black p-4 rounded-t-lg shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bot className="h-6 w-6" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white animate-pulse"></div>
              </div>
              <div>
                <CardTitle className="text-lg font-bold">Codeteki Assistant</CardTitle>
                <p className="text-xs opacity-80">AI Sales & Support</p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-black hover:bg-white/20 p-2 rounded-full transition-colors"
                aria-label={isMinimized ? "Expand chat window" : "Minimize chat window"}
              >
                {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-black hover:bg-white/20 p-2 rounded-full transition-colors"
                aria-label="Close chat window"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="p-0 flex flex-col h-[calc(100vh-88px)] sm:h-[calc(600px-88px)] bg-gradient-to-b from-white to-gray-50">
            <div className="flex-1 overflow-y-auto p-3 sm:p-4">
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={`${message.timestamp}-${index}`}
                    className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
                  >
                    <div
                      className={`max-w-[90%] sm:max-w-[85%] rounded-2xl px-3 py-2.5 sm:px-4 sm:py-3 shadow-sm ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] text-black ml-2 sm:ml-4"
                          : "bg-white text-gray-800 mr-2 sm:mr-4 border border-gray-200"
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.role === "assistant" && (
                          <div className="flex-shrink-0 w-6 h-6 bg-[#f9cb07] rounded-full flex items-center justify-center mt-0.5">
                            <Bot className="h-3 w-3 text-black" />
                          </div>
                        )}
                        <div className="flex-1">
                          {message.role === "assistant" ? (
                            <FormattedAIResponse content={message.content} />
                          ) : (
                            <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">{message.content}</p>
                          )}
                          <p className="text-xs opacity-50 mt-2 italic">
                            {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </p>
                        </div>
                        {message.role === "user" && (
                          <div className="flex-shrink-0 w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center mt-0.5">
                            <User className="h-3 w-3 text-white" />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {chatMutation.isPending && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="bg-white text-gray-800 rounded-2xl px-4 py-3 mr-4 border border-gray-200 shadow-sm">
                      <div className="flex items-center space-x-3">
                        <div className="w-6 h-6 bg-[#f9cb07] rounded-full flex items-center justify-center">
                          <Bot className="h-3 w-3 text-black" />
                        </div>
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-[#f9cb07] rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-[#f9cb07] rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                          <div className="w-2 h-2 bg-[#f9cb07] rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t bg-gradient-to-r from-gray-50 to-white p-3 sm:p-4">
              <div className="flex space-x-2 sm:space-x-3">
                <div className="flex-1 relative">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Ask about our AI solutions..."
                    className="border-2 border-gray-200 focus:border-[#f9cb07] focus:ring-2 focus:ring-[#f9cb07]/20 transition-all duration-300 rounded-full px-3 py-2.5 sm:px-4 sm:py-3 pr-10 sm:pr-12 bg-white shadow-sm hover:shadow-md text-sm sm:text-base font-medium placeholder:text-gray-400"
                    disabled={chatMutation.isLoading}
                  />
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || chatMutation.isPending}
                  className="bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black rounded-full px-4 py-2.5 sm:px-5 sm:py-3 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                >
                  {chatMutation.isPending ? (
                    <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="flex items-center justify-center mt-2 sm:mt-3 space-x-1.5 sm:space-x-2">
                <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-green-500 rounded-full animate-pulse"></div>
                <p className="text-[10px] sm:text-xs text-gray-500 font-medium">Powered by Codeteki AI • Always here to help</p>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
}
