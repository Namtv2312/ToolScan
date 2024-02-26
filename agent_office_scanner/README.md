# Install agent office Scanner
###
Docker libreoffice : port forward 5000
## Agent Windows:
["File pyscript"](multi.py) 

["File build"](multi.exe)
Edit config.ini for config Server AVScan, host convert
### drag, drop, move file to folder_path defined on config.ini
## On Host
["script to receive file"](api_host.py)

["script to convert pdf : install libreoffice on kvm ubuntu virtual machine "](api_kvm_pdf.py)
NOW: worker is 10, all file put on queue    
`Done`.

## config
- Settings: 
  - URL_avscan: link CHECK av engine
  - URL_off2pdf: Link API convert PDF
  - Folder_path: folder need monitor,  + level priority (highest: 0 <--)
  - Max file size: size file largest scanned
- SFTP
  - on_demand: MODE 1 or 0
  - sftp_folder_path: Remote Folder to monitor
  - root_local_folder: folder OUTPUT file classified
  - hostname
  - port
  - username
  - password
- Virustotal
  - on_demand: MODE 1 or 0
  - key : API_key        
### machine AV migrate clone
- win8 eset, go NETWORK PROTECTION, turn off firewall
- install kvm from here : https://github.com/kevoreilly/CAPEv2/tree/master
- after copy image, xml, config agent, DONE av machine ( remember ISOLATED NETWORK)
- pull docker, v.v

#### Check ACPI 4 character :
```
sudo acpidump > acpidump.out

sudo acpixtract -a acpidump.out

sudo iasl -d dsdt.dat (NOTE: my steps are case sensitive)

The output of that last command produced a line that contained a 4 digit code. ACPI: DSDT 0x0000000000000000 0213AC (v02 HPQOEM 82BF 00000000 INTL 20121018). I used 82BF to replace all of the <WOOT> instances in the kvm-qemu.sh file.
```
eg: in my case: MSFI

change all <WOOT> Ctrl H on script: [script install kvm](./installer/kvm-qemu.sh).  
Set permission  Execute: `chmod +x for each script`
## Build script to install KVM
with command: `sudo ./kvm-qemu.sh all <username> | tee kvm-qemu.log` , with <username> of machine `whoami`
view log and debug if exception raise
### Build virt-manager to manager VM, with GUI for convinient
` sudo ./kvm-qemu.sh virtmanager <username> | tee kvm-qemu-virt-manager.log`    
check log ensure no error occur



### if meet error relate missing libvirt - install it on : [install_libvirt](./extra/libvirt_installer.sh), and restart service or wait restart auto by systemd service, see on [service systemd](./systemd/cape.service)


# EXPORT KVM MACHINE, AND IMPORT
go to script automated at: [Git script](https://gist.github.com/KarthickSudhakar/d6c671597592fe5634a39b7974bc8029) or read articles on Web: [article](https://ostechnix.com/export-import-kvm-virtual-machines-linux/)
## STEP SETUP
## KASPER https://github.com/tkessels/docker_kaspersky
## clam av: https://github.com/ajilach/clamav-rest
2 docker safewall, ( windefend, avira)
### EXPORT VM
Export domain vm kvm:
`virsh dumpxml vm-name > /path/to/xm_file.xml`

copy disk storage : 
`sudo cp /var/lib/libvirt/images/win7-VM1.qcow2 .
`
### IMPORT 
May be modify name , on xml if on your host exist that name,  
May be modify UUID, if on your host , exist that uuid for another machine , go to page: to generate: [UUID generator](https://www.uuidgenerator.net/version1)

Then: 
```bash
#Define domain machine:
sudo  virsh define --file win7_migrate.xml
```
*Copy DISK TO PATH DEFINED ON XML*
` <source file="/var/lib/libvirt/images/win7.qcow2"/> `   
OK  
`sudo cp win7-VM1.qcow2 /var/lib/libvirt/images/win7_migrate.qcow2
`
nOW , YOU CAN start and run machine , obbs
