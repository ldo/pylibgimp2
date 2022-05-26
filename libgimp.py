"""
This module is a wrapper around the Gimp plug-in APIs (libgimp-2.0 etc),
implemented in pure Python using ctypes. It does not depend on any
Python support built into Gimp itself.
"""
#+
# Copyright 2022 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import sys
import enum
import ctypes as ct

class GIMP :
    "useful definitions adapted from files in /usr/include/gimp-2.0/."

    # from libgimpbase/gimpbaseenums.h:

    ChannelOps = ct.c_uint
    # values for ChannelOps:
    CHANNEL_OP_ADD = 0
    CHANNEL_OP_SUBTRACT = 1
    CHANNEL_OP_REPLACE = 2
    CHANNEL_OP_INTERSECT = 3

    MergeType = ct.c_uint
    # values for MergeType:
    EXPAND_AS_NECESSARY = 0
    CLIP_TO_IMAGE = 1
    CLIP_TO_BOTTOM_LAYER = 2
    FLATTEN_IMAGE = 3

    PDBArgType = ct.c_uint
    # values for PDBArgType:
    PDB_INT32 = 0
    PDB_INT16 = 1
    PDB_INT8 = 2
    PDB_FLOAT = 3
    PDB_STRING = 4
    PDB_INT32ARRAY = 5
    PDB_INT16ARRAY = 6
    PDB_INT8ARRAY = 7
    PDB_FLOATARRAY = 8
    PDB_STRINGARRAY = 9
    PDB_COLOUR = 10
    PDB_ITEM = 11
    PDB_DISPLAY = 12
    PDB_IMAGE = 13
    PDB_LAYER = 14
    PDB_CHANNEL = 15
    PDB_DRAWABLE = 16
    PDB_SELECTION = 17
    PDB_COLOURARRAY = 18
    PDB_VECTORS = 19
    PDB_PARASITE = 20
    PDB_STATUS = 21
    PDB_END = 22

    ImageType = ct.c_uint
    # values for ImageType:
    RGB_IMAGE = 0
    RGBA_IMAGE = 1
    GRAY_IMAGE = 2
    GRAYA_IMAGE = 3
    INDEXED_IMAGE = 4
    INDEXEDA_IMAGE = 5

    PDBProcType = ct.c_uint
    # values for PDBProcType:
    INTERNAL = 0
    PLUGIN = 1
    EXTENSION = 2
    TEMPORARY = 3

    PDBStatusType = ct.c_uint
    # values for PDBStatusType:
    PDB_EXECUTION_ERROR = 0
    PDB_CALLING_ERROR = 1
    PDB_PASS_THROUGH = 2
    PDB_SUCCESS = 3
    PDB_CANCEL = 4

    # from libgimpbase/gimpparasite.h:

    class Parasite(ct.Structure) :
        _fields_ = \
            [
                ("name", ct.c_char_p),
                ("flags", ct.c_uint32),
                ("size", ct.c_uint32),
                ("data", ct.c_void_p),
            ]
    #end Parasite

    # from libgimpcolor/gimpcolortypes.h:

    class RGB(ct.Structure) :
        _fields_ = \
            [
                ("r", ct.c_double),
                ("g", ct.c_double),
                ("b", ct.c_double),
                ("a", ct.c_double),
            ]
    #end RGB

    # from libgimp/gimp.h:

    class ParamDef(ct.Structure) :
        pass
    ParamDef._fields_ = \
        [
            ("type", PDBArgType),
            ("name", ct.c_char_p),
            ("description", ct.c_char_p),
        ]
    #end ParamDef

    class ParamRegion(ct.Structure) :
        _fields_ = \
            [
                ("x", ct.c_int32),
                ("y", ct.c_int32),
                ("width", ct.c_int32),
                ("height", ct.c_int32),
            ]
    #end ParamRegion

    class ParamData(ct.Union) :
        pass
    ParamData._fields_ = \
        [
          ("d_int32", ct.c_int32),
          ("d_int16", ct.c_int16),
          ("d_int8", ct.c_uint8),
          ("d_float", ct.c_double),
          ("d_string", ct.c_char_p),
          ("d_int32array", ct.POINTER(ct.c_int32)),
          ("d_int16array", ct.POINTER(ct.c_int16)),
          ("d_int8array", ct.POINTER(ct.c_uint8)),
          ("d_floatarray", ct.POINTER(ct.c_double)),
          ("d_stringarray", ct.POINTER(ct.c_char_p)),
          ("d_colourarray", ct.POINTER(RGB)),
          ("d_colour", RGB),
          # ("d_region", ParamRegion), # use d_item instead
          ("d_display", ct.c_int32),
          ("d_image", ct.c_int32),
          ("d_item", ct.c_int32),
          ("d_layer", ct.c_int32),
          ("d_layer_mask", ct.c_int32), # ?
          ("d_channel", ct.c_int32),
          ("d_drawable", ct.c_int32),
          ("d_selection", ct.c_int32),
          # ("d_boundary", ct.c_int32), # use d_colourarray instead
          # ("d_path", ct.c_int32), # use d_vectors instead
          ("d_vectors", ct.c_int32),
          ("d_unit", ct.c_int32), # ?
          ("d_parasite", Parasite),
          ("d_tattoo", ct.c_int32), # ?
          ("d_status", PDBStatusType),
        ]
    #end ParamData

    class Param(ct.Structure) :

        def __repr__(self) :
            "useful for debugging."
            return \
                "(%s, %s)" % (repr(self.type), repr(self.data))
        #end __repr__

    Param._fields_ = \
        [
            ("type", PDBArgType),
            ("data", ParamData),
        ]
    #end Param

    InitProc = ct.CFUNCTYPE(None)
    QuitProc = ct.CFUNCTYPE(None)
    QueryProc = ct.CFUNCTYPE(None)
    RunProc = ct.CFUNCTYPE \
        (None, ct.c_char_p, ct.c_int, ct.POINTER(Param), ct.POINTER(ct.c_int), ct.POINTER(ct.POINTER(Param)))
        # (name, nparams, params, nreturn_vals, return_vals)
    NO_INIT_PROC = InitProc(0)
    NO_QUIT_PROC = QuitProc(0)

    class PlugInInfo(ct.Structure) :
        pass
    PlugInInfo._fields_ = \
        [
            ("init_proc", InitProc),
            ("quit_proc", QuitProc),
            ("query_proc", QueryProc),
            ("run_proc", RunProc),
        ]
    #end PlugInInfo

    # from libgimp/gimpenums.h:

    HistogramChannel = ct.c_uint
    # values for HistogramChannel:
    HISTOGRAM_VALUE = 0
    HISTOGRAM_RED = 1
    HISTOGRAM_GREEN = 2
    HISTOGRAM_BLUE = 3
    HISTOGRAM_ALPHA = 4
    HISTOGRAM_LUMINANCE = 5

    LayerMode = ct.c_uint
    # values for LayerMode:
    LAYER_MODE_NORMAL_LEGACY = 0
    LAYER_MODE_DISSOLVE = 1
    LAYER_MODE_BEHIND_LEGACY = 2
    LAYER_MODE_MULTIPLY_LEGACY = 3
    LAYER_MODE_SCREEN_LEGACY = 4
    LAYER_MODE_OVERLAY_LEGACY = 5
    LAYER_MODE_DIFFERENCE_LEGACY = 6
    LAYER_MODE_ADDITION_LEGACY = 7
    LAYER_MODE_SUBTRACT_LEGACY = 8
    LAYER_MODE_DARKEN_ONLY_LEGACY = 9
    LAYER_MODE_LIGHTEN_ONLY_LEGACY = 10
    LAYER_MODE_HSV_HUE_LEGACY = 11
    LAYER_MODE_HSV_SATURATION_LEGACY = 12
    LAYER_MODE_HSL_COLOR_LEGACY = 13
    LAYER_MODE_HSV_VALUE_LEGACY = 14
    LAYER_MODE_DIVIDE_LEGACY = 15
    LAYER_MODE_DODGE_LEGACY = 16
    LAYER_MODE_BURN_LEGACY = 17
    LAYER_MODE_HARDLIGHT_LEGACY = 18
    LAYER_MODE_SOFTLIGHT_LEGACY = 19
    LAYER_MODE_GRAIN_EXTRACT_LEGACY = 20
    LAYER_MODE_GRAIN_MERGE_LEGACY = 21
    LAYER_MODE_COLOR_ERASE_LEGACY = 22
    LAYER_MODE_OVERLAY = 23
    LAYER_MODE_LCH_HUE = 24
    LAYER_MODE_LCH_CHROMA = 25
    LAYER_MODE_LCH_COLOR = 26
    LAYER_MODE_LCH_LIGHTNESS = 27
    LAYER_MODE_NORMAL = 28
    LAYER_MODE_BEHIND = 29
    LAYER_MODE_MULTIPLY = 30
    LAYER_MODE_SCREEN = 31
    LAYER_MODE_DIFFERENCE = 32
    LAYER_MODE_ADDITION = 33
    LAYER_MODE_SUBTRACT = 34
    LAYER_MODE_DARKEN_ONLY = 35
    LAYER_MODE_LIGHTEN_ONLY = 36
    LAYER_MODE_HSV_HUE = 37
    LAYER_MODE_HSV_SATURATION = 38
    LAYER_MODE_HSL_COLOR = 39
    LAYER_MODE_HSV_VALUE = 40
    LAYER_MODE_DIVIDE = 41
    LAYER_MODE_DODGE = 42
    LAYER_MODE_BURN = 43
    LAYER_MODE_HARDLIGHT = 44
    LAYER_MODE_SOFTLIGHT = 45
    LAYER_MODE_GRAIN_EXTRACT = 46
    LAYER_MODE_GRAIN_MERGE = 47
    LAYER_MODE_VIVID_LIGHT = 48
    LAYER_MODE_PIN_LIGHT = 49
    LAYER_MODE_LINEAR_LIGHT = 50
    LAYER_MODE_HARD_MIX = 51
    LAYER_MODE_EXCLUSION = 52
    LAYER_MODE_LINEAR_BURN = 53
    LAYER_MODE_LUMA_DARKEN_ONLY = 54
    LAYER_MODE_LUMA_LIGHTEN_ONLY = 55
    LAYER_MODE_LUMINANCE = 56
    LAYER_MODE_COLOR_ERASE = 57
    LAYER_MODE_ERASE = 58
    LAYER_MODE_MERGE = 59
    LAYER_MODE_SPLIT = 60
    LAYER_MODE_PASS_THROUGH = 61

#end GIMP

ident = lambda x : x
str_encode = lambda s : s.encode()
str_decode = lambda s : s.decode()

def def_c_char_p_encode(save_strs) :

    def encode(s) :
        if s != None :
            c = ct.c_char_p(s.encode())
            save_strs.append(c)
        else :
            c = None
        #end if
        return \
            c
    #end encode

#begin def_c_char_p_encode
    return \
        encode
#end def_c_char_p_encode

def seq_to_ct(seq, ct_type, conv = ident, zeroterm = False) :
    "extracts the elements of a Python sequence value into a ctypes array" \
    " of type ct_type, optionally applying the conv function to each value."
    nr_elts = len(seq)
    result = ((nr_elts + int(zeroterm)) * ct_type)()
    for i in range(nr_elts) :
        result[i] = conv(seq[i])
    #end for
    if zeroterm :
        result[nr_elts] = conv(None)
    #end if
    return \
        result
#end seq_to_ct

def ct_to_seq(arr, conv = ident, strip_zeroterm = False) :
    if len(arr) > 0 and strip_zeroterm :
        assert arr[-1] == None
        arr = arr[:-1]
    #end if
    return \
        list(conv(x) for x in arr)
#end ct_to_seq

def def_to_ct_int(nrbits, signed) :

    cttype = \
        (
            { # unsigned
                8 : ct.c_uint8,
                16 : ct.c_uint16,
                32 : ct.c_uint32,
            },
            { # signed
                8 : ct.c_int8,
                16 : ct.c_int16,
                32 : ct.c_int32,
            },
        )[signed][nrbits]

    def conv(val) :
        if (
                not isinstance(val, int)
            or
                val < - (0, 1 << nrbits - 1)[signed]
            or
                val >= 1 << nrbits - int(signed)
        ) :
            raise ValueError \
              (
                    "value %s does not fit in %d %s bits"
                %
                    (repr(val), nrbits, ("unsigned", "signed")[signed])
              )
        #end if
        return \
            cttype(val)
    #end conv

#begin def_to_ct_int
    conv.__name__ = "conv_to_%d_%s" % (nrbits, ("unsigned", "signed")[signed])
    return \
        conv
#end def_to_ct_int

def def_to_ct_enum(maxval) :

    def conv(val) :
        if (
                not isinstance(val, int)
            or
                val < 0
            or
                val > maxval
        ) :
            raise ValueError("value %s must not lie outside 0 .. %d" % (repr(val), maxval))
        #end if
        return \
            val
    #end conv

#begin def_to_ct_enum
    conv.__name__ = "conv_to_enum_%d" % maxval
    return \
        conv
#end def_to_ct_enum

def def_seq_to_ct(ct_type, conv = ident, zeroterm = False) :

    def conv(val) :
        return \
            seq_to_ct(val, ct_type, conv, zeroterm)
    #conv

#begin def_seq_to_ct
    conv.__name__ = "conv_seq_to_%s_array" % ct_type.__name__
    return \
        conv
#end def_seq_to_ct

def def_ct_to_seq(conv, strip_zeroterm = False) :

    def conv(val) :
        return \
            ct_to_seq(val, conv, strip_zeroterm)
    #end conv

#begin def_ct_to_seq
    conv.__name__ = "conv_ct_to_seq"
    return \
        conv
#end def_ct_to_seq

def def_expect_type(expect_type) :

    def conv(val) :
        if not isinstance(val, expect_type) :
            raise TypeError("value %s is not of type %s" % (repr(val), expect_type.__name__))
        #end if
        return \
            val
    #end conv

#begin def_expect_type
    conv.__name__ = "conv_expect_type_%s" % expect_type.__name__
    return \
        conv
#end def_expect_type

class PARAMTYPE(enum.Enum) :

    # (argtype, fieldname, to_ct_conv, from_ct_conv)
    # FIXME: to_ct_conv routines for string pointers will need to stash ctype objects somewhere
    INT32 = (GIMP.PDB_INT32, "d_int32", def_to_ct_int(32, True), ident)
    INT16 = (GIMP.PDB_INT16, "d_int16", def_to_ct_int(16, True), ident)
    INT8 = (GIMP.PDB_INT8, "d_int8", def_to_ct_int(8, False), ident)
    FLOAT = (GIMP.PDB_FLOAT, "d_float", ct.c_double, ident)
    STRING = (GIMP.PDB_STRING, "d_string", str_encode, str_decode)
    INT32ARRAY = (GIMP.PDB_INT32ARRAY, "d_int32array", def_seq_to_ct(ct.c_int32), ct_to_seq)
    INT16ARRAY = (GIMP.PDB_INT16ARRAY, "d_int16array", def_seq_to_ct(ct.c_int16), ct_to_seq)
    INT8ARRAY = (GIMP.PDB_INT8ARRAY, "d_int8array", def_seq_to_ct(ct.c_uint8), ct_to_seq)
    FLOATARRAY = (GIMP.PDB_FLOATARRAY, "d_floatarray", def_seq_to_ct(ct.c_double), ct_to_seq)
    STRINGARRAY = (GIMP.PDB_STRINGARRAY, "d_stringarray", def_seq_to_ct(ct.c_char_p, str_encode), def_ct_to_seq(str_decode))
    COLOURARRAY = (GIMP.PDB_COLOURARRAY, "d_colourarray", def_seq_to_ct(def_expect_type(GIMP.RGB)), ident)
    COLOUR = (GIMP.PDB_COLOUR, "d_colour", def_expect_type(GIMP.RGB), ident)
    DISPLAY = (GIMP.PDB_DISPLAY, "d_display", def_to_ct_int(32, True), ident)
    IMAGE = (GIMP.PDB_IMAGE, "d_image", def_to_ct_int(32, True), ident)
    ITEM = (GIMP.PDB_ITEM, "d_item", def_to_ct_int(32, True), ident)
    LAYER = (GIMP.PDB_LAYER, "d_layer", def_to_ct_int(32, True), ident)
    # no enum for layer_mask?
    CHANNEL = (GIMP.PDB_CHANNEL, "d_channel", def_to_ct_int(32, True), ident)
    DRAWABLE = (GIMP.PDB_DRAWABLE, "d_drawable", def_to_ct_int(32, True), ident)
    SELECTION = (GIMP.PDB_SELECTION, "d_selection", def_to_ct_int(32, True), ident)
    VECTORS = (GIMP.PDB_VECTORS, "d_vectors", def_to_ct_int(32, True), ident)
    # no enum for d_unit?
    PARASITE = (GIMP.PDB_PARASITE, "d_parasite", def_expect_type(GIMP.Parasite), ident)
    # no enum for d_tattoo?
    STATUS = (GIMP.PDB_STATUS, "d_status", def_to_ct_enum(GIMP.PDB_CANCEL), ident)

    @property
    def code(self) :
        return \
            self.value[0]
    #end code

    @property
    def fieldname(self) :
        return \
            self.value[1]
    #end fieldname

    @property
    def to_ct_conv(self) :
        return \
            self.value[2]
    #end to_ct_conv

    @property
    def from_ct_conv(self) :
        return \
            self.value[3]
    #end from_ct_conv

    def __repr__(self) :
        return \
            "%s.%s" % (type(self).__name__, self.name)
    #end __repr__

#end PARAMTYPE
PARAMTYPE.from_code = dict((t.code, t) for t in PARAMTYPE)
# deprecated aliases:
PARAMTYPE.PATH = PARAMTYPE.VECTORS
PARAMTYPE.BOUNDARY = PARAMTYPE.COLOURARRAY
PARAMTYPE.REGION = PARAMTYPE.ITEM

def to_param_def(paramdef, save_strs) :
    c_type = paramdef["type"]
    if isinstance(c_type, PARAMTYPE) :
        c_type = c_type.code
    #end if
    c_name = ct.c_char_p(paramdef["name"].encode())
    c_descr = ct.c_char_p(paramdef["description"].encode())
    save_strs.extend((c_name, c_descr))
    return \
        GIMP.ParamDef \
          (
            type = c_type,
            name = c_name,
            description = c_descr,
          )
#end to_param_def

def param_to_ct(type, val) :
    if not isinstance(type, PARAMTYPE) :
        raise TypeError("type is not a PARAMTYPE")
    #end if
    paramdata = GIMP.ParamData()
    setattr(paramdata, type.fieldname, type.to_ct_conv(val))
    return \
        GIMP.Param(type = type.code, data = paramdata)
#end param_to_ct

def param_from_ct(param) :
    type = PARAMTYPE.from_code[param.type]
    return \
        type.from_ct_conv(getattr(param.data, type.fieldname))
#end param_from_ct

#+
# Routine arg/result types
#-

libgimp2 = ct.cdll.LoadLibrary("libgimp-2.0.so.0")

# from libgimp/gimp.h:

libgimp2.gimp_main.argtypes = (ct.POINTER(GIMP.PlugInInfo), ct.c_int, ct.POINTER(ct.c_char_p))
libgimp2.gimp_main.restype = ct.c_int
libgimp2.gimp_quit.argtypes = ()
libgimp2.gimp_quit.restype = None
libgimp2.gimp_install_procedure.argtypes = (ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, GIMP.PDBProcType, ct.c_int, ct.c_int, ct.POINTER(GIMP.ParamDef), ct.POINTER(GIMP.ParamDef))
libgimp2.gimp_install_procedure.restype = None
# libgimp2.gimp_run_procedure needs varargs, which ctypes doesn’t handle,
# luckily we can use gimp_run_procedure2 instead
libgimp2.gimp_run_procedure2.argtypes = (ct.c_char_p, ct.POINTER(ct.c_int), ct.c_int, ct.POINTER(GIMP.Param))
libgimp2.gimp_run_procedure2.restype = ct.POINTER(GIMP.Param)
libgimp2.gimp_destroy_params.argtypes = (ct.POINTER(GIMP.Param), ct.c_int)
libgimp2.gimp_destroy_params.restype = None
libgimp2.gimp_destroy_paramdefs.argtypes = (ct.POINTER(GIMP.ParamDef), ct.c_int)
libgimp2.gimp_destroy_paramdefs.restype = None

# from libgimp/gimpdisplay_pdb.h:

libgimp2.gimp_displays_flush.argtypes = ()
libgimp2.gimp_displays_flush.restype = None

# from libgimp/gimpproceduraldb.h:

libgimp2.gimp_procedural_db_proc_info.argtypes = (ct.c_char_p, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(GIMP.PDBProcType), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.POINTER(GIMP.ParamDef)), ct.POINTER(ct.POINTER(GIMP.ParamDef)))
libgimp2.gimp_procedural_db_proc_info.restype = ct.c_bool

# from libgimp/gimpselection_pdb.h:

libgimp2.gimp_selection_all.argtypes = (ct.c_int32,)
libgimp2.gimp_selection_all.restype = ct.c_bool
libgimp2.gimp_selection_none.argtypes = (ct.c_int32,)
libgimp2.gimp_selection_none.restype = ct.c_bool

# from libgimp/gimpselectiontools_pdb.h:

libgimp2.gimp_rect_select.argtypes = (ct.c_int32, ct.c_double, ct.c_double, ct.c_double, ct.c_double, GIMP.ChannelOps, ct.c_bool, ct.c_double)
libgimp2.gimp_rect_select.restype = ct.c_bool

# from libgimp/gimplayer.h:

libgimp2.gimp_layer_new.argtypes = (ct.c_int32, ct.c_char_p, ct.c_int, ct.c_int, GIMP.ImageType, ct.c_double, GIMP.LayerMode)
libgimp2.gimp_layer_new.restype = ct.c_int32
libgimp2.gimp_layer_copy.restypes = (ct.c_int32,)
libgimp2.gimp_layer_copy.restype = ct.c_int32

# from libgimp/gimpplugin_pdb.h:

libgimp2.gimp_plugin_menu_register.argtypes = (ct.c_char_p, ct.c_char_p)
libgimp2.gimp_plugin_menu_register.restype = ct.c_bool

# from libgimp/gimpimage_pdb.h:

libgimp2.gimp_image_add_layer.argtypes = (ct.c_int32, ct.c_int32, ct.c_int)
libgimp2.gimp_image_add_layer.restype = ct.c_bool
libgimp2.gimp_image_merge_down.argtypes = (ct.c_int32, ct.c_int32, GIMP.MergeType)
libgimp2.gimp_image_merge_down.restype = ct.c_int32
libgimp2.gimp_image_get_active_layer.argtypes = (ct.c_int32,)
libgimp2.gimp_image_get_active_layer.restype = ct.c_int32

# from libgimp/gimplayer_pdb.h:

libgimp2.gimp_layer_set_opacity.argtypes = (ct.c_int32, ct.c_double)
libgimp2.gimp_layer_set_opacity.restype = ct.c_bool
libgimp2.gimp_layer_set_mode.argtypes = (ct.c_int32, GIMP.LayerMode)
libgimp2.gimp_layer_set_mode.restype = ct.c_bool

# from libgimp/libgimp/gimpimageundo_pdb.h:

libgimp2.gimp_image_undo_group_start.argtypes = (ct.c_int32,)
libgimp2.gimp_image_undo_group_start.restype = ct.c_bool
libgimp2.gimp_image_undo_group_end.argtypes = (ct.c_int32,)
libgimp2.gimp_image_undo_group_end.restype = ct.c_bool

# from libgimp/gimpdrawablecolor_pdb.h:

libgimp2.gimp_drawable_levels.argtypes = (ct.c_int32, GIMP.HistogramChannel, ct.c_double, ct.c_double, ct.c_bool, ct.c_double, ct.c_double, ct.c_double, ct.c_bool)
libgimp2.gimp_drawable_levels.restype = ct.c_bool

#+
# Higher-level stuff follows
#-

def procedural_db_proc_info(procname : str) :
    "returns information about the specified procedure registered with the PDB," \
    " if any, or None if no such procedure was found."
    c_procname = str_encode(procname)
    c_blurb = ct.c_char_p()
    c_help = ct.c_char_p()
    c_author = ct.c_char_p()
    c_copyright = ct.c_char_p()
    c_date = ct.c_char_p()
    c_proc_type = GIMP.PDBProcType()
    c_num_args = ct.c_int()
    c_num_values = ct.c_int()
    c_args = ct.POINTER(GIMP.ParamDef)()
    c_return_vals = ct.POINTER(GIMP.ParamDef)()
    success = libgimp2.gimp_procedural_db_proc_info(c_procname, ct.byref(c_blurb), ct.byref(c_help), ct.byref(c_author), ct.byref(c_copyright), ct.byref(c_date), ct.byref(c_proc_type), ct.byref(c_num_args), ct.byref(c_num_values), ct.byref(c_args), ct.byref(c_return_vals))
    if success :
        result = \
            {
                "blurb" : str_decode(c_blurb.value),
                "help" : str_decode(c_help.value),
                "author" : str_decode(c_author.value),
                "copyright" : str_decode(c_copyright.value),
                "date" : str_decode(c_date.value),
                "proc_type" : c_proc_type.value,
            }
        for keyword, nr_items, c_items in \
            (
                ("args", c_num_args.value, c_args),
                ("return_vals", c_num_values.value, c_return_vals),
            ) \
        :
            result[keyword] = \
                list \
                  (
                    {
                        "type" : PARAMTYPE.from_code[c_item.type],
                        "name" : str_decode(c_item.name),
                        "description" : str_decode(c_item.description),
                    }
                    for c_item in c_items[:nr_items]
                  )
        #end for
        libgimp2.gimp_destroy_paramdefs(c_args, c_num_args.value)
        libgimp2.gimp_destroy_paramdefs(c_return_vals, c_num_values.value)
    else :
        result = None
    #end if
    return \
        result
#end procedural_db_proc_info

def displays_flush() :
    libgimp2.gimp_displays_flush()
#end displays_flush

def wrap_run_proc(run_proc) :
    "creates a wrapper around the given Python function, which" \
    " should be written somewhat as follows:\n" \
    "\n" \
    "    def run_proc(name, params) :\n" \
    "        ...\n" \
    "        return return_vals\n" \
    "    #end run_proc\n"

    last_return = None
      # to save constructed objects in-between invocations (not re-entrant)

    def run_wrapper(c_name, nparams, c_params, nreturn_vals, c_return_vals) :
        nonlocal last_return
        name = str_decode(c_name)
        params = ct_to_seq(c_params[:nparams], param_from_ct)
        return_vals = run_proc(name, params)
        last_return = seq_to_ct(return_vals, GIMP.Param, lambda v : param_to_ct(v[0], v[1]))
        nreturn_vals[0] = len(return_vals)
        c_return_vals[0] = last_return
    #end run_wrapper

#begin wrap_run_proc
    run_wrapper.__name__ = "wrap_%s" % run_proc.__name__
    return \
        GIMP.RunProc(run_wrapper)
#end wrap_run_proc

def install_procedure(name : str, blurb : str, help: str, author : str, copyright : str, date : str, menu_label : str, image_types : str, type : GIMP.PDBProcType, params, return_vals) :
    "installs a procedure in the procedure database. params and return_vals must be sequences" \
    " of dicts each with type, name and description fields."
    c_name = name.encode()
    c_blurb = blurb.encode()
    c_help = help.encode()
    c_author = author.encode()
    c_copyright = copyright.encode()
    c_date = date.encode()
    c_menu_label = menu_label.encode()
    c_image_types = image_types.encode()
    save_strs = []
    if params != None :
        c_params = seq_to_ct(params, GIMP.ParamDef, lambda v : to_param_def(v, save_strs))
        nr_params = len(params)
    else :
        c_params = None
        nr_params = 0
    #end if
    if return_vals != None :
        c_return_vals = seq_to_ct(return_vals, GIMP.ParamDef, lambda v : to_param_def(v, save_strs))
        nr_return_vals = len(return_vals)
    else :
        c_return_vals = None
        nr_return_vals = 0
    #end if
    libgimp2.gimp_install_procedure(c_name, c_blurb, c_help, c_author, c_copyright, c_date, c_menu_label, c_image_types, type, nr_params, nr_return_vals, c_params, c_return_vals)
#end install_procedure

def plugin_menu_register(procname, menu_item_name) :
    c_procname = str_encode(procname)
    c_menu_item_name = str_encode(menu_item_name)
    return \
        libgimp2.gimp_plugin_menu_register(c_procname, c_menu_item_name)
#end plugin_menu_register

def main(plugin_info : GIMP.PlugInInfo) :
    "to be invoked as your plugin mainline."
    save_strs = []
    argv = seq_to_ct \
      (
        seq = sys.argv,
        ct_type = ct.c_char_p,
        conv = def_c_char_p_encode(save_strs),
        zeroterm = True
      )
    status = libgimp2.gimp_main(ct.byref(plugin_info), len(argv) - 1, argv)
    sys.exit(status)
#end main
