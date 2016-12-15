pkgname=nuts
pkgver=v1.0.3
pkgrel=1
pkgdesc="A Network Unit Test System with Saltstack as Executor"
arch=('x86_64')
url="https://github.com/xsicht/SA_Network-Unit-Tests"
license=('unknown')
depends=('salt>=2016.11.0-1' 'python>=3.5.2-3' 'python-progressbar>=2.3-7' 'python-yaml>=3.12-1' 'python-pip>=8.1.2-1' 'python-crypto>=2.6.1')
source=("https://github.com/asta1992/Nuts/archive/"$pkgver".tar.gz")
md5sums=('c208c32239e873f333764fa1d745ddb7')


package() {
  	pip install --user jsonrpclib
  	pip install --user salt
  	pip install --user pykwalify

  	install -d "$pkgdir"/opt/nuts/src
  	install -d "$pkgdir"/usr/bin
  	install -d "$pkgdir"/srv/salt/_modules
  	install -d "$pkgdir"/var/log/nuts/

  	cp -R "$srcdir"/Nuts-1.0.3/src/* "$pkgdir"/opt/nuts/src
    cp -R "$srcdir"/Nuts-1.0.3/nuts.py "$pkgdir"/opt/nuts
    cp -R "$srcdir"/Nuts-1.0.3/nuts "$pkgdir"/usr/bin
    cp -R "$srcdir"/Nuts-1.0.3/_modules/* "$pkgdir"/srv/salt/_modules
    touch "$pkgdir"/var/log/nuts/error.log

}
