import os
import bpy
import bpy_extras
from bpy_extras.io_utils import ImportHelper, ExportHelper
import xml.etree.ElementTree as ET

bl_info = {
    "name" : "NierSarTools",
    "author" : "RaiderB",
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (0, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


class ImportSar(bpy.types.Operator, ImportHelper):
    '''Load a Nier:Automata Sar (Skeleton) File.'''
    bl_idname = "import_scene.sar"
    bl_label = "Import Sar Data"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".sar"
    filter_glob: bpy.props.StringProperty(default="*.sar", options={'HIDDEN'})

    tryApplyingOffsets: bpy.props.BoolProperty(name="Try Applying Offsets", default=False)

    onlyToXml: bpy.props.BoolProperty(name="Only Convert To XML", default=False)
    recursivelyImport: bpy.props.BoolProperty(name="Import all recursively", default=False)

    def doImport(self, filepath):
        from . import sarImporter
        from . import sar

        if self.onlyToXml:
            xml = sar.bxmToXml(filepath)
            with open(filepath + ".xml", "wb") as f:
                f.write(ET.tostring(xml))
        else:
            sarImporter.importSar(filepath, self.tryApplyingOffsets)

    def execute(self, context):
        if self.recursivelyImport:
            directory = os.path.split(self.filepath)[0]
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".sar"):
                        self.doImport(root + '\\' + file)
            print("Imported all file!")
        else:
            self.doImport(self.filepath)
        
        return {'FINISHED'}

class ExportSar(bpy.types.Operator, ExportHelper):
    '''Export a Nier:Automata Sar (Skeleton) File.'''
    bl_idname = "export_scene.sar"
    bl_label = "Export Sar Data"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".sar"
    filter_glob: bpy.props.StringProperty(default="*.sar", options={'HIDDEN'})

    def execute(self, context):
        from . import sarExporter
        sarExporter.exportSar(self.filepath)
        return {'FINISHED'}

def importMenuAdditions(self, context):
    self.layout.operator(ImportSar.bl_idname, text="Sar for Nier:Automata (.sar)")

def exportMenuAdditions(self, context):
    self.layout.operator(ExportSar.bl_idname, text="Sar for Nier:Automata (.sar)")

def register():
    bpy.utils.register_class(ImportSar)
    bpy.utils.register_class(ExportSar)

    bpy.types.TOPBAR_MT_file_import.append(importMenuAdditions)
    bpy.types.TOPBAR_MT_file_export.append(exportMenuAdditions)

def unregister():
    bpy.utils.unregister_class(ImportSar)
    bpy.utils.unregister_class(ExportSar)

    bpy.types.TOPBAR_MT_file_import.remove(importMenuAdditions)
    bpy.types.TOPBAR_MT_file_export.remove(exportMenuAdditions)
