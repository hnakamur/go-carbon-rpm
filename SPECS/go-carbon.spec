%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%define debug_package %{nil}

%{!?_unitdir: %define _unitdir /usr/lib/systemd/system}

%global commit             90d894b3104c1a3caa6a5555803e634dfe26f807
%global shortcommit        %(c=%{commit}; echo ${c:0:7})

Name:	        go-carbon
Version:	0.10.0
Release:	1%{?dist}
Summary:	Carbon server for graphite

Group:		Development/Tools
License:	MIT License
URL:		https://github.com/lomik/go-carbon

# Source0 tarball file %{name}.tar.gz was created with the following commands.
#
# git clone https://github.com/lomik/go-carbon
# cd go-carbon
# git checkout 90d894b3104c1a3caa6a5555803e634dfe26f807
# make submodules
# cd ..
# tar cf - go-carbon | gzip -9 > go-carbon.tar.gz
Source0:	%{name}.tar.gz

Source1:	go-carbon.conf
Source2:	storage-schemas.conf
Source3:	storage-aggregation.conf
Source4:	go-carbon.service
Source5:	logrotate
BuildRoot:      %{name}

BuildRequires:  golang >= 1.8

%description
Golang implementation of Graphite/Carbon server with classic architecture: Agent -> Cache -> Persister

%prep
%setup -c -n %{_builddir}/%{name}/go/src/github.com/lomik

%build
export GOPATH=%{_builddir}/%{name}/go:%{_builddir}/%{name}/go/src/github.com/lomik/%{name}/_vendor
cd %{_builddir}/%{name}/go/src/github.com/lomik/%{name}
go build

%install
%{__rm} -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{_bindir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/%{name}
%{__mkdir} -p %{buildroot}/var/lib/graphite/whisper
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_unitdir}

%{__install} -pD -m 755 %{_builddir}/%{name}/go/src/github.com/lomik/%{name}/%{name} \
    %{buildroot}/%{_bindir}/%{name}
%{__install} -pD -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -pD -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}/storage-schemas.conf
%{__install} -pD -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}/storage-aggregation.conf
%{__install} -pD -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE5} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/storage-schemas.conf
%config(noreplace) %{_sysconfdir}/%{name}/storage-aggregation.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/log/%{name}
%attr(0755,root,root) %dir /var/lib/graphite
%attr(0755,%{carbon_user},%{carbon_group}) %dir /var/lib/graphite/whisper
%{_unitdir}/%{name}.service

%pre
# Add the "carbon" user
getent group %{carbon_group} >/dev/null || groupadd -r %{carbon_group}
getent passwd %{carbon_user} >/dev/null || \
    useradd -r -g %{carbon_group} -s /sbin/nologin \
    --no-create-home -c "carbon user"  %{carbon_user}
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /usr/bin/systemctl preset %{name}.service >/dev/null 2>&1 || :
fi
if [ $1 -eq 1 ]; then
    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/%{name} ]; then
        if [ ! -e %{_localstatedir}/log/%{name}/%{name}.log ]; then
            touch %{_localstatedir}/log/%{name}/%{name}.log
            %{__chmod} 640 %{_localstatedir}/log/%{name}/%{name}.log
            %{__chown} %{carbon_user}:%{carbon_loggroup} %{_localstatedir}/log/%{name}/%{name}.log
        fi
    fi
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /usr/bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
    /usr/bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
fi

%postun
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%changelog
* Fri Jun 16 2017 <hnakamur@gmail.com> - 0.10.0-1
- Update to 0.10.0

* Sat Jun 10 2017 <hnakamur@gmail.com> - 0.10.0-0.4.6fbd091b3
- Update to commit 6fbd091b342316e790fe484f861b51252075525b

* Fri Jun  9 2017 <hnakamur@gmail.com> - 0.10.0-0.3.a31d03e67
- Update to commit a31d03e67d36941482ae041676e3afe8df898db4

* Sat May 27 2017 <hnakamur@gmail.com> - 0.10.0-0.2.42b9832d1
- Update to commit 42b9832d13240ff044c86768e8d0dc1f356d9458

* Sun May 21 2017 <hnakamur@gmail.com> - 0.10.0-0.1.beta1
- 0.10.0-beta1
- Adjust file paths to the same as the upstream rpm

* Wed May 10 2017 <hnakamur@gmail.com> - 0.9.1-0.6.gite825d3a
- Fix post, preun, postun scripts.

* Sun Apr 23 2017 <hnakamur@gmail.com> - 0.9.1-0.4.git42b9832
- Update to commit 42b9832d13240ff044c86768e8d0dc1f356d9458

* Sun Apr 23 2017 <hnakamur@gmail.com> - 0.9.1-0.3.git61f1fa6
- Fix logrotate for when go-carbon service is stopped

* Tue Apr 11 2017 <hnakamur@gmail.com> - 0.9.1-0.2.git61f1fa6
- Update to commit 61f1fa6d46c5c48a906d7becaf75bb3a58f7e532
- Use dateext for logrotate

* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.9.1-0.1.gite0fae15
- Initial release
