## Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random

lock = asyncio.Lock()

from pyrogram.errors.exceptions.bad_request_400 import (
    MediaEmpty,
    PhotoInvalidDimensions,
    WebpageMediaEmpty,
)
from Script import script
import pyrogram
from database.connections_mdb import (
    active_connection,
    all_connections,
    delete_connection,
    if_active,
    make_active,
    make_inactive,
)
from info import (
    ADMINS,
    AUTH_CHANNEL,
    AUTH_USERS,
    SUPPORT_CHAT_ID,
    CUSTOM_FILE_CAPTION,
    MSG_ALRT,
    PICS,
    AUTH_GROUPS,
    P_TTI_SHOW_OFF,
    GRP_LNK,
    CHNL_LNK,
    NOR_IMG,
    LOG_CHANNEL,
    SPELL_IMG,
    MAX_B_TN,
    IMDB,
    SINGLE_BUTTON,
    SPELL_CHECK_REPLY,
    IMDB_TEMPLATE,
    NO_RESULTS_MSG,
    IS_VERIFY,
    HOW_TO_VERIFY,
)
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
)
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import (
    get_size,
    is_subscribed,
    get_poster,
    search_gagala,
    temp,
    get_settings,
    save_group_settings,
    get_shortlink,
    send_all,
    check_verification,
    get_token,
)
from database.users_chats_db import db
from database.ia_filterdb import (
    Media,
    get_file_details,
    get_search_results,
    get_bad_files,
)
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logging.basicConfig(level=logging.DEBUG)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming)
# @Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        glob = await global_filters(client, message)
        if glob == False:
            manual = await manual_filters(client, message)
            if manual == False:
                settings = await get_settings(message.chat.id)
                try:
                    if settings["auto_ffilter"]:
                        await auto_filter(client, message)
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, "auto_ffilter", True)
                    settings = await get_settings(message.chat.id)
                    if settings["auto_ffilter"]:
                        await auto_filter(client, message)
    else:  # a better logic to avoid repeated lines of code in auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(
            chat_id=message.chat.id, query=search.lower(), offset=0, filter=True
        )
        if total_results == 0:
            return
        else:
            return await message.reply_text(
                text=f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>",
                parse_mode=enums.ParseMode.HTML,
            )


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"):
        return  # ignore commands and hashtags
    if user_id in ADMINS:
        return  # ignore admins
    await message.reply_text("<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴍʏ ᴍᴏᴅᴇʀᴀᴛᴏʀs !</b>")
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>",
    )


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(
            script.ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(
            script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
        return

    files, n_offset, total = await get_search_results(
        query.message.chat.id, search, offset=offset, filter=True
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    temp.SEND_ALL_TEMP[query.from_user.id] = files
    if "is_shortlink" in settings.keys():
        ENABLE_SHORTLINK = settings["is_shortlink"]
    else:
        await save_group_settings(query.message.chat.id, "is_shortlink", False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK and settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    url=await get_shortlink(
                        query.message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
            ]
            for file in files
        ]
    elif ENABLE_SHORTLINK and not settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    url=await get_shortlink(
                        query.message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(
                        query.message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
            ]
            for file in files
        ]
    elif settings["button"] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    callback_data=f"files#{file.file_id}",
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f"files#{file.file_id}"
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f"files_#{file.file_id}",
                ),
            ]
            for file in files
        ]
    """try:
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )            
    except KeyError:
        await save_group_settings(query.message.chat.id, 'auto_delete', True)
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
            ]
        )"""
    try:
        if settings["max_btn"]:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                        ),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                            callback_data="pages",
                        ),
                    ]
                )
            elif off_set is None:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                        ),
                    ]
                )
            else:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                        ),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                        ),
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                        ),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}",
                            callback_data="pages",
                        ),
                    ]
                )
            elif off_set is None:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                        ),
                    ]
                )
            else:
                btn.append(
                    [
                        InlineKeyboardButton(
                            "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                        ),
                        InlineKeyboardButton(
                            f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                        ),
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, "max_btn", True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [
                    InlineKeyboardButton(
                        "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                    ),
                    InlineKeyboardButton(
                        f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                        callback_data="pages",
                    ),
                ]
            )
        elif off_set is None:
            btn.append(
                [
                    InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                    InlineKeyboardButton(
                        f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                        callback_data="pages",
                    ),
                    InlineKeyboardButton(
                        "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                    ),
                ]
            )
        else:
            btn.append(
                [
                    InlineKeyboardButton(
                        "⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"
                    ),
                    InlineKeyboardButton(
                        f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}",
                        callback_data="pages",
                    ),
                    InlineKeyboardButton(
                        "𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}"
                    ),
                ],
            )
    btn.insert(
        0,
        [
            InlineKeyboardButton(
                "! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"send_fall#files#{offset}#{req}"
            ),
            InlineKeyboardButton("! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{req}"),
        ],
    )
    btn.insert(
        0, [InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")]
    )
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    _, userid, language = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(
            script.ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    if language == "unknown":
        return await query.answer(
            "Sᴇʟᴇᴄᴛ ᴀɴʏ ʟᴀɴɢᴜᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs !", show_alert=True
        )
    movie = temp.KEYWORD.get(query.from_user.id)
    if not movie:
        return await query.answer(
            script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    if language != "home":
        movie = f"{movie} {language}"
    files, offset, total_results = await get_search_results(
        query.message.chat.id, movie, offset=0, filter=True
    )
    if files:
        settings = await get_settings(query.message.chat.id)
        temp.SEND_ALL_TEMP[query.from_user.id] = files
        if "is_shortlink" in settings.keys():
            ENABLE_SHORTLINK = settings["is_shortlink"]
        else:
            await save_group_settings(query.message.chat.id, "is_shortlink", False)
            ENABLE_SHORTLINK = False
        pre = "filep" if settings["file_secure"] else "file"
        if ENABLE_SHORTLINK and settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}",
                        url=await get_shortlink(
                            query.message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
        elif ENABLE_SHORTLINK and not settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(
                            query.message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(
                            query.message.chat.id,
                            f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                        ),
                    ),
                ]
                for file in files
            ]
        elif settings["button"] and not ENABLE_SHORTLINK:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}",
                        callback_data=f"{pre}#{file.file_id}",
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f"{pre}#{file.file_id}",
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f"{pre}#{file.file_id}",
                    ),
                ]
                for file in files
            ]

        """try:
            if settings['auto_delete']:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                        InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                        InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                    ]
                )

            else:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                        InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                    ]
                )
                    
        except KeyError:
            await save_group_settings(query.message.chat.id, 'auto_delete', True)
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )"""

        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    "! Sᴇɴᴅ Aʟʟ Tᴏ PM !", callback_data=f"send_fall#{pre}#{0}#{userid}"
                ),
                InlineKeyboardButton(
                    "! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{userid}"
                ),
            ],
        )

        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    "⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}"
                )
            ],
        )

        if offset != "":
            key = f"{query.message.chat.id}-{query.message.id}"
            BUTTONS[key] = movie
            req = userid
            try:
                if settings["max_btn"]:
                    btn.append(
                        [
                            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                            InlineKeyboardButton(
                                text=f"1/{math.ceil(int(total_results)/10)}",
                                callback_data="pages",
                            ),
                            InlineKeyboardButton(
                                text="𝐍𝐄𝐗𝐓 ➪",
                                callback_data=f"next_{req}_{key}_{offset}",
                            ),
                        ]
                    )

                else:
                    btn.append(
                        [
                            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                            InlineKeyboardButton(
                                text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",
                                callback_data="pages",
                            ),
                            InlineKeyboardButton(
                                text="𝐍𝐄𝐗𝐓 ➪",
                                callback_data=f"next_{req}_{key}_{offset}",
                            ),
                        ]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, "max_btn", True)
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(
                            text=f"1/{math.ceil(int(total_results)/10)}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}"
                        ),
                    ]
                )
        else:
            btn.append(
                [
                    InlineKeyboardButton(
                        text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄", callback_data="pages"
                    )
                ]
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()
    else:
        return await query.answer(
            f"Sᴏʀʀʏ, Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {movie}.", show_alert=True
        )


@Client.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    _, userid = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(
            script.ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    btn = [
        [
            InlineKeyboardButton(
                "Sᴇʟᴇᴄᴛ Yᴏᴜʀ Dᴇꜱɪʀᴇᴅ Lᴀɴɢᴜᴀɢᴇ ↓", callback_data=f"lang#{userid}#unknown"
            )
        ],
        [
            InlineKeyboardButton("Eɴɢʟɪꜱʜ", callback_data=f"lang#{userid}#eng"),
            InlineKeyboardButton("Tᴀᴍɪʟ", callback_data=f"lang#{userid}#tam"),
            InlineKeyboardButton("Hɪɴᴅɪ", callback_data=f"lang#{userid}#hin"),
        ],
        [
            InlineKeyboardButton("Kᴀɴɴᴀᴅᴀ", callback_data=f"lang#{userid}#kan"),
            InlineKeyboardButton("Tᴇʟᴜɢᴜ", callback_data=f"lang#{userid}#tel"),
        ],
        [InlineKeyboardButton("Mᴀʟᴀʏᴀʟᴀᴍ", callback_data=f"lang#{userid}#mal")],
        [
            InlineKeyboardButton("Mᴜʟᴛɪ Aᴜᴅɪᴏ", callback_data=f"lang#{userid}#multi"),
            InlineKeyboardButton("Dᴜᴀʟ Aᴜᴅɪᴏ", callback_data=f"lang#{userid}#dual"),
        ],
        [InlineKeyboardButton("Gᴏ Bᴀᴄᴋ", callback_data=f"lang#{userid}#home")],
    ]
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split("#")
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(
            script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(
            script.ALRT_TXT.format(query.from_user.first_name), show_alert=True
        )
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(
                query.message.chat.id, movie, offset=0, filter=True
            )
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(
                        chat_id=LOG_CHANNEL,
                        text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)),
                    )
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, "gfilters")
        await query.answer("Dᴏɴᴇ !")
        return
    elif query.data == "gfiltersdeleteallcancel":
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Pʀᴏᴄᴇss Cᴀɴᴄᴇʟʟᴇᴅ !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text(
                        "Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True
                    )
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs!\nCʜᴇᴄᴋ /connections ᴏʀ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs",
                    quote=True,
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer(
                "Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ Gʀᴏᴜᴘ Oᴡɴᴇʀ ᴏʀ ᴀɴ Aᴜᴛʜ Usᴇʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!",
                show_alert=True,
            )
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ's ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
                    InlineKeyboardButton(
                        "DELETE", callback_data=f"deletecb:{group_id}"
                    ),
                ],
                [InlineKeyboardButton("BACK", callback_data="backcb")],
            ]
        )

        await query.message.edit_text(
            f"Gʀᴏᴜᴘ Nᴀᴍᴇ : **{title}**\nGʀᴏᴜᴘ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**", parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                "Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!", parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ **{title}**", parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!", parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text("Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ !")
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!", parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs!! Cᴏɴɴᴇᴄᴛ ᴛᴏ sᴏᴍᴇ ɢʀᴏᴜᴘs ғɪʀsᴛ.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}",
                            callback_data=f"groupcb:{groupid}:{act}",
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Yᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter("gfilters", keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer("Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.")
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name="" if title is None else title,
                    file_size="" if size is None else size,
                    file_caption="" if f_caption is None else f_caption,
                )
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(
                        url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
                    )
                    return
                else:
                    await query.answer(
                        f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !",
                        show_alert=True,
                    )
            elif settings["botpm"]:
                if clicked == typed:
                    await query.answer(
                        url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
                    )
                    return
                else:
                    await query.answer(
                        f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !",
                        show_alert=True,
                    )
            else:
                if clicked == typed:
                    if IS_VERIFY and not await check_verification(
                        client, query.from_user.id
                    ):
                        btn = [
                            [
                                InlineKeyboardButton(
                                    "download link",
                                    url=await get_token(
                                        client,
                                        query.from_user.id,
                                        f"https://telegram.me/{temp.U_NAME}?start=",
                                        file_id,
                                    ),
                                ),
                                InlineKeyboardButton(
                                    "sample video",
                                    url=await get_token(
                                        client,
                                        query.from_user.id,
                                        f"https://telegram.me/{temp.U_NAME}?start=",
                                        file_id,
                                    ),
                                ),
                            ]
                        ]
                        await client.send_message(
                            chat_id=query.from_user.id,
                            text="""<b>click "download link" to download full movie\n! click "sample video" to view 1 min sample</b>""",
                            protect_content=True if ident == "checksubp" else False,
                            disable_web_page_preview=True,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(btn),
                        )
                        return await query.answer(
                            "Hᴇʏ,download link send successfully to you. Cʜᴇᴄᴋ ᴍʏ PM ᴛᴏ ɢᴇᴛ ғɪʟᴇs!",
                            show_alert=True,
                        )
                    else:
                        await client.send_cached_media(
                            chat_id=query.from_user.id,
                            file_id=file_id,
                            caption=f_caption,
                            protect_content=True if ident == "filep" else False,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        # InlineKeyboardButton('sᴇᴀʀᴄʜ Gʀᴏᴜᴘ', url=GRP_LNK),
                                        InlineKeyboardButton(
                                            "🔰  ᴍᴀɪɴ ʜᴀɴɴᴇʟ  🔰", url=CHNL_LNK
                                        )
                                    ],
                                    [
                                        InlineKeyboardButton(
                                            "⚜️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ 🔱",
                                            url="https://t.me/vip_sender",
                                        )
                                    ],
                                ]
                            ),
                        )
                        return await query.answer(
                            "Cʜᴇᴄᴋ PM, I ʜᴀᴠᴇ sᴇɴᴛ ғɪʟᴇs ɪɴ PM", show_alert=True
                        )
                else:
                    return await query.answer(
                        f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !",
                        show_alert=True,
                    )
        except UserIsBlocked:
            await query.answer("Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !", show_alert=True)
        except PeerIdInvalid:
            await query.answer(
                url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
            )
        except Exception as e:
            await query.answer(
                url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}"
            )
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Jᴏɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        if file_id == "send_all":
            send_files = temp.SEND_ALL_TEMP.get(query.from_user.id)
            is_over = await send_all(client, query.from_user.id, send_files, ident)
            if is_over == "done":
                return await query.answer(
                    f"Hᴇʏ {query.from_user.first_name}, Aʟʟ ғɪʟᴇs ᴏɴ ᴛʜɪs ᴘᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ ʏᴏᴜʀ PM !",
                    show_alert=True,
                )
            elif is_over == "fsub":
                return await query.answer(
                    "Hᴇʏ, Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ʙᴀᴄᴋ ᴜᴘ ᴄʜᴀɴɴᴇʟ. Cʜᴇᴄᴋ ᴍʏ PM ᴛᴏ ᴊᴏɪɴ ᴀɴᴅ ɢᴇᴛ ғɪʟᴇs !",
                    show_alert=True,
                )
            elif is_over == "verify":
                return await query.answer(
                    "Hᴇʏ, Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴅᴀʏ. Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ. Cʜᴇᴄᴋ ᴍʏ PM ᴛᴏ ᴠᴇʀɪғʏ ᴀɴᴅ ɢᴇᴛ ғɪʟᴇs !",
                    show_alert=True,
                )
            else:
                return await query.answer(f"Eʀʀᴏʀ: {is_over}", show_alert=True)
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer("Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.")
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name="" if title is None else title,
                    file_size="" if size is None else size,
                    file_caption="" if f_caption is None else f_caption,
                )
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        if IS_VERIFY and not await check_verification(client, query.from_user.id):
            btn = [
                [
                    InlineKeyboardButton(
                        "download link",
                        url=await get_token(
                            client,
                            query.from_user.id,
                            f"https://telegram.me/{temp.U_NAME}?start=",
                            file_id,
                        ),
                    ),
                    InlineKeyboardButton(
                        "sample video",
                        url=await get_token(
                            client,
                            query.from_user.id,
                            f"https://telegram.me/{temp.U_NAME}?start=",
                            file_id,
                        ),
                    ),
                ]
            ]
            await client.send_message(
                chat_id=query.from_user.id,
                text="""<b>click "download link" to download full movie\n! click "sample video" to view 1 min sample</b>""",
                protect_content=True if ident == "checksubp" else False,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btn),
            )
            return
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == "checksubp" else False,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        # InlineKeyboardButton('sᴇᴀʀᴄʜ Gʀᴏᴜᴘ', url=GRP_LNK),
                        InlineKeyboardButton("🔰  ᴍᴀɪɴ ʜᴀɴɴᴇʟ  🔰", url=CHNL_LNK)
                    ],
                    [
                        InlineKeyboardButton(
                            "⚜️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ 🔱", url="https://t.me/vip_sender"
                        )
                    ],
                ]
            ),
        )
    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("send_fall"):
        temp_var, ident, offset, userid = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(
                script.ALRT_TXT.format(query.from_user.first_name), show_alert=True
            )
        files = temp.SEND_ALL_TEMP.get(query.from_user.id)
        is_over = await send_all(client, query.from_user.id, files, ident)
        if is_over == "done":
            return await query.answer(
                f"Hᴇʏ {query.from_user.first_name}, Aʟʟ ғɪʟᴇs ᴏɴ ᴛʜɪs ᴘᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ ʏᴏᴜʀ PM !",
                show_alert=True,
            )
        elif is_over == "fsub":
            return await query.answer(
                "Hᴇʏ, Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ɪɴ ᴍʏ ʙᴀᴄᴋ ᴜᴘ ᴄʜᴀɴɴᴇʟ. Cʜᴇᴄᴋ ᴍʏ PM ᴛᴏ ᴊᴏɪɴ ᴀɴᴅ ɢᴇᴛ ғɪʟᴇs !",
                show_alert=True,
            )
        elif is_over == "verify":
            return await query.answer(
                "Hᴇʏ, Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴅᴀʏ. Yᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ. Cʜᴇᴄᴋ ᴍʏ PM ᴛᴏ ᴠᴇʀɪғʏ ᴀɴᴅ ɢᴇᴛ ғɪʟᴇs !",
                show_alert=True,
            )
        else:
            return await query.answer(f"Eʀʀᴏʀ: {is_over}", show_alert=True)

    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(
            f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>"
        )
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(
            f"<b>Fᴏᴜɴᴅ {total} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>"
        )
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one(
                        {
                            "_id": file_ids,
                        }
                    )
                    if result.deleted_count:
                        logger.info(
                            f"Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ."
                        )
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(
                            f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>"
                        )
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f"Eʀʀᴏʀ: {e}")
            else:
                await query.message.edit_text(
                    f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>"
                )
    elif query.data.startswith("killfilesvip_sender"):
        ident, pattern = query.data.split("#")
        await query.message.edit_text(
            f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ `sᴇʀɪᴇs ғɪʟᴇs` ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>"
        )
        files, total = await get_files_by_series(pattern)
        await query.message.edit_text(
            f"<b>Fᴏᴜɴᴅ {total} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ `sᴇʀɪᴇs ғɪʟᴇs` !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>"
        )
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                for file in files:
                    file_id = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({"_id": file_id})
                    if result.deleted_count:
                        logger.info(
                            f"Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ `sᴇʀɪᴇs ғɪʟᴇs`! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ."
                        )
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(
                            f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ `sᴇʀɪᴇs ғɪʟᴇs` !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>"
                        )
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f"Eʀʀᴏʀ: {e}")
            else:
                await query.message.edit_text(
                    f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ `sᴇʀɪᴇs ғɪʟᴇs`.</b>"
                )

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer(
                "Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True
            )
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Sɪɴɢʟᴇ" if settings["button"] else "Dᴏᴜʙʟᴇ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ" if settings["botpm"] else "Aᴜᴛᴏ Sᴇɴᴅ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["file_secure"] else "✘ Oғғ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Iᴍᴅʙ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["imdb"] else "✘ Oғғ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Sᴘᴇʟʟ Cʜᴇᴄᴋ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["spell_check"] else "✘ Oғғ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Wᴇʟᴄᴏᴍᴇ Msɢ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["welcome"] else "✘ Oғғ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10 Mɪɴs" if settings["auto_delete"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Fɪʟᴛᴇʀ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["auto_ffilter"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Mᴀx Bᴜᴛᴛᴏɴs",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10" if settings["max_btn"] else f"{MAX_B_TN}",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "SʜᴏʀᴛLɪɴᴋ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["is_shortlink"] else "✘ Oғғ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
            )
            await query.message.edit_reply_markup(reply_markup)

    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer(
                "Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True
            )
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(
            f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>"
        )
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Sɪɴɢʟᴇ" if settings["button"] else "Dᴏᴜʙʟᴇ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ" if settings["botpm"] else "Aᴜᴛᴏ Sᴇɴᴅ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["file_secure"] else "✘ Oғғ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Iᴍᴅʙ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["imdb"] else "✘ Oғғ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Sᴘᴇʟʟ Cʜᴇᴄᴋ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["spell_check"] else "✘ Oғғ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Wᴇʟᴄᴏᴍᴇ Msɢ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["welcome"] else "✘ Oғғ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10 Mɪɴs" if settings["auto_delete"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Fɪʟᴛᴇʀ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["auto_ffilter"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Mᴀx Bᴜᴛᴛᴏɴs",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10" if settings["max_btn"] else f"{MAX_B_TN}",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "SʜᴏʀᴛLɪɴᴋ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["is_shortlink"] else "✘ Oғғ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id,
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton(
                    "Uɴᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"unavailable#{from_user}"
                ),
                InlineKeyboardButton("Uᴘʟᴏᴀᴅᴇᴅ", callback_data=f"uploaded#{from_user}"),
            ],
            [
                InlineKeyboardButton(
                    "Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ", callback_data=f"already_available#{from_user}"
                )
            ],
        ]
        btn2 = [[InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton(
                    "⚠️ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}"
                )
            ]
        ]
        btn2 = [[InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [
            [InlineKeyboardButton("✅ Uᴘʟᴏᴀᴅᴇᴅ ✅", callback_data=f"upalert#{from_user}")]
        ]
        btn2 = [[InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton(
                    "🟢 Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ 🟢", callback_data=f"alalert#{from_user}"
                )
            ]
        ]
        btn2 = [[InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2),
                )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !",
                show_alert=True,
            )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True
            )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(
                f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !",
                show_alert=True,
            )
        else:
            await query.answer(
                "Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True
            )

    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)

    elif query.data == "minfo":
        await query.answer(text=script.MINFO, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        buttons =[[
                    InlineKeyboardButton('Search Any Movie Here ▶', switch_inline_query_current_chat='')
                ],[
                    InlineKeyboardButton('➢ Hindi Movies ', callback_data='help')
                ],[
                     InlineKeyboardButton('➣ Kannada Movies', callback_data="kannada")
                ],[
                    InlineKeyboardButton('⤬ Aᴅᴅ Tᴏ Yᴏᴜʀ Own Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.START_TXT.format(
                query.from_user.mention, temp.U_NAME, temp.B_NAME
            ),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
        await query.answer(MSG_ALRT)

    elif query.data == "best0":
        buttons = [
            [
                InlineKeyboardButton("best hindi movies", callback_data="best1"),
                InlineKeyboardButton("Aᴜᴛᴏ FIʟᴛᴇʀ", callback_data="autofilter"),
            ],
            [
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
                InlineKeyboardButton("Gʟᴏʙᴀʟ Fɪʟᴛᴇʀs", callback_data="global_filters"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    #this is my
    elif query.data == "best1":
        buttons = [
[
    InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")
],
[
    InlineKeyboardButton('Sholay (1975)', switch_inline_query_current_chat='Sholay (1975)')
],
[
    InlineKeyboardButton('Mughal-e-Azam (1960)', switch_inline_query_current_chat='Mughal-e-Azam (1960)')
],
[
    InlineKeyboardButton('Dilwale Dulhania Le Jayenge (1995)', switch_inline_query_current_chat='Dilwale Dulhania Le Jayenge (1995)')
],
[
    InlineKeyboardButton('Mother India (1957)', switch_inline_query_current_chat='Mother India (1957)')
],
[
    InlineKeyboardButton('Lagaan (2001)', switch_inline_query_current_chat='Lagaan (2001)')
],
[
    InlineKeyboardButton('Rang De Basanti (2006)', switch_inline_query_current_chat='Rang De Basanti (2006)'),
],
[
    InlineKeyboardButton('Kabhi Kabhie (1976)', switch_inline_query_current_chat='Kabhi Kabhie (1976)'),
],
[
    InlineKeyboardButton('Kuch Kuch Hota Hai (1998)', switch_inline_query_current_chat='Kuch Kuch Hota Hai (1998)'),
],
[
    InlineKeyboardButton('Zindagi Na Milegi Dobara (2011)', switch_inline_query_current_chat='Zindagi Na Milegi Dobara (2011)'),
],
[
    InlineKeyboardButton('Pakeezah (1972)', switch_inline_query_current_chat='Pakeezah (1972)'),
],[
    InlineKeyboardButton('Sholay (1975)', switch_inline_query_current_chat='Sholay (1975)'),
],
[
    InlineKeyboardButton('Mughal-e-Azam (1960)', switch_inline_query_current_chat='Mughal-e-Azam (1960)'),
],
[
    InlineKeyboardButton('Dilwale Dulhania Le Jayenge (1995)', switch_inline_query_current_chat='Dilwale Dulhania Le Jayenge (1995)'),
],
[
    InlineKeyboardButton('Mother India (1957)', switch_inline_query_current_chat='Mother India (1957)'),
],
[
    InlineKeyboardButton('Lagaan (2001)', switch_inline_query_current_chat='Lagaan (2001)'),
],
[
    InlineKeyboardButton('Rang De Basanti (2006)', switch_inline_query_current_chat='Rang De Basanti (2006)'),
],
[
    InlineKeyboardButton('Kabhi Kabhie (1976)', switch_inline_query_current_chat='Kabhi Kabhie (1976)'),
],
[
    InlineKeyboardButton('Kuch Kuch Hota Hai (1998)', switch_inline_query_current_chat='Kuch Kuch Hota Hai (1998)'),
],
[
    InlineKeyboardButton('Zindagi Na Milegi Dobara (2011)', switch_inline_query_current_chat='Zindagi Na Milegi Dobara (2011)'),
],
[
    InlineKeyboardButton('Pakeezah (1972)', switch_inline_query_current_chat='Pakeezah (1972)'),
],
[
    InlineKeyboardButton('Anand (1971)', switch_inline_query_current_chat='Anand (1971)'),
],
[
    InlineKeyboardButton('Shree 420 (1955)', switch_inline_query_current_chat='Shree 420 (1955)'),
],
[
    InlineKeyboardButton('Queen (2014)', switch_inline_query_current_chat='Queen (2014)'),
],
[
    InlineKeyboardButton('Mera Naam Joker (1970)', switch_inline_query_current_chat='Mera Naam Joker (1970)'),
],
[
    InlineKeyboardButton('Black (2005)', switch_inline_query_current_chat='Black (2005)'),
],
[
    InlineKeyboardButton('Taare Zameen Par (2007)', switch_inline_query_current_chat='Taare Zameen Par (2007)'),
],
[
    InlineKeyboardButton('Shree 420 (1955)', switch_inline_query_current_chat='Shree 420 (1955)'),
],
[
    InlineKeyboardButton('Devdas (2002)', switch_inline_query_current_chat='Devdas (2002)'),
],
[
    InlineKeyboardButton('3 Idiots (2009)', switch_inline_query_current_chat='3 Idiots (2009)'),
],
[
    InlineKeyboardButton('PK (2014)', switch_inline_query_current_chat='PK (2014)'),
],
[
    InlineKeyboardButton('Chupke Chupke (1975)', switch_inline_query_current_chat='Chupke Chupke (1975)'),
],
[
    InlineKeyboardButton('Dil Chahta Hai (2001)', switch_inline_query_current_chat='Dil Chahta Hai (2001)'),
],
[
    InlineKeyboardButton('Anupama (1966)', switch_inline_query_current_chat='Anupama (1966)'),
],
[
    InlineKeyboardButton('Udaan (2010)', switch_inline_query_current_chat='Udaan (2010)'),
],
[
    InlineKeyboardButton('Bajrangi Bhaijaan (2015)', switch_inline_query_current_chat='Bajrangi Bhaijaan (2015)'),
],
[
    InlineKeyboardButton('My Name Is Khan (2010)', switch_inline_query_current_chat='My Name Is Khan (2010)'),
],
[
    InlineKeyboardButton('Raja Hindustani (1996)', switch_inline_query_current_chat='Raja Hindustani (1996)'),
],
[
    InlineKeyboardButton('Dil To Pagal Hai (1997)', switch_inline_query_current_chat='Dil To Pagal Hai (1997)'),
],
[
    InlineKeyboardButton('Jo Jeeta Wohi Sikandar (1992)', switch_inline_query_current_chat='Jo Jeeta Wohi Sikandar (1992)'),
],
[
    InlineKeyboardButton('Piku (2015)', switch_inline_query_current_chat='Piku (2015)'),
],
[
    InlineKeyboardButton('Rocket Singh: Salesman of the Year (2009)', switch_inline_query_current_chat='Rocket Singh: Salesman of the Year (2009)'),
],
[
    InlineKeyboardButton('Special 26 (2013)', switch_inline_query_current_chat='Special 26 (2013)'),
],
[
    InlineKeyboardButton('Dilwale (2015)', switch_inline_query_current_chat='Dilwale (2015)'),
],
[
    InlineKeyboardButton('Tumhari Sulu (2017)', switch_inline_query_current_chat='Tumhari Sulu (2017)'),
],[
    InlineKeyboardButton('Kabhi Khushi Kabhie Gham (2001)', switch_inline_query_current_chat='Kabhi Khushi Kabhie Gham (2001)'),
],
[
    InlineKeyboardButton('Satyam Shivam Sundaram (1978)', switch_inline_query_current_chat='Satyam Shivam Sundaram (1978)'),
],
[
    InlineKeyboardButton('Dil Dhadakne Do (2015)', switch_inline_query_current_chat='Dil Dhadakne Do (2015)'),
],
[
    InlineKeyboardButton('Dabangg (2010)', switch_inline_query_current_chat='Dabangg (2010)'),
],
[
    InlineKeyboardButton('Ghajini (2008)', switch_inline_query_current_chat='Ghajini (2008)'),
],
[
    InlineKeyboardButton('Kaagaz Ke Phool (1959)', switch_inline_query_current_chat='Kaagaz Ke Phool (1959)'),
],
[
    InlineKeyboardButton('Hum Aapke Hain Koun..! (1994)', switch_inline_query_current_chat='Hum Aapke Hain Koun..! (1994)'),
],
[
    InlineKeyboardButton('Wake Up Sid (2009)', switch_inline_query_current_chat='Wake Up Sid (2009)'),
],
[
    InlineKeyboardButton('Munna Bhai M.B.B.S. (2003)', switch_inline_query_current_chat='Munna Bhai M.B.B.S. (2003)'),
],
[
    InlineKeyboardButton('Piku (2015)', switch_inline_query_current_chat='Piku (2015)'),
],
[
    InlineKeyboardButton('Chupke Chupke (1975)', switch_inline_query_current_chat='Chupke Chupke (1975)'),
],
[
    InlineKeyboardButton('Dilwale (2015)', switch_inline_query_current_chat='Dilwale (2015)'),
],
[
    InlineKeyboardButton('Deewaar (1975)', switch_inline_query_current_chat='Deewaar (1975)'),
],
[
    InlineKeyboardButton('Jo Jeeta Wohi Sikandar (1992)', switch_inline_query_current_chat='Jo Jeeta Wohi Sikandar (1992)'),
],
[
    InlineKeyboardButton('Mohenjo Daro (2016)', switch_inline_query_current_chat='Mohenjo Daro (2016)'),
],
[
    InlineKeyboardButton('Guddi (1971)', switch_inline_query_current_chat='Guddi (1971)'),
],
[
    InlineKeyboardButton('Kabhi Alvida Naa Kehna (2006)', switch_inline_query_current_chat='Kabhi Alvida Naa Kehna (2006)'),
],
[
    InlineKeyboardButton('Pardes (1997)', switch_inline_query_current_chat='Pardes (1997)'),
],
[
    InlineKeyboardButton('Udta Punjab (2016)', switch_inline_query_current_chat='Udta Punjab (2016)'),
],
[
    InlineKeyboardButton('Koi Mil Gaya (2003)', switch_inline_query_current_chat='Koi Mil Gaya (2003)'),
],
[
    InlineKeyboardButton('Tumhari Sulu (2017)', switch_inline_query_current_chat='Tumhari Sulu (2017)'),
],
[
    InlineKeyboardButton('Queen (2014)', switch_inline_query_current_chat='Queen (2014)'),
],
[
    InlineKeyboardButton('Dhoom (2004)', switch_inline_query_current_chat='Dhoom (2004)'),
],
[
    InlineKeyboardButton('Rockstar (2011)', switch_inline_query_current_chat='Rockstar (2011)'),
],
[
    InlineKeyboardButton('Tum Bin (2001)', switch_inline_query_current_chat='Tum Bin (2001)'),
],
[
    InlineKeyboardButton('Zubeidaa (2001)', switch_inline_query_current_chat='Zubeidaa (2001)'),
],
[
    InlineKeyboardButton('Lage Raho Munna Bhai (2006)', switch_inline_query_current_chat='Lage Raho Munna Bhai (2006)'),
],
[
    InlineKeyboardButton('Dhoom 2 (2006)', switch_inline_query_current_chat='Dhoom 2 (2006)'),
],
[
    InlineKeyboardButton('Devdas (2002)', switch_inline_query_current_chat='Devdas (2002)'),
],
[
    InlineKeyboardButton('Hum Dil De Chuke Sanam (1999)', switch_inline_query_current_chat='Hum Dil De Chuke Sanam (1999)'),
],
[
    InlineKeyboardButton('Pink (2016)', switch_inline_query_current_chat='Pink (2016)'),
],
[
    InlineKeyboardButton('Kabhi Haan Kabhi Naa (1994)', switch_inline_query_current_chat='Kabhi Haan Kabhi Naa (1994)'),
],
[
    InlineKeyboardButton('Bombay (1995)', switch_inline_query_current_chat='Bombay (1995)'),
],
[
    InlineKeyboardButton('Bombay Velvet (2015)', switch_inline_query_current_chat='Bombay Velvet (2015)'),
],
[
    InlineKeyboardButton('Chak De! India (2007)', switch_inline_query_current_chat='Chak De! India (2007)'),
],
[
    InlineKeyboardButton('Dil Se.. (1998)', switch_inline_query_current_chat='Dil Se.. (1998)'),
],
[
    InlineKeyboardButton('Dilwale (2015)', switch_inline_query_current_chat='Dilwale (2015)'),
],
[
    InlineKeyboardButton('Darr (1993)', switch_inline_query_current_chat='Darr (1993)'),
],
[
    InlineKeyboardButton('Dosti (1964)', switch_inline_query_current_chat='Dosti (1964)'),
],
[
    InlineKeyboardButton('Fanaa (2006)', switch_inline_query_current_chat='Fanaa (2006)'),
],
[
    InlineKeyboardButton('Ganga Jamuna (1961)', switch_inline_query_current_chat='Ganga Jamuna (1961)'),
],
[
    InlineKeyboardButton('Golmaal: Fun Unlimited (2006)', switch_inline_query_current_chat='Golmaal: Fun Unlimited (2006)'),
],
[
    InlineKeyboardButton('Hey Ram (2000)', switch_inline_query_current_chat='Hey Ram (2000)'),
],
[
    InlineKeyboardButton('Kabhi Alvida Naa Kehna (2006)', switch_inline_query_current_chat='Kabhi Alvida Naa Kehna (2006)'),
],
[
    InlineKeyboardButton('Khamoshi: The Musical (1996)', switch_inline_query_current_chat='Khamoshi: The Musical (1996)'),
],
[
    InlineKeyboardButton('Kurbaan (1991)', switch_inline_query_current_chat='Kurbaan (1991)'),
],
[
    InlineKeyboardButton('Lamhe (1991)', switch_inline_query_current_chat='Lamhe (1991)'),
],
[
    InlineKeyboardButton('Lajja (2001)', switch_inline_query_current_chat='Lajja (2001)'),
],
[
    InlineKeyboardButton('Mary Kom (2014)', switch_inline_query_current_chat='Mary Kom (2014)'),
],
[
    InlineKeyboardButton('Rang De Basanti (2006)', switch_inline_query_current_chat='Rang De Basanti (2006)'),
],
[
    InlineKeyboardButton('Sarfarosh (1999)', switch_inline_query_current_chat='Sarfarosh (1999)'),
],
[
    InlineKeyboardButton('Udaan (2010)', switch_inline_query_current_chat='Udaan (2010)'),
],
[
    InlineKeyboardButton('Wake Up Sid (2009)', switch_inline_query_current_chat='Wake Up Sid (2009)'),
],
[
    InlineKeyboardButton('Omkara (2006)', switch_inline_query_current_chat='Omkara (2006)'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
                InlineKeyboardButton("Gʟᴏʙᴀʟ Fɪʟᴛᴇʀs", callback_data="global_filters"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
#end my

    elif query.data == "global_filters":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="filters")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton("best hindi movies", callback_data="best1")
            ],
            [
                InlineKeyboardButton("Hero List", callback_data="herolist")
            ],[
                InlineKeyboardButton(" categories-type", callback_data="type0")
            ],
            [
                InlineKeyboardButton("Hᴏᴍᴇ", callback_data="start")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(text="◌ ◌ ◌")
        await asyncio.sleep(0.3)
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await asyncio.sleep(0.2)
        await query.message.edit_text(text="● ● ●")
        await asyncio.sleep(0.3)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ", url=GRP_LNK),
                InlineKeyboardButton("Sᴏᴜʀᴄᴇ Cᴏᴅᴇ", callback_data="source"),
            ],
            [
                InlineKeyboardButton("Hᴏᴍᴇ", callback_data="start"),
                InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close_data"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(text="◌ ◌ ◌")
        await asyncio.sleep(0.3)
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await asyncio.sleep(0.3)
        await query.message.edit_text(text="● ● ●")
        await asyncio.sleep(0.2)

        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "source":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="about")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "manuelfilter":
        buttons = [
            [
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="filters"),
                InlineKeyboardButton("Bᴜᴛᴛᴏɴs", callback_data="button"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "button":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="manuelfilter")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "autofilter":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="filters")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "herolist":
        buttons = [ [
                InlineKeyboardButton("Shah Rukh Khan", callback_data="srk"),
                InlineKeyboardButton("Salman Khan", callback_data="SalmanKhan")
            ], [
                InlineKeyboardButton("Aamir Khan", callback_data="AamirKhan"),
                InlineKeyboardButton("Ranveer Singh", callback_data="RanveerSingh")
            ],[
                InlineKeyboardButton("Akshay Kumar", callback_data="AkshayKumar"),
                InlineKeyboardButton("Ranbir Kapoor", callback_data="RanbirKapoor")
            ],[
                InlineKeyboardButton("Hrithik Roshan", callback_data="HrithikRoshan"),
                InlineKeyboardButton("Ajay Devgn", callback_data="AjayDevgn")
            ],
            [
                InlineKeyboardButton("Hᴏᴍᴇ", callback_data="start"),
                InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close_data")
            ],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
        #im add startme
    elif query.data == "Thrillerk":
        buttons = [ [
    InlineKeyboardButton('RangiTaranga', switch_inline_query_current_chat='RangiTaranga'),
    InlineKeyboardButton('U-Turn', switch_inline_query_current_chat='U-Turn'),
],
[
    InlineKeyboardButton('Lucia', switch_inline_query_current_chat='Lucia'),
    InlineKeyboardButton('Kavaludaari', switch_inline_query_current_chat='Kavaludaari'),
],
[
    InlineKeyboardButton('Game', switch_inline_query_current_chat='Game'),
    InlineKeyboardButton('Aa Karaala Ratri', switch_inline_query_current_chat='Aa Karaala Ratri'),
],
[
    InlineKeyboardButton('Last Bus', switch_inline_query_current_chat='Last Bus'),
    InlineKeyboardButton('Gultoo', switch_inline_query_current_chat='Gultoo'),
],
[
    InlineKeyboardButton('Katheyondu Shuruvagide', switch_inline_query_current_chat='Katheyondu Shuruvagide'),
    InlineKeyboardButton('Rajathandira', switch_inline_query_current_chat='Rajathandira'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Horrork":
        buttons = [ [
    InlineKeyboardButton('Aake', switch_inline_query_current_chat='Aake'),
    InlineKeyboardButton('Karva', switch_inline_query_current_chat='Karva'),
],
[
    InlineKeyboardButton('Mummy - Save Me', switch_inline_query_current_chat='Mummy - Save Me'),
    InlineKeyboardButton('Raate', switch_inline_query_current_chat='Raate'),
],
[
    InlineKeyboardButton('U-Turn', switch_inline_query_current_chat='U-Turn'),
    InlineKeyboardButton('Rajkumari', switch_inline_query_current_chat='Rajkumari'),
],
[
    InlineKeyboardButton('Bayalu Daari', switch_inline_query_current_chat='Bayalu Daari'),
    InlineKeyboardButton('6-5=2', switch_inline_query_current_chat='6-5=2'),
],
[
    InlineKeyboardButton('Tunaga Tunaga', switch_inline_query_current_chat='Tunaga Tunaga'),
    InlineKeyboardButton('Kalpana', switch_inline_query_current_chat='Kalpana'),
],
[
    InlineKeyboardButton('Charlie', switch_inline_query_current_chat='Charlie'),
    InlineKeyboardButton('Preethi Prema Pranaya', switch_inline_query_current_chat='Preethi Prema Pranaya'),
],
[
    InlineKeyboardButton('Kallara Santhe', switch_inline_query_current_chat='Kallara Santhe'),
    InlineKeyboardButton('Chandralekha', switch_inline_query_current_chat='Chandralekha'),
],
[
    InlineKeyboardButton('Dracula', switch_inline_query_current_chat='Dracula'),
    InlineKeyboardButton('Mane Mane Kathe', switch_inline_query_current_chat='Mane Mane Kathe'),
],
[
    InlineKeyboardButton('Gruha Bhojana', switch_inline_query_current_chat='Gruha Bhojana'),
    InlineKeyboardButton('Nagavalli', switch_inline_query_current_chat='Nagavalli'),
],
[
    InlineKeyboardButton('Malenadina Hudugi', switch_inline_query_current_chat='Malenadina Hudugi'),
    InlineKeyboardButton('Baa Nalle Madhuchandrake', switch_inline_query_current_chat='Baa Nalle Madhuchandrake'),
],
[
    InlineKeyboardButton('Hani Hani', switch_inline_query_current_chat='Hani Hani'),
    InlineKeyboardButton('Kamarottu Checkpost', switch_inline_query_current_chat='Kamarottu Checkpost'),
],
[
    InlineKeyboardButton('Mylari', switch_inline_query_current_chat='Mylari'),
    InlineKeyboardButton('Sangliyana', switch_inline_query_current_chat='Sangliyana'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Romancek":
        buttons = [ [
    InlineKeyboardButton('Mungaru Male', switch_inline_query_current_chat='Mungaru Male'),
    InlineKeyboardButton('Milana', switch_inline_query_current_chat='Milana'),
],
[
    InlineKeyboardButton('Bhama Vijaya', switch_inline_query_current_chat='Bhama Vijaya'),
    InlineKeyboardButton('Sanju Weds Geetha', switch_inline_query_current_chat='Sanju Weds Geetha'),
],
[
    InlineKeyboardButton('Amruthavarshini', switch_inline_query_current_chat='Amruthavarshini'),
    InlineKeyboardButton('Nanu Nanna Kanasu', switch_inline_query_current_chat='Nanu Nanna Kanasu'),
],
[
    InlineKeyboardButton('Preethse Antha Pranaama', switch_inline_query_current_chat='Preethse Antha Pranaama'),
    InlineKeyboardButton('Chaitrada Chandrama', switch_inline_query_current_chat='Chaitrada Chandrama'),
],
[
    InlineKeyboardButton('Chinnari Mutha', switch_inline_query_current_chat='Chinnari Mutha'),
    InlineKeyboardButton('Mussanje Maatu', switch_inline_query_current_chat='Mussanje Maatu'),
],
[
    InlineKeyboardButton('Suntaragaali', switch_inline_query_current_chat='Suntaragaali'),
    InlineKeyboardButton('Neenello Naanalle', switch_inline_query_current_chat='Neenello Naanalle'),
],
[
    InlineKeyboardButton('Krishnan Love Story', switch_inline_query_current_chat='Krishnan Love Story'),
    InlineKeyboardButton('Aa Dinagalu', switch_inline_query_current_chat='Aa Dinagalu'),
],
[
    InlineKeyboardButton('Junglee', switch_inline_query_current_chat='Junglee'),
    InlineKeyboardButton('Bhale Jodi', switch_inline_query_current_chat='Bhale Jodi'),
],
[
    InlineKeyboardButton('Kannadada Kanda', switch_inline_query_current_chat='Kannadada Kanda'),
    InlineKeyboardButton('Janumada Jodi', switch_inline_query_current_chat='Janumada Jodi'),
],
[
    InlineKeyboardButton('Excuse Me', switch_inline_query_current_chat='Excuse Me'),
    InlineKeyboardButton('Chandramukhi Pranasakhi', switch_inline_query_current_chat='Chandramukhi Pranasakhi'),
],
[
    InlineKeyboardButton('Geleya', switch_inline_query_current_chat='Geleya'),
    InlineKeyboardButton('Nannaseya Hoove', switch_inline_query_current_chat='Nannaseya Hoove'),
],
[
    InlineKeyboardButton('Nodi Swamy Navirodu Hige', switch_inline_query_current_chat='Nodi Swamy Navirodu Hige'),
    InlineKeyboardButton('Bhagyada Lakshmi Baramma', switch_inline_query_current_chat='Bhagyada Lakshmi Baramma'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Dramak":
        buttons = [ [
    InlineKeyboardButton('Lucia', switch_inline_query_current_chat='Lucia'),
    InlineKeyboardButton('Ulidavaru Kandanthe', switch_inline_query_current_chat='Ulidavaru Kandanthe'),
],
[
    InlineKeyboardButton('Kendasampige', switch_inline_query_current_chat='Kendasampige'),
    InlineKeyboardButton('Rama Rama Re', switch_inline_query_current_chat='Rama Rama Re'),
],
[
    InlineKeyboardButton('Naanu Avanalla...Avalu', switch_inline_query_current_chat='Naanu Avanalla...Avalu'),
    InlineKeyboardButton('Thithi', switch_inline_query_current_chat='Thithi'),
],
[
    InlineKeyboardButton('Harivu', switch_inline_query_current_chat='Harivu'),
    InlineKeyboardButton('Manjari', switch_inline_query_current_chat='Manjari'),
],
[
    InlineKeyboardButton('Ishtakamya', switch_inline_query_current_chat='Ishtakamya'),
    InlineKeyboardButton('Ondu Motteya Kathe', switch_inline_query_current_chat='Ondu Motteya Kathe'),
],
[
    InlineKeyboardButton('Godhi Banna Sadharana Mykattu', switch_inline_query_current_chat='Godhi Banna Sadharana Mykattu'),
    InlineKeyboardButton('Karvva', switch_inline_query_current_chat='Karvva'),
],
[
    InlineKeyboardButton('Kiragoorina Gayyaligalu', switch_inline_query_current_chat='Kiragoorina Gayyaligalu'),
    InlineKeyboardButton('Sarkari Hi. Pra. Shaale, Kasaragodu, Koduge: Ramanna Rai', switch_inline_query_current_chat='Sarkari Hi. Pra. Shaale, Kasaragodu, Koduge: Ramanna Rai'),
],
[
    InlineKeyboardButton('96', switch_inline_query_current_chat='96'),
    InlineKeyboardButton('Birbal Trilogy: Case 1', switch_inline_query_current_chat='Birbal Trilogy: Case 1'),
],
[
    InlineKeyboardButton('Rangitaranga', switch_inline_query_current_chat='Rangitaranga'),
    InlineKeyboardButton('Nathicharami', switch_inline_query_current_chat='Nathicharami'),
],
[
    InlineKeyboardButton('Dia', switch_inline_query_current_chat='Dia'),
    InlineKeyboardButton('Bhinna', switch_inline_query_current_chat='Bhinna'),
],
[
    InlineKeyboardButton('Popcorn Monkey Tiger', switch_inline_query_current_chat='Popcorn Monkey Tiger'),
    InlineKeyboardButton('Love Mocktail', switch_inline_query_current_chat='Love Mocktail'),
],
[
    InlineKeyboardButton('Bheemasena Nalamaharaja', switch_inline_query_current_chat='Bheemasena Nalamaharaja'),
    InlineKeyboardButton('Avane Srimannarayana', switch_inline_query_current_chat='Avane Srimannarayana'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Comedyk":
        buttons = [ [
    InlineKeyboardButton('Ganeshana Maduve', switch_inline_query_current_chat='Ganeshana Maduve'),
    InlineKeyboardButton('Nammura Mandara Hoove', switch_inline_query_current_chat='Nammura Mandara Hoove'),
],
[
    InlineKeyboardButton('Operation Antha', switch_inline_query_current_chat='Operation Antha'),
    InlineKeyboardButton('Ulta Palta', switch_inline_query_current_chat='Ulta Palta'),
],
[
    InlineKeyboardButton('C.B.I Shankar', switch_inline_query_current_chat='C.B.I Shankar'),
    InlineKeyboardButton('Guru', switch_inline_query_current_chat='Guru'),
],
[
    InlineKeyboardButton('Bombat Hendthi', switch_inline_query_current_chat='Bombat Hendthi'),
    InlineKeyboardButton('Karulina Kudi', switch_inline_query_current_chat='Karulina Kudi'),
],
[
    InlineKeyboardButton('Krishna Nee Begane Baaro', switch_inline_query_current_chat='Krishna Nee Begane Baaro'),
    InlineKeyboardButton('Police Story 2', switch_inline_query_current_chat='Police Story 2'),
],
[
    InlineKeyboardButton('Ganesha Subramanya', switch_inline_query_current_chat='Ganesha Subramanya'),
    InlineKeyboardButton('Olu Saar Bari Olu', switch_inline_query_current_chat='Olu Saar Bari Olu'),
],
[
    InlineKeyboardButton('Manmatha Raja', switch_inline_query_current_chat='Manmatha Raja'),
    InlineKeyboardButton('Thandege Thakka Maga', switch_inline_query_current_chat='Thandege Thakka Maga'),
],
[
    InlineKeyboardButton('Garjane', switch_inline_query_current_chat='Garjane'),
    InlineKeyboardButton('Golmaal Radhakrishna', switch_inline_query_current_chat='Golmaal Radhakrishna'),
],
[
    InlineKeyboardButton('Kattegalu Saar Kattegalu', switch_inline_query_current_chat='Kattegalu Saar Kattegalu'),
    InlineKeyboardButton('Gopi Krishna', switch_inline_query_current_chat='Gopi Krishna'),
],
[
    InlineKeyboardButton('Aparoopada Athitigalu', switch_inline_query_current_chat='Aparoopada Athitigalu'),
    InlineKeyboardButton('Harakeya Kuri', switch_inline_query_current_chat='Harakeya Kuri'),
],
[
    InlineKeyboardButton('Dharani Mandala Madhyadolage', switch_inline_query_current_chat='Dharani Mandala Madhyadolage'),
    InlineKeyboardButton('Nodi Swamy Navirodu Hige', switch_inline_query_current_chat='Nodi Swamy Navirodu Hige'),
],
[
    InlineKeyboardButton('Kittu Puttu', switch_inline_query_current_chat='Kittu Puttu'),
    InlineKeyboardButton('Ganesh', switch_inline_query_current_chat='Ganesh'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Actionk":
        buttons = [ [
    InlineKeyboardButton('Mankatha', switch_inline_query_current_chat='Mankatha'),
    InlineKeyboardButton('Ugramm', switch_inline_query_current_chat='Ugramm'),
],
[
    InlineKeyboardButton('KGF: Chapter 1', switch_inline_query_current_chat='KGF: Chapter 1'),
    InlineKeyboardButton('Mufti', switch_inline_query_current_chat='Mufti'),
],
[
    InlineKeyboardButton('Bhairava Geetha', switch_inline_query_current_chat='Bhairava Geetha'),
    InlineKeyboardButton('Tagaru', switch_inline_query_current_chat='Tagaru'),
],
[
    InlineKeyboardButton('Badmaash', switch_inline_query_current_chat='Badmaash'),
    InlineKeyboardButton('Jigarthanda', switch_inline_query_current_chat='Jigarthanda'),
],
[
    InlineKeyboardButton('Bajarangi', switch_inline_query_current_chat='Bajarangi'),
    InlineKeyboardButton('Tyson', switch_inline_query_current_chat='Tyson'),
],
[
    InlineKeyboardButton('Masterpiece', switch_inline_query_current_chat='Masterpiece'),
    InlineKeyboardButton('Kalpana', switch_inline_query_current_chat='Kalpana'),
],
[
    InlineKeyboardButton('Deadly Soma', switch_inline_query_current_chat='Deadly Soma'),
    InlineKeyboardButton('Airavata', switch_inline_query_current_chat='Airavata'),
],
[
    InlineKeyboardButton('Ramachari', switch_inline_query_current_chat='Ramachari'),
    InlineKeyboardButton('Bhadra', switch_inline_query_current_chat='Bhadra'),
],
[
    InlineKeyboardButton('Suryavamsha', switch_inline_query_current_chat='Suryavamsha'),
    InlineKeyboardButton('Yajamana', switch_inline_query_current_chat='Yajamana'),
],
[
    InlineKeyboardButton('Chingari', switch_inline_query_current_chat='Chingari'),
    InlineKeyboardButton('Dasharatha', switch_inline_query_current_chat='Dasharatha'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "typek":
        buttons = [
            [
                InlineKeyboardButton("Action", callback_data="Actionk"),
                InlineKeyboardButton("Romance", callback_data="Romancek")
            ],[
                InlineKeyboardButton("Comedy ", callback_data="Comedyk"),
                InlineKeyboardButton("Horror", callback_data="Horrork")
            ],[
                InlineKeyboardButton("Drama", callback_data="Dramak"),
                InlineKeyboardButton("Thrillerk", callback_data="Thrillerk")
            ],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    
    elif query.data == "Shivrajkumar":
        buttons = [ [
    InlineKeyboardButton('Om', switch_inline_query_current_chat='Om'),
    InlineKeyboardButton('Jogi', switch_inline_query_current_chat='Jogi'),
],
[
    InlineKeyboardButton('Anand', switch_inline_query_current_chat='Anand'),
    InlineKeyboardButton('Raktha Kanneeru', switch_inline_query_current_chat='Raktha Kanneeru'),
],
[
    InlineKeyboardButton('Janumada Jodi', switch_inline_query_current_chat='Janumada Jodi'),
    InlineKeyboardButton('Shivalinga', switch_inline_query_current_chat='Shivalinga'),
],
[
    InlineKeyboardButton('Kavacha', switch_inline_query_current_chat='Kavacha'),
    InlineKeyboardButton('Bhajarangi', switch_inline_query_current_chat='Bhajarangi'),
],
[
    InlineKeyboardButton('Mufti', switch_inline_query_current_chat='Mufti'),
    InlineKeyboardButton('Tagaru', switch_inline_query_current_chat='Tagaru'),
],
[
    InlineKeyboardButton('Shivalinga', switch_inline_query_current_chat='Shivalinga'),
    InlineKeyboardButton('Killing Veerappan', switch_inline_query_current_chat='Killing Veerappan'),
],
[
    InlineKeyboardButton('Bhairava Geetha', switch_inline_query_current_chat='Bhairava Geetha'),
    InlineKeyboardButton('Samyuktha 2', switch_inline_query_current_chat='Samyuktha 2'),
],
[
    InlineKeyboardButton('Annavru', switch_inline_query_current_chat='Annavru'),
    InlineKeyboardButton('Muthanna', switch_inline_query_current_chat='Muthanna'),
],
[
    InlineKeyboardButton('Mylari', switch_inline_query_current_chat='Mylari'),
    InlineKeyboardButton('Cheluveye Ninne Nodalu', switch_inline_query_current_chat='Cheluveye Ninne Nodalu'),
],
[
    InlineKeyboardButton('Deadly Soma', switch_inline_query_current_chat='Deadly Soma'),
    InlineKeyboardButton('Kempe Gowda', switch_inline_query_current_chat='Kempe Gowda'),
],
[
    InlineKeyboardButton('Rathavara', switch_inline_query_current_chat='Rathavara'),
    InlineKeyboardButton('Chigurida Kanasu', switch_inline_query_current_chat='Chigurida Kanasu'),
],
[
    InlineKeyboardButton('Huchcha', switch_inline_query_current_chat='Huchcha'),
    InlineKeyboardButton('Shivalinga (2016)', switch_inline_query_current_chat='Shivalinga (2016)'),
],
[
    InlineKeyboardButton('Namma Basava', switch_inline_query_current_chat='Namma Basava'),
    InlineKeyboardButton('Hare Rama Hare Krishna', switch_inline_query_current_chat='Hare Rama Hare Krishna'),
],
[
    InlineKeyboardButton('Ganesh', switch_inline_query_current_chat='Ganesh'),
    InlineKeyboardButton('Sirivantha', switch_inline_query_current_chat='Sirivantha'),
],
[
    InlineKeyboardButton('Ayya', switch_inline_query_current_chat='Ayya'),
    InlineKeyboardButton('Thayi Illada Thavaru', switch_inline_query_current_chat='Thayi Illada Thavaru'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Upendra":
        buttons = [ [
    InlineKeyboardButton('Samskara', switch_inline_query_current_chat='Samskara'),
    InlineKeyboardButton('Ranganayaki', switch_inline_query_current_chat='Ranganayaki'),
],
[
    InlineKeyboardButton('Bhootayyana Maga Ayyu', switch_inline_query_current_chat='Bhootayyana Maga Ayyu'),
    InlineKeyboardButton('Ghatashraddha', switch_inline_query_current_chat='Ghatashraddha'),
],
[
    InlineKeyboardButton('Mane', switch_inline_query_current_chat='Mane'),
    InlineKeyboardButton('Kaadu', switch_inline_query_current_chat='Kaadu'),
],
[
    InlineKeyboardButton('Dweepa', switch_inline_query_current_chat='Dweepa'),
    InlineKeyboardButton('Thaayi Saheba', switch_inline_query_current_chat='Thaayi Saheba'),
],
[
    InlineKeyboardButton('Hoovu Hannu', switch_inline_query_current_chat='Hoovu Hannu'),
    InlineKeyboardButton('Vamsha Vriksha', switch_inline_query_current_chat='Vamsha Vriksha'),
],
[
    InlineKeyboardButton('Suryakanthi', switch_inline_query_current_chat='Suryakanthi'),
    InlineKeyboardButton('Sose Tanda Soubhagya', switch_inline_query_current_chat='Sose Tanda Soubhagya'),
],
[
    InlineKeyboardButton('Gejje Pooje', switch_inline_query_current_chat='Gejje Pooje'),
    InlineKeyboardButton('Anuroopa', switch_inline_query_current_chat='Anuroopa'),
],
[
    InlineKeyboardButton('Huliya', switch_inline_query_current_chat='Huliya'),
    InlineKeyboardButton('Nagarahaavu', switch_inline_query_current_chat='Nagarahaavu'),
],
[
    InlineKeyboardButton('Yeradu Nakshatragalu', switch_inline_query_current_chat='Yeradu Nakshatragalu'),
    InlineKeyboardButton('Minchina Ota', switch_inline_query_current_chat='Minchina Ota'),
],
[
    InlineKeyboardButton('Eradu Nakshatragalu', switch_inline_query_current_chat='Eradu Nakshatragalu'),
    InlineKeyboardButton('Upasane', switch_inline_query_current_chat='Upasane'),
],
[
    InlineKeyboardButton('Chomana Dudi', switch_inline_query_current_chat='Chomana Dudi'),
    InlineKeyboardButton('Geetha', switch_inline_query_current_chat='Geetha'),
],
[
    InlineKeyboardButton('Accident', switch_inline_query_current_chat='Accident'),
    InlineKeyboardButton('Devara Duddu', switch_inline_query_current_chat='Devara Duddu'),
],
[
    InlineKeyboardButton('Hombisilu', switch_inline_query_current_chat='Hombisilu'),
    InlineKeyboardButton('Dharma', switch_inline_query_current_chat='Dharma'),
],
[
    InlineKeyboardButton('Beluvalada Madilalli', switch_inline_query_current_chat='Beluvalada Madilalli'),
    InlineKeyboardButton('Bayalu Daari', switch_inline_query_current_chat='Bayalu Daari'),
],
[
    InlineKeyboardButton('Benkiya Bale', switch_inline_query_current_chat='Benkiya Bale'),
    InlineKeyboardButton('Bara', switch_inline_query_current_chat='Bara'),
],
[
    InlineKeyboardButton('Bettada Hoovu', switch_inline_query_current_chat='Bettada Hoovu'),
    InlineKeyboardButton('Bandhana', switch_inline_query_current_chat='Bandhana'),
],
[
    InlineKeyboardButton('Bangarada Manushya', switch_inline_query_current_chat='Bangarada Manushya'),
    InlineKeyboardButton('Dampati', switch_inline_query_current_chat='Dampati'),
],
[
    InlineKeyboardButton('Shubhamangala', switch_inline_query_current_chat='Shubhamangala'),
    InlineKeyboardButton('Kasturi Nivasa', switch_inline_query_current_chat='Kasturi Nivasa'),
],
[
    InlineKeyboardButton('Avala Hejje', switch_inline_query_current_chat='Avala Hejje'),
    InlineKeyboardButton('Devara Kannu', switch_inline_query_current_chat='Devara Kannu'),
],
[
    InlineKeyboardButton('Bhakta Prahlada', switch_inline_query_current_chat='Bhakta Prahlada'),
    InlineKeyboardButton('Bhagyada Bagilu', switch_inline_query_current_chat='Bhagyada Bagilu'),
],
[
    InlineKeyboardButton('Babruvahana', switch_inline_query_current_chat='Babruvahana'),
    InlineKeyboardButton('Bhale Huchcha', switch_inline_query_current_chat='Bhale Huchcha'),
],
[
    InlineKeyboardButton('Kutturu Hennu', switch_inline_query_current_chat='Kutturu Hennu'),
    InlineKeyboardButton('Kittu Puttu', switch_inline_query_current_chat='Kittu Puttu'),
],
[
    InlineKeyboardButton('Bhale Adrushtavo Adrushta', switch_inline_query_current_chat='Bhale Adrushtavo Adrushta'),
    InlineKeyboardButton('Upendra', switch_inline_query_current_chat='Upendra'),
],
[
    InlineKeyboardButton('H20', switch_inline_query_current_chat='H20'),
    InlineKeyboardButton('Duniya', switch_inline_query_current_chat='Duniya'),
],
[
    InlineKeyboardButton('Milana', switch_inline_query_current_chat='Milana'),
    InlineKeyboardButton('Mussanje Maathu', switch_inline_query_current_chat='Mussanje Maathu'),
],
[
    InlineKeyboardButton('Birugali', switch_inline_query_current_chat='Birugali'),
    InlineKeyboardButton('Sanju Weds Geetha', switch_inline_query_current_chat='Sanju Weds Geetha'),
],
[
    InlineKeyboardButton('Jolly Days', switch_inline_query_current_chat='Jolly Days'),
    InlineKeyboardButton('Moggina Manasu', switch_inline_query_current_chat='Moggina Manasu'),
],
[
    InlineKeyboardButton('Uyyale', switch_inline_query_current_chat='Uyyale'),
    InlineKeyboardButton('Buddhivantha', switch_inline_query_current_chat='Buddhivantha'),
],
[
    InlineKeyboardButton('Gunavantha', switch_inline_query_current_chat='Gunavantha'),
    InlineKeyboardButton('Mylari', switch_inline_query_current_chat='Mylari'),
],
[
    InlineKeyboardButton('Anatharu', switch_inline_query_current_chat='Anatharu'),
    InlineKeyboardButton('Aa Dinagalu', switch_inline_query_current_chat='Aa Dinagalu'),
],
[
    InlineKeyboardButton('Shyloo', switch_inline_query_current_chat='Shyloo'),
    InlineKeyboardButton('Sanju', switch_inline_query_current_chat='Sanju'),
],
[
    InlineKeyboardButton('Bannada Gejje', switch_inline_query_current_chat='Bannada Gejje'),
    InlineKeyboardButton('Baa Nalle Madhuchandrake', switch_inline_query_current_chat='Baa Nalle Madhuchandrake'),
],
[
    InlineKeyboardButton('Aa Eradu Varshagalu', switch_inline_query_current_chat='Aa Eradu Varshagalu'),
    InlineKeyboardButton('Huli', switch_inline_query_current_chat='Huli'),
],
[
    InlineKeyboardButton('Kotigobba', switch_inline_query_current_chat='Kotigobba'),
    InlineKeyboardButton('Kiccha Huccha', switch_inline_query_current_chat='Kiccha Huccha'),
],
[
    InlineKeyboardButton('Veera Parampare', switch_inline_query_current_chat='Veera Parampare'),
    InlineKeyboardButton('Jackie', switch_inline_query_current_chat='Jackie'),
],
[
    InlineKeyboardButton('Kempegowda', switch_inline_query_current_chat='Kempegowda'),
    InlineKeyboardButton('Vishnuvardhana', switch_inline_query_current_chat='Vishnuvardhana'),
],
[
    InlineKeyboardButton('Anna Bond', switch_inline_query_current_chat='Anna Bond'),
    InlineKeyboardButton('Bhajarangi', switch_inline_query_current_chat='Bhajarangi'),
],
[
    InlineKeyboardButton('Bulbul', switch_inline_query_current_chat='Bulbul'),
    InlineKeyboardButton('Mythri', switch_inline_query_current_chat='Mythri'),
],
[
    InlineKeyboardButton('Vajrakaya', switch_inline_query_current_chat='Vajrakaya'),
    InlineKeyboardButton('Doddmane Hudga', switch_inline_query_current_chat='Doddmane Hudga'),
],
[
    InlineKeyboardButton('Rajakumara', switch_inline_query_current_chat='Rajakumara'),
    InlineKeyboardButton('Hebbuli', switch_inline_query_current_chat='Hebbuli'),
],
[
    InlineKeyboardButton('Kotigobba 2', switch_inline_query_current_chat='Kotigobba 2'),
    InlineKeyboardButton('The Villain', switch_inline_query_current_chat='The Villain'),
],
[
    InlineKeyboardButton('Pailwaan', switch_inline_query_current_chat='Pailwaan'),
    InlineKeyboardButton('Sye Raa Narasimha Reddy (Telugu)', switch_inline_query_current_chat='Sye Raa Narasimha Reddy (Telugu)'),
],
[
    InlineKeyboardButton('Dabangg 3 (Hindi)', switch_inline_query_current_chat='Dabangg 3 (Hindi)'),
    InlineKeyboardButton('Phantom', switch_inline_query_current_chat='Phantom'),
],
[
    InlineKeyboardButton('Kotigobba 3', switch_inline_query_current_chat='Kotigobba 3'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Yash":
        buttons = [ [
    InlineKeyboardButton('Jambada Hudugi', switch_inline_query_current_chat='Jambada Hudugi'),
    InlineKeyboardButton('Joke Falls', switch_inline_query_current_chat='Joke Falls'),
],
[
    InlineKeyboardButton('Yajamana', switch_inline_query_current_chat='Yajamana'),
    InlineKeyboardButton('Rocky', switch_inline_query_current_chat='Rocky'),
],
[
    InlineKeyboardButton('Kallara Santhe', switch_inline_query_current_chat='Kallara Santhe'),
    InlineKeyboardButton('Gokula', switch_inline_query_current_chat='Gokula'),
],
[
    InlineKeyboardButton('Thamassu', switch_inline_query_current_chat='Thamassu'),
    InlineKeyboardButton('Modalasala', switch_inline_query_current_chat='Modalasala'),
],
[
    InlineKeyboardButton('Rajadhani', switch_inline_query_current_chat='Rajadhani'),
    InlineKeyboardButton('Kirataka', switch_inline_query_current_chat='Kirataka'),
],
[
    InlineKeyboardButton('Lucky', switch_inline_query_current_chat='Lucky'),
    InlineKeyboardButton('Jogaiah', switch_inline_query_current_chat='Jogaiah'),
],
[
    InlineKeyboardButton('Jaanu', switch_inline_query_current_chat='Jaanu'),
    InlineKeyboardButton('Drama', switch_inline_query_current_chat='Drama'),
],
[
    InlineKeyboardButton('Kranthiveera Sangolli Rayanna', switch_inline_query_current_chat='Kranthiveera Sangolli Rayanna'),
    InlineKeyboardButton('Chandra', switch_inline_query_current_chat='Chandra'),
],
[
    InlineKeyboardButton('Googly', switch_inline_query_current_chat='Googly'),
    InlineKeyboardButton('Raja Huli', switch_inline_query_current_chat='Raja Huli'),
],
[
    InlineKeyboardButton('Gajakesari', switch_inline_query_current_chat='Gajakesari'),
    InlineKeyboardButton('Mr. and Mrs. Ramachari', switch_inline_query_current_chat='Mr. and Mrs. Ramachari'),
],
[
    InlineKeyboardButton('Masterpiece', switch_inline_query_current_chat='Masterpiece'),
    InlineKeyboardButton('Santhu Straight Forward', switch_inline_query_current_chat='Santhu Straight Forward'),
],
[
    InlineKeyboardButton('K.G.F: Chapter 1', switch_inline_query_current_chat='K.G.F: Chapter 1'),
    InlineKeyboardButton('Kirataka', switch_inline_query_current_chat='Kirataka'),
],
[
    InlineKeyboardButton('K.G.F: Chapter 2', switch_inline_query_current_chat='K.G.F: Chapter 2'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Darshan":
        buttons = [ [
    InlineKeyboardButton('Majestic', switch_inline_query_current_chat='Majestic'),
    InlineKeyboardButton('Kariya', switch_inline_query_current_chat='Kariya'),
],
[
    InlineKeyboardButton('Lankesh Patrike', switch_inline_query_current_chat='Lankesh Patrike'),
    InlineKeyboardButton('Namma Preethiya Ramu', switch_inline_query_current_chat='Namma Preethiya Ramu'),
],
[
    InlineKeyboardButton('Ninagoskara', switch_inline_query_current_chat='Ninagoskara'),
    InlineKeyboardButton('Jothe Jotheyali', switch_inline_query_current_chat='Jothe Jotheyali'),
],
[
    InlineKeyboardButton('Daasa', switch_inline_query_current_chat='Daasa'),
    InlineKeyboardButton('Kalasipalya', switch_inline_query_current_chat='Kalasipalya'),
],
[
    InlineKeyboardButton('Nandi', switch_inline_query_current_chat='Nandi'),
    InlineKeyboardButton('En Swasa Kaatre (Tamil)', switch_inline_query_current_chat='En Swasa Kaatre (Tamil)'),
],
[
    InlineKeyboardButton('Bhoothayyana Makkalu', switch_inline_query_current_chat='Bhoothayyana Makkalu'),
    InlineKeyboardButton('Neelambari', switch_inline_query_current_chat='Neelambari'),
],
[
    InlineKeyboardButton('Devara Maga', switch_inline_query_current_chat='Devara Maga'),
    InlineKeyboardButton('Ninagagi', switch_inline_query_current_chat='Ninagagi'),
],
[
    InlineKeyboardButton('Ellara Mane Dosenu', switch_inline_query_current_chat='Ellara Mane Dosenu'),
    InlineKeyboardButton('Ninagagi', switch_inline_query_current_chat='Ninagagi'),
],
[
    InlineKeyboardButton('Odeya', switch_inline_query_current_chat='Odeya'),
    InlineKeyboardButton('Kariya 2', switch_inline_query_current_chat='Kariya 2'),
],
[
    InlineKeyboardButton('Bhagat Singh', switch_inline_query_current_chat='Bhagat Singh'),
    InlineKeyboardButton('Annavru', switch_inline_query_current_chat='Annavru'),
],
[
    InlineKeyboardButton('Kurigalu Saar Kurigalu', switch_inline_query_current_chat='Kurigalu Saar Kurigalu'),
    InlineKeyboardButton('Bhoopathy', switch_inline_query_current_chat='Bhoopathy'),
],
[
    InlineKeyboardButton('Kalasipalya', switch_inline_query_current_chat='Kalasipalya'),
    InlineKeyboardButton('Shashtri', switch_inline_query_current_chat='Shashtri'),
],
[
    InlineKeyboardButton('Ayya', switch_inline_query_current_chat='Ayya'),
    InlineKeyboardButton('Swamy', switch_inline_query_current_chat='Swamy'),
],
[
    InlineKeyboardButton('Indra', switch_inline_query_current_chat='Indra'),
    InlineKeyboardButton('Dattu', switch_inline_query_current_chat='Dattu'),
],
[
    InlineKeyboardButton('Sardara', switch_inline_query_current_chat='Sardara'),
    InlineKeyboardButton('Gaja', switch_inline_query_current_chat='Gaja'),
],
[
    InlineKeyboardButton('Bhoopathy', switch_inline_query_current_chat='Bhoopathy'),
    InlineKeyboardButton('Prince', switch_inline_query_current_chat='Prince'),
],
[
    InlineKeyboardButton('Shourya', switch_inline_query_current_chat='Shourya'),
    InlineKeyboardButton('Abhay', switch_inline_query_current_chat='Abhay'),
],
[
    InlineKeyboardButton('Jothe Jotheyali', switch_inline_query_current_chat='Jothe Jotheyali'),
    InlineKeyboardButton('Saarathi', switch_inline_query_current_chat='Saarathi'),
],
[
    InlineKeyboardButton('Viraat', switch_inline_query_current_chat='Viraat'),
    InlineKeyboardButton('Chakravarthy', switch_inline_query_current_chat='Chakravarthy'),
],
[
    InlineKeyboardButton('Tarak', switch_inline_query_current_chat='Tarak'),
    InlineKeyboardButton('Yajamana', switch_inline_query_current_chat='Yajamana'),
],
[
    InlineKeyboardButton('Kurukshetra', switch_inline_query_current_chat='Kurukshetra'),
    InlineKeyboardButton('Roberrt', switch_inline_query_current_chat='Roberrt'),
],
[
    InlineKeyboardButton('Raja Veera Madakari Nayaka', switch_inline_query_current_chat='Raja Veera Madakari Nayaka'),
    InlineKeyboardButton('Odeya', switch_inline_query_current_chat='Odeya'),
],
[
    InlineKeyboardButton('Raja Veera Madakari Nayaka', switch_inline_query_current_chat='Raja Veera Madakari Nayaka'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Sudeep":
        buttons = [ [
    InlineKeyboardButton('Sparsha', switch_inline_query_current_chat='Sparsha'),
    InlineKeyboardButton('Huchcha', switch_inline_query_current_chat='Huchcha'),
],
[
    InlineKeyboardButton('Vaalee', switch_inline_query_current_chat='Vaalee'),
    InlineKeyboardButton('Kiccha', switch_inline_query_current_chat='Kiccha'),
],
[
    InlineKeyboardButton('Partha', switch_inline_query_current_chat='Partha'),
    InlineKeyboardButton('Swathi Muthu', switch_inline_query_current_chat='Swathi Muthu'),
],
[
    InlineKeyboardButton('Ranga SSLC', switch_inline_query_current_chat='Ranga SSLC'),
    InlineKeyboardButton('My Autograph', switch_inline_query_current_chat='My Autograph'),
],
[
    InlineKeyboardButton('Nalla', switch_inline_query_current_chat='Nalla'),
    InlineKeyboardButton('Thirupathi', switch_inline_query_current_chat='Thirupathi'),
],
[
    InlineKeyboardButton('Mussanjemaatu', switch_inline_query_current_chat='Mussanjemaatu'),
    InlineKeyboardButton('Autograph Please', switch_inline_query_current_chat='Autograph Please'),
],
[
    InlineKeyboardButton('Theeradha Vilaiyattu Pillai (Tamil)', switch_inline_query_current_chat='Theeradha Vilaiyattu Pillai (Tamil)'),
    InlineKeyboardButton('Kempe Gowda', switch_inline_query_current_chat='Kempe Gowda'),
],
[
    InlineKeyboardButton('Just Maath Maathalli', switch_inline_query_current_chat='Just Maath Maathalli'),
    InlineKeyboardButton('Veera Madakari', switch_inline_query_current_chat='Veera Madakari'),
],
[
    InlineKeyboardButton('Phoonk', switch_inline_query_current_chat='Phoonk'),
    InlineKeyboardButton('Rakta Charitra (Hindi)', switch_inline_query_current_chat='Rakta Charitra (Hindi)'),
],
[
    InlineKeyboardButton('Only Vishnuvardhana', switch_inline_query_current_chat='Only Vishnuvardhana'),
    InlineKeyboardButton('Kempe Gowda', switch_inline_query_current_chat='Kempe Gowda'),
],
[
    InlineKeyboardButton('Vishnuvardhana', switch_inline_query_current_chat='Vishnuvardhana'),
    InlineKeyboardButton('Eega (Telugu)', switch_inline_query_current_chat='Eega (Telugu)'),
],
[
    InlineKeyboardButton('Bachchan', switch_inline_query_current_chat='Bachchan'),
    InlineKeyboardButton('Varadanayaka', switch_inline_query_current_chat='Varadanayaka'),
],
[
    InlineKeyboardButton('Bhajarangi', switch_inline_query_current_chat='Bhajarangi'),
    InlineKeyboardButton('Maanikya', switch_inline_query_current_chat='Maanikya'),
],
[
    InlineKeyboardButton('Ranna', switch_inline_query_current_chat='Ranna'),
    InlineKeyboardButton('Mukunda Murari', switch_inline_query_current_chat='Mukunda Murari'),
],
[
    InlineKeyboardButton('Hebbuli', switch_inline_query_current_chat='Hebbuli'),
    InlineKeyboardButton('Kotigobba 2', switch_inline_query_current_chat='Kotigobba 2'),
],
[
    InlineKeyboardButton('The Villain', switch_inline_query_current_chat='The Villain'),
    InlineKeyboardButton('Pailwaan', switch_inline_query_current_chat='Pailwaan'),
],
[
    InlineKeyboardButton('Sye Raa Narasimha Reddy (Telugu)', switch_inline_query_current_chat='Sye Raa Narasimha Reddy (Telugu)'),
    InlineKeyboardButton('Dabangg 3 (Hindi)', switch_inline_query_current_chat='Dabangg 3 (Hindi)'),
],
[
    InlineKeyboardButton('Phantom', switch_inline_query_current_chat='Phantom'),
    InlineKeyboardButton('Kotigobba 3', switch_inline_query_current_chat='Kotigobba 3'),
],
[
    InlineKeyboardButton('Risen', switch_inline_query_current_chat='Risen'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "PuneethRajkumar":
        buttons = [ [
    InlineKeyboardButton('Appu', switch_inline_query_current_chat='Appu'),
    InlineKeyboardButton('Abhi', switch_inline_query_current_chat='Abhi'),
],
[
    InlineKeyboardButton('Veera Kannadiga', switch_inline_query_current_chat='Veera Kannadiga'),
    InlineKeyboardButton('Aakash', switch_inline_query_current_chat='Aakash'),
],
[
    InlineKeyboardButton('Arasu', switch_inline_query_current_chat='Arasu'),
    InlineKeyboardButton('Namma Basava', switch_inline_query_current_chat='Namma Basava'),
],
[
    InlineKeyboardButton('Aa Dinagalu', switch_inline_query_current_chat='Aa Dinagalu'),
    InlineKeyboardButton('Milana', switch_inline_query_current_chat='Milana'),
],
[
    InlineKeyboardButton('Vamshi', switch_inline_query_current_chat='Vamshi'),
    InlineKeyboardButton('Bindaas', switch_inline_query_current_chat='Bindaas'),
],
[
    InlineKeyboardButton('Raam', switch_inline_query_current_chat='Raam'),
    InlineKeyboardButton('Jackie', switch_inline_query_current_chat='Jackie'),
],
[
    InlineKeyboardButton('Hudugaru', switch_inline_query_current_chat='Hudugaru'),
    InlineKeyboardButton('Paramathma', switch_inline_query_current_chat='Paramathma'),
],
[
    InlineKeyboardButton('Anna Bond', switch_inline_query_current_chat='Anna Bond'),
    InlineKeyboardButton('Power', switch_inline_query_current_chat='Power'),
],
[
    InlineKeyboardButton('Ninnindale', switch_inline_query_current_chat='Ninnindale'),
    InlineKeyboardButton('Yaare Koogadali', switch_inline_query_current_chat='Yaare Koogadali'),
],
[
    InlineKeyboardButton('Anna', switch_inline_query_current_chat='Anna'),
    InlineKeyboardButton('Rajakumara', switch_inline_query_current_chat='Rajakumara'),
],
[
    InlineKeyboardButton('Anjani Putra', switch_inline_query_current_chat='Anjani Putra'),
    InlineKeyboardButton('Natasaarvabhowma', switch_inline_query_current_chat='Natasaarvabhowma'),
],
[
    InlineKeyboardButton('Yuvarathnaa', switch_inline_query_current_chat='Yuvarathnaa'),
    InlineKeyboardButton('James', switch_inline_query_current_chat='James'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "herolistk":
        buttons =[
            [
                InlineKeyboardButton("Puneeth Rajkumar", callback_data="PuneethRajkumar"),
                InlineKeyboardButton("Yash", callback_data="Yash")
            ],[
                InlineKeyboardButton("Sudeep", callback_data="Sudeep"),
                InlineKeyboardButton("Upendra", callback_data="Upendra")
            ],[
                InlineKeyboardButton("Darshan", callback_data="Darshan"),
                InlineKeyboardButton("Shivrajkumar", callback_data="Shivrajkumar")
            ],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "bestk":
        buttons = [ [
    InlineKeyboardButton('Samskara', switch_inline_query_current_chat='Samskara'),
    InlineKeyboardButton('Ranganayaki', switch_inline_query_current_chat='Ranganayaki'),
],
[
    InlineKeyboardButton('Bhootayyana Maga Ayyu', switch_inline_query_current_chat='Bhootayyana Maga Ayyu'),
    InlineKeyboardButton('Ghatashraddha', switch_inline_query_current_chat='Ghatashraddha'),
],
[
    InlineKeyboardButton('Mane', switch_inline_query_current_chat='Mane'),
    InlineKeyboardButton('Kaadu', switch_inline_query_current_chat='Kaadu'),
],
[
    InlineKeyboardButton('Dweepa', switch_inline_query_current_chat='Dweepa'),
    InlineKeyboardButton('Thaayi Saheba', switch_inline_query_current_chat='Thaayi Saheba'),
],
[
    InlineKeyboardButton('Hoovu Hannu', switch_inline_query_current_chat='Hoovu Hannu'),
    InlineKeyboardButton('Vamsha Vriksha', switch_inline_query_current_chat='Vamsha Vriksha'),
],
[
    InlineKeyboardButton('Suryakanthi', switch_inline_query_current_chat='Suryakanthi'),
    InlineKeyboardButton('Sose Tanda Soubhagya', switch_inline_query_current_chat='Sose Tanda Soubhagya'),
],
[
    InlineKeyboardButton('Gejje Pooje', switch_inline_query_current_chat='Gejje Pooje'),
    InlineKeyboardButton('Anuroopa', switch_inline_query_current_chat='Anuroopa'),
],
[
    InlineKeyboardButton('Huliya', switch_inline_query_current_chat='Huliya'),
    InlineKeyboardButton('Nagarahaavu', switch_inline_query_current_chat='Nagarahaavu'),
],
[
    InlineKeyboardButton('Yeradu Nakshatragalu', switch_inline_query_current_chat='Yeradu Nakshatragalu'),
    InlineKeyboardButton('Minchina Ota', switch_inline_query_current_chat='Minchina Ota'),
],
[
    InlineKeyboardButton('Eradu Nakshatragalu', switch_inline_query_current_chat='Eradu Nakshatragalu'),
    InlineKeyboardButton('Upasane', switch_inline_query_current_chat='Upasane'),
],
[
    InlineKeyboardButton('Chomana Dudi', switch_inline_query_current_chat='Chomana Dudi'),
    InlineKeyboardButton('Geetha', switch_inline_query_current_chat='Geetha'),
],
[
    InlineKeyboardButton('Accident', switch_inline_query_current_chat='Accident'),
    InlineKeyboardButton('Devara Duddu', switch_inline_query_current_chat='Devara Duddu'),
],
[
    InlineKeyboardButton('Hombisilu', switch_inline_query_current_chat='Hombisilu'),
    InlineKeyboardButton('Dharma', switch_inline_query_current_chat='Dharma'),
],
[
    InlineKeyboardButton('Beluvalada Madilalli', switch_inline_query_current_chat='Beluvalada Madilalli'),
    InlineKeyboardButton('Bayalu Daari', switch_inline_query_current_chat='Bayalu Daari'),
],
[
    InlineKeyboardButton('Benkiya Bale', switch_inline_query_current_chat='Benkiya Bale'),
    InlineKeyboardButton('Bara', switch_inline_query_current_chat='Bara'),
],
[
    InlineKeyboardButton('Bettada Hoovu', switch_inline_query_current_chat='Bettada Hoovu'),
    InlineKeyboardButton('Bandhana', switch_inline_query_current_chat='Bandhana'),
],
[
    InlineKeyboardButton('Bangarada Manushya', switch_inline_query_current_chat='Bangarada Manushya'),
    InlineKeyboardButton('Dampati', switch_inline_query_current_chat='Dampati'),
],
[
    InlineKeyboardButton('Shubhamangala', switch_inline_query_current_chat='Shubhamangala'),
    InlineKeyboardButton('Kasturi Nivasa', switch_inline_query_current_chat='Kasturi Nivasa'),
],
[
    InlineKeyboardButton('Avala Hejje', switch_inline_query_current_chat='Avala Hejje'),
    InlineKeyboardButton('Devara Kannu', switch_inline_query_current_chat='Devara Kannu'),
],
[
    InlineKeyboardButton('Bhakta Prahlada', switch_inline_query_current_chat='Bhakta Prahlada'),
    InlineKeyboardButton('Bhagyada Bagilu', switch_inline_query_current_chat='Bhagyada Bagilu'),
],
[
    InlineKeyboardButton('Babruvahana', switch_inline_query_current_chat='Babruvahana'),
    InlineKeyboardButton('Bhale Huchcha', switch_inline_query_current_chat='Bhale Huchcha'),
],
[
    InlineKeyboardButton('Kutturu Hennu', switch_inline_query_current_chat='Kutturu Hennu'),
    InlineKeyboardButton('Kittu Puttu', switch_inline_query_current_chat='Kittu Puttu'),
],
[
    InlineKeyboardButton('Bhale Adrushtavo Adrushta', switch_inline_query_current_chat='Bhale Adrushtavo Adrushta'),
    InlineKeyboardButton('Upendra', switch_inline_query_current_chat='Upendra'),
],
[
    InlineKeyboardButton('H20', switch_inline_query_current_chat='H20'),
    InlineKeyboardButton('Duniya', switch_inline_query_current_chat='Duniya'),
],
[
    InlineKeyboardButton('Milana', switch_inline_query_current_chat='Milana'),
    InlineKeyboardButton('Mussanje Maathu', switch_inline_query_current_chat='Mussanje Maathu'),
],
[
    InlineKeyboardButton('Birugali', switch_inline_query_current_chat='Birugali'),
    InlineKeyboardButton('Sanju Weds Geetha', switch_inline_query_current_chat='Sanju Weds Geetha'),
],
[
    InlineKeyboardButton('Jolly Days', switch_inline_query_current_chat='Jolly Days'),
    InlineKeyboardButton('Moggina Manasu', switch_inline_query_current_chat='Moggina Manasu'),
],
[
    InlineKeyboardButton('Uyyale', switch_inline_query_current_chat='Uyyale'),
    InlineKeyboardButton('Buddhivantha', switch_inline_query_current_chat='Buddhivantha'),
],
[
    InlineKeyboardButton('Gunavantha', switch_inline_query_current_chat='Gunavantha'),
    InlineKeyboardButton('Mylari', switch_inline_query_current_chat='Mylari'),
],
[
    InlineKeyboardButton('Anatharu', switch_inline_query_current_chat='Anatharu'),
    InlineKeyboardButton('Aa Dinagalu', switch_inline_query_current_chat='Aa Dinagalu'),
],
[
    InlineKeyboardButton('Shyloo', switch_inline_query_current_chat='Shyloo'),
    InlineKeyboardButton('Sanju', switch_inline_query_current_chat='Sanju'),
],
[
    InlineKeyboardButton('Bannada Gejje', switch_inline_query_current_chat='Bannada Gejje'),
    InlineKeyboardButton('Baa Nalle Madhuchandrake', switch_inline_query_current_chat='Baa Nalle Madhuchandrake'),
],
[
    InlineKeyboardButton('Aa Eradu Varshagalu', switch_inline_query_current_chat='Aa Eradu Varshagalu'),
    InlineKeyboardButton('Huli', switch_inline_query_current_chat='Huli'),
],
[
    InlineKeyboardButton('Kotigobba', switch_inline_query_current_chat='Kotigobba'),
    InlineKeyboardButton('Kiccha Huccha', switch_inline_query_current_chat='Kiccha Huccha'),
],
[
    InlineKeyboardButton('Veera Parampare', switch_inline_query_current_chat='Veera Parampare'),
    InlineKeyboardButton('Jackie', switch_inline_query_current_chat='Jackie'),
],
[
    InlineKeyboardButton('Kempegowda', switch_inline_query_current_chat='Kempegowda'),
    InlineKeyboardButton('Vishnuvardhana', switch_inline_query_current_chat='Vishnuvardhana'),
],
[
    InlineKeyboardButton('Anna Bond', switch_inline_query_current_chat='Anna Bond'),
    InlineKeyboardButton('Bhajarangi', switch_inline_query_current_chat='Bhajarangi'),
],
[
    InlineKeyboardButton('Bulbul', switch_inline_query_current_chat='Bulbul'),
    InlineKeyboardButton('Mythri', switch_inline_query_current_chat='Mythri'),
],
[
    InlineKeyboardButton('Vajrakaya', switch_inline_query_current_chat='Vajrakaya'),
    InlineKeyboardButton('Doddmane Hudga', switch_inline_query_current_chat='Doddmane Hudga'),
],
[
    InlineKeyboardButton('Rajakumara', switch_inline_query_current_chat='Rajakumara'),
    InlineKeyboardButton('Hebbuli', switch_inline_query_current_chat='Hebbuli'),
],
[
    InlineKeyboardButton('The Villain', switch_inline_query_current_chat='The Villain'),
    InlineKeyboardButton('KGF: Chapter 1', switch_inline_query_current_chat='KGF: Chapter 1'),
],
[
    InlineKeyboardButton('Yajamana', switch_inline_query_current_chat='Yajamana'),
    InlineKeyboardButton('Pailwaan', switch_inline_query_current_chat='Pailwaan'),
],
[
    InlineKeyboardButton('Kurukshetra', switch_inline_query_current_chat='Kurukshetra'),
    InlineKeyboardButton('Bharaate', switch_inline_query_current_chat='Bharaate'),
],
[
    InlineKeyboardButton('Love Mocktail', switch_inline_query_current_chat='Love Mocktail'),
    InlineKeyboardButton('Dia', switch_inline_query_current_chat='Dia'),
],
[
    InlineKeyboardButton('Shivaji Surathkal', switch_inline_query_current_chat='Shivaji Surathkal'),
    InlineKeyboardButton('Law', switch_inline_query_current_chat='Law'),
],
[
    InlineKeyboardButton('Bheemasena Nalamaharaja', switch_inline_query_current_chat='Bheemasena Nalamaharaja'),
    InlineKeyboardButton('French Biriyani', switch_inline_query_current_chat='French Biriyani'),
],
[
    InlineKeyboardButton('Roberrt', switch_inline_query_current_chat='Roberrt'),
    InlineKeyboardButton('Pogaru', switch_inline_query_current_chat='Pogaru'),
],
[
    InlineKeyboardButton('Bhajarangi 2', switch_inline_query_current_chat='Bhajarangi 2'),
    InlineKeyboardButton('Yuvarathnaa', switch_inline_query_current_chat='Yuvarathnaa'),
],
[
    InlineKeyboardButton('James', switch_inline_query_current_chat='James'),
    InlineKeyboardButton('Phantom', switch_inline_query_current_chat='Phantom')
],[
    InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="kannada")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Biography":
        buttons = [ [
    InlineKeyboardButton('Bhaag Milkha Bhaag', switch_inline_query_current_chat='Bhaag Milkha Bhaag'),
    InlineKeyboardButton('Dangal', switch_inline_query_current_chat='Dangal'),
],
[
    InlineKeyboardButton('Mary Kom', switch_inline_query_current_chat='Mary Kom'),
    InlineKeyboardButton('The Dirty Picture', switch_inline_query_current_chat='The Dirty Picture'),
],
[
    InlineKeyboardButton('Neerja', switch_inline_query_current_chat='Neerja'),
    InlineKeyboardButton('M.S. Dhoni: The Untold Story', switch_inline_query_current_chat='M.S. Dhoni: The Untold Story'),
],
[
    InlineKeyboardButton('Sarbjit', switch_inline_query_current_chat='Sarbjit'),
    InlineKeyboardButton('Paan Singh Tomar', switch_inline_query_current_chat='Paan Singh Tomar'),
],
[
    InlineKeyboardButton('Guru', switch_inline_query_current_chat='Guru'),
    InlineKeyboardButton('Gandhi, My Father', switch_inline_query_current_chat='Gandhi, My Father'),
],
[
    InlineKeyboardButton('Manjhi: The Mountain Man', switch_inline_query_current_chat='Manjhi: The Mountain Man'),
    InlineKeyboardButton('The Legend of Bhagat Singh', switch_inline_query_current_chat='The Legend of Bhagat Singh'),
],
[
    InlineKeyboardButton('Hawaizaada', switch_inline_query_current_chat='Hawaizaada'),
    InlineKeyboardButton('Sardar', switch_inline_query_current_chat='Sardar'),
],
[
    InlineKeyboardButton('Jodhaa Akbar', switch_inline_query_current_chat='Jodhaa Akbar'),
    InlineKeyboardButton('Sardar Udham', switch_inline_query_current_chat='Sardar Udham'),
],
[
    InlineKeyboardButton('Shakeela', switch_inline_query_current_chat='Shakeela'),
    InlineKeyboardButton('Prithviraj (Upcoming)', switch_inline_query_current_chat='Prithviraj (Upcoming)'),
],
[
    InlineKeyboardButton('Shershaah', switch_inline_query_current_chat='Shershaah'),
    InlineKeyboardButton('Shabaash Mithu', switch_inline_query_current_chat='Shabaash Mithu'),
],
[
    InlineKeyboardButton('Rani Lakshmi Bai', switch_inline_query_current_chat='Rani Lakshmi Bai'),
    InlineKeyboardButton('Harivu', switch_inline_query_current_chat='Harivu'),
],
[
    InlineKeyboardButton('Dasharatham', switch_inline_query_current_chat='Dasharatham'),
    InlineKeyboardButton('Bhagvad Gita', switch_inline_query_current_chat='Bhagvad Gita'),
],
[
    InlineKeyboardButton('Jugaad', switch_inline_query_current_chat='Jugaad'),
    InlineKeyboardButton('Ramanujan', switch_inline_query_current_chat='Ramanujan'),
],
[
    InlineKeyboardButton('Bawandar', switch_inline_query_current_chat='Bawandar'),
    InlineKeyboardButton('Sachin: A Billion Dreams', switch_inline_query_current_chat='Sachin: A Billion Dreams'),
],
[
    InlineKeyboardButton('Shivaay (Biopic of Neerja Bhanot)', switch_inline_query_current_chat='Shivaay (Biopic of Neerja Bhanot)'),
    InlineKeyboardButton('Bala', switch_inline_query_current_chat='Bala'),
],
[
    InlineKeyboardButton('Mohenjo Daro (Biopic of Sarman)', switch_inline_query_current_chat='Mohenjo Daro (Biopic of Sarman)'),
    InlineKeyboardButton('Phamous (Biopic of Radhe Shyam)', switch_inline_query_current_chat='Phamous (Biopic of Radhe Shyam)'),
],
[
    InlineKeyboardButton('Pad Man', switch_inline_query_current_chat='Pad Man'),
    InlineKeyboardButton('Har Ghar Kuch Kehta Hai', switch_inline_query_current_chat='Har Ghar Kuch Kehta Hai'),
],
[
    InlineKeyboardButton('Gattu', switch_inline_query_current_chat='Gattu'),
    InlineKeyboardButton('Bose: Dead/Alive (Web Series)', switch_inline_query_current_chat='Bose: Dead/Alive (Web Series)'),
],
[
    InlineKeyboardButton('Modi: Journey of a Common Man (Web Series)', switch_inline_query_current_chat='Modi: Journey of a Common Man (Web Series)'),
    InlineKeyboardButton('Inside Edge (Web Series)', switch_inline_query_current_chat='Inside Edge (Web Series)'),
],
[
    InlineKeyboardButton('The Forgotten Army (Web Series)', switch_inline_query_current_chat='The Forgotten Army (Web Series)'),
    InlineKeyboardButton('Chhapaak', switch_inline_query_current_chat='Chhapaak'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Mystery":
        buttons = [ [
    InlineKeyboardButton('Kahaani', switch_inline_query_current_chat='Kahaani'),
    InlineKeyboardButton('Talvar', switch_inline_query_current_chat='Talvar'),
],
[
    InlineKeyboardButton('Drishyam', switch_inline_query_current_chat='Drishyam'),
    InlineKeyboardButton('Talaash: The Answer Lies Within', switch_inline_query_current_chat='Talaash: The Answer Lies Within'),
],
[
    InlineKeyboardButton('Gupt: The Hidden Truth', switch_inline_query_current_chat='Gupt: The Hidden Truth'),
    InlineKeyboardButton('Karthik Calling Karthik', switch_inline_query_current_chat='Karthik Calling Karthik'),
],
[
    InlineKeyboardButton('Bhool Bhulaiyaa', switch_inline_query_current_chat='Bhool Bhulaiyaa'),
    InlineKeyboardButton('Murder', switch_inline_query_current_chat='Murder'),
],
[
    InlineKeyboardButton('Johnny Gaddaar', switch_inline_query_current_chat='Johnny Gaddaar'),
    InlineKeyboardButton('Samay: When Time Strikes', switch_inline_query_current_chat='Samay: When Time Strikes'),
],
[
    InlineKeyboardButton('The Stoneman Murders', switch_inline_query_current_chat='The Stoneman Murders'),
    InlineKeyboardButton('Kaun', switch_inline_query_current_chat='Kaun'),
],
[
    InlineKeyboardButton('Guzaarish', switch_inline_query_current_chat='Guzaarish'),
    InlineKeyboardButton('Rahasya', switch_inline_query_current_chat='Rahasya'),
],
[
    InlineKeyboardButton('Manorama Six Feet Under', switch_inline_query_current_chat='Manorama Six Feet Under'),
    InlineKeyboardButton('100 Days', switch_inline_query_current_chat='100 Days'),
],
[
    InlineKeyboardButton('Te3n', switch_inline_query_current_chat='Te3n'),
    InlineKeyboardButton('Kaabil', switch_inline_query_current_chat='Kaabil'),
],
[
    InlineKeyboardButton('Aks', switch_inline_query_current_chat='Aks'),
    InlineKeyboardButton('Ugly', switch_inline_query_current_chat='Ugly'),
],
[
    InlineKeyboardButton('Ek Hasina Thi', switch_inline_query_current_chat='Ek Hasina Thi'),
    InlineKeyboardButton('Geraftaar', switch_inline_query_current_chat='Geraftaar'),
],
[
    InlineKeyboardButton('No Smoking', switch_inline_query_current_chat='No Smoking'),
    InlineKeyboardButton('X: Past Is Present', switch_inline_query_current_chat='X: Past Is Present'),
],
[
    InlineKeyboardButton('Tum Mere Ho', switch_inline_query_current_chat='Tum Mere Ho'),
    InlineKeyboardButton('Teen', switch_inline_query_current_chat='Teen'),
],
[
    InlineKeyboardButton('8 x 10 Tasveer', switch_inline_query_current_chat='8 x 10 Tasveer'),
    InlineKeyboardButton('404: Error Not Found', switch_inline_query_current_chat='404: Error Not Found'),
],
[
    InlineKeyboardButton('13B: Fear Has a New Address', switch_inline_query_current_chat='13B: Fear Has a New Address'),
    InlineKeyboardButton('Jannat', switch_inline_query_current_chat='Jannat'),
],
[
    InlineKeyboardButton('Ittefaq (1969)', switch_inline_query_current_chat='Ittefaq (1969)'),
    InlineKeyboardButton('Ittefaq (2017)', switch_inline_query_current_chat='Ittefaq (2017)'),
],
[
    InlineKeyboardButton('Jigsaw (Dubbed in Hindi)', switch_inline_query_current_chat='Jigsaw (Dubbed in Hindi)'),
    InlineKeyboardButton('Raaz: The Mystery Continues', switch_inline_query_current_chat='Raaz: The Mystery Continues'),
],
[
    InlineKeyboardButton('Koi Mil Gaya', switch_inline_query_current_chat='Koi Mil Gaya'),
    InlineKeyboardButton('Krrish', switch_inline_query_current_chat='Krrish'),
],
[
    InlineKeyboardButton('Krrish 3', switch_inline_query_current_chat='Krrish 3'),
    InlineKeyboardButton('Hawa', switch_inline_query_current_chat='Hawa'),
],
[
    InlineKeyboardButton('Rahasya', switch_inline_query_current_chat='Rahasya'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Horror":
        buttons = [ [
    InlineKeyboardButton('Raaz', switch_inline_query_current_chat='Raaz'),
    InlineKeyboardButton('Bhoot', switch_inline_query_current_chat='Bhoot'),
],
[
    InlineKeyboardButton('Darna Mana Hai', switch_inline_query_current_chat='Darna Mana Hai'),
    InlineKeyboardButton('Bhool Bhulaiyaa', switch_inline_query_current_chat='Bhool Bhulaiyaa'),
],
[
    InlineKeyboardButton('1920', switch_inline_query_current_chat='1920'),
    InlineKeyboardButton('Raaz: The Mystery Continues', switch_inline_query_current_chat='Raaz: The Mystery Continues'),
],
[
    InlineKeyboardButton('Haunted - 3D', switch_inline_query_current_chat='Haunted - 3D'),
    InlineKeyboardButton('Ragini MMS', switch_inline_query_current_chat='Ragini MMS'),
],
[
    InlineKeyboardButton('Pari', switch_inline_query_current_chat='Pari'),
    InlineKeyboardButton('Stree', switch_inline_query_current_chat='Stree'),
],
[
    InlineKeyboardButton('Tumbbad', switch_inline_query_current_chat='Tumbbad'),
    InlineKeyboardButton('Pari', switch_inline_query_current_chat='Pari'),
],
[
    InlineKeyboardButton('Darna Zaroori Hai', switch_inline_query_current_chat='Darna Zaroori Hai'),
    InlineKeyboardButton('Raat', switch_inline_query_current_chat='Raat'),
],
[
    InlineKeyboardButton('Pizza', switch_inline_query_current_chat='Pizza'),
    InlineKeyboardButton('Ek Thi Daayan', switch_inline_query_current_chat='Ek Thi Daayan'),
],
[
    InlineKeyboardButton('Ragini MMS 2', switch_inline_query_current_chat='Ragini MMS 2'),
    InlineKeyboardButton('Go Goa Gone', switch_inline_query_current_chat='Go Goa Gone'),
],
[
    InlineKeyboardButton('13B: Fear Has a New Address', switch_inline_query_current_chat='13B: Fear Has a New Address'),
    InlineKeyboardButton('Horror Story', switch_inline_query_current_chat='Horror Story'),
],
[
    InlineKeyboardButton('Phoonk', switch_inline_query_current_chat='Phoonk'),
    InlineKeyboardButton('Alone', switch_inline_query_current_chat='Alone'),
],
[
    InlineKeyboardButton('1920: Evil Returns', switch_inline_query_current_chat='1920: Evil Returns'),
    InlineKeyboardButton('Dobaara: See Your Evil', switch_inline_query_current_chat='Dobaara: See Your Evil'),
],
[
    InlineKeyboardButton('Lupt', switch_inline_query_current_chat='Lupt'),
    InlineKeyboardButton('The House Next Door', switch_inline_query_current_chat='The House Next Door'),
],
[
    InlineKeyboardButton('Amavas', switch_inline_query_current_chat='Amavas'),
    InlineKeyboardButton('Tumbbad', switch_inline_query_current_chat='Tumbbad'),
],
[
    InlineKeyboardButton('Kaal', switch_inline_query_current_chat='Kaal'),
    InlineKeyboardButton('Bhoot: Part One - The Haunted Ship', switch_inline_query_current_chat='Bhoot: Part One - The Haunted Ship'),
],
[
    InlineKeyboardButton('Roohi', switch_inline_query_current_chat='Roohi'),
    InlineKeyboardButton('Pari', switch_inline_query_current_chat='Pari'),
],
[
    InlineKeyboardButton('Darna Zaroori Hai', switch_inline_query_current_chat='Darna Zaroori Hai'),
    InlineKeyboardButton('The Conjuring 2 (Dubbed in Hindi)', switch_inline_query_current_chat='The Conjuring 2 (Dubbed in Hindi)'),
],
[
    InlineKeyboardButton('The Nun (Dubbed in Hindi)', switch_inline_query_current_chat='The Nun (Dubbed in Hindi)'),
    InlineKeyboardButton('Annabelle: Creation (Dubbed in Hindi)', switch_inline_query_current_chat='Annabelle: Creation (Dubbed in Hindi)'),
],
[
    InlineKeyboardButton('Pari', switch_inline_query_current_chat='Pari'),
    InlineKeyboardButton('Bhool Bhulaiyaa 2', switch_inline_query_current_chat='Bhool Bhulaiyaa 2'),
],
[
    InlineKeyboardButton('Bhoot Police', switch_inline_query_current_chat='Bhoot Police'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Drama":
        buttons = [ [
    InlineKeyboardButton('Dilwale Dulhania Le Jayenge', switch_inline_query_current_chat='Dilwale Dulhania Le Jayenge'),
    InlineKeyboardButton('Kabhi Khushi Kabhie Gham', switch_inline_query_current_chat='Kabhi Khushi Kabhie Gham'),
],
[
    InlineKeyboardButton('Dil Chahta Hai', switch_inline_query_current_chat='Dil Chahta Hai'),
    InlineKeyboardButton('Taare Zameen Par', switch_inline_query_current_chat='Taare Zameen Par'),
],
[
    InlineKeyboardButton('Rang De Basanti', switch_inline_query_current_chat='Rang De Basanti'),
    InlineKeyboardButton('Lagaan', switch_inline_query_current_chat='Lagaan'),
],
[
    InlineKeyboardButton('Dil Se..', switch_inline_query_current_chat='Dil Se..'),
    InlineKeyboardButton('Swades', switch_inline_query_current_chat='Swades'),
],
[
    InlineKeyboardButton('Devdas', switch_inline_query_current_chat='Devdas'),
    InlineKeyboardButton('Bajrangi Bhaijaan', switch_inline_query_current_chat='Bajrangi Bhaijaan'),
],
[
    InlineKeyboardButton('My Name Is Khan', switch_inline_query_current_chat='My Name Is Khan'),
    InlineKeyboardButton('Rockstar', switch_inline_query_current_chat='Rockstar'),
],
[
    InlineKeyboardButton('A Wednesday', switch_inline_query_current_chat='A Wednesday'),
    InlineKeyboardButton('Barfi!', switch_inline_query_current_chat='Barfi!'),
],
[
    InlineKeyboardButton('Haider', switch_inline_query_current_chat='Haider'),
    InlineKeyboardButton('Pink', switch_inline_query_current_chat='Pink'),
],
[
    InlineKeyboardButton('Piku', switch_inline_query_current_chat='Piku'),
    InlineKeyboardButton('Udta Punjab', switch_inline_query_current_chat='Udta Punjab'),
],
[
    InlineKeyboardButton('Kapoor & Sons', switch_inline_query_current_chat='Kapoor & Sons'),
    InlineKeyboardButton('Neerja', switch_inline_query_current_chat='Neerja'),
],
[
    InlineKeyboardButton('Mulk', switch_inline_query_current_chat='Mulk'),
    InlineKeyboardButton('Gully Boy', switch_inline_query_current_chat='Gully Boy'),
],
[
    InlineKeyboardButton('Article 15', switch_inline_query_current_chat='Article 15'),
    InlineKeyboardButton('Thappad', switch_inline_query_current_chat='Thappad'),
],
[
    InlineKeyboardButton('Raazi', switch_inline_query_current_chat='Raazi'),
    InlineKeyboardButton('The Lunchbox', switch_inline_query_current_chat='The Lunchbox'),
],
[
    InlineKeyboardButton('Dangal', switch_inline_query_current_chat='Dangal'),
    InlineKeyboardButton('Chhichhore', switch_inline_query_current_chat='Chhichhore'),
],
[
    InlineKeyboardButton('Super 30', switch_inline_query_current_chat='Super 30'),
    InlineKeyboardButton('Drishyam', switch_inline_query_current_chat='Drishyam'),
],
[
    InlineKeyboardButton('Kabir Singh', switch_inline_query_current_chat='Kabir Singh'),
    InlineKeyboardButton('Queen', switch_inline_query_current_chat='Queen'),
],
[
    InlineKeyboardButton('Dear Zindagi', switch_inline_query_current_chat='Dear Zindagi'),
    InlineKeyboardButton('Newton', switch_inline_query_current_chat='Newton'),
],
[
    InlineKeyboardButton('Masaan', switch_inline_query_current_chat='Masaan'),
    InlineKeyboardButton('Black', switch_inline_query_current_chat='Black'),
],
[
    InlineKeyboardButton('Iqbal', switch_inline_query_current_chat='Iqbal'),
    InlineKeyboardButton('Sarbjit', switch_inline_query_current_chat='Sarbjit'),
],
[
    InlineKeyboardButton('Tumhari Sulu', switch_inline_query_current_chat='Tumhari Sulu'),
    InlineKeyboardButton('Shubh Mangal Saavdhan', switch_inline_query_current_chat='Shubh Mangal Saavdhan'),
],
[
    InlineKeyboardButton('Andhadhun', switch_inline_query_current_chat='Andhadhun'),
    InlineKeyboardButton('Kaabil', switch_inline_query_current_chat='Kaabil'),
],
[
    InlineKeyboardButton('Fanaa', switch_inline_query_current_chat='Fanaa'),
    InlineKeyboardButton('Wake Up Sid', switch_inline_query_current_chat='Wake Up Sid'),
],
[
    InlineKeyboardButton('Tum Mile', switch_inline_query_current_chat='Tum Mile'),
    InlineKeyboardButton('No One Killed Jessica', switch_inline_query_current_chat='No One Killed Jessica'),
],
[
    InlineKeyboardButton('Hichki', switch_inline_query_current_chat='Hichki'),
    InlineKeyboardButton('Shahid', switch_inline_query_current_chat='Shahid'),
],
[
    InlineKeyboardButton('Omkara', switch_inline_query_current_chat='Omkara'),
    InlineKeyboardButton('Goliyon Ki Raasleela Ram-Leela', switch_inline_query_current_chat='Goliyon Ki Raasleela Ram-Leela'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Comedy":
        buttons = [ [
    InlineKeyboardButton('Andaz Apna Apna', switch_inline_query_current_chat='Andaz Apna Apna'),
    InlineKeyboardButton('Hera Pheri', switch_inline_query_current_chat='Hera Pheri'),
],
[
    InlineKeyboardButton('Chupke Chupke', switch_inline_query_current_chat='Chupke Chupke'),
    InlineKeyboardButton('Dhamaal', switch_inline_query_current_chat='Dhamaal'),
],
[
    InlineKeyboardButton('Golmaal: Fun Unlimited', switch_inline_query_current_chat='Golmaal: Fun Unlimited'),
    InlineKeyboardButton('No Entry', switch_inline_query_current_chat='No Entry'),
],
[
    InlineKeyboardButton('Munna Bhai M.B.B.S.', switch_inline_query_current_chat='Munna Bhai M.B.B.S.'),
    InlineKeyboardButton('3 Idiots', switch_inline_query_current_chat='3 Idiots'),
],
[
    InlineKeyboardButton('Welcome', switch_inline_query_current_chat='Welcome'),
    InlineKeyboardButton('Housefull', switch_inline_query_current_chat='Housefull'),
],
[
    InlineKeyboardButton('Phir Hera Pheri', switch_inline_query_current_chat='Phir Hera Pheri'),
    InlineKeyboardButton('Dhol', switch_inline_query_current_chat='Dhol'),
],
[
    InlineKeyboardButton('Hungama', switch_inline_query_current_chat='Hungama'),
    InlineKeyboardButton('Bhagam Bhag', switch_inline_query_current_chat='Bhagam Bhag'),
],
[
    InlineKeyboardButton('Munnabhai S.S.C.', switch_inline_query_current_chat='Munnabhai S.S.C.'),
    InlineKeyboardButton('Malamaal Weekly', switch_inline_query_current_chat='Malamaal Weekly'),
],
[
    InlineKeyboardButton('Judwaa', switch_inline_query_current_chat='Judwaa'),
    InlineKeyboardButton('Bawarchi', switch_inline_query_current_chat='Bawarchi'),
],
[
    InlineKeyboardButton('Padosan', switch_inline_query_current_chat='Padosan'),
    InlineKeyboardButton('Angoor', switch_inline_query_current_chat='Angoor'),
],
[
    InlineKeyboardButton('Dilli Ka Thug', switch_inline_query_current_chat='Dilli Ka Thug'),
    InlineKeyboardButton('Khatta Meetha', switch_inline_query_current_chat='Khatta Meetha'),
],
[
    InlineKeyboardButton('Amar Akbar Anthony', switch_inline_query_current_chat='Amar Akbar Anthony'),
    InlineKeyboardButton('Half Ticket', switch_inline_query_current_chat='Half Ticket'),
],
[
    InlineKeyboardButton('Chhoti Si Baat', switch_inline_query_current_chat='Chhoti Si Baat'),
    InlineKeyboardButton('Chhoti Si Baat', switch_inline_query_current_chat='Chhoti Si Baat'),
],
[
    InlineKeyboardButton('Namak Halaal', switch_inline_query_current_chat='Namak Halaal'),
    InlineKeyboardButton('Khoobsurat (1980)', switch_inline_query_current_chat='Khoobsurat (1980)'),
],
[
    InlineKeyboardButton('Naram Garam', switch_inline_query_current_chat='Naram Garam'),
    InlineKeyboardButton('Rang Birangi', switch_inline_query_current_chat='Rang Birangi'),
],
[
    InlineKeyboardButton('Kissi Se Na Kehna', switch_inline_query_current_chat='Kissi Se Na Kehna'),
    InlineKeyboardButton('Khoobsurat (2014)', switch_inline_query_current_chat='Khoobsurat (2014)'),
],
[
    InlineKeyboardButton('Hera Pheri (2000)', switch_inline_query_current_chat='Hera Pheri (2000)'),
    InlineKeyboardButton('Chup Chup Ke', switch_inline_query_current_chat='Chup Chup Ke'),
],
[
    InlineKeyboardButton('Bhool Bhulaiyaa', switch_inline_query_current_chat='Bhool Bhulaiyaa'),
    InlineKeyboardButton('Malamaal Weekly', switch_inline_query_current_chat='Malamaal Weekly'),
],
[
    InlineKeyboardButton('Singh Is Kinng', switch_inline_query_current_chat='Singh Is Kinng'),
    InlineKeyboardButton('Welcome (2007)', switch_inline_query_current_chat='Welcome (2007)'),
],
[
    InlineKeyboardButton('Housefull 2', switch_inline_query_current_chat='Housefull 2'),
    InlineKeyboardButton('Bol Bachchan', switch_inline_query_current_chat='Bol Bachchan'),
],
[
    InlineKeyboardButton('OMG – Oh My God!', switch_inline_query_current_chat='OMG – Oh My God!'),
    InlineKeyboardButton('Bheja Fry', switch_inline_query_current_chat='Bheja Fry'),
],
[
    InlineKeyboardButton('Khosla Ka Ghosla', switch_inline_query_current_chat='Khosla Ka Ghosla'),
    InlineKeyboardButton('102 Not Out', switch_inline_query_current_chat='102 Not Out'),
],
[
    InlineKeyboardButton('Bareilly Ki Barfi', switch_inline_query_current_chat='Bareilly Ki Barfi'),
    InlineKeyboardButton('Bhool Bhulaiyaa', switch_inline_query_current_chat='Bhool Bhulaiyaa'),
],
[
    InlineKeyboardButton('Delhi Belly', switch_inline_query_current_chat='Delhi Belly'),
    InlineKeyboardButton('Piku', switch_inline_query_current_chat='Piku'),
],
[
    InlineKeyboardButton('Badhaai Ho', switch_inline_query_current_chat='Badhaai Ho'),
    InlineKeyboardButton('Stree', switch_inline_query_current_chat='Stree'),
],
[
    InlineKeyboardButton('Badhaai Do', switch_inline_query_current_chat='Badhaai Do'),
    InlineKeyboardButton('Bareilly Ki Barfi', switch_inline_query_current_chat='Bareilly Ki Barfi'),
],
[
    InlineKeyboardButton('Fukrey', switch_inline_query_current_chat='Fukrey'),
    InlineKeyboardButton('Sonu Ke Titu Ki Sweety', switch_inline_query_current_chat='Sonu Ke Titu Ki Sweety'),
],
[
    InlineKeyboardButton('Dream Girl', switch_inline_query_current_chat='Dream Girl'),
    InlineKeyboardButton('Khosla Ka Ghosla', switch_inline_query_current_chat='Khosla Ka Ghosla'),
],
[
    InlineKeyboardButton('Masti', switch_inline_query_current_chat='Masti'),
    InlineKeyboardButton('Great Grand Masti', switch_inline_query_current_chat='Great Grand Masti'),
],
[
    InlineKeyboardButton('Mujhse Shaadi Karogi', switch_inline_query_current_chat='Mujhse Shaadi Karogi'),
    InlineKeyboardButton('De Dana Dan', switch_inline_query_current_chat='De Dana Dan'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "Action":
        buttons = [ [
    InlineKeyboardButton('Sholay', switch_inline_query_current_chat='Sholay'),
    InlineKeyboardButton('Deewar', switch_inline_query_current_chat='Deewar'),
],
[
    InlineKeyboardButton('Dhoom', switch_inline_query_current_chat='Dhoom'),
    InlineKeyboardButton('Singham', switch_inline_query_current_chat='Singham'),
],
[
    InlineKeyboardButton('Dabangg', switch_inline_query_current_chat='Dabangg'),
    InlineKeyboardButton('Baaghi', switch_inline_query_current_chat='Baaghi'),
],
[
    InlineKeyboardButton('Don', switch_inline_query_current_chat='Don'),
    InlineKeyboardButton('War', switch_inline_query_current_chat='War'),
],
[
    InlineKeyboardButton('Kick', switch_inline_query_current_chat='Kick'),
    InlineKeyboardButton('Gunday', switch_inline_query_current_chat='Gunday'),
],
[
    InlineKeyboardButton('Ghajini', switch_inline_query_current_chat='Ghajini'),
    InlineKeyboardButton('Khiladi', switch_inline_query_current_chat='Khiladi'),
],
[
    InlineKeyboardButton('Rowdy Rathore', switch_inline_query_current_chat='Rowdy Rathore'),
    InlineKeyboardButton('Wanted', switch_inline_query_current_chat='Wanted'),
],
[
    InlineKeyboardButton('Simmba', switch_inline_query_current_chat='Simmba'),
    InlineKeyboardButton('Shootout at Wadala', switch_inline_query_current_chat='Shootout at Wadala'),
],
[
    InlineKeyboardButton('Singham Returns', switch_inline_query_current_chat='Singham Returns'),
    InlineKeyboardButton('Ek Tha Tiger', switch_inline_query_current_chat='Ek Tha Tiger'),
],
[
    InlineKeyboardButton('Ek Villain', switch_inline_query_current_chat='Ek Villain'),
    InlineKeyboardButton('Chennai Express', switch_inline_query_current_chat='Chennai Express'),
],
[
    InlineKeyboardButton('Agneepath', switch_inline_query_current_chat='Agneepath'),
    InlineKeyboardButton('Baahubali: The Beginning', switch_inline_query_current_chat='Baahubali: The Beginning'),
],
[
    InlineKeyboardButton('Baahubali 2: The Conclusion', switch_inline_query_current_chat='Baahubali 2: The Conclusion'),
    InlineKeyboardButton('Bang Bang!', switch_inline_query_current_chat='Bang Bang!'),
],
[
    InlineKeyboardButton('Krrish', switch_inline_query_current_chat='Krrish'),
    InlineKeyboardButton('Krrish 3', switch_inline_query_current_chat='Krrish 3'),
],
[
    InlineKeyboardButton('Baby', switch_inline_query_current_chat='Baby'),
    InlineKeyboardButton('Rocky Handsome', switch_inline_query_current_chat='Rocky Handsome'),
],
[
    InlineKeyboardButton('Commando: A One Man Army', switch_inline_query_current_chat='Commando: A One Man Army'),
    InlineKeyboardButton('Singham 2', switch_inline_query_current_chat='Singham 2'),
],
[
    InlineKeyboardButton('Gabbar Is Back', switch_inline_query_current_chat='Gabbar Is Back'),
    InlineKeyboardButton('Bajrangi Bhaijaan', switch_inline_query_current_chat='Bajrangi Bhaijaan'),
],
[
    InlineKeyboardButton('Sultan', switch_inline_query_current_chat='Sultan'),
    InlineKeyboardButton('R... Rajkumar', switch_inline_query_current_chat='R... Rajkumar'),
],
[
    InlineKeyboardButton('Dishoom', switch_inline_query_current_chat='Dishoom'),
    InlineKeyboardButton('Force', switch_inline_query_current_chat='Force'),
],
[
    InlineKeyboardButton('Uri: The Surgical Strike', switch_inline_query_current_chat='Uri: The Surgical Strike'),
    InlineKeyboardButton('Brothers', switch_inline_query_current_chat='Brothers'),
],
[
    InlineKeyboardButton('Ek Villain', switch_inline_query_current_chat='Ek Villain'),
    InlineKeyboardButton('Goliyon Ki Raasleela Ram-Leela', switch_inline_query_current_chat='Goliyon Ki Raasleela Ram-Leela'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "type0":
        buttons = [  [
                InlineKeyboardButton("Action", callback_data="Action")
            ],[ InlineKeyboardButton("Comedy ", callback_data="Comedy")
              ],[ InlineKeyboardButton("Drama", callback_data="Drama")
                  ],[ InlineKeyboardButton("Horror", callback_data="Horror")
                    ],[ InlineKeyboardButton("Mystery", callback_data="Mystery")
                    ],[ InlineKeyboardButton("Biography", callback_data="Biography")
                    ],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "RanveerSingh":
        buttons = [ [
    InlineKeyboardButton('Band Baaja Baaraat', switch_inline_query_current_chat='Band Baaja Baaraat'),
    InlineKeyboardButton('Ladies vs Ricky Bahl', switch_inline_query_current_chat='Ladies vs Ricky Bahl'),
],
[
    InlineKeyboardButton('Lootera', switch_inline_query_current_chat='Lootera'),
    InlineKeyboardButton('Goliyon Ki Raasleela Ram-Leela', switch_inline_query_current_chat='Goliyon Ki Raasleela Ram-Leela'),
],
[
    InlineKeyboardButton('Gunday', switch_inline_query_current_chat='Gunday'),
    InlineKeyboardButton('Dil Dhadakne Do', switch_inline_query_current_chat='Dil Dhadakne Do'),
],
[
    InlineKeyboardButton('Bajirao Mastani', switch_inline_query_current_chat='Bajirao Mastani'),
    InlineKeyboardButton('Befikre', switch_inline_query_current_chat='Befikre'),
],
[
    InlineKeyboardButton('Padmaavat', switch_inline_query_current_chat='Padmaavat'),
    InlineKeyboardButton('Simmba', switch_inline_query_current_chat='Simmba'),
],
[
    InlineKeyboardButton('Gully Boy', switch_inline_query_current_chat='Gully Boy'),
    InlineKeyboardButton('83', switch_inline_query_current_chat='83'),
],
[
    InlineKeyboardButton('Jayeshbhai Jordaar', switch_inline_query_current_chat='Jayeshbhai Jordaar'),
    InlineKeyboardButton('Cirkus', switch_inline_query_current_chat='Cirkus'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "AjayDevgn":
        buttons = [ [
    InlineKeyboardButton('Phool Aur Kaante', switch_inline_query_current_chat='Phool Aur Kaante'),
    InlineKeyboardButton('Jigar', switch_inline_query_current_chat='Jigar'),
],
[
    InlineKeyboardButton('Dilwale', switch_inline_query_current_chat='Dilwale'),
    InlineKeyboardButton('Divya Shakti', switch_inline_query_current_chat='Divya Shakti'),
],
[
    InlineKeyboardButton('Diljale', switch_inline_query_current_chat='Diljale'),
    InlineKeyboardButton('Jaan', switch_inline_query_current_chat='Jaan'),
],
[
    InlineKeyboardButton('Itihaas', switch_inline_query_current_chat='Itihaas'),
    InlineKeyboardButton('Jung', switch_inline_query_current_chat='Jung'),
],
[
    InlineKeyboardButton('Dil Kya Kare', switch_inline_query_current_chat='Dil Kya Kare'),
    InlineKeyboardButton('Hum Dil De Chuke Sanam', switch_inline_query_current_chat='Hum Dil De Chuke Sanam'),
],
[
    InlineKeyboardButton('Deewangee', switch_inline_query_current_chat='Deewangee'),
    InlineKeyboardButton('Gangaajal', switch_inline_query_current_chat='Gangaajal'),
],
[
    InlineKeyboardButton('The Legend of Bhagat Singh', switch_inline_query_current_chat='The Legend of Bhagat Singh'),
    InlineKeyboardButton('Qayamat: City Under Threat', switch_inline_query_current_chat='Qayamat: City Under Threat'),
],
[
    InlineKeyboardButton('Bhoot', switch_inline_query_current_chat='Bhoot'),
    InlineKeyboardButton('Zameen', switch_inline_query_current_chat='Zameen'),
],
[
    InlineKeyboardButton('Khakee', switch_inline_query_current_chat='Khakee'),
    InlineKeyboardButton('Masti', switch_inline_query_current_chat='Masti'),
],
[
    InlineKeyboardButton('Raincoat', switch_inline_query_current_chat='Raincoat'),
    InlineKeyboardButton('Taarzan: The Wonder Car', switch_inline_query_current_chat='Taarzan: The Wonder Car'),
],
[
    InlineKeyboardButton('Apaharan', switch_inline_query_current_chat='Apaharan'),
    InlineKeyboardButton('Omkara', switch_inline_query_current_chat='Omkara'),
],
[
    InlineKeyboardButton('Golmaal: Fun Unlimited', switch_inline_query_current_chat='Golmaal: Fun Unlimited'),
    InlineKeyboardButton('Halla Bol', switch_inline_query_current_chat='Halla Bol'),
],
[
    InlineKeyboardButton('Sunday', switch_inline_query_current_chat='Sunday'),
    InlineKeyboardButton('U Me Aur Hum', switch_inline_query_current_chat='U Me Aur Hum'),
],
[
    InlineKeyboardButton('Golmaal Returns', switch_inline_query_current_chat='Golmaal Returns'),
    InlineKeyboardButton('All the Best: Fun Begins', switch_inline_query_current_chat='All the Best: Fun Begins'),
],
[
    InlineKeyboardButton('Atithi Tum Kab Jaoge?', switch_inline_query_current_chat='Atithi Tum Kab Jaoge?'),
    InlineKeyboardButton('Rajneeti', switch_inline_query_current_chat='Rajneeti'),
],
[
    InlineKeyboardButton('Once Upon a Time in Mumbaai', switch_inline_query_current_chat='Once Upon a Time in Mumbaai'),
    InlineKeyboardButton('Aakrosh', switch_inline_query_current_chat='Aakrosh'),
],
[
    InlineKeyboardButton('Golmaal 3', switch_inline_query_current_chat='Golmaal 3'),
    InlineKeyboardButton('Singham', switch_inline_query_current_chat='Singham'),
],
[
    InlineKeyboardButton('Rascals', switch_inline_query_current_chat='Rascals'),
    InlineKeyboardButton('Bol Bachchan', switch_inline_query_current_chat='Bol Bachchan'),
],
[
    InlineKeyboardButton('Son of Sardaar', switch_inline_query_current_chat='Son of Sardaar'),
    InlineKeyboardButton('Himmatwala', switch_inline_query_current_chat='Himmatwala'),
],
[
    InlineKeyboardButton('Satyagraha', switch_inline_query_current_chat='Satyagraha'),
    InlineKeyboardButton('Singham Returns', switch_inline_query_current_chat='Singham Returns'),
],
[
    InlineKeyboardButton('Action Jackson', switch_inline_query_current_chat='Action Jackson'),
    InlineKeyboardButton('Drishyam', switch_inline_query_current_chat='Drishyam'),
],
[
    InlineKeyboardButton('Shivaay', switch_inline_query_current_chat='Shivaay'),
    InlineKeyboardButton('Golmaal Again', switch_inline_query_current_chat='Golmaal Again'),
],
[
    InlineKeyboardButton('Raid', switch_inline_query_current_chat='Raid'),
    InlineKeyboardButton('Total Dhamaal', switch_inline_query_current_chat='Total Dhamaal'),
],
[
    InlineKeyboardButton('De De Pyaar De', switch_inline_query_current_chat='De De Pyaar De'),
    InlineKeyboardButton('Tanhaji: The Unsung Warrior', switch_inline_query_current_chat='Tanhaji: The Unsung Warrior'),
],
[
    InlineKeyboardButton('Bhuj: The Pride of India', switch_inline_query_current_chat='Bhuj: The Pride of India'),
    InlineKeyboardButton('Maidaan', switch_inline_query_current_chat='Maidaan'),
]

,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "HrithikRoshan":
        buttons = [ [
    InlineKeyboardButton('Kaho Naa... Pyaar Hai', switch_inline_query_current_chat='Kaho Naa... Pyaar Hai'),
    InlineKeyboardButton('Fiza', switch_inline_query_current_chat='Fiza'),
],
[
    InlineKeyboardButton('Mission Kashmir', switch_inline_query_current_chat='Mission Kashmir'),
    InlineKeyboardButton('Yaadein', switch_inline_query_current_chat='Yaadein'),
],
[
    InlineKeyboardButton('Kabhi Khushi Kabhie Gham', switch_inline_query_current_chat='Kabhi Khushi Kabhie Gham'),
    InlineKeyboardButton('Aap Mujhe Achche Lagne Lage', switch_inline_query_current_chat='Aap Mujhe Achche Lagne Lage'),
],
[
    InlineKeyboardButton('Na Tum Jaano Na Hum', switch_inline_query_current_chat='Na Tum Jaano Na Hum'),
    InlineKeyboardButton('Mujhse Dosti Karoge!', switch_inline_query_current_chat='Mujhse Dosti Karoge!'),
],
[
    InlineKeyboardButton('Main Prem Ki Diwani Hoon', switch_inline_query_current_chat='Main Prem Ki Diwani Hoon'),
    InlineKeyboardButton('Koi... Mil Gaya', switch_inline_query_current_chat='Koi... Mil Gaya'),
],
[
    InlineKeyboardButton('Lakshya', switch_inline_query_current_chat='Lakshya'),
    InlineKeyboardButton('Krrish', switch_inline_query_current_chat='Krrish'),
],
[
    InlineKeyboardButton('Dhoom 2', switch_inline_query_current_chat='Dhoom 2'),
    InlineKeyboardButton('Jodhaa Akbar', switch_inline_query_current_chat='Jodhaa Akbar'),
],
[
    InlineKeyboardButton('Luck by Chance (Special Appearance)', switch_inline_query_current_chat='Luck by Chance (Special Appearance)'),
    InlineKeyboardButton('Kites', switch_inline_query_current_chat='Kites'),
],
[
    InlineKeyboardButton('Guzaarish', switch_inline_query_current_chat='Guzaarish'),
    InlineKeyboardButton('Zindagi Na Milegi Dobara', switch_inline_query_current_chat='Zindagi Na Milegi Dobara'),
],
[
    InlineKeyboardButton('Agneepath', switch_inline_query_current_chat='Agneepath'),
    InlineKeyboardButton('Krrish 3', switch_inline_query_current_chat='Krrish 3'),
],
[
    InlineKeyboardButton('Bang Bang!', switch_inline_query_current_chat='Bang Bang!'),
    InlineKeyboardButton('Mohenjo Daro', switch_inline_query_current_chat='Mohenjo Daro'),
],
[
    InlineKeyboardButton('Kaabil', switch_inline_query_current_chat='Kaabil'),
    InlineKeyboardButton('Super 30', switch_inline_query_current_chat='Super 30'),
],
[
    InlineKeyboardButton('War', switch_inline_query_current_chat='War'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "RanbirKapoor":
        buttons = [ [
    InlineKeyboardButton('Saawariya', switch_inline_query_current_chat='Saawariya'),
    InlineKeyboardButton('Bachna Ae Haseeno', switch_inline_query_current_chat='Bachna Ae Haseeno'),
],
[
    InlineKeyboardButton('Wake Up Sid', switch_inline_query_current_chat='Wake Up Sid'),
    InlineKeyboardButton('Ajab Prem Ki Ghazab Kahani', switch_inline_query_current_chat='Ajab Prem Ki Ghazab Kahani'),
],
[
    InlineKeyboardButton('Rocket Singh: Salesman of the Year', switch_inline_query_current_chat='Rocket Singh: Salesman of the Year'),
    InlineKeyboardButton('Anjaana Anjaani', switch_inline_query_current_chat='Anjaana Anjaani'),
],
[
    InlineKeyboardButton('Rockstar', switch_inline_query_current_chat='Rockstar'),
    InlineKeyboardButton('Barfi!', switch_inline_query_current_chat='Barfi!'),
],
[
    InlineKeyboardButton('Yeh Jawaani Hai Deewani', switch_inline_query_current_chat='Yeh Jawaani Hai Deewani'),
    InlineKeyboardButton('Besharam', switch_inline_query_current_chat='Besharam'),
],
[
    InlineKeyboardButton('Tamasha', switch_inline_query_current_chat='Tamasha'),
    InlineKeyboardButton('Ae Dil Hai Mushkil', switch_inline_query_current_chat='Ae Dil Hai Mushkil'),
],
[
    InlineKeyboardButton('Jagga Jasoos', switch_inline_query_current_chat='Jagga Jasoos'),
    InlineKeyboardButton('Sanju', switch_inline_query_current_chat='Sanju'),
],
[
    InlineKeyboardButton('Brahmastra', switch_inline_query_current_chat='Brahmastra'),
    InlineKeyboardButton('Shamshera', switch_inline_query_current_chat='Shamshera'),
],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "AkshayKumar":
        buttons = [[
    InlineKeyboardButton('Khiladi', switch_inline_query_current_chat='Khiladi'),
    InlineKeyboardButton('Main Khiladi Tu Anari', switch_inline_query_current_chat='Main Khiladi Tu Anari'),
],
[
    InlineKeyboardButton('Sabse Bada Khiladi', switch_inline_query_current_chat='Sabse Bada Khiladi'),
    InlineKeyboardButton('Khiladiyon Ka Khiladi', switch_inline_query_current_chat='Khiladiyon Ka Khiladi'),
],
[
    InlineKeyboardButton('Mr. and Mrs. Khiladi', switch_inline_query_current_chat='Mr. and Mrs. Khiladi'),
    InlineKeyboardButton('Khiladi 420', switch_inline_query_current_chat='Khiladi 420'),
],
[
    InlineKeyboardButton('Khiladi 786', switch_inline_query_current_chat='Khiladi 786'),
    InlineKeyboardButton('International Khiladi', switch_inline_query_current_chat='International Khiladi'),
],
[
    InlineKeyboardButton('Hera Pheri', switch_inline_query_current_chat='Hera Pheri'),
    InlineKeyboardButton('Dhadkan', switch_inline_query_current_chat='Dhadkan'),
],
[
    InlineKeyboardButton('Bhool Bhulaiyaa', switch_inline_query_current_chat='Bhool Bhulaiyaa'),
    InlineKeyboardButton('Housefull', switch_inline_query_current_chat='Housefull'),
],
[
    InlineKeyboardButton('Housefull 2', switch_inline_query_current_chat='Housefull 2'),
    InlineKeyboardButton('Housefull 3', switch_inline_query_current_chat='Housefull 3'),
],
[
    InlineKeyboardButton('Housefull 4', switch_inline_query_current_chat='Housefull 4'),
    InlineKeyboardButton('Rowdy Rathore', switch_inline_query_current_chat='Rowdy Rathore'),
],
[
    InlineKeyboardButton('Rustom', switch_inline_query_current_chat='Rustom'),
    InlineKeyboardButton('Kesari', switch_inline_query_current_chat='Kesari'),
],
[
    InlineKeyboardButton('Toilet: Ek Prem Katha', switch_inline_query_current_chat='Toilet: Ek Prem Katha'),
    InlineKeyboardButton('Laxmii', switch_inline_query_current_chat='Laxmii'),
],
[
    InlineKeyboardButton('Jolly LLB 2', switch_inline_query_current_chat='Jolly LLB 2'),
    InlineKeyboardButton('Singh Is Kinng', switch_inline_query_current_chat='Singh Is Kinng'),
],
[
    InlineKeyboardButton('Good Newwz', switch_inline_query_current_chat='Good Newwz'),
    InlineKeyboardButton('Baby', switch_inline_query_current_chat='Baby'),
],
[
    InlineKeyboardButton('Special 26', switch_inline_query_current_chat='Special 26'),
    InlineKeyboardButton('Entertainment', switch_inline_query_current_chat='Entertainment'),
],
[
    InlineKeyboardButton('Brothers', switch_inline_query_current_chat='Brothers'),
    InlineKeyboardButton('Gold', switch_inline_query_current_chat='Gold'),
],
[
    InlineKeyboardButton('Tashan', switch_inline_query_current_chat='Tashan'),
    InlineKeyboardButton('Garam Masala', switch_inline_query_current_chat='Garam Masala'),
],
[
    InlineKeyboardButton('Boss', switch_inline_query_current_chat='Boss'),
    InlineKeyboardButton('Welcome', switch_inline_query_current_chat='Welcome'),
],
[
    InlineKeyboardButton('Once Upon a Time in Mumbaai Dobaara!', switch_inline_query_current_chat='Once Upon a Time in Mumbaai Dobaara!'),
    InlineKeyboardButton('Desi Boyz', switch_inline_query_current_chat='Desi Boyz'),
],
[
    InlineKeyboardButton('Tees Maar Khan', switch_inline_query_current_chat='Tees Maar Khan'),
    InlineKeyboardButton('Patiala House', switch_inline_query_current_chat='Patiala House'),
],
[
    InlineKeyboardButton('Gabbar is Back', switch_inline_query_current_chat='Gabbar is Back'),
    InlineKeyboardButton('Holiday: A Soldier Is Never Off Duty', switch_inline_query_current_chat='Holiday: A Soldier Is Never Off Duty'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "AamirKhan":
        buttons = [ 
        [
    InlineKeyboardButton('Qayamat Se Qayamat Tak', switch_inline_query_current_chat='Qayamat Se Qayamat Tak'),
    InlineKeyboardButton('Raakh', switch_inline_query_current_chat='Raakh'),
],
[
    InlineKeyboardButton('Dil', switch_inline_query_current_chat='Dil'),
    InlineKeyboardButton('Dil Hai Ki Manta Nahin', switch_inline_query_current_chat='Dil Hai Ki Manta Nahin'),
],
[
    InlineKeyboardButton('Jo Jeeta Wohi Sikandar', switch_inline_query_current_chat='Jo Jeeta Wohi Sikandar'),
    InlineKeyboardButton('Hum Hain Rahi Pyar Ke', switch_inline_query_current_chat='Hum Hain Rahi Pyar Ke'),
],
[
    InlineKeyboardButton('Andaz Apna Apna', switch_inline_query_current_chat='Andaz Apna Apna'),
    InlineKeyboardButton('Akele Hum Akele Tum', switch_inline_query_current_chat='Akele Hum Akele Tum'),
],
[
    InlineKeyboardButton('Raja Hindustani', switch_inline_query_current_chat='Raja Hindustani'),
    InlineKeyboardButton('Ishq', switch_inline_query_current_chat='Ishq'),
],
[
    InlineKeyboardButton('Ghulam', switch_inline_query_current_chat='Ghulam'),
    InlineKeyboardButton('Sarfarosh', switch_inline_query_current_chat='Sarfarosh'),
],
[
    InlineKeyboardButton('Mela', switch_inline_query_current_chat='Mela'),
    InlineKeyboardButton('Lagaan', switch_inline_query_current_chat='Lagaan'),
],
[
    InlineKeyboardButton('Dil Chahta Hai', switch_inline_query_current_chat='Dil Chahta Hai'),
    InlineKeyboardButton('Mangal Pandey: The Rising', switch_inline_query_current_chat='Mangal Pandey: The Rising'),
],
[
    InlineKeyboardButton('Rang De Basanti', switch_inline_query_current_chat='Rang De Basanti'),
    InlineKeyboardButton('Fanaa', switch_inline_query_current_chat='Fanaa'),
],
[
    InlineKeyboardButton('Taare Zameen Par', switch_inline_query_current_chat='Taare Zameen Par'),
    InlineKeyboardButton('Ghajini', switch_inline_query_current_chat='Ghajini'),
],
[
    InlineKeyboardButton('3 Idiots', switch_inline_query_current_chat='3 Idiots'),
    InlineKeyboardButton('Dhobi Ghat', switch_inline_query_current_chat='Dhobi Ghat'),
],
[
    InlineKeyboardButton('Talaash', switch_inline_query_current_chat='Talaash'),
    InlineKeyboardButton('Dhoom 3', switch_inline_query_current_chat='Dhoom 3'),
],
[
    InlineKeyboardButton('PK', switch_inline_query_current_chat='PK'),
    InlineKeyboardButton('Dangal', switch_inline_query_current_chat='Dangal'),
],
[
    InlineKeyboardButton('Thugs of Hindostan', switch_inline_query_current_chat='Thugs of Hindostan'),
    InlineKeyboardButton('Laal Singh Chaddha', switch_inline_query_current_chat='Laal Singh Chaddha'),
]
,[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "SalmanKhan":
        buttons = [ [
    InlineKeyboardButton('Biwi Ho To Aisi', switch_inline_query_current_chat='Biwi Ho To Aisi'),
    InlineKeyboardButton('Maine Pyar Kiya', switch_inline_query_current_chat='Maine Pyar Kiya'),
],
[
    InlineKeyboardButton('Baaghi: A Rebel for Love', switch_inline_query_current_chat='Baaghi: A Rebel for Love'),
    InlineKeyboardButton('Sanam Bewafa', switch_inline_query_current_chat='Sanam Bewafa'),
],
[
    InlineKeyboardButton('Patthar Ke Phool', switch_inline_query_current_chat='Patthar Ke Phool'),
    InlineKeyboardButton('Kurbaan', switch_inline_query_current_chat='Kurbaan'),
],
[
    InlineKeyboardButton('Karan Arjun', switch_inline_query_current_chat='Karan Arjun'),
    InlineKeyboardButton('Chaand Kaa Tukdaa', switch_inline_query_current_chat='Chaand Kaa Tukdaa'),
],
[
    InlineKeyboardButton('Jeet', switch_inline_query_current_chat='Jeet'),
    InlineKeyboardButton('Karan Arjun', switch_inline_query_current_chat='Karan Arjun'),
],
[
    InlineKeyboardButton('Judwaa', switch_inline_query_current_chat='Judwaa'),
    InlineKeyboardButton('Dushman Duniya Ka', switch_inline_query_current_chat='Dushman Duniya Ka'),
],
[
    InlineKeyboardButton('Jeet', switch_inline_query_current_chat='Jeet'),
    InlineKeyboardButton('Dus', switch_inline_query_current_chat='Dus'),
],
[
    InlineKeyboardButton('Karan Arjun', switch_inline_query_current_chat='Karan Arjun'),
    InlineKeyboardButton('Pyaar Kiya To Darna Kya', switch_inline_query_current_chat='Pyaar Kiya To Darna Kya'),
],
[
    InlineKeyboardButton('Bandhan', switch_inline_query_current_chat='Bandhan'),
    InlineKeyboardButton('Biwi No. 1', switch_inline_query_current_chat='Biwi No. 1'),
],
[
    InlineKeyboardButton('Hum Dil De Chuke Sanam', switch_inline_query_current_chat='Hum Dil De Chuke Sanam'),
    InlineKeyboardButton('Dulhan Hum Le Jayenge', switch_inline_query_current_chat='Dulhan Hum Le Jayenge'),
],
[
    InlineKeyboardButton('Har Dil Jo Pyar Karega', switch_inline_query_current_chat='Har Dil Jo Pyar Karega'),
    InlineKeyboardButton('Chal Mere Bhai', switch_inline_query_current_chat='Chal Mere Bhai'),
],
[
    InlineKeyboardButton('Har Dil Jo Pyar Karega', switch_inline_query_current_chat='Har Dil Jo Pyar Karega'),
    InlineKeyboardButton('Kahin Pyaar Na Ho Jaaye', switch_inline_query_current_chat='Kahin Pyaar Na Ho Jaaye'),
],
[
    InlineKeyboardButton('Chori Chori Chupke Chupke', switch_inline_query_current_chat='Chori Chori Chupke Chupke'),
    InlineKeyboardButton('Har Dil Jo Pyar Karega', switch_inline_query_current_chat='Har Dil Jo Pyar Karega'),
],
[
    InlineKeyboardButton('Tumko Na Bhool Paayenge', switch_inline_query_current_chat='Tumko Na Bhool Paayenge'),
    InlineKeyboardButton('Kahin Pyaar Na Ho Jaaye', switch_inline_query_current_chat='Kahin Pyaar Na Ho Jaaye'),
],
[
    InlineKeyboardButton('Tere Naam', switch_inline_query_current_chat='Tere Naam'),
    InlineKeyboardButton('Baghban', switch_inline_query_current_chat='Baghban'),
],
[
    InlineKeyboardButton('Garv: Pride and Honour', switch_inline_query_current_chat='Garv: Pride and Honour'),
    InlineKeyboardButton('Mujhse Shaadi Karogi', switch_inline_query_current_chat='Mujhse Shaadi Karogi'),
],
[
    InlineKeyboardButton('Lucky: No Time for Love', switch_inline_query_current_chat='Lucky: No Time for Love'),
    InlineKeyboardButton('Maine Pyaar Kyun Kiya?', switch_inline_query_current_chat='Maine Pyaar Kyun Kiya?'),
],
[
    InlineKeyboardButton('No Entry', switch_inline_query_current_chat='No Entry'),
    InlineKeyboardButton('Kyon Ki', switch_inline_query_current_chat='Kyon Ki'),
],
[
    InlineKeyboardButton('Shaadi Karke Phas Gaya Yaar', switch_inline_query_current_chat='Shaadi Karke Phas Gaya Yaar'),
    InlineKeyboardButton('Jaan-E-Mann', switch_inline_query_current_chat='Jaan-E-Mann'),
],
[
    InlineKeyboardButton('Baabul', switch_inline_query_current_chat='Baabul'),
    InlineKeyboardButton('Salaam-e-Ishq', switch_inline_query_current_chat='Salaam-e-Ishq'),
],
[
    InlineKeyboardButton('Partner', switch_inline_query_current_chat='Partner'),
    InlineKeyboardButton('Marigold: An Adventure in India', switch_inline_query_current_chat='Marigold: An Adventure in India'),
],
[
    InlineKeyboardButton('God Tussi Great Ho', switch_inline_query_current_chat='God Tussi Great Ho'),
    InlineKeyboardButton('Heroes', switch_inline_query_current_chat='Heroes'),
],
[
    InlineKeyboardButton('Yuvvraaj', switch_inline_query_current_chat='Yuvvraaj'),
    InlineKeyboardButton('Wanted', switch_inline_query_current_chat='Wanted'),
],
[
    InlineKeyboardButton('Main Aurr Mrs Khanna', switch_inline_query_current_chat='Main Aurr Mrs Khanna'),
    InlineKeyboardButton('London Dreams', switch_inline_query_current_chat='London Dreams'),
],
[
    InlineKeyboardButton('Veer', switch_inline_query_current_chat='Veer'),
    InlineKeyboardButton('Prem Kaa Game', switch_inline_query_current_chat='Prem Kaa Game'),
],
[
    InlineKeyboardButton('Dabangg', switch_inline_query_current_chat='Dabangg'),
    InlineKeyboardButton('Ready', switch_inline_query_current_chat='Ready'),
],
[
    InlineKeyboardButton('Bodyguard', switch_inline_query_current_chat='Bodyguard'),
    InlineKeyboardButton('Ek Tha Tiger', switch_inline_query_current_chat='Ek Tha Tiger'),
],
[
    InlineKeyboardButton('Dabangg 2', switch_inline_query_current_chat='Dabangg 2'),
    InlineKeyboardButton('Jai Ho', switch_inline_query_current_chat='Jai Ho'),
],
[
    InlineKeyboardButton('Kick', switch_inline_query_current_chat='Kick'),
    InlineKeyboardButton('Bajrangi Bhaijaan', switch_inline_query_current_chat='Bajrangi Bhaijaan'),
],
[
    InlineKeyboardButton('Prem Ratan Dhan Payo', switch_inline_query_current_chat='Prem Ratan Dhan Payo'),
    InlineKeyboardButton('Sultan', switch_inline_query_current_chat='Sultan'),
],
[
    InlineKeyboardButton('Tubelight', switch_inline_query_current_chat='Tubelight'),
    InlineKeyboardButton('Tiger Zinda Hai', switch_inline_query_current_chat='Tiger Zinda Hai'),
],
[
    InlineKeyboardButton('Race 3', switch_inline_query_current_chat='Race 3'),
    InlineKeyboardButton('Bharat', switch_inline_query_current_chat='Bharat'),
],
[
    InlineKeyboardButton('Dabangg 3', switch_inline_query_current_chat='Dabangg 3'),
    InlineKeyboardButton('Radhe: Your Most Wanted Bhai', switch_inline_query_current_chat='Radhe: Your Most Wanted Bhai')
]
,[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "srk":
        buttons = [ [
    InlineKeyboardButton('Dilwale Dulhania Le Jayenge', switch_inline_query_current_chat='Dilwale Dulhania Le Jayenge'),
    InlineKeyboardButton('Diljale', switch_inline_query_current_chat='Diljale'),
],
[
    InlineKeyboardButton('Dushman Duniya Ka', switch_inline_query_current_chat='Dushman Duniya Ka'),
    InlineKeyboardButton('Gudgudee', switch_inline_query_current_chat='Gudgudee'),
],
[
    InlineKeyboardButton('Koyla', switch_inline_query_current_chat='Koyla'),
    InlineKeyboardButton('Yes Boss', switch_inline_query_current_chat='Yes Boss'),
],
[
    InlineKeyboardButton('Pardes', switch_inline_query_current_chat='Pardes'),
    InlineKeyboardButton('Achanak', switch_inline_query_current_chat='Achanak'),
],
[
    InlineKeyboardButton('Kuch Kuch Hota Hai', switch_inline_query_current_chat='Kuch Kuch Hota Hai'),
    InlineKeyboardButton('Achanak', switch_inline_query_current_chat='Achanak'),
],
[
    InlineKeyboardButton('Baadshah', switch_inline_query_current_chat='Baadshah'),
    InlineKeyboardButton('Phir Bhi Dil Hai Hindustani', switch_inline_query_current_chat='Phir Bhi Dil Hai Hindustani'),
],
[
    InlineKeyboardButton('Har Dil Jo Pyar Karega', switch_inline_query_current_chat='Har Dil Jo Pyar Karega'),
    InlineKeyboardButton('Gaja Gamini', switch_inline_query_current_chat='Gaja Gamini'),
],
[
    InlineKeyboardButton('Josh', switch_inline_query_current_chat='Josh'),
    InlineKeyboardButton('Har Dil Jo Pyar Karega', switch_inline_query_current_chat='Har Dil Jo Pyar Karega'),
],
[
    InlineKeyboardButton('Gaja Gamini', switch_inline_query_current_chat='Gaja Gamini'),
    InlineKeyboardButton('One 2 Ka 4', switch_inline_query_current_chat='One 2 Ka 4'),
],
[
    InlineKeyboardButton('Aśoka', switch_inline_query_current_chat='Aśoka'),
    InlineKeyboardButton('Kabhi Khushi Kabhie Gham', switch_inline_query_current_chat='Kabhi Khushi Kabhie Gham'),
],
[
    InlineKeyboardButton('Hum Tumhare Hain Sanam', switch_inline_query_current_chat='Hum Tumhare Hain Sanam'),
    InlineKeyboardButton('Devdas', switch_inline_query_current_chat='Devdas'),
],
[
    InlineKeyboardButton('Chalte Chalte', switch_inline_query_current_chat='Chalte Chalte'),
    InlineKeyboardButton('Kal Ho Naa Ho', switch_inline_query_current_chat='Kal Ho Naa Ho'),
],
[
    InlineKeyboardButton('Main Hoon Na', switch_inline_query_current_chat='Main Hoon Na'),
    InlineKeyboardButton('Veer-Zaara', switch_inline_query_current_chat='Veer-Zaara'),
],
[
    InlineKeyboardButton('Swades', switch_inline_query_current_chat='Swades'),
    InlineKeyboardButton('Paheli', switch_inline_query_current_chat='Paheli'),
],
[
    InlineKeyboardButton('Don', switch_inline_query_current_chat='Don'),
    InlineKeyboardButton('Chakde! India', switch_inline_query_current_chat='Chakde! India'),
],
[
    InlineKeyboardButton('Om Shanti Om', switch_inline_query_current_chat='Om Shanti Om'),
    InlineKeyboardButton('Rab Ne Bana Di Jodi', switch_inline_query_current_chat='Rab Ne Bana Di Jodi'),
],
[
    InlineKeyboardButton('My Name Is Khan', switch_inline_query_current_chat='My Name Is Khan'),
    InlineKeyboardButton('Ra.One', switch_inline_query_current_chat='Ra.One'),
],
[
    InlineKeyboardButton('Don 2', switch_inline_query_current_chat='Don 2'),
    InlineKeyboardButton('Jab Tak Hai Jaan', switch_inline_query_current_chat='Jab Tak Hai Jaan'),
],
[
    InlineKeyboardButton('Chennai Express', switch_inline_query_current_chat='Chennai Express'),
    InlineKeyboardButton('Happy New Year', switch_inline_query_current_chat='Happy New Year'),
],
[
    InlineKeyboardButton('Dilwale', switch_inline_query_current_chat='Dilwale'),
    InlineKeyboardButton('Fan', switch_inline_query_current_chat='Fan'),
],
[
    InlineKeyboardButton('Dear Zindagi', switch_inline_query_current_chat='Dear Zindagi'),
    InlineKeyboardButton('Raees', switch_inline_query_current_chat='Raees'),
],
[
    InlineKeyboardButton('Jab Harry Met Sejal', switch_inline_query_current_chat='Jab Harry Met Sejal'),
    InlineKeyboardButton('Zero', switch_inline_query_current_chat='Zero'),
],
[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
        #im add end
    elif query.data == "extra":
        buttons = [
            [
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
                InlineKeyboardButton("Aᴅᴍɪɴ", callback_data="admin"),
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data == "store_file":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data == "admin":
        buttons = [[InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="extra")]]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "stats":
        buttons = [
            [
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
                InlineKeyboardButton("⟲ Rᴇғʀᴇsʜ", callback_data="rfrsh"),
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [
            [
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
                InlineKeyboardButton("⟲ Rᴇғʀᴇsʜ", callback_data="rfrsh"),
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )
    elif query.data == "kannada":
        btn = [
            [
                InlineKeyboardButton("best kannada movies", callback_data="bestk")
            ],[
                InlineKeyboardButton("Hero List ", callback_data="herolistk")
            ],[
                InlineKeyboardButton("categories - type", callback_data="typek")
            ],[
                InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="start")
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS)),
        )
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_text(
            text=(script.OWNER_INFO),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if set_type == "is_shortlink" and query.from_user.id not in ADMINS:
            return await query.answer(
                text=f"Hᴇʏ {query.from_user.first_name}, Yᴏᴜ ᴄᴀɴ'ᴛ ᴄʜᴀɴɢᴇ sʜᴏʀᴛʟɪɴᴋ sᴇᴛᴛɪɴɢs ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘ !\n\nIᴛ's ᴀɴ ᴀᴅᴍɪɴ ᴏɴʟʏ sᴇᴛᴛɪɴɢ !",
                show_alert=True,
            )

        if str(grp_id) != str(grpid) and query.from_user.id not in ADMINS:
            await query.message.edit(
                "Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ."
            )
            return await query.answer(MSG_ALRT)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton(
                        "Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Sɪɴɢʟᴇ" if settings["button"] else "Dᴏᴜʙʟᴇ",
                        callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ" if settings["botpm"] else "Aᴜᴛᴏ Sᴇɴᴅ",
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["file_secure"] else "✘ Oғғ",
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Iᴍᴅʙ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["imdb"] else "✘ Oғғ",
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Sᴘᴇʟʟ Cʜᴇᴄᴋ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["spell_check"] else "✘ Oғғ",
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Wᴇʟᴄᴏᴍᴇ Msɢ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["welcome"] else "✘ Oғғ",
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10 Mɪɴs" if settings["auto_delete"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Aᴜᴛᴏ-Fɪʟᴛᴇʀ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["auto_ffilter"] else "✘ Oғғ",
                        callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Mᴀx Bᴜᴛᴛᴏɴs",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "10" if settings["max_btn"] else f"{MAX_B_TN}",
                        callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "SʜᴏʀᴛLɪɴᴋ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                    InlineKeyboardButton(
                        "✔ Oɴ" if settings["is_shortlink"] else "✘ Oғғ",
                        callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}',
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)


async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        # message = msg.message.reply_to_message

        stickers = [
            "CAACAgUAAxkBAAEJwmVkuoJnyD7yKvwTfRN2_d7CGVO5yQACaAADtJCVKh_5ztQdtunSLwQ",
            "CAACAgUAAxkBAAEJwmdkuoJwCrSG3AjEg08IArw43on8nwACbAADtJCVKst8uIvkysD1LwQ",
            "CAACAgUAAxkBAAEJwnNkuoLiLSQ9EOU454AQHr0vNGswOgACegADCRqTHbffeMJ-KALcLwQ",
            "CAACAgUAAxkBAAEJwn1kuoL3gA6pKJKteaXnLmFyth7btQAC4QMAApPfIVdjRexTDQ8jVy8E",
            "CAACAgUAAxkBAAEJwoNkuoM3XXh721uh6T9XOTyDWR2ehgACggMAAim3-FVjA4sI3jodeS8E",
            # Add more sticker IDs here
        ]

        stick_id = random.choice(stickers)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("sᴇᴀʀᴄʜɪɴɢ 🔍", callback_data="hid")]]
        )
        stick = await message.reply_sticker(sticker=stick_id, reply_markup=keyboard)
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"):
            return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(
                message.chat.id, search.lower(), offset=0, filter=True
            )
            if not files:
                if settings["spell_check"]:
                    await stick.delete()
                    return await advantage_spell_chok(client, msg)

                else:
                    if NO_RESULTS_MSG:

                        await client.send_message(
                            chat_id=LOG_CHANNEL,
                            text=(
                                script.NORSLTS.format(reqstr.id, reqstr.mention, search)
                            ),
                        )
                    await stick.delete()

                    return
        else:
            await stick.delete()
            return

        await stick.delete()
    else:

        message = msg.message.reply_to_message
        stick_id = (
            "CAACAgUAAxkBAAEJwnNkuoLiLSQ9EOU454AQHr0vNGswOgACegADCRqTHbffeMJ-KALcLwQ"
        )
        # stick0 = await message.reply_sticker(sticker=stick_id)# msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
    temp.SEND_ALL_TEMP[message.from_user.id] = files
    temp.KEYWORD[message.from_user.id] = search
    if "is_shortlink" in settings.keys():
        ENABLE_SHORTLINK = settings["is_shortlink"]
    else:
        await save_group_settings(message.chat.id, "is_shortlink", False)
        ENABLE_SHORTLINK = False
    pre = "filep" if settings["file_secure"] else "file"
    if ENABLE_SHORTLINK and settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    url=await get_shortlink(
                        message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
            ]
            for file in files
        ]
    elif ENABLE_SHORTLINK and not settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    url=await get_shortlink(
                        message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(
                        message.chat.id,
                        f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}",
                    ),
                ),
            ]
            for file in files
        ]
    elif settings["button"] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    callback_data=f"{pre}#{file.file_id}",
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f"{pre}#{file.file_id}",
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f"{pre}#{file.file_id}",
                ),
            ]
            for file in files
        ]

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                "! Sᴇɴᴅ Aʟʟ Tᴏ PM !",
                callback_data=f"send_fall#{pre}#{0}#{message.from_user.id}",
            ),
            InlineKeyboardButton(
                "! Lᴀɴɢᴜᴀɢᴇs !", callback_data=f"select_lang#{message.from_user.id}"
            ),
        ],
    )

    btn.insert(
        0, [InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")]
    )

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        try:
            if settings["max_btn"]:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(
                            text=f"1/{math.ceil(int(total_results)/10)}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}"
                        ),
                    ]
                )
            else:
                btn.append(
                    [
                        InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                        InlineKeyboardButton(
                            text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",
                            callback_data="pages",
                        ),
                        InlineKeyboardButton(
                            text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}"
                        ),
                    ]
                )
        except KeyError:
            await save_group_settings(message.chat.id, "max_btn", True)
            btn.append(
                [
                    InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
                    InlineKeyboardButton(
                        text=f"1/{math.ceil(int(total_results)/10)}",
                        callback_data="pages",
                    ),
                    InlineKeyboardButton(
                        text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}"
                    ),
                ]
            )
    else:
        btn.append(
            [
                InlineKeyboardButton(
                    text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄", callback_data="pages"
                )
            ]
        )

    imdb = (
        await get_poster(search, file=(files[0]).file_name)
        if settings["imdb"]
        else None
    )
    TEMPLATE = settings["template"]
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb["title"],
            votes=imdb["votes"],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb["box_office"],
            localized_title=imdb["localized_title"],
            kind=imdb["kind"],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb["release_date"],
            year=imdb["year"],
            genres=imdb["genres"],
            poster=imdb["poster"],
            plot=imdb["plot"],
            rating=imdb["rating"],
            url=imdb["url"],
            **locals(),
        )
    else:
        cap = f"<b>Hᴇʏ {message.from_user.mention}, Hᴇʀᴇ ɪs Wʜᴀᴛ I Fᴏᴜɴᴅ Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ {search}.</b>"
    if imdb and imdb.get("poster"):
        try:
            hehe = await message.reply_photo(
                photo=imdb.get("poster"),
                caption=cap[:1024],
                reply_markup=InlineKeyboardMarkup(btn),
            )
            try:
                if settings["auto_delete"]:
                    await asyncio.sleep(400)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, "auto_delete", True)
                await asyncio.sleep(400)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get("poster")
            poster = pic.replace(".jpg", "._V1_UX360.jpg")
            hmm = await message.reply_photo(
                photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn)
            )
            try:
                if settings["auto_delete"]:
                    await asyncio.sleep(400)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, "auto_delete", True)
                await asyncio.sleep(400)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_photo(
                photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn)
            )
            try:
                if settings["auto_delete"]:
                    await asyncio.sleep(400)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, "auto_delete", True)
                await asyncio.sleep(400)
                await fek.delete()
                await message.delete()
    else:
        fuk = await message.reply_photo(
            photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn)
        )
        try:
            if settings["auto_delete"]:
                await asyncio.sleep(400)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, "auto_delete", True)
            await asyncio.sleep(400)
            await fuk.delete()
            await message.delete()
    if spoll:
        await msg.message.delete()
        await stick.delete()


@Client.on_callback_query(filters.regex("^hid$"))
async def handle_hid_query(client: Client, query: CallbackQuery):
    # Get the callback data
    callback_data = query.data

    # Send a message with the callback data
    chat_id = -1001421748926  # Replace with the desired chat or user ID
    await client.send_message(chat_id, f"Callback data: {callback_data}")


# Client.register_handler(auto_filter)
# Client.add_handler(auto_filter)    # Other code...


"""@Client.on_callback_query(filters.regex(r'^hid$'))
async def handle_hid_query(client: Client, query: CallbackQuery):
   
    
    await query.answer("ʙᴇᴄᴀᴜsᴇ ᴏғ ʟᴀɢᴛᴇ ғɪʟᴇs ɪɴ ᴅᴀᴛᴀʙᴀsᴇ,🙏\nʙᴏᴛ ɪs ʙɪᴛ sʟᴏᴡ",show_alert=True)"""


# Client.add_callback_query_handler(handle_hid_query)


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "",
        msg.text,
        flags=re.IGNORECASE,
    )  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [
            [
                InlineKeyboardButton(
                    "Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}"
                )
            ]
        ]
        if NO_RESULTS_MSG:
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)),
            )
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button),
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [
            [
                InlineKeyboardButton(
                    "Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}"
                )
            ]
        ]
        if NO_RESULTS_MSG:
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)),
            )
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button),
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get("title") for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append(
        [
            InlineKeyboardButton(
                text="Close", callback_data=f"spol#{reqstr1}#close_spellcheck"
            )
        ]
    )
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(mv_rqst)),
        reply_markup=InlineKeyboardMarkup(btn),
    )
    try:
        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
        grpid = await active_connection(str(msg.from_user.id))
        await save_group_settings(grpid, "auto_delete", True)
        settings = await get_settings(msg.chat.id)
        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await spell_check_del.delete()


async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                protect_content=True
                                if settings["file_secure"]
                                else False,
                                reply_to_message_id=reply_id,
                            )
                            try:
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                                    try:
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_ffilter", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True
                                if settings["file_secure"]
                                else False,
                                reply_to_message_id=reply_id,
                            )
                            try:
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                                    try:
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_ffilter", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id,
                        )
                        try:
                            if settings["auto_ffilter"]:
                                await auto_filter(client, message)
                                try:
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings["auto_delete"]:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, "auto_ffilter", True)
                            settings = await get_settings(message.chat.id)
                            if settings["auto_ffilter"]:
                                await auto_filter(client, message)

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id,
                        )
                        try:
                            if settings["auto_ffilter"]:
                                await auto_filter(client, message)
                                try:
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings["auto_delete"]:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, "auto_ffilter", True)
                            settings = await get_settings(message.chat.id)
                            if settings["auto_ffilter"]:
                                await auto_filter(client, message)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters("gfilters")
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter("gfilters", keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id,
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings["auto_ffilter"]:
                                        await auto_filter(client, message)
                                        try:
                                            if settings["auto_delete"]:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(
                                                str(message.from_user.id)
                                            )
                                            await save_group_settings(
                                                grpid, "auto_delete", True
                                            )
                                            settings = await get_settings(
                                                message.chat.id
                                            )
                                            if settings["auto_delete"]:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings["auto_delete"]:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(
                                                str(message.from_user.id)
                                            )
                                            await save_group_settings(
                                                grpid, "auto_delete", True
                                            )
                                            settings = await get_settings(
                                                message.chat.id
                                            )
                                            if settings["auto_delete"]:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_ffilter", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_ffilter"]:
                                        await auto_filter(client, message)
                            else:
                                try:
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await joelkb.delete()

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id,
                            )
                            manual = await manual_filters(client, message)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings["auto_ffilter"]:
                                        await auto_filter(client, message)
                                        try:
                                            if settings["auto_delete"]:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(
                                                str(message.from_user.id)
                                            )
                                            await save_group_settings(
                                                grpid, "auto_delete", True
                                            )
                                            settings = await get_settings(
                                                message.chat.id
                                            )
                                            if settings["auto_delete"]:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings["auto_delete"]:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(
                                                str(message.from_user.id)
                                            )
                                            await save_group_settings(
                                                grpid, "auto_delete", True
                                            )
                                            settings = await get_settings(
                                                message.chat.id
                                            )
                                            if settings["auto_delete"]:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_ffilter", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_ffilter"]:
                                        await auto_filter(client, message)
                            else:
                                try:
                                    if settings["auto_delete"]:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(
                                        str(message.from_user.id)
                                    )
                                    await save_group_settings(
                                        grpid, "auto_delete", True
                                    )
                                    settings = await get_settings(message.chat.id)
                                    if settings["auto_delete"]:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id,
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                                    try:
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_ffilter", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                        else:
                            try:
                                if settings["auto_delete"]:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_delete", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_delete"]:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id,
                        )
                        manual = await manual_filters(client, message)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                                    try:
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(
                                            str(message.from_user.id)
                                        )
                                        await save_group_settings(
                                            grpid, "auto_delete", True
                                        )
                                        settings = await get_settings(message.chat.id)
                                        if settings["auto_delete"]:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_ffilter", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_ffilter"]:
                                    await auto_filter(client, message)
                        else:
                            try:
                                if settings["auto_delete"]:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(
                                    str(message.from_user.id)
                                )
                                await save_group_settings(grpid, "auto_delete", True)
                                settings = await get_settings(message.chat.id)
                                if settings["auto_delete"]:
                                    await joelkb.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
