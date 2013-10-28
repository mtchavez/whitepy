# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"
  config.vm.box_url = 'http://files.vagrantup.com/precise64_vmware.box'

  config.vm.network :forwarded_port, guest: 5000, host: 8080
  config.vm.network :private_network, ip: "192.168.33.10"

  config.vm.synced_folder '.', '/vagrant', :disabled => true
  config.vm.synced_folder '.', '/srv/app'

  config.vm.provider :vmware_fusion do |f|
    f.vmx["memsize"] = "1536"
  end

  config.vm.provision 'ansible' do |ansible|
    ansible.sudo = true
    ansible.inventory_path = 'ansible/inventory'
    ansible.playbook = 'ansible/vag.yml'
  end
end
