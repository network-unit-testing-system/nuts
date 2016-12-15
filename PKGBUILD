pkgname=nuts
pkgver=v1.0.3
pkgrel=1
pkgdesc="A Network Unit Test System with Saltstack as Executor"
arch=('x86_64')
url="https://github.com/xsicht/SA_Network-Unit-Tests"
license=('unknown')
depends=('salt>=2016.11.0-1' 'python2>=2.7.12' 'python2-pip>=8.1.2'  'python2-virtualenv>=15.0.3' 'python2-crypto>=2.6.1')
source=("https://github.com/asta1992/Nuts/archive/"$pkgver".tar.gz")
md5sums=('c768cd3ca79d3ec2e9b346cdda434592')


package() {
  	install -d "$pkgdir"/opt/nuts/src
  	install -d "$pkgdir"/usr/bin
  	install -d "$pkgdir"/srv/salt/_modules
  	install -d "$pkgdir"/var/log/nuts/

  	cp -R -f "$srcdir"/Nuts-1.0.3/src/* "$pkgdir"/opt/nuts/src
    cp -R -f "$srcdir"/Nuts-1.0.3/nuts.py "$pkgdir"/opt/nuts
    cp -R -f "$srcdir"/Nuts-1.0.3/nuts "$pkgdir"/usr/bin
    cp -R -f "$srcdir"/Nuts-1.0.3/_modules/* "$pkgdir"/srv/salt/_modules
    touch "$pkgdir"/var/log/nuts/error.log

    cd "$pkgdir"/opt/nuts/
    virtualenv2 env
    env/bin/pip install progressbar
    env/bin/pip install pyyaml
    env/bin/pip install jsonrpclib
    env/bin/pip install salt
    env/bin/pip install pykwalify

}
