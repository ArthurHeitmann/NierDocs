from math import degrees
import os
import bpy
import bpy_extras
from bpy_extras.io_utils import ImportHelper, ExportHelper
from mathutils import Vector

bl_info = {
    "name" : "NierAnimationTools",
    "author" : "RaiderB",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

class ImportMotFile(bpy.types.Operator, ImportHelper):
    """Import a Nier Animation mot file"""
    bl_idname = "import_scene.mot"
    bl_label = "Import Nier Animation Data"
    bl_options = {'UNDO'}

    filename_ext = ".mot"
    filter_glob: bpy.props.StringProperty(default="*.mot", options={'HIDDEN'})

    def execute(self, context):
        from .motImporter import importMot

        importMot(self.filepath)

        return {'FINISHED'}

def importMenuAdditions(self, context):
    self.layout.operator(ImportMotFile.bl_idname, text="Mot for Nier:Automata (.mot")

class DebugPanel(bpy.types.Panel):
    bl_label = "Debug"
    bl_idname = "DEBUG_PT_debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Debug"

    def draw(self, context):
        layout = self.layout
        
        def toDegEuler(euler):
            return f"{degrees(euler[0]):.0f}, {degrees(euler[1]):.0f}, {degrees(euler[2]):.0f}"
        
        arm = bpy.data.objects["ba0108"]
        boneIndices = [0, 1, 5, 6]
        for i in boneIndices:
            if i > len(arm.data.bones):
                continue
            bone = arm.pose.bones[i]
            root = layout.column()
            root.scale_y = 0.75
            root.label(text=bone.name + (" (ACTIVE)" if bone.bone.select else ""))
            root.label(text="bone.matrix")
            root.label(text=toDegEuler(bone.matrix.to_euler()))
            root.label(text="bone.matrix.inverted()")
            root.label(text=toDegEuler(bone.matrix.inverted().to_euler()))
            root.label(text="bone.matrix.inverted() - bone.rotation_euler")
            root.label(text=toDegEuler(Vector(bone.rotation_euler) - Vector(bone.matrix.inverted().to_euler())))
            # root.label(text="bone.matrix_basis")
            # root.label(text=toDegEuler(bone.matrix_basis.to_euler()))
            # root.label(text="bone.bone.matrix")
            # root.label(text=toDegEuler(bone.bone.matrix.to_euler()))
            # root.label(text="bone.bone.matrix_local")
            # root.label(text=toDegEuler(bone.bone.matrix_local.to_euler()))
            layout.separator()


def register():
    bpy.utils.register_class(ImportMotFile)
    bpy.utils.register_class(DebugPanel)

    bpy.types.TOPBAR_MT_file_import.append(importMenuAdditions)

def unregister():
    bpy.utils.unregister_class(ImportMotFile)
    bpy.utils.unregister_class(DebugPanel)

    bpy.types.TOPBAR_MT_file_import.remove(importMenuAdditions)
