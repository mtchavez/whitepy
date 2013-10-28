# whitepy

[Flask](http://flask.pocoo.org) microblog example using [WhiteDB](http://whitedb.org) as an in memory stat layer.

## Requirements

* [Vagrant](http://vagrantup.com)
* [Ansible](http://ansibleworks.com)
* [VMware Fusion](http://www.vmware.com/products/fusion/)
  * Or you can change the `Vagrantfile` to use `VirtualBox`

## Setup

1. Start up VM `vagrant up`
2. Provision your server `vagrant provision`
3. SSH into server `vagrant ssh`
4. Make sure requirements are installed.
  * `cd /srv/app`
  * `sudo pip install -r requirements.txt`
5. Run server `sudo python main.py`
6. Now access app at `http://192.168.33.10:5000`

## Create entries

* Use login of `admin` with password `default`
* Add several entries

## Metrics captured in WhiteDB

* `views` - Number of views for an entry
* `upvotes` - Upvotes for an entry
* `downvotes` - Downvotes for an entry
