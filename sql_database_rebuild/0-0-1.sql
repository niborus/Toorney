create table database_version
(
	version varchar(16) not null
		constraint database_version_pk
			primary key
);

comment on table database_version is 'This Table has only one entry, which contains the current state of the Database.
This is required to update the Database.';

comment on column database_version.version is 'The Version.
This entry should only appere once.';

insert into database_version (version) values ('0.0.1');

create table guild_settings
(
	guild_id bigint not null
		constraint guild_settings_pk
			primary key,
	language varchar(2) default 'en' not null
);

comment on table guild_settings is 'Settings of the Guilds.';

comment on column guild_settings.guild_id is 'The Guild ID.';

comment on column guild_settings.language is 'The language of the Bot in the Guild.';
