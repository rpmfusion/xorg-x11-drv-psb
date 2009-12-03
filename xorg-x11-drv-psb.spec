%global tarball		xserver-xorg-video-psb
%global moduledir	%(pkg-config xorg-server --variable=moduledir )
%global driverdir	%{moduledir}/drivers

Summary:	Intel GMA500 (Poulsbo) video driver
Name:		xorg-x11-drv-psb
Version:	0.32.0
Release:	1%{?dist}
URL:		http://netbook-remix.archive.canonical.com/updates/pool/public/x/xserver-xorg-video-psb/
Source0:	http://netbook-remix.archive.canonical.com/updates/pool/public/x/xserver-xorg-video-psb/%{tarball}_%{version}.orig.tar.gz
# Causes psb module to be loaded when a GMA500 adapter PCI ID is found
# because the freaking module's too broken to include its own modalias
Source1:	poulsbo-modprobe.conf
# Automates X.org configuration (stolen from the NVIDIA package)
Source2:	psb-config-display
Source3:	psb-init
# Look for the variant libdrm in the right place
Patch0:		xorg-x11-drv-psb-0.31.0-libdrm.patch
# Don't do ACPI detection by default
Patch1:		xorg-x11-drv-psb-0.31.0-ignoreacpi.patch
# Attempted patch for X server 1.7
Patch2:		xorg-x11-drv-psb-0.31.0-xserver17.patch
# From UNR: disable LidTimer option to suppress polling
Patch3:		01_disable_lid_timer.patch
License:	MIT
Group:		User Interface/X Hardware Support
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if 0%{?fedora} > 11
ExclusiveArch:  i686
%else %if 0%{?fedora} > 10
ExclusiveArch:  i586
%else
ExclusiveArch:  i386
%endif

BuildRequires:	pkgconfig
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	xorg-x11-server-sdk
BuildRequires:	xorg-x11-proto-devel
BuildRequires:	libdrm-poulsbo-devel
BuildRequires:	mesa-libGL-devel
BuildRequires:	freeglut-devel

Requires:	xorg-x11-server-Xorg >= 1.1.0
Requires:	kmod-psb
Requires:	psb-firmware
Requires:	xpsb-glx
Requires:	libdrm-poulsbo
Provides:	psb-kmod-common
Requires:	livna-config-display

Requires(post):		livna-config-display
Requires(preun):	livna-config-display
Requires(post):		chkconfig
Requires(preun):	chkconfig

%description 
Video driver for the Intel GMA500 video chipset, also known as Poulsbo.
Note this driver depends on several proprietary pieces (and an
obsolete version of libdrm) to work, and is hence inappropriate for
submission to the main Fedora repositories.

%prep
%setup -q -n %{tarball}-%{version}
%patch0 -p1 -b .libdrm
%patch1 -p1 -b .ignoreacpi
%patch2 -p1 -b .xserver17
%patch3 -p1 -b .lidtimer

iconv -f iso-8859-15 -t utf-8 -o man/psb.man.utf8 man/psb.man && mv man/psb.man.utf8 man/psb.man

%build
autoreconf -i
%configure --disable-static
make

%install
rm -rf %{buildroot}
%makeinstall mandir=%{_mandir} DESTDIR=%{buildroot}

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find %{buildroot} -regex ".*\.la$" | xargs rm -f --

mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/modprobe.d/poulsbo.conf

install -D -p -m 0755 %{SOURCE2} %{buildroot}%{_sbindir}/psb-config-display
install -D -p -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/psb

%clean
rm -rf %{buildroot}

%post
if [ "$1" -eq "1" ]; then
  # Enable driver when installing
  %{_sbindir}/psb-config-display enable &>/dev/null ||:
  # Add init script and start it
  /sbin/chkconfig --add psb ||:
  %{_initrddir}/psb start &>/dev/null ||:
fi

%preun
if [ "$1" -eq "0" ]; then
    # Disable driver on final removal
    test -f %{_sbindir}/psb-config-display && %{_sbindir}/nvidia-config-display disable &>/dev/null ||:
    %{_initrddir}/psb stop &> /dev/null ||:
    /sbin/chkconfig --del psb ||:
fi ||:

%files
%defattr(-,root,root,-)
%{driverdir}/psb_drv.so
%{driverdir}/libmm.so
%{_sbindir}/psb-config-display
%{_initrddir}/psb
%config %{_sysconfdir}/modprobe.d/poulsbo.conf
%{_mandir}/man4/*.4*

%changelog
* Thu Dec 3 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.32.0-1
- newer upstream release 0.32.0 (fixes a "single SDVO jitter issue")
- add 01_disable_lid_timer.patch from UNR: disable LidTimer option
  by default to suppress polling for lid status every second

* Wed Sep 30 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-15
- change my email address in changelog to correct one for Fusion

* Fri Sep 25 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-14
- switch to requiring kmod-psb not akmod-psb now we're in rpmfusion

* Fri Aug 28 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-13
- update X server 1.7 patch with a further fix (thanks ajax)

* Fri Aug 28 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-12
- try and patch for X server 1.7 (F12)

* Mon Aug 24 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-11
- correct exclusivearch for rpmfusion buildsystem

* Thu Aug 20 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-10
- exclusivearch ix86 (there's no 64-bit poulsbo hardware)
- mark config file as config
- fix nvidia reference in comments of init script

* Wed Aug 19 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-9
- add another PCI ID to the modprobe config file

* Wed Aug 19 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-8
- fix up manpage character set

* Wed Aug 19 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-7
- drop greedy.patch as it doesn't seem to work (can't work out why)
- add xorg.conf handling initscript and script based on the ones used
  in NVIDIA and ATI packages, including setting migration heuristic
  in xorg.conf since the patch didn't work

* Fri Aug 14 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-6
- add greedy.patch: default to greedy migration heuristic (gives
  better performance for multiple testers)
- add ignoreacpi.patch: default to ignoreACPI (required to avoid X
  crashing for multiple testers)

* Tue Aug 11 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-5
- patch build to find newly relocated libdrm-poulsbo

* Mon Aug 10 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-4
- add a modprobe config file to make the kernel module auto-load (in
  this package as it's doing the job of psb-kmod-common)

* Mon Aug 10 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-3
- Require akmod-psb not kmod-psb so I don't have to keep rebuilding

* Mon Aug 10 2009 Adam Williamson <adamwill AT shaw DOT ca> - 0.31.0-2
- Begin changelog tracking

