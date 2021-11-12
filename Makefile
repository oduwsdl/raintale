me_version = $(shell grep "__appversion__ = " raintale/version.py | sed 's/__appversion__ = //g' | sed "s/'//g")

all: generic_installer rpm

source:
	-rm -rf /tmp/raintale-source
	-rm -rf /tmp/raintale-$(me_version)
	-rm -rf /tmp/raintale-$(me_version).tar.gz
	mkdir /tmp/raintale-source
	pwd
	cp -r . /tmp/raintale-source
	-rm -rf /tmp/raintale-source/hand-testing
	-rm -rf /tmp/raintale-source/.vscode
	-rm -rf /tmp/raintale-source/.git
	(cd /tmp/raintale-source && make clean)
	mv /tmp/raintale-source /tmp/raintale-$(me_version)
	tar -C /tmp --exclude='.DS_Store' -c -v -z -f /tmp/raintale-$(me_version).tar.gz raintale-$(me_version)
	-rm -rf source-distro
	mkdir source-distro
	cp /tmp/raintale-$(me_version).tar.gz source-distro
	
clean:
	-docker stop rpmbuild_mementoembed
	-docker rm rpmbuild_mementoembed
	-rm -rf .eggs
	-rm -rf eggs/
	-rm -rf build/
	-rm -rf _build/
	-rm -rf docs/build
	-rm -rf docs/source/_build
	-rm -rf dist
	-rm -rf .web_cache
	-rm -rf installer
	-rm -rf raintale.egg-info
	-rm -rf *.log
	-rm *.sqlite
	-find . -name '*.pyc' -exec rm {} \;
	-find . -name '__pycache__' -exec rm -rf {} \;
	-rm -rf source-distro
	-rm -rf rpmbuild
	-rm -rf raintale_with_wooey
	python ./setup.py clean

build:
	python ./setup.py sdist

generic_installer:
	./raintale-gui/installer/linux/create-raintale-installer.sh

rpm: source
	-rm -rf installer/rpmbuild
	mkdir -p installer/rpmbuild/RPMS installer/rpmbuild/SRPMS
	docker build -t raintale_rpmbuild:dev -f build-rpm-Dockerfile . --build-arg raintale_version=$(me_version) --progress=plain
	docker container run --name rpmbuild_raintale --rm -it -v $(CURDIR)/installer/rpmbuild/RPMS:/root/rpmbuild/RPMS -v $(CURDIR)/installer/rpmbuild/SRPMS:/root/rpmbuild/SRPMS raintale_rpmbuild:dev
	-docker stop rpmbuild_raintale
	-docker rm rpmbuild_raintale
	@echo "an RPM structure exists in the installer/rpmbuild directory"

# deb: generic_installer
# 	-rm -rf installer/debbuild
# 	mkdir -p installer/debbuild
# 	docker build -t debbuild:dev -f build-deb-Dockerfile . --build-arg mementoembed_version=$(me_version) --progress=plain
# 	docker container run --name deb_mementoembed --rm -it -v $(CURDIR)/installer/debbuild:/root/debbuild

release: source build generic_installer rpm
	-rm -rf release
	-mkdir release
	cp ./installer/install-raintale.sh release/install-raintale-${me_version}.sh
	cp ./source-distro/raintale-${me_version}.tar.gz release/
	cp ./installer/rpmbuild/RPMS/x86_64/raintale-${me_version}-1.el8.x86_64.rpm release/
	cp ./installer/rpmbuild/SRPMS/raintale-${me_version}-1.el8.src.rpm release/	
