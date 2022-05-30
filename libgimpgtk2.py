"""
This module provides a wrapper around the minimum of GLib/GTK 2
functionality to enable implementing a basic UI for plug-ins for GIMP 2.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import ctypes as ct

str_encode = lambda s : s.encode()
str_encode_optional = lambda s : (lambda : None, lambda : s.encode())[s != None]()
str_decode = lambda s : s.decode()

CANT_BE_BOTHERED_FOR_NOW = lambda : []
  # for _fields_ definitions I can’t be bothered to fill in for now

# from /usr/lib/«arch»/glib-2.0/include/glibconfig.h:

gsize = ct.c_ulong

# from glib-2.0/gobject/glib-types.h:

GType = gsize

# from glib-2.0/gobject/gclosure.h:

GCallback = ct.CFUNCTYPE(None) # actually might take args and return result, depending on context
GClosureNotify = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)

class GClosure(ct.Structure) :
    _fields_ = CANT_BE_BOTHERED_FOR_NOW()
#end GClosure

# from glib-2.0/gobject/gsignal.h:

GConnectFlags = ct.c_uint
# values for GConnectFlags:
G_CONNECT_AFTER = 1 << 0
G_CONNECT_SWAPPED = 1 << 1

class GTK :
    "useful definitions adapted from files in /usr/include/gtk-2.0/."

    # from gtk-2.0/gtk/gtktypeutils.h:

    CallbackMarshal = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p, ct.c_uint, ct.POINTER(ct.c_void_p))
    DestroyNotify = ct.CFUNCTYPE(None, ct.c_void_p)
    SignalFunc = ct.CFUNCTYPE(None)

    # from gtk-2.0/gtk/gtkenums.h:

    AttachOptions = ct.c_uint
    # values for AttachOptions:
    EXPAND = 1 << 0
    SHRINK = 1 << 1
    FILL = 1 << 2

    Orientation = ct.c_uint
    # values for Orientation:
    ORIENTATION_HORIZONTAL = 0
    ORIENTATION_VERTICAL = 1

    # from gtk-2.0/gtk/gtkwidget.h:

    class Widget(ct.Structure) :
        _fields_ = CANT_BE_BOTHERED_FOR_NOW()
    #end Widget

    # from gtk-2.0/gtk/gtkadjustment.h:

    class Adjustment(ct.Structure) :
        _fields_ = CANT_BE_BOTHERED_FOR_NOW()
    #end Adjustment

    # from gtk-2.0/gtk/gtkwindow.h:

    class Window(ct.Structure) :
        _fields_ = CANT_BE_BOTHERED_FOR_NOW()
    #end Window

    # from gtk-2.0/gtk/gtkdialog.h:

    DialogFlags = ct.c_uint
    # values for DialogFlags:
    DIALOG_MODAL = 1 << 0
    DIALOG_DESTROY_WITH_PARENT = 1 << 1
    DIALOG_NO_SEPARATOR = 1 << 2

    ResponseType = ct.c_uint
    # values for ResponseType:
    RESPONSE_NONE = -1
    RESPONSE_REJECT = -2
    RESPONSE_ACCEPT = -3
    RESPONSE_DELETE_EVENT = -4
    RESPONSE_OK = -5
    RESPONSE_CANCEL = -6
    RESPONSE_CLOSE = -7
    RESPONSE_YES = -8
    RESPONSE_NO = -9
    RESPONSE_APPLY = -10
    RESPONSE_HELP = -11

    class Dialog(ct.Structure) :
        _fields_ = CANT_BE_BOTHERED_FOR_NOW()
    #end Dialog

#end GTK

del CANT_BE_BOTHERED_FOR_NOW

#+
# Routine arg/result types
#-

libgobject2 = ct.cdll.LoadLibrary("libgobject-2.0.so.0")
libgtk2 = ct.cdll.LoadLibrary("libgtk-x11-2.0.so.0")

# from glib-2.0/gobject/gsignal.h:

libgobject2.g_signal_connect_data.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_void_p, ct.c_void_p, ct.c_void_p, GConnectFlags)
libgobject2.g_signal_connect_data.restype = ct.c_ulong

# from gtk-2.0/gtk/signal.h:

libgtk2.gtk_signal_connect_full.argtypes = (ct.c_void_p, ct.c_char_p, GCallback, GTK.CallbackMarshal, ct.c_void_p, GTK.DestroyNotify, ct.c_int, ct.c_int)
libgtk2.gtk_signal_connect_full.restype = ct.c_ulong

# from gtk-2.0/gtk/gtkwidget.h:

libgtk2.gtk_widget_show.argtypes = (ct.c_void_p,)
libgtk2.gtk_widget_show.restype = None
libgtk2.gtk_widget_destroy.argtypes = (ct.c_void_p,)
libgtk2.gtk_widget_destroy.restype = None
libgtk2.gtk_widget_set_tooltip_text.argtypes = (ct.c_void_p, ct.c_char_p)
libgtk2.gtk_widget_set_tooltip_text.restype = None
libgtk2.gtk_widget_set_tooltip_markup.argtypes = (ct.c_void_p, ct.c_char_p)
libgtk2.gtk_widget_set_tooltip_markup.restype = None

# from gtk-2.0/gtk/gtklabel.h:

libgtk2.gtk_label_new.argtypes = (ct.c_char_p,)
libgtk2.gtk_label_new.restype = ct.c_void_p
libgtk2.gtk_label_set_markup.argtypes = (ct.c_void_p, ct.c_char_p)
libgtk2.gtk_label_set_markup.restype = None
libgtk2.gtk_label_set_use_markup.argtypes = (ct.c_void_p, ct.c_bool)
libgtk2.gtk_label_set_use_markup.restype = None
libgtk2.gtk_label_set_mnemonic_widget.argtypes = (ct.c_void_p, ct.c_void_p)
libgtk2.gtk_label_set_mnemonic_widget.restype = None

# from gtk-2.0/gtk/gtkcontainer.h:

libgtk2.gtk_container_set_border_width.argtypes = (ct.c_void_p, ct.c_uint)
libgtk2.gtk_container_set_border_width.restype = None

# from gtk-2.0/gtk/gtkadjustment.h:

libgtk2.gtk_adjustment_new.argtypes = (ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
libgtk2.gtk_adjustment_new.restype = ct.c_void_p
libgtk2.gtk_adjustment_get_value.argtypes = (ct.c_void_p,)
libgtk2.gtk_adjustment_get_value.restype = ct.c_double
libgtk2.gtk_adjustment_set_value.argtypes = (ct.c_void_p, ct.c_double)
libgtk2.gtk_adjustment_set_value.restype = None
libgtk2.gtk_adjustment_configure.argtypes = (ct.c_void_p, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double)
libgtk2.gtk_adjustment_configure.restype = None

# from gtk-2.0/gtk/gtkspinbutton.h:

libgtk2.gtk_spin_button_new.argtypes = (ct.c_void_p, ct.c_double, ct.c_uint)
libgtk2.gtk_spin_button_new.restype = ct.c_void_p
libgtk2.gtk_spin_button_new_with_range.argtypes = (ct.c_double, ct.c_double, ct.c_double)
libgtk2.gtk_spin_button_new_with_range.restype = ct.c_void_p
libgtk2.gtk_spin_button_get_adjustment.argtypes = (ct.c_void_p,)
libgtk2.gtk_spin_button_get_adjustment.restype = ct.c_void_p
libgtk2.gtk_spin_button_get_value.argtypes = (ct.c_void_p,)
libgtk2.gtk_spin_button_get_value.restype = ct.c_double

# from gtk-2.0/gtk/gtktable.h:

libgtk2.gtk_table_new.argtypes = (ct.c_uint, ct.c_uint, ct.c_bool)
libgtk2.gtk_table_new.restype = ct.c_void_p
libgtk2.gtk_table_attach.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint, GTK.AttachOptions, GTK.AttachOptions, ct.c_uint, ct.c_uint)
libgtk2.gtk_table_attach.restype = None
libgtk2.gtk_table_attach_defaults.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_uint, ct.c_uint, ct.c_uint, ct.c_uint)
libgtk2.gtk_table_attach_defaults.restype = None
libgtk2.gtk_table_set_row_spacing.argtypes = (ct.c_void_p, ct.c_uint, ct.c_uint)
libgtk2.gtk_table_set_row_spacing.restype = None
libgtk2.gtk_table_set_row_spacings.argtypes = (ct.c_void_p, ct.c_uint)
libgtk2.gtk_table_set_row_spacings.restype = None
libgtk2.gtk_table_set_col_spacing.argtypes = (ct.c_void_p, ct.c_uint, ct.c_uint)
libgtk2.gtk_table_set_col_spacing.restype = None
libgtk2.gtk_table_set_col_spacings.argtypes = (ct.c_void_p, ct.c_uint)
libgtk2.gtk_table_set_col_spacings.restype = None

# from gtk-2.0/gtk/gtkbox.h:

#libgtk2._gtk_box_new.argtypes = (GTK.Orientation, ct.c_bool, ct.c_int)
#libgtk2._gtk_box_new.restype = ct.c_void_p
libgtk2.gtk_box_pack_start.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_bool, ct.c_bool, ct.c_uint)
libgtk2.gtk_box_pack_start.restype = None
libgtk2.gtk_box_pack_end.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_bool, ct.c_bool, ct.c_uint)
libgtk2.gtk_box_pack_end.restype = None

# from gtk-2.0/gtk/gtkdialog.h:

libgtk2.gtk_dialog_get_type.argtypes = ()
libgtk2.gtk_dialog_get_type.restype = GType
libgtk2.gtk_dialog_set_alternative_button_order_from_array.argtypes = (ct.c_void_p, ct.c_int, ct.POINTER(ct.c_int))
libgtk2.gtk_dialog_set_alternative_button_order_from_array.restype = None

libgtk2.gtk_dialog_get_action_area.argtypes = (ct.c_void_p,)
libgtk2.gtk_dialog_get_action_area.restype = ct.c_void_p
libgtk2.gtk_dialog_get_content_area.argtypes = (ct.c_void_p,)
libgtk2.gtk_dialog_get_content_area.restype = ct.c_void_p

#+
# Higher-level stuff follows
#-

class Object :
    "base wrapper for various GIMP-specific GTK object classes. Do not" \
    " instantiate this or any of its subclasses directly; use the various" \
    " create methods as appropriate."

    __slots__ = ("_gtkobj", "_wrappers")

    def __init__(self, _gtkobj) :
        self._gtkobj = _gtkobj
        self._wrappers = [] # for saving CFUNCTYPE wrappers to ensure they don’t randomly disappear
    #end __init__

    def signal_connect(self, name, handler, arg = None) :
        if isinstance(handler, ct._CFuncPtr) :
            c_handler = handler
        else :
            c_handler = GCallback(handler)
        #end if
        self._wrappers.append(c_handler)
        libgobject2.g_signal_connect_data \
            (self._gtkobj, str_encode(name), c_handler, arg, None, 0)
        return \
            self
    #end signal_connect

    def destroy(self) :
        if self._gtkobj != None :
            libgtk2.gtk_object_destroy(self._gtkobj)
            self._gtkobj = None
        #end if
    #end destroy

#end Object

class Widget(Object) :

    __slots__ = ()

    def destroy(self) :
        if self._gtkobj != None :
            libgtk2.gtk_widget_destroy(self._gtkobj)
            self._gtkobj = None
        #end if
    #end destroy

    def show(self) :
        libgtk2.gtk_widget_show(self._gtkobj)
        return \
            self
    #end show

    def set_tooltip_text(self, text) :
        libgtk2.gtk_widget_set_tooltip_text(self._gtkobj, str_encode(text))
    #end set_tooltip_text

    def set_tooltip_markup(self, markup) :
        libgtk2.gtk_widget_set_tooltip_markup(self._gtkobj, str_encode(markup))
    #end set_tooltip_markup

#end Widget

class Label(Widget) :

    __slots__ = ()

    @classmethod
    def create(celf, text) :
        return \
            celf(libgtk2.gtk_label_new(str_encode(text)))
    #end create

    def set_markup(self, text) :
        libgtk2.gtk_label_set_markup(self._gtkobj, str_encode(text))
    #end set_markup

    def set_use_markup(self, use_markup) :
        libgtk2.gtk_label_set_use_markup(self._gtkobj, use_markup)
    #end set_use_markup

    def set_mnemonic_widget(self, widget) :
        if not isinstance(widget, Widget) :
            raise TypeError("widget must be a Widget")
        #end if
        libgtk2.gtk_label_set_mnemonic_widget(self._gtkobj, widget._gtkobj)
    #end set_mnemonic_widget

#end Label

class Adjustment(Object) :

    __slots__ = ()

    @classmethod
    def create(celf, value, lower, upper, step_increment, page_increment, page_size) :
        return \
            celf(libgtk2.gtk_adjustment_new(value, lower, upper, step_increment, page_increment, page_size))
    #end create

    def get_value(self) :
        return \
            libgtk2.gtk_adjustment_get_value(self._gtkobj)
    #end get_value

#end Adjustment

class SpinButton(Widget) :

    __slots__ = ()

    @classmethod
    def create(celf, adjustment, climb_rate, digits) :
        if not isinstance(adjustment, Adjustment) :
            raise TypeError("adjustment must be an Adjustment.")
        #end if
        return \
            celf(libgtk2.gtk_spin_button_new(adjustment._gtkobj, climb_rate, digits))
    #end create

    @classmethod
    def create_with_range(celf, min, max, step) :
        return \
            celf(libgtk2.gtk_spin_button_new_with_range(min, max, step))
    #end create_with_range

    def get_adjustment(self) :
        return \
            Adjustment(libgtk2.gtk_spin_button_get_adjustment(self._gtkobj))
    #end get_adjustment

    def get_value(self) :
        return \
            libgtk2.gtk_spin_button_get_value(self._gtkobj)
    #end get_value

#end SpinButton

class ScaleEntry(Adjustment) :

    __slots__ = ()

#end ScaleEntry

class Container(Widget) :

    __slots__ = ()

    def set_border_width(self, border_width) :
        libgtk2.gtk_container_set_border_width(self._gtkobj, border_width)
    #end set_border_width

#end Container

class Table(Container) :

    __slots__ = ()

    @classmethod
    def create(celf, nr_rows, nr_cols, homogeneous) :
        gtkobj = libgtk2.gtk_table_new(nr_rows, nr_cols, homogeneous)
        return \
            celf(gtkobj)
    #end create

    def attach(self, child, left_attach, right_attach, top_attach, bottom_attach, xoptions : GTK.AttachOptions, yoptions : GTK.AttachOptions, xpadding, ypadding) :
        if not isinstance(child, Widget) :
            raise TypeError("child must be a Widget")
        #end if
        libgtk2.gtk_table_attach(self._gtkobj, child._gtkobj, left_attach, right_attach, top_attach, bottom_attach, xoptions, yoptions, xpadding, ypadding)
    #end attach

    def attach_defaults(self, child, left_attach, right_attach, top_attach, bottom_attach) :
        if not isinstance(child, Widget) :
            raise TypeError("child must be a Widget")
        #end if
        libgtk2.gtk_table_attach_defaults(self._gtkobj, child._gtkobj, left_attach, right_attach, top_attach, bottom_attach)
    #end attach_defaults

    def set_col_spacings(self, spacings) :
        libgtk2.gtk_table_set_col_spacings(self._gtkobj, spacings)
        return \
            self
    #end set_col_spacings

    def set_row_spacings(self, spacings) :
        libgtk2.gtk_table_set_row_spacings(self._gtkobj, spacings)
        return \
            self
    #end set_row_spacings

#end Table
