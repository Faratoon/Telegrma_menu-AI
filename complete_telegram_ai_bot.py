import logging
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import google.generativeai as genai
import json

# ============ SETUP LOGGING ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # @BotFather
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"      # makersuite.google.com

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ============ BOT DATA ============
CHANNELS = {
    "news": -1001234567890,
    "updates": -1001234567891,
    "announcements": -1001234567892,
}

user_conversations = {}
user_posts = {}
scheduled_posts = {}

# ============ STATES ============
MENU, CHAT_MODE, POST_MODE, CHANNEL_MODE, SCHEDULE_MODE = range(5)

# ============ MAIN MENU ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display main menu - wada waafajin"""
    
    keyboard = [
        [
            InlineKeyboardButton("💬 AI Chat", callback_data="ai_chat"),
            InlineKeyboardButton("📝 Create Posts", callback_data="create_posts"),
        ],
        [
            InlineKeyboardButton("📢 Multipost", callback_data="multipost"),
            InlineKeyboardButton("📤 Forward Messages", callback_data="forward"),
        ],
        [
            InlineKeyboardButton("⏰ Schedule Post", callback_data="schedule_post"),
            InlineKeyboardButton("🎓 AI Learning", callback_data="ai_learning"),
        ],
        [
            InlineKeyboardButton("🔍 Ask AI", callback_data="ask_ai"),
            InlineKeyboardButton("✍️ AI Writing", callback_data="ai_writing"),
        ],
        [
            InlineKeyboardButton("📊 Channels", callback_data="manage_channels"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🤖 **Welcome to ALL-IN-ONE Bot!**

Qof mid oo xidhan:
✅ AI Chat (Gemini)
✅ Channel Management
✅ Post Creation & Scheduling
✅ Message Forwarding
✅ Creative Writing
✅ Learning & Q&A

Choose what you want:
    """
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    return MENU

# ============ AI CHAT FUNCTIONS ============

def get_ai_response(user_id: int, message: str, mode: str = "chat") -> str:
    """Get response from Gemini AI"""
    try:
        if user_id not in user_conversations:
            user_conversations[user_id] = []
        
        # Add context based on mode
        context = ""
        if mode == "learning":
            context = "You are an expert educator. Explain clearly and educatingly. "
        elif mode == "writing":
            context = "You are a creative writing expert. Help with creative content. "
        elif mode == "coding":
            context = "You are a programming expert. Provide code examples. "
        
        # Build conversation
        convo_text = context
        for item in user_conversations[user_id][-5:]:
            convo_text += f"{item['role']}: {item['message']}\n"
        convo_text += f"user: {message}\n"
        
        response = model.generate_content(convo_text)
        ai_text = response.text
        
        # Save to history
        user_conversations[user_id].append({"role": "user", "message": message})
        user_conversations[user_id].append({"role": "assistant", "message": ai_text})
        
        return ai_text
    
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return f"❌ Error: {str(e)}"

# ============ AI CHAT HANDLER ============

async def ai_chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """AI Chat mode"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    context.user_data["mode"] = "chat"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
💬 **AI Chat Mode**

Hadal walaac, Gemini AI ayaa jaba!
I type your message:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return CHAT_MODE

async def ai_learning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Learning mode"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    context.user_data["mode"] = "learning"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎓 **Learning Mode**

I can teach you any topic!
Bar cid runta ah, I'll explain:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return CHAT_MODE

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask questions"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    context.user_data["mode"] = "chat"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🔍 **Ask AI Anything**

Wax kasta oo su'aal ah, AI waa jabarti!
Ask your question:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return CHAT_MODE

async def ai_writing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Creative writing"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    context.user_data["mode"] = "writing"
    
    keyboard = [[InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
✍️ **Creative Writing**

I can help with:
• Stories
• Poetry
• Blog posts
• Content creation

Send your writing request:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return CHAT_MODE

async def handle_chat_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle chat messages"""
    
    user_id = update.effective_user.id
    mode = context.user_data.get("mode", "chat")
    
    await update.message.chat.send_action("typing")
    
    response = get_ai_response(user_id, update.message.text, mode)
    
    # Split long messages
    if len(response) > 4096:
        parts = [response[i:i+4096] for i in range(0, len(response), 4096)]
        for part in parts:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(response, parse_mode="Markdown")
    
    return CHAT_MODE

# ============ POST CREATION ============

async def create_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create posts"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📝 Write Post", callback_data="write_post")],
        [InlineKeyboardButton("🤖 AI Generate", callback_data="ai_generate_post")],
        [InlineKeyboardButton("⬅️ Back Menu", callback_data="back_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
📝 **Create Posts**

How do you want to create:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return POST_MODE

async def write_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Write post manually"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["post_action"] = "write"
    
    keyboard = [[InlineKeyboardButton("⬅️ Cancel", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
✍️ **Write Your Post**

Type the content you want to post:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return POST_MODE

async def ai_generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate post using AI"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["post_action"] = "ai_generate"
    
    keyboard = [[InlineKeyboardButton("⬅️ Cancel", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🤖 **AI Generate Post**

Tell me what kind of post you want:
Example: "Write a post about technology trends"
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return POST_MODE

async def handle_post_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle post content"""
    
    user_id = update.effective_user.id
    action = context.user_data.get("post_action", "write")
    
    if action == "ai_generate":
        # Generate post using AI
        await update.message.chat.send_action("typing")
        prompt = f"Write a professional social media post about: {update.message.text}"
        post_content = get_ai_response(user_id, prompt, "writing")
    else:
        post_content = update.message.text
    
    user_posts[user_id] = post_content
    
    keyboard = [
        [InlineKeyboardButton("📍 Select Channels", callback_data="select_channels")],
        [InlineKeyboardButton("👁️ Preview", callback_data="preview_post")],
        [InlineKeyboardButton("⏰ Schedule", callback_data="schedule_post")],
        [InlineKeyboardButton("✅ Post Now", callback_data="post_now")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
✅ **Post Created!**

Content: