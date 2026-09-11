import bpy

s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.samples = 64
s.cycles.device = 'CPU'

mat_chassis = bpy.data.materials.new('Mat_Chassis_Iron')
mat_chassis.use_nodes = True
b_iron = mat_chassis.node_tree.nodes.get('Principled BSDF')
b_iron.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
b_iron.inputs['Metallic'].default_value = 0.8
b_iron.inputs['Roughness'].default_value = 0.45

mat_suit = bpy.data.materials.new('Mat_Pilot_Suit')
mat_suit.use_nodes = True
b_suit = mat_suit.node_tree.nodes.get('Principled BSDF')
b_suit.inputs['Base Color'].default_value = (0.55, 0.22, 0.08, 1.0) # Weathered hazard canvas/rubber
b_suit.inputs['Roughness'].default_value = 0.85

mat_visor = bpy.data.materials.new('Mat_Visor_Glow')
mat_visor.use_nodes = True
b_vis = mat_visor.node_tree.nodes.get('Principled BSDF')
b_vis.inputs['Base Color'].default_value = (1.0, 0.45, 0.02, 1.0)
b_vis.inputs['Emission Color'].default_value = (1.0, 0.45, 0.02, 1.0)
b_vis.inputs['Emission Strength'].default_value = 3.0

def assign_mat(obj, mat):
    if obj.data and hasattr(obj.data, 'materials'):
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

for col_name in ['02_OPERATOR_HULL', '03_LOAD_FRAME', '04_POWERPLANT', '05_GROUND_INTERFACE', '06_MANIPULATORS']:
    col = bpy.data.collections.get(col_name)
    if col:
        for o in col.objects:
            if o.name == 'Operator_Visor_Optical_Slit':
                assign_mat(o, mat_visor)
            else:
                assign_mat(o, mat_chassis)

pilot_col = bpy.data.collections.get('01_PILOT_ENVELOPE')
if pilot_col:
    for o in pilot_col.objects:
        o.hide_render = False
        o.hide_viewport = False
        assign_mat(o, mat_suit)

# Add basic 3-point studio lighting
world = bpy.data.worlds.new('World_Studio')
s.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.04, 0.04, 0.05, 1.0)
bg.inputs['Strength'].default_value = 1.0

key_light_data = bpy.data.lights.new(name='Key_Light', type='AREA')
key_light_data.energy = 800
key_light_data.size = 2.0
key_light_data.color = (1.0, 0.95, 0.9)
key_light = bpy.data.objects.new(name='Key_Light', object_data=key_light_data)
key_light.location = (3.0, -4.0, 3.5)
s.collection.objects.link(key_light)

fill_light_data = bpy.data.lights.new(name='Fill_Light', type='AREA')
fill_light_data.energy = 300
fill_light_data.size = 3.0
fill_light_data.color = (0.7, 0.8, 1.0)
fill_light = bpy.data.objects.new(name='Fill_Light', object_data=fill_light_data)
fill_light.location = (-4.0, -2.5, 2.0)
s.collection.objects.link(fill_light)

rim_light_data = bpy.data.lights.new(name='Rim_Light', type='AREA')
rim_light_data.energy = 1200
rim_light_data.size = 2.5
rim_light_data.color = (1.0, 0.9, 0.8)
rim_light = bpy.data.objects.new(name='Rim_Light', object_data=rim_light_data)
rim_light.location = (0.0, 4.0, 3.0)
s.collection.objects.link(rim_light)
