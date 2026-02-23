import os
import re
import logging
import deepl
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("8608262327:AAFj3RBpjTc6ilan_Z4MDHhkgjQf9R8C1bw")
deepl_key = os.environ.get("d4fefdbb-c8fc-4580-915b-b123ec965c8c:fx")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translator-bot")

# Regex simples pra detectar chinês (CJK)
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

def is_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))

def looks_like_command(text: str) -> bool:
    return (text or "").strip().startswith("/")

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg or not msg.text:
        return

    # Evita loop (não traduz mensagens de bots)
    if msg.from_user and msg.from_user.is_bot:
        return

    text = msg.text.strip()
    if not text or looks_like_command(text):
        return

    translator: deepl.Translator = context.bot_data["translator"]

    try:
        if is_cjk(text):
            # chinês -> pt-br
            result = translator.translate_text(text, target_lang="PT-BR")
            await msg.reply_text(f"🇧🇷 PT-BR: {result.text}")
        else:
            # pt (ou outro) -> chinês
            # DeepL usa "ZH" como target (chinês)
            result = translator.translate_text(text, target_lang="ZH")
            await msg.reply_text(f"🇨🇳 中文: {result.text}")

    except Exception as e:
        logger.exception("Translation error")
        await msg.reply_text("⚠️ Deu erro ao traduzir agora. Tenta de novo em instantes.")

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    deepl_key = os.environ.get("DEEPL_API_KEY")

    if not token:
        raise RuntimeError("Faltou TELEGRAM_BOT_TOKEN no ambiente.")
    if not deepl_key:
        raise RuntimeError("Faltou DEEPL_API_KEY no ambiente.")

    app = Application.builder().token(token).build()

    # DeepL client (recomendado usar 1 instância)
    app.bot_data["translator"] = deepl.Translator(deepl_key)

    # Handler de texto comum (sem comandos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    # polling (pra começar rápido)
    app.run_polling()

if __name__ == "__main__":
    main()
