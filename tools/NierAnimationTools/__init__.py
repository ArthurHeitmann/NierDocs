import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper

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
    self.layout.operator(ImportMotFile.bl_idname, text="Mot for Nier:Automata (.mot)")

def register():
    bpy.utils.register_class(ImportMotFile)

    bpy.types.TOPBAR_MT_file_import.append(importMenuAdditions)

def unregister():
    bpy.utils.unregister_class(ImportMotFile)

    bpy.types.TOPBAR_MT_file_import.remove(importMenuAdditions)
