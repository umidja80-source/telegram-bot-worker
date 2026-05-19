
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

# ========== SOZLAMALAR ==========
WORKER_BOT_TOKEN    = "8906343763:AAHiayqVtXGiad2SDV4BP2yq15WI7uG-Dac"   # @BotFather dan oling
CUSTOMER_BOT_TOKEN  = "8908187461:AAHT-RhnhHdpAkm6hDDKqTRwilWGLjHjxgk" # Mijoz boti tokeni

# Ruxsat etilgan ishchilar Telegram ID lari
ALLOWED_WORKERS = [
    1200329840,   # Admin ID
    987654321,   # Oshpaz ID
    111222333,   # Menejer ID
]

# ========== ROUTER ==========
router = Router()

# ========== HANDLERLAR ==========

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_WORKERS:
        await message.answer(
            "⛔ Sizga bu botdan foydalanish ruxsati yo'q.\n"
            "Menejer bilan bog'laning."
        )
        return

    await message.answer(
        f"👨‍🍳 Xush kelibsiz, <b>{message.from_user.first_name}</b>!\n\n"
        "🔔 <b>Ishchilar paneli</b>\n\n"
        "Bu bot orqali yangi buyurtmalarni ko'rasiz va qabul qilasiz.\n\n"
        "✅ Bot tayyor! Buyurtmalar kelishini kuting...",
        parse_mode="HTML"
    )

# --- Buyurtmani QABUL QILISH ---
@router.callback_query(F.data.startswith("accept_"))
async def accept_order(call: CallbackQuery):
    if call.from_user.id not in ALLOWED_WORKERS:
        await call.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return

    parts    = call.data.split("_")
    order_id = parts[1]
    user_id  = int(parts[2])
    worker   = call.from_user.full_name

    # Buyurtma xabarini yangilash
    original_text = call.message.text or call.message.caption or ""
    await call.message.edit_text(
        original_text + f"\n\n✅ <b>QABUL QILINDI</b>\n👷 Ishchi: {worker}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🚚 Yetkazildi deb belgilash",
                callback_data=f"delivered_{order_id}_{user_id}"
            )
        ]])
    )
    await call.answer("✅ Buyurtma qabul qilindi!", show_alert=True)

    # Mijozga xabar yuborish
    try:
        customer_bot = Bot(token=CUSTOMER_BOT_TOKEN)
        await customer_bot.send_message(
            user_id,
            f"✅ <b>Buyurtma #{order_id} qabul qilindi!</b>\n\n"
            f"👨‍🍳 Oshpaz tayyorlay boshladi.\n"
            f"🚗 Tez orada yetkazuvchi yo'lga chiqadi.\n\n"
            f"⏰ Taxminiy vaqt: <b>30-45 daqiqa</b>",
            parse_mode="HTML"
        )
        await customer_bot.session.close()
    except Exception as e:
        print(f"Mijozga xabar yuborishda xato: {e}")

# --- Buyurtmani RAD ETISH ---
@router.callback_query(F.data.startswith("reject_"))
async def reject_order(call: CallbackQuery):
    if call.from_user.id not in ALLOWED_WORKERS:
        await call.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return

    parts    = call.data.split("_")
    order_id = parts[1]
    user_id  = int(parts[2])
    worker   = call.from_user.full_name

    original_text = call.message.text or ""
    await call.message.edit_text(
        original_text + f"\n\n❌ <b>RAD ETILDI</b>\n👷 Ishchi: {worker}",
        parse_mode="HTML"
    )
    await call.answer("❌ Buyurtma rad etildi", show_alert=True)

    # Mijozga xabar yuborish
    try:
        customer_bot = Bot(token=CUSTOMER_BOT_TOKEN)
        await customer_bot.send_message(
            user_id,
            f"😔 <b>Buyurtma #{order_id} rad etildi.</b>\n\n"
            f"Kechirasiz, hozirda bu mahsulotni tayyorlay olmaymiz.\n"
            f"Boshqa taom tanlang yoki keyinroq urinib ko'ring.\n\n"
            f"📞 Muammo bo'lsa bog'laning: +998901234567",
            parse_mode="HTML"
        )
        await customer_bot.session.close()
    except Exception as e:
        print(f"Mijozga xabar yuborishda xato: {e}")

# --- Yetkazildi ---
@router.callback_query(F.data.startswith("delivered_"))
async def order_delivered(call: CallbackQuery):
    if call.from_user.id not in ALLOWED_WORKERS:
        await call.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return

    parts    = call.data.split("_")
    order_id = parts[1]
    user_id  = int(parts[2])
    worker   = call.from_user.full_name

    original_text = call.message.text or ""
    await call.message.edit_text(
        original_text + f"\n\n🚀 <b>YETKAZILDI</b>\n👷 {worker}",
        parse_mode="HTML"
    )
    await call.answer("🚀 Buyurtma yetkazildi deb belgilandi!", show_alert=True)

    # Mijozga xabar
    try:
        customer_bot = Bot(token=CUSTOMER_BOT_TOKEN)
        await customer_bot.send_message(
            user_id,
            f"🎉 <b>Buyurtma #{order_id} yetkazildi!</b>\n\n"
            f"Rahmat! Yana buyurtma bering 😊\n"
            f"Ishtaha bo'lsin! 🍽️",
            parse_mode="HTML"
        )
        await customer_bot.session.close()
    except Exception as e:
        print(f"Mijozga xabar yuborishda xato: {e}")

# ========== MAIN ==========
async def main():
    bot = Bot(token=WORKER_BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    print("✅ Ishchilar boti ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
