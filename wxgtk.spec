# disable python bytecompile outside python dirs
%global _python_bytecompile_extra 0

# disable unsecure webkit1 support
%bcond_with webkit1

# bcond_with gtk3    = gtk2
# bcond_without gtk3 = gtk3
%bcond_without gtk3


%define gtkver %{?with_gtk3:3}%{!?with_gtk3:2}

%define oname           wxWidgets

%define major           4
%define api             3.1
%define libnameudev     %mklibname wxgtku %{api} -d

%define apind		%(echo %{api} |tr -d .)

Summary:        GTK+ port of the wxWidgets library
Name:           wxgtk
Version:        3.1.4
Release:        1
License:        wxWidgets Library Licence
Group:          System/Libraries
URL:            http://www.wxwidgets.org/
Source0:        https://github.com/wxWidgets/wxWidgets/releases/download/v%{version}/%{oname}-%{version}.tar.bz2
Patch0:         wxWidgets-2.9.5-fix-linking.patch
Patch1:         wxWidgets-2.9.5-multiarch-includes.patch
# Originally from Gentoo
Patch2:         wxWidgets-3.0.4-collision.patch
# From Fedora
Patch3:		wxGTK3-3.0.3-abicheck.patch

#BuildRequires:  bakefile
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(cppunit)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glu)
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-plugins-base-1.0)
%if %{with gtk3}
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(webkit2gtk-4.0)
%else
BuildRequires:  pkgconfig(gtk+-2.0)
%if %{with webkit1}
BuildRequires:  pkgconfig(webkit-1.0) >= 1.3.1
%endif
%endif
BuildRequires:  pkgconfig(libmspack)
BuildRequires:  pkgconfig(libnotify) >= 0.7
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(sm)
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(zlib)

%description
wxWidgets is a free C++ library for cross-platform GUI development.
With wxWidgets, you can create applications for different GUIs (GTK+,
Motif/LessTif, MS Windows, Mac) from the same source code.

%package -n %{name}%{api}
Summary:        GTK+ port of the wxWidgets library
Group:          System/Libraries
Obsoletes:      %{name} > 3.1

%description -n %{name}%{api}
wxWidgets is a free C++ library for cross-platform GUI development.
With wxWidgets, you can create applications for different GUIs (GTK+,
Motif/LessTif, MS Windows, Mac) from the same source code.

%global wxlibs wx_baseu \\\
wx_baseu_net \\\
wx_baseu_xml \\\
wx_gtk%{gtkver}u_adv \\\
wx_gtk%{gtkver}u_aui \\\
wx_gtk%{gtkver}u_core \\\
wx_gtk%{gtkver}u_gl \\\
wx_gtk%{gtkver}u_html \\\
wx_gtk%{gtkver}u_media \\\
wx_gtk%{gtkver}u_propgrid \\\
wx_gtk%{gtkver}u_qa \\\
wx_gtk%{gtkver}u_ribbon \\\
wx_gtk%{gtkver}u_richtext \\\
wx_gtk%{gtkver}u_stc \\\
wx_gtk%{gtkver}u_xrc

%if %{with webkit1} || %{with gtk3}
%global wxlibs %{wxlibs} wx_gtk%{gtkver}u_webview
%endif

%{expand:%(for lib in %{wxlibs}; do cat << EOF
%%global libname$lib %%mklibname $lib %{api} %{major}
%%package -n %%{libname$lib}
Summary:        wxGTK $lib shared library
Group:          System/Libraries
Requires:       %{name}%{api} >= %{version}-%{release}
EOF
done)}

%{expand:%(for lib in %{wxlibs}; do cat << EOF
%%description -n %%{libname$lib}
This package contains the library needed to run programs dynamically
linked with the wxGTK.
EOF
done)}

%{expand:%(for lib in %{wxlibs}; do cat << EOF
%%files -n %%{libname$lib}
%{_libdir}/lib$lib-%{api}.so.%{major}{,.*}
%if "$lib" == "wx_gtk%{gtkver}u_webview"
%if %{with gtk3}
%dir %{_libdir}/wx/%{version}/web-extensions/
%{_libdir}/wx/%{version}/web-extensions/webkit2_extu-%{version}.so
%endif
%endif
EOF
done)}

%package -n %{libnameudev}
Summary:        Header files and development documentation for wxGTK - unicode
Group:          Development/C++
Requires:	%{expand:%(for lib in %{wxlibs}; do echo -n "%%{libname$lib} = %{version}-%{release} "; done)}
Provides:       libwxgtku%{api}-devel = %{version}-%{release}
Provides:       wxgtku%{api}-devel = %{version}-%{release}
Provides:       wxgtk%{api}-devel = %{version}-%{release}
Provides:       libwxgtk%{api}-devel = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Requires(post):         update-alternatives
Requires(postun):       update-alternatives

%description -n %{libnameudev}
Header files for the unicode enabled version of wxGTK, the GTK+ port of
the wxWidgets library.

%prep
%setup -qn %{oname}-%{version}
%autopatch -p1

# (fwang) Don't promote LDFLAGS in wx-config
sed -i -e 's/@LDFLAGS@//' -e 's/@WXCONFIG_CXXFLAGS@//' wx-config.in

# fix plugin dir for 64-bit
sed -i -e 's|/lib|/%{_lib}|' src/unix/stdpaths.cpp

find samples demos -name .cvsignore -delete

%build
aclocal --force -I$PWD/build/aclocal
autoconf -f
libtoolize --copy --force
# --disable-optimise prevents our $RPM_OPT_FLAGS being overridden
# (see OPTIMISE in configure).
# this code dereferences type-punned pointers like there's no tomorrow.
CFLAGS="%{optflags} -fno-strict-aliasing"
CXXFLAGS="%{optflags} -fno-strict-aliasing"

# In OMV #configure passes disable-static options by default to ensure, we have shared libraries. 
# This broke build for this package, because it see it as: unrecognized options: --disable-static, --disable-silent-rules
# Solution is below:
CC="%{__cc}" CXX="%{__cxx}" CFLAGS="%{optflags}" CXXFLAGS="%{optflags}" ./configure --prefix=%{_prefix} --libdir=%{_libdir} --enable-intl --with-gtk=%{gtkver} --with-sdl --with-libmspack --with-libpng=sys --with-libjpeg=sys --with-libtiff=sys --with-zlib=sys --with-expat=sys --with-regex=builtin --disable-optimise --enable-calendar --enable-compat28 --enable-controls --enable-msgdlg --enable-dirdlg --enable-numberdlg --enable-splash --enable-textdlg --enable-graphics_ctx --enable-grid --enable-catch_segvs --enable-mediactrl --enable-dataviewctrl --enable-permissive --enable-ipv6 --disable-rpath

%make_build
# Why isn't this this part of the main build? Need to investigate.
%make_build -C locale allmo

#gw prepare samples
pushd demos
        make clean
        rm -f makefile* demos.bkl
popd

pushd samples
        make clean
        rm -f makefile* samples.bkl
popd

find demos samples -name Makefile|xargs perl -pi -e 's^CXXC =.*^CXXC=\$(CXX) `wx-config --cflags`^'
find demos samples -name Makefile|xargs perl -pi -e 's^EXTRALIBS =.*^EXTRALIBS=^'
find demos samples -name Makefile|xargs perl -pi -e 's^SAMPLES_RPATH_FLAG =.*^SAMPLES_RPATH_FLAG=^'

%install
%make_install

# dummy translation file
find %{buildroot} -name "wxmsw.mo" -delete

%find_lang wxstd%{apind}

%post -n %{libnameudev}
%{_sbindir}/update-alternatives \
        --install %{_bindir}/wx-config wx-config %{_bindir}/wx-config-%{api} 35 \
	--slave %{_bindir}/wxrc wxrc %{_bindir}/wxrc-%{api}

%postun -n %{libnameudev}
if [ $1 -eq 0 ]; then
%{_sbindir}/update-alternatives \
        --remove wx-config %{_bindir}/wx-config-%{api}
fi

%files -n %{name}%{api} -f wxstd%{apind}.lang
%doc README.md

%files -n %{libnameudev}
%doc samples/ docs/ demos/
%ghost %{_bindir}/wx-config
%ghost %{_bindir}/wxrc
%{_bindir}/wx-config-%{api}
%{_bindir}/wxrc-%{api}
%{_includedir}/wx-%{api}/
%dir %{_libdir}/wx/
%dir %{_libdir}/wx/include/
%dir %{_libdir}/wx/include/gtk%{gtkver}-unicode-%{api}/
%dir %{_libdir}/wx/include/gtk%{gtkver}-unicode-%{api}/wx/
%dir %{_libdir}/wx/config
%{_libdir}/wx/config/gtk%{gtkver}-unicode-%{api}
%{_libdir}/wx/include/gtk%{gtkver}-unicode-%{api}/wx/setup.h
%{_libdir}/libwx_baseu-%{api}.so
%{_libdir}/libwx_baseu_net-%{api}.so
%{_libdir}/libwx_baseu_xml-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_adv-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_aui-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_core-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_gl-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_html-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_media-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_propgrid-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_qa-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_ribbon-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_richtext-%{api}.so
%{_libdir}/libwx_gtk%{gtkver}u_stc-%{api}.so
%if %{with webkit1} || %{with gtk3}
%{_libdir}/libwx_gtk%{gtkver}u_webview-%{api}.so
%endif
%{_libdir}/libwx_gtk%{gtkver}u_xrc-%{api}.so
%{_datadir}/bakefile/presets/wx*
%{_datadir}/aclocal/wxwin%{apind}.m4
