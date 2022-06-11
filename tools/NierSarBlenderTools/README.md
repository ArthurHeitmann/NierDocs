Blender addon for viewing and editing Nier Automata .sar files. Sar files seem to contain data about ambient sounds and music.

# Installation

(Requires Blender 3 or later)

1. Download zip from [Releases](https://github.com/ArthurHeitmann/NierDocs/releases).

2. In Blender: Edit > Preferences > Add-ons > Install

# Usage

# Importing

File > Import > Sar

If you have a map file open (from wd1/wd3/wd5) you can check "Try Applying Offsets". This will try to convert the global game coordinates to local coordinates.

Locations where you can find sar files:

- data002/data012
	- st1/st2/st5
- data003/data013
	- wd1/wd3

More information [here](../../sar/sarContents.md).

## Exporting

File > Export > Sar

If you have imported multiple sar files into the scene, only one will be exported. The object called "Field-Root" will be used as the root object.

## Editing shapes

| Shape Type Description | Shape Type Id | Things you can edit                                  |
|------------------------|---------------|------------------------------------------------------|
| Sphere                 | 0             | Core Sphere Loc, Rot, Scale + Edge Sphere Scale      |
| Curve/Tube             | 1             | Core Curve points + Core/Edge bevel depth            |
| Tall Curve             | 2             | Parent Loc, Rot + Vertices Pos XY & Vertices Scale Z |
| Cube                   | 10            | Cube Loc, Rot, Scale                                 |
| Extruded Polygon       | 11            | Parent Loc, Rot + Vertex Pos XY                      |
| Cylinder               | 15            | Core Cylinder Loc, Rot, Extrude + Core/Edge Scale XY |
| Sphere with scale ?    | 100           | Sphere Loc, Rot, Scale                               |
| Volume between faces?  | 200           | Parent Loc, Rot + Vertex Pos + Modifier Z Property   |

## Good to know

Most objects have xml data attached to them in the custom properties. Some interesting properties: "ShapeGroup" objects have "InEvent" and "OutEvent" properties for entering/exiting the shape. The Param property is the distance of the player to the shape.
