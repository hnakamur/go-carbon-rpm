%define carbon_user carbon
%define carbon_group carbon
%define carbon_loggroup adm

%global commit             e0fae152afccbc0133fb7babe48c4f708456f639
%global shortcommit        %(c=%{commit}; echo ${c:0:7})

Name:	        go-carbon
Version:	0.9.1
Release:	0.1.git%{shortcommit}%{?dist}
Summary:	Carbon server for graphite

Group:		Development/Tools
License:	MIT License
URL:		https://github.com/lomik/go-carbon

# NOTE: We use "git clone" in %prep instead of having tarball here
# since we need .git directory to run "make submodules" to get
# dependency packages of go-carbon.
#Source0:	%{name}.tar.gz

Source1:	go-carbon.conf
Source2:	schemas
Source3:	go-carbon.service
Source4:	logrotate
BuildRoot:      %{name}

BuildRequires:  golang >= 1.8
BuildRequires:  git

%description
Golang implementation of Graphite/Carbon server with classic architecture: Agent -> Cache -> Persister

%prep
%{__rm} -rf %{_builddir}

# NOTE: To use go "get ./..." to install dependencies,
# we need to have .git directory in carbonapi source directory.
%{__mkdir} -p %{_builddir}/%{name}/go/src/github.com/lomik
cd %{_builddir}/%{name}/go/src/github.com/lomik
git clone https://github.com/lomik/%{name}
cd %{_builddir}/%{name}/go/src/github.com/lomik/%{name}
git checkout %{commit}

%build
export GOPATH=%{_builddir}/%{name}/go:%{_builddir}/%{name}/go/src/github.com/lomik/%{name}/_vendor
cd %{_builddir}/%{name}/go/src/github.com/lomik/%{name}
make submodules
make

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
* Mon Apr 10 2017 <hnakamur@gmail.com> - 0.9.1-0.1.gite0fae15
- Initial release
