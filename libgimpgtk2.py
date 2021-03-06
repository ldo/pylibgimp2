"""
This module provides a wrapper around the minimum of GLib/GTK 2
functionality to enable implementing a basic UI for plug-ins for GIMP 2.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

# GTK 2 and related docs can be found at <https://developer-old.gnome.org/references>.

import ctypes as ct

# lowest-level GLib/GObject stuff is now in Gabler’s gegl module
import gegl
from gegl import \
    str_encode, \
    str_encode_optional, \
    str_decode, \
    GType, \
    GValue, \
    GCallback

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

    # from gtk-2.0/gtk/gtktreemodel.h:

    class TreeIter(ct.Structure) :
        _fields_ = \
            [
                ("stamp", ct.c_int),
                ("user_data", ct.c_void_p),
                ("user_data2", ct.c_void_p),
                ("user_data3", ct.c_void_p),
            ]
    #end TreeIter

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

#end GTK

#+
# Routine arg/result types
#-

libgtk2 = ct.cdll.LoadLibrary("libgtk-x11-2.0.so.0")

# from gtk-2.0/gtk/gtksignal.h:

libgtk2.gtk_signal_connect_full.argtypes = (ct.c_void_p, ct.c_char_p, GCallback, GTK.CallbackMarshal, ct.c_void_p, GTK.DestroyNotify, ct.c_int, ct.c_int)
libgtk2.gtk_signal_connect_full.restype = ct.c_ulong

# from gtk-2.0/gtk/gtkmisc.h:

libgtk2.gtk_misc_set_alignment.argtypes = (ct.c_void_p, ct.c_float, ct.c_float)
libgtk2.gtk_misc_set_alignment.restype = None
libgtk2.gtk_misc_get_alignment.argtypes = (ct.c_void_p, ct.POINTER(ct.c_float), ct.POINTER(ct.c_float))
libgtk2.gtk_misc_get_alignment.restype = None
libgtk2.gtk_misc_set_padding.argtypes = (ct.c_void_p, ct.c_int, ct.c_int)
libgtk2.gtk_misc_set_padding.restype = None
libgtk2.gtk_misc_get_padding.argtypes = (ct.c_void_p, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
libgtk2.gtk_misc_get_padding.restype = None

# from gtk-2.0/gtk/gtkliststore.h:

libgtk2.gtk_list_store_newv.argtypes = (ct.c_int, ct.POINTER(GType))
libgtk2.gtk_list_store_newv.restype = ct.c_void_p
libgtk2.gtk_list_store_append.argtypes = (ct.c_void_p, ct.POINTER(GTK.TreeIter))
libgtk2.gtk_list_store_append.restype = None
libgtk2.gtk_list_store_set_valuesv.argtypes = (ct.c_void_p, ct.POINTER(GTK.TreeIter), ct.POINTER(ct.c_int), ct.POINTER(GValue), ct.c_int)
libgtk2.gtk_list_store_set_valuesv.restype = None

# from gtk-2.0/gtk/gtkwidget.h:

libgtk2.gtk_widget_set_size_request.argtypes = (ct.c_void_p, ct.c_int, ct.c_int)
libgtk2.gtk_widget_set_size_request.restype = None
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

# from gtk-2.0/gtk/gtktogglebutton.h:

libgtk2.gtk_toggle_button_set_active.argtypes = (ct.c_void_p, ct.c_bool)
libgtk2.gtk_toggle_button_set_active.restype = None
libgtk2.gtk_toggle_button_get_active.argtypes = (ct.c_void_p,)
libgtk2.gtk_toggle_button_get_active.restype = ct.c_bool

# from gtk-2.0/gtk/gtkcheckbutton.h:

libgtk2.gtk_check_button_new_with_label.argtypes = (ct.c_char_p,)
libgtk2.gtk_check_button_new_with_label.restype = ct.c_void_p

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

# from gtk-2.0/gtk/gtkcelllayout.h:

libgtk2.gtk_cell_layout_pack_start.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_bool)
libgtk2.gtk_cell_layout_pack_start.restype = None
libgtk2.gtk_cell_layout_add_attribute.argtypes = (ct.c_void_p, ct.c_void_p, ct.c_char_p, ct.c_int)
libgtk2.gtk_cell_layout_add_attribute.restype = None

# from gtk-2.0/gtk/gtkcombobox.h:

libgtk2.gtk_combo_box_new_with_model.argtypes = (ct.c_void_p,)
libgtk2.gtk_combo_box_new_with_model.restype = ct.c_void_p
libgtk2.gtk_combo_box_get_active.argtypes = (ct.c_void_p,)
libgtk2.gtk_combo_box_get_active.restype = ct.c_int
libgtk2.gtk_combo_box_set_active.argtypes = (ct.c_void_p, ct.c_int)
libgtk2.gtk_combo_box_set_active.restype = None

# from gtk-2.0/gtk/gtkcellrenderertext.h:

libgtk2.gtk_cell_renderer_text_new.argtypes = ()
libgtk2.gtk_cell_renderer_text_new.restype = ct.c_void_p

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
        gegl.libgobject2.g_signal_connect_data \
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

    def set_alignment(self, xalign, yalign) :
        libgtk2.gtk_misc_set_alignment(self._gtkobj, xalign, yalign)
    #end set_alignment

    def set_padding(self, xpad, ypad) :
        libgtk2.gtk_misc_set_padding(self._gtkobj, xpad, ypad)
    #end set_padding

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

class Checkbox(Widget) :

    __slots__ = ()

    @classmethod
    def create_with_label(celf, label) :
        return \
            celf(libgtk2.gtk_check_button_new_with_label(str_encode(label)))
    #end create

    def set_checked(self, checked) :
        libgtk2.gtk_toggle_button_set_active(self._gtkobj, checked)
    #end set_value

    def get_checked(self) :
        return \
            libgtk2.gtk_toggle_button_get_active(self._gtkobj)
    #end get_checked

#end Checkbox

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
