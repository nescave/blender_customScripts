bl_info = {
    "name": "SuperbrightPivotPaint",
    "blender": (2, 90, 0),
    "category": "Edit",
}

import bpy
import bmesh
import random
import numpy
import math

context = bpy.context

def loadRestrictedData():
    context = bpy.context
    return context

class SuperbrightPivotPaint(bpy.types.Operator):
    """Superbright PivotPaint"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "edit.s_pivot_paint"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Superbright PivotPaint"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def draw(self, context):
        distanceAlpha = self.layout.column(align = True)
        distanceAlpha.prop(context.scene, "Distance_Importance")
        sizeAlpha = self.layout.column(align = True)
        sizeAlpha.prop(context.scene, "Size_Importance")
        limitAmplitude = self.layout.column(align = True)
        limitAmplitude.prop(context.scene, "Scale_Amplitude")
        limitRotation = self.layout.column(align = True)
        limitRotation.prop(context.scene, "Scale_Rotation")
        scaleAdjust = self.layout.column(align = True)
        scaleAdjust.prop(context.scene, "Scale_Adjust")
        paintOnlyPivot = self.layout.column(align = True)
        paintOnlyPivot.prop(context.scene, "Paint_Only_Pivot")
        singleAxisDistance = self.layout.column(align = True)
        singleAxisDistance.prop(context.scene, "Single_Axis_Distance")

    def getBoundingBox(island):
        
        Xvalues = []
        Yvalues = []
        Zvalues = []

        for v in island:
            Xvalues.append(v.co.x)
            Yvalues.append(v.co.y)
            Zvalues.append(v.co.z)
        
        maxX = max(Xvalues)
        maxY = max(Yvalues)
        maxZ = max(Zvalues)

        minX = min(Xvalues)
        minY = min(Yvalues)
        minZ = min(Zvalues)

        center = [(maxX+minX)/2, (maxY+minY)/2, (maxZ+minZ)/2]
        size = abs(maxX-minX) * abs(maxY-minY) * abs(maxZ-minZ)
        boundingBox = center
        boundingBox.append(size)
        return boundingBox

    def getMaxY(islands):
        Y = []
        for island in islands:
            Y.append(SuperbrightPivotPaint.getBoundingBox(island)[1])
        return max(Y)

    def getMaxBound(islands):
        maxRange = []
        for island in islands:
            maxRange.append(SuperbrightPivotPaint.getBoundingBox(island)[0])
            maxRange.append(SuperbrightPivotPaint.getBoundingBox(island)[1])
            maxRange.append(SuperbrightPivotPaint.getBoundingBox(island)[2])
        return max(maxRange)


    def separateIsland(vert):
        vert.tag = True
        yield(vert)
        linked_verts = [e.other_vert(vert) for e in vert.link_edges
                if not e.other_vert(vert).tag]

        for v in linked_verts:
            if v.tag:
                continue
            yield from SuperbrightPivotPaint.separateIsland(v)

    def getIslands(bm, verts=[]):
        def tag(verts, switch):
            for v in verts:
                v.tag = switch
        tag(bm.verts, True)
        tag(verts, False)
        ret = []
        verts = set(verts)
        while verts:
            v = verts.pop()
            verts.add(v)
            island = set(SuperbrightPivotPaint.separateIsland(v))
            ret.append(list(island))
            tag(island, False) # remove tag = True
            verts -= island
        
        return ret
    def lerp(x,y,a):
        return x*(1-a)+y*a

    def magnitudeV3(vector):
        mag = math.sqrt((vector[0]*vector[0] + vector[1]*vector[1]) + vector[2]*vector[2])    
        return mag

    def normalizeV3(vector, mag):
        if mag>0:
            normalizedVector = numpy.array([vector[0]/mag, vector[1]/mag, vector[2]/mag])
        else:
            normalizedVector = vector
        return normalizedVector

    def getPivotVector(island):
        boundingBoxData = SuperbrightPivotPaint.getBoundingBox(island)
        boundsCenter = numpy.array([boundingBoxData[0],boundingBoxData[1],boundingBoxData[2]])
        vec = boundsCenter
        return vec

    def deselectAll(bm):
        for v in bm.verts:
            v.select_set(False)
        bm.select_flush(False)

    def selectIsland(bm, island):
        for v in island:
            v.select_set(True)
        bm.select_flush(True)    
        
    def vecToCol(vector):
        vec1 = numpy.array([1,1,1,1])
        vec2 = numpy.array([2,2,2,2])
        vec = (vector +vec1)/vec2
        retVec = [vec[0], vec[1], vec[2], 1]

        return retVec

    def colorIsland(context, bm, island, maxDist):
        SuperbrightPivotPaint.deselectAll(bm)
    
        col = bm.loops.layers.color["Col"]
        
        bBData = SuperbrightPivotPaint.getBoundingBox(island)
        
        rndVal1 = random.random()
        rndVal2 = random.random()
        size = SuperbrightPivotPaint.lerp(1, bBData[3]*pow(context.scene.Scale_Adjust,3)/.6, context.scene.Size_Importance)

        if context.scene.Single_Axis_Distance:
            distance = SuperbrightPivotPaint.lerp(1, bBData[1]/(maxDist), context.scene.Distance_Importance)
        else:
            distance = SuperbrightPivotPaint.lerp(1, SuperbrightPivotPaint.magnitudeV3(bBData)/maxDist, context.scene.Distance_Importance)

        blue = rndVal1/size * distance * context.scene.Scale_Rotation

        if blue<0.025:
            blue = 0
        
        SuperbrightPivotPaint.selectIsland(bm, island)
            
        for f in bm.faces:
            if f.select:
                for l in f.loops:
                    l[col][0] = 0.5
                    l[col][1] = distance/size * context.scene.Scale_Amplitude
                    l[col][2] = blue
                    l[col][3] = rndVal2* distance
                    

    def reportColors(bm, island):
        SuperbrightPivotPaint.deselectAll(bm) 
        
        col = bm.loops.layers.color["Col"]
        
        SuperbrightPivotPaint.selectIsland(bm, island)

        i=0
        for f in bm.faces:
            if i == 0:
                if f.select:
                    print(str(f.loops[0][col]))
                    i+=1

    def savePivotToUVs(context, bm, island):
        SuperbrightPivotPaint.deselectAll(bm)

        uv2 = bm.loops.layers.uv[2]
        uv3 = bm.loops.layers.uv[3]

        vec = SuperbrightPivotPaint.getPivotVector(island)

        
        SuperbrightPivotPaint.selectIsland(bm, island)
        
        for f in bm.faces:
            if f.select:
                for l in f.loops:
                    l[uv2].uv[0] = 1 - vec[0]
                    l[uv2].uv[1] = 1 - vec[1]
                    l[uv3].uv[0] = 1 - vec[2]
                    l[uv3].uv[1] = 0 

    def createUVs(me):
        i = 0
        for uv in me.uv_layers:
            i+=1
            
        while i<4:
            me.uv_layers.new()
            i += 1
            
    def main(context):
        
        ob = context.edit_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        
        SuperbrightPivotPaint.createUVs(me)
        

        if not me.vertex_colors:
            me.vertex_colors.new()
        islands = []
        for island in SuperbrightPivotPaint.getIslands(bm, verts=bm.verts):
            islands.append(island)
            
        for island in islands:
            SuperbrightPivotPaint.savePivotToUVs(context, bm, island)        

        if context.scene.Paint_Only_Pivot:
            return
        if context.scene.Single_Axis_Distance:
            maxDist = SuperbrightPivotPaint.getMaxY(islands)
        else:
            maxDist = SuperbrightPivotPaint.getMaxBound(islands)

        for island in islands:
            SuperbrightPivotPaint.colorIsland(context, bm, island, maxDist)

        SuperbrightPivotPaint.deselectAll(bm)

    
    def execute(self, context):       # execute() is called when running the operator.

        context = loadRestrictedData()
        SuperbrightPivotPaint.main(context)

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

def menu_func(self, context):
    self.layout.operator(SuperbrightPivotPaint.bl_idname)

def register():

    bpy.utils.register_class(SuperbrightPivotPaint)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_func)
    bpy.types.Scene.Distance_Importance = bpy.props.FloatProperty \
        (
            name = "Distance Importance",
            description = "should distance from pivot affect painted values?",
            soft_min = 0.0,
            soft_max = 1.0,
            default = 1.0
        )
    bpy.types.Scene.Size_Importance = bpy.props.FloatProperty \
        (
            name = "Size Importance",
            description = "should chunk sizes affect painted values?",
            soft_min = 0.0,
            soft_max = 1.0,
            default = 1.0
        )
    bpy.types.Scene.Scale_Amplitude = bpy.props.FloatProperty \
        (
            name = "Scale Amplitude",
            description = "Scales down value on G Vertex Color Channel that represents Up-Down floating",
            soft_min = 0.0,
            soft_max = 1.0,
            default = 1.0
        )
    bpy.types.Scene.Scale_Rotation = bpy.props.FloatProperty \
        (
            name = "Scale Rotation",
            description = "Scales down value on B Vertex Color Channel that represents rotation",
            soft_min = 0.0,
            soft_max = 1.0,
            default = 1.0
        )
    bpy.types.Scene.Scale_Adjust = bpy.props.FloatProperty \
        (
            name = "Scale Adjust",
            description = "Fixes problems when scale of object isn't 1 - provide objects scale value",
            soft_min = 0.0001,
            soft_max = 100.0,
            default = 1.0
        )
    bpy.types.Scene.Paint_Only_Pivot = bpy.props.BoolProperty \
        (
            name = "Paint Only Pivot ",
            description = "bakes only pivot location to UV chanels",
            default = True
        )
    bpy.types.Scene.Single_Axis_Distance = bpy.props.BoolProperty \
        (
            name = "Single Axis Distance",
            description = "paints amplitude and rotation according to distance in single Y direction - helpful when creating falloff effect",
            default = False
        )

def unregister():
    bpy.utils.unregister_class(SuperbrightPivotPaint)
    del bpy.types.Scene.Distance_Importance
    del bpy.types.Scene.Size_Importance
    del bpy.types.Scene.Scale_Amplitude
    del bpy.types.Scene.Scale_Rotation
    del bpy.types.Scene.Scale_Adjust
    del bpy.types.Scene.Paint_Only_Pivot
    del bpy.types.Scene.Single_Axis_Rotation
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_func)
    