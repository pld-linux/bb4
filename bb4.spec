Summary:	Big Brother System and Network Monitor
Summary(pl):	Wielki Brat - monitor systemów i sieci
Name:		bb4
Version:	1.8d
%define	nshort	bb18d
Release:	2
License:	Free for non-commercial use, 30-day trial for commercial use; not distributable
Group:		Networking
Source0:	bb-%{version}.tar.gz
Source1:	%{name}.init
Patch0:		%{name}-pld.patch
NoSource:	0
URL:		http://bb4.com/
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	/usr/bin/setsid
Conflicts:	iputils-ping < 1:ss020124
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_etcdir		/etc/bb
%define		_libdir		/usr/lib/bb
%define		_htmldir	/home/services/httpd/html/bb
%define		_cgidir		/home/services/httpd/cgi-bin
%define		_vardir		/var/lib/bb
%define		_sysconfdir	/etc/dummy

%description
Big Brother - network monitoring system.

%description -l pl
Wielki Brat - monitor systemów i sieci.

%prep
%setup -q -c
tar xf %{nshort}.tar
%patch -p1

%build
cd %{nshort}
touch tmp/.license
mkdir cgi-bin
CGIDIR=`pwd`/cgi-bin
MYID=`id -nu`
MYGR=`id -ng`
cd install
./bbconfig pld <<EOF

y
bb
n
y
pldmachine
pldmachine
y
y
bb@localhost
/bb
$CGIDIR
/cgi-bin
$MYID
$MYGR
EOF

cd ../src
%{__make} OPTCFLAGS="%{rpmcflags}"

# installs to ../bin
%{__make} install

cd ../bin
for f in bbmv bbprune bbrm ; do
	sed -e 's@&&BBHOME@%{_libdir}@' $f.DIST > $f
done
rm -f *.DIST

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_htmldir}/{html,notes,rep},%{_cgidir},%{_vardir}/tmp} \
	$RPM_BUILD_ROOT{%{_etcdir},/etc/rc.d/init.d}

cp -rf bbvar/* $RPM_BUILD_ROOT%{_vardir}

for f in bb-ack.sh bb-hist.sh bb-histlog.sh bb-hostsvc.sh bb-rep.sh bb-replog.sh ; do
	sed -e 's@&&BBHOME@%{_libdir}@' %{nshort}/web/$f.DIST > $RPM_BUILD_ROOT%{_cgidir}/$f
done
sed -e 's@&BBHOME@%{_libdir}@' %{nshort}/runbb.sh.DIST > $RPM_BUILD_ROOT%{_libdir}/runbb.sh

rm -f %{nshort}/web/*.DIST %{nshort}/www/help/*.DIST

cp -rf %{nshort}/{bin,ext,web} $RPM_BUILD_ROOT%{_libdir}
cp -rf %{nshort}/www/{gifs,gifs-bb13,psy,help} $RPM_BUILD_ROOT%{_htmldir}

install %{nshort}/etc/bbchk*.sh $RPM_BUILD_ROOT%{_libdir}/bin

ln -sf bb.html $RPM_BUILD_ROOT%{_htmldir}/index.html
ln -sf %{_etcdir} $RPM_BUILD_ROOT%{_libdir}/etc
ln -sf %{_htmldir} $RPM_BUILD_ROOT%{_libdir}/www
ln -sf %{_vardir}/tmp $RPM_BUILD_ROOT%{_libdir}/tmp
ln -sf %{_vardir} $RPM_BUILD_ROOT/usr/lib/bbvar

for f in bb-bbexttab bb-cputab bb-dftab bb-msgstab bb-proctab security ; do
	sed -e 's/^[^#]/#\&/' %{nshort}/etc/$f.DIST > $RPM_BUILD_ROOT%{_etcdir}/$f
done
echo '0.0.0.0/0.0.0.0' >> $RPM_BUILD_ROOT%{_etcdir}/security
sed -e 's/^[^#]/#\&/' %{nshort}/etc/bb-hosts > $RPM_BUILD_ROOT%{_etcdir}/bb-hosts
install %{nshort}/etc/{bbdef.sh,bbinc.sh,bbsys.local,bbsys.sh,bbwarnrules.cfg,bbwarnsetup.cfg,*.scr} \
	$RPM_BUILD_ROOT%{_etcdir}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/bb

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid bb`" ]; then
	if [ "`/usr/bin/getgid bb`" != "73" ]; then
		echo "Error: group bb doesn't have gid=73. Correct this before installing BB." 1>&2
                exit 1
        fi
else
        /usr/sbin/groupadd -g 73 -r -f bb
fi
if [ -n "`/bin/id -u bb 2>/dev/null`" ]; then
	if [ "`/bin/id -u bb`" != "73" ]; then
		echo "Error: user bb doesn't have uid=73. Correct this before installing BB." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 73 -r -d %{_vardir} -s /bin/sh -c "Big Brother" -g bb -G root,proc,adm bb 1>&2
fi

%post
/sbin/chkconfig --add bb
if [ -f /var/lock/subsys/bb ]; then
	/etc/rc.d/init.d/bb restart >&2
else
	echo "Run \"/etc/rc.d/init.d/bb start\" to start Big Brother daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/bb ]; then
		 /etc/rc.d/init.d/bb stop >&2
	fi
	/sbin/chkconfig --del bb
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel bb
	/usr/sbin/groupdel bb
fi

%files
%defattr(644,root,root,755)
%doc %{nshort}/{LICENSE,README,README.CHANGES,README.SECURITY,README.SUPPORT}
%dir %{_etcdir}
%config(noreplace) %verify(not size mtime md5) %{_etcdir}/*
%attr(755,root,root) %{_cgidir}/*
%dir %{_libdir}
%attr(755,root,root) %{_libdir}/bin
%{_libdir}/etc
%attr(755,root,root) %{_libdir}/ext
%dir %attr(755,root,root) %{_libdir}/web
%{_libdir}/web/*_*er
%attr(755,root,root) %{_libdir}/web/bb-*
%attr(755,root,root) %{_libdir}/web/mk*
%{_libdir}/www
%{_libdir}/tmp
%attr(755,root,root) %{_libdir}/runbb.sh
/usr/lib/bbvar
%attr(775,root,bb) %dir %{_htmldir}
%attr(775,root,bb) %{_htmldir}/html
%{_htmldir}/gifs*
%{_htmldir}/help
%{_htmldir}/index.html
%{_htmldir}/notes
%{_htmldir}/psy
%attr(775,root,http) %{_htmldir}/rep
%dir %{_vardir}
%attr(775,root,bb) %{_vardir}/*
%attr(754,root,root) /etc/rc.d/init.d/bb
