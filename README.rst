Basic usage
-----------

You need to create a `mr.cabot.cfg` file in your buildout directory with the
following info:

.. code :: 

	[cabot]
	sources =
		plone-users
		plone-developers
		product-developers
		stackoverflow
		github-core
		github-collective

	[github-collective]
	type = github
	key = collective
	token = YOUR_GITHUB_OAUTH_TOKEN
	checkout_directory = ./var/github-collective

	[github-core]
	type = github
	key = plone
	token = YOUR_GITHUB_OAUTH_TOKEN
	checkout_directory = ./var/github-core

	[plone-users]
	type = gmane
	key = gmane.comp.web.zope.plone.user
	messages = 5

	[plone-developers]
	type = gmane
	key = gmane.comp.web.zope.plone.devel
	messages = 5

	[product-developers]
	type = gmane
	key = gmane.comp.web.zope.plone.product-developers
	messages = 5

	[stackoverflow]
	type = stackoverflow
	key = plone
	days = 5

github oauth token generation is coming soon, but there is info on their API on
how to do it for now.

You need to create var/github-collective etc yourself, if it's missing it will
use a tempdir and have to redownload every time.

You can generate the HTML snippets with `./bin/cabot > snippets.html`
