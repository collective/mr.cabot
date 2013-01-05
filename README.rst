About
-----

mr.cabot is a tool for allowing software projects to map where their contributions are coming from. It reads data form common sources like GitHub, gmane and stackoverflow and attempts to locate where those contributors are physically located.

Basic usage
-----------

You need to customise your `mr.cabot.cfg` config file to match your software project. The basic format is that the `sources` line lists the sections that supply lists of contributors and `users` lists the sections that supply lists of contributors.

Only the GitHub sources support user enumeration at the moment, but stackoverflow and gmane both extract geolocation information where possible.

Example
-------

The current example from the Plone project generates the following:

.. image :: http://dist.plone.org/media/contributormaps/latest.png

Source types
------------

github
======

type
	github
key
	the name of the organisation to be scanned
token
	an oauth token, preferably one with the `repo` scope. See https://help.github.com/articles/creating-an-oauth-token-for-command-line-use
checkout_directory
	an existing directory to cache checkouts in to save on bandwidth

git
===

type
	git
key
	a clone url of a git repository

stackoverflow
=============

type
	stackoverflow
key
	a tag used on stack overflow
days
	the number of days of history to download

gmane
=====

type
	gmane
key
	the full gmane newsgroup name
messages
	downloads the last x messages

Output types
------------

Output type defaults to a google static map, but can be selected using `--output type` on the command line.

The available options are:

* googlestaticmap
* html
* kml

Caching
-------

No caching of geolocation data is included as yet, but data runs are cached under `var/data`, with the filename `yyyy-mm-dd.pickle`. This allows you to re-run old data sets if you are changing display methods.

To load a pickle instead of re-scanning use the --pickle command line option::

  ./bin/cabot --pickle ./var/data/2013-01-05.pickle --output kml

Additionally, there is a command line option to skip pulling git repositories. This is useful for re-running when you are tweaking the config file initially, as updating git is the slowest section::

  ./bin/cabot -N --output kml

