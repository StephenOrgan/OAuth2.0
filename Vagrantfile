# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.network "private_network", ip: "192.168.33.15"
  config.vm.provision :shell, path: "pg_config.sh"
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 5500, host: 5500
  
end
