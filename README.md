
<img src="images/raintale-logo.png" width="100px">

# Raintale

Raintale is a utility for publishing social media stories from groups of archived web pages (mementos). Raintale uses [MementoEmbed](https://github.com/oduwsdl/MementoEmbed)
 to extract memento information and then publishes a story to the given **storyteller**, a static file or an online social media service.

Raintale accepts the following inputs:
* a file containing a list of memento URLs (URI-Ms) (required)
* a title for your story (required)
* the URL of the underlying collection (optional)
* the author, organization, or algorithm that generated the story (optional)
* the storyteller to use when generating the story (e.g., HTML, Twitter, Markdown)
* an output file for saving the story (if applicable)
* a credential file for the a social media service (if applicable)
* a template file allowing the user to format their story differently than the defaults (optional, and not supported by all storytellers)

Raintale supports the following storytellers:
* facebook - (EXPERIMENTAL) publishes a story as a Facebook thread, with titles, snippets, URLs, and memento-datetimes supplied by MementoEmbed
* html - the HTML that makes up a story, suitable for pasting into a web page or a blogging application such as Blogger
* twitter - publishes a story as a Twitter thread, with titles, URLs, memento-datetimes, and images supplied by MementoEmbed
* template - given input data and a template file, this storyteller generates a story formatted based on the template and saves it to the given output file, allowing the end user to format their own stories
* jekyll-html - writes output to [Jekyll](https://jekyllrb.com/) HTML file format, suitable for use with Jekyll and GitHub pages
* jekyll-markdown - writes output to [Jekyll](https://jekyllrb.com/) Markdown file format, suitable for use with Jekyll and GitHub pages
* markdown - writes output to the [GitHub Flavored Markdown](https://github.github.com/gfm/) file format, suitable for pasting into GitHub
* mediawiki - writes output to this [MediaWiki](https://www.mediawiki.org/wiki/Help:Formatting) file format, suitable for pasting into MediaWiki pages

Railtale also supports a number of presets for formatting a story for output to a specific file format:
* default - provides a default set of fields like those seen in the social cards from social networking; may also provide an approximation, depending on file format (html, markdown, mediawiki, and jekyll storytellers)
* thumbnails3col - provides a 3 column layout containing thumbnails of the submitted mementos (HTML storyteller only)
* thumbnails4col - provides a 4 column layout containing thumbnails of the submitted mementos (HTML storyteller only)

Note that not all file formats support all presets.

<!-- # Running Raintale

Raintale uses docker-compose to load and execute all dependencies. To run Raintale, do the following:
1. Create a directory on your system
2. Copy docker-compose.yml from this repository into that directory
3. Open a terminal
4. Type: ```docker-compose run raintale tellstory --help``` to find the list of options

For example to create a raw HTML story suitable for pasting, type the following within that prompt:

``
docker-compose run raintale tellstory -i story-mementos.txt --storyteller html -o mystory.html --title "This is My Story Title"	--generated-by "Me"
``

The output will be stored in ``mystory.html``.

To create a twitter story, you will need to create a Twitter app. Log into Twitter from a web browser and visit https://developer.twitter.com/en/apps for more information. Once you have created an app, make a file named ``twitter-credentials.yml``, save it in the same directory, and fill it with the following content.

```
consumer_key: XXXXXX
consumer_secret: XXXXXX
access_token_key: XXXXXX
access_token_secret: XXXXXX
```

Replace the ``XXXXXX`` values with the corresponding values as displayed on your Twitter app page.

Once that is done, type the following within the Docker prompt:

``
docker-compose run raintale tellstory -i story_mementos.txt --storyteller twitter --title "This is My Story Title"	--generated-by "Me” -c twitter-credentials.yml
`` -->

# Installing Raintale

Before installing Raintale, make sure that the [MementoEmbed](https://github.com/oduwsdl/MementoEmbed) service is installed and running somewhere.

## Installing Raintale on Linux or Unix

Before installing Raintale, you must have an instance of MementoEmbed running on a machine, either locally or elsewhere. If you do not have MementoEmbed, please install [the latest release of MementoEmbed](https://github.com/oduwsdl/MementoEmbed).

To install Raintale on Linux or Unix, choose your target platform below.

### CentOS 8

If you would like to use the RPM installer for RHEL 8 and CentOS 8 systems:

1. Download the RPM and save it to the Linux server (e.g., `raintale-0.20211106041644-1.el8.x86_64.rpm`)
2. Type `dnf install raintale-0.20211106041644-1.el8.x86_64.rpm`
3. Type `systemctl start raintale-django.service`

To stop Raintale, type `systemctl stop raintale-django.service`.

To remove Raintale, type `dnf remove raintale`. Removing Raintale stops the associated raintale service and its celery companion. Be patient, sometimes celery takes a long time to stop.

During removal, the directory `/opt/raintale/raintale_with_wooey/raintale_with_wooey/user_uploads` is saved to `/opt/raintale/user_uploads-backup-[DATE].tar.gz where [DATE] was the date and time of removal. This is where all story outputs are stored. The administrator may wish to delete or backup this file for future use.

### Ubuntu 21.04

If you would like to use the DEB installer for RHEL 8 and CentOS 8 systems:

1. Download the RPM and save it to the Linux server (e.g., `raintale-0.20211113202900.deb`)
2. Type `apt-get install raintale-0.20211113202900.deb`
3. Type `systemctl enable raintale-celery.service`
4. Type `systemctl enable raintale-django.service`
4. Type `systemctl start raintale-django.service`

To stop Raintale, type `systemctl stop raintale-django.service`.

To remove Raintale, type `apt-get remove raintale`.

### Generic Unix

We also support a generic Unix installer which downloads many dependencies from the web. Unfortunately, these dependencies are not always version-locked and results on your system may vary.

1. Download the generic Unix installer (e.g., `install-raintale.sh`)
2. Type `install-raintale.sh`
3. To start the Raintale GUI, type `/opt/raintale/start-raintale-wui.sh`

To stop raintale, type `/opt/raintale/stop-raintale-wui.sh`.

## Installing Raintale in a Python Environment

Raintale uses ```pip``` for build and installation. Clone this repository and type the following from the root of the source code:

1. Clone this repository.
2. Change into the directory where it was cloned.
3. [Create a virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) to separate Raintale's install from other Python installations.
4. Type ```pip install .``` 

## Installing the Raintale Web User Interface (WUI) in a Python Environment

To install the Raintale WUI, do the following:
1. Follow the above instructions for installing Raintale in a Python Environment.
2. Type `raintale-gui/install-gui.sh`

This installation script will install [Wooey](https://github.com/wooey/Wooey) and other dependencies required to run the Raintale GUI.

Once the installation is complete, to start the Raintale GUI, do the following:
1. Run `raintale-gui/start-gui.sh`.
2. Once the service is started, you can access the Raintale GUI at http://127.0.0.1:8000/. 

To stop Raintale GUI, type `raintale-gui/stop-gui.sh`.

# Improving the performance of the Raintale WUI

Once installed, Raintale's WUI performance can be improved in a few ways.

## Configuring Raintale WUI for Postgres

By default, the Raintale WUI uses SQLite, which does not perform well for multiple users logging into the same Raintale WUI system. For optimial user experience, the Raintale WUI can be connected to a Postgres database.

1. Install Postgres on a system accessible to the server that on which the Raintale WUI is running. Record that system's host and the port Postgres is running on -- the default port is 5432.
2. Log into Postgres and create a database with postgres for Raintale.
3. Create a user and password.
4. Grant all privileges on the database from step 2 in step 3.
5. Run `/opt/raintale/raintale-gui/set-raintale-database.sh --dbuser [DBUSER] --dbname [DBNAME] --dbhost [DBHOST] --dbport [DBPORT]` -- with DBUSER created from step 3, DBNAME replaced by the database you created in step 2, DBHOST and DBPORT recorded from step 1. The script will prompt you for the password.
6. Restart Raintale as appropriate for your system.

#### Configuring the Raintale WUI for RabbitMQ

For optimal process control, the Raintale WUI can use a queueing service like RabbitMQ.

1. Install RabbitMQ on a system accessible to the server that the Raintale WUI is running on. Record that system's hostname and the port that RabbitMQ is running on -- the default port is 5672.
2. Run `/opt/raintale/raintale-gui/set-raintale-queueing-service.sh --amqp-url amqp://[HOST]:[PORT]/` where HOST is the host of the RabbitMQ server and PORT is its port

# Enabling Raintale's Experimental Video Stories for the Raintale WUI on CentOS 8

By default, Raintale's video stories are not enabled in the Raintale WUI in CentOS 8 installs. Generating these stories requires ffmpeg. Installing ffmpeg on Ubuntu is easy. Installing ffmpeg on CentOS 8 requires using YUM/DNF repositories outside of those provided by CentOS, as detailed in [https://linuxize.com/post/how-to-install-ffmpeg-on-centos-8/](these instructions). Rather than force all Centos 8 Raintale administrators to go through this process, we have disabled video stories through the Raintale WUI.

To enable them:
1. install ffmpeg
2. Open `/opt/raintale/raintale-gui/add-raintale-scripts.sh` in an editor and remove the # and space from the line containing `Create Video Story.py` so it looks like this (spaces are significant):
```
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Video Story.py"
```
3. Run `/opt/raintale/raintale-gui/add-raintale-scripts.sh`
