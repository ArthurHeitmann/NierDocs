import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
import os

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

        self.report({'INFO'}, "Imported mot file")

        return {'FINISHED'}

class ExportMotFile(bpy.types.Operator, ExportHelper):
    """Export a Nier Animation mot file"""
    bl_idname = "export_scene.mot"
    bl_label = "Export Nier Animation Data"
    bl_options = {'UNDO'}

    patchExisting: bpy.props.BoolProperty(
        name="Patch Existing",
        description="Patch existing mot file instead of creating a new one",
        default=False
    )
    filename_ext = ".mot"
    filter_glob: bpy.props.StringProperty(default="*.mot", options={'HIDDEN'})

    def execute(self, context):
        from .motExporter import exportMot

        if self.patchExisting and not os.path.exists(self.filepath):
            self.report({'ERROR'}, "File does not exist")
            return {'CANCELLED'}
        
        exportMot(self.filepath, self.patchExisting)

        self.report({'INFO'}, "Exported mot file")

        return {'FINISHED'}

def importMenuAdditions(self, context):
    self.layout.operator(ImportMotFile.bl_idname, text="Mot for Nier:Automata (.mot)")

def exportMenuAdditions(self, context):
    self.layout.operator(ExportMotFile.bl_idname, text="Mot for Nier:Automata (.mot)")

def register():
    bpy.utils.register_class(ImportMotFile)
    bpy.utils.register_class(ExportMotFile)

    bpy.types.TOPBAR_MT_file_import.append(importMenuAdditions)
    bpy.types.TOPBAR_MT_file_export.append(exportMenuAdditions)

def unregister():
    bpy.utils.unregister_class(ImportMotFile)
    bpy.utils.unregister_class(ExportMotFile)

    bpy.types.TOPBAR_MT_file_import.remove(importMenuAdditions)
    bpy.types.TOPBAR_MT_file_export.remove(exportMenuAdditions)
