# -*- coding: utf-8 -*-
# discord token
token = ''

# updates about bans
MOD_LOG = 289494042000228352

# main guild to sync bans and roles from
BLOB_GUILD = 272885620769161216

# guilds which get bans and roles synced to
EXTRA_GUILDS = [
    356869031870988309,  # blob emoji 2
    356876866952364032,  # blob emoji 3
    356876897403011072,  # blob emoji 4
]

# roles to sync across guilds
ROLES = {
    # role_id in main (BLOB_GUILD) guild
    294928463536586754: [
        # guild_id: role_id pairs
        (288369367769677826, 310870481479794691),
        (304383757975289857, 344293286652936212),
    ],
}

# mod logs which can be set up in each guild
# currently only shows joins and leaves
MINI_MOD_LOGS = {
    # guild_id: channel_id pairs
    272885620769161216: 364202355001917453,
}

# emoji
BLOB_HAMMER = '<:blobhammer:357765371769651201>'
BOLB = '<:bolb:357767364118315008>'

YES = '<:yes:344892554887692290>'
NO = '<:no:344892555063853056>'
