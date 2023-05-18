"""
This module is a wrapper around the GIMP plug-in APIs (libgimp-2.0 etc),
implemented in pure Python using ctypes. It does not depend on any
Python support built into GIMP itself, but it does need my GEGL
and BABL wrappers, obtainable from <https://gitlab.com/ldo/gabler>
or <https://github.com/ldo/gabler>.
"""
#+
# Copyright 2022-2023 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
# Licensed under the GNU Lesser General Public License v2.1 or later.
#-

import sys
import os
import enum
import ctypes as ct
from weakref import \
    WeakValueDictionary
import colorsys

import gegl
from gegl import \
    GType, \
    GValue, \
    GCallback, \
    ident, \
    str_encode, \
    str_encode_optional, \
    str_decode
import libgimpgtk2
from libgimpgtk2 import \
    GTK, \
    Widget

class Structure(ct.Structure) :

    def __repr__(self) :
        celf = type(self)
        return \
            (
                    "%s(%s)"
                %
                    (
                        celf.__name__,
                        ", ".join
                          (
                                "%s = %s"
                            %
                                (f[0], repr(getattr(self, f[0])))
                            for f in celf._fields_
                          ),
                    )
            )
    #end __repr__

#end Structure

class GIMP :
    "useful definitions adapted from files in /usr/include/gimp-2.0/."

    # from libgimpbase/gimpbaseenums.h:

    AddMaskType = ct.c_uint
    # values for AddMaskType:
    ADD_MASK_WHITE = 0
    ADD_MASK_BLACK = 1
    ADD_MASK_ALPHA = 2
    ADD_MASK_ALPHA_TRANSFER = 3
    ADD_MASK_SELECTION = 4
    ADD_MASK_COPY = 5
    ADD_MASK_CHANNEL = 6
    # deprecated:
    ADD_WHITE_MASK = ADD_MASK_WHITE
    ADD_BLACK_MASK = ADD_MASK_BLACK
    ADD_ALPHA_MASK = ADD_MASK_ALPHA
    ADD_ALPHA_TRANSFER_MASK = ADD_MASK_ALPHA_TRANSFER
    ADD_SELECTION_MASK = ADD_MASK_SELECTION
    ADD_COPY_MASK = ADD_MASK_COPY
    ADD_CHANNEL_MASK = ADD_MASK_CHANNEL

    BlendMode = ct.c_uint
    # values for BlendMode:
    BLEND_FG_BG_RGB = 0
    BLEND_FG_BG_HSV = 1
    BLEND_FG_TRANSPARENT = 2
    BLEND_CUSTOM = 3
    # deprecated:
    FG_BG_RGB_MODE = BLEND_FG_BG_RGB
    FG_BG_HSV_MODE = BLEND_FG_BG_HSV
    FG_TRANSPARENT_MODE = BLEND_FG_TRANSPARENT
    CUSTOM_MODE = BLEND_CUSTOM

    BrushGeneratedShape = ct.c_uint
    # values for BrushGeneratedShape:
    BRUSH_GENERATED_CIRCLE = 0
    BRUSH_GENERATED_SQUARE = 1
    BRUSH_GENERATED_DIAMOND = 2

    BucketFillMode = ct.c_uint
    # values for BucketFillMode:
    BUCKET_FILL_FG = 0
    BUCKET_FILL_BG = 1
    BUCKET_FILL_PATTERN = 2
    # deprecated:
    FG_BUCKET_FILL = BUCKET_FILL_FG
    BG_BUCKET_FILL = BUCKET_FILL_BG
    PATTERN_BUCKET_FILL = BUCKET_FILL_PATTERN

    CapStyle = ct.c_uint
    # values for CapStyle:
    CAP_BUTT = 0
    CAP_ROUND = 1
    CAP_SQUARE = 2

    ChannelOps = ct.c_uint
    # values for ChannelOps:
    CHANNEL_OP_ADD = 0
    CHANNEL_OP_SUBTRACT = 1
    CHANNEL_OP_REPLACE = 2
    CHANNEL_OP_INTERSECT = 3

    ChannelType = ct.c_uint
    # values for ChannelType:
    CHANNEL_RED = 0
    CHANNEL_GREEN = 1
    CHANNEL_BLUE = 2
    CHANNEL_GRAY = 3
    CHANNEL_INDEXED = 4
    CHANNEL_ALPHA = 5
    # deprecated:
    RED_CHANNEL = CHANNEL_RED
    GREEN_CHANNEL = CHANNEL_GREEN
    BLUE_CHANNEL = CHANNEL_BLUE
    GRAY_CHANNEL = CHANNEL_GRAY
    INDEXED_CHANNEL = CHANNEL_INDEXED
    ALPHA_CHANNEL = CHANNEL_ALPHA

    CheckSize = ct.c_uint
    # values for CheckSize:
    CHECK_SIZE_SMALL_CHECKS = 0
    CHECK_SIZE_MEDIUM_CHECKS = 1
    CHECK_SIZE_LARGE_CHECKS = 2

    CheckType = ct.c_uint
    # values for CheckType:
    CHECK_TYPE_LIGHT_CHECKS = 0
    CHECK_TYPE_GRAY_CHECKS = 1
    CHECK_TYPE_DARK_CHECKS = 2
    CHECK_TYPE_WHITE_ONLY = 3
    CHECK_TYPE_GRAY_ONLY = 4
    CHECK_TYPE_BLACK_ONLY = 5

    CloneType = ct.c_uint
    # values for CloneType:
    CLONE_IMAGE = 0
    CLONE_PATTERN = 1
    # deprecated:
    IMAGE_CLONE = CLONE_IMAGE
    PATTERN_CLONE = CLONE_PATTERN

    ColourTag = ct.c_uint
    # values for ColourTag:
    COLOUR_TAG_NONE = 0
    COLOUR_TAG_BLUE = 1
    COLOUR_TAG_GREEN = 2
    COLOUR_TAG_YELLOW = 3
    COLOUR_TAG_ORANGE = 4
    COLOUR_TAG_BROWN = 5
    COLOUR_TAG_RED = 6
    COLOUR_TAG_VIOLET = 7
    COLOUR_TAG_GRAY = 8

    ComponentType = ct.c_uint
    # values for ComponentType:
    COMPONENT_TYPE_U8 = 100
    COMPONENT_TYPE_U16 = 200
    COMPONENT_TYPE_U32 = 300
    COMPONENT_TYPE_HALF = 500
    COMPONENT_TYPE_FLOAT = 600
    COMPONENT_TYPE_DOUBLE = 700

    ConvertPaletteType = ct.c_uint
    # values for ConvertPaletteType:
    CONVERT_PALETTE_GENERATE = 0
    CONVERT_PALETTE_REUSE = 1
    CONVERT_PALETTE_WEB = 2
    CONVERT_PALETTE_MONO = 3
    CONVERT_PALETTE_CUSTOM = 4
    # deprecated:
    MAKE_PALETTE = CONVERT_PALETTE_GENERATE
    REUSE_PALETTE = CONVERT_PALETTE_REUSE
    WEB_PALETTE = CONVERT_PALETTE_WEB
    MONO_PALETTE = CONVERT_PALETTE_MONO
    CUSTOM_PALETTE = CONVERT_PALETTE_CUSTOM

    ConvolveType = ct.c_uint
    # values for ConvolveType:
    CONVOLVE_BLUR = 0
    CONVOLVE_SHARPEN = 1
    # deprecated:
    BLUR_CONVOLVE = CONVOLVE_BLUR
    SHARPEN_CONVOLVE = CONVOLVE_SHARPEN

    DesaturateMode = ct.c_uint
    # values for DesaturateMode:
    DESATURATE_LIGHTNESS = 0
    DESATURATE_LUMA = 1
    DESATURATE_AVERAGE = 2
    DESATURATE_LUMINANCE = 3
    DESATURATE_VALUE = 4
    # deprecated:
    DESATURATE_LUMINOSITY = DESATURATE_LUMA

    DodgeBurnType = ct.c_uint
    # values for DodgeBurnType
    DODGE_BURN_TYPE_DODGE = 0
    DODGE_BURN_TYPE_BURN = 1
    # deprecated:
    DODGE = DODGE_BURN_TYPE_DODGE
    BURN = DODGE_BURN_TYPE_BURN

    FillType = ct.c_uint
    # values for FillType:
    FILL_FOREGROUND = 0
    FILL_BACKGROUND = 1
    FILL_WHITE = 2
    FILL_TRANSPARENT = 3
    FILL_PATTERN = 4
    # deprecated synonyms for above:
    FOREGROUND_FILL = FILL_FOREGROUND
    BACKGROUND_FILL = FILL_BACKGROUND
    WHITE_FILL = FILL_WHITE
    TRANSPARENT_FILL = FILL_TRANSPARENT
    PATTERN_FILL = FILL_PATTERN

    ForegroundExtractMode = ct.c_uint
    # values for ForegroundExtractMode:
    FOREGROUND_EXTRACT_SIOX = 0
    FOREGROUND_EXTRACT_MATTING = 1

    GradientBlendColourSpace = ct.c_uint
    # values for GradientBlendColourSpace:
    GRADIENT_BLEND_RGB_PERCEPTUAL = 0
    GRADIENT_BLEND_RGB_LINEAR = 1
    GRADIENT_BLEND_CIE_LAB = 2

    GradientSegmentColour = ct.c_uint
    # values for GradientSegmentColour:
    GRADIENT_SEGMENT_RGB = 0
    GRADIENT_SEGMENT_HSV_CCW = 1
    GRADIENT_SEGMENT_HSV_CW = 2

    GradientSegmentType = ct.c_uint
    # values for GradientSegmentType:
    GRADIENT_SEGMENT_LINEAR = 0
    GRADIENT_SEGMENT_CURVED = 1
    GRADIENT_SEGMENT_SINE = 2
    GRADIENT_SEGMENT_SPHERE_INCREASING = 3
    GRADIENT_SEGMENT_SPHERE_DECREASING = 4
    GRADIENT_SEGMENT_STEP = 5

    GradientType = ct.c_uint
    # values for GradientType:
    GRADIENT_LINEAR = 0
    GRADIENT_BILINEAR = 1
    GRADIENT_RADIAL = 2
    GRADIENT_SQUARE = 3
    GRADIENT_CONICAL_SYMMETRIC = 4
    GRADIENT_CONICAL_ASYMMETRIC = 5
    GRADIENT_SHAPEBURST_ANGULAR = 6
    GRADIENT_SHAPEBURST_SPHERICAL = 7
    GRADIENT_SHAPEBURST_DIMPLED = 8
    GRADIENT_SPIRAL_CLOCKWISE = 9
    GRADIENT_SPIRAL_ANTICLOCKWISE = 10

    GridStyle = ct.c_uint
    # values for GridStyle:
    GRID_DOTS = 0
    GRID_INTERSECTIONS = 1
    GRID_ON_OFF_DASH = 2
    GRID_DOUBLE_DASH = 3
    GRID_SOLID = 4

    HueRange = ct.c_uint
    # values for HueRange:
    HUE_RANGE_ALL = 0
    HUE_RANGE_RED = 1
    HUE_RANGE_YELLOW = 2
    HUE_RANGE_GREEN = 3
    HUE_RANGE_CYAN = 4
    HUE_RANGE_BLUE = 5
    HUE_RANGE_MAGENTA = 6
    # deprecated:
    ALL_HUES = HUE_RANGE_ALL
    RED_HUES = HUE_RANGE_RED
    YELLOW_HUES = HUE_RANGE_YELLOW
    GREEN_HUES = HUE_RANGE_GREEN
    CYAN_HUES = HUE_RANGE_CYAN
    BLUE_HUES = HUE_RANGE_BLUE
    MAGENTA_HUES = HUE_RANGE_MAGENTA

    IconType = ct.c_uint
    # values for IconType:
    ICON_TYPE_ICON_NAME = 0
    ICON_TYPE_INLINE_PIXBUF = 1
    ICON_TYPE_IMAGE_FILE = 2
    ICON_TYPE_STOCK_ID = ICON_TYPE_ICON_NAME

    ImageBaseType = ct.c_uint
    # values for ImageBaseType:
    RGB = 0
    GRAY = 1
    INDEXED = 2

    ImageType = ct.c_uint
    # values for ImageType:
    RGB_IMAGE = 0
    RGBA_IMAGE = 1
    GRAY_IMAGE = 2
    GRAYA_IMAGE = 3
    INDEXED_IMAGE = 4
    INDEXEDA_IMAGE = 5

    InkBlobType = ct.c_uint
    # values for InkBlobType:
    INK_BLOB_TYPE_CIRCLE = 0
    INK_BLOB_TYPE_SQUARE = 1
    INK_BLOB_TYPE_DIAMOND = 2

    InterpolationType = ct.c_uint
    # values for InterpolationType:
    INTERPOLATION_NONE = 0
    INTERPOLATION_LINEAR = 1
    INTERPOLATION_CUBIC = 2
    INTERPOLATION_NOHALO = 3
    INTERPOLATION_LOHALO = 4
    # deprecated:
    INTERPOLATION_LANCZOS = INTERPOLATION_NOHALO

    JoinStyle = ct.c_uint
    # values for JoinStyle:
    JOIN_MITER = 0
    JOIN_ROUND = 1
    JOIN_BEVEL = 2

    MaskApplyMode = ct.c_uint
    # values for MaskApplyMode:
    MASK_APPLY = 0
    MASK_DISCARD = 1

    MergeType = ct.c_uint
    # values for MergeType:
    EXPAND_AS_NECESSARY = 0
    CLIP_TO_IMAGE = 1
    CLIP_TO_BOTTOM_LAYER = 2
    FLATTEN_IMAGE = 3

    MessageHandlerType = ct.c_uint
    # values for MessageHandlerType:
    MESSAGE_BOX = 0
    CONSOLE = 1
    ERROR_CONSOLE = 2

    OffsetType = ct.c_uint
    # values for OffsetType:
    OFFSET_BACKGROUND = 0
    OFFSET_TRANSPARENT = 1
    OFFSET_WRAP_AROUND = 2

    OrientationType = ct.c_uint
    # values for OrientationType:
    ORIENTATION_HORIZONTAL = 0
    ORIENTATION_VERTICAL = 1
    ORIENTATION_UNKNOWN = 2

    PaintApplicationMode = ct.c_uint
    # values for PaintApplicationMode:
    PAINT_CONSTANT = 0
    PAINT_INCREMENTAL = 1

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

    PDBErrorHandler = ct.c_uint
    # values for PDBErrorHandler:
    PDB_ERROR_HANDLER_INTERNAL = 0
    PDB_ERROR_HANDLER_PLUGIN = 1

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

    Precision = ct.c_uint
    # values for Precision:
    PRECISION_U8_LINEAR = 100
    PRECISION_U8_GAMMA = 150
    PRECISION_U16_LINEAR = 200
    PRECISION_U16_GAMMA = 250
    PRECISION_U32_LINEAR = 300
    PRECISION_U32_GAMMA = 350
    PRECISION_HALF_LINEAR = 500
    PRECISION_HALF_GAMMA = 550
    PRECISION_FLOAT_LINEAR = 600
    PRECISION_FLOAT_GAMMA = 650
    PRECISION_DOUBLE_LINEAR = 700
    PRECISION_DOUBLE_GAMMA = 750

    ProgressCommand = ct.c_uint
    # values for ProgressCommand:
    PROGRESS_COMMAND_START = 0
    PROGRESS_COMMAND_END = 1
    PROGRESS_COMMAND_SET_TEXT = 2
    PROGRESS_COMMAND_SET_VALUE = 3
    PROGRESS_COMMAND_PULSE = 4
    PROGRESS_COMMAND_GET_WINDOW = 5

    RepeatMode = ct.c_uint
    # values for RepeatMode:
    REPEAT_NONE = 0
    REPEAT_SAWTOOTH = 1
    REPEAT_TRIANGULAR = 2
    REPEAT_TRUNCATE = 3

    RotationType = ct.c_uint
    # values for RotationType:
    ROTATE_90 = 0
    ROTATE_180 = 1
    ROTATE_270 = 2

    RunMode = ct.c_uint # first argument to every plugin.
    # values for RunMode:
    RUN_INTERACTIVE = 0
    RUN_NONINTERACTIVE = 1
    RUN_WITH_LAST_VALS = 2

    SelectCriterion = ct.c_uint
    # values for SelectCriterion:
    SELECT_CRITERION_COMPOSITE = 0
    SELECT_CRITERION_R = 1
    SELECT_CRITERION_G = 2
    SELECT_CRITERION_B = 3
    SELECT_CRITERION_H = 4
    SELECT_CRITERION_S = 5
    SELECT_CRITERION_V = 6
    SELECT_CRITERION_A = 7
    SELECT_CRITERION_LCH_L = 8
    SELECT_CRITERION_LCH_C = 9
    SELECT_CRITERION_LCH_H = 10

    SizeType = ct.c_uint
    # values for SizeType:
    PIXELS = 0
    POINTS = 1

    StackTraceMode = ct.c_uint
    # values for StackTraceMode:
    STACK_TRACE_NEVER = 0
    STACK_TRACE_QUERY = 1
    STACK_TRACE_ALWAYS = 2

    StrokeMethod = ct.c_uint
    # values for StrokeMethod:
    STROKE_LINE = 0
    STROKE_PAINT_METHOD = 1

    TextDirection = ct.c_uint
    # values for TextDirection:
    TEXT_DIRECTION_LTR = 0
    TEXT_DIRECTION_RTL = 1
    TEXT_DIRECTION_TTB_RTL = 2
    TEXT_DIRECTION_TTB_RTL_UPRIGHT = 3
    TEXT_DIRECTION_TTB_LTR = 4
    TEXT_DIRECTION_TTB_LTR_UPRIGHT = 5

    TextHintStyle = ct.c_uint
    # values for TextHintStyle:
    TEXT_HINT_STYLE_NONE = 0
    TEXT_HINT_STYLE_SLIGHT = 1
    TEXT_HINT_STYLE_MEDIUM = 2
    TEXT_HINT_STYLE_FULL = 3

    TextJustification = ct.c_uint
    # values for TextJustification:
    TEXT_JUSTIFY_LEFT = 0
    TEXT_JUSTIFY_RIGHT = 1
    TEXT_JUSTIFY_CENTER = 2
    TEXT_JUSTIFY_FILL = 3

    TransferMode = ct.c_uint
    # values for TransferMode:
    TRANSFER_SHADOWS = 0
    TRANSFER_MIDTONES = 1
    TRANSFER_HIGHLIGHTS = 2
    # deprecated:
    SHADOWS = TRANSFER_SHADOWS
    MIDTONES = TRANSFER_MIDTONES
    HIGHLIGHTS = TRANSFER_HIGHLIGHTS

    TransformDirection = ct.c_uint
    # values for TransformDirection:
    TRANSFORM_FORWARD = 0
    TRANSFORM_BACKWARD = 1

    TransformResize = ct.c_uint
    # values for TransformResize:
    TRANSFORM_RESIZE_ADJUST = 0
    TRANSFORM_RESIZE_CLIP = 1
    TRANSFORM_RESIZE_CROP = 2
    TRANSFORM_RESIZE_CROP_WITH_ASPECT = 3

    Unit = ct.c_uint
    # values for Unit:
    UNIT_PIXEL = 0
    UNIT_INCH = 1
    UNIT_MM = 2
    UNIT_POINT = 3
    UNIT_PICA = 4
    UNIT_END = 5
    UNIT_PERCENT = 65536

    # from libgimpbase/gimpparasite.h:

    class Parasite(Structure) :
        _fields_ = \
            [
                ("name", ct.c_char_p),
                ("flags", ct.c_uint32),
                ("size", ct.c_uint32),
                ("data", ct.c_void_p),
            ]
    #end Parasite

    # from libgimpcolor/gimpcolortypes.h:

    class RGB(Structure) :
        _fields_ = \
            [
                ("r", ct.c_double),
                ("g", ct.c_double),
                ("b", ct.c_double),
                ("a", ct.c_double),
            ]
    #end RGB

    class HSV(Structure) :
        _fields_ = \
            [
                ("h", ct.c_double),
                ("s", ct.c_double),
                ("v", ct.c_double),
                ("a", ct.c_double),
            ]
    #end HSV

    class HSL(Structure) :
        _fields_ = \
            [
                ("h", ct.c_double),
                ("s", ct.c_double),
                ("l", ct.c_double),
                ("a", ct.c_double),
            ]
    #end HSL

    class CMYK(Structure) :
        _fields_ = \
            [
                ("c", ct.c_double),
                ("m", ct.c_double),
                ("y", ct.c_double),
                ("k", ct.c_double),
                ("a", ct.c_double),
            ]
    #end CMYK

    RenderFunc = ct.CFUNCTYPE(None, ct.c_double, ct.c_double, ct.POINTER(RGB), ct.c_void_p)
    PutPixelFunc = ct.CFUNCTYPE(None, ct.c_int, ct.c_int, ct.POINTER(RGB), ct.c_void_p)
    ProgressFunc = ct.CFUNCTYPE(None, ct.c_int, ct.c_int, ct.c_int, ct.c_void_p)

    # from libgimp/gimp.h:

    class ParamDef(Structure) :
        pass
    ParamDef._fields_ = \
        [
            ("type", PDBArgType),
            ("name", ct.c_char_p),
            ("description", ct.c_char_p),
        ]
    #end ParamDef

    class ParamRegion(Structure) :
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

    class Param(Structure) :

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
        # (name, nparams, params, nreturns, returns)
    NO_INIT_PROC = InitProc(0)
    NO_QUIT_PROC = QuitProc(0)
    NO_QUERY_PROC = QueryProc(0)
    NO_RUN_PROC = RunProc(0)

    class PlugInInfo(Structure) :
        pass
    PlugInInfo._fields_ = \
        [
            ("init_proc", InitProc),
            ("quit_proc", QuitProc),
            ("query_proc", QueryProc),
            ("run_proc", RunProc),
        ]
    #end PlugInInfo

    # from libgimpconfig/gimpconfigenums.h:

    ColourManagementMode = ct.c_uint
    # values for ColourManagementMode:
    COLOUR_MANAGEMENT_OFF = 0
    COLOUR_MANAGEMENT_DISPLAY = 1
    COLOUR_MANAGEMENT_SOFTPROOF = 2

    ColourRenderingIntent = ct.c_uint
    # values for ColourRenderingIntent:
    COLOUR_RENDERING_INTENT_PERCEPTUAL = 0
    COLOUR_RENDERING_INTENT_RELATIVE_COLOURIMETRIC = 1
    COLOUR_RENDERING_INTENT_SATURATION = 2
    COLOUR_RENDERING_INTENT_ABSOLUTE_COLOURIMETRIC = 3

    # from libgimp/gimpenums.h:

    BrushApplicationMode = ct.c_uint
    # values for BrushApplicationMode:
    BRUSH_HARD = 0
    BRUSH_SOFT = 1

    ConvertDitherType = ct.c_uint
    # values for ConvertDitherType:
    CONVERT_DITHER_NONE = 0
    CONVERT_DITHER_FS = 1
    CONVERT_DITHER_FS_LOWBLEED = 2
    CONVERT_DITHER_FIXED = 3

    HistogramChannel = ct.c_uint
    # values for HistogramChannel:
    HISTOGRAM_VALUE = 0
    HISTOGRAM_RED = 1
    HISTOGRAM_GREEN = 2
    HISTOGRAM_BLUE = 3
    HISTOGRAM_ALPHA = 4
    HISTOGRAM_LUMINANCE = 5

    LayerColourSpace = ct.c_uint
    # values for LayerColourSpace:
    LAYER_COLOUR_SPACE_AUTO = 0
    LAYER_COLOUR_SPACE_RGB_LINEAR = 1
    LAYER_COLOUR_SPACE_RGB_PERCEPTUAL = 2

    LayerCompositeMode = ct.c_uint
    # values for LayerCompositeMode:
    LAYER_COMPOSITE_AUTO = 0
    LAYER_COMPOSITE_UNION = 1
    LAYER_COMPOSITE_CLIP_TO_BACKDROP = 2
    LAYER_COMPOSITE_CLIP_TO_LAYER = 3
    LAYER_COMPOSITE_INTERSECTION = 4

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
    LAYER_MODE_HSL_COLOUR_LEGACY = 13
    LAYER_MODE_HSV_VALUE_LEGACY = 14
    LAYER_MODE_DIVIDE_LEGACY = 15
    LAYER_MODE_DODGE_LEGACY = 16
    LAYER_MODE_BURN_LEGACY = 17
    LAYER_MODE_HARDLIGHT_LEGACY = 18
    LAYER_MODE_SOFTLIGHT_LEGACY = 19
    LAYER_MODE_GRAIN_EXTRACT_LEGACY = 20
    LAYER_MODE_GRAIN_MERGE_LEGACY = 21
    LAYER_MODE_COLOUR_ERASE_LEGACY = 22
    LAYER_MODE_OVERLAY = 23
    LAYER_MODE_LCH_HUE = 24
    LAYER_MODE_LCH_CHROMA = 25
    LAYER_MODE_LCH_COLOUR = 26
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
    LAYER_MODE_HSL_COLOUR = 39
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
    LAYER_MODE_COLOUR_ERASE = 57
    LAYER_MODE_ERASE = 58
    LAYER_MODE_MERGE = 59
    LAYER_MODE_SPLIT = 60
    LAYER_MODE_PASS_THROUGH = 61

    # from libgimpwidgets/gimpwidgetstypes.h:

    HelpFunc = ct.CFUNCTYPE(None, ct.c_char_p, ct.c_void_p)

    # from libgimpwidgets/gimpwidgetsenums.h:

    ColourSelectorChannel = ct.c_uint
    # values for ColourSelectorChannel:
    COLOUR_SELECTOR_HUE = 0
    COLOUR_SELECTOR_SATURATION = 1
    COLOUR_SELECTOR_VALUE = 2
    COLOUR_SELECTOR_RED = 3
    COLOUR_SELECTOR_GREEN = 4
    COLOUR_SELECTOR_BLUE = 5
    COLOUR_SELECTOR_ALPHA = 6
    COLOUR_SELECTOR_LCH_LIGHTNESS = 7
    COLOUR_SELECTOR_LCH_CHROMA = 8
    COLOUR_SELECTOR_LCH_HUE = 9

    ColourSelectorModel = ct.c_uint
    # values for ColourSelectorModel:
    COLOUR_SELECTOR_MODEL_RGB = 0
    COLOUR_SELECTOR_MODEL_LCH = 1
    COLOUR_SELECTOR_MODEL_HSV = 2

    # from libgimpwidgets/gimpcolorselector.h:

    COLOUR_SELECTOR_SIZE = 150
    COLOUR_SELECTOR_BAR_SIZE = 15

    class ColourSelector(Structure) :
        pass
    ColourSelector._fields_ = \
        [
            ("parent_instance", ct.c_void_p), # GtkBox
            ("toggles_visible", ct.c_bool),
            ("toggles_sensitive", ct.c_bool),
            ("show_alpha", ct.c_bool),
            ("rgb", RGB),
            ("hsv", HSV),
            ("channel", ColourSelectorChannel),
        ]
    #end ColourSelector

    # from libgimpwidgets/gimpdialog.h:

    class Dialog(Structure) :
        _fields_ = \
            [
                ("parent_instance", ct.c_void_p),
            ]
    #end Dialog

#end GIMP

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

#+
# Routine arg/result types
#-

libgimp2 = ct.cdll.LoadLibrary("libgimp-2.0.so.0")
libgimpui2 = ct.cdll.LoadLibrary("libgimpui-2.0.so.0")

# from libgimpbase/gimpbaseenums.h:

libgimp2.gimp_add_mask_type_get_type.restype = GType
libgimp2.gimp_add_mask_type_get_type.argtypes = ()
libgimp2.gimp_blend_mode_get_type.restype = GType
libgimp2.gimp_blend_mode_get_type.argtypes = ()
libgimp2.gimp_brush_generated_shape_get_type.restype = GType
libgimp2.gimp_brush_generated_shape_get_type.argtypes = ()
libgimp2.gimp_bucket_fill_mode_get_type.restype = GType
libgimp2.gimp_bucket_fill_mode_get_type.argtypes = ()
libgimp2.gimp_cap_style_get_type.restype = GType
libgimp2.gimp_cap_style_get_type.argtypes = ()
libgimp2.gimp_channel_ops_get_type.restype = GType
libgimp2.gimp_channel_ops_get_type.argtypes = ()
libgimp2.gimp_channel_type_get_type.restype = GType
libgimp2.gimp_channel_type_get_type.argtypes = ()
libgimp2.gimp_check_size_get_type.restype = GType
libgimp2.gimp_check_size_get_type.argtypes = ()
libgimp2.gimp_check_type_get_type.restype = GType
libgimp2.gimp_check_type_get_type.argtypes = ()
libgimp2.gimp_clone_type_get_type.restype = GType
libgimp2.gimp_clone_type_get_type.argtypes = ()
libgimp2.gimp_color_tag_get_type.restype = GType
libgimp2.gimp_color_tag_get_type.argtypes = ()
libgimp2.gimp_component_type_get_type.restype = GType
libgimp2.gimp_component_type_get_type.argtypes = ()
libgimp2.gimp_convert_palette_type_get_type.restype = GType
libgimp2.gimp_convert_palette_type_get_type.argtypes = ()
libgimp2.gimp_convolve_type_get_type.restype = GType
libgimp2.gimp_convolve_type_get_type.argtypes = ()
libgimp2.gimp_desaturate_mode_get_type.restype = GType
libgimp2.gimp_desaturate_mode_get_type.argtypes = ()
libgimp2.gimp_dodge_burn_type_get_type.restype = GType
libgimp2.gimp_dodge_burn_type_get_type.argtypes = ()
libgimp2.gimp_fill_type_get_type.restype = GType
libgimp2.gimp_fill_type_get_type.argtypes = ()
libgimp2.gimp_foreground_extract_mode_get_type.restype = GType
libgimp2.gimp_foreground_extract_mode_get_type.argtypes = ()
libgimp2.gimp_gradient_blend_color_space_get_type.restype = GType
libgimp2.gimp_gradient_blend_color_space_get_type.argtypes = ()
libgimp2.gimp_gradient_segment_color_get_type.restype = GType
libgimp2.gimp_gradient_segment_color_get_type.argtypes = ()
libgimp2.gimp_gradient_segment_type_get_type.restype = GType
libgimp2.gimp_gradient_segment_type_get_type.argtypes = ()
libgimp2.gimp_gradient_type_get_type.restype = GType
libgimp2.gimp_gradient_type_get_type.argtypes = ()
libgimp2.gimp_grid_style_get_type.restype = GType
libgimp2.gimp_grid_style_get_type.argtypes = ()
libgimp2.gimp_hue_range_get_type.restype = GType
libgimp2.gimp_hue_range_get_type.argtypes = ()
libgimp2.gimp_icon_type_get_type.restype = GType
libgimp2.gimp_icon_type_get_type.argtypes = ()
libgimp2.gimp_image_base_type_get_type.restype = GType
libgimp2.gimp_image_base_type_get_type.argtypes = ()
libgimp2.gimp_image_type_get_type.restype = GType
libgimp2.gimp_image_type_get_type.argtypes = ()
libgimp2.gimp_ink_blob_type_get_type.restype = GType
libgimp2.gimp_ink_blob_type_get_type.argtypes = ()
libgimp2.gimp_interpolation_type_get_type.restype = GType
libgimp2.gimp_interpolation_type_get_type.argtypes = ()
libgimp2.gimp_join_style_get_type.restype = GType
libgimp2.gimp_join_style_get_type.argtypes = ()
libgimp2.gimp_mask_apply_mode_get_type.restype = GType
libgimp2.gimp_mask_apply_mode_get_type.argtypes = ()
libgimp2.gimp_merge_type_get_type.restype = GType
libgimp2.gimp_merge_type_get_type.argtypes = ()
libgimp2.gimp_message_handler_type_get_type.restype = GType
libgimp2.gimp_message_handler_type_get_type.argtypes = ()
libgimp2.gimp_offset_type_get_type.restype = GType
libgimp2.gimp_offset_type_get_type.argtypes = ()
libgimp2.gimp_orientation_type_get_type.restype = GType
libgimp2.gimp_orientation_type_get_type.argtypes = ()
libgimp2.gimp_paint_application_mode_get_type.restype = GType
libgimp2.gimp_paint_application_mode_get_type.argtypes = ()
libgimp2.gimp_pdb_arg_type_get_type.restype = GType
libgimp2.gimp_pdb_arg_type_get_type.argtypes = ()
libgimp2.gimp_pdb_error_handler_get_type.restype = GType
libgimp2.gimp_pdb_error_handler_get_type.argtypes = ()
libgimp2.gimp_pdb_proc_type_get_type.restype = GType
libgimp2.gimp_pdb_proc_type_get_type.argtypes = ()
libgimp2.gimp_pdb_status_type_get_type.restype = GType
libgimp2.gimp_pdb_status_type_get_type.argtypes = ()
libgimp2.gimp_precision_get_type.restype = GType
libgimp2.gimp_precision_get_type.argtypes = ()
libgimp2.gimp_progress_command_get_type.restype = GType
libgimp2.gimp_progress_command_get_type.argtypes = ()
libgimp2.gimp_repeat_mode_get_type.restype = GType
libgimp2.gimp_repeat_mode_get_type.argtypes = ()
libgimp2.gimp_rotation_type_get_type.restype = GType
libgimp2.gimp_rotation_type_get_type.argtypes = ()
libgimp2.gimp_run_mode_get_type.restype = GType
libgimp2.gimp_run_mode_get_type.argtypes = ()
libgimp2.gimp_select_criterion_get_type.restype = GType
libgimp2.gimp_select_criterion_get_type.argtypes = ()
libgimp2.gimp_size_type_get_type.restype = GType
libgimp2.gimp_size_type_get_type.argtypes = ()
libgimp2.gimp_stack_trace_mode_get_type.restype = GType
libgimp2.gimp_stack_trace_mode_get_type.argtypes = ()
libgimp2.gimp_stroke_method_get_type.restype = GType
libgimp2.gimp_stroke_method_get_type.argtypes = ()
libgimp2.gimp_text_direction_get_type.restype = GType
libgimp2.gimp_text_direction_get_type.argtypes = ()
libgimp2.gimp_text_hint_style_get_type.restype = GType
libgimp2.gimp_text_hint_style_get_type.argtypes = ()
libgimp2.gimp_text_justification_get_type.restype = GType
libgimp2.gimp_text_justification_get_type.argtypes = ()
libgimp2.gimp_transfer_mode_get_type.restype = GType
libgimp2.gimp_transfer_mode_get_type.argtypes = ()
libgimp2.gimp_transform_direction_get_type.restype = GType
libgimp2.gimp_transform_direction_get_type.argtypes = ()

# from libgimpconfig/gimpconfigenums.h:
libgimp2.gimp_color_management_mode_get_type.restype = GType
libgimp2.gimp_color_management_mode_get_type.argtypes = ()
libgimp2.gimp_color_rendering_intent_get_type.restype = GType
libgimp2.gimp_color_rendering_intent_get_type.argtypes = ()

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

# from libgimp/gimpdrawable.h:

libgimp2.gimp_drawable_get_buffer.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_get_buffer.restype = ct.c_void_p
libgimp2.gimp_drawable_get_shadow_buffer.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_get_shadow_buffer.restype = ct.c_void_p
#libgimp2.gimp_drawable_flush.argtypes = (ct.c_void_p,)
#libgimp2.gimp_drawable_flush.restype = None
  # deprecated, use GEGL instead

# from libgimp/gimpdrawable_pdb.h:

libgimp2.gimp_drawable_type.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_type.restype = GIMP.ImageType
libgimp2.gimp_drawable_type_with_alpha.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_type_with_alpha.restype = GIMP.ImageType
libgimp2.gimp_drawable_has_alpha.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_has_alpha.restype = ct.c_bool
libgimp2.gimp_drawable_is_rgb.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_is_rgb.restype = ct.c_bool
libgimp2.gimp_drawable_is_gray.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_is_gray.restype = ct.c_bool
libgimp2.gimp_drawable_is_indexed.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_is_indexed.restype = ct.c_bool
libgimp2.gimp_drawable_bpp.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_bpp.restype = ct.c_int
libgimp2.gimp_drawable_width.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_width.restype = ct.c_int
libgimp2.gimp_drawable_height.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_height.restype = ct.c_int
libgimp2.gimp_drawable_offsets.argtypes = (ct.c_int32, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
libgimp2.gimp_drawable_offsets.restype = ct.c_bool
libgimp2.gimp_drawable_set_image.argtypes = (ct.c_int32, ct.c_int32)
libgimp2.gimp_drawable_set_image.restype = ct.c_bool
libgimp2.gimp_drawable_mask_bounds.argtypes = (ct.c_int32, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
libgimp2.gimp_drawable_mask_bounds.restype = ct.c_bool
libgimp2.gimp_drawable_mask_intersect.argtypes = (ct.c_int32, ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
libgimp2.gimp_drawable_mask_intersect.restype = ct.c_bool
libgimp2.gimp_drawable_merge_shadow.argtypes = (ct.c_int32, ct.c_bool)
libgimp2.gimp_drawable_merge_shadow.restype = ct.c_bool
libgimp2.gimp_drawable_free_shadow.argtypes = (ct.c_int32,)
libgimp2.gimp_drawable_free_shadow.restype = ct.c_bool
libgimp2.gimp_drawable_update.argtypes = (ct.c_int32, ct.c_int, ct.c_int, ct.c_int, ct.c_int)
libgimp2.gimp_drawable_update.restype = ct.c_bool
libgimp2.gimp_drawable_get_pixel.argtypes = (ct.c_int32, ct.c_int, ct.c_int, ct.POINTER(ct.c_int))
libgimp2.gimp_drawable_get_pixel.restype = ct.c_void_p # ct.POINTER(ct.c_uint8)
libgimp2.gimp_drawable_set_pixel.argtypes = (ct.c_int32, ct.c_int, ct.c_int, ct.c_int, ct.c_void_p)
libgimp2.gimp_drawable_set_pixel.restype = ct.c_bool
libgimp2.gimp_drawable_fill.argtypes = (ct.c_int32, GIMP.FillType)
libgimp2.gimp_drawable_fill.restype = ct.c_bool
libgimp2.gimp_drawable_offset.argtypes = (ct.c_int32, ct.c_bool, GIMP.OffsetType, ct.c_int, ct.c_int)
libgimp2.gimp_drawable_offset.restype = ct.c_bool
libgimp2.gimp_drawable_foreground_extract.argtypes = (ct.c_uint32, GIMP.ForegroundExtractMode, ct.c_uint32)
libgimp2.gimp_drawable_foreground_extract.restype = ct.c_bool

# from libgimp/gimpdisplay_pdb.h:

libgimp2.gimp_displays_flush.argtypes = ()
libgimp2.gimp_displays_flush.restype = None

# from libgimp/gimpenums.h:

libgimp2.gimp_brush_application_mode_get_type.argtypes = ()
libgimp2.gimp_brush_application_mode_get_type.restype = GType
libgimp2.gimp_convert_dither_type_get_type.argtypes = ()
libgimp2.gimp_convert_dither_type_get_type.restype = GType
libgimp2.gimp_histogram_channel_get_type.argtypes = ()
libgimp2.gimp_histogram_channel_get_type.restype = GType
libgimp2.gimp_layer_color_space_get_type.argtypes = ()
libgimp2.gimp_layer_color_space_get_type.restype = GType
libgimp2.gimp_layer_composite_mode_get_type.argtypes = ()
libgimp2.gimp_layer_composite_mode_get_type.restype = GType
libgimp2.gimp_layer_mode_get_type.argtypes = ()
libgimp2.gimp_layer_mode_get_type.restype = GType
libgimp2.gimp_enums_init.argtypes = ()
libgimp2.gimp_enums_init.restype = None
libgimp2.gimp_enums_get_type_names.argtypes = (ct.POINTER(ct.c_int),)
libgimp2.gimp_enums_get_type_names.restype = ct.c_void_p # ct.POINTER(ct.c_char_p)

# from libgimp/gimpproceduraldb.h:

libgimp2.gimp_procedural_db_proc_info.argtypes = (ct.c_char_p, ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(ct.c_char_p), ct.POINTER(GIMP.PDBProcType), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.POINTER(GIMP.ParamDef)), ct.POINTER(ct.POINTER(GIMP.ParamDef)))
libgimp2.gimp_procedural_db_proc_info.restype = ct.c_bool
libgimp2.gimp_procedural_db_get_data.argtypes = (ct.c_char_p, ct.c_void_p)
libgimp2.gimp_procedural_db_get_data.restype = ct.c_bool
libgimp2.gimp_procedural_db_set_data.argtypes = (ct.c_char_p, ct.c_void_p, ct.c_uint32)
libgimp2.gimp_procedural_db_set_data.restype = ct.c_bool

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
libgimp2.gimp_layer_new_from_surface.argtypes = (ct.c_int32, ct.c_char_p, ct.c_void_p, ct.c_double, ct.c_double)
libgimp2.gimp_layer_new_from_surface.restype = ct.c_int32
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

libgimp2.gimp_layer_new_from_visible.argtypes = (ct.c_int32, ct.c_int32, ct.c_char_p)
libgimp2.gimp_layer_new_from_visible.restype = ct.c_int32
libgimp2.gimp_layer_new_from_drawable.argtypes = (ct.c_int32, ct.c_int32)
libgimp2.gimp_layer_new_from_drawable.restype = ct.c_int32
libgimp2.gimp_layer_group_new.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_group_new.restype = ct.c_int32
libgimp2.gimp_layer_add_alpha.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_add_alpha.restype = ct.c_bool
libgimp2.gimp_layer_flatten.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_flatten.restype = ct.c_bool
libgimp2.gimp_layer_scale.argtypes = (ct.c_int32, ct.c_int, ct.c_int, ct.c_bool)
libgimp2.gimp_layer_scale.restype = ct.c_bool
# gimp_layer_scale_full deprecated
libgimp2.gimp_layer_resize.argtypes = (ct.c_int32, ct.c_int, ct.c_int, ct.c_int, ct.c_int)
libgimp2.gimp_layer_resize.restype = ct.c_bool
libgimp2.gimp_layer_resize_to_image_size.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_resize_to_image_size.restype = ct.c_bool
# gimp_layer_translate deprecated
libgimp2.gimp_layer_set_offsets.argtypes = (ct.c_int32, ct.c_int, ct.c_int)
libgimp2.gimp_layer_set_offsets.restype = ct.c_bool
libgimp2.gimp_layer_create_mask.argtypes = (ct.c_int32, ct.c_int, GIMP.AddMaskType)
libgimp2.gimp_layer_create_mask.restype = ct.c_bool
libgimp2.gimp_layer_get_mask.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_mask.restype = ct.c_int32
libgimp2.gimp_layer_from_mask.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_from_mask.restype = ct.c_int32
libgimp2.gimp_layer_add_mask.argtypes = (ct.c_int32, ct.c_int32)
libgimp2.gimp_layer_add_mask.restype = ct.c_bool
libgimp2.gimp_layer_remove_mask.argtypes = (ct.c_int32, GIMP.MaskApplyMode)
libgimp2.gimp_layer_remove_mask.restype = ct.c_bool
libgimp2.gimp_layer_is_floating_sel.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_is_floating_sel.restype = ct.c_bool
libgimp2.gimp_layer_get_lock_alpha.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_lock_alpha.restype = ct.c_bool
libgimp2.gimp_layer_set_lock_alpha.argtypes = (ct.c_int32, ct.c_bool)
libgimp2.gimp_layer_set_lock_alpha.restype = ct.c_bool
libgimp2.gimp_layer_get_apply_mask.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_apply_mask.restype = ct.c_bool
libgimp2.gimp_layer_set_apply_mask.argtypes = (ct.c_int32, ct.c_bool)
libgimp2.gimp_layer_set_apply_mask.restype = ct.c_bool
libgimp2.gimp_layer_get_show_mask.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_show_mask.restype = ct.c_bool
libgimp2.gimp_layer_set_show_mask.argtypes = (ct.c_int32, ct.c_bool)
libgimp2.gimp_layer_set_show_mask.restype = ct.c_bool
libgimp2.gimp_layer_get_edit_mask.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_edit_mask.restype = ct.c_bool
libgimp2.gimp_layer_set_edit_mask.argtypes = (ct.c_int32, ct.c_bool)
libgimp2.gimp_layer_set_edit_mask.restype = ct.c_bool
libgimp2.gimp_layer_get_opacity.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_opacity.restype = ct.c_double
libgimp2.gimp_layer_set_opacity.argtypes = (ct.c_int32, ct.c_double)
libgimp2.gimp_layer_set_opacity.restype = ct.c_bool
libgimp2.gimp_layer_get_mode.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_mode.restype = GIMP.LayerMode
libgimp2.gimp_layer_set_mode.argtypes = (ct.c_int32, GIMP.LayerMode)
libgimp2.gimp_layer_set_mode.restype = ct.c_bool
libgimp2.gimp_layer_get_blend_space.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_blend_space.restype = GIMP.LayerColourSpace
libgimp2.gimp_layer_set_blend_space.argtypes = (ct.c_int32, GIMP.LayerColourSpace)
libgimp2.gimp_layer_set_blend_space.restype = ct.c_bool
libgimp2.gimp_layer_get_composite_space.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_composite_space.restype = GIMP.LayerColourSpace
libgimp2.gimp_layer_set_composite_space.argtypes = (ct.c_int32, GIMP.LayerColourSpace)
libgimp2.gimp_layer_set_composite_space.restype = ct.c_bool
libgimp2.gimp_layer_get_composite_mode.argtypes = (ct.c_int32,)
libgimp2.gimp_layer_get_composite_mode.restype = GIMP.LayerCompositeMode
libgimp2.gimp_layer_set_composite_mode.argtypes = (ct.c_int32, GIMP.LayerCompositeMode)
libgimp2.gimp_layer_set_composite_mode.restype = ct.c_bool

# from libgimp/libgimp/gimpimageundo_pdb.h:

libgimp2.gimp_image_undo_group_start.argtypes = (ct.c_int32,)
libgimp2.gimp_image_undo_group_start.restype = ct.c_bool
libgimp2.gimp_image_undo_group_end.argtypes = (ct.c_int32,)
libgimp2.gimp_image_undo_group_end.restype = ct.c_bool

# from libgimp/gimpdrawablecolor_pdb.h:

libgimp2.gimp_drawable_levels.argtypes = (ct.c_int32, GIMP.HistogramChannel, ct.c_double, ct.c_double, ct.c_bool, ct.c_double, ct.c_double, ct.c_double, ct.c_bool)
libgimp2.gimp_drawable_levels.restype = ct.c_bool

# from libgimp/gimpprogress.h:

libgimp2.gimp_progress_update.argtypes = (ct.c_double,)
libgimp2.gimp_progress_update.restype = ct.c_bool

# from libgimp/gimpui.h:

libgimpui2.gimp_ui_init.argtypes = (ct.c_char_p, ct.c_bool)
libgimpui2.gimp_ui_init.restype = None
libgimpui2.gimp_ui_get_display_window.argtypes = (ct.c_uint32,)
libgimpui2.gimp_ui_get_display_window.restype = ct.c_void_p
libgimpui2.gimp_ui_get_progress_window.argtypes = ()
libgimpui2.gimp_ui_get_progress_window.restype = ct.c_void_p
libgimpui2.gimp_window_set_transient_for_display.argtypes = (ct.c_void_p, ct.c_uint32)
libgimpui2.gimp_window_set_transient_for_display.restype = None
libgimpui2.gimp_window_set_transient.restype = None
libgimpui2.gimp_window_set_transient.argtypes = (ct.c_void_p,)

# from libgimpwidgets/gimpwidgets.h:

libgimpui2.gimp_toggle_button_update.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_toggle_button_update.restype = None
libgimpui2.gimp_radio_button_update.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_radio_button_update.restype = None
libgimpui2.gimp_int_adjustment_update.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_int_adjustment_update.restype = None
libgimpui2.gimp_float_adjustment_update.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_float_adjustment_update.restype = None
libgimpui2.gimp_double_adjustment_update.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_double_adjustment_update.restype = None
# note that gimp_spin_button_new is deprecated
libgimpui2.gimp_int_radio_group_new.argtypes = (ct.c_bool, ct.c_char_p, GCallback, ct.c_void_p, ct.c_int, ct.c_void_p) # varargs!
libgimpui2.gimp_int_radio_group_new.restype = ct.c_void_p
libgimpui2.gimp_int_radio_group_set_active.argtypes = (ct.c_void_p, ct.c_int)
libgimpui2.gimp_int_radio_group_set_active.restype = None
libgimpui2.gimp_radio_group_new.argtypes = (ct.c_bool, ct.c_char_p, ct.c_void_p) # varargs!
libgimpui2.gimp_radio_group_new.restype = ct.c_void_p
libgimpui2.gimp_radio_group_new2.argtypes = (ct.c_bool, ct.c_char_p, GCallback, ct.c_void_p, ct.c_void_p, ct.c_void_p) # varargs!
libgimpui2.gimp_radio_group_new2.restype = ct.c_void_p
libgimpui2.gimp_radio_group_set_active.argtypes = (ct.c_void_p, ct.c_void_p)
libgimpui2.gimp_radio_group_set_active.restype = None

# from libgimpwidgets/gimpframe.h:

libgimpui2.gimp_frame_new.argtypes = (ct.c_char_p,)
libgimpui2.gimp_frame_new.restype = ct.c_void_p

# from libgimpwidgets/gimpscaleentry.h:

libgimpui2.gimp_scale_entry_new.argtypes = (ct.c_void_p, ct.c_int, ct.c_int, ct.c_char_p, ct.c_int, ct.c_int, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_uint, ct.c_bool, ct.c_double, ct.c_double, ct.c_char_p, ct.c_char_p)
libgimpui2.gimp_scale_entry_new.restype = ct.c_void_p
libgimpui2.gimp_color_scale_entry_new.argtypes = (ct.c_void_p, ct.c_int, ct.c_int, ct.c_char_p, ct.c_int, ct.c_int, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.c_uint, ct.c_char_p, ct.c_char_p)
libgimpui2.gimp_color_scale_entry_new.restype = ct.c_void_p
libgimpui2.gimp_scale_entry_set_sensitive.argtypes = (ct.c_void_p, ct.c_bool)
libgimpui2.gimp_scale_entry_set_sensitive.restype = None
libgimpui2.gimp_scale_entry_set_logarithmic.argtypes = (ct.c_void_p, ct.c_bool)
libgimpui2.gimp_scale_entry_set_logarithmic.restype = None
libgimpui2.gimp_scale_entry_get_logarithmic.argtypes = (ct.c_void_p,)
libgimpui2.gimp_scale_entry_get_logarithmic.restype = ct.c_bool

# from libgimpwidgets/gimpspinbutton.h:

libgimpui2.gimp_spin_button_new_.argtypes = (ct.c_void_p, ct.c_double, ct.c_uint)
libgimpui2.gimp_spin_button_new_.restype = ct.c_void_p
libgimpui2.gimp_spin_button_new_with_range.argtypes = (ct.c_double, ct.c_double, ct.c_double)
libgimpui2.gimp_spin_button_new_with_range.restype = ct.c_void_p

# from libgimpwidgets/gimpcolorselector.h:

libgimpui2.gimp_color_selector_get_type.argtypes = ()
libgimpui2.gimp_color_selector_get_type.restype = GType
libgimpui2.gimp_color_selector_new.argtypes = (GType, ct.POINTER(GIMP.RGB), ct.POINTER(GIMP.HSV), GIMP.ColourSelectorChannel)
libgimpui2.gimp_color_selector_new.restype = ct.c_void_p
libgimpui2.gimp_color_selector_set_toggles_visible.argtypes = (ct.c_void_p, ct.c_bool)
libgimpui2.gimp_color_selector_set_toggles_visible.restype = None
libgimpui2.gimp_color_selector_get_toggles_visible.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_get_toggles_visible.restype = ct.c_bool
libgimpui2.gimp_color_selector_set_toggles_sensitive.argtypes = (ct.c_void_p, ct.c_bool)
libgimpui2.gimp_color_selector_set_toggles_sensitive.restype = None
libgimpui2.gimp_color_selector_get_toggles_sensitive.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_get_toggles_sensitive.restype = ct.c_bool
libgimpui2.gimp_color_selector_set_show_alpha.argtypes = (ct.c_void_p, ct.c_bool)
libgimpui2.gimp_color_selector_set_show_alpha.restype = None
libgimpui2.gimp_color_selector_get_show_alpha.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_get_show_alpha.restype = ct.c_bool
libgimpui2.gimp_color_selector_set_color.argtypes = (ct.c_void_p, ct.POINTER(GIMP.RGB), ct.POINTER(GIMP.HSV))
libgimpui2.gimp_color_selector_set_color.restype = None
libgimpui2.gimp_color_selector_get_color.argtypes = (ct.c_void_p, ct.POINTER(GIMP.RGB), ct.POINTER(GIMP.HSV))
libgimpui2.gimp_color_selector_get_color.restype = None
libgimpui2.gimp_color_selector_set_channel.argtypes = (ct.c_void_p, GIMP.ColourSelectorChannel)
libgimpui2.gimp_color_selector_set_channel.restype = None
libgimpui2.gimp_color_selector_get_channel.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_get_channel.restype = GIMP.ColourSelectorChannel
libgimpui2.gimp_color_selector_set_model_visible.argtypes = (ct.c_void_p, GIMP.ColourSelectorModel, ct.c_bool)
libgimpui2.gimp_color_selector_set_model_visible.restype = None
libgimpui2.gimp_color_selector_get_model_visible.argtypes = (ct.c_void_p, GIMP.ColourSelectorModel)
libgimpui2.gimp_color_selector_set_model_visible.restype = ct.c_bool
libgimpui2.gimp_color_selector_color_changed.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_color_changed.restype = None
libgimpui2.gimp_color_selector_channel_changed.argtypes = (ct.c_void_p,)
libgimpui2.gimp_color_selector_channel_changed.restype = None
libgimpui2.gimp_color_selector_model_visible_changed.argtypes = (ct.c_void_p, GIMP.ColourSelectorModel)
libgimpui2.gimp_color_selector_model_visible_changed.restype = None
# todo gimp_color_selector_set_config

# from libgimpwidgets/gimpcolorselect.h:

libgimpui2.gimp_color_select_get_type.argtypes = ()
libgimpui2.gimp_color_select_get_type.restype = GType

# from libgimpwidgets/gimpdialog.h:

libgimpui2.gimp_dialog_new.argtypes = (ct.c_char_p, ct.c_char_p, ct.c_void_p, GTK.DialogFlags, GIMP.HelpFunc, ct.c_char_p, ct.c_void_p)
  # Unfortunately I can’t do the varargs bit, so last arg must always be None
libgimpui2.gimp_dialog_new.restype = ct.c_void_p
libgimpui2.gimp_dialog_add_button.argtypes = (ct.c_void_p, ct.c_char_p, ct.c_int)
libgimpui2.gimp_dialog_add_button.restype = ct.c_void_p
libgimpui2.gimp_dialog_run.argtypes = (ct.c_void_p,)
libgimpui2.gimp_dialog_run.restype = ct.c_int

# from libgimpwidgets/gimphelpui.h:

libgimpui2.gimp_standard_help_func.argtypes = (ct.c_char_p, ct.c_void_p)
libgimpui2.gimp_standard_help_func.restype = None
STANDARD_HELP_FUNC = GIMP.HelpFunc(libgimpui2.gimp_standard_help_func)

# from libgimpwidgets/gimp3migration.h:

libgimpui2.gtk_box_new.argtypes = (GTK.Orientation, ct.c_int)
libgimpui2.gtk_box_new.restype = ct.c_void_p
libgimpui2.gtk_scale_new.argtypes = (GTK.Orientation, ct.c_void_p)
libgimpui2.gtk_scale_new.restype = ct.c_void_p

#+
# Higher-level stuff follows
#-

class CallFailed(Exception) :
    "used internally for reporting general failure from calling a GIMP routine."

    __slots__ = ("funcname",)

    def __init__(self, funcname) :
        self.args = ("%s failed" % funcname,)
        self.funcname = funcname
    #end __init__

#end CallFailed

class ObjID :
    "base class for convenient wrappers for objects which GIMP identifies" \
    " just by an integer ID. Instantiate a suitable subclass around such an" \
    " ID, and you can use it to make the relevant wrapped method calls."

    __slots__ = ("id", "__weakref__")

    _instances = WeakValueDictionary()

    def __new__(celf, id) :
        self = celf._instances.get(id)
        if self != None and type(self) != celf :
            self = None # force creation of a separate wrapper for different expected type
        #end if
        if self == None :
            self = super().__new__(celf)
            self.id = id
            celf._instances[id] = self
        #end if
        return \
            self
    #end __new__

    def __repr__(self) :
        "show object class name and ID."
        return \
            "%s(%d)"% (type(self).__name__, self.id)
    #end __repr__

#end ObjID

class Image(ObjID) :

    __slots__ = ()

#end Image

class Drawable(ObjID) :

    __slots__ = ()

    @property
    def has_alpha(self) :
        return \
            libgimp2.gimp_drawable_has_alpha(self.id)
    #end has_alpha

    @property
    def is_rgb(self) :
        return \
            libgimp2.gimp_drawable_is_rgb(self.id)
    #end is_rgb

    @property
    def is_grey(self) :
        return \
            libgimp2.gimp_drawable_is_gray(self.id)
    #end is_grey
    is_gray = is_grey # if you prefer

    @property
    def is_indexed(self) :
        return \
            libgimp2.gimp_drawable_is_indexed(self.id)
    #end is_indexed

    @property
    def bpp(self) :
        return \
            libgimp2.gimp_drawable_bpp(self.id)
    #end bpp

    @property
    def width(self) :
        return \
            libgimp2.gimp_drawable_width(self.id)
    #end width

    @property
    def height(self) :
        return \
            libgimp2.gimp_drawable_height(self.id)
    #end height

    @property
    def bpp(self) :
        x = ct.c_int()
        y = ct.c_int()
        if not libgimp2.gimp_drawable_offsets(self.id, ct.byref(x), ct.byref(y)) :
            raise CallFailed("gimp_drawable_offsets")
        #end if
        return \
            (x.value, y.value)
    #end bpp

    def set_image(self, image) :
        if not isinstance(image, Image) :
            raise TypeError("image must be an Image")
        #end if
        if not libgimp2.gimp_drawable_set_image(self.id, image.id) :
            raise CallFailed("gimp_drawable_set_image")
        #end if
    #end set_image

    @property
    def mask_bounds(self) :
        "the bounds of the current selection, or None if none."
        x1 = ct.c_int()
        y1 = ct.c_int()
        x2 = ct.c_int()
        y2 = ct.c_int()
        if libgimp2.gimp_drawable_mask_bounds(self.id, ct.byref(x1), ct.byref(y1), ct.byref(x2), ct.byref(y2)) :
            result = (x1.value, y1.value, x2.value, y2.value)
        else :
            result = None
        #end if
        return \
            result
    #end mask_bounds

    @property
    def mask_intersect(self) :
        x = ct.c_int()
        y = ct.c_int()
        width = ct.c_int()
        height = ct.c_int()
        if libgimp2.gimp_drawable_mask_intersect(self.id, ct.byref(x), ct.byref(y), ct.byref(width), ct.byref(height)) :
            result = (x.value, y.value, width.value, height.value)
        else :
            result = None
        #end if
        return \
            result
    #end mask_intersect

    def merge_shadow(self, undo) :
        if not libgimp2.gimp_drawable_merge_shadow(self.id, undo) :
            raise CallFailed("gimp_drawable_merge_shadow")
        #end if
    #end merge_shadow

    def free_shadow(self) :
        if not libgimp2.gimp_drawable_free_shadow(self.id) :
            raise CallFailed("gimp_drawable_free_shadow")
        #end if
    #end free_shadow

    def update(self, x, y, width, height) :
        if not libgimp2.gimp_drawable_update(self.id, x, y, width, height) :
            raise CallFailed("gimp_drawable_update")
        #end if
    #end update

    def get_pixel(self, x, y) :
        "Note that returned pixel data was allocated with g_new(), and" \
        " needs to be freed with gegl.libglib2.g_free()."
        # Perhaps I should create my own wrapper around
        # gimp_run_procedure("gimp-drawable-get-pixel" ...),
        # following example of gimp_drawable_get_pixel routine in
        # libgimp/gimpdrawable_pdb.c in source code?
        nr_channels = ct.c_int()
        pixel = libgimp2.gimp_drawable_get_pixel(self.id, x, y, ct.byref(nr_channels))
        nr_channels = nr_channels.value
        if nr_channels == 0 :
            raise CallFailed("gimp_drawable_get_pixel")
        #end if
        return \
            pixel, nr_channels
    #end get_pixel

    # TODO: set_pixel

    def fill(self, fill_type) :
        if not libgimp2.gimp_drawable_fill(self.id, fill_type) :
            raise CallFailed("gimp_drawable_fill")
        #end if
    #end fill

    def offset(self, wrap_around, fill_type, offset_x, offset_y) :
        if not libgimp2.gimp_drawable_offset(self.id, wrap_around, fill_type, offset_x, offset_y) :
            raise CallFailed("gimp_drawable_offset")
        #end if
    #end offset

    def foreground_extract(self, mode, mask) :
        if not isinstance(mask, Drawable) :
            raise TypeError("mask must be a Drawable")
        #end if
        if not libgimp2.gimp_drawable_foreground_extract(self.id, mode, mask.id) :
            raise CallFailed("gimp_drawable_foreground_extract")
        #end if
    #end foreground_extract

    def get_buffer(self) :
        return \
            gegl.Buffer(libgimp2.gimp_drawable_get_buffer(self.id))
    #end get_buffer

    def get_shadow_buffer(self) :
        return \
            gegl.Buffer(libgimp2.gimp_drawable_get_shadow_buffer(self.id))
    #end get_shadow_buffer

#end Drawable

class Layer(Drawable) :

    __slots__ = ()

    @classmethod
    def create(celf, image, name, width, height, type, opacity, mode) :
        if not isinstance(image, Image) :
            raise TypeError("image must be an Image")
        #end if
        result = libgimp2.gimp_layer_new(image.id, str_encode(name), width, height, type, opacity, mode)
        if result < 0 :
            raise CallFailed("gimp_layer_new")
        #end if
        return \
            celf(result)
    #end create

    # TODO create_from_surface

    @classmethod
    def create_from_visible(celf, image, dest_image, name) :
        if not isinstance(image, Image) or not isinstance(dest_image, Image) :
            raise TypeError("image and dest_image must be Image objects")
        #end if
        result = libgimp2.gimp_layer_new_from_visible(image.id, dest_image.id, str_encode(name))
        if result < 0 :
            raise CallFailed("gimp_layer_new_from_visible")
        #end if
        return \
            celf(result)
    #end create_from_visible

    @classmethod
    def create_from_drawable(celf, drawable, dest_image, name) :
        if not isinstance(drawable, Drawable) or not isinstance(dest_image, Image) :
            raise TypeError("drawable must be Drawable and image must be Image")
        #end if
        result = libgimp2.gimp_layer_new_from_drawable(drawable.id, dest_image.id, str_encode(name))
        if result < 0 :
            raise CallFailed("gimp_layer_new_from_drawable")
        #end if
        return \
            celf(result)
    #end create_from_drawable

    # TODO layer_group_new

    def add_alpha(self) :
        if not libgimp2.gimp_layer_add_alpha(self.id) :
            raise CallFailed("gimp_layer_add_alpha")
        #end if
    #end add_alpha

    def flatten(self) :
        if not libgimp2.gimp_layer_flatten(self.id) :
            raise CallFailed("gimp_layer_flatten")
        #end if
    #end flatten

    def scale(self, new_width, new_height, local_origin) :
        if not libgimp2.gimp_layer_scale(self.id, new_width, new_height, local_origin) :
            raise CallFailed("gimp_layer_scale")
        #end if
    #end scale

    def resize(self, new_width, new_height, offx, offy) :
        if not libgimp2.gimp_layer_resize(self.id, new_width, new_height, offx, offy) :
            raise CallFailed("gimp_layer_resize")
        #end if
    #end resize

    def resize_to_image_size(self) :
        if not libgimp2.gimp_layer_resize_to_image_size(self.id) :
            raise CallFailed("gimp_layer_resize_to_image_size")
        #end if
    #end resize_to_image_size

    def translate(self, offx, offy) :
        if not libgimp2.gimp_layer_translate(self.id, offx, offy) :
            raise CallFailed("gimp_layer_translate")
        #end if
    #end translate

    def set_offsets(self, offx, offy) :
        if not libgimp2.gimp_layer_set_offsets(self.id, offx, offy) :
            raise CallFailed("gimp_layer_set_offsets")
        #end if
    #end set_offsets

    def create_mask(self, mask_type) :
        result = libgimp2.gimp_layer_create_mask(self.id, mask_type)
        if result < 0 :
            raise CallFailed("gimp_layer_create_mask")
        #end if
        return \
            LayerMask(result)
    #end create_mask

    def get_mask(self) :
        result = libgimp2.gimp_layer_get_mask(self.id)
        if result >= 0 :
            result = LayerMask(result)
        else :
            result = None
        #end if
        return \
            result
    #end get_mask

    def add_mask(self, mask) :
        if not isinstance(mask, LayerMask) :
            raise TypeError("mask must be a LayerMask")
        #end if
        if not libgimp2.gimp_layer_add_mask(self.id, mask.id) :
            raise CallFailed("gimp_layer_add_mask")
        #end if
    #end add_mask

    def remove_mask(self, mode) :
        if not libgimp2.gimp_layer_remove_mask(self.id, mode) :
            raise CallFailed("gimp_layer_remove_mask")
        #end if
    #end remove_mask

    @property
    def is_floating_sel(self) :
        return \
            libgimp2.gimp_layer_is_floating_sel(self.id)
    #end is_floating_sel

    # TODO get/set lock_alpha, apply_mask, show_mask, edit_mask,
    # opacity, mode, blend_space, composite_space, composite_mode

#end Layer

class LayerMask(Drawable) :

    __slots__ = ()

    @classmethod
    def create(celf, from_layer, mask_type) :
        if not isinstance(from_layer, Layer) :
            raise TypeError("from_layer must be a layer")
        #end if
        result = libgimp2.gimp_layer_create_mask(from_layer.id, mask_type)
        if result < 0 :
            raise CallFailed("gimp_layer_create_mask")
        #end if
        return \
            celf(result)
    #end create

    def get_layer(self) :
        result = libgimp2.gimp_layer_from_mask(self.id)
        if result >= 0 :
            result = Layer(result)
        else :
            result = None
        #end if
        return \
            result
    #end get_layer

#end LayerMask

def def_expect_id_type(id_type) :

    def get_id(obj) :
        if not isinstance(obj, id_type) :
            raise TypeError("arg must be of type %s" % id_type.__name__)
        #end if
        return \
            obj.id
    #end get_id

#begin def_expect_id_type
    get_id.__name__ = "get_id_%s" % id_type.__name__
    return get_id
#end def_expect_id_type

class PARAMTYPE(enum.Enum) :

    # (argtype, ct_type, ParamData fieldname, to_ct_conv, from_ct_conv)
    # FIXME: to_ct_conv routines for string pointers will need to stash ctype objects somewhere
    INT32 = (GIMP.PDB_INT32, ct.c_int32, "d_int32", def_to_ct_int(32, True), ident)
    INT16 = (GIMP.PDB_INT16, ct.c_int16, "d_int16", def_to_ct_int(16, True), ident)
    INT8 = (GIMP.PDB_INT8, ct.c_int8, "d_int8", def_to_ct_int(8, False), ident)
    FLOAT = (GIMP.PDB_FLOAT, ct.c_double, "d_float", ct.c_double, ident)
    STRING = (GIMP.PDB_STRING, ct.c_char_p, "d_string", str_encode, str_decode)
    INT32ARRAY = (GIMP.PDB_INT32ARRAY, ct.c_void_p, "d_int32array", def_seq_to_ct(ct.c_int32), ct_to_seq)
    INT16ARRAY = (GIMP.PDB_INT16ARRAY, ct.c_void_p, "d_int16array", def_seq_to_ct(ct.c_int16), ct_to_seq)
    INT8ARRAY = (GIMP.PDB_INT8ARRAY, ct.c_void_p, "d_int8array", def_seq_to_ct(ct.c_uint8), ct_to_seq)
    FLOATARRAY = (GIMP.PDB_FLOATARRAY, ct.c_void_p, "d_floatarray", def_seq_to_ct(ct.c_double), ct_to_seq)
    STRINGARRAY = (GIMP.PDB_STRINGARRAY, ct.c_void_p, "d_stringarray", def_seq_to_ct(ct.c_char_p, str_encode), def_ct_to_seq(str_decode))
    COLOURARRAY = (GIMP.PDB_COLOURARRAY, ct.c_void_p, "d_colourarray", def_seq_to_ct(def_expect_type(GIMP.RGB)), ident)
    COLOUR = (GIMP.PDB_COLOUR, GIMP.RGB, "d_colour", def_expect_type(GIMP.RGB), ident)
    DISPLAY = (GIMP.PDB_DISPLAY, ct.c_int32, "d_display", def_to_ct_int(32, True), ident)
    IMAGE = (GIMP.PDB_IMAGE, ct.c_int32, "d_image", def_expect_id_type(Image), Image)
    ITEM = (GIMP.PDB_ITEM, ct.c_int32, "d_item", def_to_ct_int(32, True), ident)
    LAYER = (GIMP.PDB_LAYER, ct.c_int32, "d_layer", def_expect_id_type(Layer), Layer)
    # no enum for layer_mask?
    CHANNEL = (GIMP.PDB_CHANNEL, ct.c_int32, "d_channel", def_to_ct_int(32, True), ident)
    DRAWABLE = (GIMP.PDB_DRAWABLE, ct.c_int32, "d_drawable", def_expect_id_type(Drawable), Drawable)
    SELECTION = (GIMP.PDB_SELECTION, ct.c_int32, "d_selection", def_to_ct_int(32, True), ident)
    VECTORS = (GIMP.PDB_VECTORS, ct.c_int32, "d_vectors", def_to_ct_int(32, True), ident)
    # no enum for d_unit?
    PARASITE = (GIMP.PDB_PARASITE, GIMP.Parasite, "d_parasite", def_expect_type(GIMP.Parasite), ident)
    # no enum for d_tattoo?
    STATUS = (GIMP.PDB_STATUS, ct.c_uint, "d_status", def_to_ct_enum(GIMP.PDB_CANCEL), ident)

    @property
    def code(self) :
        return \
            self.value[0]
    #end code

    @property
    def ct_type(self) :
        return \
            self.value[1]
    #end ct_type

    @property
    def fieldname(self) :
        return \
            self.value[2]
    #end fieldname

    @property
    def to_ct_conv(self) :
        return \
            self.value[3]
    #end to_ct_conv

    @property
    def from_ct_conv(self) :
        return \
            self.value[4]
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

def params_to_ct(defs, vals) :
    if len(vals) != len(defs) :
        raise TypeError("expecting %d args, got %d" % (len(defs), len(vals)))
    #end if
    result = seq_to_ct \
      (
        seq = list(zip(defs, vals)),
        ct_type = GIMP.Param,
        conv = lambda v : param_to_ct(v[0]["type"], v[1])
      )
    return \
        result
#end params_to_ct

def param_from_ct(param) :
    type = PARAMTYPE.from_code[param.type]
    return \
        type.from_ct_conv(getattr(param.data, type.fieldname))
#end param_from_ct

class UI_PLACEMENT(enum.Enum) :
    "information about required parameters for plugins registered" \
    " at particular points in the UI."

    # path_prefix, required_params (excluding run-mode)
    TOOLBOX = ("<Toolbox>", ())
    IMAGE = \
        (
            "<Image>",
            (
                {"type" : PARAMTYPE.IMAGE, "name" : "image", "description" : "Input image"},
                {"type" : PARAMTYPE.DRAWABLE, "name" : "drawable", "description" : "Drawable to draw on"},
            ),
        )
    # I don’t know how to use the ones below. Also note other path prefixes
    # listed in app/plug-in/gimppluginprocedure.c in GIMP source code.
    LOAD = \
        (
            "<Load>",
            (
                {"type" : PARAMTYPE.STRING, "name" : "?1", "description" : "?1"},
                {"type" : PARAMTYPE.STRING, "name" : "?2", "description" : "?2"},
            ),
        )
    SAVE = \
        (
            "<Save>",
            (
                {"type" : PARAMTYPE.IMAGE, "name" : "image", "description" : "Input image"},
                {"type" : PARAMTYPE.DRAWABLE, "name" : "drawable", "description" : "Drawable to draw on"},
                {"type" : PARAMTYPE.STRING, "name" : "?1", "description" : "?1"},
                {"type" : PARAMTYPE.STRING, "name" : "?2", "description" : "?2"},
            ),
        )

    @property
    def path_prefix(self) :
        return \
            self.value[0]
    #end path_prefix

    @property
    def nr_required_params(self) :
        return \
            len(self.value[1]) + 1
    #end nr_required_params

    @property
    def required_params(self) :
        return \
            (
                [{"type" : PARAMTYPE.INT32, "name" : "run-mode", "description" : "invocation mode"}]
            +
                list(dict(p) for p in self.value[1])
            )
    #end required_params

#end UI_PLACEMENT

#+
# Interface to Procedural Database. This is where a plugin registers
# its callbacks, and it can also find and call routines registered
# by other plugins, as well as by GIMP itself.
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
    c_returns = ct.POINTER(GIMP.ParamDef)()
    success = libgimp2.gimp_procedural_db_proc_info(c_procname, ct.byref(c_blurb), ct.byref(c_help), ct.byref(c_author), ct.byref(c_copyright), ct.byref(c_date), ct.byref(c_proc_type), ct.byref(c_num_args), ct.byref(c_num_values), ct.byref(c_args), ct.byref(c_returns))
    if success :
        result = \
            {
                "name" : procname,
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
                ("returns", c_num_values.value, c_returns),
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
        libgimp2.gimp_destroy_paramdefs(c_returns, c_num_values.value)
    else :
        result = None
    #end if
    return \
        result
#end procedural_db_proc_info

class PDB :
    "local cache of GIMP’s procedure database (PDB). You can call any" \
    " procedure registered in the PDB as\n" \
    "\n" \
    "    returns = pdb.procname(args)\n" \
    "\n" \
    " where args and returns are sequences of argument/return values." \
    " Conversions between Python objects and GIMP.Param representation will" \
    " happen automatically, according to the argument and return ParamDefs" \
    " registered for the procedure, so you never pass or get back any" \
    " PDBArgType codes.\n" \
    "\n" \
    "Besides the general “pdb” cache, there are also ones called “pdb1”, for" \
    " procedures assumed to return a single result, and “pdbpi” for plugin" \
    " procedures, that take an initial argument which is the run mode (set to" \
    " GIMP.RUN_NONINTERACTIVE for your convenience). These save you having to" \
    " extract the returned value and pass the extra arg, respectively."

    __slots__ = ("_procs", "_procinfo_check", "_params_filter", "_returns_filter")

    def __init__(self, procinfo_check = None, params_filter = None, returns_filter = None) :
        self._procs = {}
        self._procinfo_check = procinfo_check
        self._params_filter = params_filter
        self._returns_filter = returns_filter
    #end __init__

    def __getattr__(self, procname) :

        def def_proc_wrapper(proctype, paramdefs, returndefs) :

            c_procname = str_encode(procname)

            def proc_wrapper(*args, **kwargs) :
                if self._params_filter != None :
                    args = self._params_filter(args)
                #end if
                if len(args) + len(kwargs) != len(paramdefs) :
                    raise TypeError \
                      (
                            "expecting %d arg(s), got %d positional + %d keyword = %d"
                        %
                            (len(paramdefs), len(args), len(kwargs), len(args) + len(kwargs))
                      )
                #end if
                if len(kwargs) != 0 :
                    paramnames = list(p["name"].replace("-", "_") for p in paramdefs)
                    done_positional = set(paramnames[:len(args)])
                    expect_keyword = list(paramnames[len(args):])
                    unrecognized = set(kwargs.keys()) - set(paramnames)
                    if len(unrecognized) != 0 :
                        raise TypeError \
                          (
                                "unrecognized arg keyword(s) %s, must be in %s"
                            %
                                (
                                    ", ".join(sorted(unrecognized)),
                                    ", ".join(paramnames),
                                )
                          )
                    #end if
                    dup_keyword = set(kwargs.keys()) & done_positional
                    if len(dup_keyword) != 0 :
                        raise TypeError \
                          (
                                "keyword arg(s) %s already specified positionally"
                            %
                                ", ".join(sorted(dup_keyword))
                          )
                    #end if
                    # assert set(kwargs.keys()) == set(expect_keyword)
                    args = list(args)
                    for key in paramnames[len(args):] :
                        args.append(kwargs[key])
                    #end for
                #end if
                c_args = params_to_ct(paramdefs, args)
                c_nr_returns = ct.c_int()
                c_returns = libgimp2.gimp_run_procedure2(c_procname, ct.byref(c_nr_returns), len(args), c_args)
                returns = ct_to_seq \
                  (
                    arr = c_returns[:c_nr_returns.value],
                    conv = param_from_ct
                  )
                libgimp2.gimp_destroy_params(c_returns, c_nr_returns.value)
                status = returns[0]
                if status != GIMP.PDB_SUCCESS :
                    raise RuntimeError("procedure %s returned status %d" % (procname, status))
                #end if
                returns = returns[1:]
                if len(returns) == 0 :
                    returns = None
                else :
                    if self._returns_filter != None :
                        returns = self._returns_filter(returns)
                    #end if
                #end if
                return \
                    returns
            #end proc_wrapper

        #begin def_proc_wrapper
            proc_wrapper.__name__ = procname
            return \
                proc_wrapper
        #end def_proc_wrapper

    #begin __getattr__
        if procname not in self._procs :
            procinfo = procedural_db_proc_info(procname)
            if procinfo == None :
                raise AttributeError("no such procedure registered as “%s”" % procname)
            #end if
            if self._procinfo_check != None :
                self._procinfo_check(procinfo)
            #end if
            self._procs[procname] = def_proc_wrapper \
                (procinfo["proc_type"], procinfo["args"], procinfo["returns"])
        #end if
        return \
            self._procs[procname]
    #end __getattr__

#end PDB

class PDBExtra :
    # additional checks/filters for particular PDB instances.

    def check_one_result(procinfo) :
        # ensures the procedure only returns one result (besides the status).
        if len(procinfo["returns"]) != 1 :
            raise TypeError("procedure %s does not return a single non-status result: %s" % (procinfo["name"], repr(procinfo)))
        #end if
    check_one_result

    def check_takes_run_mode(procinfo) :
        if len(procinfo["args"]) == 0 or procinfo["args"][0]["type"] != PARAMTYPE.INT32 :
            raise TypeError("procedure %s does not take run mode as first arg" % procinfo["name"])
        #end if
    #end check_takes_run_mode

    def prepend_run_mode(args) :
        return \
            (GIMP.RUN_NONINTERACTIVE,) + args
    #end prepend_run_mode

    def extract_single_result(results) :
        assert len(results) == 1
        return \
            results[0]
    #end extract_single_result

#end PDBExtra

pdb = PDB() # everything allowed here, but caller has to deal with it
pdb1 = PDB \
  (
    procinfo_check = PDBExtra.check_one_result,
    returns_filter = PDBExtra.extract_single_result
  )
  # those returning just one result
pdbpi = PDB \
  (
    procinfo_check = PDBExtra.check_takes_run_mode,
    params_filter = PDBExtra.prepend_run_mode
  )
  # plugins, requiring the first arg to be the run mode
del PDB, PDBExtra

def displays_flush() :
    libgimp2.gimp_displays_flush()
#end displays_flush

class ENTRYSTYLE(enum.Enum) :
    "preferred style of entry UI for each parameter."
    SPINBUTTON = "spinner"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    COMBOBOX = "combobox"
    RADIOBUTTONS = "radiobuttons"
#end ENTRYSTYLE

class Params :
    "convenience wrapper for holding param definitions and values in Python" \
    " format with easy conversion to/from the format GIMP expects."

    __slots__ = ("name", "defs", "ct_struct", "_struct_fields", "cur_vals")

    def __init__(self, name, defs) :

        class ct_struct(Structure) :
            pass # filled in below
        #end ct_struct

    #begin __init__
        self.name = name
        if (
                not isinstance(defs, (list, tuple))
            or
                not all(isinstance(e, dict) for e in defs)
            or
                not all(k in e for k in ("type", "name", "description") for e in defs)
            or
                not all(isinstance(e["type"], PARAMTYPE) for e in defs)
            or
                not all("entry_style" not in e or isinstance(e["entry_style"], ENTRYSTYLE) for e in defs)
        ) :
            raise TypeError \
              (
                "defs must be sequence of dicts, each with type, name and description keys"
              )
        #end if
        self.defs = list(defs)
        for e in self.defs :
            if e["type"] in (PARAMTYPE.INT32, PARAMTYPE.FLOAT) and "entry_style" not in e :
                e["entry_style"] = ENTRYSTYLE.SPINBUTTON # default
            #end if
            if e.get("entry_style") in (ENTRYSTYLE.COMBOBOX, ENTRYSTYLE.RADIOBUTTONS) :
                if not (e["type"] == PARAMTYPE.INT32 and "enums" in e) :
                    raise KeyError("combo box and radio buttons need enum values")
                #end if
            #end if
        #end for
        ct_struct.__name__ = "%s_params" % name
        ct_struct._fields_ = list((e["name"], e["type"].ct_type) for e in defs)
        self._struct_fields = dict \
          (
            (f[0], {"offset" : getattr(ct_struct, f[0]).offset})
            for f in ct_struct._fields_
          )
        for e in defs :
            self._struct_fields[e["name"]]["type"] = e["type"]
        #end for
        self.ct_struct = ct_struct
        self.cur_vals = ct_struct()
        self.reset_default()
    #end __init__

    def field_addr(self, fieldname) :
        "returns the address of the specified field within cur_vals, for use" \
        " with GIMP adjustment callbacks that write directly into struct fields."
        return \
            (
                ct.addressof(self.cur_vals)
            +
                self._struct_fields[fieldname]["offset"]
            )
    #end field_addr

    def save_data(self) :
        "tells GIMP to save the cur_vals as the plug-in’s last-used settings."
        libgimp2.gimp_procedural_db_set_data \
            (str_encode(self.name), ct.byref(self.cur_vals), ct.sizeof(self.cur_vals))
    #end save_data

    def load_data(self) :
        "retrieves the plug-in’s last-used settings, if there are any."
        return \
            libgimp2.gimp_procedural_db_get_data(str_encode(self.name), ct.byref(self.cur_vals))
    #end load_data

    def reset_default(self) :
        "resets cur_vals to the defaults."
        for e in self.defs :
            if "default" in e :
                setattr(self.cur_vals, e["name"], e["type"].to_ct_conv(e["default"]))
            #end if
        #end for
    #end reset_default

    def get_current(self) :
        "returns the current parameter values as a dict of Python objects."
        return \
            dict \
              (
                (e["name"], e["type"].from_ct_conv(getattr(self.cur_vals, e["name"])))
                for e in self.defs
              )
    #end get_current

    def __getitem__(self, field) :
        "for accessing individual fields as a dict of Python objects."
        return \
            self._struct_fields[field]["type"].from_ct_conv(getattr(self.cur_vals, field))
    #end __getitem__

    def __setitem__(self, field, val) :
        "for accessing individual fields as a dict of Python objects."
        setattr(self.cur_vals, field, self._struct_fields[field]["type"].to_ct_conv(val))
    #end __setitem__

    def __len__(self) :
        return \
            len(self.defs)
    #end __len__

    def __repr__(self) :
        return \
            repr(self.cur_vals)
    #end __repr__

#end Params

def wrap_run_proc(run_proc) :
    "creates a wrapper around the given Python function, which" \
    " should be written somewhat as follows:\n" \
    "\n" \
    "    def run_proc(name, params) :\n" \
    "        ...\n" \
    "        return returns\n" \
    "    #end run_proc\n"

    last_return = None
      # to save constructed objects in-between invocations (not re-entrant)

    def run_wrapper(c_name, nparams, c_params, nreturns, c_returns) :
        nonlocal last_return
        name = str_decode(c_name)
        params = ct_to_seq(c_params[:nparams], param_from_ct)
        returns = run_proc(name, params)
        last_return = seq_to_ct(returns, GIMP.Param, lambda v : param_to_ct(v[0], v[1]))
        nreturns[0] = len(returns)
        c_returns[0] = last_return
    #end run_wrapper

#begin wrap_run_proc
    run_wrapper.__name__ = "wrap_%s" % run_proc.__name__
    return \
        GIMP.RunProc(run_wrapper)
#end wrap_run_proc

def install_procedure(name : str, blurb : str, help: str, author : str, copyright : str, date : str, item_label : str, image_types : str, type : GIMP.PDBProcType, params = None, returns = None) :
    "installs a procedure in the procedure database. params and returns must be sequences" \
    " of dicts each with type, name and description fields."
    c_name = name.encode()
    c_blurb = blurb.encode()
    c_help = help.encode()
    c_author = author.encode()
    c_copyright = copyright.encode()
    c_date = date.encode()
    c_item_label = item_label.encode()
    c_image_types = image_types.encode()
    save_strs = []
    if params != None :
        c_params = seq_to_ct(params, GIMP.ParamDef, lambda v : to_param_def(v, save_strs))
        nr_params = len(params)
    else :
        c_params = None
        nr_params = 0
    #end if
    if returns != None :
        c_returns = seq_to_ct(returns, GIMP.ParamDef, lambda v : to_param_def(v, save_strs))
        nr_returns = len(returns)
    else :
        c_returns = None
        nr_returns = 0
    #end if
    libgimp2.gimp_install_procedure(c_name, c_blurb, c_help, c_author, c_copyright, c_date, c_item_label, c_image_types, type, nr_params, nr_returns, c_params, c_returns)
#end install_procedure

#+
# User Interface
#-

prog_name = os.path.basename(sys.argv[0])

def plugin_menu_register(procname, menu_name) :
    c_procname = str_encode(procname)
    c_menu_name = str_encode(menu_name)
    return \
        libgimp2.gimp_plugin_menu_register(c_procname, c_menu_name)
#end plugin_menu_register

def ui_init(preview : bool) :
    "need to call this before using any UI functions."
    libgimpui2.gimp_ui_init(str_encode(prog_name), preview)
#end ui_init

class ColourSelect(Widget) :
    "high-level wrapper for a GIMP colour selector. Actually GIMP provides" \
    " a “color_selector” abstract base class, and a “color_select”" \
    " concrete implementation of this; this wrapper represents the latter."

    @classmethod
    def create(celf, rgb : GIMP.RGB, channel) :
        hsv = GIMP.HSV()
        hsv.h, hsv.s, hsv.v, hsv.a = colorsys.rgb_to_hsv(rgb.r, rgb.g, rgb.b) + (rgb.a,)
        result = libgimpui2.gimp_color_selector_new \
          (
            libgimpui2.gimp_color_select_get_type(), # selector_type
            ct.byref(rgb), # *rgb
            ct.byref(hsv), # *hsv
            channel # channel
          )
        return \
            celf(result)
    #end create

#end ColourSelect

class Table(libgimpgtk2.Table) :

    __slots__ = ()

    def scale_entry_new(self, column : int, row : int, text : str, scale_width : int, spinbutton_width : int, value : float, lower : float, upper : float, step_increment : float, page_increment : float, digits : int, constrain : bool, unconstrained_lower : float, unconstrained_upper : float, tooltip : str, help_id : str) :
        c_text = str_encode(text)
        c_tooltip = str_encode_optional(tooltip)
        c_help_id = str_encode_optional(help_id)
        result = libgimpui2.gimp_scale_entry_new(self._gtkobj, column, row, c_text, scale_width, spinbutton_width, value, lower, upper, step_increment, page_increment, digits, constrain, unconstrained_lower, unconstrained_upper, c_tooltip, c_help_id)
        return \
            libgimpgtk2.ScaleEntry(result)
    #end scale_entry_new

#end Table

class Box(libgimpgtk2.Container) :
    "high-level wrapper for a GTK layout box. Do not instantiate directly; use" \
    " the create method or Dialog.get_content_area."

    __slots__ = ()

    @classmethod
    def create(celf, orientation, spacing) :
        return \
            celf(libgimpui2.gtk_box_new(orientation, spacing))
    #end create

    def pack_start(self, child, expand, fill, padding) :
        if not isinstance(child, Widget) :
            raise TypeError("child must be a Widget")
        #end if
        libgimpgtk2.libgtk2.gtk_box_pack_start(self._gtkobj, child._gtkobj, expand, fill, padding)
    #end pack_start

    def pack_end(self, child, expand, fill, padding) :
        if not isinstance(child, Widget) :
            raise TypeError("child must be a Widget")
        #end if
        libgimpgtk2.libgtk2.gtk_box_pack_end(self._gtkobj, child._gtkobj, expand, fill, padding)
    #end pack_end

#end Box

class Frame(Widget) :

    __slots__ = ()

    @classmethod
    def create(celf, label) :
        return \
            celf(libgimpui2.gimp_frame_new(str_encode(label)))
    #end create

    def container_add(self, child) :
        if not isinstance(child, Widget) :
            raise TypeError("child must be a Widget")
        #end if
        libgimpgtk2.libgtk2.gtk_container_add(self._gtkobj, child._gtkobj)
    #end container_add

#end Frame

class EnumComboBox(Widget) :
    "a very simple specialization of a GTK combo box, that" \
    " lets the user choose from a predefined list of text labels" \
    " associated with integer values, returning the value chosen."

    __slots__ = ("_values_store",)

    @classmethod
    def create(celf, labels) :
        if (
                not isinstance(labels, (list, tuple))
            or
                not all(isinstance(v, str) for v in labels)
        ) :
            raise TypeError("labels must be sequence of strings")
        #end if
        # actually it might be easier just to use a ComboBoxText ...
        coltype = GType(gegl.G_TYPE_STRING)
        values_store = libgimpgtk2.libgtk2.gtk_list_store_newv(1, coltype)
        pos = GTK.TreeIter()
        colpos = ct.c_int(0)
        cell = GValue()
        gegl.libgobject2.g_value_init(cell, gegl.G_TYPE_STRING)
        for i, name in enumerate(labels) :
            gegl.libgobject2.g_value_set_string(ct.byref(cell), str_encode(name))
            libgimpgtk2.libgtk2.gtk_list_store_append(values_store, ct.byref(pos))
            libgimpgtk2.libgtk2.gtk_list_store_set_valuesv \
                (values_store, ct.byref(pos), colpos, ct.byref(cell), 1)
        #end for
        gegl.libgobject2.g_value_unset(cell)
        result = celf(libgimpgtk2.libgtk2.gtk_combo_box_new_with_model(values_store))
        result._values_store = values_store
        renderer = libgimpgtk2.libgtk2.gtk_cell_renderer_text_new()
        libgimpgtk2.libgtk2.gtk_cell_layout_pack_start(result._gtkobj, renderer, False)
        libgimpgtk2.libgtk2.gtk_cell_layout_add_attribute \
          (result._gtkobj, renderer, str_encode("text"), 0)
        return \
            result
    #end create

    def get_active(self) :
        return \
            libgimpgtk2.libgtk2.gtk_combo_box_get_active(self._gtkobj)
    #end get_active

    def set_active(self, index) :
        libgimpgtk2.libgtk2.gtk_combo_box_set_active(self._gtkobj, index)
    #end set_active

#end EnumComboBox

class EnumRadioGroup(Widget) :

    __slots__ = ()

    @classmethod
    def create(celf, frame_title, labels, initial, callback, callback_data) :
        basefunc = libgimpui2.gimp_int_radio_group_new
          # fixed part of type info already set up
        func = type(basefunc).from_address(ct.addressof(basefunc))
          # same entry point, but can have entirely different arg/result types
        func.restype = basefunc.restype
        fixedargtypes = basefunc.argtypes[:-1] # drop trailing null-pointer arg, re-added below
        all_arg_types = list(fixedargtypes)
        all_args = [True, str_encode(frame_title), callback, callback_data, initial]
        for index, label in enumerate(labels) :
            all_args.extend([str_encode(label), index, None])
            all_arg_types.extend([ct.c_char_p, ct.c_int, ct.c_void_p])
        #end for
        all_arg_types.append(ct.c_void_p) # null to mark end of arg list
        all_args.append(None)
        func.argtypes = tuple(all_arg_types)
        return \
            celf(func(*all_args))
    #end create

#end EnumRadioGroup

class Dialog(Widget) :
    "high-level wrapper for a GIMP dialog. Do not instantiate directly; use the" \
    " create method."

    __slots__ = ()

    @classmethod
    def create(celf, title : str, role : str, parent, flags : int, help_func, help_id, buttons = None) :
        if parent != None :
            if not isinstance(parent, celf) :
                raise TypeError("parent is not a %s" % celf.__name__)
            #end if
            c_parent = parent._gtkobj
        else :
            c_parent = None
        #end if
        if (
                buttons != None
            and
                (
                    not isinstance(buttons, (list, tuple))
                or
                    not all
                      (
                            isinstance(b, (list, tuple))
                        and
                            len(b) == 2
                        and
                            isinstance(b[0], str)
                        and
                            isinstance(b[1], int)
                        for b in buttons
                      )
                )
        ) :
            raise TypeError("buttons is not a list of (name, id) tuples")
        #end if
        c_title = str_encode(title)
        c_role = str_encode(role)
        c_help_id = str_encode(help_id)
        wrap_help_func = help_func
        if help_func == None :
            help_func = STANDARD_HELP_FUNC
        #end if
        dialog = libgimpui2.gimp_dialog_new(c_title, c_role, c_parent, flags, help_func, c_help_id, None)
        self = celf(dialog)
        if wrap_help_func != None :
            self._wrappers.append(wrap_help_func)
        #end if
        if buttons != None :
            for button in buttons :
                self.add_button(*button)
            #end for
        #end if
        return \
            self
    #end create

    def get_content_area(self) :
        return \
            Box(libgimpgtk2.libgtk2.gtk_dialog_get_content_area(self._gtkobj))
    #end get_content_area

    def add_button(self, button_text : str, response_id : int) :
        libgimpui2.gimp_dialog_add_button(self._gtkobj, str_encode(button_text), response_id)
        return \
            self
    #end add_button

    def set_alternative_button_order(self, response_ids) :
        c_ids = seq_to_ct(response_ids, ct.c_int)
        libgimpgtk2.libgtk2.gtk_dialog_set_alternative_button_order_from_array \
            (self._gtkobj, len(response_ids), c_ids)
        return \
            self
    #end set_alternative_button_order

    def set_transient(self) :
        libgimpui2.gimp_window_set_transient(self._gtkobj)
        return \
            self
    #end set_transient

    def run(self) :
        return \
            libgimpui2.gimp_dialog_run(self._gtkobj)
    #end run

    def run_and_close(self) :
        "convenience routine which runs the dialog and closes it" \
        " before returning the user’s response."
        response = self.run()
        self.destroy()
        return \
            response
    #end run_and_close

#end Dialog

#+
# Procedure Registration
#
# This provides easy management of one or more plugin action callbacks
# to be registered with register_dispatched and invoked by
# run_dispatched (below). plugin_install should be invoked for all
# your plugin actions in your script mainline, outside any of the
# actual GIMP callbacks. This is because plugin registration and
# invocation will be done in separate process instances, so we need to
# ensure the dispatch table is always correctly built, for both
# registration and invocation purposes.
#-

installed_procedures = {}

def plugin_install(name, *, blurb, help, author, copyright, date, image_types, placement, action, params = None, returns = None, use_gegl = False, menu_name, item_label) :
    "registers a plugin action to be dispatched under the given name," \
    " and optionally attached to the given menu item. The params omit the" \
    " initial mandatory ones, which are determined from the placement. The" \
    " type is always GIMP.PLUGIN for now.\n" \
    "\n" \
    "When the plugin is invoked, the initial mandatory args are passed" \
    " positionally, so you can give them whatever names you like but the order" \
    " is fixed, while the plugin-specific ones are passed by keyword. This means" \
    " their names must match those given in the parameter definitions, but they" \
    " can be listed in any order."
    if name in installed_procedures :
        raise RuntimeError("duplicate installation of “%s”" % name)
    #end if
    if not isinstance(placement, UI_PLACEMENT) :
        raise TypeError("placement must be a UI_PLACEMENT")
    #end if
    if params == None :
        params = []
    #end if
    if returns != None and len(returns) == 0 :
        returns = None # GIMP doesn’t like zero-length returns
    #end if
    do_ui = len(params) != 0
    only_handle_paramtypes = (PARAMTYPE.COLOUR, PARAMTYPE.INT32, PARAMTYPE.FLOAT)
    if do_ui :
        if (
            not all
              (
                    p["type"] in only_handle_paramtypes
                and
                    (
                        p["type"] not in (PARAMTYPE.INT32, PARAMTYPE.FLOAT)
                    or
                        p["type"] == PARAMTYPE.INT32 and "enums" in p
                    or
                        all(k in p for k in ("lower", "upper"))
                    )
                for p in params
              )
        ) :
            raise ValueError \
              (
                    "auto UI can only handle %s params for now"
                %
                    ", ".join(n.name for n in only_handle_paramtypes)
              )
        #end if
    #end if
    installed_procedures[name] = \
        {
            "placement" : placement,
            "type" : GIMP.PLUGIN,
            "action" : action,
            "params" : params,
            "returns" : returns,
            "image_types" : image_types,
            "use_gegl" : use_gegl,

            "do_ui" : do_ui,
            "menu_name" : menu_name,
            "item_label" : item_label,

            "blurb" : blurb,
            "help" : help,
            "author" : author,
            "copyright" : copyright,
            "date" : date,
        }
#end plugin_install

#+
# Mainline
#-

def register_dispatched() :
    "convenience query_proc which automatically registers all entries in" \
    " managed_procedures with GIMP."
    for name, entry in installed_procedures.items() :
        install_procedure \
          (
            name = name,
            blurb = entry["blurb"],
            help = entry["help"],
            author = entry["author"],
            copyright = entry["copyright"],
            date = entry["date"],
            image_types = entry["image_types"],
            type = entry["type"],
            params =
                    entry["placement"].required_params
                +
                    entry["params"],
            returns = entry["returns"],
            item_label = entry["item_label"],
          )
        if entry["menu_name"] != None :
            plugin_menu_register(name, "%s%s" % (entry["placement"].path_prefix, entry["menu_name"]))
        #end if
    #end for
#end register_dispatched

def run_dispatched(name, params) :
    "convenience run_proc which automatically provides a simple settings UI" \
    " for your parameters as appropriate, before invoking your actual installed" \
    " action to perform the operation on the image."

    entry = installed_procedures[name]
    cur_params = Params(name, entry["params"])

    def do_settings() :

        c_wrap = [] # strong refs to callbacks kept here

        def def_handle_rgb_changed(rgb_param) :

            def handle_rgb_changed(widget, rgb_elt, hsv_elt) :
                ct.memmove(rgb_param, rgb_elt, ct.sizeof(GIMP.RGB))
            #end handle_rgb_changed

        #begin def_handle_rgb_changed
            result = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p, ct.c_void_p)(handle_rgb_changed)
            c_wrap.append(result)
            return \
                result
        #end def_handle_rgb_changed

        def def_handle_int32_changed() :

            def handle_int32_changed(adj, valaddr) :
                ct.cast(valaddr, ct.POINTER(ct.c_int32))[0] = \
                    round(libgimpgtk2.libgtk2.gtk_adjustment_get_value(adj))
            #end handle_int32_changed

        #begin def_handle_int32_changed
            result = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)(handle_int32_changed)
            c_wrap.append(result)
              # I could reuse the same one each time, but what the hey
            return \
                result
        #end def_handle_int32_changed

        def def_handle_checkbox_changed() :

            def handle_checkbox_changed(wdg, valaddr) :
                ct.cast(valaddr, ct.POINTER(ct.c_int32))[0] = \
                    libgimpgtk2.libgtk2.gtk_toggle_button_get_active(wdg)
            #end handle_checkbox_changed

        #begin def_handle_checkbox_changed
            result = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)(handle_checkbox_changed)
            c_wrap.append(result)
              # I could reuse the same one each time, but what the hey
            return \
                result
        #end def_handle_checkbox_changed

        def def_handle_combobox_changed() :

            def handle_combobox_changed(wdg, valaddr) :
                ct.cast(valaddr, ct.POINTER(ct.c_int32))[0] = \
                    libgimpgtk2.libgtk2.gtk_combo_box_get_active(wdg)
            #end handle_combobox_changed

        #begin def_handle_combobox_changed
            result = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)(handle_combobox_changed)
            c_wrap.append(result)
              # I could reuse the same one each time, but what the hey
            return \
                result
        #end def_handle_combobox_changed

        def def_handle_radiobutton_changed() :

            def handle_radiobutton_changed(wdg, valaddr) :
                index = gegl.libgobject2.g_object_get_data(wdg, str_encode("gimp-item-data"))
                if index == None :
                    index = 0
                #end if
                ct.cast(valaddr, ct.POINTER(ct.c_int32))[0] = index
            #end handle_radiobutton_changed

        #begin def_handle_radiobutton_changed
            result = ct.CFUNCTYPE(None, ct.c_void_p, ct.c_void_p)(handle_radiobutton_changed)
            c_wrap.append(result)
              # I could reuse the same one each time, but what the hey
            return \
                result
        #end def_handle_radiobutton_changed

    #begin do_settings
        ui_init(False)
        settings = Dialog.create \
          (
            title = name,
            role = "%s settings" % name,
            parent = None,
            flags = 0,
            help_func = None,
            help_id = name,
            buttons =
                (
                    ("Cancel", GTK.RESPONSE_CANCEL),
                    ("OK", GTK.RESPONSE_OK),
                )
          )
        settings.set_transient()
        main_vbox = Box.create(GTK.ORIENTATION_VERTICAL, 12)
        main_vbox.set_border_width(12)
        settings.get_content_area().pack_start(main_vbox, expand = True, fill = True, padding = 0)
        main_vbox.show()
        table = Table.create \
          (
            nr_rows = len(entry["params"]),
            nr_cols = 3,
            homogeneous = False
          )
        table.set_col_spacings(6).set_row_spacings(6)
        main_vbox.pack_start(table, expand = False, fill = False, padding = 0)
        table.show()
        for i, param in enumerate(entry["params"]) :
            def labelled_row(wdg) :
                label = libgimpgtk2.Label.create(param["description"])
                label.set_alignment(0, 0.5)
                label.show()
                table.attach_defaults(label, 0, 1, i, i + 1)
                table.attach_defaults(wdg, 1, 3, i, i + 1)
                wdg.show()
                return \
                    wdg
            #end labelled_row
            if param["type"] == PARAMTYPE.COLOUR :
                rgb_elt = cur_params.field_addr(param["name"])
                selector = labelled_row \
                  (
                    ColourSelect.create
                      (
                        ct.cast(rgb_elt, ct.POINTER(GIMP.RGB))[0],
                        GIMP.COLOUR_SELECTOR_HUE # channel
                      )
                  )
                selector.signal_connect("color-changed", def_handle_rgb_changed(rgb_elt))
            elif param["type"] == PARAMTYPE.INT32 :
                if param["entry_style"] == ENTRYSTYLE.SLIDER :
                    slider = table.scale_entry_new \
                      (
                        column = 0,
                        row = i,
                        text = param["description"],
                        scale_width = 100,
                        spinbutton_width = 2,
                        value = cur_params[param["name"]],
                        lower = param["lower"],
                        upper = param["upper"],
                        step_increment = 1,
                        page_increment = 10,
                        digits = 0,
                        constrain = True,
                        unconstrained_lower = 0,
                        unconstrained_upper = 0,
                        tooltip = None,
                        help_id = None
                      )
                    slider.signal_connect \
                      (
                        name = "value-changed",
                        handler = def_handle_int32_changed(),
                        arg = cur_params.field_addr(param["name"])
                      )
                elif param["entry_style"] == ENTRYSTYLE.COMBOBOX :
                    widget = labelled_row \
                      (
                        EnumComboBox.create(param["enums"])
                      )
                    widget.set_active(cur_params[param["name"]])
                    widget.signal_connect \
                      (
                        name = "changed",
                        handler = def_handle_combobox_changed(),
                        arg = cur_params.field_addr(param["name"])
                      )
                elif param["entry_style"] == ENTRYSTYLE.RADIOBUTTONS :
                    widget = EnumRadioGroup.create \
                      (
                        frame_title = param["description"],
                        labels = param["enums"],
                        initial = cur_params[param["name"]],
                        callback = ct.cast(def_handle_radiobutton_changed(), GCallback),
                        callback_data = cur_params.field_addr(param["name"])
                      )
                    widget.show()
                    table.attach_defaults(widget, 0, 3, i, i + 1)
                elif param["entry_style"] == ENTRYSTYLE.CHECKBOX :
                    button = libgimpgtk2.Checkbox.create_with_label(param["description"])
                    button.set_checked(cur_params[param["name"]] != 0)
                    button.show()
                    table.attach_defaults(button, 0, 3, i, i + 1)
                    button.signal_connect \
                      (
                        name = "toggled",
                        handler = def_handle_checkbox_changed(),
                        arg = cur_params.field_addr(param["name"])
                      )
                else :
                    adj = libgimpgtk2.Adjustment.create \
                      (
                        value = cur_params[param["name"]],
                        lower = param["lower"],
                        upper = param["upper"],
                        step_increment = 1,
                        page_increment = 10,
                        page_size = 0 # seems nonzero value is deprecated anyway
                      )
                    spinner = labelled_row \
                      (
                        libgimpgtk2.SpinButton.create
                          (
                            adjustment = adj,
                            climb_rate = 10, # ?
                            digits = 0
                          )
                      )
                    adj.signal_connect \
                      (
                        name = "value-changed",
                        handler = def_handle_int32_changed(),
                        arg = cur_params.field_addr(param["name"])
                      )
                #end if
            elif param["type"] == PARAMTYPE.FLOAT :
                if param["entry_style"] == ENTRYSTYLE.SLIDER :
                    slider = table.scale_entry_new \
                      (
                        column = 0,
                        row = i,
                        text = param["description"],
                        scale_width = 100,
                        spinbutton_width = 5,
                        value = cur_params[param["name"]],
                        lower = param["lower"],
                        upper = param["upper"],
                        step_increment = param.get("step_increment", 1),
                        page_increment = param.get("page_increment", 10),
                        digits = 3, # needs to be nonzero for fractional step increments
                        constrain = True,
                        unconstrained_lower = 0,
                        unconstrained_upper = 0,
                        tooltip = None,
                        help_id = None
                      )
                    slider.signal_connect \
                      (
                        name = "value-changed",
                        handler = libgimpui2.gimp_double_adjustment_update,
                        arg = cur_params.field_addr(param["name"])
                      )
                else :
                    adj = libgimpgtk2.Adjustment.create \
                      (
                        value = cur_params[param["name"]],
                        lower = param["lower"],
                        upper = param["upper"],
                        step_increment = param.get("step_increment", 1),
                        page_increment = param.get("page_increment", 10),
                        page_size = 0 # seems nonzero value is deprecated anyway
                      )
                    spinner = labelled_row \
                      (
                        libgimpgtk2.SpinButton.create
                          (
                            adjustment = adj,
                            climb_rate = 10, # ?
                            digits = 3
                          )
                      )
                    adj.signal_connect \
                      (
                        name = "value-changed",
                        handler = libgimpui2.gimp_double_adjustment_update,
                        arg = cur_params.field_addr(param["name"])
                      )
                #end if
            else :
                raise AssertionError("unsupported param type -- how did you get here?")
            #end if
        #end for
        settings.show()
        confirm = settings.run_and_close() == GTK.RESPONSE_OK
        return \
            confirm
    #end do_settings

#begin run_dispatched
    if entry["use_gegl"] :
        gegl.init()
    #end if
    run_mode = params[0]
    confirm = True # to begin with
    if run_mode == GIMP.RUN_INTERACTIVE :
        cur_params.load_data()
        if entry["do_ui"] :
            confirm = do_settings()
        #end if
    elif run_mode == GIMP.RUN_NONINTERACTIVE :
        base = entry["placement"].nr_required_params
        for i in range(len(params) - base) :
            cur_params[cur_params.ct_struct._fields_[i][0]] = params[i + base]
        #end for
    #end if
    if confirm :
        args = params[1:entry["placement"].nr_required_params]
          # omit run_mode
        kwargs = cur_params.get_current()
        returns = entry["action"](*args, **kwargs)
        if returns == None :
            returns = [(PARAMTYPE.STATUS, GIMP.PDB_SUCCESS)]
        #end if
        if run_mode != GIMP.RUN_NONINTERACTIVE :
            displays_flush()
        #end if
        if run_mode == GIMP.RUN_INTERACTIVE :
            if entry["do_ui"] :
                cur_params.save_data()
            #end if
        #end if
    else :
        returns = [(PARAMTYPE.STATUS, GIMP.PDB_CANCEL)]
    #end if
    if entry["use_gegl"] :
        gegl.exit()
    #end if
    return \
        returns
#end run_dispatched

def main(*, init_proc = None, quit_proc = None, query_proc = None, run_proc = None) :
    "to be invoked as your plugin mainline. You can omit all args to automatically" \
    " use the managed-procedures mechanism."
    if init_proc != None :
        c_init_proc = GIMP.InitProc(init_proc)
    else :
        c_init_proc = GIMP.NO_INIT_PROC
    #end if
    if quit_proc != None :
        c_quit_proc = GIMP.QuitProc(quit_proc)
    else :
        c_quit_proc = GIMP.NO_QUIT_PROC
    #end if
    if query_proc == None and run_proc == None :
        if len(installed_procedures) != 0 :
            c_query_proc = GIMP.QueryProc(register_dispatched)
            c_run_proc = wrap_run_proc(run_dispatched)
        else :
            raise ValueError \
              (
                "no query_proc or run_proc specified, and no managed procedures installed"
              )
        #end if
    else :
        if query_proc != None :
            c_query_proc = GIMP.QueryProc(query_proc)
        else :
            c_query_proc = GIMP.NO_QUERY_PROC
        #end if
        if run_proc == None :
            raise ValueError("missing run_proc")
        #end if
        c_run_proc = wrap_run_proc(run_proc)
    #end if
    plugin_info = GIMP.PlugInInfo \
      (
        init_proc = c_init_proc,
        quit_proc = c_quit_proc,
        query_proc = c_query_proc,
        run_proc = c_run_proc
      )
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
