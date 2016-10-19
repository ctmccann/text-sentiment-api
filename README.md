# Text Sentiment REST API

## Overview

This API is used to analyze the sentiment of text documents at several levels: word level, sentence level, paragraph level, and whole document level.

This API is very simple and easy to use. There no reason it needs to be complex!

## Make This Your Own!

If you want to use this repository as a starting point for _your_ API, then you should:

1. Clone this repo.
1. Modify the two variables at the top of [app.py](webapp/app.py).
1. Change the title of the swagger UI home page (see [index.html](webapp/static/swagger-ui-build/index.html), lines 6 and 92).
1. Change the interface, documentation, and behavior of the [v100.py](webapp/v100.py) endpoints.
1. Change the demo (see [the demo directory](webapp/static/demo/)).
1. Modify this [README.md](README.md) file.

## Simple Demo

You can see how to use this text sentiment REST API within JavaScript (leveraging jQuery) in [this simple demo](https://sentiment.rhobota.com/static/demo/index.html).

## Documentation

Powered by Swagger-UI: [Text Sentiment REST API Documentation](https://sentiment.rhobota.com/)

## Technologies Used

- [python](https://www.python.org/)
- [flask](http://flask.pocoo.org/)
- [flask-swagger](https://github.com/gangverk/flask-swagger)
- [Swagger-UI](https://github.com/swagger-api/swagger-ui)
- [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification/) (fla _Swagger Spec_)
    - also see http://editor.swagger.io/ for a playground to help you write Swagger Spec
- [SQLite](https://www.sqlite.org/)
- [Apache](https://httpd.apache.org/)
- [mod_wsgi](http://modwsgi.readthedocs.io/)
- [AWS](https://aws.amazon.com/) (with an EC2 [Ubuntu](http://www.ubuntu.com/) image)

In addition and by necessity, the simple demo uses [HTML5](https://en.wikipedia.org/wiki/HTML5)/[CSS3](https://en.wikipedia.org/wiki/Cascading_Style_Sheets#CSS_3) + [Javascript](https://en.wikipedia.org/wiki/JavaScript)/[jQuery](https://jquery.com/).

## How to deploy!

**Launch an Ubuntu EC2 instance**:

We will configure everything from scratch. You'll probably want to launch a small-ish instance first while you are just toying around. You can always make it larger (i.e. change the "instance type") later. So, launch an Ubuntu-based image and `ssh` into it.

REMEMBER: Be sure to set your instance's _security group_ up so that it lets incoming ports 22 and 80 through.

If you want a better command prompt, do this:
```
#> wget https://raw.githubusercontent.com/acu192/config-bash/master/linux/Dotbashrc
#> mv Dotbashrc .bashrc
```

(now log out and back in)

**Install Anaconda**:

Install Anaconda with the following commands. You should accept all default options _except_ for the one about modifying the `PATH` variable (answer 'yes' to that question).

```
#> wget http://repo.continuum.io/archive/Anaconda2-4.1.1-Linux-x86_64.sh
#> bash Anaconda2-4.1.1-Linux-x86_64.sh
#> rm Anaconda2-4.1.1-Linux-x86_64.sh
```

(now log out and back in)

Later on we will use `mod_wsgi` as a way to plug our Flask app into Apache. In a bit we will use `apt-get` to install `mod_wsgi`. The version of `mod_wsgi` that `apt-get` has was built against Python 2.7.6, so let's tell Anaconda to use that version of Python! Versions gotta match.

```
#> conda install python=2.7.6
```

And while we're at it, we need two extra packages that Anaconda doesn't install by default.

```
#> pip install flask-swagger
```

(now log out and back in; yes, I do that a lot)

**Install Apache and mod\_wsgi**:

Now we're ready to install all the Apache stuff we'll use to deploy our site for realz. Using `apt-get` this is pretty easy:

```
#> sudo apt-get update
#> sudo apt-get upgrade
#> sudo apt-get install apache2 apache2-mpm-prefork apache2-utils libexpat1 ssl-cert libapache2-mod-wsgi git unzip cmake build-essential
#> sudo service apache2 restart
```

Bam. Apache should be running now. We'll configure Apache to use our Flask app next.

**Connect our Flask app to Apache**:

We still haven't actually put our Flask app code on our EC2 instance yet. Let's do that now:

```
#> mkdir -p github/acu192
#> cd github/acu192
#> git clone https://github.com/acu192/text-sentiment-api.git
```

Now, let's create an Apache Virtual Host that uses our Flask app to serve requests. Use the command `sudo nano /etc/apache2/sites-available/text-sentiment-api.conf` to open an editor to a new Apache virtual host configuration file. Paste in the following configuration:

```
<VirtualHost *:80>

	ServerName sentiment.rhobota.com

	WSGIDaemonProcess text-sentiment-api \
		threads=5 \
		home=/home/ubuntu/github/acu192/text-sentiment-api/webapp

	WSGIScriptAlias / /home/ubuntu/github/acu192/text-sentiment-api/webapp/app.wsgi

	<Directory /home/ubuntu/github/acu192/text-sentiment-api/webapp>
		WSGIProcessGroup text-sentiment-api
		WSGIApplicationGroup %{GLOBAL}
		WSGIScriptReloading On
		Require all granted
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```

Edit it to your liking.

Clean up Apache's default configuration a little bit by doing this:

```
#> sudo rm /etc/apache2/sites-*/*default*
```

There is a tiny amount of global Apache configuration to do. Open the global config file with the command `sudo nano /etc/apache2/apache2.conf`, and paste the following two lines at the top of the file:

```
WSGIPythonHome /home/ubuntu/anaconda2
WSGIRestrictStdout Off
```

Finally, let's enable our new virtual host:

```
#> sudo a2ensite text-sentiment-api.conf
```

Restart Apache (and hope for no errors) with the command:

```
#> sudo service apache2 restart
```

Debugging tip: If things are going wrong (in a previous step or in a future step, or whenever!), you can look at the Apache error log with the command:

```
#> cat /var/log/apache2/error.log
```

**Final touches to make the Flask app happy**:

This specific Flask app uses an SQLite database, so we need to (1) init the database, and (2) set permissions on the containing folder to allow the database to be written to by any user (this is needed because Apache runs the app as the "www-data" user for security purposes). Do all this with the following commands:

```
#> cd ~/github/acu192/text-sentiment-api/webapp/
#> python -c 'import db; db.init()'
#> chmod 0666 *.db
#> chmod 777 .
```

Now, reboot your server with a `sudo reboot`, wait a minute for it to reboot, cross your fingers, and try to hit the site with your browser (in my case, I'll hit the URL https://sentiment.rhobota.com/).

Good luck!

**Serve over HTTPS:**

If you want to serve over _https_, start by buying an SSL certificate from [namecheap.com](https://www.namecheap.com).

Through that process, you will eventually obtain these files:
 - &lt;whatever&gt;.ca-bundle
 - &lt;whatever&gt;.csr
 - &lt;whatever&gt;.zip
 - &lt;whatever&gt;.crt
 - &lt;whatever&gt;.key

We need to configure Apache to enable SSL-based sites (https). Do the following:

```
#> sudo a2enmod ssl
#> sudo service apache2 restart
```

Next, open the virtual host configuration file with a quick `sudo vim /etc/apache2/sites-available/text-sentiment-api.conf`. Modify it to look like:

```
<VirtualHost *:80>

    ServerName sentiment.rhobota.com

    Redirect permanent / https://sentiment.rhobota.com/

</VirtualHost>

<VirtualHost *:443>

    ServerName sentiment.rhobota.com

    SSLEngine on
    SSLCertificateFile /home/ubuntu/ssl_cert/STAR_rhobota_com.crt
    SSLCertificateKeyFile /home/ubuntu/ssl_cert/STAR_rhobota_com.key
    SSLCertificateChainFile /home/ubuntu/ssl_cert/STAR_rhobota_com.ca-bundle

    WSGIDaemonProcess text-sentiment-api \
        threads=5 \
        home=/home/ubuntu/github/acu192/text-sentiment-api/webapp

    WSGIScriptAlias / /home/ubuntu/github/acu192/text-sentiment-api/webapp/app.wsgi

    <Directory /home/ubuntu/github/acu192/text-sentiment-api/webapp>
        WSGIProcessGroup text-sentiment-api
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```

Notice what is different:
 1. There are now two virutal host records. The first listens on port 80 (for http) and just redirects. The second listens on port 443 (for https) and it is mostly the same as before, except for...
 2. We now specify paths to our SSL certificates inside the second virtual host! (all else is the same)

Finally, cross your fingers, reboot with `sudo reboot`, wait a few mintues, cross your fingers more, and test it out!

Good luck!
