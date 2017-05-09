%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%define debug_package %{nil}

%{!?_unitdir: %define _unitdir /usr/lib/systemd/system}

%global commit             e825d3aa0bef05b3d64ef9a9d770f62488a65b3a
%global shortcommit        %(c=%{commit}; echo ${c:0:7})

Name:	        go-carbon
Version:	0.9.1
Release:	0.5.git%{shortcommit}%{?dist}
Summary:	Carbon server for graphite

Group:		Development/Tools
License:	MIT License
URL:		https://github.com/lomik/go-carbon

# Source0 tarball file %{name}.tar.gz was created with the following commands.
#
# git clone https://github.com/lomik/go-carbon
# cd go-carbon
# git checkout e825d3aa0bef05b3d64ef9a9d770f62488a65b3a
# make submodules
# cd ..
# tar cf - go-carbon | gzip -9 > go-carbon.tar.gz
Source0:	%{name}.tar.gz

Source1:	go-carbon.conf
Source2:	schemas
Source3:	go-carbon.service
Source4:	logrotate
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
%{__mkdir} -p %{buildroot}%{_sbindir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}
%{__mkdir} -p %{buildroot}/data/graphite/whisper
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_unitdir}

%{__install} -pD -m 755 %{_builddir}/%{name}/go/src/github.com/lomik/%{name}/%{name} \
    %{buildroot}/%{_sbindir}/%{name}
%{__install} -pD -m 644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/%{name}.conf
%{__install} -pD -m 644 %{SOURCE2} %{buildroot}/data/graphite/schemas
%{__install} -pD -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE4} \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

%files
%defattr(-,root,root,-)
%{_sbindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) /data/graphite/schemas
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %dir %{_localstatedir}/log/%{name}
%attr(0755,root,root) %dir /data/graphite
%attr(0755,%{carbon_user},%{carbon_group}) %dir /data/graphite/whisper
%{_unitdir}/%{name}.service

%pre
# Add the "carbon" user
getent group %{carbon_group} >/dev/null || groupadd -r %{carbon_group}
getent passwd %{carbon_user} >/dev/null || \
    useradd -r -g %{carbon_group} -s /sbin/nologin \
    --no-create-home -c "carbon user"  %{carbon_user}
exit 0

%post
%systemd_post %{name}.service
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
%systemd_preun %{name}.service

%postun
%systemd_postun

%changelog
* Tue May  9 2017 <hnakamur@gmail.com> - 0.9.1-0.5.gite825d3a
- Update to commit e825d3aa0bef05b3d64ef9a9d770f62488a65b3a

* Sun Apr 23 2017 <hnakamur@gmail.com> - 0.9.1-0.4.git42b9832
- Update to commit 42b9832d13240ff044c86768e8d0dc1f356d9458

* Sun Apr 23 2017 <hnakamur@gmail.com> - 0.9.1-0.3.git61f1fa6
- Fix logrotate for when go-carbon service is stopped

* Tue Apr 11 2017 <hnakamur@gmail.com> - 0.9.1-0.2.git61f1fa6
- Update to commit 61f1fa6d46c5c48a906d7becaf75bb3a58f7e532
- Use dateext for logrotate

* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.9.1-0.1.gite0fae15
- Initial release
