"""
This module provides a wrapper around the minimum of GLib/GTK 2
functionality to enable implementing a basic UI for plug-ins for Gimp 2.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import ctypes as ct

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

    # from gtk-2.0/gtk/gtkenums.h:

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

# from gtk-2.0/gtk/gtkwidget.h:

libgtk2.gtk_widget_show.argtypes = (ct.c_void_p,)
libgtk2.gtk_widget_show.restype = None
libgtk2.gtk_widget_destroy.argtypes = (ct.c_void_p,)
libgtk2.gtk_widget_destroy.restype = None

# from gtk-2.0/gtk/gtklabel.h:

libgtk2.gtk_label_new.argtypes = (ct.c_char_p,)
libgtk2.gtk_label_new.restype = ct.c_void_p
libgtk2.gtk_label_set_markup.argtypes = (ct.c_void_p, ct.c_char_p)
libgtk2.gtk_label_set_markup.restype = None
libgtk2.gtk_label_set_use_markup.argtypes = (ct.c_void_p, ct.c_bool)
libgtk2.gtk_label_set_use_markup.restype = None

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

libgtk2.gtk_spin_button_get_value.argtypes = (ct.c_void_p,)
libgtk2.gtk_spin_button_get_value.restype = ct.c_double

# from gtk-2.0/gtk/gtktable.h:

libgtk2.gtk_table_new.argtypes = (ct.c_uint, ct.c_uint, ct.c_bool)
libgtk2.gtk_table_new.restype = ct.c_void_p
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
