import { streamText } from 'ai';
import { createDeepSeek } from '@ai-sdk/deepseek';

const deepseek = createDeepSeek({
  apiKey: process.env.DEEPSEEK_API_KEY ?? '',
  baseURL: 'https://api.deepseek.com/v1'
});

interface MessagePart {
  type: 'text';
  text: string;
}

interface InputMessage {
  role: 'user' | 'assistant';
  content?: string;
  parts?: MessagePart[];
}

interface FormattedMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function POST(req: Request) {
  try {
    const { messages }: { messages: InputMessage[] } = await req.json();

    console.log('API Key exists:', !!process.env.DEEPSEEK_API_KEY);
    console.log('Messages received:', messages);

    // Handle both old format (content) and new format (parts)
    const formattedMessages: FormattedMessage[] = messages.map(
      (msg: InputMessage) => {
        let content = '';

        if (typeof msg.content === 'string') {
          content = msg.content;
        } else if (msg.parts && Array.isArray(msg.parts)) {
          // Extract text from parts array
          content = msg.parts
            .filter((part) => part.type === 'text')
            .map((part) => part.text)
            .join('');
        }

        return {
          role: msg.role,
          content: content
        };
      }
    );

    console.log('Formatted messages:', formattedMessages);

    const result = await streamText({
      model: deepseek('deepseek-chat'),
      messages: formattedMessages,
      system: `您是学长帮 AI 留学规划师，一个专业的留学咨询助手。

您的职责是：
• 🎯 推荐适合的学校和专业
• 📋 查询申请要求和截止日期
• 👥 匹配合适的学长学姐引路人
• 🛍️ 推荐相关指导服务
• 📅 制定申请时间规划
• 💡 提供文书和面试建议

请用专业、友好、详细的方式回答用户的留学相关问题。如果用户询问与留学无关的问题，请礼貌地引导他们回到留学相关话题。`
    });

    return result.toTextStreamResponse();
  } catch (error) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({
        error: 'Failed to process chat request',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
