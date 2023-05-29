bl_info = {
    "name": "SuperbrightUVAutomation",
    "blender": (2, 90, 0),
    "category": "Object",
}

import bpy
import bmesh

context = bpy.context


class SuperbrightUVAutomation(bpy.types.Operator):
    """UV Automation"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.uv_automation"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Superbright UVAutomation"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
           
    def reshuffleUVs (self, selected):
        if len(selected) == 0:
            return

        for obj in selected:
            uvs = obj.data.uv_layers
            if len(uvs.values()) <3:
                continue
            
            print(len(uvs.values()))
            i = 0
            for uv in uvs:
                if i>2:
                    uvs.remove(uvs[3])
                i+=1
            
            uvs.active_index = 1
            uvs.new() 

            uvs.remove(uvs[0])
            uvs.remove(uvs[0])

        return
    
    def materialsCleanup (self, selected):
        if len(selected) == 0:
            return

        for obj in selected:
            mats = obj.data.materials
            if len(mats.values()) < 2:
                pass
            while len(mats.values()) > 1:
                mats.pop()

    def execute(self, context):       # execute() is called when running the operator.

        selected = context.selected_objects

        SuperbrightUVAutomation.reshuffleUVs(self,selected)
        SuperbrightUVAutomation.materialsCleanup(self, selected)

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

class UVToggle(bpy.types.Operator):
    """UV Toggle"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.uv_toggle"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Superbright UVToggle"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    def toggle_UVs(self, context):
        selected = context.selected_objects
        if len(selected) == 0:
            return

        targetIndex = 0
        if(context.active_object and context.active_object.type == "MESH"):
            if(context.active_object.data.uv_layers.active_index == 0):
                targetIndex = 1

        for obj in selected:
            if (not obj.type == "MESH"):
                continue
            obj.data.uv_layers.active_index = targetIndex
    
    def execute(self, context):
        UVToggle.toggle_UVs(self, context)
        return {'FINISHED'} 

def menu_func(self, context):
    self.layout.operator(SuperbrightUVAutomation.bl_idname)
    self.layout.operator(UVToggle.bl_idname)

def register():
    bpy.utils.register_class(SuperbrightUVAutomation)
    bpy.utils.register_class(UVToggle)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(SuperbrightUVAutomation)
    bpy.utils.unregister_class(UVToggle)
