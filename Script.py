class script(object):
    START_TXT = """  just send movie name .. i will send download link  """

    HELP_TXT = """<b>Hᴇʏ {}
✨Enjoy it, but remember my name: VIP Sender Bot ✨.</b>"""

    ABOUT_TXT = """<b>⚜️ BoT Nᴀᴍᴇ : {}
✯ Bᴜɪʟᴅ Sᴛᴀᴛᴜs: v2.7.1 [ Sᴛᴀʙʟᴇ ]
running succsfully  </b>"""

    SOURCE_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    MANUELFILTER_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    BUTTON_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    AUTOFILTER_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    CONNECTION_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    EXTRAMOD_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    ADMIN_TXT = """Enjoy it, but remember my name: VIP Sender Bot"""

    STATUS_TXT = """<b>★ Tᴏᴛᴀʟ Fɪʟᴇs: <code>{}</code>
★ Tᴏᴛᴀʟ Usᴇʀs:<b>  <code>{}</code>
★ Tᴏᴛᴀʟ Cʜᴀᴛs: <code>{}</code>
★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ: <code>{}</code>
★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ: <code>{}</code></b>"""

    LOG_TEXT_G = """#NewGroup
Gʀᴏᴜᴘ = {}(<code>{}</code>)
Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs = <code>{}</code>
Aᴅᴅᴇᴅ Bʏ - {}"""

    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Nᴀᴍᴇ - {}"""

    ALRT_TXT = """ʜᴇʟʟᴏ {},
ᴛʜɪꜱ ɪꜱ sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ʀᴇQᴜᴇꜱᴛ,
ʀᴇQᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ ᴏᴡɴ 🎈..."""

    OLD_ALRT_TXT = """ʜᴇʏ {},
ᴛʜᴀᴛ ᴡᴀs ᴏɴᴇ ᴏꜰ ᴍʏ ᴏʟᴅ ᴍᴇꜱꜱᴀɢᴇꜱ, 
ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ʀᴇQᴜᴇꜱᴛ ᴀɢᴀɪɴ 🔍."""

    CUDNT_FND = """👀 ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴀɴʏᴛʜɪɴɢ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ {}
ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴀɴʏ ᴏɴᴇ ᴏꜰ ᴛʜᴇꜱᴇ? 🧐."""

    I_CUDNT = """<b>sᴏʀʀʏ ɴᴏ ꜰɪʟᴇs ᴡᴇʀᴇ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ {} 😕..
ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴘᴇʟʟɪɴɢ ɪɴ ɢᴏᴏɢʟᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ 😃

ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ 👇
ᴇxᴀᴍᴘʟᴇ : Uncharted or Uncharted 2022 or Uncharted En
ꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ 👇
ᴇxᴀᴍᴘʟᴇ : Loki S01 or Loki S01E04 or Lucifer S03E24
🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)</b>

#REQUEST_MOVIE = contact<b> @vip_sender </b>
"""

    I_CUD_NT = """ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴀɴʏ ᴍᴏᴠɪᴇ ɴᴀᴍᴇᴅ  {}.
ᴘʟᴇᴀꜱᴇ ᴄᴏᴍғɪʀᴍ ᴛʜᴇ ꜱᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ ᴏʀ ɪᴍᴅʙ..."""

    MVE_NT_FND = """ᴍᴏᴠɪᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ..."""

    TOP_ALRT_MSG = """Cʜᴇᴄᴋɪɴɢ Fᴏʀ Mᴏᴠɪᴇ  ⎚ Dᴀᴛᴀʙᴀsᴇ..."""

    MELCOW_ENG = """<b>Hᴇʟʟᴏ {} 🤪, Aɴᴅ Wᴇʟᴄᴏᴍᴇ Tᴏ {} Gʀᴏᴜᴘ ❤️</b>"""

    OWNER_INFO = """
Enjoy it, but remember my name: VIP Sender Bot>"""


    PAID_INFO = """
<b>premium pack 😍👇👇👇 
 
*all new movies available for premium members 
*VIP customer support with whatsapp and calls 
*No ads link 
*Hindi (Bollywood),Telugu (Tollywood),Tamil (Kollywood),Malayalam (Mollywood),Bengali (Tollywood)
Kannada (Sandalwood) all language all movies available for premium members
*Discounts on tickets to movie theaters
*Netflix id password available for premium members
*our telegram channel admin permission for premium users 
        -————--100 year validity————
DIAMOND 🔹: 200RS   ( LIFETIME VALIDITY)
GOLD 🥇        : 150 RS   ( LIFETIME VALIDITY)
SLIVER 🥈      : 100 RS ( LIFETIME VALIDITY) 

ɪғ ᴀɴʏᴏɴᴇ ɪɴᴛᴇʀᴇsᴛᴇᴅ ᴄᴏɴᴛᴀᴄᴛ [https://telegram.me/jagadeeshGowda , https://telegram.me/vip_sender]"""
    REQINFO = """
⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠

ᴀꜰᴛᴇʀ 10 ᴍɪɴᴜᴛᴇꜱ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇᴅ

ɪꜰ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ꜱᴇᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ / sᴇʀɪᴇs ꜰɪʟᴇ, ʟᴏᴏᴋ ᴀᴛ ᴛʜᴇ ɴᴇxᴛ ᴘᴀɢᴇ"""

    MINFO = """
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯

ɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ

ᴇxᴀᴍᴘʟᴇ : Uncharted

🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)"""

    SINFO = """
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
ꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯

ɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ꜱᴇʀɪᴇꜱ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ

ᴇxᴀᴍᴘʟᴇ : Loki S01E01

🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)"""

    NORSLTS = """
★ #𝗡𝗼𝗥𝗲𝘀𝘂𝗹𝘁𝘀 ★

𝗜𝗗 <b>: {}</b>

𝗡𝗮𝗺𝗲 <b>: {}</b>

𝗠𝗲𝘀𝘀𝗮𝗴𝗲 <b>: {}</b>"""

    CAPTION = """
⚡ɴᴀᴍᴇ: <code>{file_name}</code>

 SIZE: <code>{file_size}</code> 
  
 ᴊᴏɪɴ ɴᴏᴡ:<b> [vip_sender ⎚](https://telegram.me/vip_sender)</b>"""

    IMDB_TEMPLATE_TXT = """
<b>Query: {query}
IMDb Data:

🔖 ᴛɪᴛʟᴇ : <a href={url}>{title}</a>
🎭 ɢᴇɴʀᴇ : {genres}
📆 ʀᴇʟᴇᴀsᴇ : <a href={url}/releaseinfo>{year}</a>
🌟 ʀᴀᴛɪɴɢ : <a href={url}/ratings>{rating}</a> / 10
🎙️ʟᴀɴɢᴜᴀɢᴇ : {languages}

🔖 sʜᴏʀᴛ : {plot}

★ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <b>[vip_sender ⎚](https://telegram.me/vip_sender)</b></b>"""
    
    ALL_FILTERS = """
<b>Enjoy it, but remember my name: VIP Sender Bot</b>"""
    
    GFILTER_TXT = """
<b>Enjoy it, but remember my name: VIP Sender Bot</b> """
    
    FILE_STORE_TXT = """
<b>Enjoy it, but remember my name: VIP Sender Bot</b>

"""

    RESTART_TXT = """
<b>Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ !
bot updated...
if face any problem contact devloper @jagadeeshgowda
📅 Dᴀᴛᴇ : <code>{}</code>
⏰ Tɪᴍᴇ : <code>{}</code>
🌐 Tɪᴍᴇᴢᴏɴᴇ : <code>Asia/Kolkata</code>
🛠️ Bᴜɪʟᴅ Sᴛᴀᴛᴜs: <code>v2.7.1 [ Sᴛᴀʙʟᴇ ]</code></b>"""

    LOGO = """


.▄▄ ·       ▄▄▄  ▄▄▄   ▄· ▄▌       ▐▄▄▄▄• ▄▌.▄▄ · ▄▄▄▄▄  ·▄▄▄      ▄▄▄    ·▄▄▄▄• ▄▌ ▐ ▄         ·▄▄▄▄• ▄▌ ▄▄· ▄ •▄    ▄· ▄▌      ▄• ▄▌      
▐█ ▀.  ▄█▀▄ ▀▄ █·▀▄ █·▐█▪██▌        ·███▪██▌▐█ ▀. •██    ▐▄▄· ▄█▀▄ ▀▄ █·  ▐▄▄·█▪██▌•█▌▐█        ▐▄▄·█▪██▌▐█ ▌▪█▌▄▌▪  ▐█▪██▌ ▄█▀▄ █▪██▌      
▄▀▀▀█▄▐█▌.▐▌▐▀▀▄ ▐▀▀▄ ▐█▌▐█▪      ▪▄ ███▌▐█▌▄▀▀▀█▄ ▐█.▪  ██▪ ▐█▌.▐▌▐▀▀▄   ██▪ █▌▐█▌▐█▐▐▌        ██▪ █▌▐█▌██ ▄▄▐▀▀▄·  ▐█▌▐█▪▐█▌.▐▌█▌▐█▌      
▐█▄▪▐█▐█▌.▐▌▐█•█▌▐█•█▌ ▐█▀·.      ▐▌▐█▌▐█▄█▌▐█▄▪▐█ ▐█▌·  ██▌.▐█▌.▐▌▐█•█▌  ██▌.▐█▄█▌██▐█▌        ██▌.▐█▄█▌▐███▌▐█.█▌   ▐█▀·.▐█▌.▐▌▐█▄█▌      
 ▀▀▀▀  ▀█▄▀▪.▀  ▀.▀  ▀  ▀ • ▀ ▀ ▀  ▀▀▀• ▀▀▀  ▀▀▀▀  ▀▀▀   ▀▀▀  ▀█▄▀▪.▀  ▀  ▀▀▀  ▀▀▀ ▀▀ █▪  ▀ ▀ ▀ ▀▀▀  ▀▀▀ ·▀▀▀ ·▀  ▀    ▀ •  ▀█▄▀▪ ▀▀▀     ▀ """
