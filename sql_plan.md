supporter:
    channel_following:
        followed_channel: bigint
        access_token: varchar(64)
        expires: bigint
        refresh_token: varchar(64)
        name: varchar(128)
        channel_id: bigint
        token: varchar(256)
        guild_id: bigint
        id: bigint PK
    channel_following_state:
        state varchar(90) PK
        channel_id bigint
    user_tags
        tag_id int auto_increment PK,
        guild_id bigint not null,
        tag_name varchar(128) not null,
        tag_content text null,
        author_id bigint not null,
    guild_settings:
        guild_id bigint pk,
        public_tags_edit
        public_tags_call
