Zinfo
=====

_An interface for "interesting folders" in the filesystem_

	Walk a folder tree
		if exist meta-file and not .ignore:
			parse meta-file into meta-dict
			add/insert/update INDEX meta-dict values
	

Config
------
meta-file: zinfo.txt
	metadata filename, can be anything, but is a global and must be the same everywhere. Default is `zinfo.txt`.
		
root: \\Server\share\projects | D:\work | /home/user/stuff
	where do we start searching from? UNC or local path

depth: 5
	how deep in the folder tree do we traverse?

index_location: \\server\share\dashboard | %homeprofile%\Documents\dashboard 
	where do we save the index?

	
### Future ###

ignore-key: do_not_index: True
	if this keyword and value exists in meta-file do not add to index. Also remove from index if already there.

ignore-file: do_not_index.zinfo
	if this file exists in project folder do not add to index. Also remove from index if already there.
	
	
Metadata file specification
---------------------------
The first 50? lines are read and parsed into a dictionary. Any keyword and values can be used, but we only watch for the ones below. Keyword is case insensitive.

	{word}{colon}{characters}{new line}

	title: Zinfo Index System
	summary: An interface for "interesting folders" in the filesystem
	description: Searches filesystem for certain metadata file and adds founds to a master index.
	authors: matt wilkie <maphew@gmail.com>, @maphew; collaborator <name@example.org>
	date_started: 2017-12-22
	last_update: 2018-01-15
	client: F&W Branch
	contact: joshua_whale@ocean.wo
	arbitrary: some other thing, whataver you like
	
title			| 30 chars	| a few words, the project's name
summary			| 140 chars	| a short sentence, the project tagline, motto or short description
description		| 500 chars | what is the project about. 2 or 3 sentences
authors			| xxx char	| semi-colon delimited list. Email addresses and Github style nick names are parsed
date_started	| iso date 	| When was the project started?
last_update 	| iso date	| Significant work happened up to this date.
client			| 30 chars	| what organization asked for, commissioned or sponsored this work?
contact			| xxx chars	| who is or are the main contacts? semi-colon delimited list. Email addresses and Github style nick names are parsed
{arbitrary}		| xxx chars | any arbitrary word and value.



Thoughts
========

? Why 2 dates? ... because I want to know when a project was first begun, as well as the last time something happened that "moved the needle". For this reason I don't want to simply use last-modification-time of certain files. I'm not happy with the name 'latest_milestone' but am not sure of what else might be appropriate. Any suggestions?
Arguably this distinction is not worth the maintenaance effort. I'm still dithering. Maybe just "date" and "last update", and maybe just plain ol' date!

Authors & Contacts: use same length and character restrictions and conventions as RFC### that's used for email messages.

Ignoring -- I'm a little unsure about this part. Here I am adding options to something that isn't even built yet! I do like the idea of being able to work on something, still use the metadata format for self-documentation, but not have it yet open for the public. I guess at the very least I should commit to not writing the code for it until the core features are present and working.



